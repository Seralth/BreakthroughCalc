// Regression tests for the form-refresh bug: initialValue-driven, unkeyed
// form fields kept stale State when inputs were bulk-replaced (build-code
// import) or when a pill-effect row was deleted. Both failure modes were
// first reproduced with inverted assertions against the unfixed code; the
// fix is _formGeneration keying the form ListView plus stable per-row
// ValueKeys on the pill-effect editor rows.
import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:breakthrough_calc/engine.dart';
import 'package:breakthrough_calc/main.dart';
import 'package:breakthrough_calc/share_codec.dart';

Engine loadEngine() => Engine(jsonDecode(
        File('../data/breakthrough.json').readAsStringSync())
    as Map<String, dynamic>);

/// The text currently DISPLAYED by the [index]-th TextFormField labeled
/// [label] (which, for an unkeyed initialValue field, can differ from the
/// data).
String fieldText(WidgetTester tester, String label, {int index = 0}) {
  final editable = find.descendant(
      of: find.widgetWithText(TextFormField, label).at(index),
      matching: find.byType(EditableText));
  return tester.widget<EditableText>(editable).controller.text;
}

void main() {
  final engine = loadEngine();

  Future<SharedPreferences> mockPrefs(
      [Map<String, Object> initial = const {}]) {
    // Suppress the one-time Obtainium startup dialog (modal, blocks finders).
    SharedPreferences.setMockInitialValues(
        {'obtainium_notice_shown': true, ...initial});
    return SharedPreferences.getInstance();
  }

  Future<void> pumpApp(WidgetTester tester, SharedPreferences prefs) async {
    tester.view.physicalSize = const Size(900, 8000);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.reset);
    await tester.pumpWidget(BreakthroughApp(engine, const {}, prefs));
    await tester.pumpAndSettle();
  }

  testWidgets('importing a build code refreshes initialValue-driven fields',
      (tester) async {
    final prefs = await mockPrefs();
    await pumpApp(tester, prefs);

    // User types 50% grade progress.
    await tester.enterText(
        find.widgetWithText(TextFormField, 'Grade progress (%)'), '50');
    await tester.pumpAndSettle();
    expect(fieldText(tester, 'Grade progress (%)'), '50');

    // Import a build whose grade progress is 25% (plus a valid speed so
    // results compute).
    final code = encodeBuildCode(
        engine,
        Inputs.fromMap(const {
          'grade_completion': 0.25,
          'culti_speed': 300.0,
          'absorption_ratio': 0.31,
        }),
        [],
        {});
    await tester.tap(find.byIcon(Icons.ios_share));
    await tester.pumpAndSettle();
    await tester.enterText(
        find.widgetWithText(TextField, 'Paste a build code to import'), code);
    await tester.tap(find.text('Import'));
    await tester.pumpAndSettle();

    // Results are computed from the imported inputs...
    expect(find.text('967.7', findRichText: true), findsOneWidget);
    // ...and the form fields remount and display them too.
    expect(fieldText(tester, 'Grade progress (%)'), '25',
        reason: 'import must refresh initialValue-driven fields');
  });

  testWidgets('deleting pill-effect row 0 of 2 refreshes the surviving row',
      (tester) async {
    final prefs = await mockPrefs({
      'inputs_v1': jsonEncode({
        'pe_sources': [
          ['Alpha', 5.0],
          ['Beta', 10.0],
        ],
      }),
    });
    await pumpApp(tester, prefs);

    expect(fieldText(tester, 'Pill-effect source', index: 0), 'Alpha');
    expect(fieldText(tester, 'Pill-effect source', index: 1), 'Beta');

    // Delete row 0 ('Alpha', 5%).
    await tester.tap(find.byIcon(Icons.close).first);
    await tester.pumpAndSettle();

    // The data holds only Beta/10 — the total proves it...
    expect(find.textContaining('Pill effect total'), findsOneWidget);
    expect(find.textContaining('10.00%'), findsOneWidget);
    // ...and the surviving row displays its own entry, not the deleted one's.
    expect(fieldText(tester, 'Pill-effect source'), 'Beta',
        reason: 'survivor must show its own name');
    expect(fieldText(tester, '%'), '10',
        reason: 'survivor must show its own percent');
  });
}
