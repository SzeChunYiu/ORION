# P9 merged-evidence claim ledger

| ID | Bounded claim | Evidence and checker | Authority | Status |
|---|---|---|---|---|
| P9-C1 | On the pinned ASlib `SAT11-HAND-ALGO` scenario, the failure-aware RF reduced attempts on 77 VBS-unsolved instances by 0.7143 absolute (paired bootstrap 95% CI 0.6104–0.8182) while retaining 0.9645 of RF_ROUTER's solved instances. | `results/ASLIB_SAT11_HAND_ALGO_V1.json`; `benchmark/run_aslib_v1.py`; `benchmark/test_aslib_v1.py` | Generated public-benchmark evidence | `SUPPORTED` |
| P9-C2 | The public result is bound to exact source digests and scenario-provided outer folds; a source-digest substitution fails reproduction. | `benchmark/ASLIB_SAT11_PROTOCOL_V1.json`; `benchmark/aslib_sat11_hand_algo/SOURCE.md`; digest-mismatch hostile test | Executable integrity evidence | `SUPPORTED` |
| P9-C3 | Two complete runs produced byte-identical machine-readable output with SHA-256 `8246d007260be1bc5df437002c1de004bc98868edd114b29c3ffb22046532f06`. | Recorded rerun receipt in `JOURNAL_READINESS.md`; deterministic seeds and versions in result JSON | Local deterministic replay | `SUPPORTED` |
| P9-C4 | The framework can return a supported mechanic or abstain while exposing all competence estimates; the returned route cannot authorize execution. | `CapabilityRoute`, `LearningMachine.route_capability`, framework integration and authority tests | Executable structural evidence | `SUPPORTED` |
| P9-C5 | Competence fitting does not mutate the absorbed mechanic specification or silently append evidence. | `test_recording_experience_is_append_only_and_separate_from_fitting` | Hostile framework test | `SUPPORTED` |
| P9-C6 | P9 has no standalone novelty residual after constructive nearest-work assimilation and P5/P8 ownership pressure. | `SATURATION_LEDGER_2026-08-18.md`; `MERGE_DISPOSITION.md` | Dated bounded review judgment | `SUPPORTED_BOUNDED` |

## Nonclaims

- No superiority over AutoFolio or other configured algorithm selectors.
- No ASlib-wide, SAT-wide, cross-domain or LLM-agent generalization.
- No novelty for algorithm selection, scheduling, learned routing, selective
  prediction, self-assessment or tool-call suppression.
- No inference from abstention to authorization, correctness or scientific
  authority.
- Phase 1 false commitment remains `NOT_MEASURED`; its V1 numeric constant is
  rejected, not interpreted as an observed zero.
