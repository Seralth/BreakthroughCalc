/// Application themes — mirrors breakthrough_calc/theme.py on the desktop.
library;

import 'package:flutter/material.dart';

const themes = ['Seralth', 'Dark', 'Light', 'System'];

ThemeData themeData(String name, Brightness platform) {
  Brightness b;
  Color seed;
  switch (name) {
    case 'Light':
      b = Brightness.light;
      seed = const Color(0xFF2A72C8);
      break;
    case 'Dark':
      b = Brightness.dark;
      seed = const Color(0xFF2A82DA);
      break;
    case 'System':
      b = platform;
      seed = const Color(0xFF2A82DA);
      break;
    default: // Seralth
      b = Brightness.dark;
      seed = const Color(0xFF3D6FB5);
  }
  final scheme = ColorScheme.fromSeed(seedColor: seed, brightness: b);
  return ThemeData(
    colorScheme: name == 'Seralth'
        ? scheme.copyWith(surface: const Color(0xFF1E2530))
        : scheme,
    scaffoldBackgroundColor: name == 'Seralth' ? const Color(0xFF1A1F28) : null,
    useMaterial3: true,
    inputDecorationTheme: const InputDecorationTheme(
      border: OutlineInputBorder(),
      isDense: true,
      contentPadding: EdgeInsets.symmetric(horizontal: 10, vertical: 12),
    ),
  );
}
