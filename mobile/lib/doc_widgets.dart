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
      Table(
        border: TableBorder.all(color: t.dividerColor),
        defaultColumnWidth: const IntrinsicColumnWidth(),
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
      if (note != null) Padding(padding: const EdgeInsets.only(top: 4), child: Text(note, style: muted)),
    ]),
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
