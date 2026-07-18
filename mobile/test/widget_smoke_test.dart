// Pre-refactor safety net: whole-app widget smoke test plus a pin on the
// persisted-inputs schema ('inputs_v1' prefs blob key set).
//
// The schema pin is the contract that protects saved user state through the
// main.dart split: whatever produces the blob, the key set must stay exactly
// this list (values are covered by the engine round-trip and codec tests).
import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:breakthrough_calc/engine.dart';
import 'package:breakthrough_calc/main.dart';
import 'package:breakthrough_calc/share_codec.dart';
import 'package:breakthrough_calc/shelf.dart';

Engine loadEngine() => Engine(jsonDecode(
        File('../data/breakthrough.json').readAsStringSync())
    as Map<String, dynamic>);

/// The exact key set of the persisted 'inputs_v1' blob (and of build-code
/// decode output). Adding an input is allowed (append here); removing or
/// renaming a key silently drops user state and must fail loudly.
const inputsV1Keys = [
  'stage',
  'phase',
  'grade',
  'grade_completion',
  'culti_speed',
  'absorption_ratio',
  'aura_gem',
  'target_stage',
  'target_phase',
  'target_grade',
  'timegate_days',
  'top_stage',
  'mature_server',
  'dailies_done',
  'reset_in_hours',
  'respira_per_day',
  'respira_event',
  'respira_exp',
  'pill_rank',
  'pill_effect',
  'pill_limit',
  'gold_per_day',
  'purple_per_day',
  'blue_per_day',
  'mark_blue',
  'mark_purple',
  'mark_gold',
  'vase',
  'vase_star',
  'vase_skin',
  'vase_input',
  'mirror',
  'mirror_star',
  'mirror_skin',
  'pearl',
  'pearl_star',
  'pearl_skin',
  'pearl_xp_per_10',
  'vase_charge',
  'mirror_charge',
  'pearl_charge',
  'fruit_rank',
  'fruit_count',
  'fruit_highest_rank',
  'lvl_culti',
  'lvl_quality',
  'lvl_gush',
  'extractor_rarity',
  'bless_pp',
  'bless_window_pp',
  'elixir_per_day',
  'elixir_exp',
  'elixir_effect',
  'pe_sources',
  'respira_sources',
];

