// Cross-reference integrity for the mobile Reference/Guide docs.
//
// Prose uses [[ref:slug#anchor|label]] / [[guide:slug#anchor|label]] markup
// (parsed by _docLinkRe in doc_nav.dart). A link is only live if its slug is
// a real page (refSlugs / guideSlugs) and, when it carries an #anchor, the
// target page registers anchorKey('tree:slug:anchor'). Nothing enforced that,
// so a renamed heading would silently dead-link. These tests read the two doc
// sources and assert every link target exists.
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

import 'package:breakthrough_calc/guide_tab.dart' show guideSlugs;
import 'package:breakthrough_calc/reference_tab.dart' show refSlugs;

/// Same shape as doc_nav.dart's _docLinkRe: [[tree:slug(#anchor)?|label]].
final _linkRe = RegExp(r'\[\[(ref|guide):([a-z]+)(?:#([a-z]+))?\|([^\]]+)\]\]');

/// Read a lib/ source regardless of the test runner's working directory
/// (flutter test runs from the package root, but stay robust either way).
String _readLib(String name) {
  for (final p in ['lib/$name', '../lib/$name', 'mobile/lib/$name']) {
    final f = File(p);
    if (f.existsSync()) return f.readAsStringSync();
  }
  throw StateError('cannot locate lib/$name from ${Directory.current.path}');
}

/// Drop pure comment lines so the format examples in doc-comments
/// (e.g. `/// ... [[ref:slug|...]] ...`) aren't mistaken for real links.
String _stripComments(String src) => src
    .split('\n')
    .where((l) => !l.trimLeft().startsWith('//'))
    .join('\n');

class _Link {
  _Link(this.tree, this.slug, this.anchor, this.origin);
  final String tree;
  final String slug;
  final String? anchor;
  final String origin; // which source file the link text lives in
  String get display =>
      '[[$tree:$slug${anchor == null ? '' : '#$anchor'}|...]] (in $origin)';
}

List<_Link> _linksIn(String src, String origin) => _linkRe
    .allMatches(_stripComments(src))
    .map((m) => _Link(m.group(1)!, m.group(2)!, m.group(3), origin))
    .toList();

void main() {
  final refSrc = _readLib('reference_tab.dart');
  final guideSrc = _readLib('guide_tab.dart');
  final sourceForTree = {'ref': refSrc, 'guide': guideSrc};

  final links = [
    ..._linksIn(refSrc, 'reference_tab.dart'),
    ..._linksIn(guideSrc, 'guide_tab.dart'),
  ];

  test('doc sources contain cross-reference links to check', () {
    expect(links, isNotEmpty);
  });

  test('every cross-link slug resolves to a real page', () {
    final slugsForTree = {'ref': refSlugs, 'guide': guideSlugs};
    for (final l in links) {
      expect(slugsForTree[l.tree]!.containsKey(l.slug), isTrue,
          reason: 'dead link ${l.display}: no "${l.slug}" page in ${l.tree} '
              '(have: ${slugsForTree[l.tree]!.keys.toList()})');
    }
  });

  test('every anchor-bearing link has a matching anchorKey in the target page',
      () {
    for (final l in links.where((l) => l.anchor != null)) {
      // Anchors register as anchorKey('tree:slug:anchor') in the target
      // tree's own source file.
      final id = '${l.tree}:${l.slug}:${l.anchor}';
      expect(sourceForTree[l.tree]!.contains("anchorKey('$id')"), isTrue,
          reason: 'dead link ${l.display}: no anchorKey(\'$id\') in '
              '${l.tree == 'ref' ? 'reference_tab.dart' : 'guide_tab.dart'}');
    }
  });

  test('guide pages register no anchors and no link targets a guide anchor',
      () {
    // guide_tab.dart has zero anchorKey calls today; pin that so a future
    // guide anchor typo (a link to a #anchor that was never registered) is
    // caught here instead of dead-linking in the app.
    expect(RegExp(r'anchorKey\(').hasMatch(guideSrc), isFalse,
        reason: 'guide_tab.dart gained anchorKey calls -- if guide links now '
            'use #anchors, wire the anchor check to guideSrc too');
    final guideAnchorLinks =
        links.where((l) => l.tree == 'guide' && l.anchor != null).toList();
    expect(guideAnchorLinks, isEmpty,
        reason: 'guide links target anchors that cannot exist (guide pages '
            'register none): ${guideAnchorLinks.map((l) => l.display).toList()}');
  });
}
