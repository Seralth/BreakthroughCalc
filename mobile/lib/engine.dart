/// Breakthrough calculator engine — Dart port of breakthrough_calc/engine.py.
///
/// Faithful translation kept 1:1 with the Python engine so both share the same
/// data tables and regression fixtures. See the Python module for the full
/// model derivation; comments here only note Dart-specific concerns.
library;

import 'dart:math' as math;

const double tickSeconds = 8.0;

// Respira crit roll (cfg_us_calc yunqi_crit): multiplier x weight/1000.
const List<List<double>> _respiraCrit = [
  [1, 0.60],
  [2, 0.30],
  [5, 0.08],
  [10, 0.02],
];
final double respiraCritMean =
    _respiraCrit.fold(0.0, (a, e) => a + e[0] * e[1]); // 1.8
final double respiraCritVar =
    _respiraCrit.fold(0.0, (a, e) => a + e[1] * e[0] * e[0]) -
        respiraCritMean * respiraCritMean; // 2.56
const double _bandZ = 1.645; // ~90% (P5..P95) interval

// Fruit pity: a gush is guaranteed within N fruits of the last gush (SOFT
// pity — any gush resets the counter; verified in-game 2026-07-10).
const int gushGuaranteeEvery = 6;

// pill_xp row layout: each rank maps to [gold, purple, blue, mythic]
// (data/breakthrough.json; e.g. 1R = [1500, 750, 400, 3000]). Use these
// consts anywhere a pill row is indexed so the color->column mapping is
// spelled out.
const int pillGold = 0;
const int pillPurple = 1;
const int pillBlue = 2;
const int pillMythic = 3;

// Artifact star levels and Vase input-pill kinds. The OMV2 share codec
// stores INDEXES into these lists, so their order is part of the wire
// format — never reorder (share_codec_test.dart pins usage via the golden
// vector).
const List<String> starLevels = ['0*', '1*', '2*', '3*', '4*', '5*'];
const List<String> vaseInputKinds = ['Blue', 'Purple', 'Gold'];

const Map<int, double> _striveShapeTbl = {
  1: 0.15, 2: 0.20, 3: 0.30, 4: 0.40, 5: 0.50, 6: 0.60, 7: 0.70,
};
// (min level gap, tier) — new_sub_lv_exp_accelerate_array, world level >= 30.
const List<List<double>> _striveSubShape = [
  [60, 0.70],
  [50, 0.30],
  [40, 0.20],
];
const Map<int, double> _striveExtraRank = {1: 0.30, 2: 0.50};

double _striveShape(int gap) {
  if (gap <= 0) return 0.0;
  if (gap >= 7) return 0.70;
  return _striveShapeTbl[gap]!;
}

double _striveShapeMature(int levelGap, int majorGap) {
  double sub = 0.0;
  for (final row in _striveSubShape) {
    if (levelGap >= row[0]) {
      sub = row[1];
      break;
    }
  }
  double extra = 0.0;
  if (majorGap >= 2) {
    extra = _striveExtraRank[2]!;
  } else if (majorGap == 1) {
    extra = _striveExtraRank[1]!;
  }
  return sub + extra;
}

class Inputs {
  String stage;
  String phase;
  String grade;
  double gradeCompletion;
  double cultiSpeed;
  double absorptionRatio;
  String auraGem;
  String targetStage;
  String targetPhase;
  String targetGrade;
  // UI-only: never read by the math. Both UIs compare it against
  // prestock_days; it rides Inputs for the cross-platform schema (prefs
  // blob + OMV2 'td' key on mobile).
  double timegateDays;
  String topStage;
  bool matureServer;
  bool dailiesDone;
  double resetInHours;

  double respiraPerDay;
  double respiraEvent;
  double respiraExp;

  String pillRank;
  double pillEffect;
  double pillLimit;
  double goldPerDay;
  double purplePerDay;
  double bluePerDay;
  double markBlue;
  double markPurple;
  double markGold;

  bool vase;
  String vaseStar;
  bool vaseSkin;
  String vaseInput;
  bool mirror;
  String mirrorStar;
  bool mirrorSkin;
  bool pearl;
  String pearlStar;
  bool pearlSkin;
  double pearlXpPer10;
  bool vaseCharge;
  bool mirrorCharge;
  bool pearlCharge;

