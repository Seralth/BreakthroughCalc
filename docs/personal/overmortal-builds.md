# OverMortal — Build & Cast Order Notes (InkedSeralth)

Living doc for PvE (Myrimon) loadouts. **PvP build lives in
[overmortal-literatia.md](../knowledge/overmortal-literatia.md)** (sections 10–12), which is
also the APK-verified source for Erudition/Summit/Boundfree mechanics — where
this doc and that one disagree on mechanics, that one wins.

## Character snapshot (2026-07-15)

- Literatia path, Incarnation (L) Late 65.1% / Nascent Soul (M) Middle 46.6%
- M.ATK 3.42M, P.ATK 524K, M.DEF 519.5K, P.DEF 195.5K, Max MP ~228M
- Erudition cap: **300**, resets to 0 after 30s without gain (APK-verified, see overmortal-literatia.md §1)
- Zodiac Word (知行合一): auto-casts at full Erudition, consumes all of it,
  deals 1300% M.DMG + 20% Max MP as M.DMG. Not slotted; always active.

**Result: Myrimon Wonder went from ~1.2B stuck → cleared 1.8B final reward tier
with the cast order below.**

## Combat mechanics (how ordering works)

- One priority list covers abilities + curios + relics (15 slots here).
  Skills auto-cast in priority order as they come off cooldown, and a
  higher-priority skill **cuts in line** when it comes back up.
  (Ability screen → gear icon → Ability Casting Order; player-confirmed.)
- "Shield First" toggle prioritizes shield-type skills — keep ON.
- Curios all sit on 60s cooldowns → they burst together every minute;
  priority decides their sequence within that burst.
- Old-tier abilities carry a stage penalty that grows as realm rises
  (Connection −10%, Foundation −5% at current realm).

## Myrimon PvE cast order (verified working)

Design: an **Erudition ladder** — builders stack the bar so threshold
(Summit) abilities cast exactly when their bonus is live, debuffs land just
before the 300-point Zodiac detonation, and the Exorcism curio leads the
minute-mark curio burst.

| # | Skill | Role / why this slot |
|---|-------|----------------------|
| 1 | Speech - Word of Kindness | Shield First; shield 39.6% MP, +50 Erud (→50) |
| 2 | Speech - Hidden Hook | +75 Erud, clamped at 200 — early slot wastes none (→125). Summit @250: +15% dmg + Scorch (M.DMG taken +12%) |
| 3 | Unleashed Ink | Best slotted ST hit (467%), M.Hit −20% debuff, +50 (→175) |
| 4 | Master's Hand | +25 (→200); Encumberment M.DEF −23.8% = the Zodiac amp window; 85.5% Silence |
| 5 | Speech - Threefold Reflection | Casts at ≥200 → Summit: 3rd hit. Disperse strips elite/boss buffs |
| 6 | Speech - Verbal Assault | 249.3%/8s CD + **50 Erud/8s = best Erud income in kit** (replaced Discordant Verse) |
| 7 | Primeval Brush | 386% + Summit ≥100: +25% dmg (near-permanent uptime) |
| 8 | Cosmic Demon Spire | 595% + **Exorcism self-buff: +20% dmg to Monsters 8s** — must lead the curio burst |
| 9 | Dragonpit Sword | 282%×3 inside Exorcism window (HP-regen rider useless: Myrimon bosses don't heal) |
| 10 | Fire Lotus | 105%×5 inside Exorcism window |
| 11–12 | Yellow Primeval Inkstones | 356%×2 targets, +25 Erud/24s each |
| 13–15 | Purple Primeval Inkstones | 305%×2, +25 Erud/24s each — rarity does NOT affect Erud income |

Opener Erudition track: 50 → 125 → 175 → 200 (Threefold Summit) → 250
(Hook's 2nd cast gets Scorch) → relics carry to 300 → Zodiac fires inside
Master's Hand's shred window. Relic income alone: +125 Erud / ~24s cycle.

Deliberate omissions:
- **No slotted AoE.** Myrimon is decided by elite-pair/boss stages; trash
  dies to stat check + 2-target inkstones. If a wave stage ever times out,
  slot **Speech - Written Condemnation** (293.7%×3 = 881% total, best owned
  AoE, +19% crit buff) — NOT Discordant Verse.
- **Inksworn Strike**: strictly worse Unleashed Ink; never slot.
- Don't feed spare inkstones as fodder — all 5 + brush fit the 6 relic
  slots, and slotted Erud income beats their stat value.

## Bench reference (unslotted, evaluated 2026-07-15)

| Skill | Numbers | Verdict |
|---|---|---|
| Discordant Verse (Lv29) | 180.7%×3 + Crescendo 100% shield-ignore, +25 Erud | Replaced by Verbal Assault; level to 65/80 for unlocks only |
| Written Condemnation (Lv39, Found.) | 881% total ×3, Perception crit+19% | Best AoE; wave-stage tech slot |
| Inksworn Strike (Lv20, Conn.) | 228.6%×2, 11s | Skip |
| Verbal Assault (Lv20, Conn.) | see slot 6 | Slotted |

## Upgrade priorities (as of 2026-07-15)

1. **Threefold Reflection 69 → 80** → unlocks **Speech - Word of Silence**
   (113.6%×3, 80% Paralysis 2s, Summit @200: +50% dmg → ~511%/18s).
   Also grants Threefold's own Lv80 +8% M.DMG.
   - When learned: close call between replacing Verbal Assault
     (Silence ~28.4%/s + control vs Verbal 31.2%/s + 6.25 Erud/s) or
     Master's Hand (lose M.DEF −23.8% Zodiac window). **Test both in
     combat, don't theorycraft** — flagged unresolved.
2. **Hidden Hook 19 → 40**: Lv20 Acute (M.Hit +20%); Lv40 drops Summit
   250 → 200 → Scorch live for the whole upper bar.
3. Long term: **Discordant Verse → 80** unlocks **Painted Cranes**
   (355.6% + Summit @150: extra dmg = 3% Max MP ≈ 6.8M flat now, scales
   with MP stacking; synergizes with Kindness shield + Zodiac MP scaling).
   Skip Lotus Dreamscape (Verse 65, evasion utility) for PvE.
4. Curio resources → **Fire Lotus star-up** (5★ = −20% CD) and Spire;
   Dragonpit Sword is a stat stick here.

## PvP build

Documented in [overmortal-literatia.md](../knowledge/overmortal-literatia.md) §10 (loadout &
cast order vs Swordia/Ghostia), §11 (gear decisions), §12 (cast-slot economics,
stun rejection, monsterform unequip — 2026-07-14 fight data). Key structural
difference vs Myrimon: PvP runs borrowed shields (Windwalker, Spiritual Wall)
in place of Threefold Reflection / Verbal Assault, and Exorcism is useless
against players, so Cosmic Demon Spire casts LAST of the three curios there
(opposite of the PvE order in this doc).
