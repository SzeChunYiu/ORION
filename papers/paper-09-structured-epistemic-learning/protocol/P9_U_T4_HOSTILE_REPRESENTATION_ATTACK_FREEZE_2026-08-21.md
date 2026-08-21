# P9-U-T4 freeze: running the representation-length and format-prior attacks

- **Record id**: `P9_U_T4_HOSTILE_REPRESENTATION_ATTACK_FREEZE`
- **Date frozen**: 2026-08-21
- **Status at freeze time**: written before any new arm was defined in code, before any new
  dataset variant was generated, and before any number produced by this work existed. The only
  outcomes consulted while writing this file are ones already published in the repository — the
  four shipped D1 arm accuracies and the arm-response census in
  `research/failures/2026-08-unresponsive-comparator-prior-valued-margin/README.md`. Every
  threshold below is chosen from the split's resolution or from the meaning of the alternative
  being tested, never from a result of this study.
- **Gate served**: `P9-U-T4` — *"representation-length and format-prior attacks fail"*
  (`src/orion/programme/superiority_terminals.py:427-433`,
  `research/paper-programme-v1/P1_P10_SUPERIORITY_TERMINAL_LEDGER_V1.json`, issue #662).
- **Ledger blocker being addressed**: "The representation-length and format-prior attacks are
  named as hostile alternatives but have not been run."
- **Ledger unblock being executed**: "Run equal-token/length controls, semantic-orbit controls,
  symbol and order reminting, and same-information round-trip validation as gates rather than as
  robustness appendices."
- **Machine-readable twin**:
  `P9_U_T4_HOSTILE_REPRESENTATION_ATTACK_FREEZE_2026-08-21.json`. It carries the same parameter
  block plus its sha256. The runner recomputes that digest from its own constants and refuses to
  execute on a mismatch.
- **Runner**: `python -m orion.study.p9.hostile_representation_attacks --repo-root . --output <path>`

---

## 1. Where the attacks are named, and what they are attacking

The two attacks exist only as names. They are written down in exactly one place —
`papers/paper-09-structured-epistemic-learning/successor/P9_U_MANUSCRIPT.tex`:

> "Equal-token/length controls, order/symbol reminting, semantic-orbit controls and exact
> information checks are mandatory." (§ Frozen factorial design)
>
> "…tests, in order, whether the cause is information mismatch/leakage, **token/length confound**,
> preprocessing answer computation, architecture substitution, …" (§ AAGD)
>
> "H4: the effect survives information/length/reminting/orbit, architecture, preprocessing and
> stronger-model attacks." (§ Primary hypotheses)

A repository-wide grep over `*.py`, `*.md`, `*.tex` and `*.json` finds no runner, no arm, no
result and no fixture for any of them. They have been named and not run.

**What they are attacking.** The successor experiment those attacks were written for — the frozen
Qwen2.5 0.5B/1.5B/3B same-information run of issue #618 — **does not exist**; `P9-U-T1` is blocked
on it, no open-weight checkpoint is present in this repository, and this environment's proxy
refuses outbound CONNECT to model and metadata providers. The attacks cannot be run against a
result that has no outcome, and this freeze does not pretend otherwise.

The attacks *can* be run against the one representation contrast P9 actually publishes: **D1**,
protocol `P9.D1MethodTransferProtocol.v1.2`, shipped as
`research/extensions/p9-structured-neural/execution/D1_EXECUTION_RESULT_V1_2.json`
(`result_digest sha256:34003fb8…`, `dataset_manifest_digest sha256:27752984…`). The sentence under
attack is `manuscript/main.tex`'s reading of that result:

> "explicit relational comparison makes those fields more useful to the selected classical learner
> on this held-out-domain protocol."

## 2. Claim scope, fixed now

> **`BOUNDED_D1_ONLY`.** Whatever this study returns, it is a statement about the D1 v1.2
> classical-learner benchmark on its 128-case held-out-domain protected split, and about nothing
> else. It licenses **no** statement about any language model, any scale, any second family, or
> the successor experiment of issue #618.

**Anti-promotion commitment, fixed now.** `P9-U-T4` stays **BLOCKED** whatever this study returns.
This work can only *subtract*: if an attack succeeds, the D1 representation reading is narrowed or
withdrawn. If no attack succeeds, the only sentence earned is *"on D1, these two alternatives do
not account for the margin against the one comparator that answered"* — which is not the terminal,
because the terminal is about a result that does not yet exist. No result of this study may be
entered against `P9-U-T4` as a discharge.

## 3. What is already known, and what it does to the gate

`research/failures/2026-08-unresponsive-comparator-prior-valued-margin/` establishes, from the
shipped predictions, that on the 128-case protected split:

| arm | accuracy | distinct predictions | macro informedness |
|---|---|---|---|
| `TYPED_RELATIONAL` | 1.0 | 3 | 1.000000 |
| `UNTYPED_PAIR` | 0.90625 | 3 | 0.895833 |
| `TYPED_SERIALIZED_BAG` | 0.5 | **1** (`OBSTRUCTION` ×128) | **0.0** |
| `TRANSCRIPT_BAG` | 0.25 | **1** (`ALIGNED` ×128) | **0.0** |

so the two headline margins `+0.75` and `+0.50` are `1 − prior(ALIGNED)` and `1 − prior(OBSTRUCTION)`
and are `CANNOT_CHECK` under `orion.programme.comparator_response.measure_contrast_margin`.

**Consequence, fixed now:** *an attack cannot fail against a margin that was never measured.* A
hostile alternative is a competing explanation of an effect; where there is no measured effect
there is nothing for it to explain and nothing for it to be refuted by. So `P9-U-T4` is evaluated
**per contrast, three-valued**, and any contrast whose comparator is constant returns
`CANNOT_CHECK` for the attack as well. Reporting "the length attack failed" over
`typed − transcript` would be exactly the vacuous-guard substitution this programme has recorded
nine times.

The runner therefore begins by re-measuring all three contrasts with `measure_contrast_margin`
and records which ones are eligible to be attacked at all.

## 4. What each attack asserts

### 4.1 `H_LEN` — the representation-length attack

> **The arm ordering on D1 is produced by representation *length*: by how many fields and how many
> elements each view presents and by the fact that D1's corruptions change cardinality. Nothing
> about relational organisation is needed to produce it.**

This is a live alternative on D1 by construction, not a rhetorical one. Six of the eight
comparison coordinates are corrupted by `d1._mutated_value` in a way that changes a cardinality
or a presence: the four sequence coordinates gain an element, and the `UNRESOLVED` construction
sets `reconstruction_map` to `None`. `_typed_relational_features` and `_untyped_features` both
emit raw `left_length` / `right_length` features. If length alone decides the label, the paper's
"explicit relational comparison" sentence is unsupported.

### 4.2 `H_FMT` — the format-prior attack

> **The arm ordering on D1 is produced by a *format prior*: by how each view happens to be written
> down — whether its tokens carry held-out-domain-specific values, how its keys and paths are
> named, what symbol alphabet it uses — rather than by relational organisation of the same
> information. A change of format alone, adding no information and no comparison operator, moves
> the ordering.**

Also live by construction: `TYPED_SERIALIZED_BAG` emits `root.left.preconditions[]=<value>` tokens
whose value halves are workflow-domain strings that the train split never contains, and a
`DictVectorizer` silently drops every key it did not see when fitting.

## 5. Preconditions, checked before any arm runs

The run aborts and reports `T4_CONSTRUCTION_FAILED` — with no arm accuracy anywhere in the output
— if any of these fails.

| id | precondition | why |
|---|---|---|
| **PC-1 DATASET FIDELITY** | the locally regenerated D1 v1.2 dataset reproduces the shipped `dataset_manifest_digest` `sha256:2775298457b7bdee815b207733507cd27d55719df314ef6352bb601bd709c19c` | the attacks must be run on P9's dataset, not on a local lookalike |
| **PC-2 GOLD PRESERVATION** | every derived dataset variant (equal-length control, semantic orbit, order permutation) reproduces the gold label of every one of the 512 instances, position for position | a transform that moves a label is a different benchmark, not a control |
| **PC-3 CARDINALITY MATCH** | in the equal-length control, for every instance, every comparison coordinate and both sides: the coordinate's cardinality and presence are identical to the *unmutated* analogue's | otherwise it is not an equal-length control |
| **PC-4 ORBIT BIJECTIVITY** | the symbol remint is injective on the atom alphabet (no two distinct atoms map to one symbol) | a non-injective remint destroys information and would not be a semantic orbit |
| **PC-5 INDEX REVERSIBILITY** | for all 512 instances, the reversible-indexed serialization decodes back to the original serialized token list, byte for byte, using only the per-instance index table | the reformat must be shown to add and remove nothing |
| **PC-6 LABEL VARIETY** | the protected split's gold takes more than one value | `n/0` and "every case has the same answer" are `CANNOT_CHECK`, never a pass |

## 6. Arms

Every arm below is fitted with the **frozen D1 model grid and the frozen selection rule** —
`d1_experiment.model_specs()` (7 configs), train on TRAIN, select on DEV by
`(-dev_accuracy, complexity_rank, config_id)`, refit, predict the protected TEST split. Nothing
about model selection is changed; only the feature map changes. The four base arms are the frozen
ones, re-executed here so that every number in this artifact comes from one environment.

| arm id | new? | features |
|---|---|---|
| `TRANSCRIPT_BAG`, `UNTYPED_PAIR`, `TYPED_RELATIONAL`, `TYPED_SERIALIZED_BAG` | no | frozen, `d1_experiment.features` verbatim |
| `LENGTH_ONLY` | yes | for each of the 8 comparison coordinates and each side: `present` (bool); and `length` (int) when the coordinate is sequence-valued. **No** value identity, **no** cross-side comparison, **no** `unknown` flag. |
| `LENGTH_RELATIONAL` | yes | for each coordinate: `present_agree` (bool); and when both sides are sequence-valued, `same_length` (bool) and `length_diff` (int). **No** absolute lengths, **no** value identity, **no** `unknown` flag. |
| `SERIALIZED_INDEXED` | yes | `TYPED_SERIALIZED_BAG`'s token bag with every **string** leaf value replaced by `#i`, where `i` indexes that atom in the sorted list of distinct string atoms occurring anywhere in *that instance's* typed payload. Paths, `LEN=` tokens, `<NONE>` markers and integer leaves are untouched. Reversible: the per-instance table restores the original tokens (PC-5). |
| `SERIALIZED_PATHONLY` | yes | the same token bag with every string leaf value replaced by the single constant `<STR>`. Strictly **less** information than `TYPED_SERIALIZED_BAG`; a pure reformat with a domain-independent vocabulary. |

`LENGTH_ONLY` and `LENGTH_RELATIONAL` are `H_LEN` made into arms. `SERIALIZED_INDEXED` and
`SERIALIZED_PATHONLY` are `H_FMT` made into arms: neither adds an equality operator, neither adds
information, and `SERIALIZED_PATHONLY` removes information.

**Stated in advance as a limitation of `SERIALIZED_INDEXED`:** a hostile reading can say that
per-instance canonical indexing *is* a relational operation, because an atom shared by both sides
receives one index. That is why `SERIALIZED_PATHONLY` — which cannot be read that way, since it
erases all values — is reported beside it, and why the format-prior verdict is reported per arm
rather than pooled.

## 7. Derived dataset variants

### 7.1 `EQUAL_LENGTH` control (the equal-token/length control)

Regenerate D1 with one change: a sequence coordinate is corrupted by **replacing** its
last-in-canonical-order element with the mutation token instead of **appending** the token. Scalar
coordinates (`progress_measure`, `terminal_condition`, `reconstruction_map`) and `dependencies`
are already corrupted by replacement and edge reversal and are unchanged. Cardinality and presence
are therefore identical between corrupted and uncorrupted methods (PC-3), and the gold label is
unchanged (PC-2).

**Stated limitation, in advance.** The `UNRESOLVED` construction still sets `reconstruction_map`
to `None`, so *presence* still marks `UNRESOLVED`. The control therefore equalises length for the
`ALIGNED`-versus-`OBSTRUCTION` decision only. Accuracy on the 96-case `ALIGNED ∪ OBSTRUCTION`
sub-split is reported beside accuracy on the full 128, and the `H_LEN` verdict is read on the
full split with the sub-split reported for interpretation.

### 7.2 `SEMANTIC_ORBIT` (symbol remint)

Apply one global bijection to every atomic string value occurring in any of the eight comparison
coordinates of any method: `a → "v_" + sha256("p9-t4-orbit-2026-08-21|" + a)[:12]`, checked
injective (PC-4). Mechanic names, dependency structure, surface tokens and split membership are
untouched. The semantic content — which coordinates agree and which differ — is exactly preserved,
so every gold label is preserved (PC-2). Both train and test are transformed; every arm is refit
on the transformed train.

### 7.3 `ORDER_PERMUTATION` (order remint)

Reverse the element order of every sequence-valued comparison coordinate before rebuilding each
method.

**Declared in advance to be expected-vacuous, and to be reported as `CANNOT_CHECK` if it is.**
`orion.transfer.v2.p1_method_realization.build_method_realization` passes every sequence
coordinate through `_tuple(...) = tuple(sorted(set(...)))`, so a permutation is destroyed by the
constructor and cannot reach any arm. The runner *measures* the number of protected instances
whose feature dict actually changes rather than assuming it, and if that denominator is zero the
component is `CANNOT_CHECK / NEVER_EXERCISED`. It is **not** reported as "the order-remint attack
failed"; a control with no opportunity to fire has not held.

## 8. Attack components, success criteria and thresholds

`δ = 1/128 = 0.0078125` is the protected split's resolution: the finest accuracy difference 128
cases can express. Every tolerance below is stated in units of it.

| id | component | the attack **succeeds** iff | the attack **fails** iff | `CANNOT_CHECK` iff |
|---|---|---|---|---|
| **RL-1** | `LENGTH_ONLY` sufficiency | `acc(LENGTH_ONLY) ≥ acc(TYPED_RELATIONAL) − δ` | `acc(LENGTH_ONLY) < acc(TYPED_RELATIONAL) − δ` | either arm scored 0 cases |
| **RL-2** | `LENGTH_RELATIONAL` sufficiency | `acc(LENGTH_RELATIONAL) ≥ acc(TYPED_RELATIONAL) − δ` | `<` that | either arm scored 0 cases |
| **RL-3** | equal-length control | `acc_control(TYPED_RELATIONAL) ≤ trivial_floor(control split)` | `acc_control(TYPED_RELATIONAL) ≥ 0.95` | strictly between the two |
| **FP-1** | reformat closes the gap, once per reformatted arm `A` of base arm `B` | `gap(A) ≤ 0.5 × gap(B)` **and** `A` is not constant, where `gap(X) = acc(TYPED_RELATIONAL) − acc(X)` | `gap(A) > 0.5 × gap(B)` | `gap(B) < 4δ`, or `A` is constant |
| **FP-2** | semantic-orbit invariance, once per arm | `assess_guard` returns `FAIL` — the arm's prediction changed on at least one protected case whose features changed under a bijective renaming | `assess_guard` returns `PASS` | `assess_guard` returns `CANNOT_CHECK` (no protected instance's features changed: the arm had no opportunity) |
| **FP-3** | order remint, once per arm | as FP-2 | as FP-2 | as FP-2 — expected here, see §7.3 |
| **RT** | same-information round trip | — (this is a validity gate, not an attack) | 0 decode failures over a non-zero denominator ⇒ `PASS` | denominator 0 |

