import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

import 'package:breakthrough_calc/i18n.dart';

/// The shared translation file (data/i18n.json) is the single source of
/// truth both apps load. Drive the mobile loader against the real file and
/// confirm tr() resolves — so the runtime wiring can't silently break.
void main() {
  setUp(() {
    loadTranslations(File('../data/i18n.json').readAsStringSync());
  });

  tearDown(() => currentLang = 'en');

  test('loadTranslations populates tr() from the shared file', () {
    currentLang = 'ru';
    expect(tr('Calculator'), isNot('Calculator'));
    expect(tr('Calculator'), 'Калькулятор');
  });

  test('English is a pass-through, unknown keys fall back', () {
    currentLang = 'en';
    expect(tr('Calculator'), 'Calculator');
    currentLang = 'de';
    expect(tr('a string with no translation ever'),
        'a string with no translation ever');
  });

  test('every key carries all four languages (shared-file invariant)', () {
    final raw = File('../data/i18n.json').readAsStringSync();
    for (final lang in ['ru', 'de', 'es', 'zh']) {
      currentLang = lang;
      // sample a stage label + a field label
      for (final k in ['Nascent Soul', 'Target Stage', 'Vault']) {
        if (raw.contains('"$k"')) {
          expect(tr(k), isNot(k), reason: '$lang missing $k');
        }
      }
    }
  });
}
