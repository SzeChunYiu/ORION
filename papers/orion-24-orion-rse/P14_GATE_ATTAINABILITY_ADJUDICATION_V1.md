# ORION-24 Gate-Attainability Adjudication V1

**Paper:** ORION-24 — ORION-RSE
**Issue:** #669
**Schema:** `ORION.ORION-24.GateAttainabilityAdjudication.v1`
**Receipt:** `P14_GATE_ATTAINABILITY_ADJUDICATION_V1.json`
**Adjudicator:** `verify_p14_gate_attainability_v1.py`
**Terminal:** `P14A_SUPERIORITY_GATES_UNMEASURABLE__QUESTION_ANSWERED_BY_P14C_AT_UNCHANGED_THRESHOLDS`

## What this changes, and what it does not

Nothing frozen is edited. P14A's protocol, seed, thresholds, receipt and terminal
are retained verbatim; `P14A_CONTROLLED_GOVERNANCE_SUPERIORITY_GATE_NOT_MET`
remains permanent and is not relabelled positive. P14B remains
diagnostic/non-authoritative. P14C's cases, gold labels, policies, comparators,
thresholds and canonical hash are untouched.

What changes is the **reading** of P14A's two failed gates. They were reported as
a negative result about the governance contract. They are a `CANNOT_CHECK`: a
measurement the frozen protocol was unable to take.

And, since 2026-08-22, the reading of P14B's eight passed gates. Its terminal
stands and is reachable in both directions — that half is a real result — but four
of the eight gates supporting it could not have said anything else, so the receipt
offers four readings where it appears to offer eight. Its disposition is recorded
as `TERMINAL_REACHABLE__GATE_COUNT_INFLATED`. Nothing about P14B is edited or
re-run by that either.

## The question nobody had asked

A preregistered gate publishes a threshold, and a receipt publishes which side of
it the run landed on. That report is identical in two different worlds — the run
measured the system and fell short of a bar it could have cleared, and the bar
was above every value the protocol's own sampling support can produce. A
serialized `false` cannot tell them apart.

P14A is honest on every other property. Its terminal is derived from a live
conjunction rather than written as a literal; its thresholds were frozen before
execution; its seed is published; its comparator is selected prospectively; its
digest reproduces; and the paper wrote its own root-cause audit and declined to
edit the result. None of that is a statement about the support of the statistic
the thresholds read.

## P14A: both failing gates read one quantity, and it cannot reach either bar

`MULTI_REVIEW` reproduces the gold adjudication except where a positive is a
same-evidence rereading of a live negative history. Over the 144 fact states the
case generator can emit, that exception is **one state**, and it is also
`MULTI_REVIEW`'s only false promotion. So the two gates that failed are the same
number under two thresholds:

- `strongest_baseline_false_promotion_ge_0_05` reads its frequency;
- `accuracy_gain_ge_0_08` reads `1.0 − (1 − its frequency)`, the same number.

The receipt prints both as `0.018375` because they are one quantity.

The eight case facts are independent Bernoulli draws whose rates are each
monotone in a different declared uniform, and `main()` mixes every family's draw
half-and-half with a fixed base. The prevalence is therefore a product whose
extrema over the declared box sit at corners, and it is computed exactly without
running anything:

| | value |
|---|---|
| infimum over the declared sampling support | `0.009085` |
| **supremum over the declared sampling support** | **`0.042326`** |
| the realized shipped run | `0.018375` |
| best of five registered admissible worlds, ending at the extremal corner | `0.040250` |
| the two frozen thresholds | `0.05`, `0.08` |

Measured over the five worlds the freeze admits — the shipped draw, an alternate
seed, and three nested sub-boxes of the declared ranges ending at the corner:

| gate | role | reason | best reachable | attainment margin |
|---|---|---|---|---|
| `strongest_baseline_false_promotion_ge_0_05` | PRECONDITION | `THRESHOLD_UNATTAINABLE` | `0.040250` | **`−0.009750`** |
| `accuracy_gain_ge_0_08` | HYPOTHESIS | `THRESHOLD_UNATTAINABLE` | `0.040250` | **`−0.039750`** |

No admissible world satisfies either. The remaining five gates are satisfied by
every admissible world, so `all(gates.values())` is `False` for every seed and
every family draw the protocol permits: **the conjunction had one reachable
value**, and the published terminal is the only terminal the artifact could have
printed.

Two further measurements bound the finding:

- **The emitter is not broken.** Re-opening the declared sampling ranges and
  nothing else — same seed, same nine arms, same seven thresholds, same terminal
  expression — moves the terminal to the positive branch in three of three
  registered capability worlds, with two distinct terminals observed and no inert
  case. The pass region is live; it simply lies outside the set of runs the
  preregistration admits.
- **The graded arm is the answer key.** `policy("ORION_RSE_FULL", c)` is
  `return gold(c)`, measured at **0 divergent points of 256**. Three of the five
  unconditional gates read that arm's own error rates, which is why they cannot
  be anything but `true`.

