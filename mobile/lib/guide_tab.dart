/// Stage-by-stage cultivation guide, one sub-tab per realm band.
///
/// One ordered [guideSections] registry drives the slug->index map, the
/// TabController length, the Tab labels and the TabBarView children, so a
/// section can only be added or moved in one place.
library;

import 'package:flutter/material.dart';

import 'doc_nav.dart';
import 'doc_widgets.dart';
import 'pet_planner.dart';

class GuideSection {
  final String slug;
  final String title;
  final WidgetBuilder page;
  const GuideSection(this.slug, this.title, this.page);
}

const List<GuideSection> guideSections = [
  GuideSection('paths', 'Choosing a Path', _choosingPage),
  GuideSection('server', 'Server Timeline', _serverPage),
  GuideSection('routine', 'Daily Routine', _routinePage),
  GuideSection('novice', 'Novice–Foundation', _novicePage),
  GuideSection('virtuoso', 'Virtuoso', _virtuosoPage),
  GuideSection('nascent', 'Nascent Soul', _nascentPage),
  GuideSection('incarnation', 'Incarnation', _incarnationPage),
  GuideSection('timegate', 'Timegate', _timegatePage),
  GuideSection('voidbreak', 'Voidbreak+', _voidbreakPage),
  GuideSection('garden', 'Garden & Laws', _gardenPage),
  GuideSection('pets', 'Pets', _petsPage),
  GuideSection('aux', 'Aux Paths', _auxPage),
  GuideSection('techniques', 'Techniques', _techniquesPage),
  GuideSection('spending', 'Spending', _spendingPage),
];

/// Slug -> sub-tab index for [[guide:slug|...]] links (derived from
/// [guideSections]; registry order IS the tab order).
final Map<String, int> guideSlugs = {
  for (var i = 0; i < guideSections.length; i++) guideSections[i].slug: i
};

const _guideFooterText =
    'Spotted an error or something missing? Please report '
    'corrections and new data at:';

class GuideTab extends StatefulWidget {
  const GuideTab({super.key});

  @override
  State<GuideTab> createState() => _GuideTabState();
}

class _GuideTabState extends State<GuideTab>
    with SingleTickerProviderStateMixin {
  late final TabController _tabs =
      TabController(length: guideSections.length, vsync: this);
  final _nav = DocNavigator.instance;

  @override
  void initState() {
    super.initState();
    _tabs.addListener(() => _nav.guideSub = _tabs.index);
    _nav.pendingLink.addListener(_onDocLink);
    WidgetsBinding.instance.addPostFrameCallback((_) => _onDocLink());
  }

  void _onDocLink() {
    if (!mounted) return;
    final req = _nav.consumePendingFor(topTabGuide);
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
          tabs: [for (final s in guideSections) Tab(text: s.title)],
        )),
      ]),
      Expanded(
        child: TabBarView(controller: _tabs, children: [
          for (final s in guideSections) s.page(context),
        ]),
      ),
    ]);
  }
}


// Path meta from a circulating community guide (2026) plus the
// maintainer's read of Discord consensus — opinion, not client data.

Widget _choosingPage(BuildContext context) {
  final h3 = Theme.of(context).textTheme.titleMedium;
  Widget para(String s) => docPara(context, s);
  Widget table(String title, List<String> headers,
          List<List<String>> rows, [String? note]) =>
      docTable(context, title, headers, rows, note);
  return docPage(context, [
    Text('Choosing your path', style: h3),
    para('The first decision in the game. It\'s less permanent than it '
        'looks — [[ref:systems#pathswitch|Path Switch]] exists from '
        'Foundation — but your path shapes combat style, gear '
        'priorities, and which elixirs/pets/aux picks fit. This summary '
        'is subjective, and opinion is genuinely mixed — '
        'treat it as orientation, not law.'),
    table(
      'The five paths',
      ['Path', 'Type', 'Style', 'Relics', 'Verdict'],
      [
        ['Swordia', 'HP / physical', 'Highest sustained DPS; strong PvP and PvE bossing', 'Very reliant', 'The safe strong pick'],
        ['Corporia', 'HP / physical', 'Burst damage, death-immunity ultimate; weak early, much stronger later', 'Not reliant', 'PvP-leaning; weak PvE'],
        ['Magicka', 'MP / magic', 'AoE damage, shields and crowd control; more piloting than Swordia', 'Not reliant', 'The flexible pick; good PvE farm, holds up in PvP'],
        ['Ghostia', 'MP / magic', 'Ghost companion (taunt + damage), unblockable-paralyze ultimate', 'Very reliant', 'Strong PvE and dueling'],
        ['Literatia', 'MP / magic', 'Builds erudition for a high-burst mana dump; weak early, scales up later', 'Not reliant', 'Good AoE farm and PvE; PvP still unproven'],
      ],
    ),
    para('Rules of thumb: want one answer for everything — Swordia. '
        'PvE/farming focus — Ghostia or Magicka. PvP focus — Corporia or '
        'Swordia. Patient scaler who accepts a weak mortal world — '
        'Literatia. Aux pairings are on the [[guide:aux|Aux Paths tab]].'),
    para('Relic-reliant paths (Swordia, Ghostia) care more about relic '
        'income and forging; ability-focused paths (Corporia, Magicka, '
        'Literatia) lean on ability levels — which come from Demon Spire '
        'climbing ([[ref:systems#spire|Reference → World Systems]]).'),
  ], footerText: _guideFooterText,
      padding: const EdgeInsets.all(16));
}

// Server calendar sources: docs/knowledge/game-mechanics-verified.md
// (Worlds section); day numbers are era estimates.
Widget _serverPage(BuildContext context) {
  final h3 = Theme.of(context).textTheme.titleMedium;
  Widget para(String s) => docPara(context, s);
  return docPage(context, [
    Text('How a server unfolds', style: h3),
    para('OverMortal is server-paced. World-level timegates hold the whole '
        'server to one calendar — nobody enters a new era before its gate '
        'opens — and the catch-up mechanics accelerate everyone behind the '
        'front. Two consequences: your first month has a known shape, and '
        'you cannot fall permanently behind.'),
    Text('The first month (day numbers drift by era)', style: h3),
    para('• Day 0 — the server opens. The early stages fly: '
        'Novice–Foundation on day one, Virtuoso by its end, Nascent Soul '
        'around day 3 free-to-play.\n'
        '• Weeks 1–4 — the climb through Nascent Soul and Incarnation. '
        'Build the extractor and stockpile fruits, keep every daily stream '
        'full, and keep battle rating growing: the Ascension Virya '
        'blessings at Incarnation\'s end gate on Myrimon Wonder boss '
        'clears.\n'
        '• ~Day 35–38 — the first timegate lifts: Ascension into '
        'Voidbreak, the Mortal → Spiritual World boundary. The parked '
        'weeks before it are the prestock window — the full playbook is '
        'on [[guide:timegate|Guide → Timegate]].\n'
        '• Day 40 — server transfer unlocks (for Voidbreak and higher).\n'
        '• After that — every major Stage from Wholeness on is paced by '
        'its own gate, and the World-boundary resets (fresh Myrimon tier '
        'and extractor) repeat at Celestial. The rhythm you learn at the '
        'first gate is the game\'s permanent shape.'),
    Text('Why you can\'t fall behind', style: h3),
    para('Two mechanics work together. Timegates hold the server\'s front '
        'in place — the leaders sit parked at caps, stocking overcap EXP '
        'while the gate is closed — and Strive multiplies absorption for '
        'everyone behind the front, fading only as you close the gap '
        '([[ref:basics|Reference → Basics]]). The server bunches up at '
        'every gate, then peels off front to back. A slow week doesn\'t '
        'compound; the system pulls you back toward the pack.'),
    Text('Joining an established server', style: h3),
    para('• Once a gate has opened for the server it stays open — you '
        'ascend the moment you\'re ready, no waiting.\n'
        '• Strive is your engine: the further behind the front you start, '
        'the bigger your absorption multiplier.\n'
        '• The +50% highest-Stage fruit bonus isn\'t yours until you reach '
        'the server\'s front, so extractor leveling discipline '
        '([[ref:myrimon|Reference → Myrimon & Extractor]]) matters even '
        'more for you — the multipliers you control are the ones you '
        'get.\n'
        '• Server transfer (Voidbreak and higher) can move you to a server '
        'whose calendar fits your pace.'),
  ], footerText: _guideFooterText,
      padding: const EdgeInsets.all(16));
}

