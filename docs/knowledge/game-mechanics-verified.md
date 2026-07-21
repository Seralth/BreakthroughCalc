# Verified game mechanics (in-game ground truth)


Verified from Seralth's in-game screenshots (2026-07-07, Incarnation (L) Middle G1, Mortal World Epic extractor, tracks Culti 20 / Quality 15 / Gush 14). Engine implements these since the model-overhaul commit after v2.6.1:

- **Pills/Respira are flat daily XP** (pill panel shows absolute XP and % of grade XP; 112.7K/1,412,392 = the displayed 7.98%). Modeled per-row: rate = speed(row)×(1+gem)/8s + daily_xp/86400.
- **Aura Gem** = claimable storage accruing gem% × cultivation speed (16/20/24% = Rare/Epic/Legendary, 18–32h cap per claim). Multiplies cultivation speed only, NOT pills/Respira. Donk's sheet's time/(1+gem)/(1+pills) was wrong on both counts. NUMERIC PIN (Seralth 2026-07-15): at culti speed 103.012/8s (=1.1125M/day), Legendary gem storage caps at exactly 356.01k = 24% × speed × 32h — confirms both the 24% rate and the 32h cap to the point. The continuous-income approximation is exact iff claimed ≥ every 32h. Claimed XP is a transferable flat stream: PLAYER-CONFIRMED (Seralth
  2026-07-15) the gem accrues off the HIGHEST path's speed regardless of
  settings, and the claim lands on whichever path is set as "cultivating" —
  swap-to-aux → claim → swap-back transfers the full amount at zero loss.
  SECOND PIN (2026-07-18, from the 2026-07-17 batch): at speed 159.78/8s the
  Legendary cap reads 552.21K = 0.24 × (159.78/8) × 32h to the digit.
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
- Extractor at highest server Stage: base fruit EXP +50% (= `fruit_highest_rank`). Extractor quality/bonus reset to Common/0 on REALM ascension only — owner-corrected 2026-07-17: e.g. mortal → Spiritual; stage breakthroughs within a realm (Nascent Soul → Incarnation) do NOT reset it. Leftover fruits of the previous realm auto-consume at pre-upgrade rates. (Earlier "main-Stage breakthrough" wording here and in the app docs was wrong; app fixed same day.)

Tests in tests/test_engine.py class ScreenshotGroundTruth2026_07_07 pin all of this. Related: [[fruit-ranks-no-r4-r5]].

## 2026-07-17 screenshot batch (~/Pictures/virya-extractor-techniques-2026-07-17/)

Player state: Nascent Soul (M) Late G3 (secondary), Incarnation (L) Completed
(primary, No.1), abode 266.30, absorption 40.00% +20.00%, speed 159.78,
Legendary gem, extractor Mortal World rank / Culti 23 / High Rank 14 /
Quality 30 / Gush 22.

- **"Next Breakthrough: Year N" display convention (verified)**: N = remaining
  grade XP ÷ raw cultivation speed, in Taoist Years of **900 s (15 real
  minutes)** — no gem, no pills. Reproduced exactly: (1,095,950 − 514,390) /
  (159.78/8) / 900 = 32.353 vs the on-screen "Year 32.353"; two more shots
  match at their own progress values. Consistent with the artifact-energy rule
  "1 per Taoist Year" = 1 per 15 min. The figure is a countdown (duration),
  not an age.
- **Blessing pp are additive percentage points — now screenshot-verified**:
  the Cultivation Bonus panel shows "40.00% +20.00%" (Incarnation Late base
  band + Perfection (C)) and speed = 266.30 × 0.60 = 159.78 exactly (60%,
  not 40% × 1.2 = 48%). This resolves the tooltip-grade check the blessing
  section below listed as pending. Composition ORDER vs Strive is NOT
  distinguishable here (player is No.1 ⇒ Strive 0, both orders coincide);
  that remains client-string-sourced. Perfection (C) activated between
  2026-07-15 (speed 103.012, absorption 0.40, abode 257.5) and this batch —
  which also confirms the primary broke Incarnation Completion this week.
