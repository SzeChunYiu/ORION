# A hostile attack whose survival was decided by which arm was placed in the gate

**Observed:** 2026-08-21, auditing P11G — the paper's `PRIMARY` hostile nonlinear
evidence — for whether the attack it reports as failed was ever able to succeed.

## Failure

P11 is the good citizen of the batch on the properties the neighbouring records
deny. It ships a preregistered negative it refuses to retune
(`P11D_SPARSE_DECODER_GAP_NOT_MET`, with `P11D_NEGATIVE_ROOT_CAUSE_V1.md`
explaining why the ≥4× claim is false), it discloses its own replay defect
(`UNSEEDED_LIBLINEAR_SPARSE_SOLVER`), it demotes its own positive after hostile
review found an `n_jobs=-1` protocol mismatch (P11F → non-authoritative), and its
successor puts the two-subprocess byte-identical replay inside the terminal
decision path rather than in prose. Its terminal is derived, not a literal:

```python
terminal = ("P11G_DETERMINISTIC_TREE_DECODER_GAP_SUPPORTED"
            if all(gates.values()) else "P11G_DETERMINISTIC_TREE_DECODER_GAP_NOT_MET")
```

The claim ledger records the result as **`SUPPORTED / HOSTILE NONLINEAR /
PRIMARY`** and the paper's headline reads "a replay-gated deterministic nonlinear
tree successor remains `NOT_REACHED` through `n=1024` where compiled state
reaches the target at `n=64`".

The question none of that answers is whether the tree arm had a value of its
statistic that the protocol was able to produce.

`orion.study.p11.decoder_attack_reach` loads the shipped runner and replays its
RNG stream — same query draws, same test set, same training draws, and the
estimator `random_state` values the runner's own `tree_seed`/`compiled_seed`
derive from its seed — with the arm, the resource envelope, the columns the
attack is shown and the data seed lifted out as parameters. At the shipped
settings it reproduces the committed scientific payload digest
`a2b0c33ce3c39e54ca1aa400a2b7d52d019fc4503f6cd5eb726c7b8bbe79a7cc` and every
curve value the receipt publishes, to the last bit. Every number below was
produced by that module.

### Two of the four scientific gates read the tree arm, and neither can fail

P11G's positive terminal needs all four scientific gates. `no_answer_laundering`
and `compiled_by_64` are about the defence. The two that are supposed to be the
hostile test are

| gate | fails only if |
| --- | --- |
| `tree_threshold_ge_256` | the tree arm reaches mean accuracy 0.95 at `n=64` or `n=128` |
| `delta64_ge_0_20` | the tree arm gets within 0.20 of the compiled arm at `n=64` |

Over **48 fresh seeds of the frozen protocol** — the protocol says "fresh data
seed" and fixes one, so any seed is a draw it admits, and each world moves the
data seed and, with it, the estimator `random_state` values the runner derives
from it — the tree arm's statistic never comes close to either:

| cell | `tree@64` min / mean / **max** | `tree@128` min / mean / **max** | `delta64` **min** / mean / max |
| --- | --- | --- | --- |
| `(17,4,5)` | 0.5227 / 0.5566 / **0.5859** | 0.5597 / 0.6025 / **0.6375** | **0.4112** / 0.4419 / 0.4773 |
| `(19,3,7)` | 0.5227 / 0.5680 / **0.5949** | 0.5756 / 0.6162 / **0.6508** | **0.3730** / 0.4174 / 0.4628 |

All four gates are satisfied in **48 of 48** worlds, and the terminal is
`GAP_SUPPORTED` in **48 of 48**. The nearest any world comes to bringing a gate
down:

| gate | statistic | direction | worst value over 48 worlds | margin |
| --- | --- | --- | --- | --- |
| `no_answer_laundering` | laundering failures | `AT_MOST 0.0` | 0 | `+0.000000` |
| `compiled_by_64` | smallest compiled accuracy @64 | `AT_LEAST 0.95` | 0.957438 | `+0.007438` |
| `tree_threshold_ge_256` | best attack accuracy below `n=256` | `AT_MOST 0.95` | 0.650798 | **`+0.299202`** |
| `delta64_ge_0_20` | smallest `compiled − attack` @64 | `AT_LEAST 0.20` | 0.372965 | **`+0.172965`** |