Widget _routinePage(BuildContext context) {
  final h3 = Theme.of(context).textTheme.titleMedium;
  Widget para(String s) => docPara(context, s);
  return docPage(context, [
    Text('Your daily loop', style: h3),
    para('OverMortal is an idle game with a short list of things that '
        'actually need your hands each day. Everything here is collected '
        'from the other guide pages — this is just the checklist form.'),
    Text('Every day', style: h3),
    para('• Spend your daily pill attempts — highest color first (all '
        'colors share one attempt pool; Vase reds are exempt). Never leave '
        'attempts unused: pill EXP roughly halves per quality step, so a '
        'full limit of a lower color beats a half-filled limit of a higher '
        'one.\n'
        '• Use your Respira attempts.\n'
        '• Keep artifact energy below its cap — Vase refines, Mirror '
        'duplications, Pearl uses. Energy regenerating into a full pool is '
        'wasted. If you pay, the 30 Fateum/Destium daily charge per '
        'artifact is among the cheapest EXP money buys.\n'
        '• Claim your Aura Gem before its storage caps — once full it '
        'stops accruing ([[ref:artifacts#auragem|Reference → Artifacts & '
        'Gems]]).\n'
        '• Check the market for Demonroot (pet skills) and similar limited '
        'stock.\n'
        '• Take stat pills and elixirs as they arrive — there\'s no timing '
        'play on either ([[ref:elixirs|Reference → Elixirs & Stat Pills]]).\n'
        '• Myrimon runs: during the event\'s first week they don\'t '
        'accumulate — use them daily at the highest realm you can clear.'),
    Text('Weekly', style: h3),
    para('• Banked Myrimon runs: spend them on Sunday, or hold them until '
        'you can clear a higher-requirement dungeon. Fruits go to the '
        'stockpile, not the extractor, until the extractor is maxed '
        '([[ref:myrimon#verified|Reference → Myrimon & Extractor]]).\n'
        '• Spend resources as they come. Hoarding pays only in the parked '
        'weeks before a timegate ([[guide:timegate|Guide → Timegate]]) — '
        'between gates, saved resources are power you didn\'t use.'),
    Text('Before every major breakthrough', style: h3),
    para('• Spend all daily pills and Respira attempts — they reset on the '
        'breakthrough.\n'
        '• Eat the fruit stockpile before a realm ascension — the extractor '
        'resets to Common there (stage breakthroughs within a realm don\'t '
        'reset it) and auto-consumes leftovers at pre-upgrade '
        'rates.\n'
        '• Spend Fatevillion shop tokens — that shop resets too.\n'
        '• Don\'t claim pill bags until after the ascension.\n'
        '• If you spend money: the three elixir packs offered on reaching '
        'the new realm are among the best value in the game '
        '([[ref:elixirs#expelixirs|Reference → Elixirs & Stat Pills]]); the full '
        'what\'s-worth-it list is on [[guide:spending|Guide → Spending]].'),
    Text('Quality-of-life settings', style: h3),
    para('• Turn off wandering (settings) — it only animates your '
        'character walking around and costs attention for nothing.\n'
        '• Set battle speed to 3× once it unlocks; there is no downside.'),
  ], footerText: _guideFooterText,
      padding: const EdgeInsets.all(16));
}

Widget _novicePage(BuildContext context) {
  final h3 = Theme.of(context).textTheme.titleMedium;
  Widget para(String s) => docPara(context, s);
  return docPage(context, [
    Text('Novice → Foundation (your first day)', style: h3),
    para('These first realms go by in hours. The goal is simple: keep the '
        'cultivation bar filling and break through the moment you can — the '
        'Breakthrough button appears on the main cultivation screen when the '
        'bar is full.'),
    para('• Break through to Connection immediately; nothing in Novice is '
        'worth lingering for.\n'
        '• Pills are the bottles on the bottom row of the cultivation screen '
        '— each grants instant EXP against a daily attempt limit. Use only '
        'blue pills at first, and don\'t max your attempts before claiming '
        'the pill bag from the early quests. Save 5–10 attempts for '
        'Foundation 10, and spend pills mainly when they push a stage '
        'breakthrough. (What each pill is worth: '
        '[[ref:pills#daily|Reference → Pills & Respira]].)\n'
        '• Alchemy: save blue/purple pill materials for F9–F10 instead of '
        'crafting them immediately.\n'
        '• Respira is the daily breathing exercise on the cultivation screen '
        '(the "Today\'s Attempts" counter). Before the Foundation '
        'breakthrough, open Techniques and max Longevity — it permanently '
        'adds +1 daily Respira attempt and is cheapest now.\n'
        '• In Foundation, unlock the Energy Unification technique before '
        'spending Respira attempts, and hold pill attempts until Foundation '
        'Late with Rejuvenation at T3.\n'
        '• Energy Array materials come from the world-map realms: 56 '
        'violetite from Violet Streams, then 110 frostite from Lake '
        'Blackwater. The array permanently raises your Abode Aura — the base '
        'of your cultivation speed ([[ref:basics#cultivation|Reference → Basics]]).'),
  ], footerText: _guideFooterText,
      padding: const EdgeInsets.all(16));
}

Widget _virtuosoPage(BuildContext context) {
  final h3 = Theme.of(context).textTheme.titleMedium;
  Widget para(String s) => docPara(context, s);
  return docPage(context, [
    Text('Virtuoso (usually end of day 1)', style: h3),
    para('• Myrimon unlocks here — the Aura Extractor lotus next to your '
        'character on the cultivation screen, fed by fruits from the weekly '
        'Myrimon dungeon runs. It becomes your biggest free source of '
        'cultivation EXP, so read [[ref:myrimon|Reference → Myrimon & '
        'Extractor]] before '
        'spending anything.\n'
        '• During the first week of the Myrimon event your daily runs don\'t '
        'accumulate — use them every day at the highest realm you can clear. '
        'Afterwards they stack: bank them for Sunday or until you can clear '
        'a higher-requirement dungeon.\n'
        '• Work through Realm Abyss and Cultivation Ruins (in the realm '
        'menus) for all three Virtuoso realms — one-time cultivation '
        'rewards.\n'
        '• Check the events panel for realm exploration events; the curio '
        'rewards are worth the detour.\n'
        '• Free equipment upgrade materials: open the Library of No Bound → '
        'Encyclopedia Tales and go through the lore chronicles. Each '
        'chronicle has a comment section with notes from game NPCs — the '
        'first like you give in each chronicle\'s comments awards equipment '
        'upgrade material. Worth sweeping once while pushing through '
        'Virtuoso.'),
  ], footerText: _guideFooterText,
      padding: const EdgeInsets.all(16));
}

Widget _nascentPage(BuildContext context) {
  final h3 = Theme.of(context).textTheme.titleMedium;
  Widget para(String s) => docPara(context, s);
  return docPage(context, [
    Text('Nascent Soul (~day 3 for F2P)', style: h3),
    para('• Pacing: roughly 3 days to Nascent Late and 3 more to '
        'Incarnation. Spenders arrive faster — don\'t panic if you\'re a day '
        'behind.\n'
        '• Strive unlocks here: a catch-up bonus that raises your absorption '
        'while you\'re behind your server\'s #1 cultivator. In this '
        'calculator it appears as the implied Strive readout, and the '
        '"Server #1\'s Stage" input starts to matter for long-range '
        'estimates ([[ref:basics#tips|Reference → Basics]] covers the math).\n'
        '• Keep the story, Demon Spire, and realms pushed as far as they\'ll '
        'go each cultivation stage — several systems gate on them.\n'
        '• By now stat pills and elixirs are flowing in from shops and '
        'rewards. Take them as they arrive — neither can be wasted by using '
        'them early, and stat pills\' use caps grow with each realm anyway '
        '([[ref:elixirs|Reference → Elixirs & Stat Pills]]).'),
  ], footerText: _guideFooterText,
      padding: const EdgeInsets.all(16));
}

