# Verified game mechanics (in-game ground truth)


Verified from Seralth's in-game screenshots (2026-07-07, Incarnation (L) Middle G1, Mortal World Epic extractor, tracks Culti 20 / Quality 15 / Gush 14). Engine implements these since the model-overhaul commit after v2.6.1:

- **Pills/Respira are flat daily XP** (pill panel shows absolute XP and % of grade XP; 112.7K/1,412,392 = the displayed 7.98%). Modeled per-row: rate = speed(row)×(1+gem)/8s + daily_xp/86400.
- **Aura Gem** = claimable storage accruing gem% × cultivation speed (16/20/24% = Rare/Epic/Legendary, 18–32h cap per claim). Multiplies cultivation speed only, NOT pills/Respira. Donk's sheet's time/(1+gem)/(1+pills) was wrong on both counts. NUMERIC PIN (Seralth 2026-07-15): at culti speed 103.012/8s (=1.1125M/day), Legendary gem storage caps at exactly 356.01k = 24% × speed × 32h — confirms both the 24% rate and the 32h cap to the point. The continuous-income approximation is exact iff claimed ≥ every 32h. Claimed XP is a transferable flat stream: PLAYER-CONFIRMED (Seralth
  2026-07-15) the gem accrues off the HIGHEST path's speed regardless of
  settings, and the claim lands on whichever path is set as "cultivating" —
  swap-to-aux → claim → swap-back transfers the full amount at zero loss.
