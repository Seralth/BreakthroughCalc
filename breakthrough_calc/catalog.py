"""Catalog shape primitives (no Qt, no engine).

The ONE place that decodes the data/sources.json entry shape so a schema
change touches a single module per platform instead of rippling across the
shelf, advisor, docs and UI. It owns:
- the value_model star math (star_upgrade), 0-based stars;
- effect gating: min_level ladder incl. the "max" sentinel, plus the
  parametric-source "owning is binary" rule;
- presentational level labels;
- the small effect-threshold reads the advisor walks.

Twin of mobile/lib/catalog.dart — keep the two in lockstep (the shared
fixtures shelf_cases.json / advisor_cases.json pin that both platforms
agree). See shelf.py's module docstring for the owned-map shapes by
levels.kind.
"""

from __future__ import annotations

LEVEL_KINDS = ("binary", "tier", "level", "ladder", "custom")
STAR_UPGRADE = "star_upgrade"


def model_value(model: dict, params) -> float:
    """Evaluate a value_model for owned `params`.

    star_upgrade: stars are 0-based like the game's display (0..5 +
    Awakened=6); star_add[star] is the tooltip's "Increases Curio Passive
    Stats" scalar, added in percentage points to the upgrade ladder.
    """
    if model.get("kind") == STAR_UPGRADE:
        star, upgrade = int(params[0]), int(params[1])
        star = max(0, min(model["stars"] - 1, star))
        upgrade = max(0, min(model["max_upgrade"], upgrade))
        return (model["base"] + model["per_upgrade"] * upgrade
                + model["star_add"][star])
    raise ValueError(f"unknown value model: {model.get('kind')}")


def model_range(model: dict):
    """(min, max) display bounds for a value_model, as stored (base and the
    recorded max_value). Raw values so callers format them themselves."""
    return model["base"], model["max_value"]


def level_ok(min_level, owned_level, levels) -> bool:
    """Is an effect with `min_level` active at `owned_level`? Handles the
    'max' sentinel (satisfied by owned == -1 or reaching levels.max)."""
    if owned_level is None:
        return False
    if min_level == "max":
        mx = levels.get("max")
        return owned_level == -1 or (mx is not None and owned_level >= mx)
    if owned_level == -1:       # maxed satisfies every numeric threshold
        return True
    return owned_level >= (min_level if min_level is not None else 1)


def effect_active(levels, min_level, owned) -> bool:
    """Effect gating with the parametric rule folded in: owning a custom
    (parametric) source is binary — any owned params activate every effect —
    otherwise fall back to the min_level ladder check."""
    if levels.get("kind") == "custom":
        return owned is not None
    return level_ok(min_level, owned, levels)


def effect_value(eff: dict, owned):
    """The numeric contribution of one effect at `owned`, or None when the
    amount is unrecorded (value_model wins; else literal value; else None)."""
    if "value_model" in eff:
        return model_value(eff["value_model"], owned)
    v = eff.get("value")
    return None if v is None else float(v)


def level_label(entry: dict, owned) -> str:
    """Presentational owned-level label ("Tier 7" / "lv 73" / "max" / a
    ladder rung / star/upgrade for custom; "" for binary)."""
    kind = entry["levels"]["kind"]
    if kind == "binary":
        return ""
    if kind == "ladder":
        labels = entry["levels"]["labels"]
        i = max(1, min(len(labels), int(owned)))
        return labels[i - 1]
    if kind == "custom":
        return "/".join(str(int(p)) for p in owned)
    if owned == -1:
        return "max"
    prefix = "Tier " if kind == "tier" else "lv "
    return f"{prefix}{int(owned)}"


def int_thresholds(entry: dict) -> list:
    """Sorted set of integer effect min_levels (absent defaults to 1). The
    'max' sentinel and any non-int thresholds are excluded."""
    return sorted({e.get("min_level", 1) for e in entry.get("effects", [])
                   if isinstance(e.get("min_level", 1), int)})


def has_max_effect(entry: dict) -> bool:
    """True when any effect gates on the 'max' sentinel."""
    return any(e.get("min_level") == "max" for e in entry.get("effects", []))


def value_model_error(model: dict):
    """Schema check for a value_model; a short message or None (the caller
    prefixes the source id)."""
    if model.get("kind") != STAR_UPGRADE:
        return "unknown value_model kind"
    if len(model["star_add"]) != model["stars"] or \
            sorted(model["star_add"]) != model["star_add"]:
        return "malformed star_add"
    return None
