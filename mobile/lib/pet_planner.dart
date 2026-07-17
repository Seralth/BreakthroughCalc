/// Interactive pet exchange planner, embedded in Guide → Pets. Guide pages
/// are plain builder functions with no state plumbing, so the planner is
/// self-contained: it loads assets/data/pets.json itself and persists its
/// inputs in its own 'pets_v1' prefs blob (math lives in pets.dart).
library;

import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart' show rootBundle;
import 'package:shared_preferences/shared_preferences.dart';

import 'doc_widgets.dart';
import 'form_widgets.dart';
import 'i18n.dart';
import 'pets.dart';

class PetPlanner extends StatefulWidget {
  const PetPlanner({super.key});

  @override
  State<PetPlanner> createState() => _PetPlannerState();
}

class _PetPlannerState extends State<PetPlanner> {
  Map? _catalog; // null until _load finishes; {} when the asset is missing
  final Map<String, int> _owned = {};
  final Map<String, int> _essences = {};
  SharedPreferences? _prefs;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    Map cat = {};
    try {
      cat = jsonDecode(await rootBundle.loadString('assets/data/pets.json'))
          as Map;
    } catch (_) {}
    try {
      _prefs = await SharedPreferences.getInstance();
      final raw = _prefs?.getString('pets_v1');
      if (raw != null) {
        final m = jsonDecode(raw) as Map;
        ((m['owned'] as Map?) ?? {})
            .forEach((k, v) => _owned[k as String] = (v as num).toInt());
        ((m['essences'] as Map?) ?? {})
            .forEach((k, v) => _essences[k as String] = (v as num).toInt());
      }
    } catch (_) {} // no prefs backend (tests): the planner just won't persist
    if (mounted) setState(() => _catalog = cat);
  }

  void _edit(void Function() f) {
    setState(f);
    _prefs?.setString(
        'pets_v1', jsonEncode({'owned': _owned, 'essences': _essences}));
  }

  /// Two inputs per row keeps the fields finger-sized without eating the
  /// page; an odd trailing field gets an empty twin.
  List<Widget> _grid(List<Widget> fields) => [
        for (var i = 0; i < fields.length; i += 2)
          Row(children: [
            Expanded(child: fields[i]),
            const SizedBox(width: 12),
            Expanded(
                child: i + 1 < fields.length
                    ? fields[i + 1]
                    : const SizedBox()),
          ]),
      ];

  @override
  Widget build(BuildContext context) {
    final cat = _catalog;
    if (cat == null) return const SizedBox(height: 48);
    final pets = ((cat['pets'] ?? []) as List).cast<Map>();
    if (pets.isEmpty) return const SizedBox();
    final essences = ((cat['essences'] ?? []) as List).cast<Map>();
    final plans = planPets(cat, _owned, _essences);

    return formGroup(context, tr('Pet planner'), [
      Text(
        tr('Enter what you own once; each pet row then shows the copies '
            'and rarity you could reach by going all-in on that pet.'),
        style: TextStyle(fontSize: 12, color: Theme.of(context).hintColor),
      ),
      const SizedBox(height: 4),
      Text(tr('Pets owned'),
          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
      ..._grid([
        for (final p in pets)
          numIntField(p['name'] as String, _owned[p['id']] ?? 0,
              (v) => _edit(() => _owned[p['id'] as String] = v < 0 ? 0 : v)),
      ]),
      const SizedBox(height: 4),
      Text(tr('Rare essences owned'),
          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
      ..._grid([
        for (final e in essences)
          numIntField(e['name'] as String, _essences[e['id']] ?? 0,
              (v) => _edit(() => _essences[e['id'] as String] = v < 0 ? 0 : v)),
      ]),
      docTable(
        context,
        tr('Going all-in on one pet'),
        [tr('Pet'), tr('Copies'), tr('Rarity'), tr('Pet realm')],
        [
          for (final p in pets)
            [
              p['name'] as String,
              '${plans[p['id']]!.copies}',
              plans[p['id']]!.rarity ?? '—',
              plans[p['id']]!.realm ?? '—',
            ],
        ],
      ),
    ]);
  }
}
