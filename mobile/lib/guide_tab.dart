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
  return docPage(context, [
    Text('Choosing your path', style: h3),
    para('The first decision in the game. It\'s less permanent than it '
        'looks — Path Switch exists from Foundation (7-day cooldown, '
        'rising Fateum cost) — but your path shapes combat style, gear '
        'priorities, and which elixirs/pets/aux picks fit. This summary '
        'is subjective, and opinion is genuinely mixed — '
        'treat it as orientation, not law.'),
    Text('The five paths', style: h3),
    para('• Swordia (HP/physical) — highest sustained DPS in the game; '
        'strong in both PvP and PvE bossing. Very reliant on its relics '
        '(flying swords). The safe strong pick.\n'
        '• Corporia (HP/physical) — burst physical damage with a '
        'death-immunity ultimate; not relic-reliant. Weaker early, much '
        'stronger later; PvE is its weak side — a PvP-leaning pick.\n'
        '• Magicka (MP/magic) — AoE damage, lots of shields and crowd '
        'control. Good at PvE farming and holds up in PvP, though it '
        'takes more piloting than Swordia. The flexible pick.\n'
        '• Ghostia (MP/magic) — summons a ghost companion that taunts '
        'and deals damage; unblockable-paralyze ultimate. Very '
        'relic-reliant. Strong PvE and dueling.\n'
        '• Literatia (MP/magic) — the newest path: builds erudition to '
        'unleash a high-burst mana dump (Literal Reality). Weak early in '
        'the mortal world and scales up later; good AoE farm and PvE, '
        'PvP still unproven.'),
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
        '• Claim your Aura Gem before its storage caps (18–32 h by rarity) '
        '— once full it stops accruing.\n'
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
        '([[ref:elixirs#tolerance|Reference → Elixirs & Stat Pills]]).'),
  ], footerText: _guideFooterText,
      padding: const EdgeInsets.all(16));
}