  String fruitRank;
  double fruitCount;
  bool fruitHighestRank;
  int lvlCulti;
  int lvlQuality;
  int lvlGush;
  String extractorRarity;

  // Ascension Virya blessings: additive percentage-point bonuses on the
  // absorption ratio; the conditional tier applies only before Voidbreak
  // MIDDLE. The entered absorption is the on-screen total (includes them).
  double blessPp;
  double blessWindowPp;

  // XP elixirs: flat daily XP stream analogous to Respira (no crit roll).
  double elixirPerDay;
  double elixirExp;
  double elixirEffect;

  Inputs({
    this.stage = 'Novice',
    this.phase = 'N/A',
    this.grade = 'N/A',
    this.gradeCompletion = 0.0,
    this.cultiSpeed = 0.0,
    this.absorptionRatio = 0.0,
    this.auraGem = 'None',
    this.targetStage = '',
    this.targetPhase = '',
    this.targetGrade = '',
    this.timegateDays = 0.0,
    this.topStage = '',
    this.matureServer = true,
    this.dailiesDone = false,
    this.resetInHours = 24.0,
    this.respiraPerDay = 0.0,
    this.respiraEvent = 0.0,
    this.respiraExp = 0.0,
    this.pillRank = '1R',
    this.pillEffect = 0.0,
    this.pillLimit = 0.0,
    this.goldPerDay = 0.0,
    this.purplePerDay = 0.0,
    this.bluePerDay = 0.0,
    this.markBlue = 0.0,
    this.markPurple = 0.0,
    this.markGold = 0.0,
    this.vase = false,
    this.vaseStar = '0*',
    this.vaseSkin = false,
    this.vaseInput = 'Blue',
    this.mirror = false,
    this.mirrorStar = '0*',
    this.mirrorSkin = false,
    this.pearl = false,
    this.pearlStar = '0*',
    this.pearlSkin = false,
    this.pearlXpPer10 = 0.0,
    this.vaseCharge = true,
    this.mirrorCharge = true,
    this.pearlCharge = true,
    this.fruitRank = 'R3',
    this.fruitCount = 0.0,
    this.fruitHighestRank = false,
    this.lvlCulti = 0,
    this.lvlQuality = 0,
    this.lvlGush = 0,
    this.extractorRarity = 'Common',
    this.blessPp = 0.0,
    this.blessWindowPp = 0.0,
    this.elixirPerDay = 0.0,
    this.elixirExp = 0.0,
    this.elixirEffect = 1.0,
  });

  /// Build from a snake_case map (matches the Python Inputs kwargs). Used by the
  /// parity harness and settings load.
  factory Inputs.fromMap(Map<String, dynamic> m) {
    double d(String k, double dv) => m.containsKey(k) ? (m[k] as num).toDouble() : dv;
    int i(String k, int dv) => m.containsKey(k) ? (m[k] as num).toInt() : dv;
    String s(String k, String dv) => m.containsKey(k) ? m[k] as String : dv;
    bool b(String k, bool dv) => m.containsKey(k) ? m[k] as bool : dv;
    return Inputs(
      stage: s('stage', 'Novice'),
      phase: s('phase', 'N/A'),
      grade: s('grade', 'N/A'),
      gradeCompletion: d('grade_completion', 0.0),
      cultiSpeed: d('culti_speed', 0.0),
      absorptionRatio: d('absorption_ratio', 0.0),
      auraGem: s('aura_gem', 'None'),
      targetStage: s('target_stage', ''),
      targetPhase: s('target_phase', ''),
      targetGrade: s('target_grade', ''),
      timegateDays: d('timegate_days', 0.0),
      topStage: s('top_stage', ''),
      matureServer: b('mature_server', true),
      dailiesDone: b('dailies_done', false),
      resetInHours: d('reset_in_hours', 24.0),
      respiraPerDay: d('respira_per_day', 0.0),
      respiraEvent: d('respira_event', 0.0),
      respiraExp: d('respira_exp', 0.0),
      pillRank: s('pill_rank', '1R'),
      pillEffect: d('pill_effect', 0.0),
      pillLimit: d('pill_limit', 0.0),
      goldPerDay: d('gold_per_day', 0.0),
      purplePerDay: d('purple_per_day', 0.0),
      bluePerDay: d('blue_per_day', 0.0),
      markBlue: d('mark_blue', 0.0),
      markPurple: d('mark_purple', 0.0),
      markGold: d('mark_gold', 0.0),
      vase: b('vase', false),
      vaseStar: s('vase_star', '0*'),
      vaseSkin: b('vase_skin', false),
      vaseInput: s('vase_input', 'Blue'),
      mirror: b('mirror', false),
      mirrorStar: s('mirror_star', '0*'),
      mirrorSkin: b('mirror_skin', false),
      pearl: b('pearl', false),
      pearlStar: s('pearl_star', '0*'),
      pearlSkin: b('pearl_skin', false),
      pearlXpPer10: d('pearl_xp_per_10', 0.0),
      vaseCharge: b('vase_charge', true),
      mirrorCharge: b('mirror_charge', true),
      pearlCharge: b('pearl_charge', true),
      fruitRank: s('fruit_rank', 'R3'),
      fruitCount: d('fruit_count', 0.0),
      fruitHighestRank: b('fruit_highest_rank', false),
      lvlCulti: i('lvl_culti', 0),
      lvlQuality: i('lvl_quality', 0),
      lvlGush: i('lvl_gush', 0),
      extractorRarity: s('extractor_rarity', 'Common'),
      blessPp: d('bless_pp', 0.0),
      blessWindowPp: d('bless_window_pp', 0.0),
      elixirPerDay: d('elixir_per_day', 0.0),
      elixirExp: d('elixir_exp', 0.0),
      elixirEffect: d('elixir_effect', 1.0),
    );
  }

