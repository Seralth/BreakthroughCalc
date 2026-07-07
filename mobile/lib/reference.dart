import 'package:flutter/material.dart';

import 'engine.dart';

/// Read-only reference tables + primer, rendered from the same engine data so
/// the numbers can't drift from the calculations. Organized as scrollable
/// sub-tabs: mechanics first, then a stage-by-stage progression walkthrough.
class ReferenceTab extends StatelessWidget {
  final Engine engine;
  final List<dynamic> catalog;
  const ReferenceTab({super.key, required this.engine, required this.catalog});

  @override
  Widget build(BuildContext context) {
    final d = engine.data;
    final t = Theme.of(context);
    final h3 = t.textTheme.titleMedium;
    final muted = TextStyle(color: t.hintColor, fontSize: 12);

    Widget para(String s) =>
        Padding(padding: const EdgeInsets.symmetric(vertical: 6), child: Text(s));

    Widget table(String title, List<String> headers, List<List<String>> rows, [String? note]) {
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

    Widget page(List<Widget> children) =>
        ListView(padding: const EdgeInsets.all(12), children: children);

    final pillXp = d['pill_xp'] as Map<String, dynamic>;
    final vaseCost = d['vase_energy_cost'] as Map<String, dynamic>? ?? {};
    final gems = d['gem_bonus'] as Map<String, dynamic>;

    final basics = page([
      Text('How cultivation works', style: h3),
      para('Cultivation EXP accrues one tick every 8 seconds (a "Cosmoapsis"). '
          'Cultivation Speed = Abode Aura × Absorption Ratio — all read from the '
          'in-game Cultivation Bonus screen. Progression is Stage → Half-step → Grade, '
          'each grade needing a fixed EXP amount.'),
      Text('Core formulas', style: h3),
      para('• Cultivation Speed = Abode Aura × Absorption Ratio\n'
          '• Abode Aura = 130 × (1 + total aura bonus) — base 130 holds for '
          'Connection through Incarnation\n'
          '• Cultivation ticks every 8 seconds (one Cosmoapsis)\n'
          '• Absorption = stage base × (1 + Strive); Strive unlocks at Nascent Soul '
          'and fades as you approach your server\'s #1\n'
          '• Pill EXP = base × (1 + pill effect + quality star mark [+ Vase star/skin '
          'for reds])'),
      Text('Strive', style: h3),
      para('From Nascent Soul, Strive multiplies absorption and grows the further you '
          'are behind server #1, fading as you catch up. Set "Server #1 Stage" to model '
          'the drop-off. It does not change your current-position time (it cancels out).'),
      Text('Crit variance (best / worst)', style: h3),
      para('Respira crits and fruit gushes are random, so estimates carry a ~90% best/worst '
          'band. Because these are sums of many independent rolls, luck averages out: the band '
          'is widest on short estimates and tightens over long horizons. Fruit gushes also have '
          'a pity floor (every 6th fruit is a guaranteed gush), narrowing the fruit side.'),
      Text('Timegates', style: h3),
      para('Timegates pace whole-server progression; Myrimon is the main F2P tool for '
          'meeting them.'),
      Text('Tips for using the calculator', style: h3),
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
    ]);

    final pills = page([
      Text('Daily pills', style: h3),
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
              (e.value[2] as num).toString(),
              (e.value[1] as num).toString(),
              (e.value[0] as num).toString(),
              (e.value[3] as num).toString(),
            ]
        ],
        'Confirmed against in-game tooltips. Pill-effect bonuses add as percentage '
        'points and multiply the base once.',
      ),
      if (catalog.isNotEmpty)
        table(
          'Pill Effect sources',
          ['Source', 'Bonus'],
          [
            for (final s in catalog.cast<Map<String, dynamic>>())
              [
                s['name'] as String,
                ((s['percent'] as num?) ?? 0) == 0 ? 'varies' : '${s['percent']}%'
              ]
          ],
          'All sources stack additively.',
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
    ]);

