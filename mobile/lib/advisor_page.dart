/// Advisor page (Flutter only — every ranking comes from advisor.dart).
/// Mirror of the desktop advisor_ui.py page: the plan lists steps you can
/// work toward; the draws list prices what a lucky curio pull would be
/// worth, since curios cannot simply be bought.
library;

import 'package:flutter/material.dart';

import 'advisor.dart';
import 'engine.dart';
import 'i18n.dart';

class AdvisorPage extends StatefulWidget {
  final Engine engine;
  final Map catalog;
  final Inputs Function() getInputs;
  final Map Function() getShelf;
  const AdvisorPage(
      {super.key,
      required this.engine,
      required this.catalog,
      required this.getInputs,
      required this.getShelf});

  @override
  State<AdvisorPage> createState() => _AdvisorPageState();
}

class _AdvisorPageState extends State<AdvisorPage> {
  Advice? _advice;

  @override
  void initState() {
    super.initState();
    _refresh();
  }

  void _refresh() {
    setState(() {
      _advice = rank(widget.engine, widget.getInputs(), widget.catalog,
          widget.getShelf());
    });
  }

  Widget _group(BuildContext context, String title, List<RankedStep> ranked) {
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Padding(
        padding: const EdgeInsets.fromLTRB(16, 16, 16, 4),
        child:
            Text(title, style: Theme.of(context).textTheme.titleMedium),
      ),
      if (ranked.isEmpty)
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
          child: Text(tr('Nothing here helps right now.'),
              style: const TextStyle(fontSize: 12, color: Colors.grey)),
        ),
      for (final r in ranked)
        ListTile(
          dense: true,
          title: Text(r.candidate.name),
          subtitle: Text(r.candidate.action == 'Own'
              ? tr('Own')
              : r.candidate.action),
          trailing: Text(trDuration(fmtDays(r.daysSaved)),
              style: const TextStyle(fontWeight: FontWeight.bold)),
        ),
    ]);
  }

  @override
  Widget build(BuildContext context) {
    final adv = _advice;
    return Scaffold(
      appBar: AppBar(title: Text(tr('Advisor')), actions: [
        IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: tr('Rank again'),
            onPressed: _refresh),
      ]),
      body: adv == null
          ? const SizedBox.shrink()
          : ListView(children: [
              Padding(
                padding: const EdgeInsets.all(16),
                child: Text(
                  tr('What to work on next, priced in days saved on your '
                      'current projection. The plan lists steps you can '
                      'simply go do; curios come from random draws, so '
                      'those rank separately as what a lucky pull would '
                      'be worth.'),
                  style: const TextStyle(fontSize: 12, color: Colors.grey),
                ),
              ),
              if (!adv.valid)
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  child: Text(tr(
                      'Fill in the Calculator first — the advisor prices '
                      'improvements against your current projection.')),
                )
              else ...[
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  child: Text(
                    '${adv.metric == 'target' ? tr('Ranking: days until your target Stage.') : tr('Ranking: days to finish the current Stage.')}'
                    ' (${trDuration(fmtDays(adv.baselineDays))})',
                    style: const TextStyle(fontSize: 12),
                  ),
                ),
                _group(context, tr('Plan — level or learn next'), adv.plan),
                _group(context, tr('Random draws — worth pulling for'),
                    adv.draws),
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: Text(
                    tr('Bonuses the calculator does not model — combat '
                        'stats, Spiritium, Abode Aura already inside your '
                        'readings — are not ranked.'),
                    style:
                        const TextStyle(fontSize: 11, color: Colors.grey),
                  ),
                ),
              ],
            ]),
    );
  }
}
