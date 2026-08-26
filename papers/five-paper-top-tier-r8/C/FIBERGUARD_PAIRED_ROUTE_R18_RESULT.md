# FiberGuard R18 — outcome-exposed recovery of the frozen paired-route protocol

Date: 2026-08-27

Current terminal:

`FIBERGUARD_R18_NO_PAIRED_ROUTE_VALUE`

Authority:

`OUTCOME_EXPOSED_RECOVERY_CORROBORATION`

## 1. Custody correction and recovery subject

The former R18 positive transfer prose was withdrawn because its claimed execution commit, workflow run, runner modules, and full result did not exist. That unsupported positive terminal remains retracted.

The protocol objects committed before that prose remain valid:

- `bc3387916139af8a739a910eb58c354f73fb2a24` — source/protocol freeze;
- `c2df6e2b47b69f387a33e0ebe5e272fc8a1aad74` — scientific contract;
- `1040eaaa56ab5daf087dc01fc9988c7f3a4f2045` — workflow definition.

A complete replacement implementation was then committed without using the withdrawn positive result as an input. The immutable recovery subject is

`ac4a50f85a147f5933cd2055809c7ac30b29e3c1`.

Workflow run `33023149716`, job `98358163251`, executed that subject twice byte-identically against the exact ASlib commit

`551b22beef8df17de59286b4822ef720e0aa4d6f`.

The complete result, terminal, and issue-comment bytes are now committed durably on the branch. The recovery result JSON has SHA-256

`8136ac6e614406a51270342d73786dfec43a9ecdac81f62e815cd14d1a739c45`,

and its pre-digest canonical result subject has SHA-256

`e3a0ccb27484cbb5a950a5de10d60966edccee2c76272e79f239b940e3fd9c50`.

Because the former positive prose had already been exposed, this recovery is corroboration under the original frozen protocol, not a new prospective first result.

## 2. Frozen experiment

The protocol retained the original subjects and denominator:

- development: `MAXSAT12-PMS`;
- no-retuning validation: `MAXSAT19-UCMS`;
- untouched cross-domain test: `QBF-2016`;
- official CV repetition 1 with ten outer test folds;
- calibration fold `1 + (test_fold mod 10)` and the remaining eight folds for proper training;
- eleven model specifications, three alpha values, and three route modes, for exactly 99 development candidates;
- one statewise virtual-best oracle within each scenario;
- learned and routed arms pay feature acquisition cost;
- the no-feature fallback arm pays no learned-feature cost;
- timeout and broader non-`ok` outcomes are reported separately.

The three paired route modes were `paired_upper`, `interval_no_harm`, and `direct_difference`. Frozen KNN and ExtraTrees full-selector references, the one-sided learned-action certificate, no-feature fallback, full learned selector, and oracle contextual route were retained as controls.

## 3. Exact observed result

No candidate satisfied the prospectively frozen MAXSAT12 development constraints. The deterministic tie-break selected only the least-bad row for complete adverse reporting:

- model: ExtraTrees, 128 trees, `min_samples_leaf=2`, `max_features=0.5`;
- alpha: `0.05`;
- route mode: `direct_difference`.

It changed the route on zero development instances. Consequently the paired route and full learned selector had identical total cost.

| Panel | Gate | Routed mean total cost | Full learned mean | No-feature fallback mean | Route coverage | Certificate failure |
|---|---:|---:|---:|---:|---:|---:|
| MAXSAT12-PMS | FAIL | 3292.7431 | 3292.7431 | 7652.9374 | 0.0000 | 0.0491 |
| MAXSAT19-UCMS | FAIL | 10392.3040 | 10392.3040 | 12392.3775 | 0.0000 | 0.0297 |
| QBF-2016 | FAIL | 1964.8780 | 1964.8780 | 4860.6993 | 0.0000 | 0.0364 |

The full learned selector beat the no-feature robust fallback in mean total cost on every panel, but the frozen paired certificate did not produce a nontrivial route. Calibration of the route score therefore did not yield selective decision value.

The exact terminal is

`FIBERGUARD_R18_NO_PAIRED_ROUTE_VALUE`.

## 4. Scientific interpretation

R18 is a prospective-protocol, outcome-exposed recovery **null**, not positive transfer evidence. It strengthens the adverse chain already exposed by R14 and R16:

1. exact complete-corpus fibres do not automatically transfer inductively;
2. a one-sided learned-action certificate may be calibrated while fallback routing is harmful;
3. adding a paired marginal certificate does not by itself create a useful deployed route;
4. the exact joint-policy language, route observation, compatibility relation, and acquisition timing must be audited directly, as formalized by the R19 replacement theorem.

The failure is not hidden by validation or test performance: the development gate itself had zero feasible candidates. MAXSAT19 and QBF are retained for complete adverse reporting only and cannot rescue the development failure.

## 5. Authority boundary

Supported:

- the prospective R18 protocol identity;
- the complete outcome-exposed recovery implementation and byte-identical replay;
- exact source/blob custody;
- the 99-candidate development denominator;
- the observed null terminal and all adverse panel metrics;
- marginal certificate semantics under exchangeability.

Not supported:

- the withdrawn positive R18 terminal;
- deterministic worst-case fibre safety;
- conditional validity on routed cases;
- arbitrary family-shift validity;
- pathwise randomization safety;
- strongest-baseline completeness;
- production value;
- external independence;
- novelty or journal authority.

The next admissible application experiment must use the exact R19 joint-profile subject and retain this null as a required baseline. It must not retune the R18 protocol or reinterpret zero routing as successful abstention.
