"""Run the shared scenarios through the Python engine and dump expected outputs.
The Dart parity test checks its own engine against this file."""
import dataclasses
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))  # repo root -> breakthrough_calc

from breakthrough_calc.engine import Engine, Inputs, Results

# Every Results field is parity-checked; a field added to only one engine
# fails loudly in parity.dart instead of silently escaping coverage.
FIELDS = [f.name for f in dataclasses.fields(Results)]

e = Engine()
scenarios = json.load(open(os.path.join(HERE, "scenarios.json")))
out = []
for sc in scenarios:
    r = e.calculate(Inputs(**sc))
    out.append({f: getattr(r, f) for f in FIELDS})
json.dump(out, open(os.path.join(HERE, "expected.json"), "w"), indent=1)
print(f"wrote expected.json for {len(out)} scenarios")
