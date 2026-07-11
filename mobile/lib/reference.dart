import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

import 'engine.dart';

const _issuesUrl = 'https://github.com/Seralth/BreakthroughCalc/issues';

/// In-text cross-reference markup: `[[ref:slug|label]]` / `[[guide:slug|label]]`.
/// Slug order must match the Tab order in ReferenceTab / GuideTab below.
const refSlugs = {'basics': 0, 'pills': 1, 'elixirs': 2, 'myrimon': 3,
                  'artifacts': 4, 'combat': 5, 'systems': 6, 'advanced': 7};
const guideSlugs = {'paths': 0, 'routine': 1, 'novice': 2, 'virtuoso': 3,
                    'nascent': 4, 'incarnation': 5, 'voidbreak': 6,
                    'pets': 7, 'aux': 8, 'spending': 9};

class DocLink {
  final int tab; // top-level tab index: 1 = Reference, 2 = Guide
  final int sub; // sub-tab index within it
  const DocLink(this.tab, this.sub);
}

/// Pending cross-reference jump. Set when a link is tapped; the main scaffold
/// switches the top-level tab and the target tab consumes it — on first build
/// if its TabBarView page wasn't alive when the link was tapped.
final ValueNotifier<DocLink?> docLinkRequest = ValueNotifier(null);

final _docLinkRe = RegExp(r'\[\[(ref|guide):([a-z]+)\|([^\]]+)\]\]');

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
    final tree = m.group(1)!, slug = m.group(2)!, label = m.group(3)!;
    final sub = tree == 'ref' ? refSlugs[slug] : guideSlugs[slug];
    spans.add(sub == null
        ? TextSpan(text: label)
        : TextSpan(
            text: label,
            style: linkStyle,
            recognizer: TapGestureRecognizer()
              ..onTap = () => docLinkRequest.value =
                  DocLink(tree == 'ref' ? 1 : 2, sub)));
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

/// Read-only reference tables + primer, rendered from the same engine data so
/// the numbers can't drift from the calculations. Organized as scrollable
/// sub-tabs: mechanics first, then a stage-by-stage progression walkthrough.
class ReferenceTab extends StatefulWidget {
  final Engine engine;
  final List<dynamic> catalog;
  const ReferenceTab({super.key, required this.engine, required this.catalog});

  @override
  State<ReferenceTab> createState() => _ReferenceTabState();
}

