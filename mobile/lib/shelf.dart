/// Sources Shelf: pure derivation logic (no Flutter imports).
///
/// Dart twin of breakthrough_calc/shelf.py — keep in lockstep (pinned by
/// the shared fixture mobile/test/shelf_cases.json, which both platforms'
/// test suites run). See shelf.py's module docstring for the target-mode
/// taxonomy and owned-map shapes.
library;

import 'catalog.dart';

class Contribution {
  final String sourceId;
  final String name;
  final String levelLabel;
  final double value;
  final String dataStatus;
  final String note;
  const Contribution({
    required this.sourceId,
    required this.name,
    required this.levelLabel,
    required this.value,
    required this.dataStatus,
    required this.note,
  });
}

class Derived {
  final double total;
  final List<Contribution> contributions;
  final List<List<dynamic>> custom; // [label, value] extras
  final bool incomplete;
  const Derived({
    required this.total,
    this.contributions = const [],
    this.custom = const [],
    this.incomplete = false,
  });
}

/// shelf = {'owned': {id: level|params}, 'custom': {target: [[label, v]]}}
/// -> {targetId: Derived}. Mirrors shelf.py derive() exactly.
Map<String, Derived> derive(Map catalog, Map shelf) {
  final targets = (catalog['targets'] ?? {}) as Map;
  final categories = (catalog['categories'] ?? []) as List;
  final catOrder = {
    for (var i = 0; i < categories.length; i++)
      (categories[i] as Map)['id']: i
  };
  final byId = <String, Map>{
    for (final s in (catalog['sources'] ?? []) as List)
      (s as Map)['id'] as String: s
  };
  final buckets = <String, List<Contribution>>{};
  final incomplete = <String, bool>{};

  final owned = (shelf['owned'] ?? {}) as Map;
  owned.forEach((sid, ownedLevel) {
    final entry = byId[sid];
    if (entry == null) return; // version-skew passenger
    final levels = entry['levels'] as Map;
    for (final effRaw in (entry['effects'] ?? []) as List) {
      final eff = effRaw as Map;
      final tid = eff['target'] as String;
      final mode = ((targets[tid] ?? {}) as Map)['mode'];
      if (mode == 'display_embedded') continue; // guarded
      if (!effectActive(levels, eff['min_level'], ownedLevel)) continue;
      final value = effectValue(eff, ownedLevel);
      if (value == null && mode == 'raw_additive') incomplete[tid] = true;
      if (mode != 'raw_additive') continue; // info carries no numbers
      buckets.putIfAbsent(tid, () => []).add(Contribution(
            sourceId: sid as String,
            name: entry['name'] as String,
            levelLabel: levelLabel(entry, ownedLevel),
            value: value ?? 0.0,
            dataStatus: (eff['data_status'] ??
                entry['data_status'] ??
                'exact') as String,
            note: (eff['note'] ?? '') as String,
          ));
    }
  });

  final customAll = (shelf['custom'] ?? {}) as Map;
  final out = <String, Derived>{};
  final allTargets = <String>{
    ...buckets.keys,
    ...incomplete.keys,
    ...customAll.keys.cast<String>(),
  };
  for (final tid in allTargets) {
    if (((targets[tid] ?? {}) as Map)['mode'] != 'raw_additive') continue;
    final contribs = [...(buckets[tid] ?? <Contribution>[])]..sort((a, b) {
        final ca = catOrder[byId[a.sourceId]!['category']] ?? 99;
        final cb = catOrder[byId[b.sourceId]!['category']] ?? 99;
        if (ca != cb) return ca.compareTo(cb);
        if (a.value != b.value) return b.value.compareTo(a.value);
        return a.name.compareTo(b.name);
      });
    final custom = [
      for (final row in (customAll[tid] ?? []) as List)
        [(row as List)[0].toString(), (row[1] as num).toDouble()]
    ];
    var total = 0.0;
    for (final c in contribs) {
      total += c.value;
    }
    for (final row in custom) {
      total += row[1] as double;
    }
    out[tid] = Derived(
      total: total,
      contributions: contribs,
      custom: custom,
      incomplete: incomplete[tid] ?? false,
    );
  }
  return out;
}

/// Field value under the precedence: manual override > base + derived.
double effective(Derived? derived, double? override, {double base = 0.0}) {
  if (override != null) return override;
  return base + (derived?.total ?? 0.0);
}

/// One-time mapping of the old inputs into shelf state. Mirrors shelf.py
/// migrate_legacy(): returns [owned, custom, notes]. Callers must ALSO
/// rebase base:"user" targets so field values stay identical (UI layer).
List<dynamic> migrateLegacy(
    List<List<dynamic>> peRows, List<String> respiraChecked, Map catalog) {
  final alias = <String, List<dynamic>>{};
  for (final sRaw in (catalog['sources'] ?? []) as List) {
    final s = sRaw as Map;
    for (final aRaw in (s['legacy'] ?? []) as List) {
      final a = aRaw as Map;
      alias['${a['catalog']}|${a['name']}'] = [s['id'], a];
    }
  }
  final owned = <String, dynamic>{};
  final custom = <String, List<List<dynamic>>>{};
  final notes = <String>[];

  void claim(String sid, dynamic level) {
    final cur = owned[sid];
    if (cur == null ||
        (cur != -1 && (level == -1 || (level as num) > (cur as num)))) {
      owned[sid] = level;
    }
  }

  for (final row in peRows) {
    final name = row[0] as String;
    final pct = (row[1] as num).toDouble();
    final hit = alias['pe|$name'];
    if (hit == null) {
      custom.putIfAbsent('pill_effect', () => []).add([name, pct]);
      continue;
    }
    final a = hit[1] as Map;
    if (a['parametric'] == true) {
      custom.putIfAbsent('pill_effect', () => []).add([name, pct]);
      notes.add('$name: re-select it on the shelf to track its star and '
          'upgrade level automatically.');
      continue;
    }
    claim(hit[0] as String, a['implies_level']);
  }
  for (final name in respiraChecked) {
    final hit = alias['respira|$name'];
    if (hit != null) {
      claim(hit[0] as String, (hit[1] as Map)['implies_level']);
    }
  }
  return [owned, custom, notes];
}
