import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

import 'package:breakthrough_calc/shelf.dart';

Map loadCatalog() =>
    jsonDecode(File('../data/sources.json').readAsStringSync()) as Map;

List loadJsonList(String path) =>
    jsonDecode(File(path).readAsStringSync()) as List;

void main() {
  final catalog = loadCatalog();

  test('shared fixture cases match the Python derivation', () {
    for (final caseRaw in loadJsonList('test/shelf_cases.json')) {
      final c = caseRaw as Map;
      final derived = derive(catalog, c['shelf'] as Map);
      final got = derived.map((tid, d) => MapEntry(tid, d.total));
      final expect_ = (c['expect'] as Map).cast<String, num>();
      expect(got.keys.toSet(), expect_.keys.toSet(), reason: c['name'] as String);
      expect_.forEach((tid, want) {
        expect(got[tid], closeTo(want.toDouble(), 1e-9),
            reason: '${c['name']}: $tid');
      });
    }
  });

  test('contributions carry provenance and deterministic order', () {
    final d = derive(catalog, {
      'owned': {'moon_meru': 12, 'six_eared_macaque': 17, 'purify_cleanse': 3}
    })['respira_effect']!;
    expect(d.contributions.map((c) => c.sourceId).toList(),
        ['moon_meru', 'purify_cleanse', 'six_eared_macaque']);
    expect(
        derive(catalog, {
          'owned': {'purify_cleanse': 9}
        })['respira_effect']!
            .contributions
            .first
            .levelLabel,
        'Tier 9');
  });

  test('effective precedence: override > base + derived', () {
    final d = derive(catalog, {
      'owned': {'chroma': 12}
    })['pill_attempts'];
    expect(effective(d, null, base: 10.0), 11.0);
    expect(effective(d, 15.0, base: 10.0), 15.0);
    expect(effective(null, null, base: 10.0), 10.0);
  });

  test('legacy migration reproduces the old pill-effect total exactly', () {
    final pe = loadJsonList('../data/pill_effect_sources.json');
    final rows = [
      for (final e in pe) [(e as Map)['name'], (e['percent'] as num).toDouble()]
    ];
    final oldTotal = rows.fold<double>(0, (a, r) => a + (r[1] as double));
    final result = migrateLegacy(rows.cast<List<dynamic>>(), [], catalog);
    final derived = derive(
        catalog, {'owned': result[0], 'custom': result[1]})['pill_effect']!;
    expect(derived.total, closeTo(oldTotal, 1e-9));
  });

  test('legacy respira names max-merge with pe implications', () {
    final result = migrateLegacy([
      ['Chroma (R8 technique)', 4.0]
    ], [
      'Chroma Tier 3 (R8 technique)',
      'Chroma (R8 book, Tier 3)'
    ], catalog);
    expect((result[0] as Map)['chroma'], 6);
  });

  test('parametric and free-typed rows preserved as custom extras', () {
    final result = migrateLegacy([
      ['Yang Spirit Jade (curio)', 3.4],
      ['My event buff', 2.0]
    ], [], catalog);
    final owned = result[0] as Map;
    final custom = result[1] as Map;
    expect(owned.containsKey('yang_spirit_jade'), isFalse);
    expect(custom['pill_effect'], [
      ['Yang Spirit Jade (curio)', 3.4],
      ['My event buff', 2.0]
    ]);
    expect((result[2] as List), isNotEmpty);
  });
}