The two hostile gates are the two the attack has to break, and the attack's
shortfall on them is **`−0.299202`** and **`−0.172965`**. The tree arm starts at
chance and stays there: `0.5376` at `n=64` in the shipped run, where chance is
`0.5`.

The shipped register `admissible_worlds()` carries the first six of these, which
is what `orion.study.p11.attack_audit` blocks on; the 48-seed sweep is the same
measurement widened, and it moves nothing.

So `all(gates.values())` is `True` for every seed the protocol permits.
`P11G_DETERMINISTIC_TREE_DECODER_GAP_SUPPORTED` is the only terminal the
artifact could ever have printed, and the branch that prints `GAP_NOT_MET` is
live code with an empty pre-image.

### It is not the resource envelope

The protocol froze 96 trees and `max_features="sqrt"`. Re-opening only that —
same seed, same data, same gates — does not move the statistic into reach:

| tree arm | `(17,4,5)` @64 / @128 | `(19,3,7)` @64 / @128 |
| --- | --- | --- |
| 96 trees, `sqrt` (**frozen**) | 0.5376 / 0.5875 | 0.5927 / 0.6017 |
| 256 trees, `sqrt` | 0.5359 / 0.6103 | 0.6085 / 0.6018 |
| 1024 trees, `sqrt` | 0.5370 / 0.6295 | 0.6199 / 0.5999 |
| 4096 trees, `sqrt` | 0.5356 / 0.6444 | 0.6208 / 0.5974 |
| 96 trees, all features | 0.5826 / 0.6307 | 0.5366 / 0.6009 |
| 1024 trees, half the bank per split | 0.6265 / **0.7541** | 0.6191 / 0.6920 |

A **43× larger ensemble** moves `n=64` accuracy in the first cell from `0.5376`
to `0.5356` — that is, not at all. The most generous setting measured is still
`0.196` short of the threshold at `n=128` and `0.16` short of undercutting
`delta64`.

### It is not the sample budget either — the arm is the wrong family for the target

The construction's label is `sign(Σ_{j∈active} bank_j)`: an **`r`-sparse linear
threshold on the universal parity bank**. Executed check — a unit-weight linear
functional supported on the active columns, fitted on nothing at all, scores
**1.000, 1.000, 1.000** on the protected test set in both cells. There is no
approximation error in the universal representation; the entire sample cost is
*support discovery*.

An axis-aligned tree ensemble is the one family that cannot do that search here.
With `max_features="sqrt"` the split candidate set is 48 of 2,380 columns in
cell `(17,4,5)` and 31 of 969 in `(19,3,7)`, against `r=5` and `r=7` informative
columns; the probability that a split candidate set contains **any** informative
column is `0.0969` and `0.2041`. Nine splits in ten in the first cell are chosen
among pure noise.

Handing the tree arm the answer to the discovery problem confirms it. Give the
same 96-tree ExtraTrees the `r` active columns and nothing else — the exact
representation the compiler produces — and it still does not clear the bar:

| bank given to the tree arm | `(17,4,5)` @64 / @128 | `(19,3,7)` @64 / @128 |
| --- | --- | --- |
| active columns only (`m=0` nuisance) | **0.9386** / 0.9795 | **0.8112** / 0.8728 |
| active + 5 nuisance | 0.8643 / 0.9181 | 0.8182 / 0.8517 |
| active + 20 | 0.7939 / 0.8851 | 0.7983 / 0.8363 |
| active + 50 | 0.7319 / 0.8272 | 0.7543 / 0.8046 |
| active + 100 | 0.6992 / 0.7911 | 0.7227 / 0.7740 |
| active + 300 | 0.6125 / 0.7246 | 0.6289 / 0.6728 |
| active + 1000 | 0.5649 / 0.6560 | 0.5858 / 0.5989 |
| the full bank (**frozen**) | 0.5376 / 0.5875 | 0.5927 / 0.6017 |

The first three rows print `P11G_DETERMINISTIC_TREE_DECODER_GAP_NOT_MET` and the
rest print `GAP_SUPPORTED`, so the emitter is a function of its run:
`measure_receipt_responsiveness` over the three banks a reader can agree must not
earn the positive terminal reports **3 of 3 cases moved the verdict, 0 inert, 2
distinct verdicts, `PASS`**. The finding is about the frozen bank, not about a
decoder that cannot decode.

