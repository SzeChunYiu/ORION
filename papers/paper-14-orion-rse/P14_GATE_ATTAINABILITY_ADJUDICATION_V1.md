# P14 Gate-Attainability Adjudication V1

**Paper:** ORION-P14 — ORION-RSE
**Issue:** #669
**Schema:** `ORION.P14.GateAttainabilityAdjudication.v1`
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
python papers/paper-14-orion-rse/verify_p14_gate_attainability_v1.py
python -m orion.study.p14.gate_audit                    # exits 3: P14A blocks
python -m orion.study.p14.specification_conformance     # exits 0: P14C passes
python -m pytest tests/unit/study/p14 tests/unit/programme/test_gate_attainability.py
```

The instruments load the shipped `run_p14a_controlled_governance_v1.py` and
`run_p14c_specification_separated_governance_v1.py` from this directory and
reproduce their committed digests — `3ac625b7…57a28fe` and `74032348…f01a63` —
before any verdict is read, so a failure above is about P14 and not about a local
fixture.

## Failure class

`UNATTAINABLE_GATE_PREDETERMINED_TERMINAL`, recorded under
`research/failures/2026-08-unattainable-gate-predetermined-terminal/`. The
general lesson: **a negative is evidence only for as long as the protocol could
have produced a positive.** Freeze the threshold and the support together, or you
have frozen an outcome.