Widget _incarnationPage(BuildContext context) {
  final h3 = Theme.of(context).textTheme.titleMedium;
  Widget para(String s) => docPara(context, s);
  Widget bullets(List<String> items, [String? note]) => docBullets(context, items, note: note);
  return docPage(context, [
    Text('Incarnation', style: h3),
    Text('Extractor priorities', style: h3),
    para('The extractor endgame for the mortal world: open Aura Extractor '
        '→ Boost and max its tracks — Quality first, then Cultivation, then '
        'Gush (High Rank last). Keep stockpiling fruits instead of eating '
        'them: every extractor level makes each fruit worth more, and at '
        'Mortal World rank the extractor adds +50% base fruit EXP while '
        'you\'re at the server\'s highest Stage.'),
    Text('Pre-breakthrough checklist', style: h3),
    bullets([
      'Eat the stockpile before the realm timegate — fruits lose 50% of '
          'their EXP once the next realm\'s timegate passes — or on the '
          'last day before your own breakthrough, whichever comes first. '
          '(Full fruit math: [[ref:myrimon#fruits|Reference → Myrimon & '
          'Extractor]].)',
      'Before breaking through to Voidbreak: spend all pills and Respira '
          '(they reset), don\'t claim daily pill bags until after '
          'ascension, and spend Fatevillion shop tokens beforehand — '
          'that shop resets on breakthroughs too.',
      'On the ascension itself you\'ll be offered three real-money '
          'elixir packs — if you spend at all, these are among the best '
          'value in the game ([[ref:elixirs#expelixirs|Reference → '
          'Elixirs & Stat Pills]] explains why the early tolerance tiers '
          'make them worth the most).',
    ]),
    Text('Keep battle rating growing all era', style: h3),
    para('The Ascension Virya blessing tiers gate on Myrimon Wonder boss '
        'clears (Amethyst Fiend, Jade-Eyed Lion). Reaching the gate weeks '
        'with the bosses unkillable means blessings locked exactly when '
        'they matter most.'),
    para('The run-up to the realm timegate — prestocking past 100%, the '
        'Ascension Virya blessings, and what to do the day the gate lifts '
        '— has its own page: [[guide:timegate|Guide → Timegate]].'),
  ], footerText: _guideFooterText,
      padding: const EdgeInsets.all(16));
}

// Overcap/Virya mechanics and half-step totals:
// docs/knowledge/game-mechanics-verified.md + data/breakthrough.json.
Widget _timegatePage(BuildContext context) {
  final h3 = Theme.of(context).textTheme.titleMedium;
  Widget para(String s) => docPara(context, s);
  Widget bullets(List<String> items, [String? note]) => docBullets(context, items, note: note);
  return docPage(context, [
    Text('The Voidbreak timegate', style: h3),
    para('A world-level timegate blocks the ascension from Incarnation '
        'into Voidbreak until a fixed server day (roughly day 35–38 of a '
        'server\'s life; the exact day drifts by era). This ascension is '
        'also the Mortal → Spiritual World boundary — the fresh Myrimon '
        'tier and extractor ride on it (see the Worlds table in '
        '[[ref:basics|Reference → Basics]]). Handled well, the gated '
        'weeks become a stockpile that carries you deep into Voidbreak '
        'the day the gate opens. The same pattern returns at every later '
        'gate.'),
    Text('Excess EXP: nothing is lost at a full gauge', style: h3),
    para('• While the gate blocks your breakthrough, cultivation EXP keeps '
        'accruing past the full gauge into an Excess EXP pool that is '
        'returned after the breakthrough.\n'
        '• Breakthroughs are always manual: stocked excess applies as you '
        'click through each grade, so a large pool clears whole half-steps '
        'in one go.\n'
        '• The gauge percentage past 100% reads as EXP gained since the '
        'start of your current half-step ÷ that half-step\'s total — read it '
        'off the half-step completion gauge that fills to 100% and keeps '
        'climbing, not the per-grade step bar. An overcap percentage '
        'translates directly into future progress.'),
    docTable(context, 'What a given stock buys you',
        ['Half-step', 'Total EXP'],
        [
          ['Incarnation Late', '61.8M'],
          ['Voidbreak Early (20 grades)', '68.0M'],
          ['Voidbreak Middle (20 grades)', '142.1M'],
          ['Voidbreak Late (20 grades)', '307.7M'],
        ]),
    para('• 100% — gauge full: take the Completion breakthrough (below) '
        'and keep stocking.\n'
        '• 210% — the excess clears all of Voidbreak Early on ascension '
        'day.\n'
        '• 440% — Early and Middle both: you arrive at Voidbreak Late G1 '
        'immediately.'),
    Text('Accrual while parked at a full gauge', style: h3),
    para('• You accrue at the capped row\'s base band — no future-row '
        'speed scaling.\n'
        '• Strive does NOT apply while overcapped. Server leaders lose '
        'nothing; the further behind the top player you are, the more '
        'parking under-performs your normal rate.\n'
        '• Virya blessing points apply in full.\n'
        '• Flat daily EXP — pills, Respira, elixirs, fruits — lands in the '
        'pool at face value, unaffected by parking.'),
    para('Base bands rise with each half-step: Incarnation Late 0.40 → '
        'Voidbreak Early 0.50 → Middle 0.65 → Late 0.80.'),
    Text('Ascension Virya blessings: the biggest lever', style: h3),
    para('Blessing points are the difference between a mediocre stock and '
        'a huge one. Tiers unlock from your primary and secondary paths '
        'together:'),
    bullets([
      '**Completion** — reach Incarnation Late 100% and break through '
          'into Incarnation (Perfected). A full gauge alone is not '
          'enough: the blessing system does not start until this '
          'breakthrough is taken. It is not blocked by the timegate — '
          'the gate blocks only the ascension into Voidbreak — so take '
          'it the moment the gauge fills. It removes realm restrictions '
          'on cultivation pills (higher-rank pills can feed a lower '
          'secondary path; rank-appropriate pills already work there '
          'without it) and unlocks pill auto-transmogrification, which '
          'lets breakthrough pills of one path be used on the other '
          '(physical ↔ magical). Together these make the secondary '
          'rush below possible.',
      '**Perfection** — primary at Incarnation (Perfected), secondary '
          'at Nascent Soul Late, clear Amethyst Fiend in Myrimon '
          'Wonder: +20 points absorption in your current Stage.',
      '**Perfect** — secondary at Incarnation Middle, clear Jade-Eyed '
          'Lion: a second absorption tier, plus an "Absorption Ratio '
          'Before Voidbreak Middle" line that comes into play once you '
          'are in Voidbreak.',
    ]),
    para('Secondary requirements are satisfied on REACHING the named '
        'half-step, not completing it. On the Incarnation base band a live '
        '+20 points already lifts your parked rate well above the raw '
        'passive rate, so the rush is worth prioritising. How the tiers '
        'carry into Voidbreak depends on your build — read your in-game '
        'absorption there and enter it into the calculator rather than '
        'assuming a fixed total.'),
    Text('Preparing while gated', style: h3),
    bullets([
      '**Cap Incarnation early** and take the Completion breakthrough at '
          'once. Days spent climbing to the cap are not stocking days, '
          'and the gauge filling by itself starts nothing. Top off with '
          'banked fruits if the gauge won\'t fill on streams alone.',
      '**Rush the Virya tiers** immediately after: divert your daily '
          'pills to the secondary path (passive stays on the primary) '
          '— Nascent Soul Late unlocks the first absorption tier, '
          'Incarnation Middle the next. The earlier the tiers land, the '
          'longer they lift your parked accrual. Clear the two Myrimon '
          'Wonder bosses ahead of time so they never hold a tier '
          'hostage.',
      '**Fill every flat stream, every day.** Never leave pill attempts '
          'unused: pill EXP roughly halves per quality step, so a full '
          'limit of the next quality down matches a half-filled limit '
          'of the one above.',
      '**Eat the fruit bank before the gate opens** — the banking and '
          '50% rules are on [[guide:incarnation|Guide → Incarnation]]. '
          'Leftovers don\'t survive the ascension anyway: the mortal '
          'extractor resets at the World boundary and auto-consumes '
          'them at pre-upgrade rates.',
      '**Hoard for the arrival** — the parked weeks are the window: '
          'sect contribution (~13–14k) for the new realm\'s blueprints '
          'and formulas; Fateum and Fate Tokens, Revealstones, plant '
          'speed-ups; trove jadeslips for Cosmic Atlas, Ancient '
          'Treasure and Pet Index — their contents re-tier on realm '
          'breakthrough, so opened on arrival they pay out at the new '
          'realm\'s tier. Don\'t run this hoard between gates: realm '
          'gates are months apart, and resources sat on for months are '
          'power you didn\'t use.',
      '**Fully unlock the garden before Voidbreak**, even though Law '
          'Fruit isn\'t usable until you\'re there. You can still buy a '
          'garden slot later, but every day it stays unbought is '
          'Elemental Law throughput you can\'t recover afterward — '
          'there\'s no way to go back and claim the law levels a locked '
          'cell would have earned you. This is separate from harvesting '
          'it empty below: buy every cell now, '
          'then replant Law Fruit the moment Voidbreak opens '
          '([[guide:garden|Guide → Garden & Laws]] covers the layout and '
          'throughput math).',
      '**Spend what dies with the realm**: beyond the pre-breakthrough '
          'rules on the Incarnation page, spend Ability Knowledge and '
          'harvest the garden empty before ascending.',
      '**Have breakthrough materials ready.** Excess EXP applies only '
          'as fast as you can click through breakthroughs; missing '
          'consumables are the only thing that can stall a charged '
          'climb.',
    ]),
    Text('Gate day', style: h3),
    bullets([
      'Ascend the moment the gate lifts. Voidbreak Early\'s base band '
          '(0.50) beats Incarnation Late\'s (0.40) — whether you park or '
          'push, you accrue faster inside.',
      'Click through Voidbreak Early — your excess charges its grades '
          'instantly.',
    ]),
    para('**Route by where the server\'s leaders are, not by your current '
        'Strive number.** Two rates compete once you are inside. Parked '
        'at the Early cap you accrue at your base band PLUS your '
        'blessing, with no Strive; pushing live through Middle you '
        'accrue at Middle\'s higher base band × (1 + Strive). Strive is '
        'measured against the server\'s top cultivator, so what matters '
        'is the Strive you would have WHILE in Middle:'),
    Padding(
      padding: const EdgeInsets.only(left: 16),
      child: bullets([
        '**Never be the first into Middle**: while the leaders hold the '
            'Early cap, pushing past them makes you the front — your '
            'Strive drops away and you grind Middle at its flat base '
            'band, which the parked rate can beat.',
        '**Front-runners**: stay parked until the pool covers all '
            '142.1M of Middle, then clear it in one push and arrive at '
            'Voidbreak Late. A one-push spends no live time in Middle, '
            'so lost Strive never enters into it.',
        '**After the leaders push to Late**, trailing players keep '
            'their Strive while climbing Middle live. Once your live '
            'Strive is high enough that the live rate beats the parked '
            'rate, pushing wins; below that, keep parking until your '
            'own pool covers the rest.',
      ]),
    ),
    para('The crossover depends on how much blessing you have live in '
        'Voidbreak, so let the calculator compare the two for your own '
        'absorption and Strive. The net effect: the server bunches at '
        'the Early cap, then peels off front to back.'),
    bullets([
      'Move your streams up a tier: switch to the newly unlocked pill '
          'rank as soon as it\'s sustainable, start leveling the '
          'Spiritual World\'s fresh extractor with the new fruit income, '
          'open the saved jadeslips, and spend the hoarded sect '
          'contribution. The rest of arrival day (laws, Pandemonium, '
          'the trove) is the checklist on [[guide:voidbreak|Guide → '
          'Voidbreak+]].',
    ]),
    Text('By account type', style: h3),
    bullets([
      '**Without the Vase**: your pill stream is exactly the daily '
          'limit, so quality per attempt is everything you control '
          'there — and your prestock leans hardest on passive accrual, '
          'which makes the Virya rush proportionally your biggest '
          'lever. Fruits are your swing resource; bank them well.',
      '**With the Vase (and Mirror)**: refined red pills bypass the '
          'daily limit, so a fed Vase adds stock at face value every '
          'parked day, and the Mirror stacks copies on top. Keep them '
          'fed for the whole gated stretch — artifact energy sitting at '
          'its cap is stock lost ([[ref:artifacts|Reference → '
          'Artifacts & Gems]]).',
      '**Free-to-play**: fruits are the main F2P tool for meeting '
          'timegates, and blessings are progression-gated, not paid — '
          'a built secondary path is worth more than any consumable. '
          'Sustain the best pill quality you can, but a full limit of '
          'a lower quality still beats a half-filled limit of a higher '
          'one.',
      '**Paying**: the two standout paid levers during a gate are the '
          'daily artifact charges and the three elixir packs offered '
          'on entering the new realm — take those at Voidbreak, not '
          'before. The full what\'s-worth-it list is on '
          '[[guide:spending|Guide → Spending]].',
      '**Underdeveloped secondary path**: the blessing tiers need the '
          'secondary at Nascent Soul Late, then Incarnation Middle. '
          'Completion\'s realm-restriction removal exists exactly to '
          'fix this — the moment it lands, divert your '
          'now-unrestricted daily pills to the secondary and '
          'power-level it. Until the tiers land you park at base band '
          'only — well under half the blessed rate — so every day of '
          'delay is expensive.',
    ]),
    para('Set "Timegate lifts in (days)" on the calculator\'s input panel '
        'to compare the gate date against the prestock projection and see '
        'where your stock will land you.'),
  ], footerText: _guideFooterText,
      padding: const EdgeInsets.all(16));
}