Even at zero nuisance the tree decoder does not reach 0.95 at `n=64` in either
cell — it needs `n=128` in the first and, on the full frozen grid, `n=512` in the
second — where the compiled L2 arm is at 1.0000 and 0.9869 with 64 samples. **`0.0614` of the published `+0.4624` gap and `0.1757` of
the published `+0.3942` gap is the change of decoder family, not the change of
state.** The comparison P11G reports changes the representation and the learner
at the same time.

### The register already contained an arm that wins, on P11G's own data

This is the half that makes the finding a fact about arm placement rather than
about nonlinearity. `P11C_STRONGER_DECODER_ATTACK_PROTOCOL_V1.md` froze **three**
universal-state arms — `UNIVERSAL_L2`, `UNIVERSAL_L1`, `UNIVERSAL_EXTRA_TREES` —
and froze the rule that combines them:

> Define the best hostile universal threshold as the earliest threshold reached
> by any of the three universal-state arms.

Each successor carried one arm forward and gated on that arm alone: P11D and
P11E on `UNIVERSAL_L1`, P11G on `UNIVERSAL_EXTRA_TREES`.

**Correction, 2026-08-22.** This record was written while P11C was
`CANNOT_CHECK`, and said the rule "was never applied to an outcome". That is no
longer true. `P11C_EXECUTION_RECEIPT_V1.md` records the frozen protocol run to
completion twice in fresh processes, and its payload carries the rule's own
statistic per cell (`best_universal_threshold_0_95`: 256 and 256) and the gate it
feeds (`best_universal_threshold_ratio_ge_4`: true). The rule was applied — by
P11C, to P11C's own frozen data. Reading the two freezes against each other then
settles where it stops: it feeds a `>=4x` *ratio* gate on a five-query, `n=2048`,
8,192-test ladder over a pool whose tree arm is 256 estimators, for a claim about
a family of attacks; P11G froze an absolute `>=256` gate on a three-query,
`n=1024`, 4,096-test ladder over one 96-tree arm, for a claim about one decoder,
and P11D froze outright that it "does not settle the frozen ExtraTrees attack".
So P11C's rule governs P11C and does not bind P11G, and correct response 6 below
is withdrawn as stated.

What survives that correction is the axis, which is what this record is actually
about and which does not depend on whose rule it is:

Run all three on **P11G's own frozen data stream** — identical queries, test set,
training draws and estimator seeds, only the decoder swapped:

| arm | `(17,4,5)` threshold | `(19,3,7)` threshold | `delta64` |
| --- | --- | --- | --- |
| `UNIVERSAL_EXTRA_TREES` (**reported**) | `NOT_REACHED` | `NOT_REACHED` | 0.4624 / 0.3942 |
| `UNIVERSAL_L2` | `NOT_REACHED` | `NOT_REACHED` | 0.4568 / 0.4120 |
| `UNIVERSAL_L1` | **128** | **256** | 0.3252 / 0.3258 |

The best threshold over the three registered arms is **128 and 256**. Placed in
P11G's own gate 3, which requires `>= 256` **in both cells**, `UNIVERSAL_L1`'s
128 in the first cell makes P11G's terminal expression print
`P11G_DETERMINISTIC_TREE_DECODER_GAP_NOT_MET`. Two of the three comparable pairs
on the `decoder_arm` axis change the verdict, so the terminal is a function of
which registered arm was carried forward — on P11G's own bytes, under P11G's own
gate arithmetic, with no rule borrowed from anywhere.

Over 12 seeds of the frozen protocol the flip is unanimous: `UNIVERSAL_L1`
reaches 0.95 at `n=128` in cell `(17,4,5)` in **12 of 12** worlds, and gate 3
read through the best of the three registered arms holds in **0 of 12**. The
same gate, on the same bytes, is unconditionally `True` read through the arm
P11G reported and unconditionally `False` read through the arm P11D and P11E
carried. What it measures is which arm was placed in it.

### What P11's own documents already say, and what they do not

The paper is not hiding the L1 result: `P11D_NEGATIVE_ROOT_CAUSE_V1.md` records
sparse universal thresholds of 128 and 256, calls the ≥4× claim false, and even
lists P11C as "stronger unresolved attack … listed as an open attack rather than
inferred from P11D". P11E replicates the 128/256 pair on a fresh seed and the
ledger carries it.

