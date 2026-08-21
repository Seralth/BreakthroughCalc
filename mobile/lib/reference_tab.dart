/// Read-only reference tables + primer, rendered from the same engine data so
/// the numbers can't drift from the calculations. Organized as scrollable
/// sub-tabs: mechanics first, then a stage-by-stage progression walkthrough.
///
/// One ordered [refSections] registry drives the slug->index map, the
/// TabController length, the Tab labels and the TabBarView children, so a
/// section can only be added or moved in one place.
library;

import 'package:flutter/material.dart';

import 'catalog.dart';
import 'doc_nav.dart';
import 'doc_widgets.dart';
import 'engine.dart';
import 'form_widgets.dart';

typedef RefPageBuilder = Widget Function(
    BuildContext context, Engine engine, Map<String, dynamic> catalog);

/// [[source name, bonus summary], ...] for every Vault entry with an
/// effect aimed at one of [wanted]'s target ids ({target: unit suffix}).
/// Twin of docs.py _vault_bonus_rows — renders from the Vault's catalog.
/// [[curio name, cultivation effect summary], ...] for cultivation-helping
/// curios. Twin of docs._curio_bonus_rows. Sorted by name.
List<List<String>> curioBonusRows(Map<String, dynamic> shelfCatalog) {
  const cult = {
    'pill_effect', 'pill_attempts', 'respira_attempts', 'respira_effect'
  };
  final rows = <List<String>>[];
  for (final sRaw in (shelfCatalog['sources'] ?? []) as List) {
    final s = sRaw as Map;
    if (s['category'] != 'curio') continue;
    final parts = <String>[];
    for (final eRaw in (s['effects'] ?? []) as List) {
      final e = eRaw as Map;
      final tid = e['target'] as String?;
      final note = (e['note'] as String?) ?? '';
      if (tid == 'info') {
        if (note.contains('Abode Aura') ||
            note.contains('Aura Gem') ||
            note.contains('Respira') ||
            note.contains('Auxiliary')) {
          parts.add(note.split(' (inside')[0].replaceAll(RegExp(r'\.$'), ''));
        }
        continue;
      }
      if (!cult.contains(tid)) continue;
      if (e.containsKey('value_model')) {
        final (lo, hi) = modelRange(e['value_model'] as Map);
        parts.add('Cultivation Pill Effect +$lo% to '
            '+$hi% by star and upgrade');
      } else if (e['value'] != null) {
        parts.add(note.isEmpty
            ? '+${fmtNum((e['value'] as num).toDouble())}'
            : note.replaceAll(RegExp(r'\.$'), ''));
      }
    }
    if (parts.isNotEmpty) {
      rows.add([s['name'] as String, {for (final p in parts) p: 1}.keys.join('; ')]);
    }
  }
  rows.sort((a, b) => a[0].compareTo(b[0]));
  return rows;
}

List<List<String>> vaultBonusRows(
    Map<String, dynamic> shelfCatalog, Map<String, String> wanted) {
  final rows = <List<String>>[];
  for (final sRaw in (shelfCatalog['sources'] ?? []) as List) {
    final s = sRaw as Map;
    final parts = <String>[];
    for (final eRaw in (s['effects'] ?? []) as List) {
      final e = eRaw as Map;
      final tid = e['target'] as String?;
      if (tid == null || !wanted.containsKey(tid)) continue;
      if (e.containsKey('value_model')) {
        final (lo, hi) = modelRange(e['value_model'] as Map);
        parts.add('$lo–$hi'
            '${wanted[tid]} by star/upgrade');
        continue;
      }
      final v = e['value'] as num?;
      if (v == null) continue;
      var part = '+${fmtNum(v.toDouble())}${wanted[tid]}';
      final ml = e['min_level'];
      if (ml is int && ml > 1) {
        final kind = (s['levels'] as Map)['kind'];
        part += kind == 'tier' ? ' (Tier $ml)' : ' (level $ml)';
      } else if (ml == 'max') {
        part += ' (max level)';
      }
      parts.add(part);
    }
    if (parts.isNotEmpty) {
      var name = s['name'] as String;
      if (s['rank'] != null) name += ' (${s['rank']} book)';
      rows.add([name, parts.join(', ')]);
    }
  }
  return rows;
}

class RefSection {
  final String slug;
  final String title;
  final RefPageBuilder page;
  const RefSection(this.slug, this.title, this.page);
}

const List<RefSection> refSections = [
  RefSection('basics', 'Basics', _basicsPage),
  RefSection('pills', 'Pills & Respira', _pillsPage),
  RefSection('elixirs', 'Elixirs & Stat Pills', _elixirsPage),
  RefSection('myrimon', 'Myrimon & Extractor', _myrimonPage),
  RefSection('curios', 'Curios', _curiosPage),
  RefSection('artifacts', 'Artifacts & Gems', _artifactsPage),
  RefSection('combat', 'Combat & Gear', _combatPage),
  RefSection('affixes', 'Affixes', _affixesPage),
  RefSection('systems', 'World Systems', _systemsPage),
  RefSection('cultivation-internals', 'Cultivation Internals', _cultivationInternalsPage),
  RefSection('combat-internals', 'Combat Internals', _combatInternalsPage),
];

/// Slug -> sub-tab index for [[ref:slug|...]] links (derived from
/// [refSections]; registry order IS the tab order).
final Map<String, int> refSlugs = {
  for (var i = 0; i < refSections.length; i++) refSections[i].slug: i
};

const _refFooterText =
    'Spotted an error, or have data for a "?" in a table (a '
    'screenshot of a tier you\'ve crossed, an endgame number)? '
    'Single data points regularly fill real gaps — please '
    'report it at:';

class ReferenceTab extends StatefulWidget {
  final Engine engine;
  final Map<String, dynamic> catalog; // the Vault (shelf) catalog
  const ReferenceTab({super.key, required this.engine, required this.catalog});

  @override
  State<ReferenceTab> createState() => _ReferenceTabState();
}

class _ReferenceTabState extends State<ReferenceTab>
    with SingleTickerProviderStateMixin {
  late final TabController _tabs =
      TabController(length: refSections.length, vsync: this);
  final _nav = DocNavigator.instance;

  @override
  void initState() {
    super.initState();
    _tabs.addListener(() => _nav.refSub = _tabs.index);
    _nav.pendingLink.addListener(_onDocLink);
    WidgetsBinding.instance.addPostFrameCallback((_) => _onDocLink());
  }

  void _onDocLink() {
    if (!mounted) return;
    final req = _nav.consumePendingFor(topTabReference);
    if (req == null) return;
    _tabs.animateTo(req.sub);
    if (req.anchor != null) scrollToDocAnchor(req.anchor!);
  }

  @override
  void dispose() {
    _nav.pendingLink.removeListener(_onDocLink);
    _tabs.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Column(children: [
      Row(children: [
        docBackButton(),
        Expanded(
            child: TabBar(
          controller: _tabs,
          isScrollable: true,
          tabAlignment: TabAlignment.start,
          tabs: [for (final s in refSections) Tab(text: s.title)],
        )),
      ]),
      Expanded(
        child: TabBarView(controller: _tabs, children: [
          for (final s in refSections)
            s.page(context, widget.engine, widget.catalog),
        ]),
      ),
    ]);
  }
}


Widget _basicsPage(BuildContext context, Engine engine, Map<String, dynamic> catalog) {
  final h3 = Theme.of(context).textTheme.titleMedium;
  Widget para(String s) => docPara(context, s);
  Widget bullets(List<String> items, [String? note]) => docBullets(context, items, note: note);
  return docPage(context, [
    Text('How cultivation works',
        key: anchorKey('ref:basics:cultivation'), style: h3),
    para('Cultivation EXP accrues one tick every 8 seconds (a "Cosmoapsis"). '
        'Cultivation Speed = Abode Aura × Absorption Ratio — all read from the '
        'in-game Cultivation Bonus screen. Progression is Stage → Half-step → Grade, '
        'each grade needing a fixed EXP amount.'),
    Text('The three Worlds', style: h3),
    bullets([
      '**Mortal World**: Novice → Connection → Foundation → Virtuoso → '
          'Nascent Soul → Incarnation.',
      '**Spiritual World**: Voidbreak → Wholeness → Perfection → Nirvana. '
          'Entered via Ascension, the first timegate.',
      '**Immortal World**: Celestial → Eternal → Supreme. Entered via '
          'Transcendence.',
    ]),
    para('World boundaries carry the big resets — a fresh Myrimon fruit tier '
        'and extractor — while pill ranks step with every major Stage '
        '(Connection 1R … Incarnation 5R, Voidbreak 6R … Supreme 12R). Each '
        'era from Incarnation on is paced by a server timegate '
        '([[guide:timegate|Guide → Timegate]]).'),
    Text('Core formulas', style: h3),
    para('• Cultivation Speed = Abode Aura × Absorption Ratio\n'
        '• Abode Aura = 130 × (1 + total aura bonus) — base 130 holds for '
        'Connection through Incarnation\n'
        '• Cultivation ticks every 8 seconds (one Cosmoapsis)\n'
        '• Absorption = (stage base + Virya blessing points) × (1 + Strive); Strive '
        'unlocks at Nascent Soul and fades as you approach your server\'s #1\n'
        '• Pill EXP = base × (1 + pill effect + quality star mark [+ Vase star/skin '
        'for reds])'),
    Text('Strive', style: h3),
    para('From Nascent Soul, Strive multiplies absorption and grows the further you '
        'are behind server #1, fading as you catch up. Virya blessing points join the '
        'stage base inside the multiplier from Incarnation (Perfected) on '
        '([[guide:timegate|Guide → Timegate]]). Set "Server #1 Stage" to model '
        'the drop-off. It does not change your current-position time (it cancels out).'),
    Text('Crit variance (best / worst)', style: h3),
    para('Respira crits and fruit gushes are random, so estimates carry a ~90% best/worst '
        'band. Because these are sums of many independent rolls, luck averages out: the band '
        'is widest on short estimates and tightens over long horizons. Fruit gushes also have '
        'a pity floor (a gush is guaranteed within 6 fruits of the last one), narrowing the fruit side.'),
    Text('Timegates', style: h3),
    para('Timegates pace whole-server progression; Myrimon is the main F2P tool for '
        'meeting them. The prestock playbook for a gate is on '
        '[[guide:timegate|Guide → Timegate]].'),
    Text('Tips for using the calculator',
        key: anchorKey('ref:basics:tips'), style: h3),
    para('• Fill in Abode Aura and Absorption Ratio from the Cultivation Bonus '
        'screen and press Apply — that guarantees a current speed. A red warning '
        'means one of your readings is stale.\n'
        '• Re-read your numbers after any upgrade that touches aura (Energy Array, '
        'curios, sect level) — bonuses creep constantly and quietly.\n'
        '• Percentages in this game stack additively almost everywhere (pill '
        'effect sources, artifact star + skin bonuses, energy discounts). When in '
        'doubt, add percentage points; don\'t multiply.\n'
        '• Projections assume instant first-try breakthroughs and today\'s daily '
        'routine held constant — treat long-range estimates (with high Strive '
        'especially) as optimistic bounds.'),
  ], footerText: _refFooterText);
}

