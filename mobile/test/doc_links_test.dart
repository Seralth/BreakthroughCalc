// Cross-reference link tests: [[tree:slug#section|label]] markup parsing and
// #section anchor scrolling (issue #14 v2).
import 'dart:convert';
import 'dart:io';

import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:breakthrough_calc/engine.dart';
import 'package:breakthrough_calc/reference.dart';

/// Fire the tap recognizer of the span whose text is [label].
void tapLink(WidgetTester tester, String label) {
  final rich = tester.widgetList<Text>(find.byType(Text)).firstWhere((t) =>
      t.textSpan != null && t.textSpan!.toPlainText().contains(label));
  TapGestureRecognizer? hit;
  rich.textSpan!.visitChildren((span) {
    if (span is TextSpan && span.text == label && span.recognizer != null) {
      hit = span.recognizer as TapGestureRecognizer;
      return false;
    }
    return true;
  });
  expect(hit, isNotNull, reason: 'no tappable span "$label"');
  hit!.onTap!();
}

void main() {
  setUp(() => docLinkRequest.value = null);

  testWidgets('markup without #section produces tab-only DocLink',
      (tester) async {
    await tester.pumpWidget(MaterialApp(
        home: Builder(
            builder: (c) => docText(c, 'see [[guide:spending|Spending]]'))));
    tapLink(tester, 'Spending');
    expect(docLinkRequest.value!.tab, 2);
    expect(docLinkRequest.value!.sub, guideSlugs['spending']);
    expect(docLinkRequest.value!.anchor, isNull);
  });

  testWidgets('markup with #section carries qualified anchor id',
      (tester) async {
    await tester.pumpWidget(MaterialApp(
        home: Builder(
            builder: (c) =>
                docText(c, 'see [[ref:systems#shops|the shop guide]]'))));
    tapLink(tester, 'the shop guide');
    expect(docLinkRequest.value!.tab, 1);
    expect(docLinkRequest.value!.sub, refSlugs['systems']);
    expect(docLinkRequest.value!.anchor, 'ref/systems#shops');
  });

  testWidgets('#section link scrolls the Systems page to its anchor',
      (tester) async {
    final data = jsonDecode(
            File('assets/data/breakthrough.json').readAsStringSync())
        as Map<String, dynamic>;
    await tester.pumpWidget(MaterialApp(
        home: Scaffold(
            body: ReferenceTab(engine: Engine(data), catalog: const []))));
    await tester.pumpAndSettle();

    docLinkRequest.value =
        DocLink(1, refSlugs['systems']!, 'ref/systems#shops');
    await tester.pumpAndSettle();

    final ctx = anchorKey('ref/systems#shops').currentContext;
    expect(ctx, isNotNull, reason: 'anchor header never built');
    final scrollable = Scrollable.of(ctx!);
    expect(scrollable.position.pixels, greaterThan(0),
        reason: 'page did not scroll toward the anchor');
    expect(docLinkRequest.value, isNull, reason: 'request not consumed');
  });
}
