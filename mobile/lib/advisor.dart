/// Advisor (pure module — no Flutter): ranks the next Vault step by time
/// saved. Twin of breakthrough_calc/advisor.py — keep the two in lockstep.
///
/// For every catalog source the advisor proposes the next step that could
/// unlock an effect — own it, or raise it to the next effect threshold —
/// recomputes the shelf derivation with that step taken, maps the derived
/// target deltas onto a copy of the current engine Inputs, and diffs
/// Engine.calculate. The ranking metric is days toward the target Stage
/// when one is set, otherwise days to finish the current Stage.
///
/// Acquisition channels: the Vault knows what you own, and HOW the rest is
/// obtained decides where a step ranks. Books, friend levels and blessing
/// tiers form the plan; curios drop from random draws, so their steps rank
/// in a separate draws list instead of pretending they are plannable.
library;

import 'catalog.dart';
import 'engine.dart';
import 'shelf.dart';

const planned = 'planned';
const random = 'random';

const _channelByCategory = {'curio': random};

// raw_additive target -> (Inputs setter, catalog-unit -> Inputs-unit scale).
// respira_effect and the blessing targets are handled separately: both are
// embedded in an entered reading (respira_exp / the absorption total).

class Candidate {
  final String sourceId;
  final String name;
  final String category;
  final String channel;
  final String action;
  final dynamic newOwned;
  final Map<String, double> deltas;
  const Candidate(this.sourceId, this.name, this.category, this.channel,
      this.action, this.newOwned, this.deltas);
}

class RankedStep {
  final Candidate candidate;
  final double daysSaved;
  const RankedStep(this.candidate, this.daysSaved);
}

class Advice {
  final bool valid;
  final String reason;
  final String metric; // 'target' | 'stage'
  final double baselineDays;
  final List<RankedStep> plan;
  final List<RankedStep> draws;
  const Advice(
      {required this.valid,
      this.reason = '',
      this.metric = '',
      this.baselineDays = 0.0,
      this.plan = const [],
      this.draws = const []});
}

String channelFor(Map entry) =>
    _channelByCategory[entry['category']] ?? planned;

/// The player's realm-level index (the client's gating unit), from the
/// catalog's realm_levels table. Early/Middle/Late are the sub-levels of a
/// Stage; multi-sub Stages (Connection) resolve to the entry level. Null
/// when the Stage is unknown — gating then stays permissive.
int? playerLevel(Map catalog, String stage, String phase) {
  final band = (catalog['realm_levels'] as Map?)?[stage];
  if (band == null) return null;
  final lo = (band[0] as num).toInt();
  final hi = (band[1] as num).toInt();
  const offsets = {'EARLY': 0, 'MIDDLE': 1, 'LATE': 2};
  final v = lo + (offsets[phase] ?? 0);
  return v > hi ? hi : v;
}

class Step {
  final String action;
  final dynamic newOwned;
  final int? requireLevel;
  const Step(this.action, this.newOwned, this.requireLevel);
}

/// Upgrade tracks for one source: each an ordered list of future steps.
/// A candidate is the first step on a track that changes something the
/// calculator can price; requireLevel (or null) is the realm-level gate.
List<List<Step>> steps(Map entry, dynamic owned) {
  final levels = entry['levels'] as Map;
  final kind = levels['kind'];
  if (((entry['effects'] ?? []) as List).isEmpty) return [];
  if (kind == 'binary') {
    return owned != null
        ? []
        : [
            [const Step('Own', 1, null)]
          ];
  }
  if (kind == 'custom') {
    final params = (levels['params'] as List).cast<Map>();
    final reqs = entry['upgrade_requires_level'] as List?;
    if (owned == null) {
      return [
        [
          Step('Own',
              [for (final p in params) (p['min'] as num).toInt()], null)
        ]
      ];
    }
    final vals = [for (final v in owned as List) (v as num).toInt()];
    final tracks = <List<Step>>[];
    for (var i = 0; i < params.length; i++) {
      final p = params[i];
      final track = <Step>[];
      for (var nv = vals[i] + 1; nv <= (p['max'] as num).toInt(); nv++) {
        final nxt = List<int>.from(vals);
        nxt[i] = nv;
        int? req;
        if (p['id'] == 'upgrade' && reqs != null && nv < reqs.length) {
          req = (reqs[nv] as num).toInt();
        }
        track.add(Step("${p['label']} $nv", nxt, req));
      }
      if (track.isNotEmpty) tracks.add(track);
    }
    return tracks;
  }
  if (kind == 'ladder') {
    final labels = (levels['labels'] as List).cast<String>();
    final cur = owned == null ? 0 : (owned as num).toInt();
    if (cur >= labels.length) return [];
    return [
      [
        for (var i = cur; i < labels.length; i++)
          Step(labels[i], i + 1, null)
      ]
    ];
  }
  // tier / level: walk the effect thresholds above the current level.
  if (owned == -1) return [];
  final cur = owned == null ? 0 : (owned as num).toInt();
  final prefix = kind == 'tier' ? 'Tier ' : 'lv ';
  final track = <Step>[
    for (final t in intThresholds(entry))
      if (t > cur) Step('$prefix$t', t, null)
  ];
  if (hasMaxEffect(entry)) track.add(const Step('max', -1, null));
  return track.isEmpty ? [] : [track];
}