    final myrimon = page([
      Text('Myrimon Fruits', style: h3),
      para('Fruits processed through the Aura Extractor grant a one-time EXP payout '
          '(the calculator credits it against the earliest remaining EXP). Payout scales '
          'with fruit rank, your Culti/Quality/Gush levels, and extractor rarity — higher '
          'quality rolls multiply the base substantially, so extractor upgrades compound.'),
      Text('Fruit ranks and realms', style: h3),
      para('Fruit ranks map to realm bands: R3 covers Nascent–Voidbreak, R6 starts '
          'the Spiritual world, R12 the Immortal world. R4/R5 don\'t exist.'),
      para('Myrimon unlocks at Virtuoso; Virtuoso–Incarnation share one '
          'fruit/extractor tier; each later major realm has its own.'),
      Text('Uses and stacking', style: h3),
      para('During the first week uses don\'t stack; after that they do — save them '
          'for Sunday or the next BR threshold.'),
      Text('Aura Extractor', style: h3),
      para('Extractor tracks: the Cultivation Bonus track is +4% per level, plus '
          'Quality and Gush tracks. Rarity bonuses: each rarity rank unlocks +20% '
          'orb EXP for its tier, and extractor rank at your Stage gives base fruit '
          'EXP +50%.'),
      Text('Gush', style: h3),
      para('Gush: base 150% multiplier, raised on the Gush track. Every 6th '
          'identical fruit is a guaranteed gush, on top of the displayed random rate.'),
      Text('Reset on breakthrough', style: h3),
      para('The Aura Extractor resets to Common quality / bonus 0 on main-Stage '
          'breakthrough and auto-consumes leftover previous-Stage fruits at '
          'pre-upgrade rates — upgrade fully before burning a stockpile, and burn '
          'it before breaking through.'),
      Text('Leveling and stockpiling', style: h3),
      para('Extractor leveling priority: Quality → Cultivation → Gush → High Rank '
          '(High Rank last, only after the rest are maxed).'),
      para('Advisory — tiering the extractor up requires consuming a number of fruits, '
          'so spend only the minimum needed for each tier-up and stockpile everything '
          'else until the extractor is maxed. Every fruit eaten early forfeits the '
          'better quality/EXP multipliers it would have received at higher extractor '
          'tiers — the same hoard is worth substantially more processed at max rarity. '
          'But do burn the stockpile before a main-Stage breakthrough: the extractor '
          'resets on breakthrough (see above).'),
      Text('Timegate penalty', style: h3),
      para('Fruits lose 50% of their EXP once the realm\'s timegate passes — eat '
          'the stockpile before the timegate.'),
    ]);

    final artifacts = page([
      Text('Creation Artifacts', style: h3),
      para('Vase refines pills into mythic reds (exempt from the daily limit). Mirror '
          'duplicates reds on top. Pearl converts energy to EXP scaled by your speed. '
          'Energy regenerates and caps — spend before it fills. The daily charge (30 '
          'Fateum/Destium for +100) is a per-artifact toggle.'),
      table(
        'Creation Artifact energy',
        ['Property', 'Value'],
        [
          ['Regeneration', '1 energy / 15 min at 0★ (faster per star)'],
          ['Cap', '200 at 0★ (rises with stars); regen stops at cap'],
          ['Daily charge', '+100 energy for 30 Fateum/Destium,\nonce per day per artifact'],
          ['Mirror copy cost', '200 base; −5% (1★), −10% (3★), −10% skin\n— discounts add together'],
          ['Mirror 5★', '15% chance of an extra copy per Duplication'],
          ['Pearl use cost', '10 energy; star/skin discounts add (skin −10%)'],
          ['Pearl EXP bonus', '+20% from 1★ (does not grow at higher stars)'],
        ],
      ),
      table(
        'Vase refine energy cost (per rank)',
        ['Rank', 'Energy'],
        [for (final r in pillXp.keys) [r, (vaseCost[r] ?? 100).toString()]],
        'Epic input −5%, Legendary −20%. Star: +10% EXP (1★), +20% (3★), 15% no-cost (5★). '
        'Skin +8% EXP.',
      ),
      table(
        'Aura Gem speed bonus',
        ['Rarity', 'Bonus'],
        [
          for (final e in gems.entries)
            if (e.key != 'None') [e.key, '+${((e.value as num) * 100).round()}%']
        ],
      ),
      Text('Aura Gem storage', style: h3),
      para('Aura Gem is claimable storage: it accrues the gem\'s % of your '
          'cultivation speed and caps at 18–32 hours\' worth depending on rarity. '
          'Claim before it caps — the calculator assumes you always do.'),
    ]);