  /// Snake_case map with EXACTLY the keys [fromMap] reads (round-trip pinned
  /// by test). This is the single enumeration of the cross-platform input
  /// schema: the prefs blob and build-code expansion both derive from it.
  Map<String, dynamic> toMap() => {
        'stage': stage,
        'phase': phase,
        'grade': grade,
        'grade_completion': gradeCompletion,
        'culti_speed': cultiSpeed,
        'absorption_ratio': absorptionRatio,
        'aura_gem': auraGem,
        'target_stage': targetStage,
        'target_phase': targetPhase,
        'target_grade': targetGrade,
        'timegate_days': timegateDays,
        'top_stage': topStage,
        'mature_server': matureServer,
        'dailies_done': dailiesDone,
        'reset_in_hours': resetInHours,
        'respira_per_day': respiraPerDay,
        'respira_event': respiraEvent,
        'respira_exp': respiraExp,
        'pill_rank': pillRank,
        'pill_effect': pillEffect,
        'pill_limit': pillLimit,
        'gold_per_day': goldPerDay,
        'purple_per_day': purplePerDay,
        'blue_per_day': bluePerDay,
        'mark_blue': markBlue,
        'mark_purple': markPurple,
        'mark_gold': markGold,
        'vase': vase,
        'vase_star': vaseStar,
        'vase_skin': vaseSkin,
        'vase_input': vaseInput,
        'mirror': mirror,
        'mirror_star': mirrorStar,
        'mirror_skin': mirrorSkin,
        'pearl': pearl,
        'pearl_star': pearlStar,
        'pearl_skin': pearlSkin,
        'pearl_xp_per_10': pearlXpPer10,
        'vase_charge': vaseCharge,
        'mirror_charge': mirrorCharge,
        'pearl_charge': pearlCharge,
        'fruit_rank': fruitRank,
        'fruit_count': fruitCount,
        'fruit_highest_rank': fruitHighestRank,
        'lvl_culti': lvlCulti,
        'lvl_quality': lvlQuality,
        'lvl_gush': lvlGush,
        'extractor_rarity': extractorRarity,
        'bless_pp': blessPp,
        'bless_window_pp': blessWindowPp,
        'elixir_per_day': elixirPerDay,
        'elixir_exp': elixirExp,
        'elixir_effect': elixirEffect,
      };
}

