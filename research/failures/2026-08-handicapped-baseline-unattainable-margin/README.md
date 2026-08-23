# A superiority margin measured over a baseline that could not have won it

**Observed:** 2026-08-21, auditing P12A's positive terminal — the one paper in
this sweep whose verdict is derived from live gates rather than issued.

## Failure

P12A registers a matched-budget benchmark. Every item hides a resource
requirement in one of four regimes — `EASY (0,0)`, `ACCESS (2,0)`,
`REASON (0,2)`, `BOTH (1,1)` — every policy gets a two-unit budget, and success
is exact coverage on both axes. `run_p12a_matched_budget_v1.py` runs 16 families
of 512 items at protected seed `2026082112` and its receipt records

```json
"mean_joint_gain_vs_best_one_axis": 0.334716796875,
"family_block_bootstrap_95ci": [0.2860076904296875, 0.38269348144531223],
"worst_family_joint_gain": 0.158203125,
"terminal": "P12A_JOINT_ALLOCATION_SUPERIORITY_SUPPORTED"
```

Re-implemented from the seed in `orion.study.p12.allocation_arms`, the world
reproduces all eight published summary numbers to the bit and the runner
reproduces `replay_sha256 = 0194bc09…8947`. The terminal is not a literal: it is
`"…SUPPORTED" if all(gates.values()) else "…GATE_NOT_MET"`, and the sibling
paper P14 lands on the negative branch, so the branch is live. Four of the seven
gates reject every wrong allocation rule put to them. The budget is genuinely
matched — over all 8,192 items and all five arms, `budget_violations == 0`, and
that is a fact rather than an accident of the seed.

The variable the claim names is how many pre-outcome signals a policy reads. The
variable it does not name is **how many allocations a policy is allowed to
emit**, and the runner holds both inside a single lambda body:

| arm | may allocate | signals read | achieved | ceiling under a perfect signal | items no allocation of its set can satisfy |
| --- | --- | --- | --- | --- | --- |
| `FIXED_11` | `(1,1)` | none | 0.515503 | 0.515503 | 3,969 / 8,192 |
| `ADAPTIVE_STATE_ONLY` | `(0,0) (2,0)` | `s_c` | 0.463135 | **0.475464** | **4,297 / 8,192** |
| `ADAPTIVE_REASON_ONLY` | `(0,0) (0,2)` | `s_r` | 0.452759 | **0.463623** | **4,394 / 8,192** |
| `JOINT_FROZEN` | `(0,0) (1,1) (2,0) (0,2)` | `s_c s_r` | **0.858154** | 1.000000 | **0 / 8,192** |

The winner can satisfy every item in the benchmark. Each baseline is unable to
satisfy about half of them, at any signal, because the allocation those items
require is not in its set: `ADAPTIVE_STATE_ONLY` can never emit `(1,1)` or
`(0,2)`, so it fails every `BOTH` and every `REASON` item before reading
anything. Its ceiling, 0.475464, sits below `JOINT_FROZEN`'s *achieved* 0.858154
in **16 of 16 families**, and it already extracts 0.463135 of that 0.475464 — a
headroom of **0.012329**. There was no adaptation deficit to measure.

So the margin splits:

| | value |
| --- | --- |
| reported margin, `JOINT_FROZEN` − `ADAPTIVE_STATE_ONLY` | 0.395020 |
| unreachable before the run (winner's score − baseline's ceiling) | **0.382690** |
| in play for the mechanism under test | **0.012329** |
| handicap share of the reported margin | **96.9 %** |

and the headline number splits the same way. Hand *both* one-axis arms a perfect
signal, take the better per family, and `JOINT_FROZEN` still beats them by
**0.319336** — **95.4 %** of the published 0.334717, in 16 of 16 families.

### The second signal is not the variable, and inside the baseline it is inert

Holding the two coordinates apart in a 2×2 gives the effect sizes directly:

| | 2 actions `{(0,0),(2,0)}` | 4 actions |
| --- | --- | --- |
| **1 signal** | 0.463135 | 0.809448 |
| **2 signals** | 0.463135 | 0.858154 |

- main effect of **adding the second signal**: **+0.024353**
- main effect of **widening the action set**: **+0.370667**

