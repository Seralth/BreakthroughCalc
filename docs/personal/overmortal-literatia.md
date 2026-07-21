# OverMortal — Literatia class mechanics & PvP (personal reference)

Personal notes for InkedSeralth's Literatia PvP build. **Not** part of the calc —
reference only. Sourced from the client APK decompile (`apk_analysis/om/`) plus
in-game tooltips and fight reports. Verified-from-config vs inference is flagged
throughout; confident-wrong is the worst failure mode.

Context: Literatia is extremely rare — on this server InkedSeralth is the *only*
Literatia player among hundreds; ~99% are Swordia or Ghostia. The two top players
are Ghostia. Primary path Literatia, secondary Magicka. Realm: Incarnation (L) Late.

---

## 1. Core resource: Erudition (文气 `wenqi`)

Official in-game help string (`cfg_us_helper_tip.lua`, key `wenqi`), verified:

> Use Abilities/Relics with **[Boundfree]** (浩然 `haoran`) to accumulate Erudition,
> **cap 300**. Use Abilities/Relics with **[Summit]** (入圣 `ru_sheng`): if Erudition
> is high enough, both the appearance and effects are enhanced. **If no Erudition is
> gained for 30s, it resets to 0.**

Internal names: Erudition = 文气 `wenqi` / `ru_energy`; [Boundfree] = 浩然;
[Summit] = 入圣; condition key in skill configs = `ru_energy_need`.

## 2. [Summit] — how it actually works (verified)

- Summit is a **cast-time threshold check**, not a resource cost. It does **not**
  consume Erudition (that's Literal Reality's job). Skill fires with its Summit
  payload **if** current Erudition >= `need` at the instant of the cast; otherwise
  the base version fires.
- Implemented as `skill_mod = "skill_ru_energy_effect"` with
  `mod_args = { need = N, <payload> }`. The runtime
  (`managers_combat_effect_arpg.lua`, `get_level_effect`) selects the enhanced
  animation/effect sequence per-cast via `sequence_with_args` keyed on `need`.
- **No recast / no cooldown-bypass.** The community theory that a Summit skill
  "recasts when you cross the threshold even on cooldown" is FALSE — nothing in
  the configs does this. (The engine *does* have `reset_skill_cd_if_target_dead`,
  used by a Swordia skill, so such a mechanic would be visible if present.)
- Thresholds can be reduced by skill level-up riders (e.g. a shield skill drops
  200->150 at level 60).

Summit payload types seen in config: `add_damage`, `apply_status`, `extra_hit_time`,
`extra_attack_scale`, `damage_with_hit_time`, `damage_with_mp_max`,
`damage_with_hp_percent`, `crit_percent_up`, `apply_skill`, shields, HP recovery,
Immunity, Curse, Finishing Touch.

## 3. [Boundfree] — generation (verified)

Boundfree riders spend a % of max MP to grant Erudition. Equipped-kit values:

| Source | Erudition | Notes |
|---|---|---|
| Speech - Word of Kindness | +50 | 2% MP |
| Unleashed Ink | +50 | 2% MP, 13s cd — best sustained generator |
| Master's Hand | +25 | 1% MP |
| Primeval Inkstone (each) | +25 | 1% MP, 24s cd |
| Speech - Hidden Hook | +75 | 3% MP, **but capped: will not raise you past 200** |
| Speech - Threefold Reflection | **0** | generates nothing — pure Summit payoff |
| Windwalker (borrowed Magicka shield) | **0** | no Erudition; 31.6% MP shield, 11s |

## 4. Literal Reality (知行合一) — the payoff (verified tooltip)

- **Auto-casts the moment Erudition hits full (300).** Does not need to be equipped.
- **Consumes ALL Erudition** -> deal 1300% M.DMG to target + M.DMG = 20% of max MP.
- Levels up with each major Literatia Stage breakthrough; Stage Penalty scales with
  the gap between primary path and Literatia (+10%/Stage, up to 80%).
- Because it empties the bar to 0, the rotation is a continuous **0->300 cycle**, NOT
  "sit pinned at cap." Design goals: (a) LR detonates *inside* a Scorch window,
  (b) Summit skills cast on the way *up*, and (c) the post-LR hole (0 Erudition for
  a few seconds) is refilled by recycling generators.
