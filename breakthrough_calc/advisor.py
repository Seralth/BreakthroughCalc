"""Advisor (pure module — no Qt): ranks the next Vault step by time saved.

For every catalog source the advisor proposes the next step that could
unlock an effect — own it, or raise it to the next effect threshold —
recomputes the shelf derivation with that step taken, maps the derived
target deltas onto a copy of the current engine Inputs, and diffs
Engine.calculate. The ranking metric is days toward the target Stage when
one is set, otherwise days to finish the current Stage.

Acquisition channels: the Vault knows what you own, and HOW the rest is
obtained decides where a step ranks. Books, friend levels and blessing
tiers are things you can plan toward, so they form the plan list. Curios
drop from random draws — you cannot simply go buy the next one — so curio
steps rank in a separate draws list ("worth pulling for") instead of
pretending they are plannable.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from .engine import Engine, Inputs, Results
from .shelf import derive

PLANNED = "planned"
RANDOM = "random"

# How each category's next step is acquired in game. Curio steps (both new
# curios and the shards/materials that star them up) come from random draws.
_CHANNEL_BY_CATEGORY = {"curio": RANDOM}

# raw_additive target -> (Inputs attr, catalog-unit -> Inputs-unit scale).
# respira_effect is handled separately: it is embedded in the respira_exp
# reading, so a delta rescales that reading instead of adding to a field.
_APPLY = {
    "pill_effect": ("pill_effect", 0.01),
    "pill_attempts": ("pill_limit", 1.0),
    "respira_attempts": ("respira_per_day", 1.0),
    "bless_pp": ("bless_pp", 1.0),
    "bless_window_pp": ("bless_window_pp", 1.0),
}


@dataclass(frozen=True)
class Candidate:
    source_id: str
    name: str
    category: str
    channel: str
    action: str            # "Own" / "Tier 7" / "lv 73" / "max" / "Star 5" / rung label
    new_owned: object      # the owned[] value once the step is taken
    deltas: dict           # target -> +value in catalog units


@dataclass(frozen=True)
class Ranked:
    candidate: Candidate
    days_saved: float


@dataclass(frozen=True)
class Advice:
    valid: bool
    reason: str = ""
    metric: str = ""            # "target" | "stage"
    baseline_days: float = 0.0
    plan: tuple = ()            # Ranked, best first
    draws: tuple = ()           # Ranked, best first


def channel_for(entry: dict) -> str:
    return _CHANNEL_BY_CATEGORY.get(entry.get("category"), PLANNED)


def _int_thresholds(entry: dict) -> list:
    return sorted({e.get("min_level", 1) for e in entry.get("effects", [])
                   if isinstance(e.get("min_level", 1), int)})


def steps(entry: dict, owned) -> list:
    """The next step(s) for one source: [] when maxed or nothing to unlock.

    Steps target the next EFFECT threshold, not the next raw level — a
    recommendation must change something the calculator can price.
    """
    levels = entry["levels"]
    kind = levels["kind"]
    if not entry.get("effects"):
        return []
    if kind == "binary":
        return [] if owned is not None else [("Own", 1)]
    if kind == "custom":
        params = levels["params"]
        if owned is None:
            return [("Own", [int(p["min"]) for p in params])]
        vals = [int(v) for v in owned]
        out = []
        for i, p in enumerate(params):
            if vals[i] < int(p["max"]):
                nxt = list(vals)
                nxt[i] += 1
                out.append((f"{p['label']} {nxt[i]}", nxt))
        return out
    if kind == "ladder":
        labels = levels["labels"]
        cur = int(owned) if owned else 0
        return [(labels[cur], cur + 1)] if cur < len(labels) else []
    # tier / level: the next effect threshold above the current level.
    if owned == -1:
        return []
    cur = int(owned) if owned else 0
    for t in _int_thresholds(entry):
        if t > cur:
            prefix = "Tier " if kind == "tier" else "lv "
            return [(f"{prefix}{t}", t)]
    if any(e.get("min_level") == "max" for e in entry.get("effects", [])):
        return [("max", -1)]
    return []


def _totals(derived: dict, targets: dict) -> dict:
    return {tid: d.total for tid, d in derived.items()
            if targets.get(tid, {}).get("mode") == "raw_additive"}


def candidates(catalog: dict, shelf: dict) -> list:
    """Every next step with a nonzero raw-target delta, unranked."""
    targets = catalog.get("targets", {})
    owned = shelf.get("owned") or {}
    before = _totals(derive(catalog, shelf), targets)
    out = []
    for entry in catalog.get("sources", []):
        sid = entry["id"]
        for action, new_owned in steps(entry, owned.get(sid)):
            shelf2 = dict(shelf)
            shelf2["owned"] = {**owned, sid: new_owned}
            after = _totals(derive(catalog, shelf2), targets)
            deltas = {}
            for tid in after.keys() | before.keys():
                dv = after.get(tid, 0.0) - before.get(tid, 0.0)
                if abs(dv) > 1e-12:
                    deltas[tid] = dv
            if deltas:
                out.append(Candidate(sid, entry["name"], entry["category"],
                                     channel_for(entry), action, new_owned,
                                     deltas))
    return out


def apply_deltas(inp: Inputs, deltas: dict, books_now: float) -> Inputs | None:
    """A copy of `inp` with the candidate's bonuses landed, or None when
    nothing the engine models would change."""
    kw = {}
    for tid, dv in deltas.items():
        if tid == "respira_effect":
            # The respira_exp reading already contains today's book/curio
            # percent; rescale it as if the new percent were active.
            if inp.respira_exp > 0:
                kw["respira_exp"] = (inp.respira_exp
                                     * (100.0 + books_now + dv)
                                     / (100.0 + books_now))
            continue
        m = _APPLY.get(tid)
        if m is not None:
            attr, scale = m
            kw[attr] = getattr(inp, attr) + dv * scale
    return replace(inp, **kw) if kw else None


def _metric_days(r: Results, metric: str) -> float:
    return r.target_days if metric == "target" else r.stage_days


def rank(engine: Engine, inp: Inputs, catalog: dict, shelf: dict) -> Advice:
    base = engine.calculate(inp)
    if not base.valid:
        return Advice(valid=False, reason=base.error)
    metric = "target" if base.target_valid else "stage"
    base_days = _metric_days(base, metric)
    if base_days <= 0:
        return Advice(valid=False, reason="nothing left to shorten")
    derived = derive(catalog, shelf)
    books_now = derived.get("respira_effect").total \
        if "respira_effect" in derived else 0.0
    plan, draws = [], []
    for cand in candidates(catalog, shelf):
        inp2 = apply_deltas(inp, cand.deltas, books_now)
        if inp2 is None:
            continue
        r2 = engine.calculate(inp2)
        if not r2.valid:
            continue
        saved = base_days - _metric_days(r2, metric)
        if saved <= 1e-9:
            continue
        (plan if cand.channel == PLANNED else draws).append(
            Ranked(cand, saved))
    plan.sort(key=lambda r: (-r.days_saved, r.candidate.name))
    draws.sort(key=lambda r: (-r.days_saved, r.candidate.name))
    return Advice(valid=True, metric=metric, baseline_days=base_days,
                  plan=tuple(plan), draws=tuple(draws))
