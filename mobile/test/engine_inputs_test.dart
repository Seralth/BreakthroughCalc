// Inputs.toMap()/fromMap() schema tests plus the pill row-layout pin.
import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

import 'package:breakthrough_calc/engine.dart';

void main() {
  group('Inputs.toMap round-trip', () {
    test('fully-populated instance survives fromMap(toMap())', () {
      // Every field set to a non-default value so a dropped or misspelled
      // key cannot hide behind a matching default.
      final inp = Inputs(
        stage: 'Incarnation',
        phase: 'MIDDLE',
        grade: 'G3',
        gradeCompletion: 0.25,
        cultiSpeed: 321.5,
        absorptionRatio: 0.31,
        auraGem: 'Legendary',
        targetStage: 'Wholeness',
        targetPhase: 'EARLY',
        targetGrade: 'G2',
        timegateDays: 12.5,
        topStage: 'Nirvana',
        matureServer: false,
        dailiesDone: true,
        resetInHours: 6.0,
        respiraPerDay: 22.0,
        respiraEvent: 4.0,
        respiraExp: 5500.0,
        pillRank: '7R',
        pillEffect: 0.075,
        pillLimit: 12.0,
        goldPerDay: 3.0,
        purplePerDay: 4.0,
        bluePerDay: 5.0,
        markBlue: 0.05,
        markPurple: 0.1,
        markGold: 0.15,
        vase: true,
        vaseStar: '4*',
        vaseSkin: true,
        vaseInput: 'Purple',
        mirror: true,
        mirrorStar: '2*',
        mirrorSkin: true,
        pearl: true,
        pearlStar: '3*',
        pearlSkin: true,
        pearlXpPer10: 2500.0,
        vaseCharge: false,
        mirrorCharge: false,
        pearlCharge: false,
        fruitRank: 'R8',
        fruitCount: 15.0,
        fruitHighestRank: true,
        lvlCulti: 12,
        lvlQuality: 9,
        lvlGush: 14,
        extractorRarity: 'Epic',
        blessPp: 0.15,
        blessWindowPp: 0.2,
        elixirPerDay: 12.0,
        elixirExp: 4000.0,
        elixirEffect: 0.75,
      );
      final m = inp.toMap();
      expect(Inputs.fromMap(m).toMap(), equals(m));
      // No value may still equal its Inputs() default, or the round-trip
      // could not detect a lost key for that field.
      final defaults = Inputs().toMap();
      m.forEach((k, v) {
        expect(v, isNot(equals(defaults[k])),
            reason: '$k is at its default; pick a distinct test value');
      });
    });

    test('defaults survive fromMap of an empty map', () {
      expect(Inputs.fromMap(const {}).toMap(), equals(Inputs().toMap()));
    });
  });

  group('pill row layout consts', () {
    test('match data/breakthrough.json ordering [gold, purple, blue, mythic]',
        () {
      final data = jsonDecode(
              File('../data/breakthrough.json').readAsStringSync())
          as Map<String, dynamic>;
      final pillXp = data['pill_xp'] as Map<String, dynamic>;
      // Layout invariant for every rank: mythic > gold > purple > blue.
      for (final e in pillXp.entries) {
        final row = (e.value as List).cast<num>();
        expect(row.length, 4, reason: '${e.key} row length');
        expect(row[pillMythic], greaterThan(row[pillGold]),
            reason: '${e.key}: mythic must be the largest payout');
        expect(row[pillGold], greaterThan(row[pillPurple]),
            reason: '${e.key}: gold > purple');
        expect(row[pillPurple], greaterThan(row[pillBlue]),
            reason: '${e.key}: purple > blue');
      }
      // Anchor one verified row outright (in-game tooltips, 2026-07-07).
      expect(pillXp['1R'], [1500, 750, 400, 3000]);
    });
  });
}
