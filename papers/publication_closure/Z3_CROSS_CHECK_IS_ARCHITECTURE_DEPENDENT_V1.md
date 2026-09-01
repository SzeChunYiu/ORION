# The P6 Z3 cross-check is architecture-dependent, and cannot be a blocking gate

**Status:** `FINDING__MEASURED__DISPOSITION_PROPOSED_NOT_APPLIED`
**Scientific authority delta:** `NONE`. Theorem 7 is untouched by this; see below.

## The observation

`test_p6_commutation_kernel.py::test_z3_refutes_the_negation` re-runs
`ck.z3_cross_check()` live. On CI it returns `UNKNOWN` with
`reason_unknown() == "timeout"`, and it has now done so at two different budgets:

| run | budget | result |
|---|---|---|
| `33512213821` | 60 s | `UNKNOWN` after 60.17 s |
| the job on #2069 | **300 s** | `UNKNOWN` after 300 s |

The 300 s budget is the one raised in #2033 precisely because 60 s was not enough. It was
not enough either.

## What it is not

**Not host contention.** The same call, on this machine, returns `PROVED` in **0.11 s** — and
in 0.03 s warm. A contended runner does not turn a 0.1 s query into a 300 s one; that is a
factor of roughly three thousand.

**Not the random seed.** Six seeds, same query, same machine:

| seed | verdict | wall |
|---|---|---|
| 0 | `unsat` | 0.045 s |
| 1 | `unsat` | 0.030 s |
| 7 | `unsat` | 0.011 s |
| 42 | `unsat` | 0.011 s |
| 1234 | `unsat` | 0.011 s |
| 99991 | `unsat` | 0.022 s |

Uniformly trivial, and `unsat` on the negation every time — which is the proof.

**Not the version.** Local z3 reports `5.1.0`; `uv.lock` pins `z3-solver==5.1.0.0`. The same
release.

## What remains

Architecture. This machine is arm64 macOS; the runner is x86-64 `ubuntu-24.04`. The query is
quantified over uninterpreted sorts — `ForAll` over a `DeclareSort`ed `Env` — which is the
fragment where E-matching order decides everything, and where two builds of the same release
can differ between instant and hopeless.

**Stated as a limit:** the Linux wheel was not tested here, so the architecture attribution
is the remaining explanation after eliminating the others, not a measurement. Running the
same six-seed sweep on an x86-64 host would confirm or refute it, and that is the next step
if anyone wants certainty.

## Why this does not weaken Theorem 7

The kernel proof is the primary evidence and is untouched. It is a serialized proof log
replayed from nothing by an LCF-style kernel, deterministic, and independently guarded by
tests that reject a mutated payload, a rerouted input, and a swapped conclusion.

The Z3 leg is a **cross-check** — a second opinion under a different engine — and the
committed artifact already records its outcome. `test_the_z3_cross_check_is_recorded_as_proved`
asserts `machine["z3_cross_check"]["outcome"] == "PROVED"`, runs in milliseconds, and passes.

So the theorem's evidence is intact whether or not the live re-run terminates on any
particular host.

## The disposition this argues for

**Keep** the recorded-outcome assertion in the fast job. It is deterministic and it is what
guards the artifact.

**Move** the live re-run out of a job named `fast`, into one where a budget of minutes is
acceptable, or gate it behind an explicit opt-in. A check that cannot terminate on the
architecture CI runs is not a gate on that architecture, and leaving it in place produces a
recurring red that has now blocked three unrelated pull requests — #2033's own run, #2038,
and #2069 — none of which touched P6.

**Do not** raise the budget again. Sixty seconds became three hundred and the answer did not
change; the variance being fought is not measured in seconds.

**Do not** downgrade an `UNKNOWN` to a pass. The guard added in #2033 exists to say which
world a failure is in, and it did that correctly here: *"Z3 returned UNKNOWN […] That is the
prover giving up, not the theorem being lost."* That message is the reason this was
diagnosable at all, and turning it into a skip would put back exactly the ambiguity it
removed.

Not applied here, because the disposition is a CI-topology decision and this document's job
is the measurement.
