# P11G Arm-Placement Adjudication V1

**Paper:** ORION-ORION-21 — State as Computation
**Issues:** #471, #664, #667
**Schema:** `ORION.P11G.ArmPlacementAdjudication.v1`
**Instrument:** `orion.study.p11.decoder_attack_reach`, audited by `python -m orion.study.p11.attack_audit`
**Terminal:** `P11G_TERMINAL_RETAINED__SCOPED_TO_THE_ARM_PLACED_IN_ITS_GATE`

## What this changes, and what it does not

Nothing frozen is edited. P11G's protocol, seed, arms, thresholds, receipt and
terminal are retained verbatim. `P11G_DETERMINISTIC_TREE_DECODER_GAP_SUPPORTED`
remains the terminal its frozen gates produced on its frozen seed, both
fresh-subprocess scientific payloads still have SHA-256
`a2b0c33ce3c39e54ca1aa400a2b7d52d019fc4503f6cd5eb726c7b8bbe79a7cc`, and no
published ORION-21 number moves. P11C, P11D, P11E and P11F are untouched.

What changes is the **reading** of that terminal, and one row of the claim
ledger. P11G's receipt publishes curves for one universal-state arm. The
programme registered three. On P11G's own frozen bytes the terminal is a
function of which of the three is placed in the gate, and the receipt carries
that axis with exactly one value. The terminal is therefore evidence about the
arm it names — which is what P11G's own claim-authority sentence says — and not
about universal-state decoding.

Two things follow, and they cut in opposite directions. The **placement claim**
survives and is quantified below: most of the published `n=64` gap is the change
of state rather than the change of decoder family. The **`HOSTILE NONLINEAR /
PRIMARY` promotion** does not, and the ledger row is narrowed to the arm.

## Part 1 — does a combination rule frozen in one protocol bind another?

`P11C_STRONGER_DECODER_ATTACK_PROTOCOL_V1.md` froze three universal-state arms
and the rule that combines them:

> Define the best hostile universal threshold as the earliest threshold reached
> by any of the three universal-state arms.

Transplanted onto P11G's own frozen data stream — identical queries, test set,
training draws and estimator seeds, only the decoder swapped — that rule gives
best-of-arms thresholds of **128 and 256**, and P11G's gate 3 wants `>= 256` in
both cells. The audit reports this and will keep reporting it. The question this
part settles is which protocol the rule governs.

### The premise that was retired

The instrument was built on 2026-08-21 on the premise that P11C "exceeded its
execution window and is `CANNOT_CHECK`, so that rule was never applied to an
outcome". That was true when it was written and is false now.
`P11C_EXECUTION_RECEIPT_V1.md` records the run executed to completion, twice, in
fresh processes, in 1m47s, with nothing changed to make it finish. Its frozen
payload `P11C_STRONGER_DECODER_ATTACK_RESULT_V1.json` carries the rule's own
statistic per cell (`best_universal_threshold_0_95`: **256 and 256**) and the
gate it feeds (`best_universal_threshold_ratio_ge_4`: **true**), and terminates
at `P11C_STRONGER_DECODER_GAP_SUPPORTED`.

The rule is not unapplied. It was applied, by P11C, to P11C's own frozen data.

### The two freezes ask different questions

`rule_binding()` reads the two protocols against each other and refuses to
transcribe any of this if either file stops containing the words.

| respect | `ORION.P11C.StrongerDecoderAttack.v1` | `ORION.P11G.DeterministicTreeDecoder.v1` |
|---|---|---|
| gate the rule feeds | "the best hostile universal threshold is at least 4x the compiled threshold in both cells" | "tree-universal 0.95 threshold `>=256` or `NOT_REACHED` in both cells" |
| scale ladder | "Training sizes: `64, 128, 256, 512, 1024, 2048`." | "train sizes: `64,128,256,512,1024`;" |
| test size | "Test size: `8192`." | "test size: `4096`;" |
| protected queries per cell | "Five protected queries per cell" | "three protected queries per cell;" |
| the pooled tree arm | "`UNIVERSAL_EXTRA_TREES`: 256 ExtraTrees" | "`n_estimators=96`" |
| claim served | "survives fixed sparse-linear and nonlinear tree-ensemble attacks." | "over a deterministic single-thread 96-tree ExtraTrees decoder operating on the complete universal parity bank." |

Each row alone would keep a rule inside its own protocol. Together they say the
rule is not portable at all: it is a **ratio** against a compiled threshold, not
an absolute `>=256`; it is defined over five queries per cell to `n=2048` on
8,192 test points, not three to `n=1024` on 4,096; and two of the three arms it
pools are not registered by P11G, while the third is a 256-tree ensemble where
P11G froze 96 at `n_jobs=1`. P11C's pool cannot be assembled inside P11G's
freeze. `registered_pool()` builds a hybrid — P11C's arm identities on P11G's
construction — and that hybrid is a new unfrozen experiment, not a frozen rule.

