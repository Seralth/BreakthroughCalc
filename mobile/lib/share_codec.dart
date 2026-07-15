// Shareable build codes: 'OMV2.' + base64url(zlib(JSON of a compact map)).
// Enum-ish fields (stage/phase/grade, gem, ranks, stars, rarity) are stored
// as indexes into the engine's own data tables, fields still at their
// defaults are omitted, and the result is deflated. Catalog source names in
// P/R are kept as full strings so codes survive catalog reordering.
//
// decodeBuildCode returns the long-key map (same shape as the persisted
// 'inputs_v1' prefs blob, incl. pe_sources/respira_sources) or null if the
// code is unreadable.
//
// FORWARD COMPATIBILITY — adding a new input feature:
// 1. Give it a fresh short key: add one _F entry to _fields below (the
//    field also needs its long key in Inputs.toMap/fromMap). Never reuse or
//    rename existing short keys.
// 2. That's it: old codes lack the key and decode to the default (defaults
//    are omitted at encode time anyway), and codes from newer app versions
//    import fine on older ones — unknown keys are simply ignored. Only a
//    truly incompatible restructuring warrants bumping the 'OMV2.' prefix.
//
// WIRE-FORMAT CONTRACT: the enum indexes reference the engine data tables,
// so the ORDER of breakthrough.json's rows / gem_bonus / pill_xp / fruit_xp
// keys / rarity_names (plus engine.dart's starLevels/vaseInputKinds) and the
// zlib+base64url framing are all part of the format. Reordering any of them
// corrupts every previously shared code; test/share_codec_test.dart pins
// each order and a golden vector.
import 'dart:convert';

import 'package:archive/archive.dart';

import 'engine.dart';

List<String> _gems(Engine e) => (e.data['gem_bonus'] as Map).keys.cast<String>().toList();
List<String> _ranks(Engine e) => (e.data['pill_xp'] as Map).keys.cast<String>().toList();
List<String> _fruits(Engine e) => (e.data['fruit_xp'] as Map).keys.cast<String>().toList();
List<String> _rarities(Engine e) => (e.data['rarity_names'] as List).cast<String>();

List<String> _stars(Engine e) => starLevels;
List<String> _vaseInputs(Engine e) => vaseInputKinds;

/// One short<->long key table shared by encode and decode. `kind` drives
/// both directions ('d' double, 'i' int, 'b' bool-as-0/1, 'e' enum index
/// into `src`), so the two sides can never drift apart.
///
/// Stage/phase/grade and the target/top-stage keys ('s','p','g','ts','tp',
/// 'tg','os') are handled separately: their decode cascades (a phase index
/// is relative to the decoded stage) and empty selections encode as -1.
class _F {
  final String short;
  final String long;
  final String kind;
  final List<String> Function(Engine)? src;
  const _F(this.short, this.long, this.kind, [this.src]);
}

const List<_F> _fields = [
  _F('gc', 'grade_completion', 'd'),
  _F('cs', 'culti_speed', 'd'),
  _F('ar', 'absorption_ratio', 'd'),
  _F('ag', 'aura_gem', 'e', _gems),
  _F('td', 'timegate_days', 'd'),
  _F('ms', 'mature_server', 'b'),
  _F('dd', 'dailies_done', 'b'),
  _F('rh', 'reset_in_hours', 'd'),
  _F('rd', 'respira_per_day', 'd'),
  _F('re', 'respira_event', 'd'),
  _F('rx', 'respira_exp', 'd'),
  _F('pr', 'pill_rank', 'e', _ranks),
  _F('pl', 'pill_limit', 'd'),
  _F('gd', 'gold_per_day', 'd'),
  _F('pd', 'purple_per_day', 'd'),
  _F('bd', 'blue_per_day', 'd'),
  _F('mb', 'mark_blue', 'd'),
  _F('mp', 'mark_purple', 'd'),
  _F('mg', 'mark_gold', 'd'),
  _F('v', 'vase', 'b'),
  _F('vs', 'vase_star', 'e', _stars),
  _F('vk', 'vase_skin', 'b'),
  _F('vi', 'vase_input', 'e', _vaseInputs),
  _F('vc', 'vase_charge', 'b'),
  _F('mi', 'mirror', 'b'),
  _F('mis', 'mirror_star', 'e', _stars),
  _F('mik', 'mirror_skin', 'b'),
  _F('mic', 'mirror_charge', 'b'),
  _F('pe', 'pearl', 'b'),
  _F('pes', 'pearl_star', 'e', _stars),
  _F('pek', 'pearl_skin', 'b'),
  _F('pex', 'pearl_xp_per_10', 'd'),
  _F('pec', 'pearl_charge', 'b'),
  _F('fr', 'fruit_rank', 'e', _fruits),
  _F('fc', 'fruit_count', 'd'),
  _F('fh', 'fruit_highest_rank', 'b'),
  _F('lc', 'lvl_culti', 'i'),
  _F('lq', 'lvl_quality', 'i'),
  _F('lg', 'lvl_gush', 'i'),
  _F('er', 'extractor_rarity', 'e', _rarities),
];

