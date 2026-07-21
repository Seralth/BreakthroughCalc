All six inputs read. Design follows — grounded in the actual catalogs, codec, and verified-mechanics doc.

---

# TRACK C — `data/sources.json` schema + semantics design

## 0. Grounding facts that drove the design

- The engine formula already handles the only realm-conditional effect via dedicated inputs (`bless_pp` / `bless_window_pp`, applied per-row). So the shelf **never needs runtime condition evaluation** — a windowed effect simply targets the windowed *field*, and `condition` is descriptive metadata. Big simplification.
- Respira displayed EXP is per-account: `display = round(stage_base × (1 + books%/100))`, bases measured Nascent 3,157 / Incarnation 6,385. This is the canonical display-embedded case: book % must feed a *model*, never the field.
- Old `respira_sources` persisted sets only ever contain **attempt-kind** names (exp_pct rows were read-only in the picker); old `pe_sources` rows are `[name, pct]` including free-typed custom rows and the parametric Yang Spirit Jade. The old respira catalog contains a genuine duplicate ("Chroma Tier 3 (R8 technique)" and "Chroma (R8 book, Tier 3)") — migration must tolerate N-to-1 aliasing.
- OMV2 ignores unknown keys in both directions; string-keyed values survive catalog reordering. New keys are cheap; only order-indexed values are fragile.

---

## 1. File shape

```json
{
  "schema_version": 1,
  "catalog_version": 1,
  "categories": [
    {"id": "technique_book", "label": "Technique books"},
    {"id": "immortal_friend", "label": "Immortal friends"},
    {"id": "blessing", "label": "Ascension blessings"},
    {"id": "curio", "label": "Curios"},
    {"id": "technique", "label": "Techniques"},
    {"id": "other", "label": "Other"}
  ],
  "targets": { ... },
  "sources": [ ... ]
}
```

`catalog_version` bumps on every content change; used only for version-skew messaging ("this code was made with a newer catalog"). `categories` order = display order everywhere (shelf sections, provenance breakdowns).

## 2. Targets registry — the double-counting taxonomy, in data

Every effect points at a target; every target declares its **mode**. This is where raw-additive-safe vs display-embedded becomes machine-checkable instead of tribal knowledge.

```json
"targets": {
  "pill_effect": {
    "field": "pill_effect", "label": "Cultivation Pill Effect",
    "unit": "percent", "mode": "raw_additive", "combine": "sum", "base": "none"
  },
  "pill_attempts": {
    "field": "pill_limit", "label": "Daily pill limit",
    "unit": "count", "mode": "raw_additive", "combine": "sum", "base": "user"
  },
  "respira_attempts": {
    "field": "respira_per_day", "label": "Respira attempts per day",
    "unit": "count", "mode": "raw_additive", "combine": "sum", "base": "user"
  },
  "respira_effect": {
    "field": "respira_exp", "label": "Respira Effect",
    "unit": "percent", "mode": "display_embedded", "combine": "sum",
    "model": {
      "kind": "respira_display",
      "formula": "round(stage_base * (1 + total_pct / 100))",
      "stage_bases": {"Nascent Soul": 3157, "Incarnation": 6385}
    }
  },
  "bless_pp": {
    "field": "bless_pp", "label": "Absorption blessing",
    "unit": "fraction_pp", "mode": "raw_additive", "combine": "sum", "base": "none"
  },
  "bless_window_pp": {
    "field": "bless_window_pp", "label": "Absorption blessing (windowed)",
    "unit": "fraction_pp", "mode": "raw_additive", "combine": "sum", "base": "none"
  },
  "mark_blue":   {"field": "mark_blue",   "unit": "count", "mode": "raw_additive", "combine": "sum", "base": "user"},
  "mark_purple": {"field": "mark_purple", "unit": "count", "mode": "raw_additive", "combine": "sum", "base": "user"},
  "mark_gold":   {"field": "mark_gold",   "unit": "count", "mode": "raw_additive", "combine": "sum", "base": "user"},
  "culti_speed":      {"field": "culti_speed",      "mode": "display_embedded", "effects_allowed": false},
  "absorption_ratio": {"field": "absorption_ratio", "mode": "display_embedded", "effects_allowed": false},
  "info": {"mode": "informational"}
}
```