### The programme already froze the non-crossing rule in its own voice

P11D was the first single-arm successor, and it froze this:

> It does not settle the frozen ExtraTrees attack or establish a universal
> nonlinear lower bound.

P11D, P11E and P11G then each re-froze a **single-arm statistic** under its own
protocol identity — "universal-L1 threshold / compiled threshold >=4 in both
cells", "sparse universal threshold >=128 or `NOT_REACHED` in both cells",
"tree-universal 0.95 threshold `>=256` or `NOT_REACHED` in both cells" — and
P11G's freeze says outright that "P11G is a new successor; it does not edit or
relabel P11F."

That is a deliberate decomposition of P11C's pooled question into arm-scoped
questions, each with its own freeze, its own seed and its own claim authority.
It is not an unapplied rule.

**Finding.** P11C's best-of-arms rule governs P11C. It does not bind P11G, and
the transplanted `[128, 256]` reading is not a refutation of P11G's terminal.

## Part 2 — what the transplant measured anyway: `decoder_arm`

The finding above disposes of the *rule*. It does not dispose of the *axis*, and
the axis is the part that reaches the paper.

Running all three registered universal arms on P11G's own frozen data stream —
identical queries, test set, training draws and estimator seeds, only the
decoder swapped — and reading P11G's own four scientific gates on each:

| arm | 0.95 threshold per cell, censored at 256 | terminal P11G's own gates print |
|---|---|---|
| `UNIVERSAL_L2` | >=256, >=256 | P11G_DETERMINISTIC_TREE_DECODER_GAP_SUPPORTED |
| `UNIVERSAL_L1` | 128, >=256 | P11G_DETERMINISTIC_TREE_DECODER_GAP_NOT_MET |
| `UNIVERSAL_EXTRA_TREES` | >=256, >=256 | P11G_DETERMINISTIC_TREE_DECODER_GAP_SUPPORTED |

The reported arm is `UNIVERSAL_EXTRA_TREES`; it is the only one the receipt
publishes curves for. Thresholds are censored at 256 because that is all gate 3
distinguishes: a curve reaching the target at 256, at 1024 or nowhere are one
value to it, and `>=256` says that without promoting a censored reading to
`NOT_REACHED`.

`refutation_capacity.axis_sensitivity` on the `decoder_arm` axis: **3 values, 3
comparable pairs, 2 verdict-changing, inert `False`**. This is the mirror of
ORION-16's donor axis, which was carried with five values and changed nothing, so
every count it multiplied was a relabelling. Here the axis changes the terminal
and is carried once.

The flip is entirely gate 3. `UNIVERSAL_L1` reaches mean accuracy 0.95 at
`n=128` in cell `(17,4,5)`, and `128` is not `>= 256`. Its `n=64` gaps are
`+0.3252` and `+0.3258`, so it clears P11G's `delta64_ge_0_20` gate comfortably;
what it does not clear is the threshold gate P11G's positive terminal needs.

### This is not a new measurement, and that is the point

ORION-21's own documents already carry the number. `P11D_NEGATIVE_ROOT_CAUSE_V1.md`
records sparse universal thresholds of 128 and 256 and calls the ≥4× claim
false; P11E replicates the 128/256 pair on a fresh seed; and
`P11C_EXECUTION_RECEIPT_V1.md` sweeps it — over twenty seeds of the P11C
construction, `UNIVERSAL_L1` in cell `(17,4,5)` reads `128` in 9 and `256` in
11, so the conjunction P11C's gate 3 asks for holds in **11 of 20 draws**, and
the second cell never moves.

What no ORION-21 document stated before this one is that the two facts meet: the arm
whose 128 the paper reports as a *negative* result would, placed in P11G's gate,
print `P11G_DETERMINISTIC_TREE_DECODER_GAP_NOT_MET` on P11G's own bytes. Reading
`NOT_REACHED through n=1024` as a stronger result than the L1 arm's 128 inverts
it: an arm that reaches nothing anywhere gives the same gate reading in every
world, which is what makes that gate uninformative about the mechanism.

**Declaration.** The axis is `decoder_arm`. Its registered values, each value's
censored threshold pair on P11G's data, and the terminal each prints are the
three-row table above. The shipped receipt carries one of the three.
`arm_disclosure_gaps()` in `orion.study.p11.decoder_attack_reach` recomputes
every one of those strings from the replayed runner and compares them against
this file; the audit blocks while any is missing, and blocks again if a future
ORION-21 receipt publishes another verdict-changing axis with one value.

## Part 3 — the decomposition, in both directions

P11G compares L2 logistic regression on `r` compiled columns against a 96-tree
ExtraTrees ensemble on the complete parity bank. That moves the representation
and the learner at the same time. Holding the decoder at ExtraTrees and moving
only the representation — `COMPILED_EXTRA_TREES`, the same ensemble on the `r`
active columns — separates the two:

