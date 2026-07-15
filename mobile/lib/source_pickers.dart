/// Pill-effect and Respira source catalogs: the inline pill-effect row
/// editor, the two bottom-sheet pickers, and the star-upgrade prompt.
/// State (the lists and Inputs) lives with the caller; structural changes
/// go through the provided callbacks.
library;

import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart' show rootBundle;

import 'engine.dart';
import 'form_widgets.dart';
import 'i18n.dart';

/// Load a JSON-list data catalog from the bundled assets; missing or
/// corrupt files (e.g. a build packaged without them) yield [].
Future<List<dynamic>> loadCatalog(String asset) async {
  try {
    return jsonDecode(await rootBundle.loadString(asset)) as List;
  } catch (_) {
    return [];
  }
}

/// Editor for the pill-effect source rows ([name, percent] entries plus a
/// parallel stable-id list used as row keys — see the form-refresh fix).
Widget peSourcesEditor(
  BuildContext context,
  List<List<dynamic>> sources,
  List<int> rowIds, {
  required VoidCallback recalc,
  required void Function(int index) onRemove,
  required VoidCallback onAdd,
  required VoidCallback onCatalog,
}) {
  final total = sources.fold(0.0, (a, s) => a + (s[1] as num));
  return Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
    for (var i = 0; i < sources.length; i++)
      Padding(
        key: ValueKey(rowIds[i]),
        padding: const EdgeInsets.symmetric(vertical: 3),
        child: Row(children: [
          Expanded(
            child: TextFormField(
              initialValue: sources[i][0] as String,
              decoration: InputDecoration(labelText: tr('Pill-effect source')),
              onChanged: (t) => sources[i][0] = t,
            ),
          ),
          const SizedBox(width: 8),
          SizedBox(
            width: 80,
            child: TextFormField(
              initialValue: fmtNum((sources[i][1] as num).toDouble()),
              keyboardType: const TextInputType.numberWithOptions(decimal: true),
              decoration: const InputDecoration(labelText: '%'),
              onChanged: (t) { sources[i][1] = double.tryParse(t) ?? 0; recalc(); },
            ),
          ),
          IconButton(
            icon: const Icon(Icons.close),
            onPressed: () => onRemove(i),
          ),
        ]),
      ),
    Row(children: [
      Expanded(child: Text('${tr('Pill effect total')}: ${total.toStringAsFixed(2)}%',
          style: TextStyle(color: Theme.of(context).hintColor))),
      TextButton.icon(
        icon: const Icon(Icons.add),
        label: Text(tr('Add')),
        onPressed: onAdd,
      ),
      TextButton.icon(
        icon: const Icon(Icons.list),
        label: Text(tr('Catalog')),
        onPressed: onCatalog,
      ),
    ]),
  ]);
}

/// Bottom-sheet pill-effect catalog picker. Sources already in [existing]
/// are hidden so they can't be picked twice; remove them via their row's
/// delete button. A successful pick (including the star-upgrade prompt)
/// reports (name, percent) through [onPicked].
Future<void> pickCatalogSource(
  BuildContext context,
  List<dynamic> catalog,
  List<List<dynamic>> existing, {
  required void Function(String name, double value) onPicked,
}) async {
  final added = {for (final e in existing) e[0] as String};
  final choice = await showModalBottomSheet<Map<String, dynamic>>(
    context: context,
    builder: (_) => ListView(
      children: [
        for (final s in catalog.cast<Map<String, dynamic>>())
          if (!added.contains(s['name']))
          ListTile(
            title: Text(s['name'] as String),
            trailing: Text(((s['percent'] as num?) ?? 0) == 0 ? tr('varies') : '${s['percent']}%'),
            subtitle: s['note'] != null ? Text(s['note'] as String, style: const TextStyle(fontSize: 11)) : null,
            onTap: () => Navigator.pop(context, s),
          ),
      ],
    ),
  );
  if (choice == null || !context.mounted) return;
  double? value;
  final prompt = choice['prompt'] as Map<String, dynamic>?;
  if (prompt != null && prompt['kind'] == 'star_upgrade') {
    value = await _askStarUpgrade(context, choice['name'] as String, prompt);
    if (value == null) return; // user cancelled
  } else {
    value = ((choice['percent'] as num?) ?? 0).toDouble();
  }
  onPicked(choice['name'] as String, value);
}

