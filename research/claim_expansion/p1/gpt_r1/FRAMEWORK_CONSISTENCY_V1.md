# P1-U GPT-R1 framework consistency map

Issue: #696  
Frozen framework subject: `83abfc5c3a98606d9339b88024f83d1d4ab313e7`

## Canonical synchronization status

`papers/FRAMEWORK_SNAPSHOT.json` and `src/orion/registry.py` agree on:

- framework version `0.3.9-shadow`;
- paper sync epoch `2026-08-16-phase1-rakl-donor-closure-v3`;
- K/W/M coordinates;
- core operator sequence `FRAME -> SEARCH -> ABSORB -> RECONSTRUCT -> DETECT -> DIAGNOSE -> REFRAME -> REOPEN -> SATURATE_BOUNDED`;
- registered mechanics-substrate identifiers.

This establishes terminology/substrate synchronization only. It does not establish P1-U scientific support.

## P1-U concept -> framework mapping

| P1-U object | Current code/substrate | Status | Rule |
|---|---|---|---|
| failure/anomaly diagnosis | `DIAGNOSE.v1`; responsibility modules | IMPLEMENTED SUBSTRATE | may inform cause hypotheses, never self-authorize revision |
| `KEEP+SEARCH` | `SEARCH.v1`, search-universe and bounded saturation substrate | IMPLEMENTED SUBSTRATE | search failure alone cannot imply problem inadequacy |
| `KEEP+COMPILE` | `InterfaceAdequacyReport`; current P9/P11 research substrate | IMPLEMENTED/CANDIDATE SUBSTRATE | interface repair has precedence over broader method/model revision where registered |
| `KEEP+REPAIR` | responsibility binding + `HigherOrderEpistemicMechanic` candidate selection | IMPLEMENTED/CANDIDATE SUBSTRATE | select minimal admissible repair when responsibility is identified |
| `REVISE_MEASUREMENT` | measurement relation / responsibility mechanics | IMPLEMENTED/CANDIDATE SUBSTRATE | measurement change remains distinct from objective/problem change |
| `REFORMULATE_OBJECTIVE` | `REFRAME.v1`; P1/P1-X exact revision classes | CORE OPERATOR + RESEARCH SUBSTRATE | broad naturalistic objective reformulation is prospective |
| `REFORMULATE_BOUNDARY` | `REFRAME.v1`; higher-order revision proposal mechanism | CORE OPERATOR + PROSPECTIVE SCIENCE | no current runtime claim of universal problem-boundary inference |
| `UNRESOLVED/CANNOT_CHECK` | fail-closed status semantics throughout evidence/revision gates | IMPLEMENTED SUBSTRATE | missing evidence never becomes positive authority |
| exact reopen scope | `REOPEN.v1`; P1-X exact reopen evaluation | IMPLEMENTED/RESEARCH SUBSTRATE | broader change must reopen affected evidence exactly where support requires |
| proposal != adoption | `SelfOrionRevisionGateReport.v1` and host authority rules | IMPLEMENTED SUBSTRATE | gate hard-codes no adoption/promotion/merge authority |
| minimal scientific revision | `HigherOrderEpistemicMechanic`, assessment, `select_minimal_admissible` | IMPLEMENTED CANDIDATE SUBSTRATE | candidate selection is claim-relative and fail-closed |
| active responsibility discrimination (ARD) | no canonical registry object | **PROSPECTIVE** | research harness only until protected value is established |
| cross-domain learned reformulation router | no canonical runtime object | **PROSPECTIVE** | must not be described as current ORION capability |
| generalized reformulation superiority | no empirical authority yet | **PROSPECTIVE CLAIM** | requires #696 protected execution + verification |

## Critical runtime correspondence

Current `src/orion/self_orion/revision_gate.py` enforces three P1-U assumptions directly:

1. unresolved responsibility -> `UNRESOLVED`;
2. `InterfaceAdequacyStatus.REPAIR_REQUIRED` withholds broader candidates and considers only registered in-scope interface repair mechanics;
3. a selected candidate remains non-authorizing: adoption, promotion and merge authority are all false.

Therefore the P1-U lower-level-before-higher-level ladder is consistent with current framework direction.

## Deliberate paper-ahead-of-code objects

The following are scientific targets and must stay visibly prospective:

- naturalistic responsibility labels across arbitrary scientific domains;
- active selection of discriminating experiments/actions to identify revision responsibility;
- learned cross-domain regime selection among search/compile/repair/measurement/objective/boundary actions;
- invention of a new reformulation discriminator/operator from a failure;
- general reformulation superiority.

These are not added to `MECHANICS_SUBSTRATE_IDS` in this tranche.

## P1-X reuse boundary

The P1-X generator/checker/schema/protected V2 evidence may be reused for:

- exact case shapes;
- responsibility/intervention/revision separation;
- protected/candidate-visible field separation;
- exact reopen and preservation evaluation;
- baseline fairness patterns;
- independent reconstruction patterns.

P1-U must not reuse P1-X protected cases as a hidden generalization test or expose their gold through training/tuning.

## Synchronization verdict

`CONSISTENT_AS_PROSPECTIVE_EXTENSION`

No contradiction was found between P1-U's lower-level repair precedence, fail-closed unresolved state, exact reopen semantics, or proposal/adoption separation and the current framework.

The principal gap is implementation/evidence, not semantic conflict: ARD and broad cross-domain reformulation selection do not yet exist as canonical runtime capabilities.
