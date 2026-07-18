import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

import 'package:breakthrough_calc/advisor.dart';
import 'package:breakthrough_calc/engine.dart';

Map loadCatalog() =>
    jsonDecode(File('../data/sources.json').readAsStringSync()) as Map;

Engine loadEngine() => Engine(
    jsonDecode(File('../data/breakthrough.json').readAsStringSync())
        as Map<String, dynamic>);

Inputs baseInputs() => Inputs.fromMap({
      'stage': 'Nascent',
      'phase': 'LATE',
      'grade': 'G5',
      'culti_speed': 57.22,
      'absorption_ratio': 0.275,
    });

void main() {
  final catalog = loadCatalog();
  final engine = loadEngine();
  Map byId(String id) => ((catalog['sources'] as List)
      .cast<Map>()
      .firstWhere((s) => s['id'] == id));

  // Cross-platform parity layer: the same rank() scenarios the Python twin
  // asserts (tests/test_advisor.py). The advisors can only drift if one of
  // these suites goes red. Only values identical across both engines are
  // pinned — the ordered source_id lists, channels, valid and metric —
  // never raw day-savings.
  group('shared fixture (twin of tests/test_advisor.py)', () {
    final cases =
        jsonDecode(File('test/advisor_cases.json').readAsStringSync()) as List;
    for (final caseRaw in cases) {
      final c = caseRaw as Map;
      test(c['name'] as String, () {
        final adv = rank(
            engine,
            Inputs.fromMap((c['inputs'] as Map).cast<String, dynamic>()),
            catalog,
            c['shelf'] as Map);
        final exp = c['expect'] as Map;
        expect(adv.valid, exp['valid']);
        if (exp['valid'] != true) {
          expect(adv.plan, isEmpty);
          expect(adv.draws, isEmpty);
          expect(adv.reason, isNotEmpty);
          return;
        }
        expect(adv.metric, exp['metric']);
        expect([for (final r in adv.plan) r.candidate.sourceId],
            exp['plan_ids']);
        expect([for (final r in adv.draws) r.candidate.sourceId],
            exp['draws_ids']);
        // Channel-of-each plus the positive-and-sorted savings invariant.
        for (final entry in [
          [adv.plan, planned],
          [adv.draws, random]
        ]) {
          final grp = entry[0] as List<RankedStep>;
          final chan = entry[1] as String;
          final saved = [for (final r in grp) r.daysSaved];
          expect(saved.every((s) => s > 0), isTrue);
          final sortedDesc = List<double>.from(saved)
            ..sort((a, b) => b.compareTo(a));
          expect(saved, sortedDesc);
          for (final r in grp) {
            expect(r.candidate.channel, chan);
          }
        }
      });
    }
  });

  group('step tracks (twin of tests/test_advisor.py)', () {
    test('binary curio owned vs not', () {
      final lantern = byId('dongxuans_lantern');
      final tracks = steps(lantern, null);
      expect(tracks.length, 1);
      expect(tracks[0].single.action, 'Own');
      expect(steps(lantern, 1), isEmpty);
    });

    test('tier walk covers every future threshold', () {
      final tracks = steps(byId('longevity'), null);
      expect([for (final s in tracks.single) s.action], ['Tier 1', 'Tier 3']);
    });

    test('parametric curio tracks carry upgrade requirements', () {
      final tracks = steps(byId('yang_spirit_jade'), [6, 3]);
      expect(tracks.length, 1); // star maxed: upgrade track only
      expect(tracks.single.first.action, 'Upgrade level 4');
      expect(tracks.single.first.requireLevel, 18);
      expect(tracks.single.last.action, 'Upgrade level 8');
      expect(tracks.single.last.requireLevel, 26);
    });

    test('channels: curios are random draws', () {
      expect(channelFor(byId('dongxuans_lantern')), random);
      expect(channelFor(byId('chroma')), planned);
    });
  });

  group('obtainability', () {
    test('player level from realm table', () {
      expect(playerLevel(catalog, 'Novice', 'N/A'), 1);
      expect(playerLevel(catalog, 'Nascent', 'EARLY'), 18);
      expect(playerLevel(catalog, 'Voidbreak', 'LATE'), 26);
      expect(playerLevel(catalog, 'Atlantis', 'EARLY'), isNull);
    });

    test('blessing gated until Incarnation Late is completed', () {
      for (final lvl in [18, 21, 23]) {
        final ids = {
          for (final c in candidates(catalog, {'owned': {}},
              currentLevel: lvl))
            c.sourceId
        };
        expect(ids, isNot(contains('ascension_virya')), reason: '$lvl');
      }
      final voidbreak = {
        for (final c in candidates(catalog, {'owned': {}}, currentLevel: 24))
          c.sourceId
      };
      expect(voidbreak, contains('ascension_virya'));
    });

    test('R9 books need two R8 books at Tier 13', () {
      final none = {
        for (final c in candidates(catalog, {'owned': {}})) c.sourceId
      };
      expect(none, isNot(contains('laws_of_nature')));
      final ready = {
        for (final c in candidates(catalog, {
          'owned': {'chroma': 13, 'zixiao_sutra': 13}
        }))
          c.sourceId
      };
      expect(ready, contains('laws_of_nature'));
    });

    test('friends gated until Voidbreak', () {
      final pre = {
        for (final c in candidates(catalog, {'owned': {}}, currentLevel: 23))
          c.sourceId
      };
      expect(pre, isNot(contains('daji')));
      final post = {
        for (final c in candidates(catalog, {'owned': {}}, currentLevel: 24))
          c.sourceId
      };
      expect(post, contains('daji'));
    });

    test('book ranks gate by realm phase', () {
      Set<String> ids(int level, [Map? owned]) => {
            for (final c in candidates(catalog, {'owned': owned ?? {}},
                currentLevel: level))
              c.sourceId
          };
      expect(ids(19), isNot(contains('lions_roar')));
      expect(ids(20), contains('lions_roar'));
      expect(ids(14), isNot(contains('longevity')));
      expect(ids(15), contains('longevity'));
      expect(ids(21), isNot(contains('chroma')));
      expect(ids(22), contains('chroma'));
      final ready = {'chroma': 13, 'zixiao_sutra': 13};
      expect(ids(22, ready), isNot(contains('laws_of_nature')));
      expect(ids(23, ready), contains('laws_of_nature'));
    });

    test('curio upgrades gate on realm level', () {
      final shelf = {
        'owned': {
          'yang_spirit_jade': [6, 3]
        }
      };
      final low = [
        for (final c in candidates(catalog, shelf, currentLevel: 12))
          if (c.sourceId == 'yang_spirit_jade') c
      ];
      expect(low, isEmpty);
      final mid = [
        for (final c in candidates(catalog, shelf, currentLevel: 18))
          if (c.sourceId == 'yang_spirit_jade') c
      ];
      expect([for (final c in mid) c.action], ['Upgrade level 4']);
    });
  });

  group('ranking', () {
    final inp = baseInputs()
      ..targetStage = 'Incarnation'
      ..pillRank = '4R'
      ..pillLimit = 4
      ..pillEffect = 0.04
      ..goldPerDay = 4
      ..respiraPerDay = 10
      ..respiraExp = 4041.0;

    test('splits plan from random draws, blessing hidden pre-ascension', () {
      final adv = rank(engine, inp, catalog, {'owned': {}});
      expect(adv.valid, isTrue);
      expect(adv.metric, 'target');
      expect(adv.plan, isNotEmpty);
      expect(adv.draws, isNotEmpty);
      for (final r in adv.plan) {
        expect(r.candidate.channel, planned);
      }
      for (final r in adv.draws) {
        expect(r.candidate.channel, random);
      }
      final ids = {
        for (final r in [...adv.plan, ...adv.draws]) r.candidate.sourceId
      };
      expect(ids, contains('dongxuans_lantern'));
      expect(ids, isNot(contains('ascension_virya')));
    });

    test('savings positive and sorted', () {
      final adv = rank(engine, inp, catalog, {'owned': {}});
      for (final group in [adv.plan, adv.draws]) {
        final saved = [for (final r in group) r.daysSaved];
        expect(saved.every((s) => s > 0), isTrue);
        final sorted = List<double>.from(saved)
          ..sort((a, b) => b.compareTo(a));
        expect(saved, sorted);
      }
    });

    test('ties break by cheapness: R1 book above R3 above friends', () {
      final vb = Inputs.fromMap({
        'stage': 'Voidbreak',
        'phase': 'EARLY',
        'grade': 'G1',
        'culti_speed': 208.0,
        'absorption_ratio': 1.0,
        'target_stage': 'Wholeness',
      });
      final adv = rank(engine, vb, catalog, {'owned': {}});
      final order = [for (final r in adv.plan) r.candidate.sourceId];
      expect(order, contains('longevity'));
      expect(order, contains('cosmic_power'));
      expect(order.indexOf('longevity'),
          lessThan(order.indexOf('cosmic_power')));
    });

    test('blank respira fields floor to the stock minimum', () {
      final bare = baseInputs()..targetStage = 'Incarnation';
      final adv = rank(engine, bare, catalog, {'owned': {}});
      final ids = {
        for (final r in [...adv.plan, ...adv.draws]) r.candidate.sourceId
      };
      expect(ids, contains('dongxuans_cushion')); // +1 attempt on stock 10
      expect(ids, contains('dongxuans_lantern')); // +10% on the estimate
    });
  });
}
