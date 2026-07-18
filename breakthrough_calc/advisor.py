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
# respira_effect and the blessing targets are handled separately: both are
# embedded in an entered reading (respira_exp / the absorption total), so a
# delta rescales that reading instead of adding to a field.
_APPLY = {
    "pill_effect": ("pill_effect", 0.01),
    "pill_attempts": ("pill_limit", 1.0),
    "respira_attempts": ("respira_per_day", 1.0),
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


def player_level(catalog: dict, stage: str, phase: str):
    """The player's realm-level index (the client's gating unit), from the
    catalog's realm_levels table. Early/Middle/Late are the sub-levels of a
    Stage; multi-sub Stages (Connection) resolve to the entry level. None
    when the Stage is unknown — gating then stays permissive."""
    band = (catalog.get("realm_levels") or {}).get(stage)
    if not band:
        return None
    lo, hi = band
    offset = {"EARLY": 0, "MIDDLE": 1, "LATE": 2}.get(phase, 0)
    return min(lo + offset, hi)


def steps(entry: dict, owned) -> list:
    """Upgrade tracks for one source: a list of tracks, each an ordered
    list of (action, new_owned, require_level) future steps. A candidate is
    the first step on a track that changes something the calculator can
    price; require_level (or None) is the realm-level gate for that step.
    """
    levels = entry["levels"]
    kind = levels["kind"]
    if not entry.get("effects"):
        return []
    if kind == "binary":
        return [] if owned is not None else [[("Own", 1, None)]]
    if kind == "custom":
        params = levels["params"]
        reqs = entry.get("upgrade_requires_level")
        if owned is None:
            return [[("Own", [int(p["min"]) for p in params], None)]]
        vals = [int(v) for v in owned]
        tracks = []
        for i, p in enumerate(params):
            track = []
            for nv in range(vals[i] + 1, int(p["max"]) + 1):
                nxt = list(vals)
                nxt[i] = nv
                req = None
                if p.get("id") == "upgrade" and reqs and nv < len(reqs):
                    req = reqs[nv]
                track.append((f"{p['label']} {nv}", nxt, req))
            if track:
                tracks.append(track)
        return tracks
    if kind == "ladder":
        labels = levels["labels"]
        cur = int(owned) if owned else 0
        return [[(labels[i], i + 1, None)
                 for i in range(cur, len(labels))]] if cur < len(labels) \
            else []
    # tier / level: walk the effect thresholds above the current level.
    if owned == -1:
        return []
    cur = int(owned) if owned else 0
    prefix = "Tier " if kind == "tier" else "lv "
    track = [(f"{prefix}{t}", t, None)
             for t in _int_thresholds(entry) if t > cur]
    if any(e.get("min_level") == "max" for e in entry.get("effects", [])):
        track.append(("max", -1, None))
    return [track] if track else []


def _totals(derived: dict, targets: dict) -> dict:
    return {tid: d.total for tid, d in derived.items()
            if targets.get(tid, {}).get("mode") == "raw_additive"}


def candidates(catalog: dict, shelf: dict, current_level=None) -> list:
    """Every obtainable next step with a nonzero raw-target delta.

    Per track, the first step that changes a raw target becomes the
    candidate; steps whose realm-level requirement exceeds current_level
    are unobtainable and end their track. Sources gated by requires.stage
    the player has not reached are skipped entirely.
    """
    targets = catalog.get("targets", {})
    realm = catalog.get("realm_levels") or {}
    owned = shelf.get("owned") or {}
    by_rank: dict = {}
    for s in catalog.get("sources", []):
        if s["category"] == "technique_book" and s.get("rank"):
            by_rank.setdefault(s["rank"], []).append(s["id"])
    before = _totals(derive(catalog, shelf), targets)
    out = []
    for entry in catalog.get("sources", []):
        sid = entry["id"]
        req = entry.get("requires") or {}
        req_stage = req.get("stage")
        if req_stage and current_level is not None:
            band = realm.get(req_stage)
            if band and current_level < band[0]:
                continue
        rb = req.get("rank_books")
        if rb:
            have = 0
            for bid in by_rank.get(rb["rank"], []):
                lvl = owned.get(bid)
                if lvl == -1 or (isinstance(lvl, int) and lvl >= rb["tier"]):
                    have += 1
            if have < rb["count"]:
                continue
        for track in steps(entry, owned.get(sid)):
            for action, new_owned, req_level in track:
                if (req_level is not None and current_level is not None
                        and current_level < req_level):
                    break                 # steps beyond this stay locked too
                shelf2 = dict(shelf)
                shelf2["owned"] = {**owned, sid: new_owned}
                after = _totals(derive(catalog, shelf2), targets)
                deltas = {}
                for tid in after.keys() | before.keys():
                    dv = after.get(tid, 0.0) - before.get(tid, 0.0)
                    if abs(dv) > 1e-12:
                        deltas[tid] = dv
                if deltas:
                    out.append(Candidate(sid, entry["name"],
                                         entry["category"],
                                         channel_for(entry), action,
                                         new_owned, deltas))
                    break                 # first priced step wins the track
    return out


def apply_deltas(inp: Inputs, deltas: dict, books_now: float,
                 engine: Engine | None = None) -> Inputs | None:
    """A copy of `inp` with the candidate's bonuses landed, or None when
    nothing the engine models would change."""
    kw = {}
    bless_dv = deltas.get("bless_pp", 0.0)
    window_dv = deltas.get("bless_window_pp", 0.0)
    if bless_dv or window_dv:
        # The absorption reading is (row base + blessing pp) x (1 + Strive).
        # Acquiring a tier raises the reading; Strive stays what it was, so
        # the counterfactual rescales by the blessed-base ratio. Without the
        # row's base the gain cannot be priced — skip rather than misprice.
        if engine is None:
            return None
        base = engine.base_low(inp.stage, inp.phase, inp.grade)
        if base is None or base <= 0 or inp.absorption_ratio <= 0:
            return None
        in_window = engine.blessing_applies(inp.stage, inp.phase, inp.grade)
        blessed = base + inp.bless_pp + \
            (inp.bless_window_pp if in_window else 0.0)
        now_dv = bless_dv + (window_dv if in_window else 0.0)
        if now_dv and blessed > 0:
            factor = (blessed + now_dv) / blessed
            kw["absorption_ratio"] = inp.absorption_ratio * factor
            # Abode Aura is speed / absorption and a blessing leaves it
            # untouched, so the current XP/tick rises with the ratio.
            kw["culti_speed"] = inp.culti_speed * factor
        if bless_dv:
            kw["bless_pp"] = inp.bless_pp + bless_dv
        if window_dv:
            kw["bless_window_pp"] = inp.bless_window_pp + window_dv
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


def _cost_key(cand: Candidate, by_id: dict) -> tuple:
    """Tie-break for equal savings: the cheapest step first. Heuristic
    order — books before the blessing before friends (books are the
    cheapest deterministic progress), lower ranks before higher (an R1
    book costs far less than an R5), then the smaller step."""
    entry = by_id.get(cand.source_id, {})
    cat = {"technique_book": 0, "exclusive_book": 0,
           "blessing": 1, "immortal_friend": 2}.get(entry.get("category"), 3)
    rank = entry.get("rank")
    rank_n = 99
    if isinstance(rank, str) and rank[:1] == "R" and rank[1:].isdigit():
        rank_n = int(rank[1:])
    elif isinstance(rank, int):
        rank_n = rank
    new = cand.new_owned
    if isinstance(new, list):
        mag = sum(int(v) for v in new)
    elif new == -1:
        mag = 10**6
    else:
        mag = int(new)
    return (cat, rank_n, mag, cand.name)


def _metric_days(r: Results, metric: str) -> float:
    return r.target_days if metric == "target" else r.stage_days


def _with_respira_floor(engine: Engine, inp: Inputs, derived: dict) -> Inputs:
    """Respira never counts as empty: blank fields assume the game's stock
    minimum — 10 daily attempts plus the Vault's permanent bonuses, and the
    Stage's base EXP estimate times the Vault's Respira Effect percent —
    so respira sources always price instead of silently vanishing."""
    kw = {}
    if inp.respira_per_day <= 0:
        attempts = derived.get("respira_attempts")
        kw["respira_per_day"] = 10.0 + (attempts.total if attempts else 0.0)
    if inp.respira_exp <= 0:
        est = engine.respira_base_estimate(inp.stage)
        if est:
            books = derived.get("respira_effect")
            pct = books.total if books else 0.0
            kw["respira_exp"] = est * (1.0 + pct / 100.0)
    return replace(inp, **kw) if kw else inp


def rank(engine: Engine, inp: Inputs, catalog: dict, shelf: dict) -> Advice:
    derived = derive(catalog, shelf)
    inp = _with_respira_floor(engine, inp, derived)
    base = engine.calculate(inp)
    if not base.valid:
        return Advice(valid=False, reason=base.error)
    metric = "target" if base.target_valid else "stage"
    base_days = _metric_days(base, metric)
    if base_days <= 0:
        return Advice(valid=False, reason="nothing left to shorten")
    books_now = derived.get("respira_effect").total \
        if "respira_effect" in derived else 0.0
    level_now = player_level(catalog, inp.stage, inp.phase)
    by_id = {s["id"]: s for s in catalog.get("sources", [])}
    plan, draws = [], []
    for cand in candidates(catalog, shelf, level_now):
        inp2 = apply_deltas(inp, cand.deltas, books_now, engine)
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
    key = lambda r: (-r.days_saved, *_cost_key(r.candidate, by_id))  # noqa: E731
    plan.sort(key=key)
    draws.sort(key=key)
    return Advice(valid=True, metric=metric, baseline_days=base_days,
                  plan=tuple(plan), draws=tuple(draws))