Map<String, dynamic> _compact(
    Engine e, Inputs inp, List<List<dynamic>> pe, Set<String> respira) {
  final long = inp.toMap();
  final m = <String, dynamic>{
    's': e.stages().indexOf(inp.stage),
    'p': e.phasesFor(inp.stage).indexOf(inp.phase),
    'g': e.gradesFor(inp.stage, inp.phase).indexOf(inp.grade),
    'ts': inp.targetStage.isEmpty ? -1 : e.stages().indexOf(inp.targetStage),
    'tp': inp.targetPhase.isEmpty || inp.targetStage.isEmpty
        ? -1
        : e.phasesFor(inp.targetStage).indexOf(inp.targetPhase),
    'tg': inp.targetGrade.isEmpty ||
            inp.targetPhase.isEmpty ||
            inp.targetStage.isEmpty
        ? -1
        : e.gradesFor(inp.targetStage, inp.targetPhase).indexOf(inp.targetGrade),
    'os': inp.topStage.isEmpty ? -1 : e.stages().indexOf(inp.topStage),
    for (final f in _fields)
      f.short: switch (f.kind) {
        'b' => (long[f.long] as bool) ? 1 : 0,
        'e' => f.src!(e).indexOf(long[f.long] as String),
        _ => long[f.long], // 'd' / 'i': raw number
      },
    'P': pe,
    'R': respira.toList()..sort(),
  };
  return m;
}

Inputs _defaultInputs(Engine e) {
  final inp = Inputs();
  inp.stage = e.stages().first;
  inp.phase = e.phasesFor(inp.stage).first;
  inp.grade = e.gradesFor(inp.stage, inp.phase).first;
  inp.pillRank = _ranks(e).first;
  return inp;
}

String encodeBuildCode(
    Engine e, Inputs inp, List<List<dynamic>> pe, Set<String> respira) {
  final m = _compact(e, inp, pe, respira);
  final def = _compact(e, _defaultInputs(e), [], {});
  def.forEach((k, v) {
    if (jsonEncode(m[k]) == jsonEncode(v)) m.remove(k);
  });
  final bytes =
      const ZLibEncoder().encode(utf8.encode(jsonEncode(m)), level: 9);
  return 'OMV2.${base64UrlEncode(bytes)}';
}

Map<String, dynamic>? decodeBuildCode(Engine e, String code) {
  final body = code.trim();
  if (!body.startsWith('OMV2.')) return null;
  try {
    final bytes = base64Url.decode(base64Url.normalize(body.substring(5)));
    final m = jsonDecode(utf8.decode(const ZLibDecoder().decodeBytes(bytes)))
        as Map<String, dynamic>;
    return _expand(e, m);
  } catch (_) {
    return null;
  }
}

String _pick(List<String> l, dynamic i, String dv) {
  final n = (i as num?)?.toInt() ?? -2;
  return (n >= 0 && n < l.length) ? l[n] : dv;
}

Map<String, dynamic> _expand(Engine e, Map<String, dynamic> m) {
  // Start from the full default long-key map and overlay only the decoded
  // short keys — absent keys therefore decode to the defaults by
  // construction, and the output shape always matches the prefs blob.
  // pill_effect is derived from pe_sources at recalc time and has never
  // been wire data, so it is not part of the decode output either.
  final out = _defaultInputs(e).toMap()..remove('pill_effect');

  final stage = _pick(e.stages(), m['s'], out['stage'] as String);
  final phase = _pick(e.phasesFor(stage), m['p'], e.phasesFor(stage).first);
  final grade =
      _pick(e.gradesFor(stage, phase), m['g'], e.gradesFor(stage, phase).first);
  final tstage = _pick(e.stages(), m['ts'], '');
  final tphase = tstage.isEmpty ? '' : _pick(e.phasesFor(tstage), m['tp'], '');
  final tgrade = tstage.isEmpty || tphase.isEmpty
      ? ''
      : _pick(e.gradesFor(tstage, tphase), m['tg'], '');
  out['stage'] = stage;
  out['phase'] = phase;
  out['grade'] = grade;
  out['target_stage'] = tstage;
  out['target_phase'] = tphase;
  out['target_grade'] = tgrade;
  out['top_stage'] = _pick(e.stages(), m['os'], '');

  for (final f in _fields) {
    switch (f.kind) {
      case 'd':
        final v = m[f.short];
        if (v != null) out[f.long] = (v as num).toDouble();
      case 'i':
        final v = m[f.short];
        if (v != null) out[f.long] = (v as num).toInt();
      case 'b':
        // A present-but-null value decodes to false (legacy semantics),
        // not to the default.
        if (m.containsKey(f.short)) out[f.long] = m[f.short] == 1;
      case 'e':
        if (m.containsKey(f.short)) {
          out[f.long] = _pick(f.src!(e), m[f.short], out[f.long] as String);
        }
    }
  }

  out['pe_sources'] = m['P'] as List? ?? [];
  out['respira_sources'] = m['R'] as List? ?? [];
  return out;
}
