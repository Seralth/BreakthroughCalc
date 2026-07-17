/// Pet exchange planner math (pure logic, no Flutter — Python twin:
/// breakthrough_calc/pets.py).
///
/// The exchange system: pets are bought with rare essences, and eliminating
/// an owned copy refunds exactly its exchange cost, so every owned pet is
/// also a liquid essence reserve. The planner answers "if I went all-in on
/// pet X, how many copies could I end up with, and what rarity is that?"
/// for every pet at once. Both implementations run the shared fixture
/// test/pet_cases.json. Mechanics evidence: docs/knowledge/pet-mechanics.md.
library;

class PetPlan {
  final int copies; // total copies reachable going all-in on this pet
  final String? rarity; // highest rarity those copies afford (null: none)
  final String? realm; // pet realm required to apply that rarity
  const PetPlan(this.copies, this.rarity, this.realm);
}

/// All-in projection per pet.
///
/// [owned]: {petId: copies}; [essences]: {essenceId: count}. The essence
/// pool per type is what you hold plus the full refund from eliminating
/// every owned pet (including copies of the pet being planned —
/// re-exchanging them is lossless, so the projection stays exact).
/// Non-exchangeable pets (cost null) can only ever total their owned copies.
Map<String, PetPlan> planPets(
    Map catalog, Map<String, int> owned, Map<String, int> essences) {
  final pool = <String, int>{
    for (final e in (catalog['essences'] ?? []) as List)
      (e as Map)['id'] as String: essences[e['id']] ?? 0
  };
  for (final p in (catalog['pets'] ?? []) as List) {
    final n = owned[(p as Map)['id']] ?? 0;
    for (final ent in ((p['refund'] as Map?) ?? {}).entries) {
      pool[ent.key as String] =
          (pool[ent.key] ?? 0) + n * (ent.value as num).toInt();
    }
  }

  final out = <String, PetPlan>{};
  for (final p in (catalog['pets'] ?? []) as List) {
    final cost = (p as Map)['cost'] as Map?;
    int copies;
    if (cost != null && cost.isNotEmpty) {
      copies = cost.entries
          .map((ent) =>
              (pool[ent.key] ?? 0) ~/ (ent.value as num).toInt())
          .reduce((a, b) => a < b ? a : b);
    } else {
      copies = owned[p['id']] ?? 0;
    }
    Map? tier;
    for (final step in (catalog['rarity_ladder'] ?? []) as List) {
      if (copies >= ((step as Map)['copies'] as num).toInt()) tier = step;
    }
    out[p['id'] as String] = PetPlan(
        copies, tier?['name'] as String?, tier?['realm'] as String?);
  }
  return out;
}
