# ORION-02 R18 — recovered paired-route null

Date: 2026-08-27

Current terminal:

`FIBERGUARD_R18_NO_PAIRED_ROUTE_VALUE`

Authority:

`OUTCOME_EXPOSED_RECOVERY_CORROBORATION`

## Custody

The formerly reported positive R18 transfer terminal remains retracted. Its claimed execution commit, workflow run, runner modules, and complete result were absent.

The prospective protocol itself remains valid and pre-outcome:

- `bc3387916139af8a739a910eb58c354f73fb2a24` — protocol/source freeze;
- `c2df6e2b47b69f387a33e0ebe5e272fc8a1aad74` — scientific contract;
- `1040eaaa56ab5daf087dc01fc9988c7f3a4f2045` — initial workflow definition.

A complete replacement implementation was committed without using the withdrawn positive prose as an input. Immutable recovery subject:

`ac4a50f85a147f5933cd2055809c7ac30b29e3c1`.

Workflow run `33023149716`, job `98358163251`, executed the frozen subject twice byte-identically on `coseal/aslib_data@551b22beef8df17de59286b4822ef720e0aa4d6f`. A later run `33024187320` rechecked the durably committed recovery bytes.

The complete recovery JSON is retained in the source branch history and has SHA-256

`8136ac6e614406a51270342d73786dfec43a9ecdac81f62e815cd14d1a739c45`.

Its pre-digest canonical result subject has SHA-256

`e3a0ccb27484cbb5a950a5de10d60966edccee2c76272e79f239b940e3fd9c50`.

This current-main record is a content-bound custody pointer; it does not rewrite the historical result bytes.

## Frozen experiment

- development `MAXSAT12-PMS`;
- no-retuning validation `MAXSAT19-UCMS`;
- untouched test `QBF-2016`;
- official repetition-1 ten-fold custody;
- one proper-training, calibration, and test partition per outer fold;
- eleven model specifications × three alpha values × three route modes = 99 development candidates;
- one statewise virtual-best oracle within scenario;
- learned and routed arms pay feature cost;
- no-feature fallback pays no learned-feature cost;
- timeout and broader non-`ok` outcomes remain separate.

## Exact result

Zero of 99 candidates satisfied the prospectively frozen MAXSAT12 development constraints. The deterministic least-bad row—ExtraTrees with 128 trees, leaf size 2, `max_features=0.5`, alpha `0.05`, direct-difference routing—changed zero routes.

| Panel | Gate | Routed mean | Full learned mean | No-feature fallback mean | Route coverage | Certificate failure |
|---|---:|---:|---:|---:|---:|---:|
| MAXSAT12-PMS | FAIL | 3292.7431 | 3292.7431 | 7652.9374 | 0.0000 | 0.0491 |
| MAXSAT19-UCMS | FAIL | 10392.3040 | 10392.3040 | 12392.3775 | 0.0000 | 0.0297 |
| QBF-2016 | FAIL | 1964.8780 | 1964.8780 | 4860.6993 | 0.0000 | 0.0364 |

The full learned selector beat the no-feature robust fallback in mean cost on every panel, but the paired marginal certificate produced no nontrivial selective route. Validation and test results are retained for adverse reporting and cannot rescue the failed development gate.

## Consequence for the paper

R18 is not transfer evidence. Together with R14 and R16 it establishes a negative deployment sequence:

1. exact closed-world fibres need not recur inductively;
2. a calibrated one-sided learned-action certificate can route into a worse fallback;
3. paired marginal calibration can remain non-actionable even when its empirical failure rate is controlled;
4. the legal joint learned/fallback profile language, route observation, compatibility relation, common-oracle accounting, and acquisition timing are therefore indispensable, as formalized by R19.

## Authority boundary

Supported: protocol identity, recovery implementation, byte-identical execution, source custody, 99-candidate denominator, exact null terminal, and adverse panel metrics.

Not supported: the withdrawn positive terminal, deterministic fibre safety, conditional routed-case validity, arbitrary family-shift validity, pathwise safety, strongest-baseline completeness, production value, external independence, novelty, or journal authority.