Widget _pillsPage(BuildContext context, Engine engine, Map<String, dynamic> catalog) {
  final h3 = Theme.of(context).textTheme.titleMedium;
  Widget para(String s) => docPara(context, s);
  Widget table(String title, List<String> headers,
          List<List<String>> rows, [String? note]) =>
      docTable(context, title, headers, rows, note);
  final pillXp = engine.data['pill_xp'] as Map<String, dynamic>;
  return docPage(context, [
    Text('Daily pills', key: anchorKey('ref:pills:daily'), style: h3),
    para('All pill colors share one daily attempt pool — spend your highest color first. '
        'Vase red (mythic) pills are exempt. A pill tooltip shows total EXP with the bonus '
        'in parentheses; base = total − bonus.'),
    table(
      'Cultivation Pill base EXP',
      ['Rank', 'Blue', 'Purple', 'Gold', 'Mythic'],
      [
        for (final e in pillXp.entries)
          [
            e.key,
            (e.value[pillBlue] as num).toString(),
            (e.value[pillPurple] as num).toString(),
            (e.value[pillGold] as num).toString(),
            (e.value[pillMythic] as num).toString(),
          ]
      ],
      'Pill-effect bonuses add as percentage points and multiply the '
      'base once.',
    ),
    table(
      'Pill Effect sources',
      ['Source', 'Bonus'],
      vaultBonusRows(catalog, {'pill_effect': '%'}),
      'All sources stack additively. Record what you own in the Vault and '
      'these fill themselves; type anything else in as a custom row.',
    ),
    table(
      'Respira bonus sources',
      ['Source', 'Effect'],
      vaultBonusRows(catalog,
          {'respira_attempts': ' attempt/day', 'respira_effect': '% Respira Effect'}),
      'Record these in the Vault; the Attempts / day and Respira Effect '
      'books fields fill themselves.',
    ),
    Text('Respira', style: h3),
    para('Daily-limited cultivation exercise. Each attempt rolls ×1/×2/×5/×10 crits at '
        '60/30/8/2% (mean ×1.8, applied automatically). Enter attempts/day and the base '
        '(non-crit) EXP per attempt — the small, most-common value you see, not a crit result.'),
    Text('Flat EXP', style: h3),
    para('Pills and Respira are flat EXP. The pill panel\'s % is relative to the '
        'current grade\'s requirement, so pills matter less as grades grow.'),
    Text('Dailies reset', style: h3),
    para('Daily pills/Respira reset on major breakthrough/ascension — spend them first.'),
  ], footerText: _refFooterText);
}

// Permanent consumables — verified 2026-07-10 from in-game screens
// (formula panel, elixir tooltips, Compare BR "Pill and Elixir Details").

Widget _elixirsPage(BuildContext context, Engine engine, Map<String, dynamic> catalog) {
  final h3 = Theme.of(context).textTheme.titleMedium;
  Widget para(String s) => docPara(context, s);
  Widget table(String title, List<String> headers,
          List<List<String>> rows, [String? note]) =>
      docTable(context, title, headers, rows, note);
  return docPage(context, [
    Text('Three things called "pill"', style: h3),
    para('"Pill" means three different things: daily cultivation pills '
        '(cultivation screen, Pill tab — see Pills & Respira), permanent stat '
        'pills crafted via alchemy (used from the backpack), and aux-path EXP '
        'items named pills (cultivation screen, Elixir tab — e.g. Hundred '
        'Fortunes Pill — mechanically elixirs).'),
    para('Elixirs are the other permanent family: reward/shop items granting '
        'either combat stats ("stat elixirs") or cultivation EXP ("EXP '
        'elixirs"), both with diminishing returns the more of an item you '
        'consume. Both families are covered below.'),
    Text('Stat pills (alchemy)', style: h3),
    para('Crafted from per-rank formulas (Windride = +10 P.EVA, Agility = '
        '+10 M.EVA). Flat effect, no decay, until the rank\'s permanent use '
        'cap is exhausted. The cap is on the pill, not the formula — '
        'shop/reward pills spend the same budget, and the counter ticks even '
        'with the formula unlearned. Each major realm breakthrough unlocks '
        'the next rank\'s uses per line.'),
    table(
      'Stat pill permanent use cap',
      ['Rank', 'Uses', 'Unlocks at'],
      [
        ['R1', '20', 'start'],
        ['R2', '40', 'next realm'],
        ['R3+', '50', 'each further realm'],
      ],
      '"Stat Pill Use Limit" on the Compare BR panel sums this across '
      'unlocked ranks × 2 evasion pill lines: 320 at Nascent Soul, 420 at '
      'Incarnation, 520 at Voidbreak. **Practical read:** there\'s no way '
      'to waste a stat pill — every use pays the same flat amount and the '
      'budget only refills by reaching new realms — so take them as you '
      'get them; the only real decision is whether the crafting cost is '
      'worth it, which gets steep at high ranks.',
    ),
    table(
      'Stat pill crafting cost (one craft)',
      ['Rank', 'Herb', 'Spiritium', 'Formula source'],
      [
        ['R1', 'Greenspirit ×1', '500', 'Market'],
        ['R2', 'Miragium ×2', '5,000', 'Sect Library'],
        ['R3', 'Spirit Marrow ×3', '24,000', 'Sect Library'],
        ['R4', 'Loftine ×4', '80,000', 'Sect Library'],
        ['R5', 'Udumbara ×6', '300,000', 'Sect Library'],
      ],
      'All formulas craft at Max Quality. A fully capped +10 line across '
      'R1–R5 = (20+40+50+50+50) × 10 = 2,100 stat.',
    ),
    Text('Stat elixirs (tolerance ladder)',
        key: anchorKey('ref:elixirs:tolerance'), style: h3),
    para('Stat elixirs (Yijing, Celeszure, Gouchen, dews and fruits…) grant '
        'permanent combat stats — but with diminishing returns. Each item '
        'tracks how many you\'ve consumed over your character\'s lifetime '
        '(the "Used" number on its panel), and the effect ratio steps down '
        'through fixed tiers as that count grows: the first few pay 150% of '
        'the listed stat, later ones less and less, until "Pill limit '
        'reached; it no longer takes effect" ends the item for good. The a/b '
        'counter on the panel is your position inside the current tier, not '
        'the overall cap.'),
    para('The ladder is a property of the item, not the character — a 3R '
        'elixir steps through the same tiers no matter whose realm consumes '
        'it.'),
    para('Practical read: there is no timing play — an elixir is worth the '
        'same whenever you take it, so use them as they arrive. When buying, '
        'remember the posted stat is the base: your next pill actually pays '
        'base × your current ratio, so an item deep into its ladder is worth '
        'a fraction of its face value.'),
    table(
      'Effect-ratio tiers (uses per tier)',
      ['Ratio', '3R', '4R', '5R'],
      [
        ['150%', '10', '10', '10'],
        ['120%', '—', '20', '20'],
        ['100%', '20', '30', '40'],
        ['80%', '50', '—', '—'],
        ['70%', '?', '60', '?'],
        ['50/30/20%', '?', '?', '?'],
      ],
      'Each tier contributes uses × base × ratio. "?" marks tiers no '
      'character has crossed yet; the in-game tooltip says the ladder '
      'continues 70 → 50 → 30 → 20% before the hard cap. Cultivation-EXP '
      'elixirs use different, wider tiers (first tier 20 uses, not 10).',
    ),
    Text('Elixirs and paths', style: h3),
    table(
      'Elixir line → path',
      ['Elixir line', 'Feeds'],
      [
        ['Vigor', 'Literatia, Fatebreaker Ghostia, Emerald Magicka, Nonagen Corporia, Cloudcut Grit Swordia'],
        ['Spiritual Nectar', 'your current path'],
        ['Hundred Fortunes / Pyroessence', 'your auxiliary path'],
      ],
      'A red requirement line = realm not met on that item\'s path. Path '
      'Switch swaps each elixir\'s remaining quantity, use attempts and '
      'efficiency along with the paths.',
    ),
    Text('Getting EXP elixirs',
        key: anchorKey('ref:elixirs:expelixirs'), style: h3),
    para('In normal play EXP elixirs only trickle in — small amounts, often '
        'priced in Fateum, which F2P players should generally spend on the '
        'garden first — it feeds the law system that starts at Voidbreak '
        '(see [[guide:voidbreak|Guide → Voidbreak+]]). The exception: breaking through to a new realm offers '
        'three real-money elixir packs, among the best value in the game for '
        'anyone optimizing money spent — the 150%/120% early tolerance tiers '
        'make each realm\'s batch worth the most right when you buy it.'),
  ], footerText: _refFooterText);
}