Map<String, double> _totals(Map<String, Derived> derived, Map targets) => {
      for (final e in derived.entries)
        if ((targets[e.key] as Map?)?['mode'] == 'raw_additive')
          e.key: e.value.total
    };

/// Every obtainable next step with a nonzero raw-target delta.
List<Candidate> candidates(Map catalog, Map shelf, {int? currentLevel}) {
  final targets = (catalog['targets'] ?? {}) as Map;
  final realm = (catalog['realm_levels'] ?? {}) as Map;
  final owned = (shelf['owned'] ?? {}) as Map;
  final byRank = <String, List<String>>{};
  for (final s in (catalog['sources'] ?? []) as List) {
    final m = s as Map;
    if (m['category'] == 'technique_book' && m['rank'] != null) {
      byRank.putIfAbsent(m['rank'] as String, () => []).add(m['id'] as String);
    }
  }
  final before = _totals(derive(catalog, shelf), targets);
  final out = <Candidate>[];
  for (final s in (catalog['sources'] ?? []) as List) {
    final entry = s as Map;
    final sid = entry['id'] as String;
    final req = (entry['requires'] ?? {}) as Map;
    final reqStage = req['stage'];
    if (reqStage != null && currentLevel != null) {
      final band = realm[reqStage];
      if (band != null) {
        const offsets = {'EARLY': 0, 'MIDDLE': 1, 'LATE': 2};
        final lo = (band[0] as num).toInt() + (offsets[req['phase']] ?? 0);
        final hi = (band[1] as num).toInt();
        if (currentLevel < (lo > hi ? hi : lo)) continue;
      }
    }
    final rb = req['rank_books'] as Map?;
    if (rb != null) {
      var have = 0;
      for (final bid in byRank[rb['rank']] ?? const <String>[]) {
        final lvl = owned[bid];
        if (lvl == -1 ||
            (lvl is num && lvl.toInt() >= (rb['tier'] as num).toInt())) {
          have += 1;
        }
      }
      if (have < (rb['count'] as num).toInt()) continue;
    }
    for (final track in steps(entry, owned[sid])) {
      for (final step in track) {
        if (step.requireLevel != null &&
            currentLevel != null &&
            currentLevel < step.requireLevel!) {
          break; // steps beyond this stay locked too
        }
        final shelf2 = Map.of(shelf);
        shelf2['owned'] = {...owned, sid: step.newOwned};
        final after = _totals(derive(catalog, shelf2), targets);
        final deltas = <String, double>{};
        for (final tid in {...after.keys, ...before.keys}) {
          final dv = (after[tid] ?? 0.0) - (before[tid] ?? 0.0);
          if (dv.abs() > 1e-12) deltas[tid] = dv;
        }
        if (deltas.isNotEmpty) {
          out.add(Candidate(sid, entry['name'] as String,
              entry['category'] as String, channelFor(entry), step.action,
              step.newOwned, deltas));
          break; // first priced step wins the track
        }
      }
    }
  }
  return out;
}

/// A copy of `inp` with the candidate's bonuses landed, or null when
/// nothing the engine models would change.
Inputs? applyDeltas(Inputs inp, Map<String, double> deltas, double booksNow,
    [Engine? engine]) {
  final out = Inputs.fromMap(inp.toMap());
  var changed = false;
  final blessDv = deltas['bless_pp'] ?? 0.0;
  final windowDv = deltas['bless_window_pp'] ?? 0.0;
  if (blessDv != 0.0 || windowDv != 0.0) {
    // The absorption reading is (row base + blessing pp) x (1 + Strive).
    // Acquiring a tier raises the reading; Strive stays what it was, so
    // the counterfactual rescales by the blessed-base ratio. Without the
    // row's base the gain cannot be priced — skip rather than misprice.
    if (engine == null) return null;
    final base = engine.baseLow(inp.stage, inp.phase, inp.grade);
    if (base == null || base <= 0 || inp.absorptionRatio <= 0) return null;
    final inWindow = engine.blessingApplies(inp.stage, inp.phase, inp.grade);
    final blessed =
        base + inp.blessPp + (inWindow ? inp.blessWindowPp : 0.0);
    final nowDv = blessDv + (inWindow ? windowDv : 0.0);
    if (nowDv != 0.0 && blessed > 0) {
      final factor = (blessed + nowDv) / blessed;
      out.absorptionRatio = inp.absorptionRatio * factor;
      // Abode Aura is speed / absorption and a blessing leaves it
      // untouched, so the current XP/tick rises with the ratio.
      out.cultiSpeed = inp.cultiSpeed * factor;
      changed = true;
    }
    if (blessDv != 0.0) {
      out.blessPp = inp.blessPp + blessDv;
      changed = true;
    }
    if (windowDv != 0.0) {
      out.blessWindowPp = inp.blessWindowPp + windowDv;
      changed = true;
    }
  }
  for (final e in deltas.entries) {
    switch (e.key) {
      case 'respira_effect':
        // The respira_exp reading already contains today's book/curio
        // percent; rescale it as if the new percent were active.
        if (inp.respiraExp > 0) {
          out.respiraExp =
              inp.respiraExp * (100.0 + booksNow + e.value) /
                  (100.0 + booksNow);
          changed = true;
        }
      case 'pill_effect':
        out.pillEffect = inp.pillEffect + e.value * 0.01;
        changed = true;
      case 'pill_attempts':
        out.pillLimit = inp.pillLimit + e.value;
        changed = true;
      case 'respira_attempts':
        out.respiraPerDay = inp.respiraPerDay + e.value;
        changed = true;
    }
  }
  return changed ? out : null;
}