Widget _incarnationPage(BuildContext context) {
  final h3 = Theme.of(context).textTheme.titleMedium;
  Widget para(String s) => docPara(context, s);
  return docPage(context, [
    Text('Incarnation', style: h3),
    para('• The extractor endgame for the mortal world: open Aura Extractor '
        '→ Boost and max its tracks — Quality first, then Cultivation, then '
        'Gush (High Rank last). Keep stockpiling fruits instead of eating '
        'them: every extractor level makes each fruit worth more, and at '
        'Mortal World rank the extractor adds +50% base fruit EXP while '
        'you\'re at the server\'s highest Stage.\n'
        '• Eat the stockpile before the realm timegate — fruits lose 50% of '
        'their EXP once the next realm\'s timegate passes — or on the last '
        'day before your own breakthrough, whichever comes first. (Full '
        'fruit math: [[ref:myrimon#fruits|Reference → Myrimon & Extractor]].)\n'
        '• Before breaking through to Voidbreak: spend all pills and Respira '
        '(they reset), don\'t claim daily pill bags until after ascension, '
        'and spend Fatevillion shop tokens beforehand — that shop resets on '
        'breakthroughs too.\n'
        '• On the ascension itself you\'ll be offered three real-money '
        'elixir packs — if you spend at all, these are among the best value '
        'in the game ([[ref:elixirs#expelixirs|Reference → Elixirs & Stat Pills]] '
        'explains why the '
        'early tolerance tiers make them worth the most).\n'
        '• Keep battle rating growing all era — the Ascension Virya '
        'blessing tiers gate on Myrimon Wonder boss clears (Amethyst '
        'Fiend, Jade-Eyed Lion). Reaching the gate weeks with the bosses '
        'unkillable means blessings locked exactly when they matter '
        'most.\n'
        '• The run-up to the realm timegate — prestocking past 100%, the '
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
        'together:\n'
        '• Completion — reach Incarnation Late 100% and break through into '
        'Incarnation (Perfected). A full gauge alone is not enough: the '
        'blessing system does not start until this breakthrough is taken. '
        'It is not blocked by the timegate — the gate blocks only the '
        'ascension into Voidbreak — so take it the moment the gauge '
        'fills. It removes realm restrictions on cultivation pills '
        '(higher-rank pills can feed a lower secondary path; '
        'rank-appropriate pills already work there without it) and '
        'unlocks pill auto-transmogrification, which lets breakthrough '
        'pills of one path be used on the other (physical ↔ magical). '
        'Together these make the secondary rush below possible.\n'
        '• Perfection — primary at Incarnation (Perfected), secondary at '
        'Nascent Soul Late, clear Amethyst Fiend in Myrimon Wonder: +20 '
        'points absorption in your current Stage.\n'
        '• Perfect — secondary at Incarnation Middle, clear Jade-Eyed '
        'Lion: a second absorption tier, plus an "Absorption Ratio Before '
        'Voidbreak Middle" line that comes into play once you are in '
        'Voidbreak.'),
    para('Secondary requirements are satisfied on REACHING the named '
        'half-step, not completing it. On the Incarnation base band a live '
        '+20 points already lifts your parked rate well above the raw '
        'passive rate, so the rush is worth prioritising. How the tiers '
        'carry into Voidbreak depends on your build — read your in-game '
        'absorption there and enter it into the calculator rather than '
        'assuming a fixed total.'),
    Text('Preparing while gated', style: h3),
    para('• Cap Incarnation early and take the Completion breakthrough at '
        'once. Days spent climbing to the cap are not stocking days, and '
        'the gauge filling by itself starts nothing. Top off with banked '
        'fruits if the gauge won\'t fill on streams alone.\n'
        '• Rush the Virya tiers immediately after: divert your daily '
        'pills to the secondary path (passive stays on the primary) — '
        'Nascent Soul Late unlocks the first absorption tier, Incarnation '
        'Middle the next. The earlier the tiers land, the longer they lift '
        'your parked accrual. Clear the two Myrimon Wonder bosses ahead of '
        'time so they never hold a tier hostage.\n'
        '• Fill every flat stream, every day. Never leave pill attempts '
        'unused: pill EXP roughly halves per quality step, so a full '
        'limit of the next quality down matches a half-filled limit of '
        'the one above.\n'
        '• Eat the fruit bank before the gate opens — the banking and 50% '
        'rules are on [[guide:incarnation|Guide → Incarnation]]. Leftovers '
        'don\'t survive the ascension anyway: the mortal extractor resets '
        'at the World boundary and auto-consumes them at pre-upgrade '
        'rates.\n'
        '• Hoard for the arrival — the parked weeks are the window: sect '
        'contribution (~13–14k) for the new realm\'s blueprints and '
        'formulas; Fateum and Fate Tokens, Revealstones, plant speed-ups; '
        'trove jadeslips for Cosmic Atlas, Ancient Treasure and Pet Index '
        '— their contents re-tier on realm breakthrough, so opened on '
        'arrival they pay out at the new realm\'s tier. Don\'t run this '
        'hoard between gates: realm gates are months apart, and resources '
        'sat on for months are power you didn\'t use.\n'
        '• Spend what dies with the realm: beyond the pre-breakthrough '
        'rules on the Incarnation page, spend Ability Knowledge and '
        'harvest the garden empty before ascending.\n'
        '• Have breakthrough materials ready. Excess EXP applies only as '
        'fast as you can click through breakthroughs; missing consumables '
        'are the only thing that can stall a charged climb.'),
    Text('Gate day', style: h3),
    para('• Ascend the moment the gate lifts. Voidbreak Early\'s base '
        'band (0.50) beats Incarnation Late\'s (0.40) — whether you park '
        'or push, you accrue faster inside.\n'
        '• Click through Voidbreak Early — your excess charges its grades '
        'instantly.\n'
        '• Route by where the server\'s leaders are, not by your current '
        'Strive number. Two rates compete once you are inside. Parked at '
        'the Early cap you accrue at your base band PLUS your blessing, '
        'with no Strive; pushing live through Middle you accrue at '
        'Middle\'s higher base band × (1 + Strive). Strive is measured '
        'against the server\'s top cultivator, so what matters is the '
        'Strive you would have WHILE in Middle:\n'
        '   – Never be the first into Middle: while the leaders hold the '
        'Early cap, pushing past them makes you the front — your Strive '
        'drops away and you grind Middle at its flat base band, which the '
        'parked rate can beat.\n'
        '   – Front-runners: stay parked until the pool covers all 142.1M '
        'of Middle, then clear it in one push and arrive at Voidbreak '
        'Late. A one-push spends no live time in Middle, so lost Strive '
        'never enters into it.\n'
        '   – After the leaders push to Late, trailing players keep their '
        'Strive while climbing Middle live. Once your live Strive is high '
        'enough that the live rate beats the parked rate, pushing wins; '
        'below that, keep parking until your own pool covers the rest.\n'
        'The crossover depends on how much blessing you have live in '
        'Voidbreak, so let the calculator compare the two for your own '
        'absorption and Strive. The net effect: the server bunches at the '
        'Early cap, then peels off front to back.\n'
        '• Move your streams up a tier: switch to the newly unlocked pill '
        'rank as soon as it\'s sustainable, start leveling the Spiritual '
        'World\'s fresh extractor with the new fruit income, open the '
        'saved jadeslips, and spend the hoarded sect contribution. The '
        'rest of arrival day (laws, Pandemonium, the trove) is the '
        'checklist on [[guide:voidbreak|Guide → Voidbreak+]].'),
    Text('By account type', style: h3),
    para('• Without the Vase: your pill stream is exactly the daily '
        'limit, so quality per attempt is everything you control there — '
        'and your prestock leans hardest on passive accrual, which makes '
        'the Virya rush proportionally your biggest lever. Fruits are '
        'your swing resource; bank them well.\n'
        '• With the Vase (and Mirror): refined red pills bypass the daily '
        'limit, so a fed Vase adds stock at face value every parked day, '
        'and the Mirror stacks copies on top. Keep them fed for the whole '
        'gated stretch — artifact energy sitting at its cap is stock lost '
        '([[ref:artifacts|Reference → Artifacts & Gems]]).\n'
        '• Free-to-play: fruits are the main F2P tool for meeting '
        'timegates, and blessings are progression-gated, not paid — a '
        'built secondary path is worth more than any consumable. Sustain '
        'the best pill quality you can, but a full limit of a lower '
        'quality still beats a half-filled limit of a higher one.\n'
        '• Paying: the two standout paid levers during a gate are the '
        'daily artifact charges and the three elixir packs offered on '
        'entering the new realm — take those at Voidbreak, not before. '
        'The full what\'s-worth-it list is on [[guide:spending|Guide → '
        'Spending]].\n'
        '• Underdeveloped secondary path: the blessing tiers need the '
        'secondary at Nascent Soul Late, then Incarnation Middle. '
        'Completion\'s realm-restriction removal exists exactly to fix '
        'this — the moment it lands, divert your now-unrestricted daily '
        'pills to the secondary and power-level it. Until the tiers land '
        'you park at base band only — well under half the blessed rate — '
        'so every day of delay is expensive.'),
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
        '• Immediately after: unlock laws as soon as possible, buy law '
        'fragments, plant law fruits in the garden, and buy Nature '
        'Mantras.\n'
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

Widget _petsPage(BuildContext context) {
  final h3 = Theme.of(context).textTheme.titleMedium;
  Widget para(String s) => docPara(context, s);
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
    para('• Feed food and Common/Uncommon pills. Rarity multiplies a '
        'pill\'s pet XP far less than it multiplies the pill\'s value '
        'everywhere else — Rare and better pills are wasted as feed.\n'
        '• Skills unlock with rarity — the second at Uncommon, third at '
        'Rare, fourth at Epic — and level up with Demonroot; buy it in '
        'the market when you see it.\n'
        '• Pets are a low spending priority; heavy investment is whale '
        'territory.\n'
        '• Save the pet system\'s speed-up items for law fruits in your '
        'garden — part of the standard pre-Voidbreak prep.'),
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
    para('• R4 — all three earn their cost: Golden Core (+2%/+3% pill '
        'effect), Astrology (+3% Respira effect, then +1 daily pill '
        'attempt), and Focus at least for its +1% pill effect unlock.\n'
        '• R5 — Ninefall is the pick (abode-aura nodes bracketing +2% '
        'pill effect). Bloodization up to its +3% aura node. Solarics: '
        'the aura node for everyone; physical paths continue for the '
        'P.ATK.\n'
        '• R6 — Yin\'s Grasp is the standout, take it to Tier 9: +5% '
        'Respira effect, then +1 daily pill attempt. Conflagration and '
        'Unbound Blade stack PvP lines and land Base Abode Aura +3% at '
        'Tier 9. Dragon Flight to Tier 6 (+2% pill effect, +2% aura).\n'
        '• R7 — Floral Essence and Purify & Cleanse are the rank\'s '
        'best, every node good: Floral Essence stacks Respira, pill '
        'effect and +1 pill attempt; Purify & Cleanse is the Respira '
        'manual (instant-complete on learning, +4%/+7% effect, +1 '
        'attempt). Great Yang Manual: weak unlock, good everything '
        'else (+2% aura, +5% Respira, +4% pill effect). Aqua Power (to '
        'Tier 6), Ninefall Hoarfrost and Sunset Halberd Dance are the '
        'PvP picks.\n'
        '• R8 — Chroma is the must-buy: pill effect, +1 Respira '
        'attempt, +4% aura, +1 pill attempt. Astral Arcanum right '
        'behind it (pill effect plus double aura nodes). Tao of '
        'Taiqing: top pick for magic paths — PvP lines ending in +4% '
        'aura. Origin Scripture: the physical-path all-rounder. Zixiao '
        'Sutra: first two nodes only (+1% pill effect, +2% aura).\n'
        '• R9 — Harvest God Secret is the cultivation manual of the '
        'rank: +3% Respira, +3%/+4% aura, +1 pill attempt. Honored '
        'Origin: bought for its aura nodes, the control stats are a '
        'bonus. Divine Water (magic) and Heartless (physical, ends in '
        '+10% Respira) are the PvP picks. Laws of Nature: the +1% pill '
        'effect unlock early; Tier 12 adds +10% Respira effect.'),
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
        'them worth the most ([[ref:elixirs#tolerance|Reference → Elixirs & Stat '
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
  ], footerText: _guideFooterText,
      padding: const EdgeInsets.all(16));
}