Widget _myrimonPage(BuildContext context, Engine engine, Map<String, dynamic> catalog) {
  final h3 = Theme.of(context).textTheme.titleMedium;
  Widget para(String s) => docPara(context, s);
  Widget bullets(List<String> items, [String? note]) => docBullets(context, items, note: note);
  return docPage(context, [
    Text('Myrimon Fruits', key: anchorKey('ref:myrimon:fruits'), style: h3),
    para('Fruits processed through the Aura Extractor grant a one-time EXP payout '
        '(the calculator credits it against the earliest remaining EXP). Payout scales '
        'with fruit rank, your Culti/Quality/Gush levels, and extractor rarity — higher '
        'quality rolls multiply the base substantially, so extractor upgrades compound.'),
    Text('Fruit ranks and realms', style: h3),
    para('Fruit ranks map to World bands: R3 is the Mortal World band (usable up '
        'to the Voidbreak gate), R6 starts the Spiritual World, R12 the Immortal '
        'World. R4/R5 don\'t exist.'),
    para('Myrimon unlocks at Virtuoso; the Mortal World (Virtuoso–Incarnation) '
        'shares one fruit/extractor tier; each World afterwards gets its own — '
        'Spiritual at Voidbreak, Immortal at Celestial.'),
    Text('Uses and stacking', style: h3),
    para('During the first week uses don\'t stack; after that they do — save them '
        'for Sunday or the next BR threshold.'),
    bullets([
      '**Weekly schedule**: each week\'s event runs Wednesday through the '
          'following Tuesday, with one free run each on Wednesday, Friday and '
          'Sunday (3 total), plus up to 2 purchasable Myrimon Tokens from the '
          'cash shop, each worth +1 run in the week you redeem it (5 runs max '
          'if both are bought and used).',
      '**Tokens** are inventory items — buy them freely and hold them '
          'unredeemed as long as you like. Near a realm ascension, don\'t '
          'redeem saved tokens for a few extra of the current realm\'s fruit; '
          'hold them and redeem right after ascending for the new realm\'s '
          'higher-tier fruit instead.',
    ]),
    Text('Aura Extractor', style: h3),
    para('Extractor tracks: the Cultivation Bonus track is +4% per level, plus '
        'Quality and Gush tracks. Rarity bonuses: each rarity rank unlocks +20% '
        'orb EXP for its tier, and extractor rank at your Stage gives base fruit '
        'EXP +50%.'),
    Text('Gush', style: h3),
    para('Gush: base 150% multiplier, raised on the Gush track. A gush is '
        'guaranteed within 6 fruits of the last one (soft pity — any gush, '
        'random or guaranteed, resets the counter), on top of the displayed '
        'random rate.'),
    Text('Reset on realm ascension', style: h3),
    para('The Aura Extractor resets to Common quality / bonus 0 when you ascend '
        'to a new realm — stage breakthroughs within a realm (e.g. Nascent Soul → '
        'Incarnation) don\'t reset it — and auto-consumes leftover previous-realm '
        'fruits at pre-upgrade rates. Upgrade fully before burning a stockpile, '
        'and burn it before ascending.'),
    Text('Leveling and stockpiling',
        key: anchorKey('ref:myrimon:verified'), style: h3),
    para('Extractor leveling priority: Quality → Cultivation → Gush → High Rank '
        '(High Rank last, only after the rest are maxed).'),
    docAdvisory(context, 'Tiering the extractor up requires consuming a number '
        'of fruits, so spend only the minimum needed for each tier-up and '
        'stockpile everything else until the extractor is maxed. Every fruit '
        'eaten early forfeits the better quality/EXP multipliers it would '
        'have received at higher extractor tiers — the same hoard is worth '
        'substantially more processed at max rarity. But do burn the '
        'stockpile before a realm ascension: the extractor resets there '
        '(see above).'),
    Text('Timegate penalty', style: h3),
    para('Fruits lose 50% of their EXP once the realm\'s timegate passes — eat '
        'the stockpile before the timegate.'),
  ], footerText: _refFooterText);
}

Widget _curiosPage(BuildContext context, Engine engine, Map<String, dynamic> catalog) {
  final h3 = Theme.of(context).textTheme.titleMedium;
  Widget para(String s) => docPara(context, s);
  Widget table(String title, List<String> headers,
          List<List<String>> rows, [String? note]) =>
      docTable(context, title, headers, rows, note);
  return docPage(context, [
    para('Curios (the Treasury half of the Vault) are passive relics. Most '
        'give combat stats, but a handful help cultivation directly — pill '
        'effect, Respira, and abode aura — and those are the ones worth '
        'chasing for breakthrough speed.'),
    Text('They come from random draws', style: h3),
    para('You don\'t buy a specific curio. New curios and the shards that star '
        'them up come from draws, so a particular curio landing is luck, not a '
        'plan. That\'s why the Advisor lists curios separately as "worth '
        'pulling for" rather than mixing them into the plannable steps — it '
        'tells you which curio, if you drew it, would save the most time, '
        'without pretending you can just go get it.'),
    Text('Stars and upgrades', style: h3),
    para('A curio\'s cultivation bonus grows two ways. Upgrade level raises '
        'the base value in small steps; stars add a scalar on top (shown in '
        'game as "Increases Curio Passive Stats"). Stars run 0 to 5 and then '
        'Awaken. For a percentage cultivation bonus the two add in percentage '
        'points — e.g. Yang Spirit Jade at 4 stars, upgrade 3 reads 3.2% (1.6 '
        'from the upgrade + 1.6 from the star scalar). Record the star and '
        'upgrade in the Vault and the pill / Respira fields fill themselves.'),
    para('A few cultivation curios are Special — the Spirit Seal set, for '
        'instance — and can\'t be starred or upgraded; they give one fixed '
        'bonus.'),
    table(
      'Cultivation curios',
      ['Curio', 'What it gives'],
      curioBonusRows(catalog),
      'Set stars and upgrade levels in the Vault\'s Treasury; only these '
      'curios feed the calculator. Abode-aura curios are already inside your '
      'entered Abode Aura reading — they\'re listed so you know which to keep.',
    ),
  ], footerText: _refFooterText);
}