- **5R pill panel, four qualities**: displayed per-pill XP 124.99K / 62.5K /
  33.33K / 20.83K = exactly {96,000 / 48,000 / 25,600 / 16,000} × 1.302 —
  confirming the pill_xp 5R gold/purple/blue values, pinning the player's
  total pill bonus at +30.2% uniformly, and revealing a FOURTH (green)
  quality with base 16,000 that the pill_xp table (gold/purple/blue/mythic)
  does not carry. The engine does not model green pills; at 5R a green is
  worth 0.625× a blue.
- **Nascent LATE ladder — TABLE CONFIRMED (2026-07-18)**: the flat gauge
  at Nascent Soul (M) Late **G4** read **7946/1295213**;
  data/breakthrough.json has **1,295,214** — a match to the digit (±1
  rounding). Nascent MIDDLE G5 also matched on 2026-07-16, so the Late
  ladder is NOT drifting and the table stands. The earlier G3 note (live
  1,095,950 vs table 1,087,558, −0.77%) is now treated as a one-off
  misread: G3/G2 = 1.193 and G4/G3 = 1.191 form a smooth progression that
  1,095,950 would break (it implies 1.202 then 1.182). No patch — the
  table was right. Tip for future spot-checks: the home-screen progress
  display toggles between % and the flat current/total EXP (tap it); the
  flat form is what verifies a denominator.