The two left-hand cells are equal, and not approximately. With the action set
`{(0,0),(2,0)}` the nearest option is `argmin` over `sc² + sr²` and
`(sc−2)² + sr²`, in which `s_r` cancels. Measured with
`orion.programme.refutation_capacity.axis_sensitivity` over a 21×21 signal grid,
comparing only points that agree on `s_c`:

| rule | axis | verdict-changing sibling pairs | inert |
| --- | --- | --- | --- |
| nearest in `{(0,0),(2,0)}` | `s_r` | **0 / 4,410** | **yes** (×21) |
| nearest in `{(0,0),(2,0)}` | `s_c` | 2,310 / 4,410 | no |
| nearest in all four | `s_r` | 2,502 / 4,410 | no |

`ADAPTIVE_STATE_ONLY` is not a policy that declines to use the second signal. It
is a policy the second signal cannot reach. "One axis versus two" is not a
contrast that can be run inside that action set at all.

### The gap widens as the signals sharpen

An advantage that comes from adapting shrinks as both arms' signals improve,
because a perfect signal is the easy case for everyone. Sweeping `sigma` with
every other coordinate of the world held (`run_families(..., sigma=…)`):

| sigma | `ADAPTIVE_STATE_ONLY` | `JOINT_FROZEN` | one signal / four actions | published-style gain | capability-matched gain |
| --- | --- | --- | --- | --- | --- |
| 0.00 | 0.4755 | 1.0000 | 1.0000 | **0.4612** | **0.0000** |
| 0.20 | 0.4755 | 0.9994 | 0.9912 | 0.4606 | 0.0057 |
| 0.30 | 0.4753 | 0.9871 | 0.9491 | 0.4484 | 0.0336 |
| 0.55 | 0.4641 | 0.8621 | 0.8087 | 0.3364 | 0.0475 |
| 0.80 | 0.4476 | 0.7451 | 0.7206 | 0.2418 | 0.0187 |
| 1.50 | 0.4116 | 0.5846 | 0.6082 | 0.1310 | **−0.0278** |
| 3.00 | 0.3800 | 0.4933 | 0.5380 | 0.0786 | **−0.0518** |
| shipped `[0.30,0.80]` | 0.4631 | 0.8582 | 0.8094 | 0.3347 | 0.0408 |

The published gain is at its **maximum** where the signals are perfect and
adaptation is worth nothing, and it falls monotonically as the signals decay.
That is the signature of a structural gap, not an informational one. The
capability-matched column runs the other way, peaks at 0.0475, and goes negative
past `sigma = 1.5` — where reading the second signal actively *hurts*, because
the joint rule spends its precision distinguishing `EASY` from `REASON` when
`(0,2)` covers both.

### The shipped gate battery, with the action set as the only change

Substituting a capability-matched baseline — **one signal, the same four
allocations** — into the runner's own seven gates, at the runner's own
thresholds, comparators, bootstrap and seed:

| | as shipped | capability matched |
| --- | --- | --- |
| mean joint gain | 0.334717 | **0.040771** |
| family-block 95 % CI | [0.286008, 0.382693] | [0.031006, 0.050659] |
| worst-family joint gain | 0.158203 | **0.001953** |
| `mean_joint_gain_ge_0_15` | true | **false** |
| `worst_family_joint_gain_ge_0_05` | true | **false** |
| `mean_joint_minus_fixed_ge_0_10` | true | true |
| terminal | `…SUPERIORITY_SUPPORTED` | **`…SUPERIORITY_GATE_NOT_MET`** |

Two independently written matched baselines — nearest option on the read axis
with the dominating tie-break, and a plain three-way threshold on that one signal
— produce **0.040771 and 0.001953 to the bit**, on both. The `FIXED_11` gate is
untouched by the substitution and still passes, so the flip is not the battery
collapsing; it is the two gates that name the one-axis comparator, and only
those.

**This is scoped, and the scope matters.** A matched baseline that keeps the four
allocations but breaks the tie at `s_c ≈ 0` toward `(0,0)` instead of the
dominating `(0,2)` scores a gain of 0.196411 with a worst family of 0.134766, and
the terminal stays `SUPPORTED`. So the *terminal flip* requires a competent
matched baseline. The *ceiling* result does not depend on any policy choice at
all: 0.319336 of the 0.334717 lies above what the shipped baselines could reach
with a perfect signal, in 16 of 16 families, and that number is a property of the
action sets alone.

### Three of the seven gates could not have failed

