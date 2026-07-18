"""Sources Shelf: pure derivation logic (no Qt).

The shelf records what the player OWNS (data/sources.json catalog +
per-profile owned levels); this module turns that into per-target
contribution lists and totals that the UI writes into the same input
widgets the user would otherwise type into. The engine never sees the
shelf. Mirrored by mobile/lib/shelf.dart — keep in lockstep (pinned by the
shared fixture mobile/test/shelf_cases.json).

Target modes (the double-counting taxonomy, machine-checked in
tests/test_shelf.py):
- raw_additive:      the shelf may write the target's input field.
- display_embedded:  NEVER written — the entered value already contains
                     these effects; the catalog may not aim effects here
                     (effects_allowed: false), except informational notes.
- informational:     breakdown-only text.

Owned map shapes, by the source's levels.kind:
- binary: 1 (owned)
- tier:   tier number 1..max
- level:  the friend's level; -1 means "maxed" and satisfies every
          threshold including the "max" sentinel
- ladder: index 1..len(labels); owning tier N implies all lower tiers
- custom: ordered param list per levels.params (e.g. [star, upgrade])
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .catalog import (
    effect_active, effect_value, level_label, value_model_error,
)
from .data_io import _load_catalog


def load_sources() -> dict:
    """The shelf catalog; {} when the data file is missing (empty shelf)."""
    data = _load_catalog("sources.json")
    return data if isinstance(data, dict) else {}


@dataclass(frozen=True)
class Contribution:
    source_id: str
    name: str
    level_label: str
    value: float
    data_status: str
    note: str


@dataclass(frozen=True)
class Derived:
    total: float
    contributions: tuple = ()
    custom: tuple = ()          # ((label, value), ...) free-form extras
    incomplete: bool = False    # an active effect has no recorded value


def derive(catalog: dict, shelf: dict) -> dict:
    """shelf = {"owned": {id: level|params}, "custom": {target: [[label, v]]}}
    -> {target_id: Derived} for every raw_additive/informational target that
    received anything. Unknown-value effects contribute 0 and set
    `incomplete`. Contributions are ordered by (category order, -value,
    name) — presentational, pinned by tests."""
    targets = catalog.get("targets", {})
    cat_order = {c["id"]: i for i, c in enumerate(catalog.get("categories", []))}
    by_id = {s["id"]: s for s in catalog.get("sources", [])}
    buckets: dict[str, list] = {}
    incomplete: dict[str, bool] = {}

    for sid, owned in (shelf.get("owned") or {}).items():
        entry = by_id.get(sid)
        if entry is None:
            continue                      # version-skew passenger
        levels = entry["levels"]
        for eff in entry.get("effects", []):
            tid = eff["target"]
            mode = targets.get(tid, {}).get("mode")
            if mode == "display_embedded":
                continue                  # guarded: never derives a value
            if not effect_active(levels, eff.get("min_level"), owned):
                continue
            value = effect_value(eff, owned)
            if value is None and mode == "raw_additive":
                incomplete[tid] = True
            if mode != "raw_additive":
                continue                  # info effects carry no numbers
            buckets.setdefault(tid, []).append(Contribution(
                source_id=sid, name=entry["name"],
                level_label=level_label(entry, owned),
                value=value if value is not None else 0.0,
                data_status=eff.get("data_status", entry.get("data_status", "exact")),
                note=eff.get("note", "")))

    out: dict[str, Derived] = {}
    all_targets = set(buckets) | set(incomplete) | set(shelf.get("custom") or {})
    for tid in all_targets:
        if targets.get(tid, {}).get("mode") != "raw_additive":
            continue
        contribs = sorted(
            buckets.get(tid, []),
            key=lambda c: (cat_order.get(by_id[c.source_id]["category"], 99),
                           -c.value, c.name))
        custom = tuple((str(l), float(v))
                       for l, v in (shelf.get("custom") or {}).get(tid, []))
        total = sum(c.value for c in contribs) + sum(v for _, v in custom)
        out[tid] = Derived(total=total, contributions=tuple(contribs),
                           custom=custom, incomplete=incomplete.get(tid, False))
    return out


def effective(derived: Derived | None, override: float | None,
              base: float = 0.0) -> float:
    """Field value under the precedence: manual override > base + derived."""
    if override is not None:
        return override
    return base + (derived.total if derived else 0.0)


def migrate_legacy(pe_rows: list, respira_checked: list, catalog: dict) -> tuple:
    """One-time mapping of the old inputs into shelf state.

    pe_rows: [[name, percent], ...] (the old pill-effect rows)
    respira_checked: [name, ...] (old checked attempt sources)
    -> (owned, custom, notes)
       owned:  {id: level} max-merged across aliases
       custom: {"pill_effect": [[label, value], ...]} for unmatched or
               parametric rows (values preserved exactly)
       notes:  [str] user-facing migration remarks

    Callers must ALSO rebase base:"user" targets so field values stay
    identical: new residual base = old input value - sum of migrated
    contributions for that target (applied in the UI layer, not here).
    """
    alias = {}
    for s in catalog.get("sources", []):
        for a in s.get("legacy", []):
            alias[(a["catalog"], a["name"])] = (s["id"], a)
    owned: dict = {}
    custom: dict = {}
    notes: list = []

    def claim(sid: str, level) -> None:
        cur = owned.get(sid)
        if cur is None or (cur != -1 and (level == -1 or level > cur)):
            owned[sid] = level

    for row in pe_rows or []:
        name, pct = row[0], float(row[1])
        hit = alias.get(("pe", name))
        if hit is None:
            custom.setdefault("pill_effect", []).append([name, pct])
            continue
        sid, a = hit
        if a.get("parametric"):
            custom.setdefault("pill_effect", []).append([name, pct])
            notes.append(f"{name}: re-select it on the shelf to track its "
                         "star and upgrade level automatically.")
            continue
        claim(sid, a["implies_level"])
    for name in respira_checked or []:
        hit = alias.get(("respira", name))
        if hit is not None:
            sid, a = hit
            claim(sid, a["implies_level"])
    return owned, custom, notes


def validate_catalog(catalog: dict) -> list:
    """Schema rules a consistency test enforces; returns error strings."""
    errors: list = []
    targets = catalog.get("targets", {})
    cats = {c["id"] for c in catalog.get("categories", [])}
    ids: set = set()
    names: set = set()
    for key in ("schema_version", "catalog_version"):
        if not isinstance(catalog.get(key), int):
            errors.append(f"{key} must be an int")
    for tid, t in targets.items():
        mode = t.get("mode")
        if mode not in ("raw_additive", "display_embedded", "informational"):
            errors.append(f"target {tid}: bad mode {mode!r}")
        if mode == "raw_additive" and not t.get("field"):
            errors.append(f"target {tid}: raw_additive needs a field")
    for s in catalog.get("sources", []):
        sid = s.get("id", "")
        if not sid or not all(c.isascii() and (c.islower() or c.isdigit() or c == "_")
                              for c in sid):
            errors.append(f"bad id {sid!r}")
        if sid in ids:
            errors.append(f"duplicate id {sid}")
        ids.add(sid)
        lname = s.get("name", "").lower()
        if lname in names:
            errors.append(f"duplicate name {s.get('name')!r}")
        names.add(lname)
        if s.get("category") not in cats:
            errors.append(f"{sid}: unknown category {s.get('category')!r}")
        levels = s.get("levels", {})
        kind = levels.get("kind")
        if kind not in ("binary", "tier", "level", "ladder", "custom"):
            errors.append(f"{sid}: bad levels.kind {kind!r}")
        if kind == "tier" and not (isinstance(levels.get("max"), int)
                                   and levels["max"] >= 1):
            errors.append(f"{sid}: tier needs int max >= 1")
        if kind == "ladder" and not levels.get("labels"):
            errors.append(f"{sid}: ladder needs labels")
        if kind == "custom" and not levels.get("params"):
            errors.append(f"{sid}: custom needs params")
        if s.get("data_status") not in ("exact", "community", "unknown"):
            errors.append(f"{sid}: bad data_status")
        for eff in s.get("effects", []):
            tid = eff.get("target")
            t = targets.get(tid)
            if t is None:
                errors.append(f"{sid}: unknown target {tid!r}")
                continue
            if t.get("effects_allowed") is False:
                errors.append(f"{sid}: target {tid} forbids effects")
            has_value = eff.get("value") is not None
            has_model = "value_model" in eff
            status = eff.get("data_status", s.get("data_status"))
            if has_value and has_model:
                errors.append(f"{sid}: value XOR value_model")
            if (not has_value and not has_model and status != "unknown"
                    and t.get("mode") == "raw_additive"):
                errors.append(f"{sid}: {tid} effect needs a value unless unknown")
            ml = eff.get("min_level")
            if ml == "max" and kind != "level":
                errors.append(f"{sid}: 'max' sentinel only on level kind")
            elif ml is not None and ml != "max":
                if not isinstance(ml, int) or ml < 1:
                    errors.append(f"{sid}: bad min_level {ml!r}")
                elif kind == "tier" and ml > levels["max"]:
                    errors.append(f"{sid}: min_level {ml} above max")
                elif kind == "ladder" and ml > len(levels["labels"]):
                    errors.append(f"{sid}: min_level {ml} above ladder")
            cond = eff.get("condition")
            if cond is not None:
                if cond.get("kind") != "before_row":
                    errors.append(f"{sid}: unknown condition kind")
                if tid != "bless_window_pp":
                    errors.append(f"{sid}: conditions may only decorate "
                                  "bless_window_pp (the engine owns windows)")
            if has_model:
                msg = value_model_error(eff["value_model"])
                if msg:
                    errors.append(f"{sid}: {msg}")
    return errors
