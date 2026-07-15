/// Generic calculator form building blocks (group card, labeled inputs).
/// Pure presentation: state lives with the caller, wired through callbacks.
library;

import 'package:flutter/material.dart';

import 'engine.dart' show starLevels;
import 'i18n.dart';

/// '' for zero; integers without a trailing '.0'; float noise stripped.
String fmtNum(double v) {
  if (v == 0) return '';
  final r = double.parse(v.toStringAsFixed(4)); // strip float noise
  if (r == r.roundToDouble()) return r.toInt().toString();
  return r.toString();
}

Widget formGroup(BuildContext context, String title, List<Widget> children) =>
    Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
          Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Text(title, style: Theme.of(context).textTheme.titleMedium),
          ),
          ...children,
        ]),
      ),
    );

/// [display] maps an INTERNAL item key to its localized label; the dropdown
/// value (and everything persisted) stays the internal key.
Widget formDropdown(String label, String value, List<String> items,
        ValueChanged<String?> onChanged,
        {String Function(String)? display}) =>
    Padding(
      padding: const EdgeInsets.symmetric(vertical: 5),
      child: DropdownButtonFormField<String>(
        initialValue: items.contains(value) ? value : items.first,
        isExpanded: true,
        decoration: InputDecoration(labelText: label),
        items: [
          for (final s in items)
            DropdownMenuItem(value: s, child: Text(display == null ? s : display(s)))
        ],
        onChanged: onChanged,
      ),
    );

Widget numCtrlField(String label, TextEditingController ctrl,
        ValueChanged<double> onChanged) =>
    Padding(
      padding: const EdgeInsets.symmetric(vertical: 5),
      child: TextField(
        controller: ctrl,
        keyboardType: const TextInputType.numberWithOptions(decimal: true),
        decoration: InputDecoration(labelText: label),
        onChanged: (t) => onChanged(double.tryParse(t) ?? 0),
      ),
    );

Widget numField(String label, double value, ValueChanged<double> onChanged) =>
    Padding(
      padding: const EdgeInsets.symmetric(vertical: 5),
      child: TextFormField(
        initialValue: fmtNum(value),
        keyboardType: const TextInputType.numberWithOptions(decimal: true),
        decoration: InputDecoration(labelText: label),
        onChanged: (t) => onChanged(double.tryParse(t) ?? 0),
      ),
    );

Widget numIntField(String label, int value, ValueChanged<int> onChanged) =>
    Padding(
      padding: const EdgeInsets.symmetric(vertical: 5),
      child: TextFormField(
        initialValue: value == 0 ? '' : '$value',
        keyboardType: TextInputType.number,
        decoration: InputDecoration(labelText: label),
        onChanged: (t) => onChanged(int.tryParse(t) ?? 0),
      ),
    );

Widget checkField(String label, bool value, ValueChanged<bool> onChanged) =>
    Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: CheckboxListTile(
        contentPadding: EdgeInsets.zero,
        controlAffinity: ListTileControlAffinity.leading,
        dense: true,
        title: Text(label),
        value: value,
        onChanged: (v) => onChanged(v ?? false),
      ),
    );

/// One Creation Artifact block: enable checkbox + star dropdown, with the
/// Skin / Daily charge options only shown while enabled. Every change also
/// triggers [recalc].
Widget artifactField(String name, bool on, String star, bool skin, bool charge,
    ValueChanged<bool> onOn, ValueChanged<String> onStar,
    ValueChanged<bool> onSkin, ValueChanged<bool> onCharge,
    {required VoidCallback recalc}) {
  // Labeled option so Skin vs Charge are never ambiguous (no hover tooltips
  // on touch). Options only show when the artifact is enabled.
  Widget labeledCheck(String label, bool value, ValueChanged<bool> cb) =>
      InkWell(
        onTap: () { cb(!value); recalc(); },
        child: Padding(
          padding: const EdgeInsets.only(right: 8),
          child: Row(mainAxisSize: MainAxisSize.min, children: [
            Checkbox(
              value: value,
              visualDensity: VisualDensity.compact,
              onChanged: (v) { cb(v ?? false); recalc(); },
            ),
            Text(label),
          ]),
        ),
      );

  return Padding(
    padding: const EdgeInsets.symmetric(vertical: 4),
    child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Row(children: [
        Expanded(
          child: Row(children: [
            Checkbox(value: on, onChanged: (v) { onOn(v ?? false); recalc(); }),
            Expanded(child: Text(name, overflow: TextOverflow.ellipsis)),
          ]),
        ),
        SizedBox(
          width: 78,
          child: DropdownButtonFormField<String>(
            initialValue: star,
            isExpanded: true,
            decoration: InputDecoration(labelText: tr('Star')),
            items: [for (final s in starLevels) DropdownMenuItem(value: s, child: Text(s))],
            onChanged: on ? (v) { onStar(v!); recalc(); } : null,
          ),
        ),
      ]),
      if (on)
        Padding(
          padding: const EdgeInsets.only(left: 24, bottom: 4),
          child: Row(children: [
            labeledCheck(tr('Skin'), skin, onSkin),
            labeledCheck(tr('Daily charge'), charge, onCharge),
          ]),
        ),
    ]),
  );
}
