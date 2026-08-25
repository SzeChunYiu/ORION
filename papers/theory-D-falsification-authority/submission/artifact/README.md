# Standalone executable artifact

Run the unit tests with Python 3.10 or later:

```text
python3 -m unittest -v test_evidence_license_evaluator.py
```

Evaluate a bundled fixture with:

```text
python3 evidence_license_evaluator.py examples/forecast_falsification.json
```

The JSON Schema validates document shape.  The Python evaluator performs the
semantic checks and least-fixed-point calculation described in the manuscript.
No repository modules, network access, or third-party Python packages are
required.

