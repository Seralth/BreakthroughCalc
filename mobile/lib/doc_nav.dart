/// Cross-reference navigation for the Reference/Guide documentation trees.
///
/// One [DocNavigator] singleton owns the reader's location, the pending
/// cross-link jump and the back stack (formerly five scattered top-level
/// mutable globals), plus the section-anchor registry and the [[...]] link
/// markup rendering. The consumption contract, in one place:
///  - a tapped [docText] link calls [DocNavigator.openLink], which pushes
///    the current location on the back stack and publishes [pendingLink];
///  - the main scaffold listens to [pendingLink] and switches the TOP tab;
///  - the target tab consumes the request via [DocNavigator.consumePendingFor]
///    (on its first build if its TabBarView page wasn't alive when the link
///    was tapped), animates its sub-tab and scrolls to the anchor.
library;

import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

import 'guide_tab.dart' show guideSlugs;
import 'reference_tab.dart' show refSlugs;

/// Top-level scaffold tab indices for the doc trees (the Vault is a
/// full-screen page off the Calculator, not a top tab).
const topTabReference = 1;
const topTabGuide = 2;

const _issuesUrl = 'https://github.com/Seralth/BreakthroughCalc/issues';

class DocLink {
  final int tab; // top-level tab index (see topTabReference/topTabGuide)
  final int sub; // sub-tab index within it
  final String? anchor; // anchor id (e.g. 'ref:elixirs:tolerance')
  const DocLink(this.tab, this.sub, [this.anchor]);
}

class DocNavigator {
  DocNavigator._();
  static final DocNavigator instance = DocNavigator._();

  /// Reader location, recorded by the tab listeners (main scaffold: topTab;
  /// Reference/Guide tab states: their sub tab).
  int topTab = 0;
  int refSub = 0;
  int guideSub = 0;

  /// Pending cross-reference jump. Set when a link is tapped; the main
  /// scaffold switches the top-level tab and the target tab consumes it.
  final ValueNotifier<DocLink?> pendingLink = ValueNotifier(null);

  /// Back-navigation for cross-reference jumps: tapping a link pushes the
  /// current location, the arrow next to the tab bar pops it.
  final ValueNotifier<List<DocLink>> backStack = ValueNotifier(const []);

  DocLink? _currentLocation() => topTab == topTabReference
      ? DocLink(topTabReference, refSub)
      : topTab == topTabGuide
          ? DocLink(topTabGuide, guideSub)
          : null;

  void openLink(DocLink target) {
    final here = _currentLocation();
    if (here != null) backStack.value = [...backStack.value, here];
    pendingLink.value = target;
  }

  void goBack() {
    final stack = backStack.value;
    if (stack.isEmpty) return;
    backStack.value = stack.sublist(0, stack.length - 1);
    pendingLink.value = stack.last;
  }

  /// The pending link if it targets top tab [tab] — consuming it — else null.
  DocLink? consumePendingFor(int tab) {
    final req = pendingLink.value;
    if (req == null || req.tab != tab) return null;
    pendingLink.value = null;
    return req;
  }
}

/// Section anchors for cross-links ([[ref:slug#anchor|...]]). Target
/// headings register a GlobalKey here; after a jump the tab handler
/// scrolls the section into view.
final Map<String, GlobalKey> anchorKeys = {};
GlobalKey anchorKey(String id) => anchorKeys.putIfAbsent(id, () => GlobalKey());

/// Scroll the anchor into view once its page has built (the TabBarView
/// page may not exist on the first frame after a cross-tree jump — retry
/// briefly until its context is mounted).
void scrollToDocAnchor(String id, [int tries = 12]) {
  final ctx = anchorKeys[id]?.currentContext;
  if (ctx != null) {
    Scrollable.ensureVisible(ctx,
        duration: const Duration(milliseconds: 250), alignment: 0.05);
  } else if (tries > 0) {
    Future.delayed(const Duration(milliseconds: 50),
        () => scrollToDocAnchor(id, tries - 1));
  }
}

/// Back arrow shown while the cross-reference back stack is non-empty.
Widget docBackButton() => ValueListenableBuilder<List<DocLink>>(
      valueListenable: DocNavigator.instance.backStack,
      builder: (_, stack, __) => stack.isEmpty
          ? const SizedBox.shrink()
          : IconButton(
              icon: const Icon(Icons.arrow_back),
              tooltip: 'Back to where you were reading',
              onPressed: DocNavigator.instance.goBack,
            ),
    );

final _docLinkRe =
    RegExp(r'\[\[(ref|guide):([a-z]+)(?:#([a-z]+))?\|([^\]]+)\]\]');

/// Paragraph text with [[...]] cross-reference markup rendered as tappable
/// links (styled like [issuesLink]). Plain text passes through untouched.
Widget docText(BuildContext context, String s) {
  if (!s.contains('[[')) return Text(s);
  final linkStyle = TextStyle(
      color: Theme.of(context).colorScheme.primary,
      decoration: TextDecoration.underline);
  final spans = <InlineSpan>[];
  var pos = 0;
  for (final m in _docLinkRe.allMatches(s)) {
    if (m.start > pos) spans.add(TextSpan(text: s.substring(pos, m.start)));
    final tree = m.group(1)!, slug = m.group(2)!;
    final anchor = m.group(3), label = m.group(4)!;
    final sub = tree == 'ref' ? refSlugs[slug] : guideSlugs[slug];
    spans.add(sub == null
        ? TextSpan(text: label)
        : TextSpan(
            text: label,
            style: linkStyle,
            recognizer: TapGestureRecognizer()
              ..onTap = () => DocNavigator.instance.openLink(DocLink(
                  tree == 'ref' ? topTabReference : topTabGuide,
                  sub,
                  anchor == null ? null : '$tree:$slug:$anchor'))));
    pos = m.end;
  }
  if (pos < s.length) spans.add(TextSpan(text: s.substring(pos)));
  return Text.rich(TextSpan(children: spans));
}

/// Tappable issues-page link used by the reference/guide footers.
Widget issuesLink(BuildContext context) => InkWell(
      onTap: () => launchUrl(Uri.parse(_issuesUrl),
          mode: LaunchMode.externalApplication),
      child: Text(_issuesUrl,
          style: TextStyle(
              color: Theme.of(context).colorScheme.primary,
              decoration: TextDecoration.underline)),
    );