Widget _artifactsPage(BuildContext context, Engine engine, Map<String, dynamic> catalog) {
  final h3 = Theme.of(context).textTheme.titleMedium;
  Widget para(String s) => docPara(context, s);
  Widget table(String title, List<String> headers,
          List<List<String>> rows, [String? note]) =>
      docTable(context, title, headers, rows, note);
  Widget bullets(List<String> items, [String? note]) => docBullets(context, items, note: note);
  final pillXp = engine.data['pill_xp'] as Map<String, dynamic>;
  final vaseCost =
      engine.data['vase_energy_cost'] as Map<String, dynamic>? ?? {};
  final gems = engine.data['gem_bonus'] as Map<String, dynamic>;
  return docPage(context, [
    Text('Creation Artifacts', style: h3),
    para('Eight Creation Artifacts exist — Vase, Pot, Mirror, Token, '
        'Shears, Cauldron, Basin, Pearl. Each has its own Artifact '
        'Energy pool that regenerates and is spent on that artifact\'s '
        'own effect. Three of them (Vase, Mirror, Pearl) spend Energy '
        'on cultivation EXP directly; two more (Pot, Shears) spend it '
        'on the garden instead. What each one does is covered below; '
        'how you acquire all eight — the point track, cash and voucher '
        'costs — is in [[ref:artifacts#summon|Acquiring the Creation '
        'Artifacts]] further down.'),
    Text('Energy (Vase, Mirror, Pearl)', style: h3),
    para('Regenerates 1 point / 15 min at 0★ (faster per star) and stops '
        'at a cap of 200 at 0★ (higher with stars) — idle energy above '
        'the cap is wasted, so spend before it fills. The paid daily '
        'charge (+100 energy for 30 Fateum/Destium, once per artifact) '
        'is usually the cheapest EXP a payer can buy; the calculator has '
        'a per-artifact checkbox for whether you use it.'),
    Text('Starsea Vase', style: h3),
    para('Refines any cultivation pill into a Mythic (red) pill worth '
        'far more EXP. Reds don\'t count against the daily attempt pool, '
        'so the Vase is effectively free extra pills every day — keep '
        'it fed.'),
    table(
      'Refine energy cost (per pill rank)',
      ['Rank', 'Energy'],
      [for (final r in pillXp.keys) [r, (vaseCost[r] ?? 100).toString()]],
      'Epic input −5%, Legendary −20%. Star: +10% EXP (1★), +20% (3★), 15% no-cost (5★). '
      'Skin +8% EXP.',
    ),
    Text('Dual-Star Mirror', style: h3),
    para('Duplicates owned items, including your red pills (only reds '
        'whose EXP bonus matches your Vase\'s unlocked tiers) — its '
        'copies stack on top of Vase production.'),
    bullets([
      '**Copy cost**: 200 energy base; −5% (1★), −10% (3★), −10% skin '
          '— discounts add together.',
      '**5★ bonus**: 15% chance of an extra copy per Duplication.',
    ]),
    Text('Timereversal Pearl', style: h3),
    para('Converts energy into auxiliary-path EXP. Its per-use EXP '
        'scales with your own cultivation speed bonuses, so re-read its '
        'tooltip after aura upgrades.'),
    bullets([
      '**Use cost**: 10 energy; star/skin discounts add (skin −10%).',
      '**EXP bonus**: +20% from 1★ (does not grow at higher stars).',
    ]),
    Text('Pot', style: h3),
    para('Speeds up garden plant growth — not Law Fruit-specific, it '
        'applies to garden plants generally, but Law Fruit only '
        'benefits from the main effect:'),
    bullets([
      '**Main effect, all plants**: 1 energy spent = 1 hour of grow '
          'time shaved off. This is the Pot\'s whole relevance to Law '
          'Fruit — see [[ref:systems#garden|Reference → World Systems]] '
          'for the garden throughput math this feeds into.',
      '**Secondary effect, gear-crafting plants only** (not Law '
          'Fruit): energy also raises those plants\' quality-limit cap '
          'from Purple up to Yellow. A 100-energy lump spend forces '
          'Red-tier evolution for gear-crafting plants specifically — '
          'Law Fruit\'s own Red tier comes from Shears instead (below), '
          'not from Pot energy.',
      '**Energy regen** is denominated in Taoist years (1 Taoist year '
          '= 15 real minutes): +1 energy/year at 0★ (≈96/day), cap 200 '
          '— higher stars raise both the regen rate and cap, plus add '
          'a flat speed-up bonus on top.',
    ]),
    para('Not to be confused with two unrelated curios that also '
        'happen to be called "Pot": the Zodiac Pot and Dongxuan\'s Pot '
        '— three separate "Pot" items in this game.'),
    Text('Shears', style: h3),
    para('Spends energy to advance an existing Law Fruit up to Red '
        'tier — the only way to get Red fruit, since it isn\'t grown '
        'naturally the way Green/Blue/Purple/Yellow are. Red\'s '
        '14-hour Blitz value is exempt from the 120-Blitz-hour/day cap '
        '(see [[ref:systems#garden|Reference → World Systems]]), the '
        'same exemption pattern cultivation pills get from the daily '
        'pill-attempt limit. Exact energy cost per conversion and any '
        'star-scaling aren\'t pinned down yet.'),
    para('Token, Cauldron, and Basin are also Creation Artifacts — see '
        'the acquisition costs below — but their own effects aren\'t '
        'documented here yet: they sit at \$5k-\$19k in the cost '
        'tables below, so few players have reached them.'),
    Text('Acquiring the Creation Artifacts',
        key: anchorKey('ref:artifacts:summon'), style: h3),
    para('All 8 Creation Artifacts — Vase, Pot, Mirror, Token, Shears, '
        'Cauldron, Basin, Pearl — come from the same point track, not a '
        'per-pull gacha. Points build up on one running total that never '
        'gets spent: crossing a relic\'s threshold unlocks it and '
        'progress keeps climbing toward the next one.'),
    table(
      'Creation Artifact point breakpoints (cumulative)',
      ['Relic', 'Points'],
      [
        ['Vase', '5,000'],
        ['Pot', '10,000'],
        ['Mirror', '20,000'],
        ['Token', '40,000'],
        ['Shears', '70,000'],
        ['Cauldron', '88,888'],
        ['Basin', '128,888'],
        ['Pearl', '158,888'],
      ],
      'Also the pool order: only one relic is available at a time, top '
      'to bottom, one per week — a hard ceiling of 8 weeks minimum for '
      'all 8 no matter how much gets spent. A relic can also be won '
      'early via an independent 0.25% instant-win roll on every draw, '
      'on top of the points.',
    ),
    para('Points also come from spending real money, at fixed yields per '
        'purchase tier that don\'t scale cleanly with price — some tiers '
        'are flatly better value than others. The same tiers can also be '
        'paid via SEAGM top-up vouchers instead of cash, which applies a '
        'flat 1.1× bonus to that tier\'s point yield regardless of which '
        'tier: every tier reduces to the same 1,000 vouchers = 11 points '
        'conversion, so voucher tier choice doesn\'t matter — only cash '
        'tier choice does, ranked here by cash rate:'),
    table(
      'Price-point value ranking',
      ['Price', 'Points (cash)', 'Rate (pts/\$)', 'Vouchers', 'Points via voucher'],
      [
        ['\$9.99', '68', '6.807 ← best', '6,800', '74.8'],
        ['\$29.99', '198', '6.602', '19,800', '217.8'],
        ['\$49.99', '328', '6.561', '32,800', '360.8'],
        ['\$14.99', '98', '6.538', '9,800', '107.8'],
        ['\$99.99', '648', '6.481', '64,800', '712.8'],
        ['\$19.99', '128', '6.403', '12,800', '140.8'],
        ['\$0.99', '6', '6.061', '600', '6.6'],
        ['\$2.99', '18', '6.020', '1,800', '19.8'],
        ['\$4.99', '30', '6.012 ← worst', '3,000', '33.0'],
      ],
      '\$99.99 is the biggest single pack — events offer up to 10× that '
      'rather than a bigger tier. Always buy \$9.99 packs over the three '
      'smallest (\$0.99/\$2.99/\$4.99), which are the worst value of the '
      'bunch; \$19.99 looks bad next to two strong neighbors but isn\'t '
      'actually the floor.',
    ),
    para('Each row below is the cumulative cost to guarantee everything '
        'through that relic — buying up to Pearl nets every relic above '
        'it too:'),
    table(
      'Cost to guarantee each relic — direct purchase',
      ['Relic', 'Points', 'Cost'],
      [
        ['Vase', '5,000', '\$739.26'],
        ['Pot', '10,000', '\$1,478.52'],
        ['Mirror', '20,000', '\$2,947.05'],
        ['Token', '40,000', '\$5,884.11'],
        ['Shears', '70,000', '\$10,289.70'],
        ['Cauldron', '88,888', '\$13,066.92'],
        ['Basin', '128,888', '\$18,941.04'],
        ['Pearl', '158,888', '\$23,346.63'],
      ],
    ),
    table(
      'Cost to guarantee each relic — SEAGM vouchers',
      ['Relic', 'Vouchers', 'Cost'],
      [
        ['Vase', '454,546', '\$650.93'],
        ['Pot', '909,091', '\$1,301.86'],
        ['Mirror', '1,818,182', '\$2,599.97'],
        ['Token', '3,636,364', '\$5,199.92'],
        ['Shears', '6,363,637', '\$9,099.71'],
        ['Cauldron', '8,080,728', '\$11,554.61'],
        ['Basin', '11,717,091', '\$16,752.75'],
        ['Pearl', '14,444,364', '\$20,650.61'],
      ],
      'Vouchers are consistently cheaper, by 11.6–12.1% at every step. '
      'Neither table accounts for the weekly one-relic-at-a-time gate or '
      'banked free draws, both of which cut real spend for a patient '
      'player — most players are better served picking a personal '
      'spending ceiling and relying on free daily draws past it '
      '([[guide:spending|Guide → Spending]] covers the tradeoffs).',
    ),
    table(
      'Aura Gem speed bonus',
      ['Rarity', 'Bonus'],
      [
        for (final e in gems.entries)
          if (e.key != 'None') [e.key, '+${((e.value as num) * 100).round()}%']
      ],
    ),
    Text('Aura Gem storage', key: anchorKey('ref:artifacts:auragem'), style: h3),
    para('Aura Gem is claimable storage: it accrues the gem\'s % of your '
        'cultivation speed and caps at 18–32 hours\' worth depending on rarity. '
        'Claim before it caps — the calculator assumes you always do.'),
  ], footerText: _refFooterText);
}

// Combat-side systems overview. Combat is resolved server-side; these are
// the client-visible rules, with exact numbers only where confirmed.

