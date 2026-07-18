/// Catalog shape primitives (no Flutter imports).
///
/// The ONE place that decodes the data/sources.json entry shape so a schema
/// change touches a single module per platform instead of rippling across
/// the shelf, advisor, reference tables and Vault UI. It owns the value_model
/// star math (star_upgrade, 0-based stars), effect gating (the min_level
/// ladder incl. the 'max' sentinel plus the parametric "owning is binary"
/// rule), presentational level labels, and the small effect-threshold reads
/// the advisor walks.
///
/// Twin of breakthrough_calc/catalog.py — keep the two in lockstep (the
/// shared fixtures shelf_cases.json / advisor_cases.json pin that both
/// platforms agree). See shelf.dart / shelf.py for the owned-map shapes by
/// levels.kind.
library;

const levelKinds = ['binary', 'tier', 'level', 'ladder', 'custom'];
const starUpgrade = 'star_upgrade';

/// Evaluate a value_model for owned [params]. star_upgrade: stars are 0-based
/// like the game's display (0..5 + Awakened=6); star_add[star] is the
/// tooltip's star scalar in percentage points, added to the upgrade ladder.
double modelValue(Map model, dynamic params) {
  if (model['kind'] == starUpgrade) {
    final p = params as List;
    var star = (p[0] as num).toInt();
    var upgrade = (p[1] as num).toInt();
    final stars = (model['stars'] as num).toInt();
    final maxUpgrade = (model['max_upgrade'] as num).toInt();
    star = star.clamp(0, stars - 1);
    upgrade = upgrade.clamp(0, maxUpgrade);
    final starAdd = (model['star_add'] as List)[star] as num;
    return (model['base'] as num).toDouble() +
        (model['per_upgrade'] as num).toDouble() * upgrade +
        starAdd.toDouble();
  }
  throw ArgumentError('unknown value model: ${model['kind']}');
}

/// (min, max) display bounds for a value_model, as stored (base and the
/// recorded max_value). Raw values so callers format them themselves.
(num, num) modelRange(Map model) =>
    (model['base'] as num, model['max_value'] as num);

/// Is an effect with [minLevel] active at [ownedLevel]? Handles the 'max'
/// sentinel (satisfied by owned == -1 or reaching levels.max).
bool levelOk(dynamic minLevel, dynamic ownedLevel, Map levels) {
  if (ownedLevel == null) return false;
  final owned = ownedLevel as num;
  if (minLevel == 'max') {
    final mx = levels['max'];
    return owned == -1 || (mx != null && owned >= (mx as num));
  }
  if (owned == -1) return true; // maxed satisfies every numeric threshold
  final ml = minLevel == null ? 1 : (minLevel as num);
  return owned >= ml;
}

/// Effect gating with the parametric rule folded in: owning a custom
/// (parametric) source is binary — any owned params activate every effect —
/// otherwise fall back to the min_level ladder check.
bool effectActive(Map levels, dynamic minLevel, dynamic owned) {
  if (levels['kind'] == 'custom') return owned != null;
  return levelOk(minLevel, owned, levels);
}

/// The numeric contribution of one effect at [owned], or null when the
/// amount is unrecorded (value_model wins; else literal value; else null).
double? effectValue(Map eff, dynamic owned) {
  if (eff.containsKey('value_model')) {
    return modelValue(eff['value_model'] as Map, owned);
  }
  final v = eff['value'];
  return v == null ? null : (v as num).toDouble();
}

/// Presentational owned-level label ('Tier 7' / 'lv 73' / 'max' / a ladder
/// rung / star/upgrade for custom; '' for binary).
String levelLabel(Map entry, dynamic owned) {
  final levels = entry['levels'] as Map;
  final kind = levels['kind'];
  if (kind == 'binary') return '';
  if (kind == 'ladder') {
    final labels = levels['labels'] as List;
    final i = (owned as num).toInt().clamp(1, labels.length);
    return labels[i - 1] as String;
  }
  if (kind == 'custom') {
    return (owned as List).map((p) => (p as num).toInt().toString()).join('/');
  }
  if (owned == -1) return 'max';
  final prefix = kind == 'tier' ? 'Tier ' : 'lv ';
  return '$prefix${(owned as num).toInt()}';
}

/// Sorted set of integer effect min_levels (absent defaults to 1). The 'max'
/// sentinel and any non-int thresholds are excluded.
List<int> intThresholds(Map entry) {
  final set = <int>{};
  for (final e in (entry['effects'] ?? []) as List) {
    final ml = (e as Map)['min_level'] ?? 1;
    if (ml is int) set.add(ml);
  }
  final out = set.toList()..sort();
  return out;
}

/// True when any effect gates on the 'max' sentinel.
bool hasMaxEffect(Map entry) {
  for (final e in (entry['effects'] ?? []) as List) {
    if ((e as Map)['min_level'] == 'max') return true;
  }
  return false;
}

/// Schema check for a value_model; a short message or null (the caller
/// prefixes the source id).
String? valueModelError(Map model) {
  if (model['kind'] != starUpgrade) return 'unknown value_model kind';
  final starAdd = (model['star_add'] as List);
  final sorted = [...starAdd]..sort((a, b) => (a as num).compareTo(b as num));
  if (starAdd.length != (model['stars'] as num).toInt() ||
      !_listEq(starAdd, sorted)) {
    return 'malformed star_add';
  }
  return null;
}

bool _listEq(List a, List b) {
  if (a.length != b.length) return false;
  for (var i = 0; i < a.length; i++) {
    if (a[i] != b[i]) return false;
  }
  return true;
}