Two things follow that no P11 document states. First, the numbers that make the
`PRIMARY` nonlinear claim would fail P11G's own gate if the paper's own best
known attack were read into it — 128 is not `>= 256`. Second, `NOT_REACHED
through n=1024` is quoted as if it were a stronger result than the L1 arm's 128,
when it is a weaker one: an arm that reaches nothing anywhere is an arm whose
gate reading is the same in every world, and P11G's own claim-authority sentence
("retains a registered low-sample advantage over a deterministic single-thread
96-tree ExtraTrees decoder") is exactly as narrow as the measurement supports.
The gap is between that sentence and the ledger row that promotes it to `HOSTILE
NONLINEAR / PRIMARY`.

## Failure class

`UNWINNABLE_ATTACK_PREDETERMINED_SURVIVAL`

A hostile protocol freezes an attack, runs it, and reports that the defence
survived. The attack's statistic has no value inside the protocol's own
admissible support that would have brought the gate down, so the survival was
fixed before the seed was drawn. The freeze is real, the seed is real, the digest
is stable, the replay is inside the terminal path, the terminal is derived from a
live conjunction — and the conjunction has one reachable value.

This extends the family rather than repeating it, and it is the *adversarial*
member:

- `2026-08-unreachable-operator-inert-ablation/` — the **independent** variable
  never varied.
- `2026-08-vacuous-guard-zero-denominator/` — the **dependent** variable never
  varied.
- `2026-08-unapplied-treatment-vacuous-null/` — the **cause** did not vary.
- `2026-08-label-recoverable-from-construction-cue/` — the **label** was
  recoverable from the construction.
- `2026-08-invertible-commitment-vacuous-custody/` — the **commitment** opened.
- `2026-08-unfalsifiable-check-zero-refutation-capacity/` — the **predicate**
  could not be false.
- `2026-08-supplied-premise-unbuilt-decision/` — the **decision** was never made.
- `2026-08-unconditional-terminal-self-issued-authority/` — the **verdict** had
  no predicate at all.
- `2026-08-unattainable-gate-predetermined-terminal/` — the **gate** had no
  reachable pass region, so a published negative was arithmetic.
- here — **the adversary had no reachable win.** P14A is the same emptiness read
  from the defender's side: a gate nobody could pass. This is a gate nobody could
  fail, reached through the attacker, and it is worth less than P14A's because a
  survived attack is *promoted* rather than retained. `commitment_custody`'s
  `SCHEME_NOT_DEMONSTRATED` is the nearest existing neighbour and it does not
  cover this: the attack here demonstrably ran, produced a real curve, and fed a
  gate that can be written `False`. What is empty is the intersection of that
  gate's failing region with the set of runs the freeze admits.

Four properties let it survive review, and the first two are why an audit tuned
to P14A would still miss it.

1. **Hostility looks like integrity, more than a negative does.** A paper that
   attacks itself with a "stronger decoder", loses one of those attacks (P11D),
   demotes one of its own positives for a protocol mismatch (P11F), and puts a
   two-subprocess byte-identical replay inside the terminal path has spent every
   signal a reviewer reads for good faith. Nobody asks the surviving attack to
   prove it could have won.
2. **The reviewed defect was real, and fixing it consumed the review.** Hostile
   PR review caught `n_jobs=-1` in P11F and P11G was frozen to fix exactly that.
   The correction is right and it is about the estimator's threading. One layer
   up, the arm being made deterministic was an arm that could not win under any
   threading.
3. **`NOT_REACHED` reads as a strong result.** `NOT_REACHED through n=1024`
   sounds like the attack was pushed to its limit and broke. It is the opposite:
   it is the reading an arm gives when its curve never leaves the neighbourhood
   of chance, and it is the same reading in every world, which is what makes the
   gate uninformative.
4. **Two live gates make the receipt look discriminating.** Six `true`s across
   four scientific gates and two replay gates reads as a panel that could have
   separated. The two replay gates are live and were the point of the P11F
   correction; the two scientific gates that carry the hostile claim are not.

## Correct response

1. Ask a *survived attack* for its reachable win before quoting the survival.
   The instrument is the one already in the tree:
   `orion.programme.gate_attainability` takes a statistic, a frozen threshold and
   a register of **admissible worlds**, and `THRESHOLD_UNCONDITIONAL` — every
   admissible world satisfies the gate — is `Outcome.FAIL`. Nothing new was
   needed. The novelty of this record is the *direction it is pointed*, at the
   arm that lost rather than the arm that won, and P11G is the case that shows
   the existing three-valued verdict already covers it.
2. Report the margin, not the boolean, and report it from the right end.
   `GateReach.attainment_margin` names the world closest to *satisfying*, which
   is the number an unattainable gate needs; an unconditional gate needs the
   mirror, so `closest_refuting_margin` reads the smallest margin in the
   register. Here that is `+0.299202` and `+0.172965` — the attack's shortfall,
   `−0.299202` and `−0.172965`. A serialized `true` says only that the attack
   lost.
3. Register worlds the freeze admits and say why. A "fresh data seed" protocol
   admits any seed, which is the whole reachable set here because everything else
   is pinned; registering a *different cell* would widen the protocol instead of
   measuring it, and belongs in the capability register, not the admissible one.
4. Ask the terminal, not the gates. `measure_terminal_reach` intersects per-world
   readings: P11G's four scientific gates have `distinct_terminals == 1`.
5. Keep the capability measurement beside the attainability one and let neither
   offset the other. P11G is `PASS` on responsiveness — reopen the tree arm's
   bank and the terminal moves — and `FAIL` on attainability. That pair is the
   diagnosis: a responsive emitter whose losing region lies outside its own
   preregistration.
6. ~~When a protocol freezes a *pool* of attacks and a combination rule, apply
   the rule.~~ **Withdrawn as stated** — see the correction above: P11C applied
   its own rule to its own data, and a rule frozen for one protocol's gate,
   ladder and claim does not bind a successor that froze its own. The durable
   form is narrower and borrows nobody's rule: **when a terminal depends on which
   of several registered arms is placed in its gate, and the receipt carries that
   axis with one value, the record owes a declaration of every registered value.**
   `refutation_capacity.axis_sensitivity` measures it and
   `decoder_attack_reach.arm_disclosure_gaps` blocks until the declaration
   exists;
   `papers/paper-11-state-as-computation/P11G_ARM_PLACEMENT_ADJUDICATION_V1.md`
   is that declaration for P11G.
7. Decompose a gap that changes two things at once. P11G compares logistic
   regression on `r` compiled columns against ExtraTrees on the full bank.
   Holding the decoder fixed and moving only the representation attributes
   `0.0614` of `0.4624` and `0.1757` of `0.3942` to the decoder family. The
   mechanism claim can carry the remainder and not the whole.
8. Check whether the attack's hypothesis class contains the target. The label is
   an `r`-sparse linear threshold on the bank; a unit-weight linear functional on
   the active support scores `1.000` with no training data. An attack family that
   cannot represent the target cheaply is not a stronger attack, it is a
   different question.
9. Do not add a parallel vocabulary for it. This record adds no module to
   `orion.programme`: the verdict is `gate_attainability`'s
   `THRESHOLD_UNCONDITIONAL`, the register is its `AdmissibleWorld`, the
   denominator is `GuardExercise`, the capability half is
   `terminal_responsiveness.measure_receipt_responsiveness`, the arm axis is
   `refutation_capacity.axis_sensitivity`, and the three-valued roll-up is
   `records.Outcome`. `commitment_custody`'s `SCHEME_NOT_DEMONSTRATED` is the one
   candidate that looked like a fit and is not one: it fires when nobody
   attacked, and here somebody did.
10. Point the instrument at the shipped artifact. `decoder_attack_reach` loads
   `run_p11g_deterministic_tree_decoder_v1.py` from `papers/` and reproduces its
   committed payload digest before transcribing a claim; a test pins the digest
   and the published curve values. An instrument that only runs on its own
   fixture is the failure it was written to catch.
11. Do not repair P11. Its protocols are frozen and its receipts are retained by
    the paper's own rule. What is owed there is a ledger correction: the P11G row
    is evidence about a 96-tree ExtraTrees decoder on a 2,380-column parity bank
    — which is what its own claim-authority sentence says — and not `HOSTILE
    NONLINEAR / PRIMARY` support for the mechanism. **Done, 2026-08-22:** that row
    now reads `HOSTILE NONLINEAR / ARM-SCOPED`, the arm axis and the
    decoder/state decomposition are in the paper's own prose (`MANUSCRIPT.md`
    5.4.1 and 5.4.2), and `P11G_ARM_PLACEMENT_ADJUDICATION_V1.md` carries the
    adjudication — every frozen byte retained, no published number moved. The
    diagnosis, the instrument and the blocking audit are still here.