Widget _combatPage(BuildContext context, Engine engine, Map<String, dynamic> catalog) {
  final h3 = Theme.of(context).textTheme.titleMedium;
  Widget para(String s) => docPara(context, s);
  Widget table(String title, List<String> headers,
          List<List<String>> rows, [String? note]) =>
      docTable(context, title, headers, rows, note);
  Widget bullets(List<String> items, [String? note]) => docBullets(context, items, note: note);
  return docPage(context, [
    para('This page is about fighting, not cultivating — nothing here changes '
        'your breakthrough time. It\'s a plain-language tour of what your stats '
        'mean and what all the gear upgrade buttons actually do.'),
    Text('Your stats, in short', style: h3),
    para('Everything starts from five base stats. Each point you gain quietly '
        'converts into the combat numbers you see on your sheet:'),
    table(
      'What each base stat gives you',
      ['Base stat', 'Each point gives'],
      [
        ['Physique', '+4 Physical ATK, +2 Physical DEF'],
        ['Psyche', '+4 Magical ATK, +2 Magical DEF'],
        ['STR', '+1000 Max HP, +3 Physical DEF'],
        ['CON', '+1000 Max MP, +3 Magical DEF'],
        ['Agility', '+3 Dodge, +3 Hit Rate (both types)'],
      ],
    ),
    para('Notice the pattern: every combat stat has a physical and a magical '
        'version. Your path fights with one or the other, so Physique-type '
        'stats matter to a body cultivator the way Psyche-type stats matter to '
        'a mage — the other half mostly just pads your defense.'),
    para('You\'ll also see PvP-only lines like "DMG dealt to Taoists +x%" — '
        'those don\'t come from base stats at all; they come from the gear '
        'systems below.'),
    Text('How crit works', style: h3),
    para('Crit Chance is shown as a flat number, not a percent. The game '
        'converts it to a real chance relative to your realm — the same flat '
        'crit that felt great at Foundation is worth a smaller percentage by '
        'Nascent Soul. To see your actual percentage, tap the crit stat '
        'in-game: its tooltip shows your current crit rate for your realm. '
        '(The exact conversion curve lives on the server, so no formula here — '
        'the tooltip is the source of truth.)'),
    para('The rest of the crit family:\n'
        '• Crit DMG: a crit deals 150% damage baseline (rounded down); Crit '
        'DMG bonuses raise that multiplier.\n'
        '• Crit Defense: each +1% cuts an attacker\'s crit multiplier by 1% '
        'against you.\n'
        '• Crit Resistance: lowers the chance of being crit in the first '
        'place.'),
    Text('Gear basics', style: h3),
    bullets([
      'You wear a weapon, armor and an accessory, plus Relics as their own separate category.',
      '**Rarity** climbs white → green → blue → purple → yellow.',
      'When an item is forged its stats **roll within a range** — so two '
          'copies of the same item can differ, and a well-rolled piece is '
          'worth keeping.',
    ]),
    Text('Equipment relics — a gear category, not a side system',
        key: anchorKey('ref:combat:relics'), style: h3),
    bullets([
      '**327 relics** fill 6 of your equipment slots, and each one grants '
          'exactly one combat skill on top of stats — your active-skill '
          'loadout is which relics you have equipped. They go through the '
          'exact same rank/level/quality/forging/marks/sets layers as '
          'weapon/armor/accessory.',
      '**Rank determines which skill you have; quality only scales the '
          'surrounding stats, never the skill itself** — a high-quality '
          'relic hits the same skill numbers as a low-quality one at the '
          'same rank, just with better stats around it.',
      'Some relics are class-locked (a level/stage-gated set unique to '
          'one path), others are generic and open to any class — '
          '**generic and class relics are peers**, not a floor/ceiling: '
          'identical slots, forge cost, and tier ceiling. Pick by skill '
          'fit for your build rather than assuming generic is the weaker '
          'option.',
    ]),
    para('Distinct from the Creation Artifacts (Vase, Pot, Mirror, Token, '
        'Shears, Cauldron, Basin, Pearl — see [[ref:artifacts#summon|'
        'Reference → Artifacts & Gems]]) and the Zodiac Relic below — '
        'different systems that happen to share the word "relic".'),
    Text('Zodiac Relic — a single signature artifact',
        key: anchorKey('ref:combat:zodiac'), style: h3),
    bullets([
      '**One relic per account**, forged into either a physical or '
          'magical stance, that deploys into battle from Rank 2 as a '
          'semi-autonomous unit — it casts its own Hexes and carries its '
          'own full stat block that adds directly to your combat power, '
          'on top of everything from your equipped gear. The two stances '
          'are mirrored: same progression, same numbers, only the stat '
          'type differs (physical vs magical).',
      '**Reforge** swaps between stances non-destructively — only one is '
          'active at a time, but the inactive one\'s progress is '
          'preserved, not lost, so switching later never means '
          'regrinding from scratch (500 Fateum, 48h cooldown).',
      'Its stat backbone (**Soulfice**) scales **purely linearly** with '
          'level — every level adds the same fixed HP/MP, ATK, and DEF, '
          'no breakpoints to plan around.',
      'It also carries its own socketing (mark stones, socket treasures) '
          'and a star-upgrade mold system unlocking at **Rank 8** — '
          'layered enhancement systems similar in shape to weapon/armor '
          'carvings and sets, just on this one relic instead of a full '
          'loadout.',
      'Its **Hexes** (the spells it casts in battle) aren\'t quantified '
          'here — no cooldown, quality, or damage numbers are available '
          'yet, so treat their combat contribution as real but '
          'unmeasured for now.',
    ]),
    Text('Leveling gear (Augmentation)', style: h3),
    para('Pouring materials into a piece does three things:\n'
        '• Every level: its base stats grow a little. Steady, nothing to time.\n'
        '• Every 10th level: it unlocks an extra bonus line. Which line is '
        'fixed per item — one weapon always grows a Crit DMG line, another an '
        'ATK line.\n'
        '• Resonance: a bonus across your whole equipped set that looks at '
        'the level of your lowest piece. Push everything past the next '
        'threshold together and you unlock PvP bonuses like "Relic DMG to '
        'Taoists +x%".'),
    para('Practical takeaway: level your gear evenly. One maxed sword does '
        'less for you than eight pieces raised together, because Resonance '
        'only counts your weakest piece.'),
    Text('Carvings (the enchant lines)', style: h3),
    para('From Foundation on, gear can hold Carvings — bonus stat lines you '
        'level separately by feeding them Carving EXP items. Slots unlock as '
        'the item\'s augment level rises, and a carving that keeps leveling '
        'steps up through its own rarity colors, getting stronger at each '
        'step. Carvings have their own Resonance too, again counted across '
        'everything you\'re wearing.'),
    Text('Gear sets', style: h3),
    para('Each realm has a gear set: wear enough current-realm pieces and the '
        'set bonus turns on, granting those PvP damage/reduction lines and '
        'raising caps like how far carvings can go. The catch: when you break '
        'through to a new realm, the old set bonus switches off — you build it '
        'back up with the new realm\'s gear. Budget for that rather than being '
        'surprised by it.'),
    Text('Immortactic gear', style: h3),
    para('A separate side-track of equipment with its own levels and stars. '
        'Its stats grow in 2-level steps, with a Crit DMG boost every 20th '
        'level.'),
    Text('Affix priorities', style: h3),
    para('Which rolled bonus lines to chase on gear and relics has its '
        'own page now — see the [[ref:affixes|Affixes tab]] for the full '
        'tier list, the named rolls and their ranges, and the exact '
        'paralysis/penetration math.'),
    Text('About the missing numbers', style: h3),
    para('The exact values — what a given 10-level bonus or resonance rank '
        'grants — are decided server-side and vary by item and realm, so '
        'this page '
        'doesn\'t guess at them. Where a number isn\'t listed, read it as '
        '"unknown", not "zero". For the exact per-point math the game does '
        'expose, see the [[ref:combat-internals#perpoint|Combat Internals tab]].'),
  ], footerText: _refFooterText);
}

// Affix tier ranking is community consensus (opinion); per-point math
// and caps are verified from the decompiled client configs — see
// docs/knowledge/combat-mechanics.md for sources.

