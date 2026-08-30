# Anonymous review data

This archive contains the reader-facing numerical evidence for **“Responsibility-Relative Reuse of Learned and Verified State.”**

`evidence.json` contains:

- all 17,970 learned-data policy evaluations, with fold, responsibility, prediction, state source, state values read, and unsupported-reuse status;
- the complete 12-case old/new Boolean-formula panel and all 96 policy evaluations;
- the complete 48-case provenance-tiered comparison and all 240 policy evaluations;
- the complete 60-case drift panel and all 240 transport-policy evaluations;
- the retained adverse measurement and its zero independent harm-opportunity denominator.

Run:

```text
python3 verify.py
```

The verifier uses only the Python standard library. It recomputes every manuscript table from row-level data, enumerates all assignments for the finite Boolean formulas, rejects any supplied prediction that fails the corresponding formula, and checks that the adverse measurement remains excluded. It does not call the model-fitting or Boolean-search programs that generated the original evidence.

The learned-data rows are technical cross-validation evaluations over 1,797 source items, not independent population draws. The finite panels are complete for their registered generators but do not imply population generalization.