- **Extractor track caps (owner-stated 2026-07-18, UNVERIFIED on screen)**:
  the tracks continue past the displayed /25 to level 30 — the "Upon
  reaching Mythic Lv. 26" tooltip lines are the 26+ band perks (Culti:
  Mythic Aura Orb EXP +20%; Gush: trigger rate +5%, matching the data
  table's gush_chance 0.30 → 0.35). PLAUSIBLE INFERENCE (unconfirmed):
  extractor rarity is keyed to track-level bands (Epic ≤20 / Legendary
  21–25 / Mythic 26–30 — fits the 2026-07-07 "Epic at Culti 20" and
  tonight's Legendary-cap gem-adjacent readings). OPEN QUESTIONS for the
  post-ascension screenshot: does the world reset wipe TRACK LEVELS or
  only rarity + the +50% bonus ("quality/bonus"), and do unspent souls
  (upgrade mats; owner income 1,600/week) persist across it?

## Fruit ranks


The `fruit_xp` table in data/breakthrough.json (R3, R6–R12) is complete despite the apparent gap. Per Seralth (2026-07-06): fruit ranks map to realm bands — R3 covers Nascent through Voidbreak, R6 starts the Spiritual world, R12 starts the Immortal world. R4/R5 were never omitted; they don't exist as fruit ranks. Don't flag this as missing data in future audits. (2026-07-17 Worlds cross-ref: "through Voidbreak" = up to the Voidbreak GATE — the Spiritual band R6 begins AT Voidbreak, the stage that opens the Spiritual World; see the Worlds section.)

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
  COMMUNITY-CONFIRMED (multiple independent players, repeatedly, via
  Seralth; label upgraded from ASSUMED 2026-07-16 — do not re-hedge this):
  blessing pp apply in full while overcapped — they are an absorption-band
  bonus, not Strive. This underpins both the prestock ceiling math and the
  park-in-Early meta.
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
  SPIRITUAL World (Voidbreak; the "Immortal World" reading recorded here
  earlier was wrong — see the Worlds section below). No other mortal-world
  stage has it.
- Grade ladders per dump (matches data/breakthrough.json): Incarnation Early
  G1–G8, Middle G1–G9, Late G1–G15.
- Completed/Perfected is not an extra XP band — breakthrough.json's
  Incarnation Late G15 row already covers the XP to reach it. Ascension
  itself is event/quest-gated ("Path to Ascension is not yet unlocked.
  Unable to ascend."), which the time calculator does not model.
  RESOLVED (2026-07-15/16): cultivation XP does keep accruing while sitting
  in Completed awaiting ascension — see "Timegate overcap / XP prestocking"
  above (capped-row rate, de-strived, blessing pp apply in full; the
  440%/404% community data points are players stocking in exactly this
  state). Note the Completion breakthrough itself is required first: the
  Virya tier text reads "Reach Incarnation (L) Late 100% and break
  through" — a full gauge without the breakthrough starts nothing
  (owner-reconfirmed 2026-07-17).

### Worlds: the full realm ladder (2026-07-17, dump i18n sweep)

The 13 stages group into three Worlds. Dump enumerations: sect relocation
"(Mortal World/Spiritual World/Immortal World)"; Ethereal Residence rules
"As the Realms of [Human - Spirit - Immortal] progress" (de: Mensch –
Geist – Unsterblich); abode skins listed per world.

- **Mortal World**: Novice, Connection, Foundation, Virtuoso, Nascent
  Soul, Incarnation — ends at Incarnation (Perfected).
- **Spiritual World**: Voidbreak, Wholeness, Perfection, Nirvana —
  entered by ASCENSION at the first world timegate (~server day 35–38).
  Boundary evidence (system strings, not flavor): server transfer
  "unlocks at server age 40 days ... Taoists of Voidbreak or higher" /
  "30 days after Spiritual World unlocks" (day math only works if the
  VB gate = Spiritual World unlock); multi-path help text "Dual
  Cultivation Gear offers powerful stats after you ascend to the
  Spiritual World... Virya stats ... may remove Pill usage restrictions"
  (= the Ascension Virya system at this gate); quest line "Ascend to the
  Spiritual World to unlock more content"; owner usage 2026-07-17
  ("mortal to spirit") for the extractor reset at this gate.
- **Immortal World**: Celestial, Eternal, Supreme — entered by
  TRANSCENDENCE ("A Taoist can transcend to the Immortal World with the
  Transcendent Token"; server milestones "Immortal World Rift",
  "Immortal Transcendent"). Celestial-stage gear crafts from "Immortal
  World" materials.

Alignments that fall out exactly:
- **Pill ranks are per major STAGE**, not per world: Connection=1R …
  Incarnation=5R, Voidbreak=6R … Supreme=12R — 12 ranks = the 12 stages
  after Novice, exact.
- **Fruit ranks are per WORLD band**: R3 = mortal band, R6 starts the
  Spiritual world (= Voidbreak), R12 the Immortal world (= Celestial).
  The older phrasing "R3 covers Nascent through Voidbreak" should read
  "up to the Voidbreak gate". UNMAPPED: how R7–R11 distribute inside the
  Spiritual world (6 ranks, 4 stages — doesn't fit 1:1; don't guess).
- **Extractor resets at WORLD boundaries only** (owner-corrected
  2026-07-17): Incarnation→Voidbreak and Nirvana→Celestial. Stage
  breakthroughs within a world never reset it.
- FLAVOR-TEXT ANOMALIES (event/NPC dialogue; do not trust over the
  system strings): a Stellar Ceremony line calls Voidbreak attendees
  "mere mortals" who may yet "ascend to the Spiritual World"; a White
  Astra quest at Voidbreak (Early) speaks of the Spiritual World as
  still ahead; one clan story has Incarnation (Late) seeking "the
  Immortal World". Loose localization.
- **Immortal Friends unlock at Voidbreak+** (owner, 2026-07-17: not
  accessible at Incarnation (L) Late) — the guide's placement of the
  friend priorities on the Voidbreak+ page is correct; don't propose
  moving them earlier.
- OPEN (revisit): the **"Spiritual Leap"** event — dump strings show
  rewards "for Taoists in Spiritual Leap" and that servers WITHOUT the
  event get server transfer "30 days after Spiritual World unlocks".
  Looks like a catch-up/transfer-adjacent server event; unmapped, owner
  unsure too (2026-07-17). Not referenced anywhere user-facing.

### Ascension Virya blessings (2026-07-15 screenshots; stacking corrected 2026-07-20)

Provenance: "Ascension Virya" screen (2026-07-15, Incarnation (L) Late G12,
blessing rank No.1 → 6 reward vases); dump strings corroborate
(圆满后境界精进可增加福泽奖励; templates '%s Absorption Ratio + %s%%',
'Absorption Ratio Before %s: + %s%%'); live absorption reading 2026-07-20
(Cultivation Bonus panel, Abode 270.20 × 0.60 = Speed 162.12).

**CURRENT MODEL (what to trust):**
- In Incarnation the Virya absorption bonus is **+20% FLAT — the tiers do
  NOT stack** (owner, 2026-07-20, own account: at Perfect the absorption read
  the same "40 + 20" as at Perfection (C)). Arithmetic confirms and rules out
  the alternatives: Abode 270.20 × 0.60 = Speed 162.12 = base 0.40 + Virya
  0.20; a stacked +40 would give 216.16, +60 would give 270.20 — only flat
  +20 matches. The tier's "Before Voidbreak (L) Middle +20%" line is
  therefore **dormant in Incarnation** (were it live, speed would imply 0.80).
- The pp are **ADDITIVE** (40 + 20 = 60, not 40 × 1.2 = 48). The base 0.40 =
  Incarnation Late `low` band at Strive 0 (parked).
- **Official formula** (client rules text + dump): Cultivation Speed = Abode
  Aura × Absorption Ratio (× Heavenly Power Bonus); Absorption Ratio =
  (Base Stage Absorption + Virya pp) × (1 + Strive Bonus) — i.e. the pp join
  the STAGE BASE *inside* the Strive multiplier, not the displayed total. The
  Virya bonus is scoped to the current Stage (dump: "Aura Absorption Rate
  +%d%% in Current Stage"; %d is server-side). Composition ORDER vs Strive is
  client-string-sourced only — the live check ran at Strive 0, where both
  orders coincide.
- **Engine model**: two pp inputs — `bless_pp` (persistent) and
  `bless_window_pp` (conditional, rows before Voidbreak MIDDLE) — applied
  per-row as speed(row) = abode × (low_row + bless(row)) × (1 + strive). The
  entered absorption is the on-screen TOTAL; the engine recovers true Strive
  as absorption / (low_cur + bless_cur) − 1, so implied-Strive is not
  contaminated for blessed accounts (a base-40% account with +20pp at Strive
  s displays (0.40 + 0.20) × (1 + s)). As of v3.11 the shelf derives
  `bless_pp` = 0.20 (flat, one tier) and no window — the Voidbreak windowing
  is left unmodeled pending a reading.

**Tier ladder (observed 2026-07-15).** Effects below are each tier's *listed*
grants; what actually goes live in Incarnation is the flat +20 above.
- **Completion** (Reach Incarnation (L) Late 100% and break through):
  "Remove Realm Restrictions for Taking Cultivation Pills"; "Cultivation Pill
  Auto-Transmogrification Privilege"; Blessing Rewards +1; "First Esotability".
  Both privileges concern **BREAKTHROUGH pills, NOT XP/cultivation-XP pills**
  (owner-corrected 2026-07-21 — the earlier "removes realm restrictions so
  higher-stage XP pills feed the lower path" reading was WRONG). The
  auto-transmog converts breakthrough pills two ways: (a) **DOWN-RANK** — turn
  a higher-rank breakthrough pill into a lower-rank one, so you never farm
  lower areas to make low-rank breakthrough pills; (b) **CROSS-PATH** —
  convert magic ↔ physical breakthrough pills of the SAME tier. Net: your
  breakthrough-pill stock becomes fungible across rank and path, which is what
  actually funds a secondary-path rush — there is no XP-pill sharing here.
- **Perfection (C)** (primary Incarnation (L) Completion; secondary Nascent
  Soul (L) Late; clear Amethyst Fiend in Myrimon Wonder): "Incarnation (L)
  Aura Absorption Ratio +20%"; Blessing Rewards +3.
- **Perfect** (gold; secondary Incarnation (L) Middle; clear Jade-Eyed Lion):
  lists BOTH "Incarnation (L) Aura Absorption Ratio +20%" AND "Absorption
  Ratio Before Voidbreak (L) Middle: +20%"; Blessing Rewards +5; "Second
  Esotability".
- Secondary-path stage reqs are **REACH, not complete** (owner-confirmed
  2026-07-16): satisfied on entering the named half-step.

**Calculator impact.** The engine's projection cancels the entered absorption
ratio (speed(row) = culti_speed × low_row / low_cur) — valid only when
bonuses scale all rows uniformly. A realm-WINDOWED bonus breaks that
cancellation (windowed rows run faster than the base-band progression
predicts); same class of issue for the +200% post-ascension privilege. Both
are additive pp per the formula, so they're modeled as pp inputs, not
multipliers. A secondary-path projection would also see a bigger flat
daily-XP term (better pills fed to it) on top of the absorption bonus.

**Other observed facts.**
- The "Double" badge between tier circles is NOT a tier (unclickable, per
  Seralth). Plausible: the active-Virya status badge (dump: 'Double' = 双;
  ">Within {1} hours, receive {3}x {2} Cosmoapsis gains") — i.e. a
  ×2-Cosmoapsis session while its countdown runs. Verify by comparing the
  /Cosmoapsis readout during vs after the timer.
- Blessings are **per cultivation path** (screen/status bar use the (L)
  primary suffix; confirms path letters beyond M/C/P, cf. elixir L/G/M/C/S).
- XP cross-check: the screen's Late G12 denominator 5,623,090 matches
  data/breakthrough.json Incarnation Late G12 grade_xp exactly.
- Dump rank→reward table: Blessing Ranking 1→6, 2→5, 3→4, 4–10→3, 11+→2
  (matches No.1 ⇒ 6 vases). Post-ascension privileges (dump): Absorption
  Ratio +200% plus high-stage pill access.

**Open / unverified (do NOT assert).** Whether the +20% persists past
Incarnation into Voidbreak; whether/how much the "Before Voidbreak Middle"
line activates in Voidbreak Early (its ceiling is VB Middle start — the dump
template is literal — but its floor is NOT Incarnation, so it's at most
Voidbreak-Early-only, value TBD); the Half Step tier; tiers beyond the three
observed; the post-ascension privilege structure. Owner is timegated out of
Voidbreak until ≈ 2026-08-03.

**Correction history (compact).**
- 2026-07-15: initial screenshots; community model had the tiers STACKING to
  +40 persistent / +60 before VB Middle (two players, one ~90% self-rated).
- 2026-07-17/18: additive-pp screenshot-confirmed (40% + 20% → effective
  60%, not 48%). Composition SUPERSEDED to the official (base+Virya)×(1+Strive)
  from the i18n corpus sweep.
- 2026-07-20: owner's OWN account overturned the stacking — flat +20 in
  Incarnation, tiers do not stack; +40/+60 RETRACTED. **Lesson: three
  concurring players were wrong here; direct observation supersedes community
  consensus.**
### Cultivation-XP pill economy (owner-confirmed 2026-07-21)

- **XP / cultivation-XP pills are fungible across BOTH paths and ALL tiers.**
  Any such pill feeds any cultivation path regardless of rank; a higher-tier
  pill simply grants more XP per use (a Voidbreak pill on an Incarnation path
  just gives more than an Incarnation pill would). This is a base mechanic, NOT
  the Completion blessing — that privilege is breakthrough pills only (see the
  Virya Completion tier above). Throughput is throttled by the per-day pill
  attempt cap (scales with realm; see elixir-sense-mechanics.md).
- **Fate Pavilion cultivation bags**: a daily reward giving one bag set per
  cultivation path (main + off), each tier-aligned to that path's current
  realm — so once the main ascends, its bags mint the higher-tier pill while an
  un-ascended off path's bags stay a tier behind (this is the whole lever
  behind "level the off path to Voidbreak to upgrade its bags"). Bags roll
  purple/gold cultivation pills; the exact purple:gold split is UNCONFIRMED
  (owner's read is anecdotal and he was told his luck runs high — do NOT treat
  any ratio as a drop rate). Daily bag count is per-account (scales), not a
  constant.

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
  mean of a distribution that includes ×2 rolls. RESOLVED (see the
  +28%-exact anchoring below): the on-screen value DOES include the +28%
  technique books; the unbuffed Incarnation base is **6,385** (× 1.28 =
  8,172.8 → 8,173).
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
  Artifact energy at 0★: 1 per Taoist Year, cap 200; charge = 30 Fateum
  for +100. Mirror copy range: Incarnation+ pills of any quality.
  Starsea Vase star scaling (owner-read 2026-07-21): energy regen is
  progressive 0★ 1 → 2★ 1.6 → 3★ 2 per Taoist Year; cap 0★ 200 → 1★ 300
  → 2★ 400 → 3★ 500 (= 200 + 100/star; 4★/5★ predicted 600/700, unread).
  SPECIAL effects appear ONLY at stars 1, 2, 5 (before the
  awakening effect) — 3★/4★ improve only base regen/cap. So the EXP-bonus
  mapping is 1★ +10%, 2★ +20% (NOT 3★ — earlier note corrected), 5★ 15%
  no-cost refine; the dump's +30%/+40% EXP tiers are then most likely the
  AWAKENING progression, not star tiers (unconfirmed). Open: exact 1★/2★
  EXP values from tooltip, the awakening effect, 1★/4★ regen, 4★/5★ cap.
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