- On InkedSeralth's **current** stats (max MP **310M**; M.ATK ~4.13M observed on the
  Harmony screen — up from the 3.11M baseline this section was first written at) LR =
  1300% M.DMG + 20% max MP = a **+62M flat** chunk on top of the coefficient. Single
  biggest hit, and enough to one-shot a ghost thrall (thrall HP ~10–20% of caster HP,
  §8) for a guaranteed taunt-free window. ~2–3 casts/fight.

## 5. Equipped Summit / relic skills (verified from `cfg_us_skill`)

Skill IDs for future lookup:

| Skill | ID | CD | Summit (`need` -> effect) |
|---|---|---|---|
| Speech - Threefold Reflection | 5907 | 15s | **200** -> +1 hit (2->3 hits). Base `hit_time=2`. |
| Speech - Hidden Hook | 5909 | 16s | **250** -> +15% dmg + Scorch (id 1168, M.DMG taken +12%, 5s) |
| Speech - Word of Kindness | 5905 | 25s | shield |
| Lotus Dreamscape (清荷画境) | 5911 | 15s | **100** -> apply_status; 2-target 213.2%; +50 Erudition when <100; **purify at skill lvl 20** (NOT YET UNLOCKED, far away) |
| Speech - Heaven's Way (天行健) | 5923 | 25s | +100 Erudition Boundfree + purify rider at lvl 20 (NOT unlocked) |

Curio relics (3 slots, do not interchange with equipment relics):

| Curio | CD | Effect | Notes |
|---|---|---|---|
| Fire Lotus | 60s (-20% at 5-star) | 5x 105% M.DMG single-target, +15% Curio DMG (star) | rating 8.37M; all on one target |
| Dragonpit Sword | 60s | 3x 282% M.DMG single + HP Regen Down (-50%, 8s) | rating 8.37M |
| Cosmic Demon Spire | 60s | 595% M.DMG + Exorcism (+20% vs **Monsters**, 8s) | PvE-only buff; PvP = plain nuke |
| Soul-destroyer | 60s | 300%x2 hits x2 targets + MP Regen Down (-60%, 8s) | benched vs Ghostia (see section 8) |

Equipment relics (6 slots: 5 inkstones + 1 brush):

| Relic | CD | Effect | Erudition |
|---|---|---|---|
| Primeval Inkstone | 24s | 356% M.ATK x2 targets | +25 (Boundfree) |
| Primeval Brush | 21s | 386% M.ATK single-target; **Summit 100 -> +25% dmg** | none |

## 6. Shield-queue mechanic (in-game observed)

Shields **queue** — you cast shield #1, and the next shield does not fire until the
first expires (it takes the next available cast slot). Consequence for ramp math:
Windwalker's cast (and anything riding it) lands *whenever shield #1 drops*, not at
its slot position. Since Windwalker generates 0 Erudition this doesn't hurt the ramp,
but it means any Windwalker rider (e.g. advancement immunity) is **uncontrollably
timed** — you cannot align it with a specific cast like Literal Reality.

## 7. Targeting modes (in-game)

Four modes: (1) closest, (2) highest HP%, (3) lowest HP%, (4) lowest HP+MP.

**Vs Ghostia use HIGHEST HP% (mode 2).** Ghost thralls are almost always the lowest-HP%
units on the field, so lowest-HP% targeting glues your single-target casts (Brush,
Fire Lotus, Dragonpit, Spire, Literal Reality) onto thralls instead of the player.
This was the single biggest fix — see section 9 fight data (true-form damage ~doubled).

## 8. Ghostia matchup (the real problem)