Widget _affixesPage(BuildContext context, Engine engine, Map<String, dynamic> catalog) {
  final t = Theme.of(context);
  final h3 = t.textTheme.titleMedium;
  Widget para(String s) => docPara(context, s);
  Widget table(String title, List<String> headers,
          List<List<String>> rows, [String? note]) =>
      docTable(context, title, headers, rows, note);
  return docPage(context, [
    Text('Gear & Relic Affixes', style: t.textTheme.titleLarge),
    para('Affixes are the rolled bonus lines on forged gear and relics. '
        'Which item drops is luck; which lines it rolls is what separates '
        'a keeper from forge fodder. The tier ranking below is '
        'subjective; the caps and per-point math are exact.'),
    para('Two caps drive most of the ranking: crit rate is hard-capped at '
        '50% and hit is capped at 99% (with a 25% floor — nobody can be '
        'evade-tanked below a 1-in-4 chance to hit). Capped stats are '
        'dead value past the cap.'),
    Text('T0 — always chase', style: h3),
    table('T0 affixes', ['Affix', 'Effect', 'Appears on'], [
      ['Wonder', '+30–46% ALL base stats', 'gear'],
      ['Blade Rage', '+20–28% P.ATK', 'swords, bracelets'],
      ['Spellforge', '+20–28% M.ATK', 'fans, pendants'],
      ['Spirit', '+9–21% relic cooldown', 'relics'],
      ['Ulti Sharp / Ulti Occult', '+15–21% P./M. ATK bonus on ultimates',
       'gear'],
      ['Bladeglow', '+11–15.4% flying-sword attack frequency',
       'longswords, greatswords'],
      ['Ether Veil', '+15–25.2% relic shield limit', 'trigrams, pearls'],
      ['Infinite Edge', '+15–25.2% relic damage limit', 'damaging relics'],
    ]),
    para('Base-stat % multipliers are the strongest lines in the game. '
        'Cast speed and the limit breakers matter most from Voidbreak on, '
        'where relic damage and shields cap easily.'),
    Text('T1 — good', style: h3),
    table('T1 affixes', ['Affix', 'Effect', 'Appears on'], [
      ['Annihilation',
       '+7.2–16.8% crit multiplier (gear); +18–42% relic crit multiplier '
           '(relics)',
       'gear, relics'],
      ['Pursuit', 'flat crit damage (stage-scaled; higher roll on relics)',
       'gear, relics'],
      ['Fatal',
       'flat crit chance (relic roll ≈4× the gear roll); dead value past '
           'the 50% cap',
       'gear, relics'],
      ['Sharp / Occult',
       'flat P./M. ATK on gear, flat P./M. DMG on relics', 'gear, relics'],
      ['Corporia / Magicka',
       'flat Physique / Manipulation (+4 ATK, +2 DEF per point)', 'gear'],
      ['Nimble',
       'flat Agility (+3 Hit and +3 EVA, both damage types, per point)',
       'gear'],
      ['Longevity / Vitality', 'flat HP / MP', 'gear'],
    ]),
    para('Match the line to your path. Sharp on a magical path — or '
        'Occult on a physical one — is trash on gear; on relics the '
        'mismatch penalty doesn\'t apply. Corporia and Magicka follow the '
        'same rule.'),
    Text('T2 — situational', style: h3),
    table('T2 affixes', ['Affix', 'Effect', 'Appears on'], [
      ['Conflict',
       '+9–21% relic status duration (T3 on relics with no status to '
           'extend)',
       'relics'],
      ['Precise / Focus', 'flat P./M. Hit (relic roll ≈4× the gear roll)',
       'gear, relics'],
      ['Insight / Agile', 'flat P./M. EVA', 'gear'],
      ['Stalwart / Refuge', 'flat P./M. DEF', 'gear'],
      ['Guardian', 'flat crit resistance', 'gear'],
      ['Soulclaim / Gloom', 'paralysis chance / duration boost',
       'weapons'],
      ['Tranquil / Serene', 'paralysis chance / duration resist',
       'armor'],
    ]),
    para('Defense lines are weak because Penetration strips up to 50% of '
        'defense when the attacker wins the contested check — see the '
        '[[ref:combat-internals#penblock|Combat Internals tab]].'),
    para('Paralysis math: boost and resist cancel 1:1; each leftover '
        'point shifts proc chance by 0.2% '
        '(enhance capped at +100%, resist at −50%) and duration by 0.5% — '
        'but the duration boost caps at +25% (only the resist side '
        'reaches −50%), so duration-boost lines saturate at 50 points of '
        'advantage.'),
    Text('T3 — avoid', style: h3),
    table('T3 affixes', ['Affix', 'Effect', 'Appears on'], [
      ['Bone / Tolerate',
       '% HP / MP regen — only ticks out of combat, which never happens '
           'in duels or the Voidgate',
       'gear'],
      ['Bladesoul',
       '+11–15.4% chance to keep flying swords when controlled — '
           'resummoning is near-instant anyway',
       'longswords, greatswords'],
    ]),
    Text('Practical takeaway', style: h3),
    para('Prioritize T0/T1 lines on weapons and pendants first. Reroll '
        'toward base-stat % (Wonder / Blade Rage / Spellforge) and relic '
        'cast speed — those two families define endgame power. Tier '
        'placement is subjective; the numbers and caps quoted are '
        'exact.'),
  ], footerText: _refFooterText);
}

// System explainers assembled from the client's own tooltip/description
// strings (i18n dump) plus user-verified play notes; server-side numbers
// are omitted rather than guessed.