- **Passive aura generation follows the "cultivating" toggle** (Seralth
  2026-07-15): whichever path is set as cultivating receives the passive
  aura income. Absorption ratio keys off the HIGHEST stage (dump: "Higher
  Stage Phase grants higher Absorption Ratio" 最高境界等级越高), so
  cultivating a lower aux path still absorbs at the main stage's band —
  the full main-rate stream is transferable 1:1 to the aux.
- **Pills redeem to the "cultivating" path too** (Seralth 2026-07-15):
  swap to the target path, redeem, swap back — passive generation then
  resumes on the chosen path. The daily pill attempt limit is SHARED
  across paths (Seralth-confirmed), so diverted pills cost the main path
  their XP 1:1; the swap itself loses nothing.
- **Gush**: data `gush_chance` = RANDOM trigger rate; the ×6 pity is a **SOFT pity** — any gush (random or guaranteed) resets the "guaranteed in x6" counter (observed 2026-07-10: random gush on 5th fruit reset counter to 6; issue #9). So a gush is guaranteed within 6 of the LAST gush, not every literal 6th. Engine models it as a 6-state Markov moment recursion (exact mean+variance). `gush_xp` is the total multiplier (1.5 base = "150%", 2.06 at Gush lvl 14 = "+206%"), keyed by the **Gush track level** (Donk keyed it by Culti level — wrong).
- **Orb quality**: residual-fill model confirmed exactly (Quality 15 + Epic → Blue 70/Purple 30). The +20% orb EXP boosts are gated on **extractor rarity rank** (Uncommon rank→Uncommon orbs, cumulative to Mythic; no Common line), not culti-level thresholds.
- **culti_xp is 4%/level** (80% at Lv20, "+4%" per level shown in-game). The data table originally had 2%/level — fixed ×2.
- Extractor at highest server Stage: base fruit EXP +50% (= `fruit_highest_rank`). Extractor quality/bonus reset to Common/0 on main-Stage breakthrough; leftover fruits of the previous Stage auto-consume at pre-upgrade rates.

Tests in tests/test_engine.py class ScreenshotGroundTruth2026_07_07 pin all of this. Related: [[fruit-ranks-no-r4-r5]].

## Fruit ranks


The `fruit_xp` table in data/breakthrough.json (R3, R6–R12) is complete despite the apparent gap. Per Seralth (2026-07-06): fruit ranks map to realm bands — R3 covers Nascent through Voidbreak, R6 starts the Spiritual world, R12 starts the Immortal world. R4/R5 were never omitted; they don't exist as fruit ranks. Don't flag this as missing data in future audits.

Related: fruit XP/balance tables are server-authoritative and NOT in the client APK dump (see apk_analysis/RE_FINDINGS.md) — client dumps can't verify balance numbers; Donk's sheet + in-game tooltips are the sources of truth.

## Timegate overcap / XP prestocking (verified 2026-07-15)

When a world-level timegate blocks a major-Stage breakthrough, cultivation
EXP keeps accruing past the full gauge as a tracked "Excess EXP" pool that is
applied after the (still manual) breakthrough.

- Client string (apk_analysis/i18n_en_ru.json line 47604): *"%s's EXP is full.
  Excess EXP will be returned after the breakthrough."* Breakthrough remains a
  manual, gauge-gated action (lines 26669, 21791); timegate lock strings at
  19482 ("Suppressed by Cosmic Laws...") and 70487 (server level limit).
- **Overcap display convention (VERIFIED against two independent community
  data points, exact match with data/breakthrough.json grade_xp):**
  `displayed % = cumulative EXP since the start of the CURRENT HALF-STEP ÷
  that half-step's total XP`. 100% = half-step complete (gauge full at cap).
  - "440% at Incarnation Late → arrive Voidbreak Late G1" (2026 new-player
    guide / community): (Inc LATE total + XP through VB Mid) / Inc LATE total
    = **440%** exactly per our table.
  - "Aux path Wholeness Early G20 overcapped to 404% = Wholeness completion"
    (same guide, Strive-sniffing section): (WN EARLY total + rest of WN) /
    WN EARLY total = **404%** exactly.
  - The double match also independently validates the Incarnation–Wholeness
    grade_xp table.
- Accrual rate while overcapped: PLAYER-CONFIRMED (Seralth 2026-07-15) —
  same as the normal capped-row rate, EXCEPT the Strive Bonus does not apply
  to overcapped accrual. (For a rank-No.1 player strive is 0 and the rates
  are literally identical.) You stay parked on the capped row, so NO
  future-row speed scaling applies. A prestock projection must divide the
  whole XP distance by the CURRENT rate minus strive (the normal target
  projection would be optimistic).
  MODELED (2026-07-15, issue #25): the engines now de-strive the overcap
  rate (abode × base low of the capped row); pinned by
  test_prestock_rate_excludes_strive / test_prestock_slows_as_strive_rises.
  The overcap leg is also reset-window aware: with dailies_done, no daily
  XP accrues until the reset and the deferred event-Respira credit lands at
  the reset.
  ASSUMED (unverified): blessing pp still apply while overcapped — they are
  an absorption-band bonus, not Strive.
- Timegate context (2026 guide): Voidbreak gate ≈ day 35–38 of a server;
  Myrimon fruits "lose 50% of their XP" once the next realm's timegate passes —
  spend fruits before the gate. RECONCILED (2026-07-15, gameplay.tips abode
  guide): this is the same mechanic as the engine's `fruit_highest_rank` +50%
  base-EXP bonus for fruits matching the server's highest unlocked realm — the
  gate passing unlocks the next realm, so your fruits stop being highest-rank
  and lose the +50% (≈ "lose a third", community rounds to 50%). Not a
  separate penalty.
- Web cross-check (2026-07-15): the Overmortal Global Wiki's Cultivation Room
  per-grade EXP tables match data/breakthrough.json exactly at spot-checked
  rows (Inc Late G15 = 6,549,973; VB Late G20 = 25,232,632). Manual,
  pill-gated breakthroughs confirmed by the wiki; multi-grade carry-through of
  stocked EXP anecdotally supported ("Middle Voidbreak in one go" videos).
- Live-screen cross-check (2026-07-16, Seralth's secondary path screenshot):
  Nascent Soul (M) Middle G5 bar reads 134,329/632,859 — the table's G5 row
  (632,859) matches to the digit.
- Dao-seed display vs grades (2026-07-16, Seralth's Incarnation (L) Late
  screen): the seed arc shows grades−1 seeds (14 seeds for G1–G14); the
  final "fill the bar to breakthrough" band is what the table records as the
  last grade (G15). The seed count is NOT the grade count — do not "fix"
  grade tables from seed screenshots.
  The 440%/overcap display convention exists nowhere on the indexed web —
  our arithmetic reproduction is the only public cross-check. Accrual rate
  while overcapped: player-confirmed same as capped-row rate minus Strive
  (see above).

## R8 technique books — pill-effect coverage complete (2026-07-15)

Screenshot-verified from the in-game R8 technique screens: only THREE R8
books carry Cultivation Pill Effect lines — Zixiao Sutra (+1% on learning),
Astral Arcanum (+2% at Tier 3), Chroma (+1% on learning, +3% at Tier 6,
plus +1 Respira attempt at Tier 3 and +1 daily pill attempt at Tier 12).
Per Seralth (2026-07-15): the other six R8 books (Tao of Taiqing, Origin
Scripture, No-Thought Sutra, Moon Meru, Dracophant, Cauldron Refinement)
have NO pill-effect lines — their absence from data/pill_effect_sources.json
is complete coverage, not missing data. Books' Base Abode Aura bonuses are
deliberately NOT cataloged (they're already inside the player's entered
Abode Aura reading; adding them would double-count).

## Stage sub-rank suffixes: (M)/(C)/(P) tracks and "Incarnation Completed" (2026-07-15)

Verified from APK i18n strings (`apk_analysis/i18n_all.json`, en/zh/ru):

- Stage names carry a **track suffix**, they are parallel ladders, not extra
  ranks on the Magicka ladder:
  - **(M) = Magicka** (main cultivation) — zh classics: Foundation (M) 筑基,
    Virtuoso (M) 结丹, Nascent Soul (M) 元婴, Incarnation 化神, Voidbreak (M)
    返虚, Wholeness 合体, Perfection (M) 大乘, Nirvana (M) 渡劫.
  - **(C) = Corporia** (body cultivation) — zh: Foundation (C) 锻骨 "forge
    bone", Incarnation (C) 神力, Voidbreak (C) 破虚, etc. Confirmed by item
    text: "A Fateum Bag for the Coporia Incarnation Stage" = 'Incarnation (C)
    Fateum Pack'.
  - **(P) = Pet** cultivation — zh: Connection (P) 通智 "gain sentience",
    Virtuoso (P) 妖丹 "demon core", Celestial (P) 仙兽 "immortal beast".
    NOT "Perfected".
- **"Incarnation (Perfected)" (live-game wording) = 化神圆满/神力圆满**, in
  our dump translated 'Incarnation (M) Completed' / 'Incarnation (C)
  Completed'. It is the ONLY stage with a Completed/圆满 state — the terminal
  sub-rank after maxing Incarnation (Late) G15 while waiting to ascend to the
  Immortal World (Voidbreak). No other mortal-world stage has it.
- Grade ladders per dump (matches data/breakthrough.json): Incarnation Early
  G1–G8, Middle G1–G9, Late G1–G15.
- Completed/Perfected is not an extra XP band — breakthrough.json's
  Incarnation Late G15 row already covers the XP to reach it. Ascension
  itself is event/quest-gated ("Path to Ascension is not yet unlocked.
  Unable to ascend."), which the time calculator does not model.
  UNVERIFIED (server-side): whether cultivation XP keeps accruing/prestocks
  while sitting in Completed awaiting ascension — same open question as the
  overcap accrual rate above.

### Ascension Virya blessings tied to Completed/Perfected (2026-07-15, screenshots)

SCREENSHOT-VERIFIED (2026-07-15, ~/Pictures/respira-books-2026-07-15/
Screenshot_20260715-0333*.png — "Ascension Virya" screen, player at
Incarnation (L) Late G12, blessing ranking No.1 → 6 reward vases). Dump
strings corroborate (圆满后境界精进可增加福泽奖励; templates '%s Absorption
Ratio + %s%%', 'Absorption Ratio Before %s: + %s%%'):

- Tier **Completion** (req: "Reach Incarnation (L) Late 100% and break
  through"): "Remove Realm Restrictions for Taking Cultivation Pills";
  "Activate the Cultivation Pill Auto-Transmogrification Privilege";
  Blessing Rewards +1; privilege "First Esotability". The restriction
  removal is what lets higher-stage Cultivation Pills be fed to the LOWER
  secondary path to catch it up (community-explained use).
- Tier **Perfection (C)** (reqs: primary at Incarnation (L) Completion;
  secondary at Nascent Soul (L) Late; clear Outer Realm Mighty Monster
  Amethyst Fiend in Myrimon Wonder): "Incarnation (L) Aura Absorption Ratio
  +20%"; Blessing Rewards +3.
- Secondary-path stage requirements are REACH, not complete (owner-confirmed
  2026-07-16): "secondary at Nascent Soul (L) Late" is satisfied on entering
  the half-step; same for the Incarnation (L) Middle requirement above it.
- Tier **Perfect ...** (gold; reqs: secondary at Incarnation (L) Middle;
  clear Jade-Eyed Lion in Myrimon Wonder): lists BOTH "Incarnation (L) Aura
  Absorption Ratio +20%" AND "Absorption Ratio Before Voidbreak (L) Middle:
  +20%"; Blessing Rewards +5; "Second Esotability".
- COMMUNITY MODEL of the stacking (TWO independent player confirmations via
  Seralth 2026-07-15 — an older player self-rated ~90% sure, plus a second
  player confirming +60% total while in Incarnation, dropping to +40% after
  Voidbreak Middle removes the conditional +20%; supersedes the narrower
  window reading where they conflict): Perfection (C)'s +20% and Perfect's +20% "Incarnation Aura
  Absorption Ratio" add flat to +40%, and that +40% PERSISTS past
  Incarnation (it is named for the tier, not windowed to the stage). The
  "Before Voidbreak (L) Middle +20%" is the conditional one on top: +60%
  total until passing Voidbreak Middle, then back to +40% permanently.
  Meta consequence: players park in Voidbreak (Early) — +60% plus VB's
  higher base band (0.50 vs Incarnation Late 0.40) — and prestock until
  they can clear Middle into Late in one push.
- The "Double" label between the tier circles is NOT a tier (unclickable,
  per Seralth). PLAUSIBLE INFERENCE: it is the active-Virya status badge
  (dump: 'Double' = 双; template ">Within {1} hours, receive {3}x {2}
  Cosmoapsis gains.") — i.e. the Ascension Virya session grants ×2
  cultivation gains per Cosmoapsis while its countdown (02:26:31 in the
  screenshot) runs. Verify by comparing the /Cosmoapsis speed readout
  during vs after the timer.
- Blessing tiers/bonuses are per-path — the screen and status bar use path
  suffix (L) (player's primary), confirming path letters beyond M/C/P
  (cf. elixir notes' L/G/M/C/S).
- Cross-check: the screen's Late G12 XP denominator 5,623,090 exactly
  matches data/breakthrough.json Incarnation Late G12 grade_xp — independent
  confirmation of our XP table.
- Dump also has a rank→reward table (Blessing Ranking 1→6, 2→5, 3→4,
  4–10→3, 11+→2 — matches No.1 ⇒ 6 vases on screen) and post-ascension
  privileges granting Absorption Ratio +200% plus high-stage pill access.
- Official absorption formula (dump): Cultivation Speed = Abode Aura ×
  Absorption Ratio (× Heavenly Power Bonus); Absorption Ratio = Base Stage
  Absorption Ratio × (1 + Strive Bonus) + Virya Absorption Ratio.

**Calculator impact — REVISED: this CAN affect the time math.** The engine's
projection cancels the entered absorption ratio (speed(row) = culti_speed ×
low_row / low_cur, engine.py) — valid only when bonuses scale all rows
uniformly. A blessing bonus restricted to a realm window ("before Voidbreak
(Late)") breaks the cancellation: windowed rows are faster than the pure
base-band progression predicts. Same class of issue for the +200%
post-ascension privilege and Virya (both additive terms, per the formula).
Per the community model above, the effective bonus is +40% persistent
(+60% before Voidbreak Middle) — and since it persists past Incarnation,
it is a permanent absorption modifier, not just a window. Separately, the pills-on-secondary-path use means a
secondary-path projection would see BOTH a bigger flat daily-XP term (better
pills) and the windowed absorption bonus. ADDITIVE per community consensus (third independent player confirmation
via Seralth 2026-07-15): the blessing "+20%" adds percentage points to the
absorption ratio (like Virya in the official formula), not ×1.2. Still
pending one in-game absorption-tooltip reading with a tier active for
screenshot-grade verification (a 40%-band player with +20% should read
60%, not 48%). SUPERSEDED on composition (2026-07-15, i18n corpus sweep):
the client's own rules text gives the official formula —
"Absorption ratio = (base absorption ratio + Virya absorption ratio) x
(1 + Strive Bonus)" — i.e. blessing/Virya pp join the STAGE BASE inside
the Strive multiplier, not the displayed total. A companion string scopes
the Virya bonus to the current Stage ("Aura Absorption Rate +%d%% in
Current Stage"); values are %d templates (server-side), so the +20pp tier
values remain community-sourced.
MODELED (2026-07-15, updated same day to the official composition): both
engines take two inputs — a persistent pp bonus (`bless_pp`) and the
conditional before-Voidbreak-MIDDLE pp bonus (`bless_window_pp`) — applied
per-row as speed(row) = abode × (low_row + bless(row)) × (1+strive). The
entered absorption ratio is the on-screen TOTAL; the engine recovers true
Strive as absorption / (low_cur + bless_cur) − 1, so the implied-Strive
readout is not contaminated for blessed accounts. The tooltip-grade check
updates accordingly: a base-40% player with +20pp blessing at Strive s
should display (0.40 + 0.20) × (1 + s).
## Respira base XP is FIXED per major Stage (verified 2026-07-15)

Community "Respira has a fixed value" claims are correct, with a precise
meaning: the base cultivation XP per Respira attempt is one constant for the
entire major Stage — it does not scale with phase or grade.

- **Verified (Seralth in-game readings, 2026-07-15, no Respira EXP % buffs,
  overcapped)**: Nascent Soul G6 and Nascent MIDDLE G7 both show **4041** XP
  per attempt. Same value across phases/grades ⇒ fixed per Stage.
- **Client dump sweep (verified)**: no base-XP table or constant exists
  client-side. Respira's internal key is `yunqi` (吐纳). The client ships only:
  crit table `yunqi_crit` = weights/multipliers {600,×1},{300,×2},{80,×5},
  {20,×10} with expected multiplier `yunqi_exp_crit = 1.8`; round size
  `yunqi_round = {20, 2}`; per-level daily attempt caps (`yunqi_limit`, 2 at
  lv1 → 10 default, std_level_calc.lua) plus `extra_times_yunqi` buffs;
  and percent-scale modifiers `extra_base_yunqi`/`extra_exp_yunqi`/
  `extra_crit_yunqi` (cfg_us_attrib.lua / cfg_us_affix.lua). The base amount
  is server-authoritative (consistent with all balance tables).
- **REFUTED (2026-07-15, issue #27)**: the hypothesis that the per-Stage
  constant equals 2.2% of the Stage's Early G1 grade_xp (Nascent:
  183,679 × 0.022 = 4,040.9 → 4041, match to 0.002% — but coincidence).
  Incarnation reading came in at **8,173** vs the rule's prediction of
  17,372 (Early G1) / 32,626 (Late G1); no grade_xp row in
  breakthrough.json yields 8,173 at 2.2% under any books assumption.
  Measured per-Stage constants so far (non-crit on-screen values):
  **Nascent 4,041 · Incarnation 8,173** (ratio 2.022 — near ×2 per Stage,
  but that is one ratio, not a verified law; a Voidbreak reading near
  16,3xx would support it). Formula unknown; treat the constants as a
  lookup of measured values.
- Technique-book Respira lines (screenshot-verified 2026-07-15, Incarnation
  char; cataloged in data/respira_sources.json): activated total **+28%
  Respira Effect** (Energy Unification 1, Cosmic Power 3, Golden Core 1,
  Astrology 3, Taiyin Meridian 3, Yin's Grasp 5, Floral Essence 3,
  Purify & Cleanse 4, Great Yang Manual 5) and **+2 attempts** (Cosmic Power,
  Purify & Cleanse). Not yet active: P&C Tier 9 +7%, Lion's Roar +1%,
  Cauldron Refinement T3 +3%, Moon Meru T12 +10%, Chroma T3 +1 attempt.
  "Respira Effect" = `extra_exp_yunqi`.
- Incarnation reading (2026-07-15, exact, resolves the pending cross-check):
  common non-crit value **8,173** with **16,3xx** crit procs observed in the
  same session. The earlier "low 18000s"/"22.2k sounds more correct" recall
  was wrong — a caution against recall-based confirmation. The ~×2 procs are
  consistent with the client crit table's ×1.8 *expected* value being the
  mean of a distribution that includes ×2 rolls. OPEN: whether the on-screen
  base already includes the +28% technique books (if so, unbuffed base is
  ~6,385) — needs a reading with a book newly toggled to compare.
- Cross-account data point (2026-07-15, friend-of-Seralth screenshots,
  Ghostia char at Incarnation (G) Late G9): normal proc 9,515, "Grasped"
  proc 19,030 — exactly ×2.0, confirming the yunqi_crit ×2 tier and its
  proc name. 9,515 ≠ Seralth's 8,173 at the same major Stage ⇒ the
  DISPLAYED per-attempt value is per-account (the within-account per-Stage
  constancy stands). Model: display = shared base × (1 + account's Respira
  Effect books). RESOLVED (2026-07-15): Seralth confirmed his +28% is
  EXACT, which anchors integer bases that reproduce both of his displays
  under rounding: **Nascent base = 3,157** (× 1.28 = 4,040.96 → 4,041) and
  **Incarnation base = 6,385** (× 1.28 = 8,172.8 → 8,173). The friend's
  true active books are then +49.0% (9,515 / 6,385 = 1.4902), inside their
  stated ±few-% uncertainty. The per-Stage ratio is 2.0225 — doubling is
  only APPROXIMATE; treat the bases as server-side measured lookup values
  (same epistemic class as the grade_xp table). Prediction for the next
  Stage reading: a Voidbreak display should imply base ≈ 12.8-12.9k if the
  ~2.02 ratio persists (unverified).
  Calculator note: the Respira input asks for the DISPLAYED per-attempt
  value, which already includes the books — no engine change needed; a
  per-Stage pre-fill would need base × (1 + user's books %). (Display quirk, player-clarified 2026-07-15:
  the cultivation screen labels cultivation-XP gain floats as "MP +x" —
  passive ticks and Respira procs alike — so these ARE cultivation-XP
  readings, not mana.)
- Guide corroboration: "do respira for Incarnation before breaking through,
  these will reset" (2026 community guide) — value is keyed to current Stage.

Engine note: no derivable formula — the Respira input stays user-entered.
A per-Stage lookup of measured constants (Nascent 4,041 / Incarnation 8,173)
could pre-fill the field as a suggestion once more Stages are recorded.

## Client-string findings from the sources-shelf sweep (2026-07-15)

From the APK i18n corpus (apk_analysis/om/allbc/cfg_us_i18n_*.luajit,
strings extraction; values in %d templates are server-side):

- **Ascension Virya tier ladder (official names)**: Completion (rating 1),
  Eminence (3), Perfection (5), Half Step (7) — es row corroborates. The
  community "Perfection (C)"/"Perfect" tier names collide with Stage names;
  mapping Eminence=+20pp / Perfection=+20pp+windowed is PLAUSIBLE (Blessing
  Rewards 1/5 match the observed tiers) but not tooltip-verified.
- **Creation artifact upgrade semantics**: "increases to / reduces to"
  wording — Vase refined-pill EXP tiers +10% → +20% → +30% → +40% and
  Mirror Duplication cost −5% → −10% REPLACE the prior tier, not stack.
  The +30/+40 Vase tiers were previously unknown (star mapping unstated).
  Artifact energy at 0★: 1 per Taoist Year, cap 200; charge = 30 Fateum
  for +100. Mirror copy range: Incarnation+ pills of any quality.
- **Star Marks**: granted by the Constellation Altar (Samsara/
  reincarnation system), five quality ranks; pill-color marks by Mansion:
  Ghost = Rare (blue), Turtle Beak = Epic (purple), Chariot = Legendary
  (gold); Dipper = "Respira Aura Bonus" (a distinct stat from the
  Respira EXP book %); Horn/Neck = Abode Aura. Per-level values
  server-side.
- **Technique tier structure**: special effects activate at Tier 3/6/9
  (higher books also have 12/15); low-rank books cap at Tier 6 per the
  achievement census. ~45 technique books exist in total; roughly half
  are uncataloged for calculator effects (values server-side).
- **Respira attempts reset** on main-Stage breakthrough (client rule
  string), consistent with per-Stage Respira planning.