class _ReferenceTabState extends State<ReferenceTab>
    with SingleTickerProviderStateMixin {
  late final TabController _tabs = TabController(length: 8, vsync: this);

  @override
  void initState() {
    super.initState();
    docLinkRequest.addListener(_onDocLink);
    WidgetsBinding.instance.addPostFrameCallback((_) => _onDocLink());
  }

  void _onDocLink() {
    final req = docLinkRequest.value;
    if (req == null || req.tab != 1 || !mounted) return;
    _tabs.animateTo(req.sub);
    docLinkRequest.value = null;
  }

  @override
  void dispose() {
    docLinkRequest.removeListener(_onDocLink);
    _tabs.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final engine = widget.engine;
    final catalog = widget.catalog;
    final d = engine.data;
    final t = Theme.of(context);
    final h3 = t.textTheme.titleMedium;
    final muted = TextStyle(color: t.hintColor, fontSize: 12);

    Widget para(String s) => Padding(
        padding: const EdgeInsets.symmetric(vertical: 6),
        child: docText(context, s));

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

    Widget footer() => Padding(
          padding: const EdgeInsets.only(top: 16, bottom: 8),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            const Divider(),
            Text(
                'Spotted an error, or have data for a "?" in a table (a '
                'screenshot of a tier you\'ve crossed, an endgame number)? '
                'Much of this page is reconstructed from player screenshots, '
                'and single data points regularly fill real gaps — please '
                'report it at:',
                style: muted),
            issuesLink(context),
          ]),
        );

    Widget page(List<Widget> children) =>
        ListView(padding: const EdgeInsets.all(12), children: [...children, footer()]);

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
          'a pity floor (a gush is guaranteed within 6 fruits of the last one), narrowing the fruit side.'),
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

    // Permanent consumables — verified 2026-07-10 from in-game screens
    // (formula panel, elixir tooltips, Compare BR "Pill and Elixir Details").
    final elixirs = page([
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
          '+10 M.EVA). Flat effect, no decay, until the rank\'s permanent use cap: '
          'R1 20 · R2 40 · R3+ 50 uses. The cap is on the pill, not the formula — '
          'shop/reward pills spend the same budget, and the counter ticks even '
          'with the formula unlearned. Each major realm breakthrough unlocks the '
          'next rank\'s 50 uses per line (Compare BR "Stat Pill Use Limit": '
          'Nascent Soul 320, Incarnation 420, Voidbreak 520).'),
      para('Practical read: there is no way to waste a stat pill — every use '
          'pays the same flat amount and the budget refills only by reaching '
          'new realms — so take them as you get them. The only real decision '
          'is whether the crafting cost is worth it, and that gets steep at '
          'high ranks.'),
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
      Text('Stat elixirs (tolerance ladder)', style: h3),
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
        'Verified against 18 observed items, whose lifetime totals all '
        'reproduce exactly from these widths (each tier contributes '
        'uses × base × ratio). "?" marks tiers no character has crossed yet; '
        'the in-game tooltip says the ladder continues 70 → 50 → 30 → 20% '
        'before the hard cap. Cultivation-EXP elixirs use different, wider '
        'tiers (first tier 20 uses, not 10).',
      ),
      Text('Elixirs and paths', style: h3),
      para('EXP elixirs are path-specific: the Vigor ladder feeds Literatia, '
          'Fatebreaker Ghostia, Emerald Magicka, Nonagen Corporia, Cloudcut Grit '
          'Swordia; Spiritual Nectar feeds your current path, Hundred Fortunes / '
          'Pyroessence your auxiliary path. A red requirement line = realm not '
          'met on that item\'s path. Path Switch swaps each elixir\'s remaining '
          'quantity, use attempts and efficiency along with the paths.'),
      Text('Getting EXP elixirs', style: h3),
      para('In normal play EXP elixirs only trickle in — small amounts, often '
          'priced in Fateum, which F2P players should generally spend on the '
          'garden first — it feeds the law system that starts at Voidbreak '
          '(see [[guide:voidbreak|Guide → Voidbreak+]]). The exception: breaking through to a new realm offers '
          'three real-money elixir packs, among the best value in the game for '
          'anyone optimizing money spent — the 150%/120% early tolerance tiers '
          'make each realm\'s batch worth the most right when you buy it.'),
      Text('The Sense stat', style: h3),
      para('Sense (internally spirit_max) currently only gates treasure capacity: '
          'Fabao slots at Sense 1/7/13/16/19/22, Gubao slots at 15/18/21. It '
          'grows ~1 per realm level; the tooltip says more uses are planned. It '
          'is not part of any exposed damage or cultivation formula.'),
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
      para('Gush: base 150% multiplier, raised on the Gush track. A gush is '
          'guaranteed within 6 fruits of the last one (soft pity — any gush, '
          'random or guaranteed, resets the counter), on top of the displayed '
          'random rate.'),
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

    // Combat-side systems overview. Combat is resolved server-side; these are
    // the client-visible rules, with exact numbers only where confirmed.
    final combat = page([
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
      para('The rest of the crit family, confirmed from game data:\n'
          '• Crit DMG: a crit deals 150% damage baseline (rounded down); Crit '
          'DMG bonuses raise that multiplier.\n'
          '• Crit Defense: each +1% cuts an attacker\'s crit multiplier by 1% '
          'against you.\n'
          '• Crit Resistance: lowers the chance of being crit in the first '
          'place.'),
      Text('Gear in one paragraph', style: h3),
      para('You wear a weapon, armor and an accessory, plus Relics as their own '
          'separate category. Rarity climbs white → green → blue → purple → '
          'yellow. When an item is forged its stats roll within a range — so two '
          'copies of the same item can differ, and a well-rolled piece is worth '
          'keeping.'),
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
      Text('Affix priorities (community tier list)', style: h3),
      para('Which gear/relic affix lines to chase, per a widely circulated '
          'community tier list (opinion, but consistent with the mechanics '
          'above). Stat caps drive a lot of it: Crit hard-caps at 50%, '
          'Hit/EVA at 99% — capped stats are dead value past the cap.\n'
          '• T0 — always chase: base-stat % (Wonder +30–46% everything; '
          'Blade Rage / Spellforge +20–28% P.ATK/M.ATK), relic cast speed '
          '(Spirit +9–21%), ultimate attack % (Ulti Sharp/Occult +15–21%), '
          'attack frequency (Bladeglow +11–15.4% on swords), relic limit '
          'breakers (Ether Veil / Infinite Edge +15–25.2%). Cast speed and '
          'limit breakers matter most from Voidbreak on, where raw damage '
          'caps easily.\n'
          '• T1 — good: crit multiplier/damage (Annihilation, Pursuit), '
          'crit chance (Fatal — dead past the 50% cap), flat attack '
          '(Sharp/Occult — match physical/magical to your path or it\'s '
          'wasted), Physique/Manipulation (+4 ATK +2 DEF per point, same '
          'path-matching rule), Agility (+3 Hit and EVA per point), flat '
          'HP/MP.\n'
          '• T2 — situational: flat Hit/EVA lines, P.DEF/M.DEF (weak — '
          'Penetration ignores defense proportionally), Crit Resist, the '
          'paralysis quartet (duration generally beats chance).\n'
          '• T3 — avoid: HP/MP regen (only ticks out of combat, which '
          'never happens in duels or the Voidgate) and Bladesoul '
          '(sword-control resist).'),
      para('Paralysis math from the same source: boost and resist cancel '
          '1:1; each leftover point shifts proc chance by 0.2% (bounded '
          '50–100%) and duration by 0.5% (max ±50%).'),
      Text('About the missing numbers', style: h3),
      para('The rules and thresholds above are confirmed from game data. The '
          'exact values — what a given 10-level bonus or resonance rank grants — '
          'are decided server-side and vary by item and realm, so this page '
          'doesn\'t guess at them. Where a number isn\'t listed, read it as '
          '"unknown", not "zero". For the exact per-point math the game does '
          'expose, see the [[ref:advanced|Advanced tab]].'),
    ]);

    // Expert-level internals; only client-stated mechanics carry numbers.
    final advanced = page([
      Text('Cultivation internals', style: h3),
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
      para('Fruit gush pity: the "Gush guaranteed in Aura Orb x6" counter is a '
          'soft pity — any gush, random or guaranteed, resets it (verified '
          'in-game 2026-07-10 with a counted batch). So a gush is guaranteed '
          'within 6 fruits of the last one, and the displayed chance is the '
          'per-fruit random rate. The calculator models the miss streak as a '
          'Markov chain and computes the exact gush-count mean and variance, '
          'which narrows the fruit side of the band.'),
      para('Strive tier tables (client config; the live value is recomputed '
          'hourly server-side, so only the shape is used, anchored to your real '
          'Strive):\n'
          '• Young servers (world level < 30): by major-realm gap to server #1 '
          '— 15/20/30/40/50/60/70% for gaps 1–7.\n'
          '• Mature servers (world level ≥ 30): by minor-level gap — 70% at '
          '≥60 levels, 30% at ≥50, 20% at ≥40 — plus an additive major-realm '
          'bonus of 30% (1 realm) or 50% (2+). The 70% + 50% sum is the ~120% '
          'cap seen on aged servers.'),
      para('The best/worst band is a ~90% central interval (P5–P95): the '
          'calculator sums the variance of every random roll over the horizon '
          'and takes ±1.645 standard deviations around the mean. The band is '
          'widest in relative terms on short projections and tightens as the '
          'horizon grows.'),
      Text('Combat internals', style: h3),
      para('Exact mechanics recovered from the game\'s own stat definitions and '
          'tooltip text. Everything numbered here is stated by the client; '
          'damage resolution itself runs on the server, so treat this as the '
          'rulebook rather than a full damage calculator.'),
      Text('Flat stats and realm normalization', style: h3),
      para('Crit Chance, Crit Resistance, Hit Rate and Dodge are stored as flat '
          'values and converted to effective percentages against a '
          'realm-dependent standard. This is why the game\'s own tooltip reports '
          'your "crit rate at your current realm": the flat number keeps its '
          'value, but each realm raises the standard it\'s measured against, '
          'deflating the percentage. The normalization curve is server-side; '
          'the in-game tooltip is the only exact readout.'),
      table(
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
      ),
      Text('Penetration and Block, exactly', style: h3),
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
          'gear. The in-game BR breakdown panel groups it into: character level '
          '& realm, inner skill, gear (base + affixes + augment levels + '
          'carvings), Relics (same sub-parts), Abilities and their training, '
          'Curios (base + active + set), pets (level, skills, growth), plus '
          'talismans, celebrity cards and the rest.'),
      para('Two useful things fall out of the client weights:\n'
          '• Defense is weighted ~2.1× attack per point (and HP/MP pool points '
          'far below either) — the game "prices" a point of defense as worth '
          'about twice a point of attack.\n'
          '• Each gear piece and Relic arrives with its BR pre-computed (a '
          'base score, and for Relics a realm-corrected score that only '
          'applies once your realm meets the item\'s requirement — an '
          'under-realm Relic shows its uncorrected, lower BR).'),
      para('The exact weight constants exist in client data but the server\'s '
          'final assembly (level factors, rounding) isn\'t visible, so per-stat '
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
    ]);

    // System explainers assembled from the client's own tooltip/description
    // strings (i18n dump) plus user-verified play notes; server-side numbers
    // are omitted rather than guessed.
    final systems = page([
      para('Short explainers for the systems the rest of this app keeps '
          'mentioning. Everything quoted is from the game\'s own text; where '
          'a number is server-side, it\'s omitted rather than guessed.'),
      Text('Currencies', style: h3),
      para('• Spiritium — "the basic currency in the cultivation world. '
          'Mainly obtained in Realms. Used in Market, Alchemy, Forge Room and '
          'other daily matters." Realm idle production scales with Demon '
          'Spire progress.\n'
          '• Fateum — the premium-adjacent currency, "obtained from gameplay '
          'or by exchanging Destium"; spent in the Fatevillion shop, on Path '
          'Switches, refreshes, and artifact daily charges.\n'
          '• Destium — purchase-only; converts to Fateum 1:1 (irreversible). '
          'Also used in the Auction House.'),
      para('Two more shop currencies worth knowing: Revealstone (Seeker '
          'Shop) and Citrine + Sect Contribution (Sect Library) — see the '
          'shop guide below.'),
      para('Spending guidance: Fateum is the scarce one for F2P — prioritize '
          'the garden (law fruits) once laws unlock at Voidbreak, ahead of '
          'elixirs and convenience refreshes. Payers get the most per unit '
          'from artifact daily charges and the realm-breakthrough elixir '
          'packs.'),
      Text('Shop-by-shop buying guide', style: h3),
      para('Community-consensus priorities (from circulating player guides — '
          'sanity-checked but not client data):\n'
          '• Market (Spiritium): Demonroot (pet skills), Kunlun Jade '
          '(backpack space), Monster Core, Rare+ cultivation pills, Atlases, '
          'stat elixirs. It refreshes every 3 hours; you get 10 manual '
          'refreshes/day (each costs more Spiritium) and every 5th refresh '
          'guarantees an Epic item.\n'
          '• Seeker Shop (Revealstone): buy NOTHING before Voidbreak. '
          'Nature Mantras there cost ~200 each and you\'ll want 3,300+ — '
          'hundreds of thousands of Revealstone — and F2P sources are '
          'scarce.\n'
          '• Sect Library (Citrine / Sect Contribution): Ability '
          'Manuscripts first — skipping them slows ability progression '
          'badly — then blueprints and alchemy formulas. Citrine comes from '
          'mining spiritual veins (capped ~2 h/day + 7 h/week — mine daily, '
          'highest vein tier first).\n'
          '• Fatevillion (Fateum): the Cultivation Bag is the standout '
          'must-buy; cultivation elixirs are worth it for F2P while your '
          'tolerance ratio is above ~120%; Demonlure for realm farming; '
          'anything at a 70% discount deserves a look. The shop resets on '
          'EVERY breakthrough — minor ones included — so check it before '
          'each one.'),
      para('Cheap daily Fateum habits: the first daily Technique Points '
          'purchase (100 points for 50 Fateum) and the second daily sect '
          'Construct (first free, second 50) are both efficient. Refreshing '
          'unclaimed Bounty Quests below Rare and Sect Tasks below C-rating '
          'once a day upgrades them guaranteed.'),
      Text('Garden & Elemental Laws', style: h3),
      para('The garden grows seeds into rewards: each seed takes plot slots '
          'and matures over time; you get limited daily watering attempts to '
          'speed growth (the first is free each day — don\'t miss it), and '
          'growth can be rushed with energy + Spiritium. Seeds yield alchemy '
          'materials, technique seeds, and — the headline crop — Law '
          'Fruits.'),
      para('Elemental Laws (unlock at Voidbreak) are a long-term damage '
          'system: Law Points accrue naturally over time (faster as your '
          'laws level) and are spent to upgrade laws once you meet the Stage '
          'requirement. Higher total law level deals bonus damage to '
          'lower-level enemies — the bigger the gap, the more damage. Every '
          '100M Law Points auto-converts to a Tao Motto. Eating Law Fruits '
          '"greatly benefits the study of laws", and Blitz spends Law Fruits '
          'for Law Points directly; advancing a Law Fruit has a 15% chance '
          'to yield an extra fruit. This is why the guide says to bank pet '
          'speed-ups and Fateum for the garden before Voidbreak: law levels '
          'are a time-integral, so starting earlier compounds.'),
      para('Community practice (consistent advice, unverified numbers): '
          'have 24 garden slots by Voidbreak; on ascension day unlock laws '
          'immediately and get fruits planted. Blitz has a daily budget '
          '(~120 hours\' worth) — ideally spend all of it every day. Law '
          'fruits range Uncommon → Legendary; early on harvest low rarities '
          'for cheap fast levels, shift higher as seeds accumulate. '
          'Leveling order: all laws to 50 one at a time, then to 150, and '
          'so on in +100 steps. The payoff: roughly +50% damage per 1,000 '
          'total law levels above your opponent — law suppression only '
          'applies while you\'re ahead.'),
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
      Text('Path Switch', style: h3),
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
      Text('Demon Spire', style: h3),
      para('A floor-climbing combat tower. Your current floor pays '
          'continuous hourly income — Ability Knowledge (levels your '
          'Abilities) and a bonus to Spiritium production in Realms — so '
          'every floor cleared is a permanent income raise. Climb whenever '
          'your battle rating allows.'),
      Text('Curios', style: h3),
      para('Collectible items placed on the Sacred Altar (six slots). A slot '
          'boosts the passive stats of curios matching its type (HP, MP, '
          'P.ATK, M.ATK, P.DEF, M.DEF); percentage-stat curios don\'t '
          'benefit. Altar effects multiply with a curio\'s Star-Up. Rarities '
          'run Rare → Epic → Legendary → Mythic, from a draw system with '
          'guarantees. Several curios also carry the cultivation bonuses '
          '(pill effect, Respira) listed elsewhere in this reference.'),
      Text('Techniques', style: h3),
      para('Unlockable passives: meet a technique\'s requirements to learn '
          'it, then spend Technique Points to tier it up — special effects '
          'unlock at Tiers 3, 6 and 9. The early-game picks the guide names '
          '(Longevity, Energy Unification, Rejuvenation) are examples of '
          'buying these tier effects at their cheapest; the same logic — '
          'tier breakpoints first — carries through the rest of the game.'),
      // Community-guide material (2026) from here down — priorities and
      // tier lists are consensus, not client data.
      Text('Technique roadmap (community priorities)', style: h3),
      para('The consensus per-rank picks, tier breakpoints first:\n'
          '• R4: Golden Core (+5% pill effect at completion) and Astrology '
          'to Tier 7.\n'
          '• R5: Ninefall and Bloodization to Tier 7.\n'
          '• R6: Dragon\'s Flight or Yin\'s Grasp to Tier 10.\n'
          '• R7 (from the app\'s own source data): Floral Essence — +3% '
          'pill effect at Tier 6, +1 daily pill attempt at Tier 9; Great '
          'Yang Manual — +4% pill effect at Tier 9.\n'
          '• R10: Immortal Ascension to Tier 13.'),
      para('The community list for R8–R9 wasn\'t preserved — if you have '
          'it, please report it via the footer link. For Technique Points, '
          'the consensus Spirit World strategy is three passes: clear what '
          'you can, come back stronger, finish later — rather than grinding '
          'one full clear early.'),
      Text('Curio priorities (community)', style: h3),
      para('• Value order: abode/pill-bonus curios > main-path ATK > '
          'HP/MP.\n'
          '• Star up Pen & Block equally — a Pen roughly 1000 over the '
          'opponent\'s Block negates their defense.\n'
          '• Get everything to 2–3 stars minimum before pushing any single '
          'curio deep.\n'
          '• Daemonfae, Field and Reincarnation curios have their own '
          'niches — hold them rather than feeding them away.'),
      Text('Fields (Perfection, community)', style: h3),
      para('At Perfection you pick a Field; the consensus mapping:\n'
          '• Solarium — PvE-leaning and the usual F2P pick.\n'
          '• Swordium — the general-purpose choice.\n'
          '• Darkmyth — team-oriented; pick it with your sect, not solo.\n'
          'Fields level and enlighten separately and have their own '
          'field-soul structure — details not yet captured here.'),
    ]);

    return Column(children: [
        TabBar(
          controller: _tabs,
          isScrollable: true,
          tabAlignment: TabAlignment.start,
          tabs: const [
            Tab(text: 'Basics'),
            Tab(text: 'Pills & Respira'),
            Tab(text: 'Elixirs & Stat Pills'),
            Tab(text: 'Myrimon & Extractor'),
            Tab(text: 'Artifacts & Gems'),
            Tab(text: 'Combat & Gear'),
            Tab(text: 'World Systems'),
            Tab(text: 'Advanced'),
          ],
        ),
        Expanded(
          child: TabBarView(controller: _tabs, children: [
            basics,
            pills,
            elixirs,
            myrimon,
            artifacts,
            combat,
            systems,
            advanced,
          ]),
        ),
      ]);
  }
}

