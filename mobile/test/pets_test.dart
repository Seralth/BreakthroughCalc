// Pet planner math against the shared fixture (Python twin:
// tests/test_pets.py runs the same cases).
import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

import 'package:breakthrough_calc/pets.dart';

void main() {
  final catalog =
      jsonDecode(File('../data/pets.json').readAsStringSync()) as Map;

  test('shared fixture cases match the Python derivation', () {
    final cases =
        jsonDecode(File('test/pet_cases.json').readAsStringSync()) as List;
    for (final caseRaw in cases) {
      final c = caseRaw as Map;
      final got = planPets(
        catalog,
        (c['owned'] as Map).map((k, v) => MapEntry(k as String, v as int)),
        (c['essences'] as Map).map((k, v) => MapEntry(k as String, v as int)),
      );
      (c['expect'] as Map).forEach((pid, wantRaw) {
        final want = wantRaw as Map;
        final p = got[pid]!;
        expect(p.copies, want['copies'], reason: '${c['name']}: $pid copies');
        expect(p.rarity, want['rarity'], reason: '${c['name']}: $pid rarity');
        expect(p.realm, want['realm'], reason: '${c['name']}: $pid realm');
      });
    }
  });
}
