// Parity check: run the shared scenarios through the Dart engine and compare
// against expected.json (produced by the Python engine). Run:
//   dart run test/parity.dart
import 'dart:convert';
import 'dart:io';

import '../lib/engine.dart';

const double tol = 1e-6;

void main() {
  final data = jsonDecode(File('assets/data/breakthrough.json').readAsStringSync())
      as Map<String, dynamic>;
  final scenarios = jsonDecode(File('test/scenarios.json').readAsStringSync()) as List;
  final expected = jsonDecode(File('test/expected.json').readAsStringSync()) as List;
  final engine = Engine(data);

  var failures = 0;
  for (var i = 0; i < scenarios.length; i++) {
    final r = engine.calculate(Inputs.fromMap(scenarios[i] as Map<String, dynamic>));
    final exp = expected[i] as Map<String, dynamic>;
    final got = <String, dynamic>{
      'valid': r.valid,
      'error': r.error,
      'phase_days': r.phaseDays,
      'stage_days': r.stageDays,
      'target_days': r.targetDays,
      'target_valid': r.targetValid,
      'abode_aura': r.abodeAura,
      'strive': r.strive,
      'base_xp_per_day': r.baseXpPerDay,
      'effective_xp_per_day': r.effectiveXpPerDay,
      'pill_xp_per_day': r.pillXpPerDay,
      'pill_speedup': r.pillSpeedup,
      'gem_speedup': r.gemSpeedup,
      'mythic_pills_per_day': r.mythicPillsPerDay,
      'pearl_xp_per_day': r.pearlXpPerDay,
      'respira_xp_per_day': r.respiraXpPerDay,
      'fruit_xp': r.fruitXp,
      'fruit_days_saved': r.fruitDaysSaved,
      'phase_band': r.phaseBand,
      'stage_band': r.stageBand,
      'target_band': r.targetBand,
    };
    final diffs = <String>[];
    exp.forEach((k, ev) {
      final gv = got[k];
      if (ev is bool || ev is String) {
        if (ev != gv) diffs.add('$k: py=$ev dart=$gv');
      } else if (ev is List) {
        for (var j = 0; j < ev.length; j++) {
          if (!_close((ev[j] as num).toDouble(), (gv[j] as num).toDouble())) {
            diffs.add('$k[$j]: py=${ev[j]} dart=${gv[j]}');
          }
        }
      } else if (ev is num) {
        if (!_close(ev.toDouble(), (gv as num).toDouble())) {
          diffs.add('$k: py=$ev dart=$gv');
        }
      }
    });
    if (diffs.isEmpty) {
      print('scenario $i: OK');
    } else {
      failures++;
      print('scenario $i: MISMATCH');
      for (final d in diffs) {
        print('    $d');
      }
    }
  }
  if (failures == 0) {
    print('\nALL ${scenarios.length} SCENARIOS MATCH');
  } else {
    print('\n$failures scenario(s) FAILED');
    exitCode = 1;
  }
}

bool _close(double a, double b) {
  final diff = (a - b).abs();
  return diff <= tol || diff <= tol * a.abs().clamp(1, double.infinity);
}