| cell | published gap at `n=64` | decoder-family half | state half | state share |
|---|---:|---:|---:|---:|
| `(17,4,5)` | +0.4624 | +0.0614 | +0.4010 | **86.7%** |
| `(19,3,7)` | +0.3942 | +0.1757 | +0.2185 | **55.4%** |

Read one way, this **undercuts the terminal as published**: `+0.4624` and
`+0.3942` are quoted as the compilation advantage, and 13.3% and 44.6% of them
are the change of decoder family. The `n=64` gap between compiled state and this
tree arm is not wholly attributable to compilation, and the ledger's wording is
narrowed accordingly.

Read the other way, it **supports the placement claim**, which is the paper's
actual residual. The state half is the majority in both cells and the large
majority in the first. Query-conditioned construction is doing most of the work
in the published comparison, and it is doing it in the direction the placement
account predicts: the same decoder, shown the compiled columns instead of the
bank, needs far fewer samples. That is a statement about where the structural
search is paid, and it survives the arm-scoping above intact — it is measured
with the decoder held fixed, so no choice of universal arm changes it.

## What a successor would need to carry the claim as published

P11G's terminal is retained and is not relabelled. A successor that wants to say
what the ledger's `HOSTILE NONLINEAR / PRIMARY` row said needs all four of:

1. **A pooled gate, frozen in its own protocol.** Register every universal-state
   arm the successor intends its claim to cover, freeze the combination rule
   inside that protocol's own positive gate, and read the gate through the pool.
   A claim about universal-state decoding cannot be gated on one arm; a claim
   about one decoder can, and must then be worded as one.
2. **A gate whose failing region the protocol can reach.** All four of P11G's
   scientific gates hold in every world its freeze admits — 48 of 48 fresh seeds
   — so the survival was fixed before the seed was drawn. The tree arm's `n=64`
   accuracy is `0.5376` against a chance level of `0.5`, and a 43× larger
   ensemble moves it to `0.5356`. Freeze the threshold and the statistic's
   support together, or an outcome has been frozen rather than a test.
3. **Power the construction does not currently have.** The binding arm's
   threshold in cell `(17,4,5)` is a coin flip across seeds — 128 in 9 of 20,
   256 in 11 — so a single draw of this construction cannot decide a gate whose
   boundary sits between them. Raising the query count per cell, or choosing a
   cell whose threshold is not on the boundary, is the change that makes the
   question decidable. Neither is a repair to an existing frozen protocol and
   both need a fresh identity.
4. **A decoder-held-fixed control in the terminal path.** The decomposition in
   Part 3 is the number the placement claim can carry. A successor should
   compute it inside its own receipt rather than leave it to an audit.

## What this does not establish

- **P11G's terminal is not overturned, and P11D's negative is not restored.**
  P11G's frozen gates on P11G's frozen seed print `SUPPORTED` and that is
  retained. The transplanted `[128, 256]` reading is a measurement of the arm
  axis, not a verdict from a rule that governs P11G.
- **No seed was swept to prefer an outcome.** The sweeps quoted here are the
  ones already in the record, and the rule against using a post-hoc sweep to
  prefer one frozen run over another applies to this document too.
- **The attainability finding stands and still blocks.** `attack_audit` exits
  `3` on `terminal_reach`: P11G's four scientific gates have one reachable
  terminal, so the attack had no reachable win. That is the
  `UNWINNABLE_ATTACK_PREDETERMINED_SURVIVAL` finding and this adjudication does
  not close it. It is a permanent property of the frozen protocol, and only a
  successor protocol can retire it.
- **The responsiveness result does not offset it.** Reopen the tree arm's bank
  to 5, 10 or 25 columns and the terminal moves in 3 of 3 cases, 2 distinct
  verdicts, `PASS`. That is the half that clears the arm of being broken. It is
  reported beside the attainability verdict and neither compensates the other.

## Reproduce

```
python -m orion.study.p11.attack_audit          # exits 3: attainability blocks
python -m orion.study.p11.attack_audit --json
python -m pytest tests/unit/study/p11
```

The instrument loads `run_p11g_deterministic_tree_decoder_v1.py` from this
directory, reproduces its committed scientific payload digest
`a2b0c33ce3c39e54ca1aa400a2b7d52d019fc4503f6cd5eb726c7b8bbe79a7cc` and every
curve value the receipt publishes before any claim above is transcribed, so a
failure is about P11G and not about a local fixture.

## Failure class

`UNWINNABLE_ATTACK_PREDETERMINED_SURVIVAL`, recorded under
`research/failures/2026-08-unwinnable-attack-predetermined-survival/`. The
general lesson: **a survived attack is evidence only for as long as the attack
could have won** — and when a programme registers several attacks and carries
one forward, the survival is a fact about the arm placed in the gate until the
record says which arm that was.