Rationale for the two non-resolution thresholds, fixed here:

- **`0.95` in RL-3** is a "did essentially nothing change" bar: `TYPED_RELATIONAL` scores `1.0` on
  the frozen split, and 0.95 of 128 is 6.4 cases, so anything at or above it is the same arm
  behaving the same way. The band between the trivial floor and 0.95 is deliberately declared
  `CANNOT_CHECK` rather than assigned to either side: a partial collapse is a partial explanation
  and this instrument is not able to apportion it.
- **`0.5` in FP-1** is the point at which a pure reformat accounts for more of the published gap
  than the relational operator it is attributed to. **`4δ`** (four cases) is the floor below which
  a halving is not distinguishable from tie-breaking noise.

`FP-2` and `FP-3` are built on `orion.programme.guard_exercise.GuardExercise` with
`opportunities` = protected instances whose feature dict changed under the transform,
`violations` = protected instances whose prediction changed, `max_violation_rate = 0.0`. The
denominator is therefore in the type, and a zero denominator cannot become a pass.

## 9. Verdict rule, fixed now

Per contrast in {`typed − transcript`, `typed − serialized`, `typed − untyped`}: run
`measure_contrast_margin`. A contrast whose verdict is not `PASS` is **not eligible** to be
attacked, is reported as `CANNOT_CHECK` with its reason, and its attack components are not
counted for or against the gate.

