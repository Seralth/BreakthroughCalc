// Wire-format contract tests for the OMV2 shareable build code.
//
// The format stores enum-ish fields as INDEXES into the engine data tables
// (stage/phase/grade row order, gem_bonus / pill_xp / fruit_xp key order,
// rarity_names) plus the const _stars/_vaseInputs lists — so those orders are
// part of the wire format. The pins below make any reorder fail loudly
// instead of silently remapping every previously shared code.
//
// The golden test pins DECODE of a fixed code (the durable contract: old
// codes must import correctly forever). Encode bytes are deliberately NOT
// pinned — zlib output may vary across `archive` versions; mutual
// compatibility is covered by the round-trip tests.
import 'dart:convert';
import 'dart:io';

import 'package:archive/archive.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:breakthrough_calc/engine.dart';
import 'package:breakthrough_calc/share_codec.dart';

Engine loadEngine() => Engine(jsonDecode(
        File('../data/breakthrough.json').readAsStringSync())
    as Map<String, dynamic>);

const goldenCode =
    'OMV2.eNo1UMtug0AM_BU011poWdhU9TmHXipVUU9FHAK7bFB4haU0UtV_r9akJ8_YY3vsH'
    'wSwIczgjODBmuAbsEq1ITQBnOssNYTzEpN5Rjh76VgD-JmwzmBFWL0MWC0401E_BfALYQhS'
    'tlbKywV8SBVhsWCtBTlwIeAONkapiOcFfCDMvUxTBG_BuVTsQ15bsIlgqKMxZQhDtJJmhM'
    'ELMIRN1m4BXBC26866PTTibNjZ0AW5fXZCZxcvj_H64Hew_nfn9tZ2EU3bgDOx0l5E3MeE'
    'JvQ3eUEfX1MQ3C5_B5clTlPtkqccZFJVUYkP11zG7vblQDo1VUU4gUu8TcvYjT45um8QPt'
    '2YvJ77HtXvH7erbBg=';

const goldenDecoded = {
  'stage': 'Incarnation',
  'phase': 'MIDDLE',
  'grade': 'G3',
  'grade_completion': 0.25,
  'culti_speed': 321.5,
  'absorption_ratio': 0.31,
  'aura_gem': 'Legendary',
  'target_stage': 'Wholeness',
  'target_phase': 'EARLY',
  'target_grade': 'G2',
  'timegate_days': 12.5,
  'top_stage': 'Nirvana',
  'mature_server': false,
  'dailies_done': true,
  'reset_in_hours': 6.0,
  'respira_per_day': 22.0,
  'respira_event': 4.0,
  'respira_exp': 5500.0,
  'pill_rank': '7R',
  'pill_limit': 12.0,
  'gold_per_day': 3.0,
  'purple_per_day': 4.0,
  'blue_per_day': 5.0,
  'mark_blue': 0.05,
  'mark_purple': 0.1,
  'mark_gold': 0.15,
  'vase': true,
  'vase_star': '4*',
  'vase_skin': true,
  'vase_input': 'Purple',
  'vase_charge': false,
  'mirror': true,
  'mirror_star': '2*',
  'mirror_skin': false,
  'mirror_charge': true,
  'pearl': true,
  'pearl_star': '3*',
  'pearl_skin': true,
  'pearl_xp_per_10': 2500.0,
  'pearl_charge': false,
  'fruit_rank': 'R8',
  'fruit_count': 15.0,
  'fruit_highest_rank': true,
  'lvl_culti': 12,
  'lvl_quality': 9,
  'lvl_gush': 14,
  'extractor_rarity': 'Epic',
  'pe_sources': [
    ['Robe +3', 5.0],
    ['Technique', 2.5],
  ],
  'respira_sources': ['Morning Dew', 'Zen Hall'],
};