`all(gates.values())` is only as strong as the gates, so each was registered as a
`MechanizedCheck` whose `accepts` re-runs the whole 16×512 world with
`JOINT_FROZEN` replaced by a candidate rule, against six declared wrong
allocation rules (`always_easy`, `always_access`, `always_fixed_11`,
`deaf_to_reasoning_signal`, `swapped_axes`, `anti_joint`):

| shipped gate | refuted | survived | verdict |
| --- | --- | --- | --- |
| `mean_joint_gain_ge_0_15` | 6 | 0 | PASS |
| `family_bootstrap_lower_gt_0` | 6 | 0 | PASS |
| `mean_joint_minus_fixed_ge_0_10` | 6 | 0 | PASS |
| `worst_family_joint_gain_ge_0_05` | 6 | 0 | PASS |
| `budget_respected` | **0** | **6** | FAIL |
| `signals_pre_outcome_by_construction` | **0** | **6** | FAIL |
| `oracle_ceiling_holds` | **0** | **6** | FAIL |

The three are dead for three different reasons, and all three are exhaustible:

- `budget_respected` counts allocations with `c + r > 2`. Every allocation any
  arm can emit comes from `{(0,0),(0,2),(1,1),(2,0)}` — the joint options and the
  four requirements are the same four pairs — whose maximum sum is exactly 2. The
  counter is unsatisfiable, not zero. This is `VACUOUS_GUARD_ZERO_DENOMINATOR`
  with the denominator equal to the numerator's impossibility.
- `signals_pre_outcome_by_construction` is the literal `True`, written into the
  gate dict beside the computed ones. It restates the protocol's clause 2; it
  does not evaluate it.
- `oracle_ceiling_holds` compares `ORACLE_JOINT` against `JOINT_FROZEN`, and
  `ORACLE_JOINT` allocates the requirement itself, so `satisfies(req, req)` is 1
  on every item and its rate is 1.0 in every family of every world the runner can
  generate.

This is a real result about P12 in both directions and should be read as one. Its
*numeric* gates are genuine gates — that is what separates P12A from the P8
defect, and it is why the flip above is worth something: the same four gates that
reject six wrong rules also reject the shipped comparison once the comparator can
compete. Three gates in the conjunction are decoration.

## Failure class

`HANDICAPPED_BASELINE_UNATTAINABLE_MARGIN`

A superiority margin was reported over a comparison arm that could not have
achieved the winner's score under any value of the mechanism under test. The
arms differ in the named variable *and* in a capability the claim does not
mention, and the unnamed one alone accounts for the margin. Every downstream
statistic is arithmetic over a comparison that was decided by construction.

This is the next case after the four that precede it, and it is the first where
the earlier instruments all return clean:

- `2026-08-unreachable-operator-inert-ablation/` — the **independent** variable
  never varied: the arm never reached the operator it ablated.
- `2026-08-vacuous-guard-zero-denominator/` — the **dependent** variable never
  varied: the guard was never pressed.
- `2026-08-unapplied-treatment-vacuous-null/` — the **cause** did not vary: the
  treatment was applied and was the identity.
- `2026-08-label-recoverable-from-construction-cue/` — both varied, and the
  correlation was with the construction.
- `2026-08-unfalsifiable-check-zero-refutation-capacity/` — the **verdict** could
  not vary.
- here — **everything varied, and a second thing varied with it.** P12A's arms
  are all reachable; its treatment is applied on all 8,192 items; four of its
  seven gates have real refutation capacity; its budget parity is exact and its
  replay is byte-identical. Ask any of the previous four questions of this
  campaign and the answer is a clean pass.

Three properties let it survive review.

1. **The constraint the protocol names is genuinely enforced.** "Identical total
   budget" is true — 0 violations in 8,192 items × 5 arms — and it is the
   sentence a reader checks. Nothing in the protocol lists the arms' action sets
   side by side, and the runner cannot: each arm is one lambda in which the
   signal it reads and the allocations it may emit are the same expression.
2. **The handicap is invisible in every quantity the receipt reports.** Rates,
   family means, a 20,000-resample block bootstrap, a worst-family minimum, a
   content digest, a two-run byte-identical replay and an independent V2
   adjudication all hold exactly, because none of them is a statement about what
   the losing arm was able to do. The ceiling is the one number that separates
   the two worlds and it appears in no artifact.
