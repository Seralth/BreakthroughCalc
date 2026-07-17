// DocNavigator contract tests: registry-derived slug order (part of every
// persisted [[ref:...]] link's meaning), cross-tree link jumps, and the
// back stack.
import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:breakthrough_calc/doc_nav.dart';
import 'package:breakthrough_calc/engine.dart';
import 'package:breakthrough_calc/guide_tab.dart';
import 'package:breakthrough_calc/main.dart';
import 'package:breakthrough_calc/reference_tab.dart';

Engine loadEngine() => Engine(jsonDecode(
        File('../data/breakthrough.json').readAsStringSync())
    as Map<String, dynamic>);

void main() {
  test('slug maps preserve the pre-split order (link targets are durable)',
      () {
    expect(refSlugs, {
      'basics': 0, 'pills': 1, 'elixirs': 2, 'myrimon': 3, 'artifacts': 4,
      'combat': 5, 'affixes': 6, 'systems': 7, 'advanced': 8,
    });
    expect(guideSlugs, {
      'paths': 0, 'server': 1, 'routine': 2, 'novice': 3, 'virtuoso': 4,
      'nascent': 5, 'incarnation': 6, 'timegate': 7, 'voidbreak': 8,
      'pets': 9, 'aux': 10, 'techniques': 11, 'spending': 12,
    });
  });

  testWidgets('doc link jumps across trees and the back stack returns',
      (tester) async {
    SharedPreferences.setMockInitialValues({});
    final prefs = await SharedPreferences.getInstance();
    await tester.pumpWidget(
        BreakthroughApp(loadEngine(), const {}, prefs));
    await tester.pumpAndSettle();

    // Read the Guide first so the jump has a location to push.
    await tester.tap(find.text('Guide'));
    await tester.pumpAndSettle();
    expect(find.text('Choosing your path'), findsOneWidget);

    // Follow a [[ref:systems#spire|...]]-shaped link.
    DocNavigator.instance
        .openLink(DocLink(topTabReference, refSlugs['systems']!, 'ref:systems:spire'));
    await tester.pumpAndSettle();
    expect(find.text('Demon Spire'), findsOneWidget,
        reason: 'jump must land on Reference → World Systems');

    // The back arrow returns to where the reader was.
    await tester.tap(find.byIcon(Icons.arrow_back));
    await tester.pumpAndSettle();
    expect(find.text('Choosing your path'), findsOneWidget,
        reason: 'back must return to Guide → Choosing a Path');
    expect(find.byIcon(Icons.arrow_back), findsNothing,
        reason: 'back stack is empty again');
  });
}
