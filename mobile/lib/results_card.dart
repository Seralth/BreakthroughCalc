/// The results summary card at the top of the calculator form: breakthrough
/// estimates with best/worst bands, the daily-XP breakdown, and the
/// absorption diagnostics rows (rendered from [diagnoseAbsorption]).
library;

import 'package:flutter/material.dart';

import 'absorption_diag.dart';
import 'engine.dart';
import 'i18n.dart';

class ResultsCard extends StatelessWidget {
  final Engine engine;
  final Inputs inp;
  final Results res;
  const ResultsCard(
      {super.key, required this.engine, required this.inp, required this.res});

  @override
  Widget build(BuildContext context) {
    final t = Theme.of(context);
    Widget row(String label, String value, [List<double>? band, Color? color]) {
      final showBand = band != null && band.length == 2 && (band[1] - band[0]).abs() > 1e-9;
      return Padding(
        padding: const EdgeInsets.symmetric(vertical: 3),
        child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Expanded(flex: 5, child: Text(label)),
          Expanded(
            flex: 7,
            child: RichText(
              textAlign: TextAlign.right,
              text: TextSpan(style: t.textTheme.bodyMedium, children: [
                TextSpan(
                    text: value,
                    style: TextStyle(fontWeight: FontWeight.bold, color: color)),
                if (showBand)
                  TextSpan(
                    text: '  (${tr('best')} ${trDuration(fmtDays(band[0]))} / ${tr('worst')} ${trDuration(fmtDays(band[1]))})',
                    style: TextStyle(color: t.hintColor, fontWeight: FontWeight.normal),
                  ),
              ]),
            ),
          ),
        ]),
      );
    }

    return Card(
      color: t.colorScheme.surfaceContainerHighest,
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: !res.valid
            ? Text(tr(res.error), style: TextStyle(color: t.colorScheme.error))
            : Column(children: [
                if (res.error.isNotEmpty)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 6),
                    child: Text(tr(res.error), style: TextStyle(color: t.colorScheme.error)),
                  ),
                row(tr('Half-step breakthrough in'), trDuration(fmtDays(res.phaseDays)), res.phaseBand),
                row(tr('Stage breakthrough in'), trDuration(fmtDays(res.stageDays)), res.stageBand),
                if (res.targetValid)
                  row(tr('Target reached in'), trDuration(fmtDays(res.targetDays)), res.targetBand),
                if (res.prestockValid)
                  row(
                      tr('Prestock for target (overcap)'),
                      '${res.prestockPct.toStringAsFixed(0)}% — ${trDuration(fmtDays(res.prestockDays))}',
                      res.prestockBand),
                if (res.prestockValid && inp.timegateDays > 0)
                  row(
                      tr('At timegate'),
                      inp.timegateDays >= res.prestockDays
                          ? '✓ ${tr('stocked {} early').replaceFirst('{}', trDuration(fmtDays(inp.timegateDays - res.prestockDays)))}'
                          : '✗ ${tr('short by {}').replaceFirst('{}', trDuration(fmtDays(res.prestockDays - inp.timegateDays)))}'),
                const Divider(),
                row(tr('Abode Aura (implied)'), res.abodeAura.toStringAsFixed(1)),
                row(tr('Cultivation XP / day'), res.baseXpPerDay.toStringAsFixed(0)),
                row(tr('Effective XP / day'), res.effectiveXpPerDay.toStringAsFixed(0)),
                row(tr('Pill XP / day'), res.pillXpPerDay.toStringAsFixed(0)),
                row(
                    tr('Daily XP share (pills+Respira / gem)'),
                    '${res.effectiveXpPerDay > 0 ? ((res.pillXpPerDay + res.respiraXpPerDay) / res.effectiveXpPerDay * 100).toStringAsFixed(1) : '0.0'}%'
                    ' / +${(res.gemSpeedup * 100).round()}% ${tr('speed')}'),
                row(tr('Mythic pills / day'), res.mythicPillsPerDay.toStringAsFixed(2)),
                row(tr('Pearl XP / day'), res.pearlXpPerDay.toStringAsFixed(0)),
                row(tr('Respira XP / day'), res.respiraXpPerDay.toStringAsFixed(0)),
                row(tr('XP from fruits'), res.fruitXp.toStringAsFixed(0)),
                row(tr('Fruit time saved'), trDuration(fmtDays(res.fruitDaysSaved))),
                ..._absorptionRows(context, row),
              ]),
      ),
    );
  }

  /// Absorption diagnostics rows: the grade's base absorption and the
  /// implied Strive %, shown only from Nascent Soul on (where Strive
  /// exists). Red when implied Strive exceeds the 120% cap (likely a stale
  /// absorption reading) or absorption is below base (implied negative
  /// Strive). Classification lives in [diagnoseAbsorption]; this only
  /// renders it.
  List<Widget> _absorptionRows(BuildContext context,
      Widget Function(String, String, [List<double>?, Color?]) row) {
    final diag = diagnoseAbsorption(engine, inp, res.strive);
    if (diag == null) return [];
    final t = Theme.of(context);
    final err = t.colorScheme.error;
    return [
      const Divider(),
      row(tr('Base absorption (grade)'), '${(diag.base * 100).toStringAsFixed(0)}%',
          null, diag.belowBase ? err : null),
      row(
          tr('Implied Strive'),
          diag.overCap
              ? '${(res.strive * 100).toStringAsFixed(0)}% — ${tr('over 120% cap (stale reading?)')}'
              : diag.belowBase
                  ? '${(res.strive * 100).toStringAsFixed(0)}% — ${tr("below base; Strive can't be negative")}'
                  : '${(res.strive * 100).toStringAsFixed(0)}%',
          null,
          (diag.overCap || diag.belowBase) ? err : null),
      if (diag.aboveCap && !diag.mortalWorld)
        Padding(
          padding: const EdgeInsets.only(top: 2),
          child: Text(
            tr('Strive above 120% — normal in later realms (overcap); '
                'later cap tables not modeled.'),
            style: TextStyle(fontSize: 12, color: t.hintColor),
          ),
        ),
    ];
  }
}