void main() {
  final e = loadEngine();

  group('wire-format order pins (indexes ARE the format)', () {
    test('stage row order', () {
      expect(e.stages(), [
        'Novice', 'Connection', 'Foundation', 'Virtuoso', 'Nascent',
        'Incarnation', 'Voidbreak', 'Wholeness', 'Perfection', 'Nirvana',
        'Celestial', 'Eternal', 'Supreme',
      ]);
    });
    test('gem_bonus key order', () {
      expect((e.data['gem_bonus'] as Map).keys.toList(), [
        'None', 'Common', 'Uncommon', 'Rare', 'Epic', 'Legendary', 'Mythic',
      ]);
    });
    test('pill_xp key order', () {
      expect((e.data['pill_xp'] as Map).keys.toList(), [
        '1R', '2R', '3R', '4R', '5R', '6R', '7R', '8R', '9R', '10R', '11R',
        '12R',
      ]);
    });
    test('fruit_xp key order (R4/R5 gap is intentional)', () {
      expect((e.data['fruit_xp'] as Map).keys.toList(),
          ['R3', 'R6', 'R7', 'R8', 'R9', 'R10', 'R11', 'R12']);
    });
    test('rarity_names order', () {
      expect((e.data['rarity_names'] as List),
          ['Common', 'Uncommon', 'Rare', 'Epic', 'Legendary', 'Mythic']);
    });
  });

  group('golden vector', () {
    test('pinned OMV2 code decodes to pinned map', () {
      expect(decodeBuildCode(e, goldenCode), equals(goldenDecoded));
    });
    test('surrounding whitespace is tolerated', () {
      expect(decodeBuildCode(e, '  $goldenCode\n'), equals(goldenDecoded));
    });
  });

  group('round-trip', () {
    test('fully-populated inputs survive encode/decode', () {
      final inp = Inputs.fromMap(
          Map<String, dynamic>.from(goldenDecoded)..remove('pe_sources')
            ..remove('respira_sources'));
      final code = encodeBuildCode(
          e,
          inp,
          [
            ['Robe +3', 5.0],
            ['Technique', 2.5],
          ],
          {'Morning Dew', 'Zen Hall'});
      expect(decodeBuildCode(e, code), equals(goldenDecoded));
    });

    test('default inputs encode compactly and decode to defaults', () {
      final inp = Inputs.fromMap(<String, dynamic>{});
      final code = encodeBuildCode(e, inp, [], {});
      final out = decodeBuildCode(e, code)!;
      expect(out['stage'], e.stages().first);
      expect(out['culti_speed'], 0.0);
      expect(out['vase'], false);
      expect(out['pe_sources'], isEmpty);
      expect(out['respira_sources'], isEmpty);
      // Omitting defaults keeps codes short — sanity bound, not a byte pin.
      expect(code.length, lessThan(100));
    });
  });

  group('malformed input', () {
    test('returns null, never throws', () {
      expect(decodeBuildCode(e, ''), isNull);
      expect(decodeBuildCode(e, 'garbage'), isNull);
      expect(decodeBuildCode(e, 'OMV1.abcdef'), isNull);
      expect(decodeBuildCode(e, 'OMV2.'), isNull);
      expect(decodeBuildCode(e, 'OMV2.@@@not-base64@@@'), isNull);
      expect(decodeBuildCode(e, goldenCode.substring(0, 40)), isNull);
    });

    test('out-of-range enum indexes fall back to defaults', () {
      // Hand-build a compact map with absurd indexes; decode must not throw.
      final m = {'s': 999, 'ag': -7, 'pr': 999, 'vs': 42, 'er': 999};
      final bytes = const ZLibEncoder().encode(utf8.encode(jsonEncode(m)));
      final code = 'OMV2.${base64UrlEncode(bytes)}';
      final out = decodeBuildCode(e, code)!;
      expect(out['stage'], e.stages().first);
      expect(out['aura_gem'], 'None');
      expect(out['vase_star'], '0*');
    });
  });
}
