# Shareable build codes — OMV2 wire format

Status: implemented on mobile only (`mobile/lib/share_codec.dart`, since
v2.13/2.14). A desktop port MUST be driven by the same pins
(`mobile/test/share_codec_test.dart`: golden vector + order pins) so codes
round-trip across platforms — mirror the engine-parity pattern.

## Framing

```
'OMV2.' + base64url( zlib_deflate( JSON(compact map), level 9 ) )
```

- Decode tolerates surrounding whitespace and missing base64 padding
  (`base64Url.normalize`); anything unreadable → null (never throws).
- Fields equal to their default are **omitted** at encode time; decode fills
  defaults. Forward compatibility: unknown keys are ignored, so codes travel
  both directions across app versions. Only a truly incompatible
  restructuring bumps the `OMV2.` prefix (OMV1 codes are no longer accepted).

## Contract: enum ORDER is part of the format

Enum-ish fields are stored as integer indexes into the engine data tables.
Reordering `data/breakthrough.json`'s `rows`, `gem_bonus`, `pill_xp`,
`fruit_xp` keys, or `rarity_names` — or the `starLevels`/`vaseInputKinds`
constants — silently remaps every previously shared code. The order pins in
`share_codec_test.dart` fail loudly if this happens.

## Field table (short key → long key)

| Short | Long | Encoding |
| --- | --- | --- |
| s / p / g | stage / phase / grade | index into stages() / phasesFor(stage) / gradesFor(stage, phase) |
| gc / cs / ar | grade_completion / culti_speed / absorption_ratio | number |
| ag | aura_gem | index into gem_bonus keys |
| ts / tp / tg | target_stage / target_phase / target_grade | index; −1 = unset (empty string) |
| td | timegate_days | number (UI-only field) |
| os | top_stage | index; −1 = unset |
| ms / dd | mature_server / dailies_done | 0/1 |
| rh / rd / re / rx | reset_in_hours / respira_per_day / respira_event / respira_exp | number |
| pr | pill_rank | index into pill_xp keys |
| pl / gd / pd / bd | pill_limit / gold_per_day / purple_per_day / blue_per_day | number |
| mb / mp / mg | mark_blue / mark_purple / mark_gold | number |
| v / vs / vk / vi / vc | vase / vase_star / vase_skin / vase_input / vase_charge | 0/1; star = index into starLevels; input = index into vaseInputKinds |
| mi / mis / mik / mic | mirror / mirror_star / mirror_skin / mirror_charge | 0/1 + star index |
| pe / pes / pek / pex / pec | pearl / pearl_star / pearl_skin / pearl_xp_per_10 / pearl_charge | 0/1 + star index + number |
| fr / fc / fh | fruit_rank / fruit_count / fruit_highest_rank | index into fruit_xp keys + number + 0/1 |
| lc / lq / lg | lvl_culti / lvl_quality / lvl_gush | int |
| er | extractor_rarity | index into rarity_names |
| bp / bw | bless_pp / bless_window_pp | fractions (0.20 = +20pp); added 2026-07-15, absent in older codes (decode to 0.0) |
| ed / ex / ef | elixir_per_day / elixir_exp / elixir_effect | numbers; added 2026-07-15 — note ef decodes to 1.0 (its default) when absent |
| P | pe_sources | list of [name, percent] pairs — full strings, so codes survive catalog reordering |
| R | respira_sources | sorted list of catalog names (same reasoning) |
| S | Vault ownership | sorted [id, level] pairs; added in 3.4 — see below |

Note: `pill_effect` itself is NOT encoded — the mobile app derives it from
`pe_sources`. A desktop port must do the same or codes will disagree.

Boolean (`0/1`) fields have one legacy-decode nuance the table above doesn't
show: a present-but-**null** wire value decodes to `false`, not to the
field's default (`share_codec.dart`'s `case 'b'` checks `m.containsKey(...)`
then does `m[f.short] == 1`, so `null == 1` is `false` even where the true
default would be `true`).

## `S`: the Vault travels with the code (since 3.4)

`'S'` carries `VaultState.owned` as `[id, level]` pairs sorted by id. Ids
are the frozen string ids from `data/sources.json` (wire data — never
renamed once shipped); levels are absolute values (int, `-1` = maxed, or a
param array for parametric sources like Yang Spirit Jade) — never catalog
indexes. An empty Vault is a default and is omitted like any other.

Decode adds one `shelf_owned` map on top of the inputs-blob shape when the
key is on the wire; `_importString` strips it before blob validation, then
(`_adoptImportedVault`):

- **Replaces** the local Vault with the imported ownership
  (`auto` = non-empty, mirroring migration).
- **Re-anchors the untracked remainders**: `bases[target] = imported field
  value − what the adopted Vault derives locally` (clamped ≥ 0), so the
  imported attempts/limit values are reproduced exactly.
- **Drops the sender's synthetic `Vault (books & curios)` pe row** and lets
  `_onVaultChanged` regenerate it from the adopted ownership — Vault
  contributions are derived locally, never trusted from (or double-counted
  with) the flattened copy.

Compatibility rules:

- **Old code → 3.4+ app** (no `'S'`): the local Vault is left untouched;
  the code's flattened values (`P`/`R` rows, attempts totals) import as
  plain fields exactly as before. This deliberately diverges from the
  sources-shelf design doc's "run the migration mapper on P/R" option —
  wiping or rewriting the receiver's Vault from a code that never carried
  one is worse than keeping the (already correct) flattened numbers.
- **3.4+ code → old app**: `'S'` is ignored (unknown keys always are), and
  the dual-emitted flattened values — the synthetic Vault pe row and the
  vault-inflated attempts — keep the imported build numerically right.
- **Version skew**: unknown ids in `'S'` are kept in `owned` as passengers
  (`derive()` skips them; they contribute nothing) and re-emit on the next
  export, so a code is lossless through any app version. Levels above the
  local catalog's max always keep their original value in `owned` —
  **correction:** "clamp for display/derivation" was an overgeneralization.
  Display clamping is real only for `ladder`-kind entries (`catalog.dart`'s
  `levelLabel()` / `main.dart`'s `_viryaCurrent()`); `tier`/`level`-kind
  Vault rows (e.g. technique books, `vault_tab.dart`'s `_bookRow`) render
  the raw unclamped value (`owned` above a book's max tier shows as
  `T20/15`, not `T15/15`). Derivation for plain numeric levels uses `owned
  >= threshold` comparisons (behaviorally capped, but not a literal
  `.clamp()`); an explicit `.clamp()` exists only for parametric/`custom`
  sources (`catalog.dart`'s `modelValue()`).

## Test vectors

The golden vector (a fully-populated build + its exact decoded long-key map)
lives in `mobile/test/share_codec_test.dart`. Decode-side behavior is the
durable contract; encode bytes are deliberately not pinned (zlib output may
vary across compressor versions — mutual compatibility is covered by
round-trip tests).