Widget _systemsPage(BuildContext context, Engine engine, Map<String, dynamic> catalog) {
  final h3 = Theme.of(context).textTheme.titleMedium;
  Widget para(String s) => docPara(context, s);
  Widget table(String title, List<String> headers,
          List<List<String>> rows, [String? note]) =>
      docTable(context, title, headers, rows, note);
  Widget bullets(List<String> items, [String? note]) => docBullets(context, items, note: note);
  return docPage(context, [
    para('Short explainers for the systems the rest of this app keeps '
        'mentioning. Where a number is server-side, it\'s omitted rather '
        'than guessed.'),
    Text('Currencies', style: h3),
    bullets([
      '**Spiritium** — "the basic currency in the cultivation world. '
          'Mainly obtained in Realms. Used in Market, Alchemy, Forge Room '
          'and other daily matters." Realm idle production scales with '
          'Demon Spire progress.',
      '**Fateum** — the premium-adjacent currency, "obtained from '
          'gameplay or by exchanging Destium"; spent in the Fatevillion '
          'shop, on Path Switches, refreshes, and artifact daily charges.',
      '**Destium** — purchase-only; converts to Fateum 1:1 '
          '(irreversible). Also used in the Auction House.',
      '**Revealstone** (Seeker Shop) and **Citrine** + **Sect '
          'Contribution** (Sect Library) — two more shop currencies, see '
          'the buying guide below.',
    ]),
    para('Priority order for spending Fateum, and the Creation-Artifact '
        'cost tables, are on [[guide:spending|Guide → Spending]].'),
    Text('Shop-by-shop buying guide', style: h3),
    para('Widely recommended priorities:'),
    table(
      '',
      ['Shop', 'Currency', 'Buy', 'Notes'],
      [
        ['Market', 'Spiritium',
         'Demonroot (pet skills), Kunlun Jade (backpack space), Monster '
             'Core, Rare+ cultivation pills, Atlases, stat elixirs',
         'Refreshes every 3h; 10 manual refreshes/day (rising cost); '
             'every 5th refresh guarantees an Epic item'],
        ['Seeker Shop', 'Revealstone', 'Buy nothing before Voidbreak',
         'Nature Mantras cost ~200 each and you\'ll want 3,300+ of '
             'them — hundreds of thousands of Revealstone — and F2P '
             'sources are scarce, so every stone spent early is a mantra '
             'missing later'],
        ['Sect Library', 'Citrine / Sect Contribution',
         'Ability Manuscripts first — skipping them slows ability '
             'progression badly — then blueprints and alchemy formulas',
         'Citrine comes from mining spiritual veins, capped ~2h/day + '
             '7h/week — mine daily, prioritize the highest vein tier'],
        ['Fatevillion', 'Fateum',
         'The Cultivation Bag is the standout must-buy; cultivation '
             'elixirs while tolerance ratio is above ~120%; Demonlure '
             'for realm farming; anything at a 70% discount',
         'Resets on every breakthrough, minor ones included (Connection '
             '9→10 counts) — check it before each one'],
      ],
    ),
    Text('Cheap daily Fateum habits', style: h3),
    bullets([
      'The first daily Technique Points purchase (100 points for 50 Fateum)',
      'The second daily sect Construct (the first is free, the second costs 50)',
      'Refresh unclaimed Bounty Quests below Rare once a day — guaranteed upgrade',
      'Refresh Sect Tasks below C-rating once a day — guaranteed upgrade',
    ]),
    Text('Garden & Elemental Laws',
        key: anchorKey('ref:systems:garden'), style: h3),
    para('The garden grows seeds into rewards: each seed takes up plot '
        'space and takes time to grow. You get 1 free watering a day '
        '(2 a day with the Sword Trio set bonus) — each one pushes '
        'every planted seed 3 hours closer to done, all at once, not '
        'one plant at a time — plus whatever extra waterings '
        'companions give you (see [[guide:garden|Guide → Garden & '
        'Laws]] for the full picture). You can also speed up growth '
        'with energy, but that\'s not a base garden feature — that\'s '
        'the Pot Creation Artifact (see below). Seeds give you alchemy '
        'materials, technique seeds, and the headline crop: Law '
        'Fruit.'),
    para('Elemental Laws (unlocks at Voidbreak; five elements — Metal, '
        'Wood, Water, Fire, Earth) is a long-term damage system. Law '
        'Points build up on their own over time, faster the higher a '
        'law\'s level, and each element\'s rate doubles at set levels '
        '— 50, 150, 250, 350, and so on every 100 levels. You spend '
        'Law Points to level up your laws once you meet the Stage '
        'requirement. They also feed a separate Cosmic Laws system '
        'from the same pool — leveling Elemental Laws first makes '
        'both earn faster.'),
    para('Law Fruit is what actually feeds Elemental Laws, grown in '
        'the garden. Blitz turns a fruit into hours of law-learning '
        'progress, at whichever element\'s current rate you apply it '
        'to, up to 120 Blitz-hours a day (Red doesn\'t count against '
        'that cap):'),
    table(
      'Law Fruit tiers',
      ['Tier', 'Grow time', 'Blitz hours'],
      [
        ['Green', '4h', '1h'],
        ['Blue', '16h', '3h'],
        ['Purple', '40h', '6h'],
        ['Yellow', '88h', '12h'],
        ['Red', 'not grown — from the Shears artifact', '14h'],
      ],
      'Which tier is best depends on what\'s limiting you: Green wins '
      'per hour of grow-time (best if garden space is your limit), '
      'Yellow wins per seed (best if seeds are your limit) — the '
      'opposite ranking, so know which one is actually holding you '
      'back before picking either rule blindly.',
    ),
    para('**Garden capacity**: fully unlocked is a 6×6 grid (36 cells). '
        'Law Fruit and Ploughwood each take up 3 cells — a garden '
        'growing nothing but one of them holds **12 plants**, for a '
        'top output of 72 Blitz-hours a day at all-Green. The '
        'gear-crafting crop takes up a bigger 4-cell space (a line of '
        '3 with one extra cell), so cells spent on it buy fewer '
        'plants than the same cells would in Fruit or Ploughwood — '
        'there\'s no single "max plants" number, it depends on what '
        'you grow. The Pot artifact (a Creation Artifact — see '
        'Artifacts & Gems) speeds up growth (1 energy = 1 hour saved) '
        'and usually pushes the all-Fruit output to around 108 a '
        'day.'),
    para('**Garden slots you haven\'t bought yet cost you law levels '
        'for every day they sit unbought** — you can still buy them '
        'after Voidbreak, but you can never get back the levels those '
        'unbought days would have earned, so fully unlocking the '
        'garden before Voidbreak is worth it no matter how you plan '
        'to split the cells. But your weekly Law Fruit Seed income '
        '(20/week from the Sect), not cell count, is what actually '
        'limits how much Law Fruit you can grow — a handful of Law '
        'Fruit slots covers your full weekly supply, so the rest of '
        'the grid is better spent on Ploughwood and the gear-crafting '
        'crop, which don\'t run into that same seed shortage '
        '([[guide:garden|Guide → Garden & Laws]] covers the '
        'split).'),
    para('**Law Suppression**: compare your total Elemental Law level '
        '(summed across all 5 elements) against an opponent\'s. Each '
        'level of advantage deals +0.05% additional damage, with no cap '
        '— the bonus only applies while you\'re ahead, and it keeps '
        'scaling the further ahead you get. It\'s a PvP-only stat; '
        'nothing in PvE content references law levels.'),
    Text('Breakthrough failure', style: h3),
    para('Stage breakthroughs can fail. A failure injures your Primordial '
        'Soul, which must be restored before the next attempt — but '
        '"cultivation won\'t be affected while injured", so EXP keeps '
        'accruing. Pills "increase breakthrough success rate" (their own '
        'tooltip).'),
    para('In practice (mortal world): the Primordial Soul recovery is a '
        'wait — around an hour at early stages, but growing steeply with '
        'realm (a mid/late Incarnation failure has been observed at 13 '
        'hours). Breakthrough pills shorten the wait; better pills shorten '
        'it more. Unless you\'re racing for your server\'s top spots, a '
        'failure costs little — but in a race those hours decide it. The '
        'calculator assumes first-try breakthroughs, so a failure streak '
        'pushes real dates past its estimates by the recovery waits.'),
    Text('Path Switch', key: anchorKey('ref:systems:pathswitch'), style: h3),
    para('Available from Foundation. Costs Fateum (rising 800 → 2400) with '
        'a 7-day cooldown, and is blocked during competitive phases '
        '(ascendance events, brawl registrations, matchmaking, mining, '
        'server/sect transfer days). Your elixirs\' state swaps with the '
        'paths: remaining quantity, use attempts, and tolerance efficiency '
        'all follow the path they belong to.'),
    Text('Sects', style: h3),
    para('The social layer: joining one opens the Sect Library (pill '
        'formulas are exchanged here from R2 up), sect salary, tasks, '
        'treasure hunts, and the sect events (Meditation, Duel, Clash). '
        'Sect realm dominion gives practical buffs — +20% gathering speed '
        'on Spiritual Veins in the dominated realm.'),
    para('Picking one: sects are guilds — join an active one and have fun; '
        'an active sect naturally progresses and its benefits follow. If '
        'you care about the PvP sect events, aim for a stronger active '
        'sect, but that\'s personal preference. Just don\'t sit sectless: '
        'the library and salary alone are worth it.'),
    Text('Demon Spire', key: anchorKey('ref:systems:spire'), style: h3),
    para('A floor-climbing combat tower. Your current floor pays '
        'continuous hourly income — Ability Knowledge (levels your '
        'Abilities) and a bonus to Spiritium production in Realms — so '
        'every floor cleared is a permanent income raise. Climb whenever '
        'your battle rating allows.'),
    Text('Sacred Altar curios', style: h3),
    para('Collectible items placed on the Sacred Altar (six slots) — a '
        'combat power system, distinct from the cultivation curios '
        'tracked in the Vault (see the [[ref:curios|Curios]] tab). A slot '
        'boosts the passive stats of curios matching its type (HP, MP, '
        'P.ATK, M.ATK, P.DEF, M.DEF); percentage-stat curios don\'t '
        'benefit. Altar effects multiply with a curio\'s Star-Up. Rarities '
        'run Rare → Epic → Legendary → Mythic, from a draw system with '
        'guarantees. Several curios also carry the cultivation bonuses '
        '(pill effect, Respira) listed on the Vault\'s Curios tab.'),
    Text('The Sense stat', style: h3),
    para('Sense (internally spirit_max) currently does one thing: it '
        'gates how many treasures you can carry — Fabao slots unlock at '
        'Sense 1/7/13/16/19/22 and Gubao slots at 15/18/21. It grows by '
        'about 1 per realm level, and the game\'s own tooltip says '
        'further uses are planned. It is not part of any damage or '
        'cultivation formula the client exposes.'),
    Text('Techniques', style: h3),
    para('Unlockable passives: meet a technique\'s requirements to learn '
        'it, then spend Technique Points to tier it up — special effects '
        'unlock at Tiers 3, 6 and 9 (higher-rank manuals continue at 12 '
        'and 15). The early-game picks the guide names (Longevity, '
        'Energy Unification, Rejuvenation) are examples of buying these '
        'tier effects at their cheapest; the same logic — tier '
        'breakpoints first — carries through the rest of the game.'),
    // Community-guide material (2026) from here down — priorities and
    // tier lists are consensus, not client data.
    Text('Technique roadmap (recommended priorities)', style: h3),
    para('Quick per-rank picks below. The full rank-by-rank list through '
        'R21 — ratings and how deep to tier each manual — is on '
        '[[guide:techniques|Guide → Techniques]]:\n'
        '• R4: Golden Core and Astrology; Focus\'s unlock too.\n'
        '• R5: Ninefall; Bloodization for its aura node.\n'
        '• R6: Yin\'s Grasp to Tier 9; Conflagration and Unbound '
        'Blade.\n'
        '• R7: Floral Essence and Purify & Cleanse.\n'
        '• R8: Chroma and Astral Arcanum, plus your path\'s PvP pick.\n'
        '• R9: Harvest God Secret; Honored Origin for its aura nodes.\n'
        '• R10: everything — Immortal Ascension to Tier 12 for its +1 '
        'daily pill attempt (Tier 15 beyond that is stats-only).\n'
        '• R11+: each rank\'s law-speed manual first.'),
    para('For Technique Points, the recommended Spirit World strategy '
        'is three passes: clear what you can, come back stronger, '
        'finish later — rather than grinding one full clear early.'),
    Text('Sacred Altar curio priorities', style: h3),
    para('• Value order: abode/pill-bonus curios > main-path ATK > '
        'HP/MP.\n'
        '• Star up Pen & Block equally — a Pen roughly 1000 over the '
        'opponent\'s Block negates their defense.\n'
        '• Get everything to 2–3 stars minimum before pushing any single '
        'curio deep.\n'
        '• Daemonfae, Field and Reincarnation curios have their own '
        'niches — hold them rather than feeding them away.'),
    Text('Fields (Perfection)', style: h3),
    para('At Perfection you pick a Field; the usual mapping:\n'
        '• Solarium — PvE-leaning and the usual F2P pick.\n'
        '• Swordium — the general-purpose choice.\n'
        '• Darkmyth — team-oriented; pick it with your sect, not solo.\n'
        'Fields level and enlighten separately and have their own '
        'field-soul structure — details not yet captured here.'),
  ], footerText: _refFooterText);
}

// Expert-level internals; only client-stated mechanics carry numbers.

Widget _cultivationInternalsPage(BuildContext context, Engine engine, Map<String, dynamic> catalog) {
  final h3 = Theme.of(context).textTheme.titleMedium;
  Widget para(String s) => docPara(context, s);
  Widget table(String title, List<String> headers,
          List<List<String>> rows, [String? note]) =>
      docTable(context, title, headers, rows, note);
  return docPage(context, [
    para('The exact numbers behind the calculator\'s model, for readers who '
        'want to check the math.'),
    table(
      'Respira crit roll (per attempt)',
      ['Multiplier', 'Chance'],
      [
        ['×1', '60%'],
        ['×2', '30%'],
        ['×5', '8%'],
        ['×10', '2%'],
      ],
      'Mean multiplier 1.8, variance 2.56 per attempt — the main driver of '
      'the best/worst band on short horizons.',
    ),
    Text('Fruit gush pity', style: h3),
    para('The "Gush guaranteed in Aura Orb x6" counter is a '
        'soft pity — any gush, random or guaranteed, resets it. So a gush '
        'is guaranteed '
        'within 6 fruits of the last one, and the displayed chance is the '
        'per-fruit random rate. The calculator models the miss streak as a '
        'Markov chain and computes the exact gush-count mean and variance, '
        'which narrows the fruit side of the band.'),
    Text('Strive tier tables', style: h3),
    para('The live value is recomputed hourly server-side, so the '
        'calculator uses these only for the shape of the drop-off, '
        'anchored to your real Strive.'),
    table(
      'Young servers (world level < 30)',
      ['Realm gap to server #1', 'Strive'],
      [
        ['1', '15%'],
        ['2', '20%'],
        ['3', '30%'],
        ['4', '40%'],
        ['5', '50%'],
        ['6', '60%'],
        ['7', '70%'],
      ],
    ),
    table(
      'Mature servers (world level ≥ 30)',
      ['Minor-level gap', 'Strive'],
      [
        ['≥40', '20%'],
        ['≥50', '30%'],
        ['≥60', '70%'],
      ],
      'Plus an additive major-realm bonus: +30% (1 realm ahead) or +50% '
      '(2+ realms ahead). The 70% + 50% sum is the ~120% cap seen on '
      'aged servers.',
    ),
    Text('How the best/worst band is built', style: h3),
    para('A ~90% central interval (P5–P95): the '
        'calculator sums the variance of every random roll over the horizon '
        'and takes ±1.645 standard deviations around the mean. The band is '
        'widest in relative terms on short projections and tightens as the '
        'horizon grows.'),
  ], footerText: _refFooterText);
}