Ghostia (`gui`) = summoner class (213 config skills, dominated by
`summon_ghost_or_link`, `summoned_ghost_order`, `summoned_ghost_recovery`,
`summoned_ghost_energy`, `absorb_soul`, `cumulate_damage_debuff_enhance`). Relic line
= soul banners (魂幡, 16–20s cd). Their sustain is **ghost-driven shields/recovery**,
NOT HP/MP regen (both regen lines read 0 in fight reports — so Soul-destroyer's MP
Regen Down and Dragonpit's HP Regen Down do nothing against them in practice).

### Primeval Mask (their core relic) — verified from opponent's tooltip
- 5x Masks + 1 banner (banner summons the ghost, mandatory 6th slot).
- Each Mask: Ghost Thrall deals 195% M.ATK x2 targets, 13s cd, **80% chance to
  Taunt (3s)**, +5 Berserk Energy/hit, Ghost Thrall HP Inheritance +10%.
- 5 Masks on 13s ~= one 80% taunt roll **every ~2.6s** -> near-permanent taunt pressure.

### Taunt (verified classification)
- Status id 1165: `type="TAUNT"`, `alias="控制"` (control), `buff_type=-1` (negative).
  "Units under taunt can only target the taunter."
- Immunity (id 1152, "免疫负面状态" = immune to negative status) **does block taunt**
  (taunt is a negative status). Purify effect cleanses poison/root/freeze/**taunt**.

### Ghost thrall behavior (in-game)
- On death it does NOT vanish-and-resummon; it **regenerates to 100% over a few
  seconds, during which it cannot act or be targeted.** Killing it = a guaranteed
  taunt-free, Mask-free burst window (but unschedulable). Thrall HP is only ~10–20%
  of caster HP, and it delivers 39–48% of their total damage — a real point of failure.

### Counters (in priority order)
1. **Highest-HP% targeting** (section 7) — biggest lever, free.
2. **Multi-target relics leak past taunt** — inkstones/Soul-destroyer hit 2 targets, so
   the 2nd hit reaches the real player even while the primary is taunt-locked onto the
   thrall. Single-target casts (Brush, Fire Lotus, Dragonpit, Spire, LR) get fully
   hijacked by taunt — this is the true RNG exposure.
3. **Fire Lotus over Soul-destroyer** (curio swap) — vs Ghostia, Soul-destroyer's MP
   debuff is dead weight and half its 2-target damage feeds a thrall; Fire Lotus
   concentrates 525%+15% on the real target under highest-HP% targeting.
4. **Lotus Dreamscape** (purify + 2-target + gen) is the eventual real answer — but
   it is FAR away and won't be available for a long time.

## 9. Fight data (DeliciousJev, Ghostia 1.04B BR vs our 1.03B)

Same opponent, same 1:17 duration, before/after the fixes:

| Metric | LOSS (before) | WIN (after) |
|---|---|---|
| Our total DMG | 539.76M | 665.86M |
| Their total DMG | 550.48M | 469.13M |
| **DMG reaching their true form** | **83.36M** | **155.65M** |
| Literal Reality casts | 2 (142.8M) | **3 (218.6M)** |
| Their Primeval Mask | 25 casts / 200M | 21 casts / 137.58M |
| Control (us vs them) | 6.2s / 3.8s | 5.1s / 1.9s |
| Result | Lose (them 26.9% HP) | **Win (them dead, us 11.1%)** |

Changes that produced the swing: highest-HP% targeting (true-form damage ~doubled),
Fire Lotus in for Soul-destroyer, Spiritual Wall added as 3rd shield (dragged the loss
to 1:17 in the first place). The loss was decided by damage *placement* (60% of our
damage went into ghosts) and one missing LR — NOT raw DPS (we out-damaged them both times).

## 10. Current loadout & casting order (PvP, vs Swordia/Ghostia) — SUPERSEDED by §15

> **SUPERSEDED (2026-07-21).** The Scorch-window plan below relied on timing curios into
> a 5s window, but skills fire blindly in priority order on cooldown (§15) — that timing
> was never fully controllable. Replaced by the shield-pierce / burst-ghost build in §15.
> Kept here for the fight-data context (§9, §12) it feeds.

Abilities: Speech - Word of Kindness, Windwalker (borrowed Magicka shield),
Spiritual Wall (borrowed shield, 38.4% MP / 9s — swapped in for Threefold Reflection),
Unleashed Ink, Master's Hand, Speech - Hidden Hook.
Curios: Dragonpit Sword, Fire Lotus, Cosmic Demon Spire.
Equipment: 1 gold + 4 purple Primeval Inkstones, 1 gold Primeval Brush.

Order (Shield First ON; shields 1–3 queue):
1. Word of Kindness (+50)
2. Windwalker (queues; 0 Erudition)
3. Spiritual Wall (queues)
4. Unleashed Ink (+50 -> 100)
5. Master's Hand (+25 -> 125, stun)
6-9. Purple Inkstones x4 (-> ~225)  ·  gold Inkstone as needed to reach 250
10. **Hidden Hook** — Summit yes 250 -> Scorch (M.DMG taken +12%, 5s)
11. **Dragonpit Sword** — in Scorch (HP Regen Down largely wasted vs Ghostia)
12. **Fire Lotus** — in Scorch, concentrated single-target
13. **Cosmic Demon Spire** — tail of window (Exorcism useless in PvP -> cast last of the 3)
14. **Primeval Brush** — Summit yes
15+. remaining Inkstone casts -> Literal Reality auto-fires at 300
    (monsterforms now UNEQUIPPED — see section 12; they blocked main-track slots
    in longer fights for the worst per-slot value on the track)

The three 60s-cd curios are once-per-fight -> they take the guaranteed FIRST Scorch
window; LR recurs 2–3x/fight so it catches later windows.

## 11. Gear-upgrade decisions (settled)

- **First forged gold inkstone -> replace a PURPLE inkstone, not the Brush.**
  Purple->gold is a *strict* stat upgrade (same skill/gen): +24.5% bonus, +50K relic
  DMG, +1 affix line, ~+2.4M BR, zero downside, keeps the Brush. Verified from +65
  tooltips (gold 11.3M BR / 170.9% bonus / 5 affixes vs purple 8.86M / 146.4% / 4).
- **Brush -> gold inkstone** is only a *lateral* gold-for-gold move (stat-neutral) that
  trades the Brush's single-target Summit for +25 gen and 2-target taunt-leak. Consider
  only later, only vs Ghostia, once the equipment row is mostly gold. Do NOT burn the
  first gold inkstone on it.
- **Windwalker advancement (lvl 35): NOT worth it.** Grants Immunity 0.3s/level (have
  mats for 3 -> 0.9s; max 5 -> 1.5s) + 0.2%/level MP shield. Immunity *does* block taunt
  (verified section 8), BUT 0.9s on an uncontrollably queue-timed cast blocks at most ~1
  of the ~15–25 taunt rolls per fight, can't be aligned to protect Literal Reality, and
  the shield bonus (+0.6% -> ~+1.3M absorb) is noise. It's a strictly worse stand-in for
  Lotus Dreamscape's purify — do NOT delay Lotus for it. **(This dismisses the lvl-35
  *advancement* only — Windwalker's base 25% magic evasion is a core keep vs magic
  classes; see §15.)**

## 12. Cast-slot economics & Magicka-stun evaluation (2026-07-14 fight report)

Source: fight report vs DeliciousJev (Ghostia, 1.04B vs 1.04B) — **Loss, 1:11 (71s)**,
Damage + both Defence tabs. In-game observed cast pacing: ~2.5s per main-track cast
("2–3 mississippi"), so a 71s fight ≈ 28 main-track slots.

### Verified structural facts

- **Pets and Zodiac skills run on their own cast tracks** (secondary units) — they do
  not consume main-track slots. Monsterforms DO block the main track while casting.
- **The main track runs fully saturated.** This fight: 6 inkstone + 4 Master's Hand +
  4 Unleashed Ink + 3 Hidden Hook + 2 Brush + 3 curios + 2 monsterform + ~6 shield
  casts ≈ 28–30 casts = the entire slot budget. Cooldowns are NOT the constraint —
  the 5 inkstones could have fired ~15x on their 24s CDs but got 6 (40% utilization).
  **Every ability swap is a slot-for-slot trade; there is no slack.**

### Per-slot value (this fight, damage dealt or absorbed per cast)

| Cast | Unleashed | Per-slot value |
|---|---|---|
| Literal Reality (auto) | 2 | 74.2M |
| Spiritual Wall | 2 | 66.1M absorbed |
| Windwalker | 1 | 58.4M absorbed |
| Word of Kindness | 3 | 32.7M absorbed + 50 gen |
| Primeval Brush | 2 | 20.7M |
| Primeval Inkstone | 6 | 19.5M + 25 gen |
| Hidden Hook | 3 | 11.5M + Scorch |
| Master's Hand | 4 | 7.9M + 25 gen |
| Unleashed Ink | 4 | 7.4M + 50 gen |
| Titan Similitude (monsterform) | 2 | 3.2M |

### Decision: Magicka paralysis skill (85.5% / 2.8s) — REJECTED

Community advice was "2 borrowed shields + the stun on top of class shield" (would
have replaced Master's Hand). Rejected on this data:

- The stun is 0 damage / 0 Erudition; its value is ~1 denied enemy cast (~2.8s ≈ one
  2.5s slot). Jev's Primeval Masks average only ~6.5M/cast — so the trade is
  7.9M + 25 gen given up for ~6.5M denied. Net negative, second-worst slot on the track.
- Total generation this fight ≈ 550–600 = exactly 2 LRs. Losing Master's Hand's
  ~100/fight risks the second Literal Reality (74M/cast, top damage source).
- The loss was NOT a control problem: we absorbed 288.8M (Spiritual Wall 132.2M /
  WoK 98.2M / Windwalker 58.4M) vs their 142.8M (Soul Banner 67.5M ×3 / Windwalker
  50.9M / Soul Symbiosis 24.5M) — out-shielded them 2:1 and still lost. Ghostia has
  no keystone cast worth interrupting; damage arrives as a stream of small mask
  ticks and sustain is banner/thrall-driven. The gap remains damage *placement*
  (thralls eating single-target casts), same as section 9.
- Contested-stat reality check (see combat-mechanics.md): duration multiplier clamps
  0.5–1.25x, so the 2.8s is 1.4s vs a stacked-resist opponent.

### Decision: monsterforms — UNEQUIP BOTH

Titan Similitude: 2 casts, 6.48M total (3.2M/slot, worst on the track), and the main
track is locked while they cast. They fire in the mid-late phase of longer fights —
exactly when the LR#2 ramp needs slots. Equipping gives no passive stats, only a
hollow BR display bump. Freed slots ≈ 2 inkstone casts ≈ ~39M + 50 gen (~6x value).

### Revised opener (Master's Hand retained; if it were ever dropped)

Losing any +25 source means the 5-inkstone sweep tops at 225, short of Hidden Hook's
250 Summit. Fix: hold Hidden Hook one slot for Unleashed Ink's 2nd cast (13s CD
returns right as the ~8-cast sweep ends at ~2.5s/cast) -> 275 -> Summit. First Scorch
lands ~22–25s. Note: at 2.5s/cast only TWO casts fit the 5s Scorch window —
Dragonpit + Fire Lotus; Spire always landed outside it (its "cast last" position is
correct but it gets no Scorch bonus).

## 13. Decompile pipeline (for future skill/config lookups)

Repo: `~/Projects/BreakthroughCalc/apk_analysis/`. Game = `com.ltgames.android.m71.us`,
Unity IL2CPP + tolua (game logic/data = Lua). See `RE_FINDINGS.md`.

- Decrypted client Lua source: `apk_analysis/om/decompiled/*.lua` (config tables).
- LuaJIT bytecode bundles: `apk_analysis/om/allbc/*.luajit` — decompile with
  `ljd` (`cd apk_analysis/ljd && python main.py -f <file>.luajit`).
- Extract a bundle: `apk_analysis/.venv/bin/python apk_analysis/om/decrypt_lua.py
  <bundle>.unity3d <outdir>` (XOR key "m71", strip 12-byte prefix, UnityFS -> TextAsset).
- i18n: `apk_analysis/i18n_all.json` — **keys are the English strings**, values are
  ru/de/es/zh translations. Search keys, not values.
- Key files: `cfg_us_skill.dec.lua` (all skills; grep `job_type` — `ru`=Literatia,
  `gui`=Ghostia, `jian`=Swordia, `fa`=Magicka, `ti`=Corporia), `skill_mod.dec.lua`
  (mod definitions), `cfg_us_status.lua` (status/debuff definitions incl. taunt id 1165),
  `cfg_us_helper_tip.lua` (wenqi help text).
- **Note:** cultivation *balance* tables are server-authoritative (not in client);
  combat *skill* definitions and status classifications ARE client-side and verifiable.

## 14. Internal term glossary

| English | Chinese | config key |
|---|---|---|
| Erudition | 文气 | `wenqi` / `ru_energy` |
| [Boundfree] | 浩然 | `skill_ru_energy_produce` |
| [Summit] | 入圣 | `skill_ru_energy_effect`, cond `ru_energy_need` |
| Literal Reality | 知行合一 | (auto-cast at 300) |
| Scorch | — | status id 1168 (M.DMG taken +12%) |
| Taunt | 嘲讽 | status id 1165, type TAUNT |
| Immunity | 免疫 | status id 1152 (immune to negative status) |
| Literatia / Ghostia / Swordia / Magicka / Corporia | 儒/鬼/剑/法/体 | `ru`/`gui`/`jian`/`fa`/`ti` |

## 15. PvP respec — shield-pierce / burst-ghost build (2026-07-21)

Supersedes the §10 Scorch-window rotation. All inputs below are owner-verified in-game
(2026-07-21 screenshot/tooltip pass). Two independent findings drove the change: (a) the
Scorch plan relied on timing curios into a 5s window, but skills auto-fire blindly in
priority order on cooldown; (b) the amp-window loses to shield-pierce + splash vs Ghostia
(model at the bottom).

### Updated stats
- Max MP **310M** (was ~210M when §4 was first written).
- Literal Reality = 1300% M.DMG + 20% max MP = **+62M flat** on top of the coefficient.
- Painted Cranes Summit = +3% max MP = **+9.3M**.

### Mechanics corrections (verified)
- **Blind priority-fire.** Equipped skills fire in slot-priority order as they come off
  CD; a higher-priority skill cuts in line. NOT optional, NOT schedulable. "Shield First"
  ON makes shield-type skills lead. You control only *which 6 skills* + their *priority
  order* + the toggle. → the §10 "dump the 3 curios into the first Scorch window" plan
  was never actually controllable.
- **Esotabilities are automatic passives (no skill slot).** Literatia eso: regain 10%
  max MP when MP drops low (sustains the MP→Erudition engine). Magicka eso: large shield
  scaled off max MP when HP <50% (auto emergency shield). Both active via the "Second
  Esotability" privilege (Ascension Virya, Perfection tier). → borrowed shields
  (Windwalker / Spiritual Wall) are NOT esotabilities; they occupy normal skill slots,
  and the skill cap is **6 total** (borrowed count toward it).
- **Capstone Mortal World passive: 20% flat chance to avoid all Mortal World CC.**
  Players are unlocking it now (top Ghostia first) → our silence whiffs ~20% vs them.
- **Word of Kindness** also grants **25% M.DEF for 8s** — magic mitigation that stacks
  with Windwalker's evasion (independent anti-magic layers).
- **Windwalker** base = 31.6% MP shield (11s) **+ 25% magic evasion** — the evasion is
  the keep-reason vs a magic class (distinct from the lvl-35 advancement, §11).
- **Master's Hand is a SILENCE, not a stun** — stops enemy skills, not autos. Near-dead
  vs Ghostia: taunt hijacks the cast onto a ghost thrall (§8), so it silences the actual
  caster only ~1 duel in 5; capstone eats another 20%. Dropped.
- **Skill unlocks are level-gated, not equip-gated** — a prereq only needs to be *leveled*
  to keep the next skill unlocked; it need not stay equipped.

### Verified skill tooltips (base, current level)
| Skill | Path | Base M.DMG | Tgts | CD | Riders |
|---|---|---|---|---|---|
| Unleashed Ink | Virtuoso (L) | 438.3% | 1 | **13s** | [Boundfree] 2% MP → +50 |
| Painted Cranes | Incarnation (L) | **534%** | 1 | 17s | [Summit] @150 → +3% max MP (~9.3M); skill Lv40 lowers req 150→100 |
| Discordant Verse | Nascent Soul (L) | 318% | **3** | 16s | [Crescendo] +140% M.DMG **ignoring Shields/Barriers**; [Buff] Focus M.ATK +15% / 4s; [Boundfree] 1% MP → +25 |
| Lotus Dreamscape | Incarnation (L) | 300% | **2** | 15s | [Boundfree] <100 Eru: 2% MP → +50; [Purify] disperse 1 debuff (incl. taunt, §8) |
| Word of Kindness | Speech | shield | — | 25s | 25% M.DEF / 8s; [Boundfree] 2% MP → +50 |

### Advancement (+5) — verified curves
| Skill | Total DMG @+5 | per-node M.DMG | cost/node | Lv req |
|---|---|---|---|---|
| **Unleashed Ink** | **+109%** | +9.7% | **1** | 20 ✓ |
| Painted Cranes | +67% | +6.0% | 3 | 30 (at 29) |
| Discordant Verse | +52% | +4.6% | 2 | 35 ✓ |
| Lotus Dreamscape | +46% | +4.1% | 3 | 30 (at 29) |

Left-side (non-build) skills gain only ~20–30% at +5. Unleashed Ink is the standout
scaler **and** the cheapest to advance — advance it first.

### The six (priority order; Shield First ON)
1. **Windwalker** — 25% magic evasion + MP shield
2. **Word of Kindness** — 25% M.DEF 8s + shield + 50 gen
3. **Discordant Verse** — 3-tgt splash + Crescendo shield-pierce + Focus + 25 gen
4. **Unleashed Ink** — ST ghost-killer, top throughput (438→~916% @+5, 13s CD) + 50 gen
5. **Painted Cranes** — ST ghost-killer #2, 534% + Summit max-MP chunk
6. **Lotus Dreamscape** — 2-tgt splash + Purify + 50 gen

Cut vs §10: Hidden Hook (Scorch premise dead under blind-fire), Master's Hand (silence
hijacked onto ghosts), Spiritual Wall (Magicka eso auto-covers emergency shields),
Threefold Reflection (benched), monsterforms (§12).

### Strategy — burst-the-ghost (exploits §8's 4s heal window)
Taunt forces single-target casts onto the ghost thrall → burst it down (Ink + Cranes +
curios; the 1300%/+62M LR one-shots it) → §8's **4s taunt-free heal window** opens → all
casts land on the player. **Harder nuke = more downtime = more player damage.** Meanwhile
Verse (3-tgt) + Lotus (2-tgt) splash the player *through* taunt continuously, and Verse's
Crescendo ignores the ghost-driven shields (§8). Two ST nukes is a feature (faster ghost
kills), not redundancy. Defense = evasion + M.DEF + Purify + both esos + dead ghosts deal
no damage (offense-as-defense).

### Priorities
- **Advance Unleashed Ink +5 first** (+109%, 1/node, already eligible). Then Verse (+52%,
  2/node). Cranes/Lotus need Lv 30 to advance, cost 3/node for less — do last.
- **Level Painted Cranes to 40** (Summit req 150→100 — real rotation gain). This is the
  leveling-mat sink that competes with Ink; advancement is a *separate* (knowledge)
  resource, so advance Ink regardless of the Cranes leveling decision.
- **Max MP is the keystone stat** — triple-duty: Boundfree fuel + Cranes-Summit / LR-20%
  max-MP damage + Magicka eso shield size. Favor it on inkstone/brush affixes.

### Model: Scorch-window (old) vs shield-pierce (new)
Raw-damage compare (mitigation cancels relatively; Crescendo still goes through M.DEF,
just not shields). Losing Scorch = +12% amp on ~120M/fight amped throughput =
14.4M×(1−f); gaining Crescendo pierce ≈ 12.5M + 4.8M×f, where **f = fraction of your
damage the target's shields absorb**. **Crossover f ≈ 10%.** Ghostia's whole sustain is
ghost-driven shields (§8), so f ≫ 10% → respec wins; blind-fire independently sinks the
old plan. Current would only stay ahead vs a genuinely shieldless target.