class Results {
  bool valid = false;
  String error = '';
  double phaseDays = 0.0;
  double stageDays = 0.0;
  double targetDays = 0.0;
  bool targetValid = false;
  bool prestockValid = false;
  double prestockPct = 0.0;
  double prestockDays = 0.0;
  List<double> prestockBand = [0.0, 0.0];
  double abodeAura = 0.0;
  double strive = 0.0;
  double baseXpPerDay = 0.0;
  double effectiveXpPerDay = 0.0;
  double pillXpPerDay = 0.0;
  double pillSpeedup = 0.0;
  double gemSpeedup = 0.0;
  double mythicPillsPerDay = 0.0;
  double pearlXpPerDay = 0.0;
  double respiraXpPerDay = 0.0;
  double elixirXpPerDay = 0.0;
  double fruitXp = 0.0;
  double fruitDaysSaved = 0.0;
  List<double> phaseBand = [0.0, 0.0];
  List<double> stageBand = [0.0, 0.0];
  List<double> targetBand = [0.0, 0.0];
}

double _num(Object? v) => (v as num).toDouble();

class Engine {
  final Map<String, dynamic> data;
  final List<dynamic> rows;

  Engine(this.data) : rows = data['rows'] as List<dynamic>;

  List<String> stages() {
    final out = <String>[];
    for (final r in rows) {
      final s = r['stage'] as String;
      if (!out.contains(s)) out.add(s);
    }
    return out;
  }

  List<String> phasesFor(String stage) {
    final out = <String>[];
    for (final r in rows) {
      if (r['stage'] == stage && !out.contains(r['phase'])) {
        out.add(r['phase'] as String);
      }
    }
    return out;
  }

  List<String> gradesFor(String stage, String phase) => [
        for (final r in rows)
          if (r['stage'] == stage && r['phase'] == phase) r['grade'] as String
      ];

  int rowIndex(String stage, String phase, String grade) {
    for (var i = 0; i < rows.length; i++) {
      final r = rows[i];
      if (r['stage'] == stage && r['phase'] == phase && r['grade'] == grade) {
        return i;
      }
    }
    return -1;
  }

  int stageStartIndex(String stage) {
    for (var i = 0; i < rows.length; i++) {
      if (rows[i]['stage'] == stage) return i;
    }
    return -1;
  }

  /// Row index where the target begins: start of the stage, of a half-step
  /// within it, or of a specific grade.
  int targetStartIndex(String stage, String phase, String grade) {
    if (phase.isEmpty) return stageStartIndex(stage);
    if (grade.isEmpty) {
      for (var i = 0; i < rows.length; i++) {
        if (rows[i]['stage'] == stage && rows[i]['phase'] == phase) return i;
      }
      return -1;
    }
    return rowIndex(stage, phase, grade);
  }

  List<double> _starRow(String key) {
    final star = data['star'] as Map<String, dynamic>;
    final v = star[key];
    if (v == null) return [1, 200, 0];
    return [for (final x in v as List) _num(x)];
  }

  double _energyDay(String starKey, bool charged) {
    final rec = _starRow(starKey)[0];
    return (1440 / 15) * rec + (charged ? 100 : 0);
  }