3. **The name of the baseline describes the wrong coordinate.**
   `ADAPTIVE_STATE_ONLY` names the signal it reads. The handicap lives in the
   allocations it may emit, and "state only" is a fair description of both, which
   is exactly why the conflation is not visible in the ledger, the protocol or
   the receipt.

## Correct response

1. Do not read a margin before establishing the loser could have earned the
   winner's score. `orion.programme.attainable_margin.ArmCapability` carries a
   measured `ceiling` beside `achieved` and requires both a
   `capability_definition` and a `ceiling_definition` in a sentence, for the same
   reason `GuardExercise.opportunity_definition` is required: a ceiling nobody
   can state is a second score, not a bound. It refuses at construction to hold
   an arm that beats its own ceiling.
2. Split the margin rather than reporting it. `AttainableMargin.handicap` is the
   part no value of the mechanism could have closed and `attainable_margin` the
   rest; on P12A those are 0.382690 and 0.012329.
3. Return three values. A baseline whose ceiling is below the winner's score is
   `Outcome.CANNOT_CHECK` — not `FAIL`, because a confounded comparison does not
   show the mechanism to be worthless, it shows nothing — and `CANNOT_CHECK`
   blocks a promotion exactly as `FAIL` does. `MarginAssessment` refuses at
   construction to pair `PASS` with any vacuity reason.
4. Refuse to score the panel. `require_attainable(margins, label="P12A")` raises,
   naming both one-axis arms and their ceilings, before any mean, interval or
   worst-case minimum is read.
5. Keep the reason set to states that can occur. A separate verdict for "the
   baseline was already at its ceiling" was written, and then removed once its
   own test showed it unreachable: a positive margin over a saturated baseline
   *is* a baseline whose ceiling is below the winner's score. Shipping it would
   have reintroduced `UNFALSIFIABLE_CHECK_ZERO_REFUTATION_CAPACITY` inside its
   own remedy, and the test that names this now pins the reason set at four.
6. Hold the two coordinates in separate fields. `orion.study.p12.Arm` carries
   `signals_read` and `allocations` apart, so a panel in which the winner is the
   only arm holding four allocations is legible at the point the arms are
   declared, and `gate_battery(families, one_axis_arms=…)` makes substituting a
   matched comparator a one-argument change rather than a re-implementation.
7. Point the instrument at the shipped artifact. `orion.study.p12.allocation_arms`
   consumes the protected seed in the runner's own draw order and its test
   asserts, against the committed receipt file, that all eight published summary
   numbers and the `replay_sha256` still match before any perturbation is read
   from it. An instrument that only ever runs on its own fixture is the failure
   it was written to catch.
8. Measure each gate's refutation capacity, not just its value.
   `orion.study.p12.gate_theories` registers all seven against six declared wrong
   allocation rules and names the three that no wrong rule can fail. The three
   are held as data (`STRUCTURALLY_UNFALSIFIABLE`), so a new gate cannot join the
   conjunction unnoticed.
9. Repair the comparison. The honest version of P12A's discriminator holds the
   allocation set fixed across arms and varies only how many signals a policy
   reads, and on this world that effect is +0.024353 with a worst family of
   0.001953 — a real, small, reportable negative. Re-registering the protocol
   around it is the paper lane's call and is **not** done here; the diagnosis and
   the instrument are.

## General lesson candidate

**A margin is evidence about a mechanism only for as long as the loser could
have closed it.** Denominators, applied treatments, refutation capacity,
byte-identical replay, an independent adjudicator and exact budget parity all
survive a handicapped comparator intact — every one of them held here, and the
V2 adjudication was a genuine correction that caught a genuine omission — because
none of them is a statement about what the losing arm was capable of.

The sharper form, and the one that generalizes past this repository: **matching
the constraint the protocol names is not the same as matching the arms, and an
experiment must state what its baseline was allowed to do, not only what it was
allowed to spend.** Two policies on an identical budget are not comparable if one
of them cannot express the answer. Every superiority claim in this repository
should be asked what its comparator scores under a perfect version of the
mechanism under test, and any margin larger than that number is a fact about the
arms rather than about the mechanism.

The operational test is one line and costs one extra run: give the baseline a
perfect signal, a perfect oracle, a perfect anything for the coordinate under
test, and see whether it now reaches the winner's published score. If it does
not, the experiment was decided before it ran.
