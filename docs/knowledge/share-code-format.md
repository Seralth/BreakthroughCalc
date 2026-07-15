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
| P | pe_sources | list of [name, percent] pairs — full strings, so codes survive catalog reordering |
| R | respira_sources | sorted list of catalog names (same reasoning) |

Note: `pill_effect` itself is NOT encoded — the mobile app derives it from
`pe_sources`. A desktop port must do the same or codes will disagree.

## Test vectors

The golden vector (a fully-populated build + its exact decoded long-key map)
lives in `mobile/test/share_codec_test.dart`. Decode-side behavior is the
durable contract; encode bytes are deliberately not pinned (zlib output may
vary across compressor versions — mutual compatibility is covered by
round-trip tests).