Widget _voidbreakPage(BuildContext context) {
  final h3 = Theme.of(context).textTheme.titleMedium;
  Widget para(String s) => docPara(context, s);
  return docPage(context, [
    Text('Voidbreak and beyond', style: h3),
    para('• Arriving with a prestock? When to hold the Early cap vs push '
        'into Middle is on [[guide:timegate|Guide → Timegate]].\n'
        '• Dailies and pill bags reset on ascension — spend before you '
        'break through, same as the Incarnation checklist.\n'
        '• Ascension opens the Spiritual World\'s own Myrimon tier: new '
        'fruit ranks (R6+) and a fresh extractor starting back at Common '
        'quality and bonus level 0. Stage breakthroughs inside the World '
        'keep it; the next reset like this comes at Celestial (Immortal '
        'World). The stockpile-then-eat rhythm repeats at each World.\n'
        '• Strive above 120% is normal here — the 120% cap belongs to the '
        'mortal world; later realms allow overcapping (e.g. keeping your aux '
        'path a minor realm behind your main). The calculator only warns '
        'about >120% readings in mortal-world stages.'),
    // Community-guide material (2026): friend levels/payoffs are the
    // circulating consensus list, cross-checked against the app's own
    // pill/Respira source data where the two overlap.
    Text('Ascension day checklist', style: h3),
    para('The order of operations for the day you break through to '
        'Voidbreak:\n'
        '• Before the breakthrough: don\'t claim dailies or pill bags — '
        'they count against the old realm (same rule as every major '
        'breakthrough).\n'
        '• Hold unredeemed Myrimon Tokens (the cash-shop item, up to '
        '2/week, each worth +1 run) rather than cashing them in on a few '
        'extra mortal-realm fruit — tokens are inventory items you can '
        'bank indefinitely, so redeem them right after ascending for '
        'Voidbreak-tier fruit instead.\n'
        '• Immediately after: unlock laws as soon as possible, buy law '
        'fragments, plant law fruits in the garden, and buy Nature '
        'Mantras ([[guide:garden|Guide → Garden & Laws]] covers layout, '
        'seed planning, and Blitz strategy in full).\n'
        '• Unlock Pandemonium and its three maps.\n'
        '• Claim the treasure trove at Voidbreak, not at Incarnation — '
        'it scales with the realm you claim it in.'),
    Text('Immortal Friends (recommended priorities)', style: h3),
    para('Friends\' levels pay off in cultivation terms at specific '
        'breakpoints. The recommended unlock/level priorities:\n'
        '• Crane Boy to max — +1 daily pill attempt.\n'
        '• Iron Fan 36, Daji 73, Shen Gongbao 117 — +1 daily Respira '
        'attempt each.\n'
        '• Jiang Ziya 116 and Taotie 117 — +3% pill effect each.\n'
        '• Macaque 17 — +3% Respira EXP (already included in your '
        'in-game Respira tooltip).\n'
        '• Also recommended (payoff unknown): White Astra 31, '
        'Princess Adalinda 81, Leizhenzi 129.'),
    para('These attempt/effect bonuses are exactly what the calculator\'s '
        'pill and Respira source pickers model — tick them there once you '
        'hit the breakpoints.'),
  ], footerText: _guideFooterText,
      padding: const EdgeInsets.all(16));
}

// Verified against the owner's own reference layout images
// (layout_8fruit_3vine.png etc., ~/Pictures/omvault-2026-08-11-garden/):
// Law Fruit/Ploughwood are 3-cell L-shapes, Soulrend Vine is a 4-cell
// line+bump shape. This tiling reuses that image's real F1-F8/V1-V3
// pattern, relabeling two Fruit pieces as Ploughwood (same 3-cell shape).
const List<List<String>> _gardenGridLayout = [
  ['F1', 'F1', 'F2', 'V1', 'V1', 'V1'],
  ['F3', 'F1', 'F2', 'F2', 'V1', 'V2'],
  ['F3', 'F3', 'F4', 'F5', 'V2', 'V2'],
  ['V3', 'F4', 'F4', 'F5', 'F5', 'V2'],
  ['V3', 'V3', 'F6', 'P1', 'P1', 'P2'],
  ['V3', 'F6', 'F6', 'P1', 'P2', 'P2'],
];

