# Money Hunt — YouTube comment sweep digest

Source: Karen Puzzles, "The Little-Known $1,000,000 Puzzle That's Never Been Solved"
(https://www.youtube.com/watch?v=lYuS2rja2nI). Sweep performed 2026-10-09 (evening) via
the InnerTube continuation API in the page context, because the comment list would not
load in the browser UI (stuck spinner; only 20 threads ever rendered).

Coverage: **1,006 of 1,006 top-level comments** (51 API pages, 20/page). The count
"1,351 Comments" includes ~345 replies. Karen's pinned comment
links a viewer-run Discord (https://discord.com/invite/ZGvu4Ts7C9) that multiple later
commenters report is **dead**; no subreddit ever consolidated the community.

Raw dump: `work_p10/yt_comments_top.json` in the private workspace (not published).

**Reply expansion, 2026-10-10 (Kimi session):** all reply threads were expanded via
the InnerTube `next` endpoint (2026 comment format: text in `commentEntityPayload`
entities, nested reply continuations under
`replies.commentRepliesRenderer.subThreads`). Yield: **232 replies across 100
threads**, 100 % fetched with text, saved privately as `work_p10/mh_replies.json`
(readable join: `work_p10/mh_replies_readable.txt`). The gap vs the ~345 estimate
is attributable to deleted/hidden comments and count drift since 2021; every thread
carrying a reply continuation was fully expanded, nested replies included.
Findings below (section "Findings from the reply expansion").

## Highest-signal comments (verbatim excerpts)

### 1. @wishkohaku — full "deduction = subtraction" attempted solve (4 years ago, edited)
Theory: back-of-box word "deduction" is literal subtraction — find repeated
illustrations across pages and subtract (what is *missing* from the copy). Example:
page 13 has a "P"; page 20 has the same P with a line through it → page 13 is missing
a "line". Then proposes a complete page→letter mapping using the poster path order
that spells (presumably) the answer. Excerpt of the mapping as written:

> US = page 15, NY = 9, T = 18, H = 24, E = 14, E = 6, M = 17, P = 21, I = 23, R = 27,
> E = 19, S = 7, T = 5, A = 8, T = 10, E = 25, B = 20, U = 22, I = 28, L = 13, D = 16,
> I = 26, N = 12, G = 11

i.e. "**US NY THE EMPIRE STATE BUILDING**" with page 10→T, page 25→E, page 28→I.
Notable: assigns a letter to every one of the 24 path pages, and "page 13 missing a
line → L for line" is the only worked example. Unverified, self-admitted speculation,
but it is the **only comment with a complete 24-page letter assignment**.

### 2. @lexter2000 — page-18 rebus + indexing ideas (4 years ago, edited)
- Page 18 middle panel = "Muskegon" (moose + key-gone) + Chicago (Blackhawks logo;
  Chicago the musical → musical bars), matching the vertical positioning of the two
  cities on the book's map, along Lake Michigan.
- Right panel = "Headlines?"
- Suggests tracing something on the map; notes order/movement (maybe backwards);
  wonders why pages are ordered in the book yet re-ordered by the path.
- Books on the last photo page "remind me of an indexing hint … remove A (1), H (8),
  switch V (19) and S (22) … maybe a Polybius Square like A Treasure's Trove".
- Repeated drawings may connect pages in a path (p11 → p28 via the weird-titled book →
  p10 via the symbols on the book cover).
- Bird photo: maybe index the count of each bird into its name (6 flamingos → 6th
  letter of FLAMINGO); 2 parrots bottom-right.

### 3. @torreyk0820 — PO Box number tie-in
> the plane crashed between the 78th and 80th floors leaving an 18 by 20 foot gap in
> the Empire State Building … The P.O. Box to enter your registration is 803878
> (18+20=38)!!!

(803878 contains "18…20…38"; consistent with the 18×20 ft hole. Coincidence vs design
unknowable.)

### 4. @everest7719 — all-NY reading (2 years ago)
1945 Jaguar = year of the B-25 crash; queen of spades → Queens NY; page 8 "Main St." +
building looks like the Main St. post office (Queens); page 10 building = Chrysler
Building; Queen Mary = England–NY express; bridges on pages 12–13 = Brooklyn Bridge;
Broadway refs; bowling → Bowling Green; polo refs → NY polo history (first US polo
club, 1904 US Open Polo Championship, first USPA HQ).

### 5. @zelandakhniteblade5436 — Malbone Street / Empire Boulevard theory (2 years ago)
"staying on track" rebus + Empire State → Malbone Street train derailment (1918);
Malbone St renamed **Empire Boulevard** afterwards; $16M painting ↔ Brooklyn-Manhattan
Transit Corp paid $1.6M in 1923. Answer would be under Flatbush/Ocean/Empire
intersection. Self-assessed "tenuous".

### 6. @peterweston6588 — page-10 suitcase glyphs
Left-most suitcase symbol = Devanagari **उ** (the "oo" in boot); next = Greek **Δ**
(d); third large symbol unidentified. (Cross-check against the p10 2×4 glyph grid.)

### 7. @Sarahle3 — red-herring + manufacturing-error hypothesis
Mini-puzzles (rebus, braille) may be red herrings; pictures themselves = tourist
attractions adding up to "Manhattan". Also warns: some "clues" may be **unproofed
errors** — the booklet was manufactured in a hurry; photocopying/shrinking artwork
introduces unintentional lines and dots. (Directly relevant to distinguishing real
marks from scan/copy artifacts in our transcriptions.)

### 8. @RebelCowboysRVs — "Flamer Taimer" reading + herring argument
"Flamer Taimer" ≈ fireman → "Firemen overcome by smoke". Argues braille/knitting are
wild goose chases because the directions say everything you need is in the materials.

### 9. @Kate_P — page-18 speech bubble
"Brume" is the French title of Stephen King's *The Mist* (1980) — ties to the
shopping-center story; "fanatical aggression from other survivors" theme.

### 10. @jasonmorello1374 / @Redwood_The_Elf — queen of spades
Three cards face up + four players around → the game **Spades** (bridges Bridge and
Hearts); Queen of Spades has strategic significance in a trick. Redwood: Stud Poker
with 3 cards; or STYX song "Queen of Spades".

### 11. @Mushiixx — timestamped page notes
Page 5 clock = "search the missing 4"; hour hand 7:28 = "the date". Page 7 "n w o d"
= "upside down" (for crossword p10? castle p13? p19?); "whole milk" box appears on
p18; "other space" → telescope p27. Page 12 = flying things (with penguin). Page 14 =
weather + birds. Page 15 "clearly showing 2 and 5" (B-25 / $1M damage). Page 16 "iron
worker" → building; "big guy on campus" → big building.

### 12. @codemiesterbeats — B-25 angle
"Find the place one did play" → maybe the plane's call-sign / maiden-voyage airfield /
pilot's home town. Also notes knitting-pattern software exists.

### 13. @markkmiecik9797 — route-following idea (2 years ago)
Start at NYC/ESB; each page yields route number + direction + distance → next
waypoint, like rally directions.

### 14. @Thedarkbunnyrabbit — anti-guess argument (3 years ago, edited)
Answer probably NOT the ESB itself (too guessable given 3 guesses allowed); more
likely where the plane was headed / scrapped / cause of accident. Instructions say
start at the page that happens **last** → back-trace the accident timeline.

### 15. @derhohlenbar — Betty Lou Oliver
Elevator operator injured in the 1945 crash, then fell 75 floors in the elevator and
survived; one elevator was a firefighter elevator; Empire State souvenir bell
resembles the book's bell ribbon.

### 16. @hannahsutton4978 / @brennadryl — music-staff notes
Notes on the staff are written backwards (stems up ⇒ noteheads should be on the left).
@brennadryl: "the notes on the staff are BA DA"; clues "are all A and D, like the
music note in the play room"; flower pot has an "E"; 9:29 "it IS hearts".

### 17. @ag4444 / @PatriciaLaliberte / @sideduck6501 / @toxicginger9936 / @GrayWind-h7g
Gorilla suit = King Kong → ESB confirmation bias cluster (very common take).

## Signal assessment
- No commenter claims a verified solution; no one in the sweep reports the prize was
  found. The "it's a scam / never had an answer" view (SNW8191, walterengler5709,
  lizehhh, ColorwaveCraftsCo, wishkohaku) is a recurring minority position.
- The most *constructive* material is the wishkohaku mapping (complete but
  unverified), the lexter2000 page-18/map/indexing notes, and the manufacturing-error
  caution (Sarahle3) — which aligns with our own transcription-errata work.
- No new factual source (document, photo, interview) appears anywhere in the
  top-level comments beyond what the repo already has; the dead Discord likely held
  the deepest discussion, now lost unless archived.

## Findings from the reply expansion (2026-10-10)

### A. Primary-source leads (highest value)

1. **@Guitarhitches claims first-hand contact with Mr. S** (1 year ago, three
   comments): *"I personally knew Mr.S through all those years"*, *"I was given one
   of those gemstones way back when"*, and — critically — ***"I have the new book
   that Mr.S tried to publish"***. If genuine, this person holds an unpublished
   primary document. No reply from Karen is attached. **This is the single best
   lead found in either comment sweep.** Action: contact via YouTube (reply to the
   comment, or channel about page).
2. **@5kmrunder15**: *"In the first version of the game with oldest box design,
   there is NO jigsaw puzzle inside the box."* Karen replied asking for specifics;
   no follow-up captured. If true, the jigsaw (and its poem, and the "turn to page
   11" on-ramp) belongs to a **later printing** — the first-version solve path may
   differ. Testable via collector photos/eBay listings of the two box designs.
3. **Karen has unpublished specifics**: to @usedtomakemesmile (who offered
   law-library access), Karen wrote she can *"send over some of the real names and
   specifics I didn't want to include in the video"* — an avenue if court-record
   research ever resumes. Touche Ross (answer custodian) merged in 1989; Karen
   emailed them and considers it a dead end (three separate threads).

### B. Mechanism-relevant puzzle content

4. **WWII-ship bird hypothesis for p12** (@BiffEnterprises, replying to @disseria):
   *"all 10 species of bird share names of WWII era US Naval ships!!"* If true,
   the p12 birds → ship namesakes layer would independently corroborate the proven
   WASHINGTON solve (USS *Washington*, BB-56) and tie the page to the military/B-25
   theme. Verifiable claim — the bird list is known. Caveat: several replies
   (@disseria, @villa1162, @dawnchesbro4189, @MiishaLynn, @simonekoenig) **correct
   the video's bird IDs** (toucans → hornbills, crane → crowned pigeons, heron →
   pelican or spoonbill, parakeet → macaw, cockatiel → palm cockatoo, penguin →
   Magellanic/Humboldt) — since the p12 method indexes counts into species *names*,
   the corrected names should be re-tested for both the letter indexing and the
   ship-name match.
5. **wishkohaku thread — crossword cross-check for subtraction letters**
   (@ashleym4882, 31 + 25 likes): page 13's missing line → *"Actually I think its
   'Lines' because that's one of the answers in the crossword"*; and page 15's
   clown *"is missing its hat or 'Cap' which is also in the crossword. But that
   would make the answer in Canada somewhere and not the empire state building."*
   Two implications: (a) the missing element's name may have to **be a crossword
   answer** — a validation rule the repo has not used; (b) an alternative p15
   extraction (CAP) yields letters pointing to Canada — a live competing variant.
   Check LINES and CAP against the transcribed clue lists (p11/p22/p23) and the
   p18 mini-crossword.
6. **Independent VA DERS corroboration** (@kaimcmanus9608, 4 months ago — the most
   recent substantive commenter): *"'va ders' … seems like one of those wordplay
   things looking for 'invaders'"* — matches the repo's verified 28→I subtraction
   (INVADERS missing IN). Same commenter: 19:56 number puzzle reads as alphabet
   positions **16-21-26-26-12-5 = PUZZLE**; the 23:47 number series "all differ by
   5, the odd one is −5, last should be 7".
7. **Suitcase glyphs converging on "USA"**: @jameshamilton6674 (top-level + reply)
   and @LuNa-zw9wu read Devanagari **उ = U**; @hendrikhardeman9832 corrects **स =
   SA** (inherent vowel), so उ + स ≈ **"U SA"**; triangles possibly A's.
   @StijnHommes: count of each glyph → nth state. Cross-check against the p10 2×4
   glyph grid transcription.
8. **"Flamer Tamer" cross-page pair** (@qazwiz + @jeandiatasmith): read as
   *"(then) FLAMER TAMER (over)COME (by) Smoke"* — the rebus and the woman reading
   *The Tamer of the Flame* "go together". Consensus settles on **firefighter
   overcome by smoke** (@byte01010101me, @gillianboate, @someonedifferent198);
   period-colorful alternative: **Red Adair** (@hughgordon6435). @For_What_It-s_Worth
   proposes rebus corrections: "-sunbeam" → "-tall tale" (yarn) and "-note (mi)" →
   "-latin friend (ami)" to absorb spare letters.
9. **Anti-guess answer alternatives, made concrete**: under @Thedarkbunnyrabbit's
   argument that ESB itself is too guessable, @jameshamilton6674 and @Rosetta90
   propose **Bedford Army Air Field, MA** (where the B-25 took off — Col. Smith's
   flight origin) or Newark (its destination) as the "specifically at ___".
   @heartofthematterlanguage counters that pre-Google such research was much
   harder. Also @PatriciaMaroney's Navy-victim angle: a young sailor returning home
   to NY after his brother died in service — "the place one did play" = native
   New Yorker.
10. **Claimed answers on record** (all unverified, no workings shown):
    **Rego Park, Queens NY** (@neggispringfeild — "knowing the answer should make
    it easier to work out how it was solved"); **University of Miami / a seat in
    the old Orange Bowl** (@thegiant573); **Canada** (@dotcorbeil6266 — "each page
    unlocks another… if you follow each clue properly", Karen invited an email, no
    follow-up visible); **Canada via p15 CAP** (@ashleym4882, item 5). Tease-only:
    @hobbybugs ("worked it out… you looked at the images too literally rather than
    the metaphor").
11. **Misc page-level notes**: p16 days/numbers read as the **May 1986 calendar**
    (only month in 1986 with Monday the 19th — @eschma94, Karen liked it); the
    wine-bottle/fence page has **two clock towers showing different times**
    (@kcandyou5263); division sign on the last stanchion p22/23 (@dontuse1029);
    1950s five-pin pins had **different point values** — affects p24 score-sheet
    math (@TarenNauxen); p9↔p26 cross-page link — ribbon on the pig-spit handle
    belongs to the upside-down bell on p26 (@helenobrien60); pool-page game read as
    4-card poker/blackjack with a *dealer* (long cuffed sleeve) not a player
    (@Puffcroc, @joshgorrell5431); playroom staff notes re-analyzed by clef —
    treble A/D, alto B/E, tenor G/C, bass C/F — and stems-on-wrong-side suggests
    reading from the back, flipped (@samanthaquant7411, @sleeps_in_october);
    braille number-sign discussion suggests the "S5_F" string's 5 is an **E**
    without a number mark (@emmi3785, @dontuse1029) — relevant to the mis-filed
    STAFF S5_F note.
12. **Physical-artifact ideas**: @Corlock78 noticed a **cardboard tab at the bottom
    of the box** and wonders if something is hidden in the box itself
    ("everything you need is in the box"); @speedpaw8023 suggested
    cutting/layering pages — Karen notes the book is double-sided and layering
    showed nothing.

### C. Reply-sweep signal assessment

- The replies are **much richer than the top-level sweep**: one primary-source lead
  (Guitarhitches), one version-history fact (no-jigsaw first edition), one
  verifiable p12 corroboration hypothesis (WWII ships), one mechanism refinement
  (subtraction names = crossword answers), and an independent VA DERS read.
- Three concrete "answers" are now on the public record (Rego Park; Orange Bowl;
  Canada), none with workings. The ESB/Bedford/Newark triangle frames the
  "specifically at ___" question properly for the first time.
- Nothing in the replies contradicts the repo's transcription work; the bird-ID
  corrections and the two-clock-towers note are worth folding into the p12/p16/etc.
  page files when those pages are next re-read.