  Map<String, double> pillMath(Inputs inp) {
    final pillXp = data['pill_xp'] as Map<String, dynamic>;
    final rankVals = pillXp[inp.pillRank];
    final gold = rankVals != null ? _num(rankVals[pillGold]) : 0.0;
    final purple = rankVals != null ? _num(rankVals[pillPurple]) : 0.0;
    final blue = rankVals != null ? _num(rankVals[pillBlue]) : 0.0;
    final mythic = rankVals != null ? _num(rankVals[pillMythic]) : 0.0;
    final plus = inp.pillEffect;
    final disc = data['artifact_energy_discount'] as Map<String, dynamic>;
    double discOf(String k) => disc.containsKey(k) ? _num(disc[k]) : 0.0;

    final vaseAdder = inp.vase ? _starRow(inp.vaseStar)[2] : 0.0;

    final goldXp = (1 + plus + inp.markGold) * gold;
    final purpleXp = (1 + plus + inp.markPurple) * purple;
    final blueXp = (1 + plus + inp.markBlue) * blue;
    final mythicXp = (1 + plus + vaseAdder + (inp.vaseSkin ? 0.08 : 0)) * mythic;

    double vasePills = 0.0;
    if (inp.vase) {
      final vec = data['vase_energy_cost'] as Map<String, dynamic>? ?? {};
      final baseCost = vec.containsKey(inp.pillRank) ? _num(vec[inp.pillRank]) : 100.0;
      final qDisc = {'Gold': 0.20, 'Purple': 0.05}[inp.vaseInput] ?? 0.0;
      final cost = baseCost * (1 - qDisc) * (inp.vaseStar == '5*' ? 0.85 : 1.0);
      vasePills = _energyDay(inp.vaseStar, inp.vaseCharge) / cost;
    }
    double mirrorPills = 0.0;
    if (inp.vase && inp.mirror) {
      final d = discOf(inp.mirrorStar) + (inp.mirrorSkin ? 10 : 0);
      final cost = 200 * (1 - d / 100);
      var copies = _energyDay(inp.mirrorStar, inp.mirrorCharge) / math.max(1e-9, cost);
      if (inp.mirrorStar == '5*') copies *= 1.15;
      mirrorPills = copies + vasePills;
    }
    final mythicPerDay = (inp.vase && inp.mirror) ? mirrorPills : vasePills;

    double pearlXpDay = 0.0;
    if (inp.pearl) {
      final d = discOf(inp.pearlStar) + (inp.pearlSkin ? 10 : 0);
      final perUse = math.max(1, (10 * (1 - d / 100)).floor());
      final uses = (_energyDay(inp.pearlStar, inp.pearlCharge) / perUse).floor();
      final c0 = inp.pearlStar.isNotEmpty ? inp.pearlStar[0] : '';
      final starN = int.tryParse(c0) ?? 0;
      pearlXpDay =
          ((uses * inp.pearlXpPer10 * (starN >= 1 ? 1.2 : 1.0)) / 10).floor() * 10;
    }

    var rem = inp.pillLimit;
    final usedGold = math.min(inp.goldPerDay, rem);
    rem -= usedGold;
    final usedPurple = math.min(inp.purplePerDay, rem);
    rem -= usedPurple;
    final usedBlue = math.min(inp.bluePerDay, rem);
    rem -= usedBlue;

    final totalXpDay = mythicPerDay * mythicXp +
        usedGold * goldXp +
        usedPurple * purpleXp +
        usedBlue * blueXp +
        pearlXpDay;
    return {
      'xp_per_day': totalXpDay,
      'mythic_per_day': mythicPerDay,
      'pearl_xp_day': pearlXpDay,
    };
  }