(Color, Color) _gardenCellColors(String label) {
  if (label.startsWith('F')) {
    return (const Color(0xFFCFE9C9), const Color(0xFF1F5C1F));
  }
  if (label.startsWith('V')) {
    return (const Color(0xFFF2E0B3), const Color(0xFF7A5A13));
  }
  return (const Color(0xFFE2D5F2), const Color(0xFF5B3F8C)); // P
}

// (row, col) of the one cell per plant that carries its label —
// matches where the label actually sits on the source reference image,
// so the rest of each plant's cells render blank (colored, no text)
// and the shape reads from the grid borders instead of a same-label
// blob.
const Set<(int, int)> _gardenGridRoots = {
  (0, 1), (1, 2), (2, 0), (3, 2), (3, 3), (5, 2), // F1-F6
  (0, 4), (2, 5), (4, 1), // V1-V3
  (4, 3), (5, 5), // P1-P2
};

String? _gardenGridAt(int r, int c) {
  if (r < 0 || r >= _gardenGridLayout.length) return null;
  if (c < 0 || c >= _gardenGridLayout[r].length) return null;
  return _gardenGridLayout[r][c];
}

Widget _gardenGridExample(BuildContext context) {
  final labelStyle = Theme.of(context)
      .textTheme
      .labelMedium
      ?.copyWith(fontWeight: FontWeight.bold);
  final captionStyle = Theme.of(context)
      .textTheme
      .bodySmall
      ?.copyWith(color: Theme.of(context).hintColor);
  const edge = BorderSide(color: Color(0xFF333333), width: 2);
  const none = BorderSide.none;
  return Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      // Only the edges between DIFFERENT plants get a border — cells of
      // the same plant share no border between them, so each plant's
      // real L/T shape is outlined instead of every cell looking like
      // an identical blob of same-colored tiles.
      Table(
        defaultColumnWidth: const FixedColumnWidth(44),
        children: [
          for (var r = 0; r < _gardenGridLayout.length; r++)
            TableRow(
              children: [
                for (var c = 0; c < _gardenGridLayout[r].length; c++)
                  Container(
                    height: 40,
                    alignment: Alignment.center,
                    decoration: BoxDecoration(
                      color: _gardenCellColors(_gardenGridLayout[r][c]).$1,
                      border: Border(
                        top: _gardenGridAt(r - 1, c) !=
                                _gardenGridLayout[r][c]
                            ? edge
                            : none,
                        right: _gardenGridAt(r, c + 1) !=
                                _gardenGridLayout[r][c]
                            ? edge
                            : none,
                        bottom: _gardenGridAt(r + 1, c) !=
                                _gardenGridLayout[r][c]
                            ? edge
                            : none,
                        left: _gardenGridAt(r, c - 1) !=
                                _gardenGridLayout[r][c]
                            ? edge
                            : none,
                      ),
                    ),
                    child: Text(
                        _gardenGridRoots.contains((r, c))
                            ? _gardenGridLayout[r][c]
                            : '',
                        style: labelStyle?.copyWith(
                            color:
                                _gardenCellColors(_gardenGridLayout[r][c]).$2)),
                  ),
              ],
            ),
        ],
      ),
      const SizedBox(height: 8),
      Wrap(spacing: 14, runSpacing: 4, children: [
        Text('The labeled cell is where each plant\'s name/timer '
            'actually shows in-game.',
            style: captionStyle),
      ]),
      Wrap(spacing: 14, runSpacing: 4, children: [
        Text('F Law Fruit (6 plants, 3 cells each)', style: captionStyle),
        Text('V Gear-crafting crop (3 plants, 4 cells each)',
            style: captionStyle),
        Text('P Ploughwood (2 plants, 3 cells each)', style: captionStyle),
      ]),
      const SizedBox(height: 16),
    ],
  );
}

