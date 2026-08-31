# Anonymous reproducibility supplement

This archive supports the finite-fibre theorem/adverse paper without identifying the authors or linking to a named repository.

## Rechecks available from the enclosed files

Run, using Python 3.10 or later:

    python3 check_fibre_diameter_floor.py
    python3 check_refinement_to_certifiability.py
    python3 verify_joint_route_repair.py --output /tmp/joint.json
    python3 verify_density_paired_comparison.py --results results/density_backoff_result.json
    python3 verify_arm_strict_violation_comparator.py --results results/arm_conditional_result.json
    python3 analyze_selector_diagnostic.py results/arm_conditional_result.json
    python3 recheck_enclosed_results.py

All scripts use only the Python standard library. The expected JSON files are frozen outputs from the package build. The theorem checkers search for finite counterexamples and include planted controls. Their output corroborates transcription and implementation; the manuscript proofs carry general authority.

The result files are deterministic anonymous scientific projections of the full frozen objects: manuscript-relevant outcomes and per-dataset records are preserved, while environment, repository, commit and implementation-digest fields are withheld for double-blind review. MANIFEST.json binds every enclosed file.

## What this archive does not provide

It does not include the upstream ASlib or PMLB datasets and therefore does not rerun the original model-fitting pipelines. It rechecks the enclosed frozen outcomes, the exact paired coverage analysis, the paired strict-violation correction, the selector diagnostic, and the analytic finite verifiers. Full provenance-bearing objects, upstream acquisition instructions and a permanent archival identifier are camera-ready actions after deanonymization.

The final held-out fold records do retain paired strict-violation flags. Matching each geometry fold's serialized selected arm into both policies reconstructs 20/44 versus 14/44, contingency `(14,6,0,24)`, and exact two-sided McNemar `p=0.03125`. Both policies fail the frozen 0.10 validity gate. This adverse correction does not establish broad lexical superiority.

The supplementary verification code is distributed under Apache License 2.0; see LICENSE_CODE.txt. Manuscript licensing is governed separately by the TMLR submission terms.
