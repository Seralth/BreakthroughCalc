// Unit tests for the absorption diagnostics (extracted from the results
// widget so the game rules are testable without pumping widgets).
import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

import 'package:breakthrough_calc/absorption_diag.dart';
import 'package:breakthrough_calc/engine.dart';

Engine loadEngine() => Engine(jsonDecode(
        File('../data/breakthrough.json').readAsStringSync())
    as Map<String, dynamic>);

void main() {
  final e = loadEngine();

  Inputs at(String stage, {double absorption = 0.5}) {
    final inp = Inputs();
    inp.stage = stage;
    inp.phase = e.phasesFor(stage).first;
    inp.grade = e.gradesFor(stage, inp.phase).first;
    inp.absorptionRatio = absorption;
    return inp;
  }

  double baseLow(Inputs inp) =>
      ((e.rows[e.rowIndex(inp.stage, inp.phase, inp.grade)] as Map)['low']
              as num)
          .toDouble();

  test('pre-Nascent stages have no Strive -> no diagnostics', () {
    expect(diagnoseAbsorption(e, at('Foundation'), 0.5), isNull);
    expect(diagnoseAbsorption(e, at('Novice'), 0.0), isNull);
  });

  test('unknown row -> no diagnostics', () {
    final inp = at('Nascent');
    inp.grade = 'NOPE';
    expect(diagnoseAbsorption(e, inp, 0.5), isNull);
  });

  test('below base: absorption under the grade base flags belowBase', () {
    final inp = at('Nascent');
    final base = baseLow(inp);
    inp.absorptionRatio = base * 0.5;
    final strive = inp.absorptionRatio / base - 1; // negative
    final d = diagnoseAbsorption(e, inp, strive)!;
    expect(d.base, base);
    expect(d.belowBase, isTrue);
    expect(d.aboveCap, isFalse);
    expect(d.mortalWorld, isTrue);
    expect(d.overCap, isFalse);
  });

  test('above cap in the mortal world (Incarnation) -> overCap warning', () {
    final inp = at('Incarnation');
    final base = baseLow(inp);
    inp.absorptionRatio = base * 2.5; // implied strive 150% > 120% cap
    final d = diagnoseAbsorption(e, inp, 1.5)!;
    expect(d.belowBase, isFalse);
    expect(d.aboveCap, isTrue);
    expect(d.mortalWorld, isTrue);
    expect(d.overCap, isTrue);
  });

  test('above cap in a late realm (Voidbreak) -> legitimate overcap, no red',
      () {
    final inp = at('Voidbreak');
    final base = baseLow(inp);
    inp.absorptionRatio = base * 3.0;
    final d = diagnoseAbsorption(e, inp, 2.0)!;
    expect(d.aboveCap, isTrue);
    expect(d.mortalWorld, isFalse);
    expect(d.overCap, isFalse);
  });

  test('healthy mortal-world reading raises no flags', () {
    final inp = at('Nascent');
    final base = baseLow(inp);
    inp.absorptionRatio = base * 1.5; // strive 50%, under the cap
    final d = diagnoseAbsorption(e, inp, 0.5)!;
    expect(d.belowBase, isFalse);
    expect(d.aboveCap, isFalse);
    expect(d.overCap, isFalse);
  });
}