Widget _combatInternalsPage(BuildContext context, Engine engine, Map<String, dynamic> catalog) {
  final h3 = Theme.of(context).textTheme.titleMedium;
  Widget para(String s) => docPara(context, s);
  Widget table(String title, List<String> headers,
          List<List<String>> rows, [String? note]) =>
      docTable(context, title, headers, rows, note);
  Widget bullets(List<String> items, [String? note]) => docBullets(context, items, note: note);
  return docPage(context, [
    para('Damage resolution itself runs on the server, so treat this as the '
        'rulebook rather than a full damage calculator.'),
    Text('Flat stats and realm normalization', style: h3),
    para('Crit Chance, Crit Resistance, Hit Rate and Dodge are stored as flat '
        'values and converted to effective percentages against a '
        'realm-dependent standard. This is why the game\'s own tooltip reports '
        'your "crit rate at your current realm": the flat number keeps its '
        'value, but each realm raises the standard it\'s measured against, '
        'deflating the percentage. The normalization curve is server-side; '
        'the in-game tooltip is the only exact readout.'),
    KeyedSubtree(
        key: anchorKey('ref:combat-internals:perpoint'),
        child: table(
      'Per-point coefficients and caps',
      ['Stat', 'Per point', 'Cap'],
      [
        ['Penetration (phys/spell)', '−0.1% target DEF per point*', '—'],
        ['Block (phys/spell)', '30% proc; −0.1% DMG per point of advantage*', '—'],
        ['Stun duration enhance', '+0.5% duration', '+25%'],
        ['Stun duration resist', '−0.5% duration taken', '−50%'],
        ['Stun chance enhance', '+0.2% proc chance', '+100%'],
        ['Stun chance resist', '−0.2% proc chance', '−50%'],
        ['Elemental Rule level', '+0.05% DMG per level over target', '—'],
      ],
      '* Penetration and Block are contested against the opponent\'s same '
      'stat: each only functions while yours is higher than theirs.',
    )),
    Text('Penetration and Block, exactly',
        key: anchorKey('ref:combat-internals:penblock'), style: h3),
    para('These are mirror-image contested stats: each is compared against '
        'the opponent\'s copy of the same stat, and only the side with the '
        'higher value gets any effect at all.'),
    para('Penetration (physical or spell): while your Penetration is higher '
        'than the target\'s, every point of it strips 0.1% off the target\'s '
        'defense against your hits — 500 pen means the target defends with '
        '50% less DEF. Against someone with more Penetration than you, yours '
        'does nothing.'),
    para('Block (physical or spell): while your Block is higher than the '
        'attacker\'s, each incoming hit has a 30% chance to trigger a block, '
        'and a triggered block reduces that hit\'s damage by 0.1% per point '
        'of your advantage — the margin counts, not your raw total. On '
        'average it\'s worth 30% × 0.1% × margin per hit.'),
    para('Practical read: both are stat-check races. Small investments do '
        'literally nothing against players who invest more — unlike defense '
        'or crit, which always contribute.'),
    Text('Stuns, exactly', style: h3),
    para('Stun effects have two dials — whether the stun lands and how long '
        'it lasts — and each dial has an attacker stat and a defender stat '
        'fighting each other:\n'
        '• Stun chance: the attacker\'s enhance adds +0.2% proc chance per '
        'point (capped at +100%); the defender\'s resist removes 0.2% per '
        'point (capped at −50%).\n'
        '• Stun duration: the attacker\'s enhance adds +0.5% duration per '
        'point (capped at +25%); the defender\'s resist removes 0.5% per '
        'point (capped at −50%).'),
    para('On top of these, three flat percent stats exist that the game '
        'explicitly says are "not affected by any other effect" — they apply '
        'after the contested math: a direct % increase to stun duration you '
        'inflict, a direct % reduction to the chance of being stunned (1% = '
        'exactly 1%), and a direct % reduction to stun duration you suffer.'),
    Text('Crit, exactly', style: h3),
    para('• Crit Chance is flat and realm-normalized (see above); it applies '
        'to Ability and Relic hits and rises mainly from realm '
        'breakthroughs, weapons and accessories.\n'
        '• Crit Resistance is the defensive mirror: also flat and '
        'realm-normalized, it reduces the chance of being crit, and comes '
        'mainly from breakthroughs and armor. Its tooltip shows your '
        'effective resist % for your realm.\n'
        '• Crit DMG: a crit deals 150% damage baseline, rounded down; Crit '
        'DMG% raises this multiplier. Soul-bound Talismans have their own '
        '120% crit base.\n'
        '• Crit Additive DMG: a flat damage amount added on top of a crit '
        '(base 0) — added after the multiplier, not multiplied by it.\n'
        '• Crit Block trades exactly 1:1 — each 1% removes 1% from the '
        'attacker\'s crit multiplier against you (150% becomes 140% against '
        '10% Crit Block). It reduces how hard crits hit, never whether they '
        'happen.'),
    para('Practical read: the chance fight (Crit Chance vs Crit Resistance) '
        'and the damage fight (Crit DMG vs Crit Block) are separate. '
        'Stacking Crit DMG does nothing against someone you can\'t crit, and '
        'Crit Block won\'t stop crits from landing — it only blunts them.'),
    Text('Sustain, exactly', style: h3),
    para('Out of combat you regenerate 2% of max HP and MP per second; regen '
        'stats raise this rate. Shields come in three kinds: standard '
        'shields absorb a fixed capacity of damage, MP-fed shields route '
        'damage into your Max MP pool instead of a capacity limit, and blood '
        'shields are fed from HP. There are also statuses that strengthen an '
        'active shield\'s absorption, deal bonus damage while your shield '
        'holds, and cleanse debuffs when a shield is applied.'),
    Text('The gear stat formula', style: h3),
    para('An item\'s visible stat line is computed as:\n\n'
        '    floor( base[rank][affix] × roll × rarity_scale )\n\n'
        '• base[rank][affix] — a lookup keyed by the item\'s level '
        'requirement and which affix the line is; this table is server-side.\n'
        '• roll — the forge-time quality roll, interpolated linearly between '
        'the affix\'s min and max range (a 0–100 score).\n'
        '• rarity_scale — a flat multiplier per rarity color; higher rarity '
        'scales every line on the item.'),
    para('Carving lines use the same base lookup times a per-carving-level '
        'multiplier, which is why a carving\'s value jumps when its rarity '
        'tier steps up. Augment levels multiply the item\'s base stats by a '
        'smooth per-level curve on top of all of this.'),
    Text('Damage families', style: h3),
    para('Offense and defense are tracked separately per source: Abilities, '
        'Relics and Immortactic arts each have their own attack, defense and '
        'crit lines, and PvP ("vs Taoists") and PvE ("vs monsters") are '
        'independent trees on top of that. Two consequences worth knowing: a '
        '"Relic DMG +x%" line does nothing for your Ability damage, and PvE '
        'reduction does nothing in duels. There are also path-split modifiers '
        '— damage vs Immortal-path and vs Demon-path cultivators are separate '
        'stats.'),
    Text('How Battle Rating is put together', style: h3),
    para('The total is computed server-side, but the client defines the '
        'structure: every stat carries a BR weight, and your BR is the '
        'weighted sum of everything you have, plus pre-scored blocks for '
        'gear. The in-game BR breakdown panel groups it into:'),
    bullets([
      'Character level & realm',
      'Inner skill',
      'Gear (base + affixes + augment levels + carvings)',
      'Relics (same sub-parts as gear)',
      'Abilities and their training',
      'Curios (base + active + set)',
      'Pets (level, skills, growth)',
      'Talismans, celebrity cards and the rest',
    ]),
    para('Two useful things fall out of the client weights:\n'
        '• Defense is weighted ~2.1× attack per point (and HP/MP pool points '
        'far below either) — the game "prices" a point of defense as worth '
        'about twice a point of attack.\n'
        '• Each gear piece and Relic arrives with its BR pre-computed (a '
        'base score, and for Relics a realm-corrected score that only '
        'applies once your realm meets the item\'s requirement — an '
        'under-realm Relic shows its uncorrected, lower BR).'),
    para('The exact weight constants are known, but the server\'s '
        'final assembly (level factors, rounding) isn\'t, so per-stat '
        'BR predictions from these weights are approximate.'),
    para('One BR formula is fully client-side — standard monster BR:\n\n'
        '    floor( (hp_std^0.98 + mp_std^0.98) × hp_mult × max(atk_mults) )\n\n'
        'where hp_std/mp_std are the standard stat values for the monster\'s '
        'level and the multipliers are the monster\'s own scaling. The 0.98 '
        'exponent means BR grows slightly sub-linearly with raw stats. The '
        'same per-level standards table drives realm normalization: the '
        '"standard" each flat stat is measured against grows by roughly 5–8× '
        'per realm tier, which is exactly why a flat crit value loses '
        'percentage on breakthrough.'),
  ], footerText: _refFooterText);
}
