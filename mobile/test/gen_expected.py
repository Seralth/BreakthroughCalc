"""Run the shared scenarios through the Python engine and dump expected outputs.
The Dart parity test checks its own engine against this file."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))  # repo root -> breakthrough_calc

from breakthrough_calc.engine import Engine, Inputs

FIELDS = [
    "valid", "error", "phase_days", "stage_days", "target_days", "target_valid",
    "abode_aura", "strive", "base_xp_per_day", "effective_xp_per_day",
    "pill_xp_per_day", "pill_speedup", "gem_speedup", "mythic_pills_per_day",
    "pearl_xp_per_day", "respira_xp_per_day", "fruit_xp", "fruit_days_saved",
    "phase_band", "stage_band", "target_band",
]

e = Engine()
scenarios = json.load(open(os.path.join(HERE, "scenarios.json")))
out = []
for sc in scenarios:
    r = e.calculate(Inputs(**sc))
    out.append({f: getattr(r, f) for f in FIELDS})
json.dump(out, open(os.path.join(HERE, "expected.json"), "w"), indent=1)
print(f"wrote expected.json for {len(out)} scenarios")