**Mode semantics** (the critical constraint):

| mode | may write the field? | how contributions are used |
| --- | --- | --- |
| `raw_additive` | yes — `field = base + Σ effects + Σ custom` | direct derivation, provenance chip on the field |
| `display_embedded` | **never** | contributions feed the target's `model` to produce a *suggestion/pre-fill* and an informational chip ("your displayed value includes +28% from 9 books"); a target with no `model` and `effects_allowed: false` exists purely as a guard rail so nobody ever adds an additive effect to it |
| `informational` | n/a | shown in the source's detail view only (QoL perks, unquantified buffs) |

**`base` semantics** for raw targets: `"none"` = the field is fully shelf-derived (pill_effect — exactly today's mobile `pe_sources → pill_effect` behavior); `"user"` = a residual base input remains (respira attempts have a level-based in-game base ~10; pill limit likewise) and the shelf *adds* to it. The residual base is the existing input field re-labeled ("base attempts, before sources").

**Stacking**: `combine: "sum"` covers everything currently known (books % additive, blessing pp additive — 40+20=60, owner-observed 2026-07-20 — attempts additive). NOTE: blessing *tiers* do NOT stack across each other; in Incarnation the blessing is a flat +20 (Perfect == Perfection), so `ascension_virya` derives a single bless_pp 0.20, not a sum of tier pp. `combine: "product_1p"` is reserved (total = Π(1+vᵢ)−1) for a future multiplicative case (e.g. elixir_effect-style multipliers); no current source uses it. Aura Gem stays an enum input, not a shelf source.

**Blessing note**: absorption_ratio is entered as the on-screen TOTAL (already includes blessing) and the engine strips the current row's blessing to recover Strive — so blessing effects target `bless_pp`/`bless_window_pp` (raw engine inputs), never `absorption_ratio`. The taxonomy encodes this: `absorption_ratio.effects_allowed = false`.

## 3. Source entry schema

```json
{
  "id": "purify_cleanse",              // stable machine id, ^[a-z0-9_]+$, unique. Wire + owned-map key. NEVER renamed.
  "name": "Purify & Cleanse",          // display name, unique
  "category": "technique_book",
  "rank": "R7",                        // optional grouping metadata
  "levels": {"kind": "tier", "max": 12},
  "effects": [ ...see below... ],
  "legacy": [ ...migration aliases, see §6... ],
  "data_status": "exact",              // exact | community | unknown (entry default; per-effect override)
  "note": "optional user-visible prose (style rules apply: no provenance phrasing)"
}
```

**Progression models** (`levels.kind`) — what the "owned level" integer means:

| kind | owned value | example |
| --- | --- | --- |
| `binary` | 1 (owned) | one-shot book learned on activation |
| `tier` | tier 1..max | technique-book tiers 1–12 |
| `level` | the friend's actual level (set once; future thresholds auto-activate as it's raised); `max` may be null (unknown cap); **sentinel −1 = "maxed"**, satisfies every numeric and `"max"` threshold | immortal friends |
| `ladder` | index 1..len(labels) into ordered named tiers; owning tier N implies all lower | blessing tiers Completion → Perfection (C) → Perfect |
| `custom` | ordered param array per `params` spec, e.g. `[star, upgrade]` | Yang Spirit Jade |

**Effect schema**:

```json
{
  "target": "respira_effect",          // key into targets registry
  "value": 7,                          // number in the target's unit; null only when data_status = "unknown"
  "value_model": { ... },              // XOR with value; kind "star_upgrade" is the only defined model
  "min_level": 9,                      // active when owned level >= this (default 1); "max" sentinel allowed for kind=level
  "condition": {                       // OPTIONAL, metadata-only (engine handles windowing via the target field)
    "kind": "before_row", "stage": "Voidbreak", "phase": "Middle"
  },
  "data_status": "exact",              // optional per-effect override
  "note": "shown in the breakdown row"
}
```

Multi-effect sources are just multiple effect rows (different targets and/or different `min_level` thresholds on the same target — the +4%-then-+7%-more pattern is two rows that both stay active).

## 4. Derivation semantics

**Persisted shelf state** (prefs blob, `shelf_v1`):