/// Small dialog matching the in-game curio upgrade screen: pick star and
/// upgrade level, return the computed pill-effect %.
Future<double?> _askStarUpgrade(
    BuildContext context, String name, Map<String, dynamic> p) {
  final base = (p['base'] as num).toDouble();
  final perUpgrade = (p['per_upgrade'] as num).toDouble();
  final maxUpgrade = p['max_upgrade'] as int;
  final stars = p['stars'] as int;
  final starAdd = (p['star_add'] as List).cast<num>();
  double valueFor(int star, int upgrade) =>
      base + perUpgrade * upgrade + starAdd[star - 1].toDouble();

  var star = 1;
  var upgrade = 0;
  return showDialog<double>(
    context: context,
    builder: (ctx) => StatefulBuilder(
      builder: (ctx, setDlg) => AlertDialog(
        title: Text(name),
        content: Column(mainAxisSize: MainAxisSize.min, children: [
          DropdownButtonFormField<int>(
            initialValue: star,
            decoration: InputDecoration(labelText: tr('Star')),
            items: [for (var i = 1; i <= stars; i++) DropdownMenuItem(value: i, child: Text('$i★'))],
            onChanged: (v) => setDlg(() => star = v!),
          ),
          DropdownButtonFormField<int>(
            initialValue: upgrade,
            decoration: InputDecoration(labelText: tr('Upgrade level')),
            items: [for (var i = 0; i <= maxUpgrade; i++) DropdownMenuItem(value: i, child: Text('$i'))],
            onChanged: (v) => setDlg(() => upgrade = v!),
          ),
          const SizedBox(height: 8),
          Text(
            '${tr('Cultivation Pill Effect')}: ${valueFor(star, upgrade).toStringAsFixed(1)}%',
            style: TextStyle(color: Theme.of(ctx).hintColor),
          ),
        ]),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: Text(tr('Cancel'))),
          TextButton(
            onPressed: () => Navigator.pop(
                ctx, double.parse(valueFor(star, upgrade).toStringAsFixed(1))),
            child: Text(tr('OK')),
          ),
        ],
      ),
    ),
  );
}

/// Bottom-sheet catalog of daily Respira attempt sources. 'attempt' entries
/// toggle and add/subtract from the attempts input; other kinds are shown
/// read-only so users learn them without double-counting.
void pickRespiraSources(
  BuildContext context,
  List<dynamic> catalog,
  Set<String> selected, {
  required Inputs inp,
  required TextEditingController respiraCtrl,
  required VoidCallback recalc,
}) {
  showModalBottomSheet<void>(
    context: context,
    builder: (_) => StatefulBuilder(
      builder: (ctx, setSheet) => ListView(
        children: [
          for (final s in catalog.cast<Map<String, dynamic>>())
            if (s['kind'] == 'attempt')
              CheckboxListTile(
                value: selected.contains(s['name'] as String),
                title: Text(s['name'] as String),
                subtitle: s['note'] != null
                    ? Text(s['note'] as String, style: const TextStyle(fontSize: 11))
                    : null,
                secondary: Text('+${s['value']}'),
                onChanged: (v) {
                  final name = s['name'] as String;
                  final delta = (s['value'] as num).toDouble();
                  setSheet(() {
                    if (v == true && selected.add(name)) {
                      inp.respiraPerDay += delta;
                    } else if (v != true && selected.remove(name)) {
                      inp.respiraPerDay -= delta;
                      if (inp.respiraPerDay < 0) inp.respiraPerDay = 0;
                    }
                  });
                  respiraCtrl.text = fmtNum(inp.respiraPerDay);
                  recalc();
                },
              )
            else
              ListTile(
                enabled: false,
                title: Text(s['name'] as String),
                subtitle: s['note'] != null
                    ? Text(s['note'] as String, style: const TextStyle(fontSize: 11))
                    : null,
                trailing: Text(s['kind'] == 'exp_pct' ? tr('info') : tr('pill input')),
              ),
        ],
      ),
    ),
  );
}
