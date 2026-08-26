# P9 NR-05 freeze: representation hardening of the serialized arm against the frozen format-prior attack class

- **Record id**: `P9_NR05_REPRESENTATION_HARDENING_FREEZE`
- **Date frozen**: 2026-08-23
- **Revival lane**: NR-05 of `research/paper-programme-v1/NEGATIVE_REVIVAL_BACKLOG_V1.md`
  ("T4 hostile attack defeated narrow representation claim" → "representation hardening against the
  frozen attack class; successor claim re-test").
- **Status at freeze time**: written before the hardened arm was implemented, before any dataset
  variant of this study was generated, and before any number produced by this study existed. The
  outcomes consulted while writing this file are ones already published in the repository — the
  frozen T4 receipt and result
  (`evidence/P9_U_T3_T4_HOSTILE_ATTACK_RECEIPT_2026-08-21.md`,
  `evidence/P9_U_T4_HOSTILE_ATTACK_RESULT_2026-08-21.json`), the frozen T4 parameter block, the
  attack-potency audit (`evidence/audit/P9_ATTACK_POTENCY_2026-08-22.json`), and three
  **construction** measurements of the frozen dataset taken to establish that the hardening is
  definable at all, listed in §10. No arm accuracy, fitted model or prediction of this study
  existed when this was written.
- **Negative being revived**: `T4_ATTACK_SUCCEEDED` — the format-prior component `FP-2` landed on
  `TYPED_SERIALIZED_BAG` (32 of 128 protected answers moved under one bijective renaming of the
  value alphabet), so the manuscript sentence "explicit relational comparison makes those fields
  more useful" cannot rest on `\DOneTypedMinusSerialized`.
- **Machine-readable twin**: `P9_NR05_REPRESENTATION_HARDENING_FREEZE_2026-08-23.json`. It carries
  the same parameter block plus its sha256. The runner recomputes that digest from its own
  constants and refuses to execute on a mismatch.
- **Runner**: `python -m orion.study.p9.representation_hardening --repo-root . --output <path>`

---

## 1. Root cause, attributed to one stage

The frozen T4 run defeated the serialized arm through its **feature map** — the representation
stage, not the learner, not the dataset, not the protocol:

1. The dataset is the shipped one (T4 `PC-1` verified the manifest digest; re-verified in §10).
2. The learner grid and selection rule are frozen and shared by every arm, including the arms the
   attack did not move.
3. `_serialized_bag_features` emits **value-identity feature keys** —
   `token:root.left.preconditions[]=<atom>` — so the surface identity of atomic values enters the
   feature space. Two concrete channels then make the arm's fitted decision function a function of
   symbol identity rather than of information:
   - **train side**: `DictVectorizer` orders columns by the alphabetical sort of key strings, and
     the frozen grid's tree and random-forest learners — and the `(-dev_accuracy, …)` selection —
     break ties as a function of column order. A bijective renaming of the train atoms re-rolls
     that order and thereby re-rolls the fitted function.
   - **protected side**: `DictVectorizer` silently drops keys outside the fitted vocabulary, and
     the protected split is a held-out **domain**: it shares **zero** value atoms with train
     (measured, §10), so every value-bearing protected token is dropped and the protected answers
     ride on structural tokens plus the train-side fit. The renaming therefore moves protected
     answers without touching any protected in-vocabulary feature — which is exactly what the
   frozen run observed (32/128 moved, 0 in-vocabulary value keys at stake).

**The representation property the attack exploits**: the serialized feature map does not quotient
the value alphabet by its renaming group. The six arms whose features are functions of equality,
presence and cardinality are invariant under the orbit for exactly this reason; the serialized arm
is the one arm that names values, and it is the one arm that moved.

## 2. The lever, fixed now: quotient canonicalization

New arm **`SERIALIZED_CANONICAL`**: `TYPED_SERIALIZED_BAG`'s token bag with every string leaf
value replaced by the canonical symbol of its **occurrence-footprint class**:

- The corpus is traversed in canonical order — `train`, then `dev`, then `test`, instances in
  stored split order — and each instance's serialized token stream is read token by token.
- For every token whose value part is a string atom (not a `LEN=` marker, not `<NONE>`, not an
  integer leaf — the frozen `string_atoms` rule), one occurrence is recorded:
  `(split, index_within_split, path)`, where `path` is the token's path part.
- The **occurrence footprint** of an atom is the sorted multiset of its occurrences.
- The **canonical symbol** of a footprint is
  `"#" + sha256("p9-nr05-canonical-2026-08-23|" + ";".join(footprint_multiset_sorted))[:12]`.
- Atoms with identical footprints share one symbol (the quotient). `LEN=` tokens, `<NONE>`
  markers, integer leaves and path parts are untouched; `sequence_length` is unchanged.

**Mechanistic invariance argument, registered before the run.** Let `v` be any bijection on the
value alphabet — the frozen attack class. Renaming moves no occurrence: positions, splits and
paths are untouched, and the rebuild's `tuple(sorted(set(...)))` normalization permutes element
order within a coordinate but cannot change the multiset of (position, path) occurrences of any
atom. Hence `footprint(v(a)) = footprint(a)` for every atom `a`; hence `σ(v(a)) = σ(a)`; hence the
canonical token stream of the transformed corpus is **byte-identical** to that of the base corpus;
hence the fitted model is the same object and every protected prediction is identical. The
hardened feature map factors through the quotient of the value alphabet by its renaming group:
the attack class is not merely survived, it is **unrepresentable** in the hardened feature space.
This is a property of the construction, not of any measured outcome, and C-1 (§6) measures it
with a real denominator anyway.

**No relational operator is added.** Keys stay path-prefixed
(`token:root.left.invariants[]=#…`). An atom shared by both sides receives the same canonical
symbol under two *different* path prefixes, so the bag still cannot express cross-side equality —
the arm keeps its role as "same information, no relational bias". The T4 freeze's warning about
per-instance indexing being readable as a relational operation does not apply: the symbol is
assigned from corpus-wide occurrence structure, not from within-instance comparison, and the
path prefix keeps left and right distinct.

**Impossibility boundary, stated now.** No orbit-invariant canonical form can separate atoms with
identical occurrence footprints: any separating rule must read the value itself and is therefore
orbit-sensitive. On this corpus the quotient has 5 multi-member classes of 2–3 atoms each, all
train-domain vocabulary atoms that co-occur in the same coordinates of the same instances (§10).
The quotient merges bag keys that are **provably always co-present** — identical footprints imply
identical presence in every row — so no row's key-pattern changes (V2-PC-4 measures this). The
strict per-token round trip holds exactly for singleton classes and restores the exact class set
for multi-member classes (V2-PC-5 reports both counts). This is the disclosed information
boundary of the hardening, not a defect found after the run.

## 3. Claim scope, inherited and unchanged

> **`BOUNDED_D1_ONLY`** (verbatim from the T4 freeze): whatever this study returns is a statement
> about the D1 v1.2 classical-learner benchmark on its 128-case held-out-domain protected split
> and about nothing else.

> **Anti-promotion commitment, inherited**: `P9-U-T4` stays **BLOCKED** whatever this returns.
> This lane revives a *representation reading* on D1 — the successor claim of §7 — not the gate.
> The protected negative `LLM_STRUCTURE_SCALING_FRONTIER_NOT_SUPPORTED` (P9 Qwen scaling) is a
> different claim under a different receipt's authority boundary; this study does not touch,
> re-run or repair it, and uses no language model at all.

## 4. Registered bijection set — instances of the frozen attack class only

The frozen attack class of the defeated component is "one global bijection on the value alphabet"
(T4 freeze §7.2). Four instances of that class are registered:

| id | salt | role |
|---|---|---|
| `ORBIT_FROZEN` | `p9-t4-orbit-2026-08-21` (the frozen orbit, verbatim `build_orbit_map`) | anchor; ties this study to the frozen result |
| `BIJECTION_1` | `p9-nr05-bijection-2026-08-23\|1` | fresh draw, same construction |
| `BIJECTION_2` | `p9-nr05-bijection-2026-08-23\|2` | fresh draw, same construction |
| `BIJECTION_3` | `p9-nr05-bijection-2026-08-23\|3` | fresh draw, same construction |

Construction identical to the frozen orbit: `v_` prefix, sha256, width 12, applied to the frozen
`REMINTED_COORDINATES`, injectivity checked. No new attack type is introduced; the fresh draws
exist so that the invariance measurement of C-1 has a denominator that does not hinge on one
salt. No equal-length control and no order permutation are re-run here: the frozen run already
returned them (`H_LEN` did not succeed; order remint is annihilated by the constructor, per the
attack-potency audit) and this lane's lever does not touch them.

## 5. Arms

| arm id | new? | features |
|---|---|---|
| `TYPED_RELATIONAL` | no | frozen, verbatim — the claim's treated arm |
| `TYPED_SERIALIZED_BAG` | no | frozen, verbatim — the defeated arm (before) |
| `SERIALIZED_INDEXED` | no | frozen, verbatim — positive control for the C-1 guard |
| `SERIALIZED_CANONICAL` | **yes** | §2 — the hardened arm (after) |

Every arm is fitted with the frozen D1 model grid and frozen selection rule
(`d1_experiment.model_specs()`, `(-dev_accuracy, complexity_rank, config_id)`), train on TRAIN,
refit, predict the protected TEST split. Nothing about model selection changes; only the feature
map of the new arm differs, exactly as the T4 arms differed from theirs.

## 6. Components, success criteria and thresholds

Thresholds are inherited verbatim from the frozen T4 block: `δ = 1/128 = 0.0078125`,
`REFORMAT_GAP_FRACTION = 0.5`, `REFORMAT_MIN_BASE_GAP = 4δ`, `max_violation_rate = 0.0`.

### Preconditions (abort → `T4V2_CONSTRUCTION_FAILED`, no arm accuracy in the output)

| id | precondition |
|---|---|
| **V2-PC-1** | the regenerated dataset reproduces the shipped manifest digest (frozen `PC-1`) |
| **V2-PC-2** | every bijection variant reproduces every gold label, position for position (512/512) |
| **V2-PC-3** | every registered bijection is injective on the atom alphabet |
| **V2-PC-4** | for every multi-member footprint class, all members occur in exactly the same set of (instance, path) bag rows — the measured form of the merge-losslessness argument |
| **V2-PC-5** | round trip in quotient form: singleton-class tokens restore byte-exactly via the per-corpus class table; class tokens restore to the exact class; counts reported over all 512 instances |
| **V2-PC-6** | the protected split's gold takes more than one value (frozen `PC-6`) |

### Measured components

**C-1 QUOTIENT INVARIANCE — the guard, with a denominator that cannot be vacuous.** For each
registered bijection `b`: opportunities = corpus instances (512) whose **raw** serialized stream
changed under `b` — the attack reached the representation; violations = instances whose
**canonicalized** stream changed. `GuardExercise` with `max_violation_rate = 0.0`, pooled over
the four bijections. PASS iff zero violations over a non-zero pooled denominator. The refit
consequence (train features identical → same selected config → identical protected predictions →
identical accuracy) is recorded alongside. The denominator is deliberately taken **before**
canonicalization: FP-2's post-feature denominator reads structural invariance as `CANNOT_CHECK`,
and the point of this study is to measure that the canonicalization stage annihilates an attack
that demonstrably reached it. `SERIALIZED_INDEXED` is the existence proof that this guard
discriminates: its per-instance sorted-order indexing is a canonicalization design, and it does
not annihilate the orbit.

**C-2 POSITIVE CONTROLS — the instrument must fire on known-movable arms.**
(i) The frozen `FP-2` component, re-run verbatim on `TYPED_SERIALIZED_BAG` under `ORBIT_FROZEN`,
must reproduce `FAIL` (violations > 0; the frozen reference count is 32/128 and is recorded).
(ii) The C-1 guard applied to `SERIALIZED_INDEXED` under `ORBIT_FROZEN` must flag it (canonical
features changed on ≥ 1 instance; the frozen run measured 128/128 protected). If either control
does not fire, the instrument is invalid and the run certifies nothing
(`T4V2_GUARD_INVALID`).

**C-3 MARGIN SURVIVAL — the successor claim.** On `BASE`, with all accuracies measured in this
environment as in the frozen run: `g = acc(TYPED_RELATIONAL) − acc(TYPED_SERIALIZED_BAG)`,
`gc = acc(TYPED_RELATIONAL) − acc(SERIALIZED_CANONICAL)`. The successor claim is **supported**
iff the canonical arm is non-constant, `measure_contrast_margin` on (typed, canonical) returns
`PASS`, `g ≥ REFORMAT_MIN_BASE_GAP`, and `gc > REFORMAT_GAP_FRACTION × g`. It is **not supported**
(FAIL) iff the arm is non-constant, the contrast is measurable, and `gc ≤ 0.5 × g` — the
canonical reformat closes the gap and the serialized margin was format after all. It is
`CANNOT_CHECK` if the arm is constant or the contrast is unmeasurable. The canonical arm's
accuracy is unknown at freeze time and no alternative canonicalization will be shopped if C-3
fails.

**C-4 FROZEN FP-2 READING ON THE HARDENED ARM.** The frozen `FP-2` component, verbatim, on
`SERIALIZED_CANONICAL` under `ORBIT_FROZEN`. Expected: `CANNOT_CHECK / NEVER_EXERCISED` — the
arm is invariant by construction, and under the frozen semantics that is not a pass. Reported as
exactly that, never as a held guard; the measured invariance lives in C-1. Both readings are
recorded so this study cannot be read as ducking the frozen semantics.

## 7. Verdict rule, fixed now

By `worst_outcome` over every component that reached a verdict:

| verdict string | outcome | when |
|---|---|---|
| `T4V2_CONSTRUCTION_FAILED` | `CANNOT_CHECK` | any precondition in §6 failed |
| `T4V2_GUARD_INVALID` | `CANNOT_CHECK` | a C-2 positive control did not fire |
| `T4V2_INVARIANCE_BROKEN` | `FAIL` | C-1 violations > 0 |
| `T4V2_MARGIN_NOT_SUPPORTED` | `FAIL` | C-3 not supported |
| `T4V2_MARGIN_UNMEASURABLE` | `CANNOT_CHECK` | C-3 unmeasurable (constant arm or unmeasurable contrast) |
| `T4V2_REPRESENTATION_HARDENED_ON_D1` | `PASS` | C-1 clean over a non-zero denominator, C-2 controls fire, C-3 supported |

`T4V2_REPRESENTATION_HARDENED_ON_D1` is a pass **of this instrument on D1**. It licenses only the
successor claim of §8 and nothing about `P9-U-T4`, any language model, any scale, or the
successor experiment of issue #618. Exit `0` on PASS, `3` on FAIL, `4` on CANNOT_CHECK.

## 8. The successor claim, fixed now

> If the verdict is `T4V2_REPRESENTATION_HARDENED_ON_D1`: on D1 v1.2, a serialized representation
> whose value alphabet is quotiented by its renaming group — same information up to the disclosed
> co-presence merge, no relational operator added, frozen learner and selection untouched — is
> unmoved by the frozen format-prior attack class (four bijections, 2,048 instance-level
> opportunities), and the typed-minus-serialized margin measured against it survives the frozen
> reformat threshold. The D1 reading "explicit relational comparison makes those fields more
> useful" is thereby restored **on a format-invariant basis**, superseding the frozen receipt's
> narrowing in exactly the scope it was narrowed.

If the verdict is `T4V2_MARGIN_NOT_SUPPORTED`, the honest successor finding is the opposite and
is reported as such: the serialized margin does not survive canonicalization and was format.

## 9. Anti-tuning commitments

1. Every constant — the canonical salt `p9-nr05-canonical-2026-08-23`, the three bijection salts,
   the footprint encoding, the inherited thresholds, the arm list, the verdict strings — is fixed
   by this document and hashed into the JSON twin. The runner recomputes the digest and aborts on
   mismatch.
2. Each dataset variant is generated once from the frozen D1 seed `p9-d1-method-transfer-v1`. No
   second seed, no re-draw, no alternative corruption rule.
3. The canonicalization design was chosen from the invariance argument of §2 alone, before any
   arm ran. If C-3 fails, that is the finding; no alternative design is tried in this study.
4. No existing P9 result, receipt, protocol or evidence artifact is modified. Only new files are
   added. The frozen T4 instrument is imported, not edited.
5. Foreign work this study builds on, cited: the frozen T4 freeze/receipt/result (this
   repository, 2026-08-21) and the attack-potency audit of 2026-08-22 (codex lane, merged via
   #831), which established the rebuild's sorted-set normalization and the per-variant reach
   census this freeze's root-cause section uses.

## 10. Pre-run construction measurements, disclosed

Taken before this freeze was finalized, to establish definability; none is an arm outcome:

- the regenerated dataset reproduces the shipped `dataset_manifest_digest`
  `sha256:27752984…` (frozen `PC-1`);
- the serialized streams of the frozen corpus contain **229** distinct string atoms falling into
  **224** occurrence-footprint classes: **5 classes have 2–3 members**, all train-domain
  vocabulary atoms co-occurring in the same coordinates of the same instances; every protected-
  split atom is a singleton class;
- **0** value atoms are shared between the train and protected splits (the held-out-domain
  boundary), which is the measured form of the protected-side channel in §1.
