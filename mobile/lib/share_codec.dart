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
// 1. Give it a fresh short key in _compact() and a defaulted read in
//    _expand(). Never reuse or rename existing keys.
// 2. That's it: old codes lack the key and decode to the default (defaults
//    are omitted at encode time anyway), and codes from newer app versions
//    import fine on older ones — unknown keys are simply ignored. Only a
//    truly incompatible restructuring warrants bumping the 'OMV2.' prefix.
//
// WIRE-FORMAT CONTRACT: the enum indexes reference the engine data tables,
// so the ORDER of breakthrough.json's rows / gem_bonus / pill_xp / fruit_xp
// keys / rarity_names (plus _stars/_vaseInputs below) and the
// zlib+base64url framing are all part of the format. Reordering any of them
// corrupts every previously shared code; test/share_codec_test.dart pins
// each order and a golden vector.
import 'dart:convert';

import 'package:archive/archive.dart';

import 'engine.dart';

const _stars = ['0*', '1*', '2*', '3*', '4*', '5*'];
const _vaseInputs = ['Blue', 'Purple', 'Gold'];

List<String> _gems(Engine e) => (e.data['gem_bonus'] as Map).keys.cast<String>().toList();
List<String> _ranks(Engine e) => (e.data['pill_xp'] as Map).keys.cast<String>().toList();
List<String> _fruits(Engine e) => (e.data['fruit_xp'] as Map).keys.cast<String>().toList();
List<String> _rarities(Engine e) => (e.data['rarity_names'] as List).cast<String>();

