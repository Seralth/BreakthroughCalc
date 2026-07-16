/// Stage-by-stage cultivation guide, one sub-tab per realm band.
///
/// One ordered [guideSections] registry drives the slug->index map, the
/// TabController length, the Tab labels and the TabBarView children, so a
/// section can only be added or moved in one place.
library;

import 'package:flutter/material.dart';

import 'doc_nav.dart';
import 'doc_widgets.dart';

class GuideSection {
  final String slug;
  final String title;
  final WidgetBuilder page;
  const GuideSection(this.slug, this.title, this.page);
}

const List<GuideSection> guideSections = [
  GuideSection('paths', 'Choosing a Path', _choosingPage),
  GuideSection('routine', 'Daily Routine', _routinePage),
  GuideSection('novice', 'Novice–Foundation', _novicePage),
  GuideSection('virtuoso', 'Virtuoso', _virtuosoPage),
  GuideSection('nascent', 'Nascent Soul', _nascentPage),
  GuideSection('incarnation', 'Incarnation', _incarnationPage),
  GuideSection('voidbreak', 'Voidbreak+', _voidbreakPage),
  GuideSection('pets', 'Pets', _petsPage),
  GuideSection('aux', 'Aux Paths', _auxPage),
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
        'colors share one attempt pool; Vase reds are exempt).\n'
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
        '([[ref:myrimon#verified|Reference → Myrimon & Extractor]]).'),
    Text('Before every major breakthrough', style: h3),
    para('• Spend all daily pills and Respira attempts — they reset on the '
        'breakthrough.\n'
        '• Eat the fruit stockpile — the extractor resets to Common on a '
        'main-Stage breakthrough and auto-consumes leftovers at pre-upgrade '
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
        'early tolerance tiers make them worth the most).'),
  ], footerText: _guideFooterText,
      padding: const EdgeInsets.all(16));
}

Widget _voidbreakPage(BuildContext context) {
  final h3 = Theme.of(context).textTheme.titleMedium;
  Widget para(String s) => docPara(context, s);
  return docPage(context, [
    Text('Voidbreak and beyond', style: h3),
    para('• Dailies and pill bags reset on ascension — spend before you '
        'break through, same as the Incarnation checklist.\n'
        '• Each major realm from here has its own Myrimon tier: a new fruit '
        'rank (R6+) and a fresh extractor starting back at Common quality '
        'and bonus level 0. The stockpile-then-eat rhythm repeats every '
        'realm.\n'
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
        'fight beside you in PvE and PvP. They do NOT affect cultivation '
        'speed or breakthrough timing, which is why this calculator has no '
        'pet inputs.'),
    para('• Upgrade one pet only — upgrades get very expensive, and a '
        'second half-built pet is worth far less than one strong one.\n'
        '• Which one: Blazelion for physical-damage paths (Corporia, '
        'Swordia); Babeox for magical paths (Magicka, Ghostia, '
        'Literatia).\n'
        '• Pet skills come from Demonroot — buy it in the market when you '
        'see it.\n'
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
        'Voidbreak, then at Wholeness hold your main at Middle G1 and pump '
        'the aux at Early G20 until absorption overcaps (~404% at Wholeness '
        'completion), then level the main normally keeping the aux a minor '
        'realm behind. An Early path always counts below a Middle path for '
        'Strive, so the bonus keeps applying. This is why the calculator\'s '
        '120% Strive warning only applies to mortal-world stages.'),
    para('The calculator models one path at a time — enter the numbers for '
        'whichever path you\'re actively cultivating.'),
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
