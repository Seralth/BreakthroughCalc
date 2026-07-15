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
- On InkedSeralth's stats (M.ATK 3.11M, max MP ~210M) LR ~= ~71M per cast and is the
  single biggest damage source. ~2 casts in a 40–55s fight (~3 if generation is high).

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

## 10. Current loadout & casting order (PvP, vs Swordia/Ghostia)

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
15+. remaining Inkstone casts -> Literal Reality auto-fires at 300 -> monsterforms
    (monsterforms usually never cast in a 40–55s fight; harmless at the tail)

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
  Lotus Dreamscape's purify — do NOT delay Lotus for it.

## 12. Decompile pipeline (for future skill/config lookups)

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

## 13. Internal term glossary

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