Widget _gardenPage(BuildContext context) {
  final h3 = Theme.of(context).textTheme.titleMedium;
  Widget para(String s) => docPara(context, s);
  return docPage(context, [
    Text('Garden & Elemental Laws', style: h3),
    para('The garden grows the fruit that levels up your Elemental '
        'Laws. Elemental Laws give you Law Suppression, an extra PvP '
        'damage bonus with no cap (more on that at the end of this '
        'page).'),
    Text('Unlocking the garden is a simple yes-or-no thing', style: h3),
    para('Can your garden grow enough Law Fruit to hit the daily Blitz '
        'cap? It comes down to one question: do you have enough cells '
        'unlocked, or not. It has nothing to do with how you\'re '
        'spending money elsewhere. Unlock the whole grid **before** '
        'Voidbreak, not after — you can still buy a slot later, but '
        'every day it sits unbought is a day of law levels you can '
        'never get back ([[ref:systems#garden|Reference → World '
        'Systems]] covers the basics this page builds on).'),
    para('The less money you spend, the more this matters. You can\'t '
        'speed up growth for free beyond your daily waterings, and '
        'those alone aren\'t enough to keep a full set of Purple fruit '
        'growing at top speed (more below) — so if you\'re not paying, '
        'having every cell unlocked matters even more for you.'),
    Text('Layout: plants take different amounts of space', style: h3),
    para('Fully unlocked is a 6×6 grid — 36 cells. Law Fruit and '
        'Ploughwood each take up a **3-cell L-shape**. The '
        'gear-crafting crop takes a bigger **4-cell shape** (a '
        'straight line of 3 with one extra cell stuck to the middle). '
        'Since the gear-crafting crop eats more cells per plant, '
        '**there\'s no single number for how many plants fit** — it '
        'depends on what you grow:\n'
        '• **Law Fruit** — feeds Elemental Laws through Blitz (below). '
        'This is the main focus of this page. 3 cells each: a grid of '
        'nothing but Law Fruit holds 12.\n'
        '• **Gear-crafting crop** — steady demand for crafting gear, '
        'and you never run short on seeds for it. 4 cells each: a '
        'grid of nothing but this crop holds only 9.\n'
        '• **Ploughwood** — used to upgrade the Zodiac Relic; only '
        'worth growing if you\'re investing in that relic. 3 cells '
        'each, same as Law Fruit.'),
    para('**Don\'t put the whole grid into Law Fruit** — your seed '
        'supply limits how much Law Fruit you can actually use (more '
        'below), so a handful of Law Fruit slots is enough. Here\'s a '
        'layout that fills every one of the 36 cells with nothing '
        'left over — 6 Law Fruit (3 cells each) + 3 gear-crafting '
        '(4 cells each) + 2 Ploughwood (3 cells each) = 36:'),
    _gardenGridExample(context),
    para('6 Law Fruit is enough to hit the daily Blitz cap. 3 '
        'gear-crafting plants keep you stocked on crafting material. '
        '2 Ploughwood isn\'t much on its own, but it\'s enough once you '
        'add the Zodiac Relic\'s own event rewards on top. Not going '
        'for the Zodiac Relic? Swap those 2 Ploughwood plants for 2 '
        'more Law Fruit instead — they\'re both 3 cells, so it\'s a '
        'clean 1-for-1 swap.'),
    Text('Watering: your free daily time-skip', style: h3),
    para('You get **1 free watering a day** from the garden itself. '
        'The **Sword Trio set bonus** gives you a second one, so **2 '
        'free waterings a day** once you have it. Each watering pushes '
        'every planted seed 3 hours closer to done — all at once, not '
        'one plant at a time. Even with the bonus that\'s only 6 hours '
        'a day for free, which isn\'t enough to keep a Purple-heavy '
        'garden running at full speed. A few other things help:\n'
        '• The **first paid watering each day is very cheap** and '
        'worth buying no matter how little else you spend.\n'
        '• **Companions** can add extra time to each watering, or cut '
        'a plant\'s grow time directly — worth watching for as you '
        'unlock them.\n'
        '• **Pets give you some free time-skip every day** too — only '
        'the amount changes, so don\'t count on a fixed number. Other '
        'daily sources add a bit more on top, same deal.'),
    Text('What to plant: seeds are your real limit, not space', style: h3),
    para('You can count on **20 Law Fruit Seeds a week from the '
        'Sect** — plan around that number only. Other sources exist '
        '(some paid, some random drops) but they\'re too rare to rely '
        'on. Seeds, not garden space or Pot energy, are what actually '
        'limits how much Law Fruit you can grow.'),
    docTable(context, 'Law Fruit tiers',
        ['Tier', 'Grow time', 'Blitz hours', 'Blitz-hours/seed'], [
      ['Green', '4h', '1h', '1.0 (best per grow-hour)'],
      ['Blue', '16h', '3h', '0.75'],
      ['Purple', '40h', '6h', '6.0 (best per seed)'],
      ['Yellow', '88h', '12h', '3.4'],
      ['Red', 'not grown — from the Shears artifact', '14h',
          'doesn\'t count against the cap'],
    ], 'Green wins per hour of grow-time (best if space is your '
        'limit); Purple wins per seed. Since seeds are your real '
        'limit, Purple is the right choice.'),
    para('**Grow Purple by default.** At 6 Blitz-hours per seed, your '
        '20 seeds a week cap you at roughly **17 Blitz-hours a day** '
        '— well under the 120-hour daily cap, and way under what a '
        'garden growing nothing but Green Law Fruit could put out on '
        'paper (about 72–108 a day with Pot energy). Only grow Green '
        'as a top-off, once Purple has already filled the day\'s Blitz '
        'cap and the weekly seed reset is close — its short grow time '
        'uses up spare time without wasting a scarce Purple seed. Skip '
        'Blue and Yellow completely: they\'re both worse than Purple '
        'per seed, and that\'s all that matters once seeds are your '
        'real limit.'),
    para('**In practice:** about 6 Law Fruit plants growing Purple is '
        'enough to use your whole weekly seed supply — that\'s why the '
        'layout above doesn\'t need more than that. Extra slots do '
        'more good on the gear-crafting crop or Ploughwood, since '
        'they don\'t run into the same seed shortage.'),
    para('Even a perfect garden usually can\'t fill the daily Blitz '
        'cap by itself. The daily **tea party** event (and a few '
        'other small daily sources) hands you Law Fruit straight up, '
        'no garden needed — in practice, that\'s what actually fills '
        'the rest of your daily cap, since the garden alone can\'t get '
        'there unless you pay.'),
    Text('Red tier and faster growth: two artifacts', style: h3),
    para('Two Creation Artifacts touch the garden, and it\'s easy to '
        'mix them up — full detail on both is in [[ref:artifacts|'
        'Reference → Artifacts & Gems]]:\n'
        '• **Shears** pushes an already-grown fruit up to Red tier. '
        'Red doesn\'t grow on its own — Shears is the only way to get '
        'it — and its 14-hour Blitz value **doesn\'t count against the '
        '120-hour/day cap**, so it\'s pure bonus on top of your Purple '
        'total.\n'
        '• **Pot** spends energy to speed up growth — 1 energy = 1 '
        'hour off, on any crop including Law Fruit. It\'s the *only* '
        'way to speed up growth besides watering, and it only works '
        'if you have the artifact — the garden itself can\'t do this. '
        'If you get it, it\'s a big help here: a well-fed Pot skips a '
        'lot of grow time every single day, on top of your watering. '
        'Pot energy also lets gear-crafting plants grow up to Yellow '
        'instead of stopping at Purple — but that doesn\'t work on Law '
        'Fruit. Law Fruit\'s top tier is fixed no matter how much Pot '
        'energy you use; you still need Shears to get Red.'),
    Text('Spending fruit: how to level up your Laws', style: h3),
    para('**Blitz** turns one fruit into hours of progress at whatever '
        'your current Learning Speed is for that element — not a '
        'fixed number of Law Points. Use it on whichever of the five '
        'elements (Metal, Wood, Water, Fire, Earth) you\'re focusing '
        'on.\n'
        '• **Spend fruit as you get them instead of saving them up.** '
        'Your Learning Speed goes up as you level, so the same fruit '
        'is worth more Law Points later — but leveling early gets '
        'your speed up sooner, and that pays off on every fruit you '
        'blitz after it. Spending as you go beats saving it all for '
        'later.\n'
        '• **Auto Blitz** turns on once your total Elemental Laws '
        'level (all 5 added up) hits 50 — after that it spends new '
        'fruit for you automatically.\n'
        '• Each element has its own **Learning Speed milestones** '
        '(your rate doubles at set levels) and **Suppression '
        'Resonance** milestones (Boost and Resist bonuses that '
        'alternate, ending in a "Completely Activated" bonus) — the '
        'exact levels and numbers are on the in-game Elemental Laws '
        'screen.\n'
        '• The Suppression Resonance track has two stages per '
        'element, 1000 levels each — the second stage doesn\'t start '
        'until the first one hits 1000. Finishing it everywhere for '
        'every element needs level 2000 each, or **10,000 total '
        'Elemental Laws levels** added up across all five.'),
    Text('The payoff: Law Suppression', style: h3),
    para('This is why all of the above is worth doing. Law '
        'Suppression compares your **total** Elemental Law level (all '
        '5 elements added up) against your opponent\'s — every level '
        'you\'re ahead adds **+0.05% extra damage**, with **no cap**. '
        'You only get the bonus while you\'re ahead, and it only '
        'matters in PvP — nothing in PvE cares about law levels, so '
        'this is purely for dueling and rankings, not something to '
        'chase for farming.'),
    para('Law Points also feed a separate system called **Cosmic '
        'Laws**, from the same pool. Leveling Elemental Laws first '
        'makes both earn faster, so there\'s no real downside — just '
        'do Elemental Laws first.'),
  ], footerText: _guideFooterText,
      padding: const EdgeInsets.all(16));
}

Widget _petsPage(BuildContext context) {
  final h3 = Theme.of(context).textTheme.titleMedium;
  Widget para(String s) => docPara(context, s);
  Widget bullets(List<String> items, [String? note]) => docBullets(context, items, note: note);
  return docPage(context, [
    Text('Pets', style: h3),
    para('Pets are combat companions — they raise your battle rating and '
        'fight beside you. They do not affect cultivation speed or '
        'breakthrough timing. Where they earn their keep is PvE damage '
        'rankings — Demonbend Abyss, Beast Invasion, Monster Hunt, Town '
        'Boss, the tower — which mostly means single-target damage against '
        'one boss. In PvP even the tanky pets only survive a couple of '
        'extra hits, so taunts and stuns rarely get to matter.'),
    para('• Raise ONE pet only. Every rarity step costs more copies and '
        'essences than the last, and activities like Realm Map farming '
        'allow a single pet anyway — a second half-built pet helps '
        'nowhere.\n'
        '• Corporia: Blazelion. Highest single-target damage, and its '
        'debuffs raise the physical damage the enemy takes.\n'
        '• Magicka: Blazelion is the recommended pick too. Babewyrm\'s '
        'debuffs do boost your magic damage, but it needs Fire essences — '
        'by far the scarcest — so a Wyrm usually sits several rarity steps '
        'behind what a Lion would be. Check the planner below with your '
        'own numbers before committing.\n'
        '• Babedeer costs double essences for PvP-only value, and Berpent '
        'only comes from events — neither suits a '
        'focused build.'),
    Text('Exchange and elimination', style: h3),
    para('Pets are bought with rare essences: Blazelion 5 Metal + 5 Wood, '
        'Babewyrm 5 Water + 5 Fire, Babetoise 5 Metal + 5 Earth, Babeox '
        '5 Wood + 5 Water, Babedeer 10 Fire + 10 Earth. Eliminating an '
        'owned pet (Abode → Pet → Eliminate, costs Fateum) returns its '
        'essences in full — Berpent returns 5 Water + 5 Earth — so spare '
        'pets are currency: melt the ones you don\'t raise to buy copies '
        'of the one you do.'),
    const PetPlanner(),
    docTable(context, 'Rarity ladder', ['Rarity', 'Copies', 'Pet realm'], [
      ['Common', '1', 'Primitive'],
      ['Uncommon', '1', 'Primitive'],
      ['Uncommon +1', '1', 'Virtuoso Early'],
      ['Rare', '2', 'Virtuoso Late'],
      ['Rare +1', '3', 'Nascent Soul Early'],
      ['Rare +2', '5', 'Nascent Soul Middle'],
      ['Epic', '8', 'Nascent Soul Late'],
      ['Epic +1', '11', 'Incarnation Early'],
      ['Epic +2', '14', 'Incarnation Middle'],
      ['Legendary', '17', 'Incarnation Late'],
      ['Legendary +1', '21', 'Voidbreak Early'],
      ['Legendary +2', '26', 'Voidbreak Middle'],
      ['Legendary +3', '32', 'Voidbreak Late'],
    ],
        'Copies are cumulative — reaching Legendary consumes 17 in total. '
        'Upgrades also take epic essences (2 by Uncommon +1, 13 in total '
        'by Rare +2), and your pet must reach the listed pet realm first.'),
    Text('Feeding and skills', style: h3),
    docTable(context, 'Pet XP per pill', ['Pill', 'Common', 'Uncommon', 'Rare'], [
      ['R1', '125', '250', '400'],
      ['R2', '625', '1,250', '2,000'],
      ['R3', '1,900', '3,800', '6,080'],
      ['R4', '5,000', '10,000', '16,000'],
      ['R5', '8,000', '16,000', '25,600'],
    ],
        'R1 Cleansing/Aura · R2 Nutrition/Revitalising · R3 Crimson/'
        'Ice Heart · R4 Purity/Dracospirit · R5 Chalcedonius/'
        'Reinvigoration. Epic pills give roughly double Rare.'),
    docTable(context, 'Pet XP per food', ['Food', 'XP'], [
      ['Platycodon', '3,500'],
      ['Siler', '11,000'],
      ['Redarrow Flower', '33,500'],
      ['Dragongall Flower', '54,000'],
      ['Curculigo', '79,000'],
    ]),
    bullets([
      'Feed food and Common/Uncommon pills. Rarity multiplies a pill\'s '
          'pet XP far less than it multiplies the pill\'s value '
          'everywhere else — Rare and better pills are wasted as feed.',
      'Skills unlock with rarity — the second at Uncommon, third at '
          'Rare, fourth at Epic — and level up with Demonroot; buy it '
          'in the market when you see it.',
      'Pets are a low spending priority; heavy investment is whale '
          'territory.',
      'Save the pet system\'s speed-up items for law fruits in your '
          'garden — part of the standard pre-Voidbreak prep.',
    ]),
  ], footerText: _guideFooterText,
      padding: const EdgeInsets.all(16));
}