Overall, by `orion.programme.guard_exercise.worst_outcome` over every component that reached a
verdict:

| verdict string | outcome | when |
|---|---|---|
| `T4_CONSTRUCTION_FAILED` | `CANNOT_CHECK` | any precondition in §5 failed |
| `T4_NO_MEASURABLE_CONTRAST` | `CANNOT_CHECK` | no contrast returned `PASS` from `measure_contrast_margin` |
| `T4_ATTACK_SUCCEEDED` | `FAIL` | at least one component in §8 succeeded |
| `T4_ATTACKS_UNEXERCISED` | `CANNOT_CHECK` | no component succeeded, but at least one component is `CANNOT_CHECK` |
| `T4_ATTACKS_DID_NOT_SUCCEED_ON_D1` | `PASS` | every component ran with a non-zero denominator and none succeeded |

`T4_ATTACKS_DID_NOT_SUCCEED_ON_D1` is a `PASS` **of this instrument on D1**, not of `P9-U-T4`
(§2). The runner exits `0` on `PASS`, `3` on `FAIL`, `4` on `CANNOT_CHECK`.

## 10. Anti-tuning commitments

1. Every constant in §5–§9 — the orbit salt `p9-t4-orbit-2026-08-21`, the atom-index rule, the
   drop-last-in-canonical-order replacement rule, `δ = 1/128`, `0.95`, `0.5`, `4δ`,
   `max_violation_rate = 0.0`, the arm list and the verdict strings — is fixed by this document
   and hashed into the JSON twin. The runner recomputes the digest and aborts on mismatch.
2. Each dataset variant is generated once from the frozen D1 seed `p9-d1-method-transfer-v1`.
   No second seed, no re-draw, no alternative corruption rule.
3. If an attack succeeds, that is the finding and it is reported as the finding. No threshold is
   moved, no arm is dropped, and no variant of an attack that the claim survives is searched for.
4. No existing P9 result, receipt, protocol or evidence artifact is modified. Only new files are
   added.