  List<double> fruitStats(Inputs inp) {
    if (inp.fruitCount <= 0) return [0.0, 0.0];
    final fruitXp = data['fruit_xp'] as Map<String, dynamic>;
    var base = fruitXp.containsKey(inp.fruitRank) ? _num(fruitXp[inp.fruitRank]) : 0.0;
    if (inp.fruitHighestRank) base *= 1.5;
    final lv = data['fruit_levels'] as Map<String, dynamic>;
    Map<String, dynamic> lvl(int x) =>
        lv['${math.max(0, math.min(30, x))}'] as Map<String, dynamic>;
    final lGush = lvl(inp.lvlGush);
    final lCulti = lvl(inp.lvlCulti);
    final lQual = lvl(inp.lvlQuality);

    final gc = _num(lGush['gush_chance']);
    // Gush multiplier is on the Gush track (in-game verified 2026-07-07;
    // mirrors engine.py — keep in lockstep).
    final gxm = _num(lGush['gush_xp']);

    final cultiMult = 1 + _num(lCulti['culti_xp']);
    final ext = (data['extractor_chance'] as Map<String, dynamic>)[inp.extractorRarity];
    final extList = ext != null ? [for (final x in ext as List) _num(x)] : [1.0, 0, 0, 0, 0, 0];
    // Extractor rarity rank grants +20% orb EXP to tiers 1..rank (no Common line).
    const ranks = ['Common', 'Uncommon', 'Rare', 'Epic', 'Legendary', 'Mythic'];
    final rankIdx = math.max(0, ranks.indexOf(inp.extractorRarity));
    final quals = lQual['quality'] as List;
    final qmults = data['quality_mult'] as List;
    // Quality rows sum to 1.0 (levels 0-10) or 0.7 (levels 11+); the extractor
    // fills the missing mass at its rarity tier so the tier probabilities form
    // a true distribution (mirrors engine.py — keep in lockstep).
    final qualSum = [for (final q in quals) _num(q)].fold(0.0, (a, b) => a + b);
    final residual = math.max(0.0, 1.0 - qualSum);
    final extTot = extList.fold(0.0, (a, b) => a + b);
    var eQ = 0.0;
    for (var i = 0; i < qmults.length; i++) {
      final p = _num(quals[i]) + (extTot > 0 ? extList[i] / extTot * residual : 0.0);
      eQ += p * (cultiMult + (i >= 1 && i <= rankIdx ? 0.2 : 0.0)) * _num(qmults[i]);
    }

    // gc is the RANDOM trigger rate; the x6 pity is SOFT — any gush resets
    // the counter, so a gush is guaranteed within 6 of the LAST gush. Exact
    // mean/variance via a 6-state Markov moment recursion over the miss
    // streak, counter fresh at batch start (mirrors engine.py — lockstep).
    final n = inp.fruitCount.toInt();
    const k = gushGuaranteeEvery;
    var p = List<double>.filled(k, 0.0); // P(miss streak = s)
    var m = List<double>.filled(k, 0.0); // E[gushes * 1{streak = s}]
    var q = List<double>.filled(k, 0.0); // E[gushes^2 * 1{streak = s}]
    p[0] = 1.0;
    for (var i = 0; i < n; i++) {
      final p2 = List<double>.filled(k, 0.0);
      final m2 = List<double>.filled(k, 0.0);
      final q2 = List<double>.filled(k, 0.0);
      for (var s = 0; s < k; s++) {
        final pg = s == k - 1 ? 1.0 : gc;
        p2[0] += pg * p[s];
        m2[0] += pg * (m[s] + p[s]);
        q2[0] += pg * (q[s] + 2 * m[s] + p[s]);
        if (s < k - 1) {
          p2[s + 1] += (1 - pg) * p[s];
          m2[s + 1] += (1 - pg) * m[s];
          q2[s + 1] += (1 - pg) * q[s];
        }
      }
      p = p2; m = m2; q = q2;
    }
    final expGushes = m.fold(0.0, (a, b) => a + b);
    final varGushCount =
        math.max(0.0, q.fold(0.0, (a, b) => a + b) - expGushes * expGushes);
    final mean = base * eQ * (n + expGushes * (gxm - 1));
    final varTotal =
        math.pow(base * eQ, 2) * math.pow(gxm - 1, 2) * varGushCount;
    return [mean, varTotal.toDouble()];
  }