Both are recorded in the receipt and neither offsets the other.

## P14B: a positive terminal, asked the same question

P14B was never audited by this instrument. This receipt had a `p14a` key and a
`p14c` key and no `p14b`; `orion.programme.registry_coverage` recorded the
omission as its sharpest example, because P14B publishes a **positive** terminal
on eight gates all `true` and the paper that invented the instrument had not
pointed it at one. `orion.study.p14.balanced_governance` points it, after
reproducing the receipt's committed `replay_sha256` `784d57e6…d679e66` byte for
byte.

The answer has two halves, and collapsing them loses the finding.

**The terminal is sound.** What P14B leaves free is the same coordinate P14C
does: which implementation occupies the graded `ORION_RSE_FULL` slot. Its
protocol registers four component ablations. Over a seven-world register — the
shipped draw, two alternate seeds, and each ablation in the graded slot in turn —
the full contract clears all eight gates, every ablation fails at least one, and
**reachable terminals: 2**. No threshold is outside reach, which is precisely
what P14B was frozen to fix about P14A and did fix: the difficulty statistic
whose supremum was `0.042326` there is exactly `1/7 = 0.142857` here, in every
admissible run, because the strata are minted in equal numbers.

**Four of the eight gates could not have gone the other way.**

| gate | role | reason | why |
|---|---|---|---|
| `full_zero_false_promotion` | HYPOTHESIS | `BOTH_OUTCOMES_REACHABLE` | all four ablations false-promote |
| `full_discovery_recall_one` | HYPOTHESIS | **`THRESHOLD_UNCONDITIONAL`** | no registered policy can decline a promotable case |
| `strongest_baseline_false_promotion_ge_0_05` | PRECONDITION | `THRESHOLD_UNCONDITIONAL` | `1/7` in every admissible table — as a precondition should be |
| `accuracy_advantage_ge_0_08` | HYPOTHESIS | `BOTH_OUTCOMES_REACHABLE` | fails for donor, interaction and negative-history ablations |
| `retain_and_reopen_exact` | HYPOTHESIS | `BOTH_OUTCOMES_REACHABLE` | fails for `ABLATE_NEGATIVE_HISTORY` |
| `each_ablation_worse` | HYPOTHESIS | `BOTH_OUTCOMES_REACHABLE` | an ablation in the graded slot is not below itself |
| `matched_budget` | HYPOTHESIS | **`THRESHOLD_UNCONDITIONAL`** | the runner writes the literal `BUDGET = 7` into all nine arms |
| `byte_identical_replay` | PRECONDITION | `THRESHOLD_UNCONDITIONAL` | a determinism certificate about the instrument |

The two marked in bold are hypothesis gates satisfied by every world the freeze
admits, so their `true` is arithmetic. `full_discovery_recall_one` is exact and
provable before any run: of the 256 assignments of the eight case facts exactly
**three** are adjudicated `SUPPORTED_RESIDUAL` by gold, and all nine registered
policies return `SUPPORTED_RESIDUAL` on all three — the rule baselines promote
supersets of gold, and an ablation flips a fact to its permissive value, which
can only *add* promotions. The published receipt shows the consequence on its
face: all five arms in its `summary` report `useful_discovery_recall` of `1.0`.
It is the same gate `specification_conformance` reports as unexercised for P14C.

So "eight gates, all true" is **four readings and four constants**. That does not
make the terminal wrong; it makes the count of evidence supporting it half what
the receipt appears to offer. `threshold_panel()` returns `FAIL` on the two
unconditional hypothesis gates while `terminal_reach()` returns `PASS`, and
neither offsets the other.

Two further measurements bound it, reported and not rolled up:

- **The draw cannot move the terminal.** Over the shipped seed and two alternates
  with the shipped subject, `seed_only_terminal_reach` finds **one** reachable
  word — the balanced strata make every rate an exact fraction. The terminal's
  two words come entirely from substituting the graded implementation.
- **The graded arm is the answer key.** `policy("ORION_RSE_FULL", c)` is
  `return gold(c)`, measured at **0 divergent points of 256** — the circularity
  `P14B_PROTOCOL_CONFORMANCE_CORRECTION_V1.md` already records, and the reason
  the subject's own side of all four discriminating gates is fixed before the run.

A bookkeeping note, the mirror of P14A's: `main()`'s terminal expression is a
conjunction of **seven** gates. `byte_identical_replay` is asserted by the receipt
beside the seven the runner emits and never enters `all(gates.values())`. The
audit's replay measurement runs the aggregation twice in one process, which
establishes that it is a pure function of its seed and its registered policies;
it is weaker than the two fresh subprocesses `verify_p14c_protocol_adjudication_v2.py`
uses, and does not re-certify P14B's replay claim independently.

P14B's receipt, protocol, seed, thresholds, gold labels, comparators, arms and
terminal are retained verbatim, as is its standing
`P14B_NON_AUTHORITATIVE_PROTOCOL_MISMATCH` downgrade. Its evidential disposition
is recorded as `TERMINAL_REACHABLE__GATE_COUNT_INFLATED`.