void main() {
  final engine = loadEngine();
  final shelfCatalog = jsonDecode(File('../data/sources.json')
      .readAsStringSync()) as Map<String, dynamic>;

  Future<SharedPreferences> mockPrefs(
      [Map<String, Object> initial = const {}]) {
    // The one-time Obtainium notice is a modal dialog at startup; without
    // this flag it sits over the app and blocks every finder below it.
    SharedPreferences.setMockInitialValues(
        {'obtainium_notice_shown': true, ...initial});
    return SharedPreferences.getInstance();
  }

  testWidgets('donation nag fires on the 10th launch; Never sticks',
      (tester) async {
    SharedPreferences.setMockInitialValues(
        {'obtainium_notice_shown': true, 'launch_count': 9});
    final prefs = await SharedPreferences.getInstance();
    await tester.pumpWidget(BreakthroughApp(engine, shelfCatalog, prefs));
    await tester.pumpAndSettle();

    expect(find.text('Enjoying the calculator?'), findsOneWidget);
    expect(prefs.getInt('launch_count'), 10);

    await tester.tap(find.text("Don't ask again"));
    await tester.pumpAndSettle();
    expect(find.text('Enjoying the calculator?'), findsNothing);
    expect(prefs.getString('donate_nag'), 'never');
  });

  testWidgets('Obtainium notice shows once, sets its flag, and closes',
      (tester) async {
    SharedPreferences.setMockInitialValues({});
    final prefs = await SharedPreferences.getInstance();
    await tester.pumpWidget(BreakthroughApp(engine, shelfCatalog, prefs));
    await tester.pumpAndSettle();

    expect(find.text('Automatic updates'), findsOneWidget);
    expect(prefs.getBool('obtainium_notice_shown'), isTrue);

    await tester.tap(find.text('Close'));
    await tester.pumpAndSettle();
    expect(find.text('Automatic updates'), findsNothing);
  });

  testWidgets('calc tab renders, computes, and top tabs switch',
      (tester) async {
    // Tall surface so the (lazily built) form ListView materializes the
    // fields the test drives without scrolling choreography.
    tester.view.physicalSize = const Size(900, 8000);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.reset);

    final prefs = await mockPrefs();
    await tester.pumpWidget(
        BreakthroughApp(engine, shelfCatalog, prefs));
    await tester.pumpAndSettle();

    // Calc tab is up; with speed/absorption at 0 the results card shows the
    // engine's validation error.
    expect(find.text('Cultivation Base'), findsOneWidget);
    expect(find.text('Cultivation speed and absorption ratio must be > 0.'),
        findsOneWidget);

    // Enter absorption + cultivation speed -> a results row appears.
    await tester.enterText(
        find.widgetWithText(TextField, 'Absorption Ratio (%)'), '31');
    await tester.enterText(
        find.widgetWithText(TextField, 'Cultivation Speed'), '300');
    await tester.pumpAndSettle();
    expect(find.text('Half-step breakthrough in'), findsOneWidget);
    // Implied abode aura = 300 / 0.31 (results rows render as RichText).
    expect(find.text('967.7', findRichText: true), findsOneWidget);

    // Reference and Guide tabs build, then back to the calculator.
    await tester.tap(find.text('Reference'));
    await tester.pumpAndSettle();
    expect(find.text('How cultivation works'), findsOneWidget);

    await tester.tap(find.text('Guide'));
    await tester.pumpAndSettle();
    expect(find.text('Choosing your path'), findsOneWidget);

    await tester.tap(find.text('Calculator'));
    await tester.pumpAndSettle();
    expect(find.text('Cultivation Base'), findsOneWidget);
  });

  testWidgets('vault card opens the Vault; Max shelf fills a rank',
      (tester) async {
    tester.view.physicalSize = const Size(900, 8000);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.reset);

    final prefs = await mockPrefs();
    await tester.pumpWidget(
        BreakthroughApp(engine, shelfCatalog, prefs));
    await tester.pumpAndSettle();

    await tester.tap(find.widgetWithText(Card, 'Vault'));
    await tester.pumpAndSettle();
    expect(find.text('Library'), findsOneWidget);
    expect(find.text('Treasury'), findsOneWidget);
    expect(find.text('Longevity'), findsOneWidget);

    // "Max shelf" on R1 sets Longevity to its final tier (tier book like
    // the rest of the Library).
    await tester.tap(find.text('Max shelf').first);
    await tester.pumpAndSettle();
    final vaultBlob = prefs.getString('shelf_v1')!;
    expect(vaultBlob, contains('"longevity":2'));

    // The Exclusive shelf lists the exclusive manuals; maxing it records
    // them at tier 6.
    await tester.tap(find.text('Exclusive'));
    await tester.pumpAndSettle();
    expect(find.text('Heavenly Scripture'), findsOneWidget);
    await tester.tap(find.text('Max shelf').last);
    await tester.pumpAndSettle();
    expect(prefs.getString('shelf_v1')!,
        contains('"heavenly_scripture":6'));
    await tester.tap(find.text('Universal'));
    await tester.pumpAndSettle();

    // Back to the calculator; the summary card reflects the contribution.
    await tester.pageBack();
    await tester.pumpAndSettle();
    expect(find.textContaining('attempts'), findsWidgets);
  });

  testWidgets('importing a code that carries the Vault adopts it',
      (tester) async {
    // Sender: owns lifeboom + full Virya, 16 Respira/day, and a code whose
    // synthetic Vault row carries a deliberately wrong value — the
    // receiver must regenerate that row from the adopted ownership, never
    // trust (or double-count) the flattened copy.
    const owned = <String, dynamic>{'ascension_virya': 3, 'lifeboom': 3};
    final senderInp = Inputs.fromMap(<String, dynamic>{});
    senderInp.stage = engine.stages().first;
    senderInp.respiraPerDay = 16.0;
    senderInp.pillLimit = 9.0;
    final code = encodeBuildCode(
        engine,
        senderInp,
        [
          ['Vault (books & curios)', 999.0],
          ['Event buff', 2.0],
        ],
        {},
        shelfOwned: owned);

    // Receiver starts with a DIFFERENT vault; import must replace it.
    final prefs = await mockPrefs({
      'shelf_v1': jsonEncode({
        'owned': {'longevity': 1},
        'bases': {'respira_attempts': 10.0, 'pill_attempts': 0.0},
        'auto': true,
      }),
    });
    await tester.pumpWidget(BreakthroughApp(engine, shelfCatalog, prefs));
    await tester.pumpAndSettle();

    await tester.tap(find.byIcon(Icons.ios_share));
    await tester.pumpAndSettle();
    await tester.enterText(
        find.descendant(
            of: find.byType(AlertDialog), matching: find.byType(TextField)),
        code);
    await tester.tap(find.text('Import'));
    await tester.pumpAndSettle();
    expect(find.text('Build imported'), findsOneWidget);

    final vault =
        jsonDecode(prefs.getString('shelf_v1')!) as Map<String, dynamic>;
    expect(vault['owned'], equals(owned));

    final d = derive(shelfCatalog, {'owned': owned});
    final peTotal = d['pill_effect']?.total ?? 0.0;
    expect(peTotal, greaterThan(0));
    final attempts = d['respira_attempts']?.total ?? 0.0;
    expect((vault['bases'] as Map)['respira_attempts'], 16.0 - attempts);

    final blob =
        jsonDecode(prefs.getString('inputs_v1')!) as Map<String, dynamic>;
    final peRows = (blob['pe_sources'] as List)
        .where((r) => (r as List)[0] == 'Vault (books & curios)')
        .toList();
    expect(peRows, hasLength(1),
        reason: 'exactly one synthetic Vault row after import');
    expect((peRows.single as List)[1], peTotal,
        reason: 'row value must be locally derived, not the sender copy');
    expect(blob['respira_per_day'], 16.0,
        reason: 're-anchored bases must reproduce the imported value');
    expect((blob['pe_sources'] as List).any(
            (r) => (r as List)[0] == 'Event buff'),
        isTrue);
  });

  testWidgets('persisted inputs blob pins the exact key set', (tester) async {
    final prefs = await mockPrefs();
    await tester.pumpWidget(
        BreakthroughApp(engine, shelfCatalog, prefs));
    await tester.pumpAndSettle();

    // initState recalculates and saves once, so the blob exists already.
    final raw = prefs.getString('inputs_v1');
    expect(raw, isNotNull, reason: 'app must persist inputs on first calc');
    final blob = jsonDecode(raw!) as Map<String, dynamic>;
    expect(blob.keys.toSet(), inputsV1Keys.toSet(),
        reason: 'inputs_v1 key set changed — saved user state would be '
            'dropped or misread');
    expect(inputsV1Keys.length, inputsV1Keys.toSet().length,
        reason: 'pin list has duplicates');
  });
}
