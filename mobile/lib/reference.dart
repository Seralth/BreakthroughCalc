import 'package:flutter/material.dart';

import 'engine.dart';

/// Read-only reference tables + primer, rendered from the same engine data so
/// the numbers can't drift from the calculations.
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

    final pillXp = d['pill_xp'] as Map<String, dynamic>;
    final vaseCost = d['vase_energy_cost'] as Map<String, dynamic>? ?? {};
    final gems = d['gem_bonus'] as Map<String, dynamic>;

    return ListView(
      padding: const EdgeInsets.all(12),
      children: [
        Text('Cultivation reference', style: t.textTheme.titleLarge),
        Text('How cultivation works', style: h3),
        para('Cultivation EXP accrues one tick every 8 seconds (a "Cosmoapsis"). '
            'Cultivation Speed = Abode Aura × Absorption Ratio — all read from the '
            'in-game Cultivation Bonus screen. Progression is Stage → Half-step → Grade, '
            'each grade needing a fixed EXP amount.'),
        Text('Strive', style: h3),
        para('From Nascent Soul, Strive multiplies absorption and grows the further you '
            'are behind server #1, fading as you catch up. Set "Server #1 Stage" to model '
            'the drop-off. It does not change your current-position time (it cancels out).'),
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
        Text('Respira', style: h3),
        para('Daily-limited cultivation exercise. Each attempt rolls ×1/×2/×5/×10 crits at '
            '60/30/8/2% (mean ×1.8, applied automatically). Enter attempts/day and the base '
            '(non-crit) EXP per attempt — the small, most-common value you see, not a crit result.'),
        Text('Crit variance (best / worst)', style: h3),
        para('Respira crits and fruit gushes are random, so estimates carry a ~90% best/worst '
            'band. Because these are sums of many independent rolls, luck averages out: the band '
            'is widest on short estimates and tightens over long horizons. Fruit gushes also have '
            'a pity floor (every 6th fruit is a guaranteed gush), narrowing the fruit side.'),
        Text('Myrimon Fruits', style: h3),
        para('Fruits processed through the Aura Extractor grant a one-time EXP payout '
            '(the calculator credits it against the earliest remaining EXP). Payout scales '
            'with fruit rank, your Culti/Quality/Gush levels, and extractor rarity — higher '
            'quality rolls multiply the base substantially, so extractor upgrades compound.'),
        para('Advisory — tiering the extractor up requires consuming a number of fruits, '
            'so spend only the minimum needed for each tier-up and stockpile everything '
            'else until the extractor is maxed. Every fruit eaten early forfeits the '
            'better quality/EXP multipliers it would have received at higher extractor '
            'tiers — the same hoard is worth substantially more processed at max rarity.'),
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
        Text('Core formulas', style: h3),
        para('• Cultivation Speed = Abode Aura × Absorption Ratio\n'
            '• Abode Aura = 130 × (1 + total aura bonus) — base 130 holds for '
            'Connection through Incarnation\n'
            '• Cultivation ticks every 8 seconds (one Cosmoapsis)\n'
            '• Absorption = stage base × (1 + Strive); Strive unlocks at Nascent Soul '
            'and fades as you approach your server\'s #1\n'
            '• Pill EXP = base × (1 + pill effect + quality star mark [+ Vase star/skin '
            'for reds])'),
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
      ],
    );
  }
}
