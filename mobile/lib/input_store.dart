/// Persistence of the calculator inputs (the 'inputs_v1' prefs blob) and
/// validation/application of restored or imported input maps. The blob's
/// key set is pinned by test/widget_smoke_test.dart.
library;

import 'dart:convert';

import 'package:shared_preferences/shared_preferences.dart';

import 'engine.dart';

class InputStore {
  static const _key = 'inputs_v1';
  final SharedPreferences prefs;
  final Engine engine;
  InputStore(this.prefs, this.engine);

  /// The persisted blob shape (also the shape decodeBuildCode produces).
  Map<String, dynamic> blob(Inputs inp, List<List<dynamic>> peSources,
          Set<String> respiraSources) =>
      {
        ...inp.toMap(),
        'pe_sources': peSources,
        'respira_sources': respiraSources.toList(),
      };

  void save(Inputs inp, List<List<dynamic>> peSources,
      Set<String> respiraSources) {
    prefs.setString(_key, jsonEncode(blob(inp, peSources, respiraSources)));
  }

  /// Validate [m] against the engine's tables and apply it: fills
  /// [peSources] / [respiraSources] and returns the new Inputs (with
  /// phase/grade sanity-cascaded), or null for an unknown stage or an
  /// ill-typed map. ATOMIC: everything is parsed into locals before any
  /// out-param is touched, so a corrupt blob or crafted build code can
  /// never leave the caller's lists half-applied (the caller keys row
  /// widgets off a parallel id list — a desync would crash its build).
  Inputs? apply(Map<String, dynamic> m, List<List<dynamic>> peSources,
      Set<String> respiraSources) {
    final Inputs restored;
    final List<List<dynamic>> pe;
    final List<String> respira;
    try {
      restored = Inputs.fromMap(m);
      pe = [
        for (final s in (m['pe_sources'] as List? ?? []))
          [(s as List)[0] as String, (s[1] as num).toDouble()]
      ];
      respira = [
        for (final s in (m['respira_sources'] as List? ?? [])) s as String
      ];
    } catch (_) {
      return null; // Ill-typed map — leave the caller untouched.
    }
    // Sanity-check the cascading dropdowns against the engine's data.
    if (!engine.stages().contains(restored.stage)) return null;
    if (!engine.phasesFor(restored.stage).contains(restored.phase)) {
      restored.phase = engine.phasesFor(restored.stage).first;
    }
    if (!engine.gradesFor(restored.stage, restored.phase).contains(restored.grade)) {
      restored.grade = engine.gradesFor(restored.stage, restored.phase).first;
    }
    peSources
      ..clear()
      ..addAll(pe);
    respiraSources
      ..clear()
      ..addAll(respira);
    return restored;
  }

  /// Apply the saved blob, or return null (missing / corrupt / unknown
  /// stage — the caller keeps its defaults).
  Inputs? restore(List<List<dynamic>> peSources, Set<String> respiraSources) {
    final raw = prefs.getString(_key);
    if (raw == null) return null;
    try {
      return apply(
          jsonDecode(raw) as Map<String, dynamic>, peSources, respiraSources);
    } catch (_) {
      return null; // Corrupt saved state — keep defaults.
    }
  }
}
