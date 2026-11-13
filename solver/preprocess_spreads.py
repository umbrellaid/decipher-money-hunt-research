# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow", "numpy"]
# ///
"""
preprocess_spreads.py
=====================
CZUR Aura full-frame spread -> clean, deskewed, dewarped single-page JPGs.

Solves all geometric & photometric failure modes on hand-held two-page spreads:
  1. Hand / thumb exclusion via chroma + upper-page geometry: paper & ink on
     CZUR LED captures (including yellowed 1960s-70s stock) have R - G < 15
     while skin has R - G in +20..+48, and hands only hold the lower half of
     the book. Closing <95 px gaps bridges deep V-shaped spine shadows without
     merging hands into the book span.
  2. Ink-masked tilted spine tracking: tracks the narrow vertical shadow crease
     within the ink-free inner gutter corridor across 16 horizontal strips,
     preventing false locks onto black text margins or fanned leaf stacks.
  3. Seamless paper-color masking & fanned leaf-stack trim: fills masked
     thumbs, mat wedges, cross-gutter regions, and outer fanned page-edge
     stripes with the page's median cream paper RGB rather than stark white
     (255,255,255), avoiding artificial contrast step edges.
  4. Global rotation + 2D page-curl dewarp: rotates each half-page by the spine
     angle, refines global tilt, and flattens local 2D baseline curl (caused
     by thumbs lifting lower page corners) over a 10x9 patch grid before 2x
     Lanczos upscaling.

Usage:
    uv run solver/preprocess_spreads.py --raw-dir <spreads> --out-dir <pages>
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import csv
import math
import re
import sys
from pathlib import Path

import numpy as np


def natural_key(path: Path) -> list:
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", path.stem)]


def close_1d(mask: np.ndarray, max_gap: int) -> np.ndarray:
    """Bridge False gaps of length <= max_gap between True runs."""
    m = mask.copy()
    idx = np.where(m)[0]
    if len(idx) < 2:
        return m
    gaps = np.where(np.diff(idx) <= max_gap + 1)[0]
    for g in gaps:
        m[idx[g] : idx[g + 1] + 1] = True
    return m


def largest_run(mask: np.ndarray, min_len: int) -> tuple[int, int] | None:
    """Longest contiguous True run of at least min_len."""
    best: tuple[int, int] | None = None
    best_len = 0
    start = None
    for i, v in enumerate(mask):
        if v and start is None:
            start = i
        elif not v and start is not None:
            if i - start > best_len and i - start >= min_len:
                best, best_len = (start, i), i - start
            start = None
    if start is not None and len(mask) - start > best_len and len(mask) - start >= min_len:
        best = (start, len(mask))
    return best


def smooth(x: np.ndarray, win: int) -> np.ndarray:
    if win <= 1 or len(x) < win:
        return x.astype(np.float32)
    k = np.ones(win, dtype=np.float32) / win
    return np.convolve(x.astype(np.float32), k, mode="same")


def fit_line_robust(ys: np.ndarray, xs: np.ndarray, inlier_tol: float = 14.0) -> tuple[float, float, int]:
    """Fit x = m * y + b robustly using pairwise/RANSAC candidates."""
    n = len(ys)
    if n == 0:
        return 0.0, 0.0, 0
    if n == 1:
        return 0.0, float(xs[0]), 1
    best_inliers = None
    best_score = -1.0
    for i in range(n):
        for j in range(i + 1, n):
            dy = float(ys[j] - ys[i])
            if abs(dy) < 80.0:
                continue
            m = float(xs[j] - xs[i]) / dy
            if abs(m) > 0.16:
                continue
            b = float(xs[i]) - m * float(ys[i])
            resid = np.abs(xs - (m * ys + b))
            inl = resid <= inlier_tol
            cnt = int(inl.sum())
            score = cnt - 0.01 * float(resid[inl].mean()) if cnt > 0 else -1.0
            if score > best_score:
                best_score = score
                best_inliers = inl
    if best_inliers is None or int(best_inliers.sum()) < 2:
        m, b = np.polyfit(ys, xs, 1)
        m = float(np.clip(m, -0.14, 0.14))
        b = float(np.median(xs - m * ys))
        return m, b, n
    yi, xi = ys[best_inliers], xs[best_inliers]
    m, b = np.polyfit(yi, xi, 1)
    return float(m), float(b), int(best_inliers.sum())


def refine_deskew_angle(page_rgb: np.ndarray, base_angle_deg: float) -> float:
    """Refine CCW rotation angle within +-2.0 deg on the upper-middle text block."""
    from PIL import Image

    h, w, _ = page_rgb.shape
    y0, y1 = int(h * 0.10), int(h * 0.75)
    x0, x1 = int(w * 0.14), int(w * 0.86)
    if y1 - y0 < 120 or x1 - x0 < 120:
        return base_angle_deg
    gray_small = page_rgb[y0:y1:3, x0:x1:3].mean(axis=2)
    ink = ((gray_small < 155) * 255).astype(np.uint8)
    if int((ink > 0).sum()) < 250:
        return round(base_angle_deg, 2)
    pil_ink = Image.fromarray(ink, mode="L")
    best_ang = base_angle_deg
    best_var = -1.0
    for delta in np.linspace(-2.0, 2.0, 21):
        ang = base_angle_deg + float(delta)
        rot = np.array(pil_ink.rotate(ang, resample=Image.BILINEAR, fillcolor=0), dtype=np.float32)
        v = float(np.var(rot.sum(axis=1)))
        if v > best_var:
            best_var = v
            best_ang = ang
    return round(best_ang, 2)


def dewarp_page_curl(page_rgb: np.ndarray, paper_rgb: np.ndarray) -> np.ndarray:
    """Flatten local 2D baseline curl (inner spine S-curl + thumb-lifted corners) across a 10x9 grid."""
    h, w, _ = page_rgb.shape
    gray = page_rgb.mean(axis=2)
    ink = (gray < 155).astype(np.float32)
    ink[:, : int(w * 0.04)] = 0.0
    ink[:, int(w * 0.94) :] = 0.0
    ink[: int(h * 0.04), :] = 0.0
    ink[int(h * 0.96) :, :] = 0.0

    if float(ink.sum()) < 700.0:
        return page_rgb

    n_y, n_x = 10, 9
    slopes = np.zeros((n_y, n_x), dtype=np.float32)
    weights = np.zeros((n_y, n_x), dtype=np.float32)
    cand_slopes = np.linspace(-0.22, 0.22, 45, dtype=np.float32)

    for iy in range(n_y):
        ya = int(h * (0.04 + 0.88 * iy / n_y))
        yb = min(h, int(h * (0.04 + 0.88 * (iy + 1.40) / n_y)))
        for ix in range(n_x):
            xa = int(w * (0.04 + 0.86 * ix / n_x))
            xb = min(w, int(w * (0.04 + 0.86 * (ix + 1.40) / n_x)))
            patch = ink[ya:yb:2, xa:xb:2]
            ink_sum = float(patch.sum())
            if ink_sum < 45.0:
                continue
            ph, pw = patch.shape
            xs_rel = np.arange(pw, dtype=np.float32) - 0.5 * pw
            base_rows = np.arange(ph, dtype=np.float32)[:, None]
            cols = np.broadcast_to(np.arange(pw, dtype=np.int32)[None, :], (ph, pw))
            best_s = 0.0
            best_v = -1.0
            for s in cand_slopes:
                shifted_y = np.rint(base_rows + s * xs_rel[None, :]).astype(np.int32)
                valid = (shifted_y >= 0) & (shifted_y < ph)
                vals = np.where(valid, patch[np.clip(shifted_y, 0, ph - 1), cols], 0.0)
                v = float(np.var(vals.sum(axis=1)))
                if v > best_v:
                    best_v = v
                    best_s = float(s)
            slopes[iy, ix] = best_s
            weights[iy, ix] = ink_sum

    if float(weights.max()) <= 0.0:
        return page_rgb

    # Propagate slopes across blank/heading patches from neighboring text patches
    for _ in range(8):
        for iy in range(n_y):
            for ix in range(n_x):
                if weights[iy, ix] > 0:
                    continue
                nb_s, nb_w = 0.0, 0.0
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        ny, nx = iy + dy, ix + dx
                        if 0 <= ny < n_y and 0 <= nx < n_x and weights[ny, nx] > 0:
                            nb_s += slopes[ny, nx] * weights[ny, nx]
                            nb_w += weights[ny, nx]
                if nb_w > 0:
                    slopes[iy, ix] = nb_s / nb_w
                    weights[iy, ix] = nb_w * 0.5

    y_centers = np.array([h * (0.04 + 0.88 * (iy + 0.70) / n_y) for iy in range(n_y)], dtype=np.float32)
    x_centers = np.array([w * (0.04 + 0.86 * (ix + 0.70) / n_x) for ix in range(n_x)], dtype=np.float32)

    xs_full = np.arange(w, dtype=np.float32)
    slope_yx_coarse = np.zeros((n_y, w), dtype=np.float32)
    for iy in range(n_y):
        slope_yx_coarse[iy, :] = np.interp(xs_full, x_centers, slopes[iy, :])

    disp_coarse = np.cumsum(slope_yx_coarse, axis=1)
    disp_coarse -= disp_coarse[:, w // 2 : w // 2 + 1]

    if float(np.max(np.abs(disp_coarse))) < 1.5:
        return page_rgb

    ys_full = np.arange(h, dtype=np.float32)
    disp_full = np.empty((h, w), dtype=np.float32)
    for x in range(0, w, 4):
        col_d = np.interp(ys_full, y_centers, disp_coarse[:, x])
        disp_full[:, x : min(w, x + 4)] = col_d[:, None]

    src_y = ys_full[:, None] + disp_full
    y0 = np.floor(src_y).astype(np.int32)
    wy = (src_y - y0)[..., None]
    oob = (y0 < 0) | (y0 + 1 >= h)
    y0_c = np.clip(y0, 0, h - 1)
    y1_c = np.clip(y0 + 1, 0, h - 1)
    cols_idx = np.arange(w, dtype=np.int32)[None, :]

    p0 = page_rgb[y0_c, cols_idx].astype(np.float32)
    p1 = page_rgb[y1_c, cols_idx].astype(np.float32)
    out = np.clip(np.rint(p0 * (1.0 - wy) + p1 * wy), 0, 255).astype(np.uint8)
    out[oob] = paper_rgb
    return out


def estimate_paper_rgb(crop: np.ndarray) -> np.ndarray:
    """Median RGB of clean bright cream paper inside the central page region."""
    h, w, _ = crop.shape
    sub = crop[int(h * 0.15) : int(h * 0.85) : 3, int(w * 0.18) : int(w * 0.82) : 3]
    g = sub.mean(axis=2)
    rg = sub[:, :, 0].astype(np.int16) - sub[:, :, 1].astype(np.int16)
    pts = sub[(g > 165) & (rg < 15)]
    if len(pts) < 100:
        return np.array([216, 224, 222], dtype=np.uint8)
    return np.median(pts, axis=0).astype(np.uint8)


def save_clean_page(
    page_rgb: np.ndarray,
    angle_ccw: float,
    paper_rgb: np.ndarray,
    dest: Path,
    margin: int,
    scale: int,
    do_dewarp: bool = True,
) -> None:
    from PIL import Image

    fill_tup = (int(paper_rgb[0]), int(paper_rgb[1]), int(paper_rgb[2]))
    im_page = Image.fromarray(page_rgb, mode="RGB")
    if abs(angle_ccw) >= 0.05:
        im_page = im_page.rotate(
            angle_ccw, resample=Image.BICUBIC, expand=False, fillcolor=fill_tup
        )
    if do_dewarp:
        rot_arr = np.array(im_page, dtype=np.uint8)
        rot_arr = dewarp_page_curl(rot_arr, paper_rgb)
        im_page = Image.fromarray(rot_arr, mode="RGB")

    pw, ph = im_page.size
    canvas = Image.new("RGB", (pw + 2 * margin, ph + 2 * margin), fill_tup)
    canvas.paste(im_page, (margin, margin))
    if scale != 1:
        canvas = canvas.resize((canvas.width * scale, canvas.height * scale), Image.LANCZOS)
    canvas.save(dest, quality=92)


def process_image(
    path: Path,
    out_dir: Path,
    thresh: int,
    margin: int,
    scale: int,
    min_span_split: int,
    min_valley: float,
) -> dict:
    from PIL import Image

    im = Image.open(path).convert("RGB")
    rgb = np.array(im, dtype=np.uint8)
    h_img, w_img, _ = rgb.shape

    rgb_h = rgb[::2, ::2].astype(np.int16)
    gray_h = rgb_h.mean(axis=2)
    rg_h = rgb_h[:, :, 0] - rgb_h[:, :, 1]
    paper_h = (gray_h > 135) & (rg_h < 15)

    rmask = close_1d(paper_h.sum(axis=1) > 350, max_gap=18)
    rspan = largest_run(rmask, min_len=400)

    is_spread = False
    c0 = c1 = r0 = r1 = 0
    if rspan is not None:
        r0_h, r1_h = rspan
        rt0 = r0_h + int(0.05 * (r1_h - r0_h))
        rt1 = r0_h + int(0.38 * (r1_h - r0_h))
        cmask = close_1d(paper_h[rt0:rt1, :].mean(axis=0) > 0.42, max_gap=48)
        cspan = largest_run(cmask, min_len=350)
        if cspan is not None and (cspan[1] - cspan[0]) * 2 >= min_span_split:
            is_spread = True
            c0, c1 = cspan[0] * 2, cspan[1] * 2
            rmask2 = close_1d(paper_h[:, cspan[0] : cspan[1]].mean(axis=1) > 0.25, max_gap=18)
            rspan2 = largest_run(rmask2, min_len=400)
            if rspan2 is not None:
                r0_h, r1_h = rspan2
            r0, r1 = r0_h * 2, r1_h * 2

    if not is_spread:
        maxc_h = rgb_h.max(axis=2)
        found = None
        for thr, frac in ((135, 0.22), (90, 0.12)):
            cm2 = close_1d((maxc_h > thr).mean(axis=0) > frac, max_gap=20)
            cs2 = largest_run(cm2, min_len=220)
            if cs2 is not None:
                rm2 = close_1d((maxc_h[:, cs2[0] : cs2[1]] > thr).mean(axis=1) > 0.25, max_gap=20)
                rs2 = largest_run(rm2, min_len=350)
                if rs2 is not None:
                    found = (cs2[0] * 2, rs2[0] * 2, cs2[1] * 2, rs2[1] * 2)
                    break
        if found is None:
            return {"image": path.name, "action": "SKIP (no book region found)"}
        sc0, sr0, sc1, sr1 = found
        crop = rgb[sr0:sr1, sc0:sc1].copy()
        white = np.array([255, 255, 255], dtype=np.uint8)
        save_clean_page(crop, 0.0, white, out_dir / f"{path.stem}.jpg", margin, scale, do_dewarp=False)
        return {
            "image": path.name,
            "action": "single",
            "span_w": int(sc1 - sc0),
            "page_h": int(sr1 - sr0),
        }

    # ---- Two-page spread: fit tilted outer borders & dark spine crease ----
    book_h = r1 - r0
    n_strips = 16
    strip_y, left_x, right_x = [], [], []
    for s in range(n_strips):
        ya_h = (r0 + int((0.04 + 0.92 * s / n_strips) * book_h)) // 2
        yb_h = (r0 + int((0.04 + 0.92 * (s + 1) / n_strips) * book_h)) // 2
        if yb_h <= ya_h + 4:
            continue
        lo_h = max(0, c0 // 2 - 90)
        hi_h = min(paper_h.shape[1], c1 // 2 + 90)
        sm = close_1d(paper_h[ya_h:yb_h, lo_h:hi_h].mean(axis=0) > 0.42, max_gap=35)
        sr = largest_run(sm, min_len=int((c1 - c0) // 2 * 0.70))
        if sr is not None:
            strip_y.append(float(ya_h + yb_h))
            left_x.append(float((lo_h + sr[0]) * 2))
            right_x.append(float((lo_h + sr[1]) * 2))

    if len(strip_y) >= 4:
        ys_arr = np.array(strip_y, dtype=np.float64)
        m_L, b_L, _ = fit_line_robust(ys_arr, np.array(left_x, dtype=np.float64), inlier_tol=14.0)
        m_R, b_R, _ = fit_line_robust(ys_arr, np.array(right_x, dtype=np.float64), inlier_tol=14.0)
    else:
        m_L, b_L = 0.0, float(c0)
        m_R, b_R = 0.0, float(c1)

    m_mid = 0.5 * (m_L + m_R)
    b_mid = 0.5 * (b_L + b_R)
    y_mid_book = 0.5 * (r0 + r1)
    span_w_mid = max(400.0, (m_R * y_mid_book + b_R) - (m_L * y_mid_book + b_L))

    gray_full = rgb.mean(axis=2)
    g_ys, g_xs, g_dips = [], [], []
    half_win = min(int(span_w_mid * 0.052), 108)
    pad_bg = 24
    for s in range(n_strips):
        ya = r0 + int((0.05 + 0.90 * s / n_strips) * book_h)
        yb = r0 + int((0.05 + 0.90 * (s + 1) / n_strips) * book_h)
        yc = 0.5 * (ya + yb)
        x_est = int(round(m_mid * yc + b_mid))
        lo = max(0, x_est - half_win - pad_bg)
        hi = min(w_img, x_est + half_win + pad_bg)
        if hi - lo < 2 * pad_bg + 20 or yb - ya < 20:
            continue
        strip = gray_full[ya:yb, lo:hi]
        v_grad = np.abs(strip[6:, :] - strip[:-6, :])
        ink_col = ((strip[3:-3, :] < 140) & (v_grad > 28)).mean(axis=0)
        ink_near = np.convolve((ink_col > 0.012).astype(np.float32), np.ones(21), mode="same") > 0

        col_med = smooth(np.median(strip, axis=0), win=5)
        bg = 0.5 * (np.roll(col_med, pad_bg) + np.roll(col_med, -pad_bg))
        dip = bg - col_med
        dip[:pad_bg] = -999.0
        dip[-pad_bg:] = -999.0
        dip = np.where(ink_near, -999.0, dip)

        vi = int(np.argmax(dip))
        if float(dip[vi]) >= 2.5:
            g_ys.append(yc)
            g_xs.append(float(lo + vi))
            g_dips.append(float(dip[vi]))

    if len(g_ys) >= 5:
        m_g, b_g, n_inl = fit_line_robust(
            np.array(g_ys, dtype=np.float64),
            np.array(g_xs, dtype=np.float64),
            inlier_tol=7.0,
        )
        if n_inl < 5 or abs(m_g - m_mid) > 0.035:
            offset = float(np.median(np.array(g_xs) - (m_mid * np.array(g_ys) + b_mid)))
            m_g, b_g = m_mid, b_mid + np.clip(offset, -85.0, 85.0)
        valley_ratio = round(float(np.median(g_dips)), 2)
    elif len(g_ys) >= 2:
        offset = float(np.median(np.array(g_xs) - (m_mid * np.array(g_ys) + b_mid)))
        m_g, b_g = m_mid, b_mid + np.clip(offset, -85.0, 85.0)
        valley_ratio = round(float(np.median(g_dips)), 2)
    else:
        m_g, b_g = m_mid, b_mid
        valley_ratio = 0.0

    gutter_mid = int(round(m_g * y_mid_book + b_g))
    w_L = int(round(gutter_mid - (m_L * y_mid_book + b_L)))
    w_R = int(round((m_R * y_mid_book + b_R) - gutter_mid))
    # True single-leaf width has zero fanned page-edge stack; trimming beyond
    # 0.982 * min(w_L, w_R) removes fanned page-edge stripes without touching text.
    max_leaf_w = max(890.0, 0.982 * float(min(w_L, w_R)))

    ry0 = max(0, r0 - 10)
    ry1 = min(h_img, r1 + 10)
    ys_col = np.arange(ry0, ry1, dtype=np.float32)[:, None]
    xg_col = m_g * ys_col + b_g
    xl_col = np.maximum(m_L * ys_col + b_L, xg_col - max_leaf_w)
    xr_col = np.minimum(m_R * ys_col + b_R, xg_col + max_leaf_w)

    # --- Left page ---
    lx0 = max(0, int(math.floor(float(xl_col.min()))) - 8)
    lx1 = min(w_img, int(math.ceil(float(xg_col.max()))) + 6)
    left_crop = rgb[ry0:ry1, lx0:lx1].copy()
    paper_L = estimate_paper_rgb(left_crop)
    xs_L = np.arange(lx0, lx1, dtype=np.float32)[None, :]
    lg = left_crop.mean(axis=2)
    l_rg = left_crop[:, :, 0].astype(np.int16) - left_crop[:, :, 1].astype(np.int16)
    mask_L = (
        (xs_L >= xg_col - 4.0)
        | (xs_L <= xl_col + 6.0)
        | (((ys_col < r0 + 42) | (ys_col > r1 - 42)) & ((lg < 120) | (l_rg >= 15)))
        | (
            ((xs_L < xl_col + 230.0) | (ys_col < r0 + 95) | (ys_col > r1 - 95))
            & (l_rg >= 15)
            & (lg > 65)
        )
    )
    left_crop[mask_L] = paper_L

    # --- Right page ---
    rx0 = max(0, int(math.floor(float(xg_col.min()))) - 6)
    rx1 = min(w_img, int(math.ceil(float(xr_col.max()))) + 8)
    right_crop = rgb[ry0:ry1, rx0:rx1].copy()
    paper_R = estimate_paper_rgb(right_crop)
    xs_R = np.arange(rx0, rx1, dtype=np.float32)[None, :]
    rg_m = right_crop.mean(axis=2)
    r_rg = right_crop[:, :, 0].astype(np.int16) - right_crop[:, :, 1].astype(np.int16)
    mask_R = (
        (xs_R <= xg_col + 4.0)
        | (xs_R >= xr_col - 6.0)
        | (((ys_col < r0 + 42) | (ys_col > r1 - 42)) & ((rg_m < 120) | (r_rg >= 15)))
        | (
            ((xs_R > xr_col - 230.0) | (ys_col < r0 + 95) | (ys_col > r1 - 95))
            & (r_rg >= 15)
            & (rg_m > 65)
        )
    )
    right_crop[mask_R] = paper_R

    base_ang = float(np.clip(-math.degrees(math.atan(m_g)), -8.0, 8.0))
    ang_L = refine_deskew_angle(left_crop, base_ang)
    ang_R = refine_deskew_angle(right_crop, base_ang)

    save_clean_page(left_crop, ang_L, paper_L, out_dir / f"{path.stem}_1L.jpg", margin, scale)
    save_clean_page(right_crop, ang_R, paper_R, out_dir / f"{path.stem}_2R.jpg", margin, scale)

    return {
        "image": path.name,
        "action": "split",
        "gutter_x": gutter_mid,
        "gutter_slope": round(m_g, 4),
        "deskew_deg": f"[{ang_L}, {ang_R}]",
        "valley_ratio": valley_ratio,
        "span_w": int(round(span_w_mid)),
        "page_h": int(r1 - r0),
        "page_w": [w_L, w_R],
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Split, deskew & dewarp CZUR two-page spreads for OCR")
    ap.add_argument("--raw-dir", required=True, type=Path)
    ap.add_argument("--out-dir", required=True, type=Path)
    ap.add_argument("--thresh", type=int, default=70, help="legacy compatibility flag")
    ap.add_argument("--margin", type=int, default=24, help="border in px before upscale (default 24)")
    ap.add_argument("--scale", type=int, default=2, help="upscale factor (default 2)")
    ap.add_argument(
        "--min-span-split",
        type=int,
        default=1450,
        help="upper-page paper width in px at/above which a capture is split (default 1450)",
    )
    ap.add_argument(
        "--min-valley",
        type=float,
        default=0.965,
        help="legacy compatibility flag",
    )
    ap.add_argument(
        "--only",
        default="",
        help="optional comma-separated image filenames/stems to re-process without rewriting full manifest",
    )
    ap.add_argument(
        "--workers",
        type=int,
        default=4,
        help="number of parallel worker threads (default 4)",
    )
    args = ap.parse_args()

    only_set = {s.strip().lower() for s in args.only.split(",") if s.strip()}
    images = sorted(
        [
            p
            for p in args.raw_dir.iterdir()
            if p.suffix.lower() in {".jpg", ".jpeg", ".png"}
            and (not only_set or p.name.lower() in only_set or p.stem.lower() in only_set)
        ],
        key=natural_key,
    )
    if not images:
        sys.exit(f"no images found in {args.raw_dir}")
    args.out_dir.mkdir(parents=True, exist_ok=True)

    def _work(img: Path) -> dict:
        try:
            return process_image(
                img,
                args.out_dir,
                args.thresh,
                args.margin,
                args.scale,
                args.min_span_split,
                args.min_valley,
            )
        except Exception as e:
            return {"image": img.name, "action": f"ERROR ({e})"}

    rows = []
    n_workers = max(1, args.workers)
    with ThreadPoolExecutor(max_workers=n_workers) as pool:
        for i, r in enumerate(pool.map(_work, images), 1):
            rows.append(r)
            extra = ""
            if r.get("action") == "split":
                extra = (
                    f" gutter={r.get('gutter_x')} slope={r.get('gutter_slope')}"
                    f" dip={r.get('valley_ratio')} deskew={r.get('deskew_deg')} w={r.get('page_w')}"
                )
            print(f"[{i}/{len(images)}] {r['image']}: {r['action']}{extra}")

    fieldnames = [
        "image",
        "action",
        "gutter_x",
        "gutter_slope",
        "deskew_deg",
        "valley_ratio",
        "span_w",
        "page_h",
        "page_w",
    ]
    if not only_set:
        with open(args.out_dir / "pages_manifest.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(rows)

    n_split = sum(1 for r in rows if r["action"] == "split")
    n_single = sum(1 for r in rows if r["action"] == "single")
    n_bad = sum(1 for r in rows if str(r["action"]).startswith(("SKIP", "ERROR")))
    print(f"done: {n_split} split, {n_single} single, {n_bad} skipped/errored")
    print(f"manifest: {args.out_dir / 'pages_manifest.csv'}")


if __name__ == "__main__":
    main()
