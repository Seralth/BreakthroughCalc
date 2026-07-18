/// Hand-rolled localization: no flutter_localizations/intl dependency.
///
/// Game terms (stages, phases, resources, item names) come verbatim from the
/// game's own localization files (data/i18n_glossary.json / the full APK
/// dictionary); app prose is translated by hand. English is the fallback for
/// any missing or empty entry.
///
/// The app persists and computes with INTERNAL keys ('Nascent', 'EARLY',
/// 'Legendary', ...); only display strings go through [tr] / [trStage] /
/// [trPhase], so saved inputs survive language switches.
library;

import 'dart:convert';

/// Supported languages, code -> native name (for the picker).
const langs = {
  'en': 'English',
  'ru': 'Русский',
  'de': 'Deutsch',
  'es': 'Español',
  'zh': '中文',
};

/// Current UI language code. The app does full-page rebuilds on change, so a
/// plain mutable top-level is enough (set from SharedPreferences before the
/// first build).
String currentLang = 'en';

/// Translate [s] into the current language; falls back to English ([s]
/// itself) when there is no (or an empty) translation.
String tr(String s) {
  if (currentLang == 'en') return s;
  final v = _t[s]?[currentLang];
  return (v == null || v.isEmpty) ? s : v;
}

/// Display name for an internal stage key ('Nascent' -> 'Пробуждение').
String trStage(String key) => tr(key);

const _phaseNames = {'EARLY': 'Early', 'MIDDLE': 'Middle', 'LATE': 'Late'};

/// Display name for an internal phase key ('EARLY' -> 'Early'/'Начальная').
String trPhase(String key) => tr(_phaseNames[key] ?? key);

/// Translations, loaded once from the shared data/i18n.json (the SAME
/// file the desktop app reads — single source of truth, so the two can
/// never drift). Populated by [loadTranslations] in main() before the
/// first frame; empty until then (tr falls back to English).
Map<String, Map<String, String>> _t = {};

/// Parse assets/data/i18n.json ({en: {lang: val}}) into [_t].
void loadTranslations(String jsonStr) {
  final raw = jsonDecode(jsonStr) as Map<String, dynamic>;
  _t = {
    for (final e in raw.entries)
      e.key: {
        for (final l in (e.value as Map<String, dynamic>).entries)
          l.key: l.value as String
      }
  };
}

/// Localize an engine-formatted duration string ("1D 12H 0M  (~1.2 yr)")
/// at display time. The engine's fmtDays stays canonical English — tests
/// and parity compare its exact output.
String trDuration(String s) {
  const suffixes = {
    'ru': ['д', 'ч', 'м', 'г'],
    'de': ['T', 'Std', 'Min', 'J'],
    'es': ['d', 'h', 'min', 'años'],
    'zh': ['天', '时', '分', '年'],
  };
  final suf = suffixes[currentLang];
  if (suf == null) return s;
  var out = s.replaceAllMapped(
      RegExp(r'(\d+)D (\d+)H (\d+)M'),
      (m) => currentLang == 'zh'
          ? '${m[1]}${suf[0]}${m[2]}${suf[1]}${m[3]}${suf[2]}'
          : '${m[1]}${suf[0]} ${m[2]}${suf[1]} ${m[3]}${suf[2]}');
  out = out.replaceAllMapped(
      RegExp(r'\(~([\d.]+) yr\)'),
      (m) => currentLang == 'zh' ? '(~${m[1]}${suf[3]})' : '(~${m[1]} ${suf[3]})');
  return out;
}
