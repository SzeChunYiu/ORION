# Tie-equivalence quotient of small-domain screening states

**Protocol identity:** `ORION21.TIE_EQUIVALENCE_QUOTIENT.v1`
**Authority:** `DIAGNOSTIC_AND_STRUCTURAL_ONLY` · `scientific_authority_delta = NONE` ·
submission authority `false`
**Run queue item:** P1.10 (issue #1701)

This is a **third instrument**. It does not reopen, replay or re-adjudicate the V1 NR07 lane
(controlling terminal `CANNOT_CHECK_INSTRUMENT_DRIFT`) nor `ORION21.TIE_ROBUST_PHASE.v1`
(executed once, terminal `T3_TIE_AMBIGUOUS_VERDICT_CHANGING`). No magnitude measured here
transfers to the NR07 anchor replay or the reconstructed ladder sweep, and none was read from
either. The claim is purely structural.

## 1. Definitions recovered from the paper

Taken verbatim from `experiments/tie-robust-phase-v1/{THEORY.md, PROTOCOL.json,
run_tie_robust_phase.py}`. A screening state is `x = (c, r)` with integer correlations `c ∈ Z^p` and support size `r`.
The rule keeps the top `r` features by **absolute integer** correlation. Writing `boundary`
for the `r`-th largest `|c|`, `fixed = {i : |c_i| > boundary}`, `tied = {i : |c_i| = boundary}`
and `need = r − |fixed|`, the rule names not one support but the **admissible set**

    S(x) = { fixed ∪ T : T ⊆ tied, |T| = need }

`S(x)` is the **tie-equivalence class**, a singleton exactly when the top-`r` rank gap is
separable. The registered ascending-index key names the **canonical representative**
`min S(x)`; the protocol states it is used *only* to name a member and never replaces
reporting the admissible range. Two realised outcomes `(x, s)` and `(x, s′)` are
**tie-equivalent** iff `s, s′ ∈ S(x)`; an invariant `f(x, s)` is **representative-independent**
iff it is constant on every class, i.e. iff it descends through `(x, s) ↦ (x, min S(x))`.
Downstream, `sign(c_i) ∈ {−1, 0, +1}`, `score(b) = Σ_{i∈s} b_i · sign(c_i)`, prediction is
`score > 0` — faithful to `candidate_prediction()`, including the strict inequality and the
annihilation of zero-correlation features.

## 2. Method

`enumerate_tie_equivalence_quotient_v1.py` (stdlib only, `--smoke` for a fast reduced scope).
Exact integers throughout; no float aggregate enters any decision. Test bank = the **complete**
sign-row space `{−1,+1}^p`, all `2^p` rows, removing any arbitrary bank choice from the
prediction readout. The accuracy readout is referenced to labels given by the canonical
representative's own predictions — declared prospectively, used only to give accuracy a
canonical zero point. The choice-free result is `prediction_stream`; `accuracy_numerator`
inherits it. **Scope enumerated exhaustively:** `p ∈ {2,3,4,5}`; `r ∈ {1..p}`; `c` over the
complete cross product of `{−2,−1,0,1,2}`; all `2^p` sign rows.

## 3. Validation, run before any finding was read

| Check | Rule | Outcome |
|---|---|---|
| Subset-predicate cross-check | constructive `S(x)` equals `{s : \|s\|=r, min_{i∈s}\|c_i\| ≥ max_{j∉s}\|c_j\|}` | 0 mismatches / 18,550 |
| Binomial class size | `\|S(x)\| = C(\|tied\|, need)` | 0 mismatches / 18,550 |
| Ordered-Bell identity | distinct level structures over magnitude alphabet `{0..p−1}` = Fubini(p) | 1, 3, 13, 75, 541 — all match, `p = 1..5` |
| Separable-gap positive control | separable rank gap ⟹ `\|S\| = 1` | 0 violations |
| No-alarm negative control | strictly distinct `\|c\|` ⟹ singleton class by **both** routes | 256 states, passed |
| Detector positive control | the refutation detector **fires** on a known-binding class and stays silent on that class's constant invariants | passed |
| Count reconciliation | `sum(count) = states`, `sum(size × count) = realized outcomes` | asserted in-run |
| Benign-bank closed form | #row-subsets making a class benign `= 2^(2^p − \|D\|)` | 112 classes verified exhaustively |

The subset-predicate check is load-bearing: it obtains the admissible set by a characterisation
sharing no code with the constructive `fixed/tied/need` decomposition. The ordered-Bell check
validates the **level-structure dedupe** only — an enumeration identity, not the quotient; its
`|c|` vectors are brute-forced then deduped, so the count is a measurement, not a construction
artefact. An independent checker
(`independent_checker/check_tie_equivalence_quotient_v1.py`) obtains `S(x)` **only** by
subset-predicate filtering, imports nothing from the runner, re-derives all 13 invariants and
the **terminal** from its own recomputation, and gates the counts, every verdict, the
surviving/refuted **sets**, `exit_code` and the `certified` flag — the headline claim itself,
not merely the counts: `status: PASS`, 0 mismatches (`CHECKER_REPORT_V1.json`).

**These checks were shown able to fail**, the only thing that makes a passing run evidence.
Blinding the refutation detector fires the detector control (exit `4`, `T5_ENUMERATOR_DEFECT`).
Falsifying the terminal, the `certified` flag, a verdict, either invariant set, `exit_code`, or
a count each drive the checker to exit `5` (`MISMATCH`); reordering a set, and the unperturbed
input, both exit `0`. `--selftest` exercises the unreached `T4`/`T5` emit paths.

## 4. The quotient

Three distinct counts, easily conflated: **18,550 states** `x = (c, r)`; **36,824 realized
outcomes** `(x, s)` with `s ∈ S(x)`; **18,550 tie-equivalence classes**, one per state. The
quotient compresses **36,824 realized outcomes onto 18,550 classes**. Classes split into **9,620
singleton** (separable gap) and **8,930 non-singleton**, the latter into **7,760
decision-binding** and **1,170 decision-benign** (§7). The histogram
`{1: 9620, 2: 3421, 3: 3650, 4: 1066, 5: 130, 6: 533, 10: 130}` is keyed by `|S(x)|` and counts
**states**, so `sum(count) = 18,550` while `sum(size × count) = 36,824` — both asserted in the
runner and independently re-derived by the checker.

## 5. Invariants: survivors and refutations

`definitional` = follows from the construction of the equality class; `empirical` = decided by
the enumeration.

**SURVIVES, all `definitional`, 0 classes refuted (8):** `support_size`,
`abs_correlation_multiset`, `abs_correlation_sum`, `min_abs_correlation_in_support`,
`max_abs_correlation_in_support`, `boundary_level`, `admissible_class_size`,
`canonical_support`.

| REFUTED invariant | Kind | Classes refuted |
|---|---|---:|
| `support_identity` | empirical | 8,930 |
| `prediction_stream` | empirical | 7,760 |
| `accuracy_numerator` | empirical | 7,760 |
| `signed_correlation_sum` | empirical | 5,392 |
| `positive_sign_count` | empirical | 5,392 |

**Survivors exist**, so no blanket impossibility is claimed. They survive for a provable
reason, not an enumerated one: every member of `S(x)` shares `fixed` exactly and draws its
remaining `need` features from `tied`, all at `|c| = boundary`, so the selected `|c|`-multiset
is identical across the class and every function of it is class-constant — at any `p`, `r` and
alphabet. That is also exactly why they are useless for the decision: each factors through
class-constant data and so **cannot separate two members of a class**.

### Refuting witness

First witness in the enumeration order (`p`, then `r`, then `c` lexicographically over the
alphabet as written). That order does not minimise `|c|`; the `--smoke` run records the
structurally identical witness at `|c| = 1`.

    p = 2, r = 1, c = (−2, −2)
    boundary = 2,  fixed = {},  tied = {0,1},  need = 1
    S(x) = { (0), (1) },  canonical = (0)

    rows, in order:            (−1,−1) (−1,+1) (+1,−1) (+1,+1)
    prediction_stream for (0):    1       1       0       0
    prediction_stream for (1):    1       0       1       0

Two members of a **single** tie-equivalence class induce different classifiers. Referenced
to the canonical labelling, the admissible accuracy numerators are `4/4` and `2/4`, so any
threshold `θ` with `2/4 < θ ≤ 4/4` receives a different verdict on two members of one class.
This mirrors the paper's `min < τ ≤ max` straddle without importing its `τ`.

## 6. Scoped impossibility — certified

**Terminal `T1_IMPOSSIBILITY_CERTIFIED`, exit 0.**

> Within the enumerated bounds, the subfamily of invariants that are **both**
> representative-independent **and** decision-determining is **empty**.

A lifting argument makes this range over more than the thirteen invariants above. Fix the
readout: the complete set of quotient-measurable functions is the set of assignments of one
value per class, so enumerating classes covers every formula of every size in every language
over that readout. Then, if `f` is constant on every class and the decision `V` satisfies
`V = g(f)`, `V` is constant on every class too — so **one** class on which `V` is non-constant
refutes representative-independence for **every** decision-determining invariant. Section 5
exhibits such a class.

**The lift covers** invariant *size* and *language*. **It does not cover domain size:** the
certificate holds over `p ≤ 5`, `r ≤ p`, `c ∈ {−2,−1,0,1,2}^p`, complete `2^p` row space — and
over all invariants of all sizes within those bounds. Blurring the two would be an overreach.

## 7. Secondary structural finding — tie exposure is not decision ambiguity

Of 8,930 non-singleton classes, 1,170 are **benign**: every member induces the same classifier
over the complete row space, so the tie is real but decision-irrelevant. Within scope the split
is exact and total — **every** benign class has `boundary = 0` (1,170/1,170), **every** binding
class has `boundary > 0` (7,760/7,760, at levels 1 and 2). Forward is definitional: `sign(0)=0`
annihilates zero-correlation tied features. The converse (`boundary > 0` ⟹ binding) is
**empirical within scope only**, not proved in general.

Separately, a binding tie can be made benign by a test bank avoiding its disagreement rows: the
number of such banks is exactly `2^(2^p − |D|)` for disagreement-row set `D` (verified
exhaustively, 112 classes). That is how an instrument can exhibit tie exposure while its
realised readings never reveal set-valuedness — consistent with, and independent of, the
distinction `experiments/tie-robust-phase-v1/CLAIM_DISPOSITION.md` already draws. No magnitude
is transferred in either direction.

## 8. CANNOT_CHECK

Recorded explicitly; none is reported as a pass.

1. **NR07-scale behaviour is not established.** Nothing here speaks to bank widths at the
   registered ladder's scale. The certificate is an existence claim, so the small scope does
   not weaken it; the *survivor list* is universal but proved separately (§5), not by sweep.
2. **Level structures beyond three magnitude levels are not swept.** `{−2,−1,0,1,2}` admits
   `|c| ∈ {0,1,2}`, so classes from four or more distinct magnitude levels appear only in the
   ordered-Bell control, not in the invariant sweep.
3. **The converse of the benign characterisation is not proved**, only observed (§7).
4. **The accuracy readout requires a declared labelling.** The choice-free refutation is
   `prediction_stream`, which alone suffices for the certificate.

## 9. What this does not license

No law, width, mechanism, superiority, manuscript-freeze or submission authority. It does not
re-adjudicate the registered width-law study, establish or refute the width law, or license
any pooled-attack, compiled-defence or P11-gate statement. The V1 lane's controlling terminal
is unchanged; the quarantined post-outcome positive stays non-authoritative.

## 10. Reproduce

From the repo root, `D = papers/orion-21-state-as-computation/theory/tie-equivalence-quotient-v1`:

    python3 $D/enumerate_tie_equivalence_quotient_v1.py --selftest   # T4/T5 emit paths
    python3 $D/enumerate_tie_equivalence_quotient_v1.py --out $D/RESULTS_V1.json
    python3 $D/independent_checker/check_tie_equivalence_quotient_v1.py
    shasum -a 256 -c $D/SHA256SUMS

Full sweep ~0.5 s single-core, checker ~0.3 s; `--smoke` is a fast reduced scope.
`RESULTS_V1.json` is byte-deterministic — interpreter version and wall clock go to stderr, not
the digest — so `shasum -c` passes on a fresh run. Runner exit codes: `0` T1 certified, `10` T2
no refutation in scope, `11` T3 partial refutation with a decision invariant surviving, `3` T4
CANNOT_CHECK, `4` T5 enumerator defect. Checker: `0` PASS, `5` MISMATCH, `3` CANNOT_CHECK.
`T2`/`T3` are **not** impossibility certificates.
