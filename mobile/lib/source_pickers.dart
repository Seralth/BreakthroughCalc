/// The inline pill-effect row editor. The Vault manages catalog-known
/// rows; these are free-typed extras (event buffs, treasures). State (the
/// lists) lives with the caller; structural changes go through callbacks.
library;

import 'package:flutter/material.dart';

import 'form_widgets.dart';
import 'i18n.dart';

/// Editor for the pill-effect source rows ([name, percent] entries plus a
/// parallel stable-id list used as row keys — see the form-refresh fix).
Widget peSourcesEditor(
  BuildContext context,
  List<List<dynamic>> sources,
  List<int> rowIds, {
  required VoidCallback recalc,
  required void Function(int index) onRemove,
  required VoidCallback onAdd,
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
    ]),
  ]);
}