Widget _auxPage(BuildContext context) {
  final h3 = Theme.of(context).textTheme.titleMedium;
  Widget para(String s) => docPara(context, s);
  return docPage(context, [
    Text('Aux Paths (dual pathing)', style: h3),
    para('Your auxiliary path is a second cultivation class alongside your '
        'main. A good aux adds real fighting power (stats, mana, shields, '
        'crowd control); a bad one adds only small stats. Common picks:'),
    para('• Corporia main → Magicka aux (MP and shields; Literatia not '
        'recommended).\n'
        '• Magicka main → Ghostia aux (MP for shields, extra CC, a ghost '
        'that helps farming).\n'
        '• Swordia main → Magicka aux for sustained damage; Corporia for '
        'burst builds.\n'
        '• Ghostia main → Corporia aux (survivability without eating the '
        'ghost\'s mana); Magicka as the alternative.\n'
        '• Literatia main → Magicka for F2P/low spenders; Corporia or '
        'Ghostia for committed dual-pathers.'),
    para('Aux paths and cultivation: from Voidbreak through Wholeness the '
        'aux enables the Strive overcap play — reach half-step in '
        'Voidbreak, then at Wholeness hold your main at Middle G1 and park '
        'the aux at Early G20, overcapping its gauge (~404% stocked = the '
        'rest of Wholeness covered; how overcap percentages read is on '
        '[[guide:timegate|Guide → Timegate]]), then level the main '
        'normally keeping the aux a minor '
        'realm behind. An Early path always counts below a Middle path for '
        'Strive, so the bonus keeps applying. This is why the calculator\'s '
        '120% Strive warning only applies to mortal-world stages.'),
    para('The calculator models one path at a time — enter the numbers for '
        'whichever path you\'re actively cultivating.'),
  ], footerText: _guideFooterText,
      padding: const EdgeInsets.all(16));
}

// Manual ratings/tier advice are a community tier list (2026-07 sheet);
// R4–R9 node values cross-checked against the Vault book tables —
// see docs/knowledge/technique-books.md for provenance and the full
// R10+ node data.