## P14C: the same question, on the successor, over the coordinate it leaves free

P14A left the discriminator's prevalence to a random mixture. P14C fixes the
composition instead: four cases per semantic stratum over seven strata. The one
stratum no partial-review contract can reach, `RETAIN_NEGATIVE`, is therefore
exactly **`4/28 = 0.142857`** of the table in every admissible table — against
P14A's ceiling of `0.042326` for the same quantity.

What P14C leaves free is the **subject**: its protocol registers six
single-component ablations as implementations of the contract. Putting each in
the graded slot in turn gives a seven-world register a reviewer can audit line by
line, and over it:

- the full contract clears all eight gates; every one of the six ablations fails
  at least one;
- **reachable terminals: 2**. P14C's conjunction could have printed either word.

Disagreements with the frozen gold over the 28 cases: `RAW_POSITIVE` 16,
`REFLECTION_CHECKLIST` 12, `DONOR_AWARE_REVIEW` 8, `MULTI_REVIEW` 4,
`ORION_RSE_FULL` 0; ablations 1/1/1 for evidence-integrity, freeze and
identifiability and 4/4/4 for donor, interaction and negative history.

## The resolution: P14A's own thresholds, unedited, on an instrument that can move them

P14A's successor rule forbids changing its thresholds. They are not changed.
`0.05` and `0.08` are registered verbatim and read on P14C's benchmark, where the
statistic they bound is `0.142857` rather than capped at `0.042326`:

| P14A gate, threshold unchanged | reachable interval on P14C | realized | verdict |
|---|---|---|---|
| `strongest_baseline_false_promotion_ge_0_05` | `[0.142857, 0.142857]` over admissible tables | `0.142857` | **MET** |
| `accuracy_gain_ge_0_08` | `[0.000000, 0.142857]` over admissible subjects | `0.142857` | **MET** |

The second interval is what matters: `0.08` sits strictly inside it, so the gate
could have gone either way and did not have to pass. It fails for
`ABLATE_DONOR`, `ABLATE_INTERACTION` and `ABLATE_NEGATIVE_HISTORY`, and passes
for the full contract and the three validity ablations.

So the scientific question P14A's two gates encoded — *does the complete
governance contract separate from the strongest partial contract by the
preregistered margin, on a benchmark hard enough for the strongest partial
contract to false-promote at the preregistered rate?* — is answered
affirmatively, at P14A's own bars, under P14C's protocol identity. P14A's
terminal is not overturned; it is classified. It recorded an unmeasurable gate,
and the successor took the measurement.

## What this does not establish

- **Claim authority is P14C's, unchanged.** Specification-separated
  governance-contract conformance only. The adjudication specification is
  internally authored, so external scientific validity still requires blinded
  independent adjudication, realistic multi-domain packets, matched agent
  workflows and longitudinal testing.
- **One P14C hypothesis gate has no refutation capacity over the registered
  subjects.** `full_discovery_recall_one` is satisfied by all seven, because an
  ablation removes a check and a policy that reads fewer facts promotes more
  rather than fewer. No registered implementation abstains, so that gate's `true`
  is a property of the ablation register rather than evidence that the contract
  preserves valid discovery. It is reported by name in the receipt under
  `hypothesis_gates_without_refutation_capacity`. It does not affect the
  terminal's discrimination, which is carried by the other seven gates.
- **P14A's replay gate was never computed.** Its `replay_status` records "one
  protected execution completed; second replay deferred to successor package", so
  seven of eight preregistered conditions reached its terminal. The digest
  reproduces on re-execution here, which makes the omission a bookkeeping gap
  rather than a failed condition, but it is a frozen gate that was not evaluated.

## Reproduce

```
python papers/orion-24-orion-rse/verify_p14_gate_attainability_v1.py
python -m orion.study.p14.gate_audit                    # exits 3: P14A blocks
python -m orion.study.p14.balanced_governance           # exits 3: P14B's count blocks
python -m orion.study.p14.specification_conformance     # exits 0: P14C passes
python -m pytest tests/unit/study/p14 tests/unit/programme/test_gate_attainability.py
```

The instruments load the shipped `run_p14a_controlled_governance_v1.py`,
`run_p14b_balanced_governance_v1.py` and
`run_p14c_specification_separated_governance_v1.py` from this directory and
reproduce their committed digests — `3ac625b7…57a28fe`, `784d57e6…d679e66` and
`74032348…f01a63` — before any verdict is read, so a failure above is about ORION-24
and not about a local fixture.

## Failure class

`UNATTAINABLE_GATE_PREDETERMINED_TERMINAL`, recorded under
`research/failures/2026-08-unattainable-gate-predetermined-terminal/`. The
general lesson: **a negative is evidence only for as long as the protocol could
have produced a positive.** Freeze the threshold and the support together, or you
have frozen an outcome.
