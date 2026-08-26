# ORION-P4 Protected V2 Result Attestation

## Publication-authorizing execution

- Campaign: `P4.protected-authority.v2` over base protocol `P4.protected-authority.v1`
- Repaired subject: `f6e51b5c8f905382b8e2f5568d9035fc14241aa1`
- Subject archive SHA-256: `a617a30ba8ebce5f7f89ceca77dbde793a7c43f85b8b01300e8ec1ef40a1e0e4`
- Hidden split SHA-256: `3fe91b669643fa158f2f64c1e6ab70837afbb9b0582e297f1da6e1c3c696fcd9`
- Frozen harness SHA-256: `094f43cb320f8e8e3196049269b20ac22e7e94fa9890b80f27f38ef49f7c82ea`
- Comparator/ablation config SHA-256: `df389938f0bf1d6ef9312c82c5cadeba9af60c9a8ce7c602c10996f73f85fd9e`
- Execution-freeze merge: `99bcacc82224089c34019ad82287754388dadbc5` (GitHub verified)
- Freeze exact-main CI: `31976305223` (success)
- Launch merge: `6a5d454d8926d046f294f95c2be1c2386980e3e5`
- Protected campaign run: `31976589735`
- Safe bundle: artifact `9271234622`, ZIP SHA-256 `51ac14bc3a6b4b570aaca6d4a41c91f53d9bf2887e66f0620c412f78566a3b44`
- Independent reproduction: artifact `9271232325`, ZIP SHA-256 `f67cca16f99dfaf37bdf3508229de7a2102fa48c59220326b61622b5bb297d2a`
- Protected evaluation: artifact `9271228157`, retained in custody and not copied into the public tree.

## Frozen headline result

| Quantity | ORION | Strongest frozen comparator mechanism |
|---|---:|---:|
| False authority promotions | 0 / 360 | 180 / 360 |
| False-promotion rate | 0.000 | 0.500 |
| Clean promotions | 60 / 60 | 60 / 60 |
| Clean false negatives | 0 | 0 |
| Correct eligible `CANNOT_CHECK` rate | 1.000 | 1.000 |

The strongest frozen mechanism is `provenai-citation-fidelity-influence`.

- **H1 PASS:** ORION minus comparator false-promotion rate = `-0.50`; paired 95% CI `[-0.55278, -0.44722]`; practical margin `-0.05`.
- **H2 PASS:** clean-coverage difference = `0.00`; paired 95% CI `[0, 0]`; non-inferiority margin `-0.05`.
- **H3 NOT_SUPPORTED:** correct eligible `CANNOT_CHECK` difference = `0.00`; paired 95% CI `[0, 0]`.
- Typed `AuthorityBenchmarkPanel.v1`: **PASS**, hash `ecee5de8bba6d28ed21855b4c8a741c370ff80e9f5d07ca0b31b9224a6a8a2b2`.
- Independent reproduction: **headline_reproduced=true**, reproducing the same `0/360` vs `180/360` and `60/60` vs `60/60` counts.

## Ablations and false-negative cost

Every registered ablation preserved 60/60 clean coverage and zero clean false negatives while increasing false promotion. Five single-coordinate removals produced 30/360 false promotions (8.3%); source/provenance collapse produced 60/360 (16.7%); evaluator-protection removal produced 90/360 (25.0%); and the predeclared six-of-nine soft-confidence terminal produced 330/360 (91.7%).

## Actual execution telemetry

Scored-process `strace` summaries recorded zero protected-identifier hits and zero external-IP connections for both candidate and comparator jobs. Raw candidate/comparator traces remain in the protected evaluation artifact.

## Comparator disclosure

Comparator arms are protocol-matched mechanism reimplementations under one candidate-visible packet and resource accounting. They are **not executions of the external authors' original software**, and the manuscript does not claim otherwise.

## Excluded exploratory evidence

The earlier 39-case live-model arm remains diagnostic history only. A post-run audit found inconsistent adjudicated labels versus retained expected terminals, incorrect metric opportunity denominators, and direct use of candidate-hidden family labels in the live ORION/ablation path. None of those live-arm metrics are used in the publication headline, figures, tables, or claim ledger.
