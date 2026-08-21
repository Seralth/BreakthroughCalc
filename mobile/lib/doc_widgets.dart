/// Shared building blocks for the Reference/Guide documentation pages:
/// paragraph with cross-link markup, data table, and the scrollable page
/// wrapper with the report-an-error footer.
library;

import 'package:flutter/material.dart';

import 'doc_nav.dart';

Widget docPara(BuildContext context, String s) => Padding(
    padding: const EdgeInsets.symmetric(vertical: 6),
    child: docText(context, s));

Widget docTable(BuildContext context, String title, List<String> headers,
    List<List<String>> rows,
    [String? note]) {
  final t = Theme.of(context);
  final h3 = t.textTheme.titleMedium;
  final muted = TextStyle(color: t.hintColor, fontSize: 12);
  return Padding(
    padding: const EdgeInsets.symmetric(vertical: 8),
    child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Text(title, style: h3),
      const SizedBox(height: 6),
      // FlexColumnWidth (not IntrinsicColumnWidth) so columns always share
      // the page's actual bounded width and long cell text wraps inside its
      // column, instead of the column sizing to the text's unwrapped width
      // and the table overflowing the page.
      Table(
        border: TableBorder.all(color: t.dividerColor),
        defaultColumnWidth: const FlexColumnWidth(),
        children: [
          TableRow(
            decoration: BoxDecoration(color: t.colorScheme.surfaceContainerHighest),
            children: [
              for (final h in headers)
                Padding(padding: const EdgeInsets.all(6),
                    child: Text(h, style: const TextStyle(fontWeight: FontWeight.bold))),
            ],
          ),
          for (final r in rows)
            TableRow(children: [
              for (final c in r) Padding(padding: const EdgeInsets.all(6), child: Text(c)),
            ]),
        ],
      ),
      if (note != null) Padding(padding: const EdgeInsets.only(top: 4),
          child: DefaultTextStyle.merge(style: muted, child: docText(context, note))),
    ]),
  );
}

/// A bulleted list where wrapped lines hang-indent under the bullet glyph
/// (unlike a plain Text with literal '• ' characters, which doesn't). Each
/// item is run through [docText] so bold/cross-link markup works inside
/// bullets too.
Widget docBullets(BuildContext context, List<String> items, {String? note}) {
  final muted = TextStyle(color: Theme.of(context).hintColor, fontSize: 12);
  return Padding(
    padding: const EdgeInsets.symmetric(vertical: 6),
    child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      for (final item in items)
        Padding(
          padding: const EdgeInsets.only(bottom: 4),
          child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
            const SizedBox(width: 20, child: Text('•')),
            Expanded(child: docText(context, item)),
          ]),
        ),
      if (note != null) Padding(padding: const EdgeInsets.only(top: 2), child: Text(note, style: muted)),
    ]),
  );
}

/// A cautionary note, matching desktop's colored "Advisory" lead-in
/// (`docs.py`'s `<b style='color:{bad}'>Advisory</b>`) — for content that's a
/// warning/gotcha rather than routine guidance (use a plain **bold** lead-in
/// via [docPara]/[docText] for routine "Practical read:"-style notes).
Widget docAdvisory(BuildContext context, String text) {
  final warn = Theme.of(context).colorScheme.error;
  return Padding(
    padding: const EdgeInsets.symmetric(vertical: 6),
    child: Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        border: Border(left: BorderSide(color: warn, width: 3)),
        color: warn.withValues(alpha: 0.08),
      ),
      child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text('Advisory  ', style: TextStyle(color: warn, fontWeight: FontWeight.bold)),
        Expanded(child: docText(context, text)),
      ]),
    ),
  );
}

Widget _docFooter(BuildContext context, String text) => Padding(
      padding: const EdgeInsets.only(top: 16, bottom: 8),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        const Divider(),
        Text(text,
            style:
                TextStyle(color: Theme.of(context).hintColor, fontSize: 12)),
        issuesLink(context),
      ]),
    );

/// A documentation page: children plus the report-an-error footer
/// ([footerText] carries each tree's wording).
// SingleChildScrollView (not ListView) so every section is mounted and
// scrollToDocAnchor/ensureVisible can reach anchors below the fold.
Widget docPage(BuildContext context, List<Widget> children,
        {required String footerText,
        EdgeInsets padding = const EdgeInsets.all(12)}) =>
    SingleChildScrollView(
        padding: padding,
        child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [...children, _docFooter(context, footerText)]));
