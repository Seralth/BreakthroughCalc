"""Pet exchange planner math (pure logic, no Qt — Dart twin: mobile/lib/pets.dart).

The exchange system: pets are bought with rare essences, and eliminating an
owned copy refunds exactly its exchange cost, so every owned pet is also a
liquid essence reserve. The planner answers "if I went all-in on pet X, how
many copies could I end up with, and what rarity is that?" for every pet at
once. Both implementations run the shared fixture mobile/test/pet_cases.json.
Mechanics evidence: docs/knowledge/pet-mechanics.md.
"""

from __future__ import annotations

from dataclasses import dataclass

from .data_io import _load_catalog


def load_pets() -> dict:
    """The pet planner catalog (data/pets.json); {} when missing/corrupt."""
    data = _load_catalog("pets.json")
    return data if isinstance(data, dict) else {}


@dataclass(frozen=True)
class PetPlan:
    copies: int          # total copies reachable going all-in on this pet
    rarity: str | None   # highest rarity those copies afford (None: none)
    realm: str | None    # pet realm required to apply that rarity


def plan(catalog: dict, owned: dict, essences: dict) -> dict[str, PetPlan]:
    """All-in projection per pet.

    owned: {pet_id: copies}; essences: {essence_id: count}. The essence pool
    per type is what you hold plus the full refund from eliminating every
    owned pet (including copies of the pet being planned — re-exchanging
    them is lossless, so the projection stays exact). Non-exchangeable pets
    (cost null) can only ever total their owned copies.
    """
    pool = {e["id"]: int(essences.get(e["id"], 0))
            for e in catalog.get("essences", [])}
    for p in catalog.get("pets", []):
        n = int(owned.get(p["id"], 0))
        for ess, amt in (p.get("refund") or {}).items():
            pool[ess] = pool.get(ess, 0) + n * int(amt)

    out: dict[str, PetPlan] = {}
    for p in catalog.get("pets", []):
        cost = p.get("cost")
        if cost:
            copies = min(pool.get(e, 0) // int(amt) for e, amt in cost.items())
        else:
            copies = int(owned.get(p["id"], 0))
        tier = None
        for step in catalog.get("rarity_ladder", []):
            if copies >= int(step["copies"]):
                tier = step
        out[p["id"]] = PetPlan(
            copies,
            tier["name"] if tier else None,
            tier["realm"] if tier else None,
        )
    return out