```json
{
  "owned":      {"chroma": 6, "macaque": 17, "yang_spirit_jade": [4, 8], "crane_boy": -1},
  "custom":     {"pill_effect": [["Event buff", 2.0]]},
  "overrides":  {"pill_effect": 30.0},
  "unrecognized": [["some_future_source", 2]]
}
```

`custom` = per-target free-form extras `[label, value]` — replaces today's free-typed pe rows and absorbs unmatched migration leftovers. `unrecognized` = version-skew passengers (§5).

**Pure derivation function** (mirrored `sources_shelf.py` / `sources_shelf.dart`, no UI deps — same pattern as engine parity):

```
derive(catalog, shelf) -> { target_key: {
    contributions: [{source_id, name, level_label, value, data_status, note}],
    custom:        [[label, value], ...],
    total:         combine(values),        // unknown-value effects contribute 0
    incomplete:    bool,                   // true if any active effect has value null
    field_value:   base? + total           // only for mode raw_additive
}}
```

1. For each owned `(id, level)`: look up entry; an effect is **active** iff `level ≥ min_level` (level −1 satisfies all; `"max"` threshold satisfied only by −1 or level == levels.max). `custom`-kind sources evaluate `value_model` with the owned params.
2. Group active effects by target; append the target's custom extras; `total = combine(...)`.
3. **Field resolution precedence**: manual override > derived > input default. If `overrides[field]` exists, the field shows that value with a "manual" badge; the auto value is still computed and shown in the breakdown ("auto would be 28%") so the user can compare; *reset-to-auto* deletes the override key. If no override: `raw_additive` targets write `base + total` into the field (base = residual input where `base:"user"`, 0 where `"none"`); `display_embedded` targets never write — they render an informational chip and, where the model has a `stage_base` for the current stage, offer a one-tap pre-fill `round(base × (1 + total/100))` plus a gentle mismatch note when the entered value differs from the prediction by more than a rounding unit.
4. **Ordering** (purely presentational — sums are commutative): breakdown rows sorted by (category order in `categories`, then value descending, then name). Deterministic, spec'd, pinned by a test.
5. `incomplete: true` renders the chip total with a "≥" prefix and an "amount unknown for N sources" line — unknown-value sources are visible but never fabricate numbers.

Engine stays pure-numeric and untouched — the shelf is strictly an input-layer derivation, exactly like today's `pe_sources → pill_effect`.

## 5. OMV2 encoding

> **Shipped (3.4)** — mobile carries `'S'` (owned pairs) per this section,
> with three implementation divergences, documented in
> docs/knowledge/share-code-format.md: `'C'`/`'O'` are not encoded (custom
> pe rows already travel in `'P'`, and the shipped Vault has residual
> `bases` instead of per-field overrides — they are re-anchored from the
> imported field totals on decode); dual-emit needs no extra code (the
> synthetic Vault pe row and vault-inflated attempts ARE the legacy
> emission); and an old code without `'S'` leaves the receiver's Vault
> untouched instead of running the §6 migration mapper on `'P'`/`'R'`.

Three new string-keyed (order-safe, reorder-proof) keys; defaults (empty) omitted as usual:

```
'S': [["ascension_virya",3],["chroma",6],["crane_boy",-1],["macaque",17],
      ["purify_cleanse",9],["yang_spirit_jade",[4,8]],["zixiao_sutra",1]]   // sorted by id; level int or param array
'C': [["pill_effect","Event buff",2.0], ...]                               // custom extras, sorted by (target,label)
'O': {"pill_effect": 30.0}                                                  // manual overrides, target-keyed
```