`orion.study.p11.attack_audit` runs all of it and exits `3`:

```
  reachable terminals: 1
  every admissible world satisfies: no_answer_laundering, compiled_by_64,
                                    tree_threshold_ge_256, delta64_ge_0_20
  responsiveness: PASS (HELD_UNDER_EXERCISE), 0/3 cases ignored, 2 verdicts
  best-of-arms thresholds per cell: [128, 256] (P11G's gate wants >= 256)
  decoder_arm axis: 3 values, 3 comparable pairs, 2 verdict-changing, inert: False
  P11C's best-of-arms rule does not bind P11G   (different gate, ladder, claim)
  decision axes carried in the receipt with one value: decoder_arm -> declared
  outcome: FAIL   (terminal_reach: the attack had no reachable win)
```

## General lesson candidate

**A survived attack is evidence only for as long as the attack could have won.**
Freezing the attack before execution, publishing its seed, pinning every
estimator's `random_state`, putting a two-process byte-identical replay inside
the terminal path, and retaining a sibling protocol's negative verbatim all
survive an unwinnable attack intact — every one of them held here — because none
of them is a statement about the support of the statistic the hostile gate reads.

The sharper form: **an adversary is a measurement instrument, and an instrument
that cannot register a positive has no null.** P14A showed that a threshold
frozen without measuring its statistic's support preregisters an answer rather
than a test. The adversarial case is worse in one respect, because its answer is
promoted rather than retained: a defence that survives is written into a ledger
as support, so the direction the empty pre-image points is the direction the
claim grows. Every hostile protocol in this repository should be asked, before
its survival is read, for one admissible world in which the attack wins — and if
the protocol froze a pool, for the pool's best arm rather than the one that was
carried forward.