/// Tie-break for equal savings: the cheapest step first. Heuristic order —
/// books before the blessing before friends (books are the cheapest
/// deterministic progress), lower ranks before higher (an R1 book costs
/// far less than an R5), then the smaller step. Twin of advisor._cost_key.
List<Comparable> _costKey(Candidate cand, Map<String, Map> byId) {
  final entry = byId[cand.sourceId] ?? const {};
  const catOrder = {
    'technique_book': 0,
    'exclusive_book': 0,
    'blessing': 1,
    'immortal_friend': 2
  };
  final cat = catOrder[entry['category']] ?? 3;
  final rank = entry['rank'];
  var rankN = 99;
  if (rank is String && rank.startsWith('R')) {
    rankN = int.tryParse(rank.substring(1)) ?? 99;
  } else if (rank is num) {
    rankN = rank.toInt();
  }
  final dynamic no = cand.newOwned;
  int mag;
  if (no is List) {
    mag = no.fold<int>(0, (a, v) => a + (v as num).toInt());
  } else if (no == -1) {
    mag = 1000000;
  } else {
    mag = (no as num).toInt();
  }
  return [cat, rankN, mag, cand.name];
}

int _compareKeys(List<Comparable> a, List<Comparable> b) {
  for (var i = 0; i < a.length; i++) {
    final c = a[i].compareTo(b[i]);
    if (c != 0) return c;
  }
  return 0;
}

double _metricDays(Results r, String metric) =>
    metric == 'target' ? r.targetDays : r.stageDays;

/// Respira never counts as empty: blank fields assume the game's stock
/// minimum — 10 daily attempts plus the Vault's permanent bonuses, and the
/// Stage's base EXP estimate times the Vault's Respira Effect percent.
Inputs _withRespiraFloor(Engine engine, Inputs inp, Map<String, Derived> d) {
  final out = Inputs.fromMap(inp.toMap());
  var changed = false;
  if (inp.respiraPerDay <= 0) {
    out.respiraPerDay = 10.0 + (d['respira_attempts']?.total ?? 0.0);
    changed = true;
  }
  if (inp.respiraExp <= 0) {
    final est = engine.respiraBaseEstimate(inp.stage);
    if (est != null) {
      final pct = d['respira_effect']?.total ?? 0.0;
      out.respiraExp = est * (1.0 + pct / 100.0);
      changed = true;
    }
  }
  return changed ? out : inp;
}

Advice rank(Engine engine, Inputs rawInp, Map catalog, Map shelf) {
  final derived = derive(catalog, shelf);
  final inp = _withRespiraFloor(engine, rawInp, derived);
  final base = engine.calculate(inp);
  if (!base.valid) return Advice(valid: false, reason: base.error);
  final metric = base.targetValid ? 'target' : 'stage';
  final baseDays = _metricDays(base, metric);
  if (baseDays <= 0) {
    return const Advice(valid: false, reason: 'nothing left to shorten');
  }
  final booksNow = derived['respira_effect']?.total ?? 0.0;
  final levelNow = playerLevel(catalog, inp.stage, inp.phase);
  final plan = <RankedStep>[];
  final draws = <RankedStep>[];
  for (final cand in candidates(catalog, shelf, currentLevel: levelNow)) {
    final inp2 = applyDeltas(inp, cand.deltas, booksNow, engine);
    if (inp2 == null) continue;
    final r2 = engine.calculate(inp2);
    if (!r2.valid) continue;
    final saved = baseDays - _metricDays(r2, metric);
    if (saved <= 1e-9) continue;
    (cand.channel == planned ? plan : draws).add(RankedStep(cand, saved));
  }
  final byId = <String, Map>{
    for (final s in (catalog['sources'] ?? []) as List)
      (s as Map)['id'] as String: s
  };
  int cmp(RankedStep a, RankedStep b) {
    final d = b.daysSaved.compareTo(a.daysSaved);
    if (d != 0) return d;
    return _compareKeys(
        _costKey(a.candidate, byId), _costKey(b.candidate, byId));
  }

  plan.sort(cmp);
  draws.sort(cmp);
  return Advice(
      valid: true,
      metric: metric,
      baselineDays: baseDays,
      plan: plan,
      draws: draws);
}