Widget _techniquesPage(BuildContext context) {
  final h3 = Theme.of(context).textTheme.titleMedium;
  Widget para(String s) => docPara(context, s);
  return docPage(context, [
    Text('Technique manuals: what to buy', style: h3),
    para('Every manual carries bonus nodes — one on learning, more at '
        'tier breakpoints (Tiers 3/6/9, adding 12 and 15 at higher '
        'ranks). The nodes that change your breakthrough time are the '
        'cultivation ones — Base Abode Aura, pill effect and attempts, '
        'Respira effect and attempts — the same bonuses the Vault '
        'tracks (record your books there and the calculator fills '
        'itself). Everything else is combat stats, mostly PvP. '
        'Ratings grade cultivation-speed value only: S+ must-buy, tier '
        'deep · S core speed manual · A solid speed value · B a node '
        'or two worth a stop · C combat or utility only (the note '
        'names its niche). How deep to go is judgment; the node values '
        'are the manuals\' own numbers.'),
    para('• Buy breakpoints, not tiers: a manual is worth reaching its '
        'next good node — stopping between nodes buys only raw stats.\n'
        '• Cultivation nodes come first: an abode-aura or pill node pays '
        'out every day forever; a PvP line only pays when you fight.\n'
        '• From R11 on, elemental-law learning speed joins the top of '
        'the list — law levels are a time-integral, so speed compounds '
        '([[ref:systems|Reference → World Systems]] covers laws).'),
    Text('R4–R9, rank by rank', style: h3),
    para('The full manual-by-manual breakdown (every book\'s rating and '
        'why) is in the table below. A few cross-rank patterns worth '
        'knowing going in: the rank\'s top-rated (S/S+) manual is almost '
        'always worth tiering all the way, mid picks (A/A−/B) are worth '
        'stopping at whichever node the "why" column names, and every '
        'rank has 1–2 pure-PvP books (C) that don\'t move your '
        'cultivation speed at all — skip those unless you specifically '
        'need the combat stat.'),
    Text('R10 and beyond', style: h3),
    para('Everything at R10 is worth taking — Immortal Ascension '
        '(the rank\'s only Universal book) to Tier 12 for its +1 daily '
        'pill attempt; Tier 15 beyond that is stats-only. From R11 the '
        'ranks settle into a '
        'pattern: each has a law-speed manual (rated S across the '
        'board), usually an abode-aura or Respira manual, and a PvP '
        'manual. New node families appear here: elemental-law learning '
        'speed, Qiyun efficiency, and divine/demonic damage.'),
    // Mirror of docs.py manual_rows — same rows, same order.
    docTable(context, 'Every Universal manual, rated',
        ['Rank', 'Manual', 'Rating', 'Why'],
        [
          ['R1', 'Longevity', 'A', 'Aura at learn, then a Respira attempt'],
          ['R2', 'Energy Unification', 'B', 'Small Respira and aura nodes'],
          ['R2', 'Rejuvenation', 'B', 'Small aura node, small pill node'],
          ['R3', 'Cosmic Power', 'A+',
           'Respira attempt at learn, effect after'],
          ['R3', 'Lifeboom', 'A', 'Pill effect, then a Respira attempt'],
          ['R3', 'Yang', 'C', 'Crit and monster-damage PvE pick'],
          ['R4', 'Astrology', 'S', 'Aura, Respira effect, then pill attempt'],
          ['R4', 'Golden Core', 'A', 'Pill effect stacked twice plus Respira'],
          ['R4', 'Focus', 'B', 'One small pill node, then Sense filler'],
          ['R4', 'Soul Drain', 'C', 'Monster-farming pick'],
          ['R5', 'Ninefall', 'A', 'Aura twice plus a pill node'],
          ['R5', 'Bloodization', 'B',
           'One good aura node behind combat filler'],
          ['R5', 'Solarics', 'B', 'One aura node, rest combat filler'],
          ['R5', 'Taiyin Meridian', 'B',
           'Single Respira node amid combat lines'],
          ['R5', 'Lunarics', 'C', 'Control-stacking PvP pick'],
          ['R6', 'Yin\'s Grasp', 'S+', 'Aura, Respira +5%, then pill attempt'],
          ['R6', 'Dragon Flight', 'A', 'Pill +2% and aura +2%, then filler'],
          ['R6', 'Unbound Blade', 'B', 'Lone aura +3%, rest ability PvP'],
          ['R6', 'Conflagration', 'B', 'Single aura +3% at T9, rest PvP'],
          ['R6', 'Lion\'s Roar', 'B', 'Respira and Spiritium early, then stop'],
          ['R6', 'Thunder Winds', 'C', 'Crit-stat combat book'],
          ['R7', 'Floral Essence', 'S+',
           'All-speed tree ending in pill attempt'],
          ['R7', 'Purify & Cleanse', 'S+',
           'Instant Respira on learn, attempts later'],
          ['R7', 'Great Yang Manual', 'S', 'Aura, Respira +5%, pill +4% ladder'],
          ['R7', 'Aqua Power', 'C', 'Ability PvP; Spiritium +4% tail'],
          ['R7', 'Bulwark', 'C', 'Control resist and PvE defense'],
          ['R7', 'Dragonsound', 'C', 'Control plus monster damage; PvE pick'],
          ['R7', 'Ninefall Hoarfrost', 'C', 'Magic-side PvP defense pick'],
          ['R7', 'Sunset Halberd Dance', 'C', 'Physical-path PvP pick'],
          ['R7', 'Vajra', 'C', 'Relic PvP niche'],
          ['R8', 'Chroma', 'S+', 'Both attempt nodes; every node speed'],
          ['R8', 'Astral Arcanum', 'S', 'Pill early, aura twice at T9/T12'],
          ['R8', 'Cauldron Refinement', 'B', 'Respira +3% at T3, then combat'],
          ['R8', 'Moon Meru', 'B', 'Control filler until Respira +10% at T12'],
          ['R8', 'Tao of Taiqing', 'B',
           'Combat tree until lone aura +4% at T12'],
          ['R8', 'Zixiao Sutra', 'B', 'Pill and aura cheap early, then stop'],
          ['R8', 'Dracophant', 'C', 'Monster and relic defense pick'],
          ['R8', 'No-Thought Sutra', 'C', 'Paralysis stack for PvP'],
          ['R8', 'Origin Scripture', 'C', 'Physical PvP defense pick'],
          ['R9', 'Harvest God Secret', 'S+',
           'Aura three times, then a pill attempt'],
          ['R9', 'Honored Origin', 'A−', 'Aura on learn, +3% again at T9'],
          ['R9', 'Heartless', 'B', 'Physical PvP until Respira +10% at T12'],
          ['R9', 'Laws of Nature', 'B',
           'Pill unlock at learn; Respira +10% at T12'],
          ['R9', 'Divine Water', 'C', 'Magic-path PvP pick'],
          ['R9', 'Eight-Nine Method', 'C', 'Relic-ability defense pick'],
          ['R9', 'Gold Smasher', 'C', 'Relic-control PvP pick'],
          ['R9', 'Mara Incarnation', 'C', 'Physical ability-PvP pick'],
          ['R9', 'Seven Star Blade', 'C', 'Relic PvP pick'],
          ['R9', 'Way of Creation', 'C', 'Relic and ability hybrid PvP'],
          ['R9', 'Wordless Scripture', 'C', 'Control-stacking utility pick'],
          ['R9', 'Zhurong Mantra', 'C', 'Magic ability-PvP pick'],
          ['R10', 'Immortal Ascension', 'S+', 'Must-take — worth tiering to 12 for +1 daily pill attempt'],
          ['R11', 'Thunder Lord Incantation', 'S', 'Every node is law speed'],
          ['R11', 'Heavenly Rhythm', 'S',
           'All Respira: attempt mid-tree, effect around it'],
          ['R11', 'Pure Mysterious', 'A+', 'Aura twice early, Fire law capstone'],
          ['R11', 'Square Inch Script', 'B',
           'One deep Respira node amid PvP filler'],
          ['R12', 'Cloud Satchel', 'S', 'Every node is law speed'],
          ['R12', 'Star Blade', 'A−', 'Two law nodes, rest combat filler'],
          ['R13', 'Pure Starlight', 'A', 'Early Respira, ends in two law nodes'],
          ['R13', 'Five Thunder Mantra', 'B',
           'Aura at unlock, then all-PvP filler'],
          ['R14', 'Yin Yang Harmony', 'S', 'Every node is law speed'],
          ['R14', 'Chaos Origin', 'S',
           'All Respira: attempt mid-tree, effect around it'],
          ['R14', 'Samsara Scripture', 'B',
           'One early aura node, Spiritium tail'],
          ['R15', 'Celestial Cloud Scripture', 'S', 'Every node is law speed'],
          ['R15', 'Taisu Scripture', 'A', 'Aura at learn plus three law nodes'],
          ['R15', 'Heaven Execution', 'C', 'PvP ladder only'],
          ['R16', 'Immortality Cloud', 'S', 'Every node is law speed'],
          ['R16', 'Supreme Heavenly Tao', 'A',
           'Respira attempt mid-tree, then combat'],
          ['R16', 'Pure Jade One', 'B+', 'Aura twice up front, then pure PvP'],
          ['R17', 'Demonbane Technique', 'B',
           'One Qiyun node early, rest divine combat'],
          ['R17', 'Zen Lotus Technique', 'B',
           'Demonic mirror: same lone Qiyun node'],
          ['R18', 'Magnetic Light Maneuver', 'A',
           'Qiyun twice, then Respira +7%'],
          ['R18', 'Sanskrit Chant', 'C', 'Crit-stacking PvP pick'],
          ['R19', 'Draconic Demon Taming', 'B',
           'One Qiyun node, then stat filler'],
          ['R19', 'Jade Reincarnation Technique', 'C',
           'Demon damage and stat lines only'],
          ['R20', 'Book of Forgotten Wishes', 'C',
           'Nothing stands out — take what you like'],
          ['R21', 'Book of Necromancy', 'B', 'A small Qiyun node amid filler'],
          ['R21', 'Book of Meditation', 'C', 'Control and stat lines, no speed'],
        ],
        'Manuals above R9 aren\'t on the Vault shelves yet — add their '
        'pill/Respira bonuses as custom rows in the calculator\'s '
        'source pickers so projections see them.'),
  ], footerText: _guideFooterText,
      padding: const EdgeInsets.all(16));
}

// Spending advice is community consensus (2026 guide + Discord);
// BR figures are era-specific estimates, not client data.

Widget _spendingPage(BuildContext context) {
  final h3 = Theme.of(context).textTheme.titleMedium;
  Widget para(String s) => docPara(context, s);
  return docPage(context, [
    Text('Spending (if you pay at all)', style: h3),
    para('None of this is a recommendation to spend — it\'s an answer '
        'to "if I do, what\'s actually worth it?" '
        'All of it is subjective.'),
    Text('Priorities', style: h3),
    para('• Permanent one-time buys first: the watering curio set and the '
        'permanent passes beat any consumable pack — you buy them once '
        'and they pay out forever.\n'
        '• The three elixir packs on reaching a new realm are among the '
        'best consumable value in the game — early tolerance tiers make '
        'them worth the most ([[ref:elixirs#expelixirs|Reference → Elixirs & Stat '
        'Pills]]).\n'
        '• The daily 30 Fateum/Destium artifact charges are among the '
        'cheapest EXP money buys.\n'
        '• Law fruit packs are atrocious value — do not buy them.\n'
        '• Heavy pet investment is whale territory '
        '([[guide:pets|Guide → Pets]]).'),
    Text('Timegate BR targets (era-specific estimates)', style: h3),
    para('Rough battle-rating bands players report aiming for at each '
        'realm\'s timegate content, by spending tier (F2P → heavy). These '
        'drift with every era — treat as orientation only:\n'
        '• Incarnation: 800m – 2b+\n'
        '• Voidbreak: 9b – 25b+\n'
        '• Wholeness: 45b – 100b+'),
    Text('Creation Artifacts (relic summon)', style: h3),
    para('Guaranteeing all 8 with cash runs \$20k+ '
        '([[ref:artifacts#summon|Reference → Artifacts & Gems]]) — a '
        'whale number, not a realistic plan for most players. Pick '
        'whichever relic still feels like a reasonable spend for your '
        'own means, pay cash up to that point, then stop and switch to '
        'free daily draws instead of buying further.\n\n'
        'Past that point, don\'t spend draws as they come in — bank '
        'them. Every draw carries the same independent instant-win shot '
        '([[ref:artifacts#summon|Reference → Artifacts & Gems]]) '
        'regardless of points banked, so a large stockpile dumped at '
        'once has real odds of winning a relic for free — roughly 50% '
        'at ~280 banked draws, 90% at ~920. A miss costs nothing extra — '
        'the points still count toward the next relic either way.\n\n'
        'When picking which relic to aim a stockpile at, target '
        'whichever one has the biggest jump from the relic before it, '
        'not necessarily the last one on your list — the size of that '
        'specific step is what a win actually saves, and it isn\'t '
        'always the priciest relic overall.'),
  ], footerText: _guideFooterText,
      padding: const EdgeInsets.all(16));
}