Stated once for the family this extends: `UNREACHABLE_OPERATOR_INERT_ABLATION` is
a mechanism that never ran, `VACUOUS_GUARD_ZERO_DENOMINATOR` an outcome that
could not vary, `UNAPPLIED_TREATMENT_VACUOUS_NULL` a cause that did not vary,
`LABEL_RECOVERABLE_FROM_CONSTRUCTION_CUE` a label explained by the construction,
`INVERTIBLE_COMMITMENT_VACUOUS_CUSTODY` a seal that opened,
`UNFALSIFIABLE_CHECK_ZERO_REFUTATION_CAPACITY` a predicate that could not be
false, `SUPPLIED_PREMISE_UNBUILT_DECISION` a decision nobody made,
`UNCONDITIONAL_TERMINAL_SELF_ISSUED_AUTHORITY` a verdict with no predicate,
`UNATTAINABLE_GATE_PREDETERMINED_TERMINAL` a threshold no admissible run could
reach — and this one an **adversary no admissible run could lose to**.

## Residuals and reopen coordinates

- P11 is not repaired (see Correct response 11). The audit blocks, which is the
  honest state, and `papers/paper-11-state-as-computation/` is untouched by this
  work.
- The unattainability here is a measured register plus a structural upper bound,
  not a closed-form supremum like P14A's. What is proved by execution is that the
  gates hold in 48 of 48 draws of the frozen protocol, that no resource setting
  in the tree family measured moves the statistic within `0.196` of the
  threshold, and that even the oracle representation — the `r` active columns and
  nothing else — leaves the arm short of `0.95` at `n=64` in both cells. A
  closed-form bound on ExtraTrees' sample complexity for `r`-sparse parity
  majorities would be stronger and is not claimed.
- P11G's receipt is not *wrong*. The tree arm really does sit at chance through
  `n=1024` and the compiled arm really does reach 0.95 at `n=64`. What is denied
  is that comparing those two numbers measured the accessibility of the state
  rather than the mismatch between an axis-aligned ensemble and a sparse linear
  target.
- The mechanism P11 claims is not refuted here, and one measurement in this
  record supports it: the nuisance ladder shows the tree arm's `n=64` accuracy
  falling monotonically from `0.9386` to `0.5376` as the bank grows from 5
  columns to 2,380, which is the discovery cost the paper attributes to universal
  state. The finding is about what P11G's gate can license, not about whether the
  placement law is real.