  Results calculate(Inputs inp) {
    final res = Results();
    final idx = rowIndex(inp.stage, inp.phase, inp.grade);
    if (idx < 0) {
      res.error = 'Select a valid stage / phase / grade.';
      return res;
    }
    if (inp.cultiSpeed <= 0 || inp.absorptionRatio <= 0) {
      res.error = 'Cultivation speed and absorption ratio must be > 0.';
      return res;
    }

    final cur = rows[idx];
    final curLow = _num(cur['low']);
    final abode = inp.cultiSpeed / inp.absorptionRatio;

    // Ascension blessing pp: the conditional tier applies only to rows
    // BEFORE Voidbreak MIDDLE; the persistent tiers apply to every row.
    final vbm = targetStartIndex('Voidbreak', 'MIDDLE', '');
    final blessEnd = vbm >= 0 ? vbm : rows.length;
    double blessAt(int j) =>
        inp.blessPp + (j < blessEnd ? inp.blessWindowPp : 0.0);
    final blessCur = blessAt(idx);
    if (blessCur > 0 && inp.absorptionRatio <= blessCur) {
      res.error = 'Absorption ratio must exceed the blessing bonus.';
      return res;
    }
    // Strive multiplies the base band; blessing pp are additive on top, so
    // the current row's blessing is stripped from the on-screen total to
    // recover the true Strive (mirrors engine.py — keep in lockstep).
    final strive =
        curLow > 0 ? (inp.absorptionRatio - blessCur) / curLow - 1 : 0.0;
    final gemMap = data['gem_bonus'] as Map<String, dynamic>;
    final gem = gemMap.containsKey(inp.auraGem) ? _num(gemMap[inp.auraGem]) : 0.0;

    final pills = pillMath(inp);
    final respiraDaily = inp.respiraPerDay * inp.respiraExp * respiraCritMean;
    final respiraEventXp = inp.respiraEvent * inp.respiraExp * respiraCritMean;
    // XP elixirs: flat daily XP, deterministic (no crit roll observed).
    final elixirDaily = inp.elixirPerDay * inp.elixirExp * inp.elixirEffect;
    final dailyXp = pills['xp_per_day']! + respiraDaily + elixirDaily;
    final pillRatio = (dailyXp / inp.cultiSpeed) * tickSeconds / 86400.0;
    final fs = fruitStats(inp);
    final fruitMean = fs[0], fruitVar = fs[1];
    final fruitXp = fruitMean + respiraEventXp;

    final exp2 = inp.respiraExp * inp.respiraExp * respiraCritVar;
    final varUpfront = fruitVar + inp.respiraEvent * exp2;
    final varDaily = inp.respiraPerDay * exp2;

    final stageOrder = stages();
    double Function(dynamic)? striveOf;
    if (stageOrder.contains(inp.topStage) && stageOrder.contains(inp.stage)) {
      final topI = stageOrder.indexOf(inp.topStage);
      final curGap = topI - stageOrder.indexOf(inp.stage);
      final topRow = stageStartIndex(inp.topStage);
      final stageIdx = {for (var i = 0; i < stageOrder.length; i++) stageOrder[i]: i};
      final rowIdxMap = {for (var i = 0; i < rows.length; i++) rows[i]: i};

      double shapeAt(int rowI, String rowStage) {
        final major = topI - (stageIdx[rowStage] ?? topI);
        if (inp.matureServer) return _striveShapeMature(topRow - rowI, major);
        return _striveShape(major);
      }

      final curShape = shapeAt(idx, inp.stage);
      // strive <= 0 cannot fade toward #1 (negative scale would raise speeds).
      if (curGap > 0 && curShape > 0 && strive > 0) {
        final scale = strive / curShape;
        striveOf = (row) => scale * shapeAt(rowIdxMap[row]!, row['stage'] as String);
      }
    }

    double speed(int j) {
      final row = rows[j];
      final s = striveOf != null ? striveOf(row) : strive;
      return math.max(
          1e-12, abode * (_num(row['low']) * (1 + s) + blessAt(j)));
    }

    // Per-row wall-clock integration: gem multiplies cultivation speed only;
    // pills/Respira are flat daily XP on top. With dailiesDone the window
    // until the daily reset runs without the daily XP, and event Respira is
    // credited when the window ends (mirrors engine.py — keep in lockstep).
    final dailyRate = dailyXp / 86400.0;
    final resetWindow =
        inp.dailiesDone ? inp.resetInHours.clamp(0.0, 24.0) * 3600.0 : 0.0;
    final startCredit = resetWindow > 0.0 ? fruitMean : fruitXp;
    final deferredCredit = resetWindow > 0.0 ? respiraEventXp : 0.0;

    double realSeconds(int upto) {
      var credit = startCredit;
      var deferred = deferredCredit;
      var windowLeft = resetWindow;
      var total = 0.0;
      final remainingCur =
          _num(cur['grade_xp']) * (1 - inp.gradeCompletion.clamp(0.0, 1.0));
      for (var j = idx; j <= upto; j++) {
        final xp = j == idx ? remainingCur : _num(rows[j]['grade_xp']);
        var take = math.min(credit, xp);
        credit -= take;
        var left = xp - take;
        final baseRate = speed(j) * (1 + gem) / tickSeconds;
        if (windowLeft > 0.0 && left > 0.0) {
          final secNp = left / baseRate;
          if (secNp <= windowLeft) {
            windowLeft -= secNp;
            total += secNp;
            continue;
          }
          left -= baseRate * windowLeft;
          total += windowLeft;
          windowLeft = 0.0;
          credit += deferred;
          deferred = 0.0;
          take = math.min(credit, left);
          credit -= take;
          left -= take;
        }
        total += left / (baseRate + dailyRate);
      }
      return total;
    }

    double days(double wallSeconds) => wallSeconds / 86400.0;

    var pend = idx;
    while (pend + 1 < rows.length &&
        rows[pend + 1]['stage'] == inp.stage &&
        rows[pend + 1]['phase'] == inp.phase) {
      pend++;
    }
    var send = pend;
    while (send + 1 < rows.length && rows[send + 1]['stage'] == inp.stage) {
      send++;
    }

    final effPerDay =
        inp.cultiSpeed * (86400.0 / tickSeconds) * (1 + gem) + dailyXp;

    double xpAhead(int upto) {
      var total = _num(cur['grade_xp']) * (1 - inp.gradeCompletion.clamp(0.0, 1.0));
      for (var j = idx + 1; j <= upto; j++) {
        total += _num(rows[j]['grade_xp']);
      }
      return math.max(0.0, total - startCredit - deferredCredit);
    }

    List<double> band(double tDays, int upto) {
      if (varUpfront <= 0 && varDaily <= 0) return [tDays, tDays];
      final rate = tDays > 0 ? xpAhead(upto) / tDays : effPerDay;
      if (rate <= 0) return [tDays, tDays];
      final varXp = varUpfront + varDaily * math.max(0.0, tDays);
      final sdDays = math.sqrt(varXp) / rate;
      return [math.max(0.0, tDays - _bandZ * sdDays), tDays + _bandZ * sdDays];
    }

    res.phaseDays = days(realSeconds(pend));
    res.stageDays = days(realSeconds(send));
    res.phaseBand = band(res.phaseDays, pend);
    res.stageBand = band(res.stageDays, send);

    if (inp.targetStage.isNotEmpty) {
      final tstart =
          targetStartIndex(inp.targetStage, inp.targetPhase, inp.targetGrade);
      if (tstart > idx) {
        res.targetDays = days(realSeconds(tstart - 1));
        res.targetBand = band(res.targetDays, tstart - 1);
        res.targetValid = true;
        if (tstart > send + 1) {
          // Prestock scenario: a timegate parks you at the Stage cap, where
          // excess EXP accrues at the CAPPED row's rate (no future-row speed
          // scaling; pills/Respira stay flat). Overcap accrual runs WITHOUT
          // the Strive Bonus (player-confirmed 2026-07-15) — de-strived aura
          // component; blessing pp still apply (mirrors engine.py).
          final capSpeed = abode * (_num(rows[send]['low']) + blessAt(send));
          final capRate = capSpeed * (1 + gem) / tickSeconds + dailyRate;
          final overflowXp = xpAhead(tstart - 1) - xpAhead(send);
          res.prestockDays = days(realSeconds(send) + overflowXp / capRate);
          res.prestockBand = band(res.prestockDays, tstart - 1);
          // Overcap % in the game's display convention (verified 2026-07-15):
          // cumulative XP since the start of the Stage's final half-step ÷
          // that half-step's total.
          final capPhase = rows[send]['phase'];
          var hsTotal = 0.0;
          for (final r in rows) {
            if (r['stage'] == inp.stage && r['phase'] == capPhase) {
              hsTotal += (r['grade_xp'] as num).toDouble();
            }
          }
          var beyond = 0.0;
          for (var j = send + 1; j < tstart; j++) {
            beyond += (rows[j]['grade_xp'] as num).toDouble();
          }
          if (hsTotal > 0) {
            res.prestockPct = (hsTotal + beyond) / hsTotal * 100.0;
            res.prestockValid = true;
          }
        }
      } else if (tstart >= 0) {
        res.error = 'Target must be after your current grade.';
      }
    }

    final fruitSecs =
        inp.cultiSpeed > 0 ? fruitXp / inp.cultiSpeed * tickSeconds : 0.0;

    res.valid = true;
    res.abodeAura = abode;
    res.strive = strive;
    res.baseXpPerDay = inp.cultiSpeed * (86400.0 / tickSeconds);
    res.effectiveXpPerDay = res.baseXpPerDay * (1 + gem) + dailyXp;
    res.pillXpPerDay = pills['xp_per_day']!;
    res.pillSpeedup = pillRatio;
    res.gemSpeedup = gem;
    res.mythicPillsPerDay = pills['mythic_per_day']!;
    res.pearlXpPerDay = pills['pearl_xp_day']!;
    res.respiraXpPerDay = respiraDaily;
    res.elixirXpPerDay = elixirDaily;
    res.fruitXp = fruitXp;
    res.fruitDaysSaved = fruitSecs / 86400.0;
    return res;
  }
}

String fmtDays(double d) {
  if (d < 0) d = 0;
  final totalMin = (d * 24 * 60).round();
  var out = '${totalMin ~/ 1440}D ${(totalMin % 1440) ~/ 60}H ${totalMin % 60}M';
  if (d > 365) out += '  (~${(d / 365.25).toStringAsFixed(1)} yr)';
  return out;
}
