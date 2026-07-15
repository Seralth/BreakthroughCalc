/// Absorption diagnostics: pure classification of the entered absorption
/// against the grade's base and the implied Strive — verified game rules
/// that used to live inside the results widget. Desktop twin:
/// engine.py STRIVE_CAP_MORTAL + gui.py's absorb-base readout.
library;

import 'engine.dart';

/// Strive Bonus caps at +120% while in the mortal world (Nascent through
/// Incarnation per the in-game Strive panel); later realms legitimately
/// overcap, so the warning only applies there.
const double striveCapMortal = 1.2;
const double _eps = 1e-9;

class AbsorptionDiag {
  /// The grade's base absorption ('low' band value from the engine data).
  final double base;

  /// Entered absorption is below base — implied Strive would be negative,
  /// which the game can't produce (likely a stale absorption reading).
  final bool belowBase;

  /// Implied Strive exceeds the 120% mortal-world cap.
  final bool aboveCap;

  /// Current stage is in the mortal world (Incarnation or earlier), where
  /// the cap actually holds.
  final bool mortalWorld;

  const AbsorptionDiag({
    required this.base,
    required this.belowBase,
    required this.aboveCap,
    required this.mortalWorld,
  });

  /// Over the cap where the cap holds — the red-warning case.
  bool get overCap => aboveCap && mortalWorld;
}

/// Diagnostics for the current row, or null before Nascent Soul (where
/// Strive doesn't exist in-game) or for an unknown row. [strive] is the
/// engine's implied Strive for the same inputs (Results.strive).
AbsorptionDiag? diagnoseAbsorption(Engine engine, Inputs inp, double strive) {
  final stages = engine.stages();
  final nascentIdx = stages.indexWhere((s) => s.startsWith('Nascent'));
  if (nascentIdx < 0 || stages.indexOf(inp.stage) < nascentIdx) return null;
  final idx = engine.rowIndex(inp.stage, inp.phase, inp.grade);
  if (idx < 0) return null;
  // Blessing pp join the base BEFORE the Strive multiplier (official
  // composition), so compare against the blessed base — mirrors the
  // engine's strive decomposition and the desktop readout.
  final vbm = engine.targetStartIndex('Voidbreak', 'MIDDLE', '');
  final bless =
      inp.blessPp + (vbm < 0 || idx < vbm ? inp.blessWindowPp : 0.0);
  final base =
      ((engine.rows[idx] as Map)['low'] as num).toDouble() + bless;
  final belowBase =
      inp.absorptionRatio > 0 && inp.absorptionRatio < base - _eps;
  final incarnIdx = stages.indexWhere((s) => s.startsWith('Incarnation'));
  final mortal = incarnIdx < 0 || stages.indexOf(inp.stage) <= incarnIdx;
  final aboveCap = strive > striveCapMortal + _eps;
  return AbsorptionDiag(
      base: base, belowBase: belowBase, aboveCap: aboveCap, mortalWorld: mortal);
}