- P11D and P11E are untouched by this record. Their arm is the capable one; their
  2× and 4× residuals are the paper's real hostile result, and they are what the
  synthesis claim should rest on.
- P11C has since run to completion under its own protocol identity and applied
  its own best-of-arms rule there, at exactly its gate boundary and with an
  11-of-20 sweep behind it, so it carries no claim authority in either direction.
  The measurement here transplants that rule onto P11G's data, which is evidence
  about P11G's arm axis, not a P11C terminal and not a verdict from a rule that
  governs P11G.
- `UNIVERSAL_L1`'s threshold in cell `(19,3,7)` is 256 at 11 of 12 seeds and 128
  at one (`2026082123`). The gate-3 flip does not depend on that cell: cell
  `(17,4,5)` reaches 128 at all 12.
- Reopen if `run_p11g_deterministic_tree_decoder_v1.py` changes: the pinned
  `a2b0c33c…79a7cc` payload digest will red first.

---

## Successor executed 2026-08-22

This record's residual says "P11 is not repaired… `papers/paper-11-state-as-computation/` is untouched", and correct-response 11 says "Do not repair P11." Both still hold and are the right instruction: **P11G's frozen protocol is untouched, its terminal is permanently unwinnable, and the audit still exits 3 on it.** What has changed is that the question was re-asked under a protocol that could answer it.

The diagnosis sharpened first. All four of P11G's gates are `THRESHOLD_UNCONDITIONAL`, not `THRESHOLD_UNATTAINABLE` — every admissible world *satisfies* them, which is the opposite failure to P14A's and needs the opposite reading. Two of the four supports are now exact rather than sampled: `no_answer_laundering` is `[0, 0]` because for odd `r ≥ 3` the majority-sign of `r` distinct parity characters equals no single character as a function on `{−1,1}^d`, so the count's only reachable value is 0 against `x ≤ 0`; and the statistic lattice is `1/12288`, on which neither `0.95·12288` nor `0.20·12288` is an integer, so no reachable value can land on a bar.

`P11H` re-asks it, carrying P11G's `0.95` and `0.20` bars **unedited** — the P14A→P14C move. Three pre-freeze measurements chose the lever rather than guessing it: capacity is not it (a 43× ensemble moves `0.5376 → 0.5356`), bank width is not it (sweeping complete banks `91 → 2380` at `r=7` never crosses `0.95`), and the width of the compiled state is (`1.0000 → 0.9736 → 0.8674 → 0.7810` across `r = 3, 5, 7, 9`). A bank-width ladder would have reproduced this record's defect in a new file.

The step whose absence caused the defect runs first and is published before the seed: `ThresholdPanel` **PASS**, nothing unattainable, two discriminating hypothesis gates, `distinct_terminals = 2` over 15 admissible draws, **3 of 15 clearing every gate**. That last figure is the power of the design, stated in advance. Rungs were admitted only if verdict-stable across three preflight seeds, and that rule cut both ways — it rejected rungs on the attack's gate *and* on the defence's.

**The attack won.** `P11H_POOLED_UNIVERSAL_ATTACK_PREVAILED`: `pooled_universal_threshold_ge_256` reached `1.0000` against `≤ 0.95`, `delta64` was `0.050586` against `≥ 0.20`. The sharp part is the decomposition: at the drawn regimes the decoder-family half of the gap is exactly `+0.0000`, a state share of **100%** against 86.7% and 55.4% in P11G's cells — the decomposition goes P11's way *harder* and the defence still loses. Across the ladder the pool reaches `0.95` by `n=128` at every `r=3` rung and no `r=7` rung, while the bank moves `91 → 969` columns inside each half without changing a verdict. The advantage is governed by the width of the compiled state, not the size of the universal representation.

The earned-survival branch did not occur: 3 of 15 draws would have produced it and the seed drew one of the other 12. Both outcomes retire this record's finding, because what it names is a terminal that could not move — and this one could.

Unresolved and named rather than smoothed: the `r=5` boundary was excluded before execution for verdict instability across three preflight seeds, in both directions, and needs more queries or a seed-averaged statistic. And no closed-form accuracy ceiling exists for ExtraTrees on `r`-sparse parity majorities, so gates 2–4's supports remain measured registers rather than derived intervals like P14A's `0.042326`.
