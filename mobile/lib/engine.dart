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

// Fruit pity: every Nth fruit is a guaranteed gush (deterministic, no variance).
const int gushGuaranteeEvery = 6;

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
  String topStage;
  bool matureServer;
  bool dailiesDone;

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

  Inputs({
    this.stage = 'Novice',
    this.phase = 'N/A',
    this.grade = 'N/A',
    this.gradeCompletion = 0.0,
    this.cultiSpeed = 0.0,
    this.absorptionRatio = 0.0,
    this.auraGem = 'None',
    this.targetStage = '',
    this.topStage = '',
    this.matureServer = true,
    this.dailiesDone = false,
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
      topStage: s('top_stage', ''),
      matureServer: b('mature_server', true),
      dailiesDone: b('dailies_done', false),
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
    );
  }
}

class Results {
  bool valid = false;
  String error = '';
  double phaseDays = 0.0;
  double stageDays = 0.0;
  double targetDays = 0.0;
  bool targetValid = false;
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
    final gold = rankVals != null ? _num(rankVals[0]) : 0.0;
    final purple = rankVals != null ? _num(rankVals[1]) : 0.0;
    final blue = rankVals != null ? _num(rankVals[2]) : 0.0;
    final mythic = rankVals != null ? _num(rankVals[3]) : 0.0;
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

    // gc is the RANDOM trigger rate; the every-6th pity is on top.
    final n = inp.fruitCount;
    final g = n.toInt() ~/ gushGuaranteeEvery;
    final expGushes = g + (n - g) * gc;
    final mean = base * eQ * (n + expGushes * (gxm - 1));
    final varGushCount = (n - g) * gc * (1 - gc);
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
    final strive = curLow > 0 ? inp.absorptionRatio / curLow - 1 : 0.0;
    final gemMap = data['gem_bonus'] as Map<String, dynamic>;
    final gem = gemMap.containsKey(inp.auraGem) ? _num(gemMap[inp.auraGem]) : 0.0;

    final pills = pillMath(inp);
    final respiraDaily = inp.respiraPerDay * inp.respiraExp * respiraCritMean;
    final respiraEventXp = inp.respiraEvent * inp.respiraExp * respiraCritMean;
    final dailyXp = pills['xp_per_day']! + respiraDaily;
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

    double speed(dynamic row) {
      final s = striveOf != null ? striveOf(row) : strive;
      return math.max(1e-12, abode * _num(row['low']) * (1 + s));
    }

    // Per-row wall-clock integration: gem multiplies cultivation speed only;
    // pills/Respira are flat daily XP on top. With dailiesDone the first 24h
    // run without the daily XP (mirrors engine.py — keep in lockstep).
    final dailyRate = dailyXp / 86400.0;
    final startCredit = fruitXp;

    double realSeconds(int upto) {
      var credit = startCredit;
      var nopillLeft = inp.dailiesDone ? 86400.0 : 0.0;
      var total = 0.0;
      final remainingCur =
          _num(cur['grade_xp']) * (1 - inp.gradeCompletion.clamp(0.0, 1.0));
      for (var j = idx; j <= upto; j++) {
        final xp = j == idx ? remainingCur : _num(rows[j]['grade_xp']);
        final take = math.min(credit, xp);
        credit -= take;
        var left = xp - take;
        final baseRate = speed(rows[j]) * (1 + gem) / tickSeconds;
        if (nopillLeft > 0.0 && left > 0.0) {
          final secNp = left / baseRate;
          if (secNp <= nopillLeft) {
            nopillLeft -= secNp;
            total += secNp;
            continue;
          }
          left -= baseRate * nopillLeft;
          total += nopillLeft;
          nopillLeft = 0.0;
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

    List<double> band(double tDays) {
      if (effPerDay <= 0 || (varUpfront <= 0 && varDaily <= 0)) {
        return [tDays, tDays];
      }
      final varXp = varUpfront + varDaily * math.max(0.0, tDays);
      final sdDays = math.sqrt(varXp) / effPerDay;
      return [math.max(0.0, tDays - _bandZ * sdDays), tDays + _bandZ * sdDays];
    }

    res.phaseDays = days(realSeconds(pend));
    res.stageDays = days(realSeconds(send));
    res.phaseBand = band(res.phaseDays);
    res.stageBand = band(res.stageDays);

    if (inp.targetStage.isNotEmpty && inp.targetStage != inp.stage) {
      final tstart = stageStartIndex(inp.targetStage);
      if (tstart > idx) {
        res.targetDays = days(realSeconds(tstart - 1));
        res.targetBand = band(res.targetDays);
        res.targetValid = true;
      } else if (tstart >= 0) {
        res.error = 'Target stage precedes current stage.';
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