/// Stage-by-stage cultivation guide, one sub-tab per realm band.
class GuideTab extends StatefulWidget {
  const GuideTab({super.key});

  @override
  State<GuideTab> createState() => _GuideTabState();
}

class _GuideTabState extends State<GuideTab>
    with SingleTickerProviderStateMixin {
  late final TabController _tabs = TabController(length: 10, vsync: this);

  @override
  void initState() {
    super.initState();
    docLinkRequest.addListener(_onDocLink);
    WidgetsBinding.instance.addPostFrameCallback((_) => _onDocLink());
  }

  void _onDocLink() {
    final req = docLinkRequest.value;
    if (req == null || req.tab != 2 || !mounted) return;
    _tabs.animateTo(req.sub);
    docLinkRequest.value = null;
  }

  @override
  void dispose() {
    docLinkRequest.removeListener(_onDocLink);
    _tabs.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final h3 = Theme.of(context).textTheme.titleMedium;

    Widget para(String s) => Padding(
        padding: const EdgeInsets.symmetric(vertical: 6),
        child: docText(context, s));

    Widget footer() => Padding(
          padding: const EdgeInsets.only(top: 16, bottom: 8),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            const Divider(),
            Text(
                'Spotted an error or something missing? Much of this guide '
                'comes from player observations — please report corrections '
                'and new data at:',
                style: TextStyle(color: Theme.of(context).hintColor, fontSize: 12)),
            issuesLink(context),
          ]),
        );

    Widget page(List<Widget> children) => ListView(
        padding: const EdgeInsets.all(16),
        children: [...children, footer()]);

    // Path meta from a circulating community guide (2026) plus the
    // maintainer's read of Discord consensus — opinion, not client data.
    final choosing = page([
      Text('Choosing your path', style: h3),
      para('The first decision in the game. It\'s less permanent than it '
          'looks — Path Switch exists from Foundation (7-day cooldown, '
          'rising Fateum cost) — but your path shapes combat style, gear '
          'priorities, and which elixirs/pets/aux picks fit. This summary '
          'is community consensus, and the consensus is genuinely mixed — '
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
          'climbing ([[ref:systems|Reference → World Systems]]).'),
    ]);

    final routine = page([
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
          '([[ref:myrimon|Reference → Myrimon & Extractor]]).'),
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
          '([[ref:elixirs|Reference → Elixirs & Stat Pills]]); the full '
          'what\'s-worth-it list is on [[guide:spending|Guide → Spending]].'),
      Text('Quality-of-life settings', style: h3),
      para('• Turn off wandering (settings) — it only animates your '
          'character walking around and costs attention for nothing.\n'
          '• Set battle speed to 3× once it unlocks; there is no downside.'),
    ]);

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
          'breakthrough. (What each pill is worth: '
          '[[ref:pills|Reference → Pills & Respira]].)\n'
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
          'of your cultivation speed ([[ref:basics|Reference → Basics]]).'),
    ]);

    final virtuoso = page([
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
          'estimates ([[ref:basics|Reference → Basics]] covers the math).\n'
          '• Keep the story, Demon Spire, and realms pushed as far as they\'ll '
          'go each cultivation stage — several systems gate on them.\n'
          '• By now stat pills and elixirs are flowing in from shops and '
          'rewards. Take them as they arrive — neither can be wasted by using '
          'them early, and stat pills\' use caps grow with each realm anyway '
          '([[ref:elixirs|Reference → Elixirs & Stat Pills]]).'),
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
          'fruit math: [[ref:myrimon|Reference → Myrimon & Extractor]].)\n'
          '• Before breaking through to Voidbreak: spend all pills and Respira '
          '(they reset), don\'t claim daily pill bags until after ascension, '
          'and spend Fatevillion shop tokens beforehand — that shop resets on '
          'breakthroughs too.\n'
          '• On the ascension itself you\'ll be offered three real-money '
          'elixir packs — if you spend at all, these are among the best value '
          'in the game ([[ref:elixirs|Reference → Elixirs & Stat Pills]] '
          'explains why the '
          'early tolerance tiers make them worth the most).'),
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
      // Community-guide material (2026): friend levels/payoffs are the
      // circulating consensus list, cross-checked against the app's own
      // pill/Respira source data where the two overlap.
      Text('Ascension day (community checklist)', style: h3),
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
      Text('Immortal Friends (community priorities)', style: h3),
      para('Friends\' levels pay off in cultivation terms at specific '
          'breakpoints. The consensus unlock/level priorities:\n'
          '• Crane Boy to max — +1 daily pill attempt.\n'
          '• Iron Fan 36, Daji 73, Shen Gongbao 117 — +1 daily Respira '
          'attempt each.\n'
          '• Jiang Ziya 116 and Taotie 117 — +3% pill effect each.\n'
          '• Macaque 17 — +3% Respira EXP (already included in your '
          'in-game Respira tooltip).\n'
          '• Also on the community priority list (payoff not recorded '
          'yet): White Astra 31, Princess Adalinda 81, Leizhenzi 129.'),
      para('These attempt/effect bonuses are exactly what the calculator\'s '
          'pill and Respira source pickers model — tick them there once you '
          'hit the breakpoints.'),
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

    // Spending advice is community consensus (2026 guide + Discord);
    // BR figures are era-specific estimates, not client data.
    final spending = page([
      Text('Spending (if you pay at all)', style: h3),
      para('None of this is a recommendation to spend — it\'s the '
          'community\'s answer to "if I do, what\'s actually worth it?" '
          'All of it is consensus opinion.'),
      Text('Priorities', style: h3),
      para('• Permanent one-time buys first: the watering curio set and the '
          'permanent passes beat any consumable pack — you buy them once '
          'and they pay out forever.\n'
          '• The three elixir packs on reaching a new realm are among the '
          'best consumable value in the game — early tolerance tiers make '
          'them worth the most ([[ref:elixirs|Reference → Elixirs & Stat '
          'Pills]]).\n'
          '• The daily 30 Fateum/Destium artifact charges are among the '
          'cheapest EXP money buys.\n'
          '• Law fruit packs are atrocious value — do not buy them.\n'
          '• Heavy pet investment is whale territory '
          '([[guide:pets|Guide → Pets]]).'),
      Text('Timegate BR targets (era-specific community estimates)', style: h3),
      para('Rough battle-rating bands players report aiming for at each '
          'realm\'s timegate content, by spending tier (F2P → heavy). These '
          'drift with every era — treat as orientation only:\n'
          '• Incarnation: 800m – 2b+\n'
          '• Voidbreak: 9b – 25b+\n'
          '• Wholeness: 45b – 100b+'),
    ]);

    return Column(children: [
        TabBar(
          controller: _tabs,
          isScrollable: true,
          tabAlignment: TabAlignment.start,
          tabs: const [
            Tab(text: 'Choosing a Path'),
            Tab(text: 'Daily Routine'),
            Tab(text: 'Novice–Foundation'),
            Tab(text: 'Virtuoso'),
            Tab(text: 'Nascent Soul'),
            Tab(text: 'Incarnation'),
            Tab(text: 'Voidbreak+'),
            Tab(text: 'Pets'),
            Tab(text: 'Aux Paths'),
            Tab(text: 'Spending'),
          ],
        ),
        Expanded(
          child: TabBarView(controller: _tabs, children: [
            choosing,
            routine,
            novice,
            virtuoso,
            nascent,
            incarnation,
            voidbreak,
            pets,
            aux,
            spending,
          ]),
        ),
      ]);
  }
}