    return DefaultTabController(
      length: 4,
      child: Column(children: [
        const TabBar(
          isScrollable: true,
          tabAlignment: TabAlignment.start,
          tabs: [
            Tab(text: 'Basics'),
            Tab(text: 'Pills & Respira'),
            Tab(text: 'Myrimon & Extractor'),
            Tab(text: 'Artifacts & Gems'),
          ],
        ),
        Expanded(
          child: TabBarView(children: [
            basics,
            pills,
            myrimon,
            artifacts,
          ]),
        ),
      ]),
    );
  }
}

/// Stage-by-stage cultivation guide, one sub-tab per realm band.
class GuideTab extends StatelessWidget {
  const GuideTab({super.key});

  @override
  Widget build(BuildContext context) {
    final h3 = Theme.of(context).textTheme.titleMedium;

    Widget para(String s) => Padding(
        padding: const EdgeInsets.symmetric(vertical: 6), child: Text(s));

    Widget page(List<Widget> children) => ListView(
        padding: const EdgeInsets.all(16),
        children: children);

    final novice = page([
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
          'breakthrough. (What each pill is worth: Reference → Pills & '
          'Respira.)\n'
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
          'of your cultivation speed (Reference → Basics).'),
    ]);

    final virtuoso = page([
      Text('Virtuoso (usually end of day 1)', style: h3),
      para('• Myrimon unlocks here — the Aura Extractor lotus next to your '
          'character on the cultivation screen, fed by fruits from the weekly '
          'Myrimon dungeon runs. It becomes your biggest free source of '
          'cultivation EXP, so read Reference → Myrimon & Extractor before '
          'spending anything.\n'
          '• During the first week of the Myrimon event your daily runs don\'t '
          'accumulate — use them every day at the highest realm you can clear. '
          'Afterwards they stack: bank them for Sunday or until you can clear '
          'a higher-requirement dungeon.\n'
          '• Work through Realm Abyss and Cultivation Ruins (in the realm '
          'menus) for all three Virtuoso realms — one-time cultivation '
          'rewards.\n'
          '• Check the events panel for realm exploration events; the curio '
          'rewards are worth the detour.'),
    ]);

    final nascent = page([
      Text('Nascent Soul (~day 3 for F2P)', style: h3),
      para('• Pacing: roughly 3 days to Nascent Late and 3 more to '
          'Incarnation. Spenders arrive faster — don\'t panic if you\'re a day '
          'behind.\n'
          '• Strive unlocks here: a catch-up bonus that raises your absorption '
          'while you\'re behind your server\'s #1 cultivator. In this '
          'calculator it appears as the implied Strive readout, and the '
          '"Server #1\'s Stage" input starts to matter for long-range '
          'estimates (Reference → Basics covers the math).\n'
          '• Keep the story, Demon Spire, and realms pushed as far as they\'ll '
          'go each cultivation stage — several systems gate on them.'),
    ]);

    final incarnation = page([
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
          'fruit math: Reference → Myrimon & Extractor.)\n'
          '• Before breaking through to Voidbreak: spend all pills and Respira '
          '(they reset), don\'t claim daily pill bags until after ascension, '
          'and spend Fatevillon shop tokens beforehand — that shop resets on '
          'breakthroughs too.'),
    ]);

    final voidbreak = page([
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
    ]);

    final pets = page([
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
    ]);

    final aux = page([
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
    ]);

    return DefaultTabController(
      length: 7,
      child: Column(children: [
        const TabBar(
          isScrollable: true,
          tabAlignment: TabAlignment.start,
          tabs: [
            Tab(text: 'Novice–Foundation'),
            Tab(text: 'Virtuoso'),
            Tab(text: 'Nascent Soul'),
            Tab(text: 'Incarnation'),
            Tab(text: 'Voidbreak+'),
            Tab(text: 'Pets'),
            Tab(text: 'Aux Paths'),
          ],
        ),
        Expanded(
          child: TabBarView(children: [
            novice,
            virtuoso,
            nascent,
            incarnation,
            voidbreak,
            pets,
            aux,
          ]),
        ),
      ]),
    );
  }
}
