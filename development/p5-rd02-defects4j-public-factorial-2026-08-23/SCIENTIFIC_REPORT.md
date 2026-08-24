# P5-RD-02 Defects4J public factorial scientific report

**Date:** 2026-08-23  
**Bridge:** `P5.PUBLIC_DEVELOPMENT_TO_PROTECTED_FRESHNESS_BRIDGE.V1`  
**Authority:** local, rights-bound public-development replay only  
**Independent units:** **n = 1** public project/bug-family cluster  
**Paper-level empirical blocker closed:** **no**

## Decision

The strongest result in this lane is narrow and descriptive:

> On the single public Defects4J `Lang-1` cluster, the already-known public
> fixed revision passed the public developer tests under both registered
> Java-11 distributions, while the public buggy revision retained the one
> registered triggering failure under both distributions. The recorded V2
> factorial therefore has implementation effect `+1.0`, environment effect
> `0.0`, interaction `0`, and primary terminal
> `IMPLEMENTATION_MAIN_EFFECT`.

This is a replay of known public fixed bytes, not a candidate-generated repair.
The evaluator is local. The four factorial cells are technical comparisons and
do not increase the independent sample size beyond one. The result supplies no
protected freshness, generality, population transport, external custody,
independence, host promotion, protected transfer, or P5 H1--H4 authority.
H1--H4 remain `CANNOT_CHECK`.

The lane terminal is:

`P5_RD02_N1_PUBLIC_KNOWN_FIX_REPLAY_ONLY__PROTECTED_FRESHNESS_AND_H1_H4_CANNOT_CHECK`

## Bound source and intervention

- Defects4J revision: `8c16da8230843cdc918eaf4ddb449637f02b83c6`.
- Public defect: Apache Commons Lang `Lang-1`.
- Original upstream revision: `396afc3e4693cfee182efe582455f2d97058c068`.
- Known public fixed revision: `d1a45e9738de5b3e299bb51e987565dcce55fee6`.
- Public fix-patch SHA-256:
  `2bacab48cc56c962cc906a3e95878735cacb2f231d4a64717a8798f1eb41090f`.
- Triggering test:
  `org.apache.commons.lang3.math.NumberUtilsTest::TestLang747`.
- Defects4J framework right: MIT at the pinned revision.
- Selected upstream code/test/configuration right: Apache-2.0, with retained
  `LICENSE.txt` SHA-256
  `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`.
- Issue prose and attachments were not accessed.

The candidate factor is original versus public known-fix bytes. The environment
factor is Homebrew OpenJDK `11.0.32.1+0` versus Eclipse Temurin OpenJDK
`11.0.32+9`, on the same native arm64 macOS host and shared build tooling. A
zero effect across these two Java-11 distributions is not evidence of broad
environment invariance.

## V1 adverse result is immutable

V1 remains `CANNOT_CHECK` with modifier
`HARMFUL_OR_ADVERSE_CELL_PRESENT`; its result SHA-256 is
`0c2f2760f622a6260e8ed34cb648df309f51b9bdb3ea170918487152033c7c0e`.
All four cells were invalid:

| V1 cell | retained adverse cause | valid | outcome |
|---|---|---:|---|
| `C0E0` | Defects4J rejected the registered Java-17 runtime before checkout | no | `CANNOT_CHECK` |
| `C1E0` | Defects4J rejected the registered Java-17 runtime before checkout | no | `CANNOT_CHECK` |
| `C0E1` | checkout succeeded under Java 11, but V1 incorrectly required the raw upstream tree instead of the Defects4J-prepared tree | no | `CANNOT_CHECK` |
| `C1E1` | checkout succeeded under Java 11, but V1 incorrectly required the raw upstream tree instead of the Defects4J-prepared tree | no | `CANNOT_CHECK` |

V2 is a separately frozen successor. It keeps both environment arms within
Defects4J's Java-11 contract and binds the prepared trees and
`.defects4j.config` hashes. It does not rewrite V1.

## V2 recorded factorial

| cell | bytes | Java environment | failing tests | valid | success |
|---|---|---|---:|---:|---:|
| `C0E0` | prepared public original | Homebrew JDK 11 | 1 registered trigger | yes | no |
| `C0E1` | prepared public original | Temurin JDK 11 | 1 registered trigger | yes | no |
| `C1E0` | prepared public known fix | Homebrew JDK 11 | 0 | yes | yes |
| `C1E1` | prepared public known fix | Temurin JDK 11 | 0 | yes | yes |

Recorded effects:

- implementation: `(1 + 1 - 0 - 0) / 2 = +1.0`;
- environment: `(0 + 1 - 0 - 1) / 2 = 0.0`;
- interaction: `(1 - 0) - (1 - 0) = 0`;
- registered adverse modifier: `NO_ADVERSE_CELL`.

The result is consistent with the public fixed revision repairing this one known
public defect under the two local Java-11 distributions. It does not estimate
the success rate of self-editing, causal diagnosis, minimal-revision selection,
or fresh transfer.

## V2 checkout-log provenance negative

V2 reused the same retained stdout/stderr paths for a cell's checkout and test
phases. `Path.with_suffix` collapsed, for example,
`V2.C0E0.checkout` and `V2.C0E0.test` to the same
`V2.C0E0.stdout.txt` and `V2.C0E0.stderr.txt`. The later test phase overwrote
the checkout streams.

Direct byte audit found:

- **8/8** retained V2 test streams match their declared hashes;
- **0/8** retained V2 checkout streams match their declared hashes;
- the original V2 checkout stream bytes cannot be recovered from the retained
  files.

Therefore exact V2 checkout-log byte preservation has terminal
`CANNOT_CHECK_EXACT_CHECKOUT_STREAM_BYTE_PRESERVATION`. This does not silently
rewrite the recorded V2 factorial terminal, but it is a material provenance
negative. A `SHA256SUMS` manifest can correctly authenticate the actual current
files while the checkout hashes declared inside `RESULT_V2.json` remain
unreproducible; manifest integrity and phase-log provenance are different
claims.

## V3 archival replay

V3 is a distinct audit-only successor, frozen after V2 outcomes were already
known. It uses four phase-qualified stream paths per cell. All 16 retained V3
streams match their declared hashes, all four per-cell path sets are distinct,
and all four cells reproduce the same local outcome pattern. Its log-retention
terminal is `ARCHIVAL_REPLAY_COMPLETE`.

V3 does not recover the overwritten V2 checkout bytes and cannot be an
independent replication or confirmatory experiment. It grants no scientific,
protected, fresh, promotion, or H1--H4 authority. Its result SHA-256 is
`e743ebb77a31c4c4606f7eded8045a60c78fa2f251c13908051156cfd4a1fb6e`.

## Scientific boundaries and next discriminator

The next scientifically material discriminator is not another local replay of
`Lang-1`. It is a genuinely new, source-disjoint, provider-held panel frozen
before candidate generation, with protected labels/evaluators, independent
custody, exact subject and comparator identities, fresh-transfer tasks, harm
adjudication, access telemetry, and signed result receipts. It must cover the
registered P5 revision classes and same-visible-symptom design rather than
relabel public implementation fixes as protected class gold.

Until those bindings and outcomes exist, preserve both bridge terminals:

- `P5_BRIDGE_PUBLIC_DEVELOPMENT_BOUND__PROTECTED_PROVIDER_AND_SIX_ARM_EXECUTION_CANNOT_CHECK`;
- `P5_WIDE_READY_FOR_EXTERNAL_PROJECT_PANEL_NOT_A_SCIENTIFIC_RESULT`.

No local replay authorizes promotion or a positive P5 H1--H4 claim.