- **Old code → new app**: no `'S'` key ⇒ if `'P'`/`'R'` present, run the §6 migration mapper on them; else empty shelf. Old codes keep working forever (decode support for `'P'`/`'R'` is ~20 lines; keep indefinitely).
- **New code → old app**: unknown keys ignored by design. To keep cross-version sharing *useful* during the transition, **dual-emit for a deprecation window**: also encode `'P'` (derived `[legacy_pe_name, pct]` pairs for pill-effect contributions that have a legacy alias) and `'R'` (legacy attempt-source names). Rule to prevent double-counting: **`'S'` present ⇒ authoritative; decoders must ignore `'P'`/`'R'` when `'S'` exists.** Ship that ignore rule in the same release that introduces `'S'`; sunset dual-emit 2–3 releases later.
- **Version skew (unknown source id in a received code)**: never drop silently. Unknown `[id, level]` pairs land in `shelf.unrecognized`, contribute nothing, surface as "1 source isn't in this app version — update to use it", and **re-encode back into `'S'` on re-share** (lossless round-trip through an old app). Same for a known id whose level exceeds the local catalog's `max`: clamp for derivation, preserve the original for re-encode. This is why ids are strings and levels are absolute values, never catalog indexes.
- No `OMV2.` prefix bump needed — this is additive, exactly the documented forward-compat path.

## 6. Migration: map vs coexist

**Option B — coexist** (keep `pe_sources`/`respira_sources` inputs alongside the shelf): zero migration code, but it's a standing double-count trap (pick Chroma on the shelf *and* keep its pe row → +8% instead of +4%), two UIs for one concept violates the set-once vision, both persistence paths and both wire keys live forever, and the provenance chip lies whenever legacy rows exist. Guarding against overlap would itself need the alias table Option A needs — so coexist costs the same mapping work *plus* permanent complexity.

**Option A — one-time migration into the shelf**: needs an alias table and an escape hatch for free-typed rows. That's it.

**Recommendation: Option A**, with these mechanics:

- Each source carries `legacy` aliases with implied levels:

  ```json
  "legacy": [
    {"catalog": "pe", "name": "Chroma (R8 technique)", "implies_level": 6},
    {"catalog": "respira", "name": "Chroma Tier 3 (R8 technique)", "implies_level": 3},
    {"catalog": "respira", "name": "Chroma (R8 book, Tier 3)", "implies_level": 3}
  ]
  ```

  Mapper: for each stored legacy name, match alias → `owned[id] = max(owned[id], implies_level)` (max-merge handles the pe+respira overlap and the old catalog's Chroma duplicate). The implied level is sound: the old pe pct for a tiered book equals its cumulative total, so having picked it implies the enabling tier.
- **Unmatched pe rows** (free-typed custom sources) → `custom["pill_effect"]` entries, values preserved exactly; provenance shows them under "Custom".
- **Parametric alias** (Yang Spirit Jade: stored pct doesn't uniquely invert to (star, upgrade)): alias carries `"parametric": true` → migrate the pct into `custom["pill_effect"]` labeled with the source name plus a one-time "re-select on the shelf for auto-tracking" nudge; picking it on the shelf removes the custom row.
- Migration runs once on first launch (prefs) and inline on every legacy-code decode; the derived `pill_effect` is bit-identical to the old sum by construction (values are copied, not recomputed), so **engine parity and existing share codes are untouched**. After migration the legacy inputs and their pickers are deleted from both apps.

## 7. Validation rules (enforced by `tests/test_sources_schema.py` + a mirrored Dart test)

1. `schema_version`/`catalog_version` present, ints; category ids unique; every `source.category` ∈ categories.
2. Source `id` unique, matches `^[a-z0-9_]+$`; `name` unique case-insensitively. Ids are append-only (pin the id set in the test's golden list so renames fail loudly — wire format depends on them).
3. `levels.kind` ∈ {binary, tier, level, ladder, custom}; tier ⇒ int `max ≥ 1`; ladder ⇒ non-empty unique `labels`; custom ⇒ non-empty ordered `params` each with numeric min/max.
4. Every `effect.target` exists in `targets`; **no effect may reference a target with `effects_allowed: false`** (culti_speed, absorption_ratio — the double-count guard rail).
5. **Every `display_embedded` target that any effect references must declare a `model`; `raw_additive` targets must not declare one.** No effect value is ever added to a display-embedded field (structural: derivation only writes where mode is raw_additive — assert the mode table itself).
6. Exactly one of `value` / `value_model` per effect, except `data_status: "unknown"` where both may be absent.
7. `min_level`: int ≥ 1 and ≤ `levels.max` when max is known; the `"max"` sentinel only on `kind: "level"`; binary sources omit it. No duplicate (target, min_level) pair within a source.
8. Unit ranges: `percent` ∈ (0, 100]; `fraction_pp` ∈ (0, 1]; `count` positive int.
9. `star_upgrade` models: `len(star_add) == stars`, ascending `star_add`, and the computed max equals a pinned `max_value` (5.8 for Yang Spirit Jade).
10. `condition` allowed only with `kind: "before_row"`, its stage/phase must exist in `breakthrough.json` rows, and **any conditioned effect must target `bless_window_pp`** (the engine is where windows live).
11. **Legacy totality**: every name in `data/pill_effect_sources.json` plus every attempt-kind name in `data/respira_sources.json` is claimed by ≥ 1 alias; no name claimed by two different sources (≥1, not ==1, because of the old Chroma duplicate).
12. `data_status` ∈ {exact, community, unknown} (maps to product language "exact"/"subjective" — never verification-speak).
13. Style rule, mechanized: user-visible `note`/`label` strings must not match the banned-provenance regex (`verified|screenshot|confirmed|dump|20\d\d-\d\d|community guide`).
14. Parity: the Dart test parses the same JSON and pins a content checksum, so desktop and mobile can never ship divergent catalogs.

## 8. Worked example entries (all schema features covered)

```json
[
  {
    "id": "purify_cleanse",
    "name": "Purify & Cleanse",
    "category": "technique_book",
    "rank": "R7",
    "levels": {"kind": "tier", "max": 12},
    "effects": [
      {"target": "respira_effect", "value": 4, "min_level": 1,
       "note": "Respira Effect +4% on activation."},
      {"target": "respira_effect", "value": 7, "min_level": 9,
       "note": "Additional Respira Effect +7% at Tier 9."},
      {"target": "respira_attempts", "value": 1, "min_level": 1,
       "note": "+1 daily Respira attempt."},
      {"target": "info", "value": null, "min_level": 1,
       "note": "Complete all Respira instantly."}
    ],
    "legacy": [
      {"catalog": "respira", "name": "Purify & Cleanse (technique book)", "implies_level": 1}
    ],
    "data_status": "exact"
  },
  {
    "id": "chroma",
    "name": "Chroma",
    "category": "technique_book",
    "rank": "R8",
    "levels": {"kind": "tier", "max": 12},
    "effects": [
      {"target": "pill_effect", "value": 1, "min_level": 1,
       "note": "+1% Cultivation Pill Effect on learning."},
      {"target": "pill_effect", "value": 3, "min_level": 6,
       "note": "+3% Cultivation Pill Effect at Tier 6."},
      {"target": "respira_attempts", "value": 1, "min_level": 3,
       "note": "+1 daily Respira attempt at Tier 3."},
      {"target": "pill_attempts", "value": 1, "min_level": 12,
       "note": "+1 daily pill attempt at Tier 12."}
    ],
    "legacy": [
      {"catalog": "pe", "name": "Chroma (R8 technique)", "implies_level": 6},
      {"catalog": "respira", "name": "Chroma Tier 3 (R8 technique)", "implies_level": 3},
      {"catalog": "respira", "name": "Chroma (R8 book, Tier 3)", "implies_level": 3}
    ],
    "data_status": "exact"
  },
  {
    "id": "macaque",
    "name": "Macaque",
    "category": "immortal_friend",
    "levels": {"kind": "level", "max": null},
    "effects": [
      {"target": "respira_effect", "value": 3, "min_level": 17,
       "note": "+3% Respira EXP at level 17. Already included in your displayed Respira EXP."}
    ],
    "legacy": [],
    "data_status": "exact"
  },
  {
    "id": "crane_boy",
    "name": "Crane Boy",
    "category": "immortal_friend",
    "levels": {"kind": "level", "max": null},
    "effects": [
      {"target": "pill_attempts", "value": 1, "min_level": "max",
       "data_status": "community",
       "note": "+1 daily pill attempt at max level."}
    ],
    "legacy": [
      {"catalog": "respira", "name": "Crane Boy (immortal friend, max)", "implies_level": -1}
    ],
    "data_status": "community"
  },
  {
    "id": "ascension_virya",
    "name": "Ascension Virya blessings",
    "category": "blessing",
    "levels": {"kind": "ladder", "labels": ["Completion", "Perfection (C)", "Perfect"]},
    "effects": [
      {"target": "info", "value": null, "min_level": 1,
       "note": "Removes realm restrictions for Cultivation Pills; auto-transmogrification lets breakthrough pills of one path be used on the other (physical ↔ magical)."},
      {"target": "bless_pp", "value": 0.20, "min_level": 2,
       "note": "Incarnation Aura Absorption Ratio +20%. Persists after Incarnation."},
      {"target": "bless_pp", "value": 0.20, "min_level": 3,
       "note": "Second +20% Absorption Ratio. Persists after Incarnation."},
      {"target": "bless_window_pp", "value": 0.20, "min_level": 3,
       "condition": {"kind": "before_row", "stage": "Voidbreak", "phase": "Middle"},
       "note": "Additional +20% Absorption Ratio until you pass Voidbreak Middle."}
    ],
    "legacy": [],
    "data_status": "community",
    "note": "Blessing bonuses are per cultivation path. Subjective: stacking is the widely agreed model."
  },
  {
    "id": "zixiao_sutra",
    "name": "Zixiao Sutra",
    "category": "technique_book",
    "rank": "R8",
    "levels": {"kind": "binary"},
    "effects": [
      {"target": "pill_effect", "value": 1,
       "note": "+1% Cultivation Pill Effect on learning."}
    ],
    "legacy": [
      {"catalog": "pe", "name": "Zixiao Sutra (R8 technique)", "implies_level": 1}
    ],
    "data_status": "exact"
  },
  {
    "id": "yang_spirit_jade",
    "name": "Yang Spirit Jade",
    "category": "curio",
    "levels": {
      "kind": "custom",
      "params": [
        {"id": "star", "label": "Star", "min": 1, "max": 5},
        {"id": "upgrade", "label": "Upgrade level", "min": 0, "max": 8}
      ]
    },
    "effects": [
      {"target": "pill_effect",
       "value_model": {
         "kind": "star_upgrade",
         "base": 1.0, "per_upgrade": 0.2, "max_upgrade": 8,
         "stars": 5, "star_add": [0.0, 0.8, 1.2, 2.2, 3.2],
         "max_value": 5.8
       },
       "note": "Epic curio. Value depends on star and upgrade level, 1.0% to 5.8%."}
    ],
    "legacy": [
      {"catalog": "pe", "name": "Yang Spirit Jade (curio)", "parametric": true}
    ],
    "data_status": "exact"
  },
  {
    "id": "virya_double",
    "name": "Virya session (Double)",
    "category": "other",
    "levels": {"kind": "binary"},
    "effects": [
      {"target": "info", "value": null, "data_status": "unknown",
       "note": "May multiply cultivation gains while its timer runs. Amount not yet established; not counted in any total."}
    ],
    "legacy": [],
    "data_status": "unknown"
  }
]
```

Coverage map: multi-effect + multi-threshold tiers (purify_cleanse, chroma), three targets from one source (chroma), friend level threshold + display-embedded target (macaque), unknown threshold via `"max"` sentinel + maxed −1 (crane_boy), ladder + windowed pp + community status + per-path note (ascension_virya), simple binary one-shot (zixiao_sutra), parametric value_model + parametric migration (yang_spirit_jade), unknown-value marker excluded from totals (virya_double), legacy N-to-1 aliasing (chroma), custom extras + overrides (§4 state example).

## 9. Notes for the other tracks

- New modules: `breakthrough_calc/sources_shelf.py` ↔ `mobile/lib/sources_shelf.dart` (pure derivation, parity-tested against shared fixture JSON), plus thin UI in `fields.py`-registry style desktop / a shelf screen mobile. `source_pickers.dart` shrinks to the shelf UI; the star-upgrade dialog becomes the generic `custom`-params dialog driven by `levels.params`.
- The old `data/pill_effect_sources.json` / `data/respira_sources.json` stay in-tree until migration ships (validation rule 11 reads them), then become test fixtures for the mapper.
- The advisor feature falls out for free: rank unowned sources (or next thresholds of owned ones) by re-running `derive` with `owned[id]` incremented and diffing engine output — no schema additions needed now; an optional `acquisition` metadata field can be added later without a wire change.
- Open item to verify before pinning blessing examples as `exact`: one in-game absorption tooltip reading with a tier active (a 40%-band player with +20% should read 60%).