Map<String, dynamic> _compact(
    Engine e, Inputs inp, List<List<dynamic>> pe, Set<String> respira) {
  int b(bool v) => v ? 1 : 0;
  final m = <String, dynamic>{
    's': e.stages().indexOf(inp.stage),
    'p': e.phasesFor(inp.stage).indexOf(inp.phase),
    'g': e.gradesFor(inp.stage, inp.phase).indexOf(inp.grade),
    'gc': inp.gradeCompletion,
    'cs': inp.cultiSpeed,
    'ar': inp.absorptionRatio,
    'ag': _gems(e).indexOf(inp.auraGem),
    'ts': inp.targetStage.isEmpty ? -1 : e.stages().indexOf(inp.targetStage),
    'tp': inp.targetPhase.isEmpty || inp.targetStage.isEmpty
        ? -1
        : e.phasesFor(inp.targetStage).indexOf(inp.targetPhase),
    'tg': inp.targetGrade.isEmpty ||
            inp.targetPhase.isEmpty ||
            inp.targetStage.isEmpty
        ? -1
        : e.gradesFor(inp.targetStage, inp.targetPhase).indexOf(inp.targetGrade),
    'td': inp.timegateDays,
    'os': inp.topStage.isEmpty ? -1 : e.stages().indexOf(inp.topStage),
    'ms': b(inp.matureServer),
    'dd': b(inp.dailiesDone),
    'rh': inp.resetInHours,
    'rd': inp.respiraPerDay,
    're': inp.respiraEvent,
    'rx': inp.respiraExp,
    'pr': _ranks(e).indexOf(inp.pillRank),
    'pl': inp.pillLimit,
    'gd': inp.goldPerDay,
    'pd': inp.purplePerDay,
    'bd': inp.bluePerDay,
    'mb': inp.markBlue,
    'mp': inp.markPurple,
    'mg': inp.markGold,
    'v': b(inp.vase),
    'vs': _stars.indexOf(inp.vaseStar),
    'vk': b(inp.vaseSkin),
    'vi': _vaseInputs.indexOf(inp.vaseInput),
    'vc': b(inp.vaseCharge),
    'mi': b(inp.mirror),
    'mis': _stars.indexOf(inp.mirrorStar),
    'mik': b(inp.mirrorSkin),
    'mic': b(inp.mirrorCharge),
    'pe': b(inp.pearl),
    'pes': _stars.indexOf(inp.pearlStar),
    'pek': b(inp.pearlSkin),
    'pex': inp.pearlXpPer10,
    'pec': b(inp.pearlCharge),
    'fr': _fruits(e).indexOf(inp.fruitRank),
    'fc': inp.fruitCount,
    'fh': b(inp.fruitHighestRank),
    'lc': inp.lvlCulti,
    'lq': inp.lvlQuality,
    'lg': inp.lvlGush,
    'er': _rarities(e).indexOf(inp.extractorRarity),
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

Map<String, dynamic> _expand(Engine e, Map<String, dynamic> m) {
  final def = _defaultInputs(e);
  String pick(List<String> l, dynamic i, String dv) {
    final n = (i as num?)?.toInt() ?? -2;
    return (n >= 0 && n < l.length) ? l[n] : dv;
  }

  double d(String k, double dv) => (m[k] as num?)?.toDouble() ?? dv;
  int ii(String k, int dv) => (m[k] as num?)?.toInt() ?? dv;
  bool b(String k, bool dv) => m.containsKey(k) ? m[k] == 1 : dv;

  final stage = pick(e.stages(), m['s'], def.stage);
  final phase = pick(e.phasesFor(stage), m['p'], e.phasesFor(stage).first);
  final grade =
      pick(e.gradesFor(stage, phase), m['g'], e.gradesFor(stage, phase).first);
  final tstage = pick(e.stages(), m['ts'], '');
  final tphase = tstage.isEmpty ? '' : pick(e.phasesFor(tstage), m['tp'], '');
  final tgrade = tstage.isEmpty || tphase.isEmpty
      ? ''
      : pick(e.gradesFor(tstage, tphase), m['tg'], '');
  return {
    'stage': stage,
    'phase': phase,
    'grade': grade,
    'grade_completion': d('gc', 0),
    'culti_speed': d('cs', 0),
    'absorption_ratio': d('ar', 0),
    'aura_gem': pick(_gems(e), m['ag'], def.auraGem),
    'target_stage': tstage,
    'target_phase': tphase,
    'target_grade': tgrade,
    'timegate_days': d('td', 0),
    'top_stage': pick(e.stages(), m['os'], ''),
    'mature_server': b('ms', def.matureServer),
    'dailies_done': b('dd', def.dailiesDone),
    'reset_in_hours': d('rh', def.resetInHours),
    'respira_per_day': d('rd', 0),
    'respira_event': d('re', 0),
    'respira_exp': d('rx', 0),
    'pill_rank': pick(_ranks(e), m['pr'], def.pillRank),
    'pill_limit': d('pl', 0),
    'gold_per_day': d('gd', 0),
    'purple_per_day': d('pd', 0),
    'blue_per_day': d('bd', 0),
    'mark_blue': d('mb', 0),
    'mark_purple': d('mp', 0),
    'mark_gold': d('mg', 0),
    'vase': b('v', false),
    'vase_star': pick(_stars, m['vs'], def.vaseStar),
    'vase_skin': b('vk', false),
    'vase_input': pick(_vaseInputs, m['vi'], def.vaseInput),
    'vase_charge': b('vc', def.vaseCharge),
    'mirror': b('mi', false),
    'mirror_star': pick(_stars, m['mis'], def.mirrorStar),
    'mirror_skin': b('mik', false),
    'mirror_charge': b('mic', def.mirrorCharge),
    'pearl': b('pe', false),
    'pearl_star': pick(_stars, m['pes'], def.pearlStar),
    'pearl_skin': b('pek', false),
    'pearl_xp_per_10': d('pex', 0),
    'pearl_charge': b('pec', def.pearlCharge),
    'fruit_rank': pick(_fruits(e), m['fr'], def.fruitRank),
    'fruit_count': d('fc', 0),
    'fruit_highest_rank': b('fh', false),
    'lvl_culti': ii('lc', 0),
    'lvl_quality': ii('lq', 0),
    'lvl_gush': ii('lg', 0),
    'extractor_rarity': pick(_rarities(e), m['er'], def.extractorRarity),
    'pe_sources': m['P'] as List? ?? [],
    'respira_sources': m['R'] as List? ?? [],
  };
}
