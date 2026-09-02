# ORION-01 — Independent adversarial proof review V1

> **V4 status header — added 2026-09-02 (additive; the audit body below is unchanged).**
>
> This review targeted the **V2-era theory manuscripts** (`theory-A-MANUSCRIPT_V2.md`,
> `theory-B-MANUSCRIPT_V2.md`). The canonical ORION-01 surfaces are now
> `MANUSCRIPT_V4.md` and `CLAIM_LEDGER_V4.md`. Each finding's status in V4 was
> verified against those two files on 2026-09-02 as follows; nothing here promotes
> any claim (`scientific_authority_delta: NONE` unchanged).
>
> | Finding | Status in V4 | Verified basis in `MANUSCRIPT_V4.md` / `CLAIM_LEDGER_V4.md` |
> |---|---|---|
> | A-F1 | Closed in V4 | §3 and §5 fix the term: "A subsequence selects an arbitrary set of positions and need not be contiguous", used consistently thereafter. |
> | A-F2 | Closed in V4 | Theorem 2 proof is a global descent (Assumption 4, strict total-support decrease, termination) delivering the existential-optimum/universal-generator form; the post-theorem remark names the quantifier. |
> | A-F3 | Closed in V4 | Assumption 2 is stated whole-instance: deletion "preserves every constraint of the full instance, not only constraints local to R". |
> | A-F4 | Closed in V4 | §6.2 states the one-occurrence incidence ("this is the only Restore term containing the letter...; replaces exactly the l-th argument of this one term"); §7 adds the telescoping additivity step; §12 summarizes the verifier coverage. |
> | A-F5 | Closed in V4 | §4 fixes `A_R` as "the set of signatures realizable by any admissible local state of that instance, fixed before optimization"; §6 adds "not from a selected optimum". |
> | A-F6 | Closed in V4 | §6 derives the nonzero total from the global-symplectic-product-as-sum-of-local-products identity. |
> | A-F7 | Closed in V4 | The named `Z_n`/`{1}` counterexample appears immediately after Theorem 3, restricting the identity to the elementary binary setting. |
> | A-F8 | Closed in V4 | §3 defines `zsf` with the explicit `{0}` union: "The explicit zero handles degenerate alphabets." |
> | A-F9 | Closed in V4 | §7 names the hypothesis ("the identity and at least two distinct nonidentity letters") in the definition of `F_b`; ledger row O1-V4-C4 repeats it as a boundary. |
> | B-F1 | Closed in V4 | Definition 1 has no epistemic clause: "An upper theorem and a lower witness establish its exact value; they are not part of the definition." |
> | B-F2 | Closed in V4 | §5 argues the deleted set cannot be the whole word (nonzero total preserved) and states "A word is terminal precisely when it is zero-sum-free." |
> | B-F3 | Closed in V4 | §8 and §9 name the frozen unit objectives `C_M` and `C_I`; §9: "Every comparison below keeps the relevant objective and support statistic fixed." |
> | B-F4 | Closed 2026-09-02 | The V2 abstract phrase "arbitrarily loose" is absent from all V4 surfaces; the V4 abstract was further narrowed on 2026-09-02 to name the one-rule scope and the true-by-construction status of the budget's exactness. See `PUBLICATION_FREEZE_ADDENDUM_V2.md` for the recorded old/new wording. |
> | B-F5 | Closed in V4 | Proposition 10 composes the lower bound via the union of disjoint bases as a terminal zero-sum-free word; §10 labels the product "a definitional amplification... not an independent compiler phenomenon"; ledger O1-V4-C11 states the defining assumptions. |
> | B-F6 | Closed in V4 | §10.1 separates the `n -> infinity` (fixed `t`) and `t`-growth limits explicitly. |
> | B-F7 | Closed in V4 | §5 renames the quantity "certifiable support budget" with the collision-avoidance sentence; §11 disclaims propositional proof complexity. |
>
> CLEAN items C1-C10 were attacks, not defects, and need no closure.

> **Subject-version note (2026-09-02).** This document audits
> `theory-A/B-MANUSCRIPT_V2.md`, **not** the canonical `MANUSCRIPT_V4.md`
> (designated 2026-09-01). Do not report its findings as live without checking
> them against V4. Checked 2026-09-02: V4 closes A-F1 (subsequence
> explicitly non-contiguous), B-F1 (Definition 1 purely mathematical, the
> epistemic clause moved out), and the remaining A-F/B-F findings; the
> abstract phrase flagged by B-F4 no longer appears, and the V4 abstract
> carries the explicit boundary sentence ("The separation is relative to the
> declared proof language and does not imply a lower bound for richer
> systems, a production-compiler transfer, or a physical quantum
> advantage."). B-F4's underlying significance question -- whether a
> rank-only proof language is externally meaningful -- is not a textual
> defect and remains the venue-fit decision tracked in
> SzeChunYiu/ORION-paper#78.


**Schema:** `ORION.PaperClosure.IndependentProofReview.v1`
**Date:** 2026-08-28
**Subjects:** `theory-A-MANUSCRIPT_V2.md` (sha256 `596217cf…`), `theory-B-MANUSCRIPT_V2.md` (sha256 `66654d73…`)
**scientific_authority_delta:** `NONE`

## 0. What this review is, and is not

This is **one adversarial reading pass by a single reviewer**, performed from the manuscript
text alone. It did **not** import, execute, or lean on the generating proof/search logic
(`research/extensions/orion-qg/paper_a_a1_multitag_tare.py`,
`paper_b_b1_rank_only_proof_gap.py`, `papers/verify_five_theory_hardening_r2.py`).

It is **NOT**:

- an external specialist audit, and must not be recorded as satisfying that gate;
- a novelty certificate (see `NOVELTY_AUDIT_V1.md`);
- authority to promote any claim. The freeze receipt
  `papers/publication_closure/receipts/remaining11/ORION-01_SCIENCE_CONTENT_FREEZE_V1.json`
  records `external_peer_review_claimed: false`; this document does not change that.

Findings are graded **GAP** (a step is asserted, not justified — repair may exist),
**DEFECT** (statement is wrong or ill-formed as written), **NAMING**, or **CLEAN**
(attacked and survived). Every CLEAN item is listed so the reader can judge coverage.

---

## 1. Findings against Paper A

### A-F1 — DEFECT — "subword" vs "subsequence" is used inconsistently, and one reading makes §4 false

Paper A abstract defines `zsf(H;A)` over sequences "containing no nonempty zero-sum
**subsequence**". §2 then defines: "A word over `A` is zero-sum-free when none of its
nonempty **subwords** has sum zero." §3's proof and §4's corollary both say *subword*.
Paper B §3 also says "removes a nonempty proper **subword** summing to zero".

In formal-language usage *subword* frequently means **factor** (contiguous). Under the
contiguous reading, §4 is **false**:

> "Every word longer than `d` is linearly dependent, hence has a nonempty zero-XOR subword."

Linear dependence yields a zero-summing **subset** of positions, not a contiguous run.
Counterexample over `F_2^2` with `A={e1,e2}`: the word `e1,e2,e1` has length `3>2`, and its
contiguous factors sum to `e1`, `e2`, `e1`, `e1+e2`, `e2+e1`, `e1+e2+e1=e2` — none zero. It is
therefore *not* reducible in the contiguous language, contradicting the §4 bound.

The intended object is plainly the sub-multiset one (deletion sets `R` to identity on an
arbitrary coordinate set, which need not be contiguous). **Repair:** fix a single term,
state it once — "a *subsequence* is any sub-multiset of letters, not necessarily
contiguous" — and use it in the abstract, §2, §3, §4, and in Paper B §3. This is
terminological, not mathematical, but as written a referee can produce the counterexample
above against the corollary that the whole rank story rests on.

### A-F2 — GAP — Theorem 1's "Repeat for every generator" does not deliver the stated quantifier

Theorem 1 asserts: there exists an exact optimum such that **for every** constrained
generator `R`, `support(R) <= zsf(H_R;A_R)`. The proof reduces one generator, then says
"Repeat for every generator."

Sequential repetition does not by itself establish the ∃-optimum/∀-generator form, because
the proof never argues non-interference: if generators share coordinates, reducing `R`
changes the signature word of `R'`, and a single pass leaves no guarantee that earlier
generators still satisfy the bound.

**A repair exists and should be written in.** Deletion only sets coordinates to identity, so
no generator's support can *increase*. Total support across all generators is therefore a
strictly decreasing non-negative integer under any admissible deletion, so the process
terminates at a **global fixed point**; at that point no generator admits a deletion, hence
every generator's word is zero-sum-free, hence bounded by its `zsf`. The theorem is fine;
the write-up does not make the argument.

### A-F3 — GAP — Assumption 2 is stated per-generator but used globally

Assumption 2 reads: "setting `R` to identity on any nonempty zero-sum subword preserves all
semantic constraints **represented by the signatures**." That is scoped to `R`'s own
signatures. The proof (and A-F2's repair) needs the stronger statement that the deletion
preserves feasibility of the *whole instance*, including constraints attached to other
generators. As written, the hypothesis does not cover its use.

### A-F4 — GAP — Lemma 3 is a one-argument bound; Theorem 4 uses it per deleted coordinate, and the incidence is never specified

Lemma 3 bounds the increase of `F_b` when **one argument** is replaced. Theorem 4's cost
accounting says each deleted coordinate "can add at most `(b-1)t_R` in Restore cost by
Lemma 3". That composition is only valid if:

1. each coordinate participates in exactly **one** `b`-way Restore functional, and
2. deleting one coordinate changes exactly **one** argument of that functional.

Neither is stated. §5 says only "the local `b`-way Restore functional". If the `b`
arguments at a coordinate are the `b` block-copies of the frame letter at that coordinate,
then deleting the coordinate changes **all `b`** arguments at once and Lemma 3 does not
apply as invoked. If a coordinate meets several functionals, the penalty multiplies and the
cone `mu >= (b-1)t_R` is the wrong cone.

**This is the most consequential gap in Paper A**: the objective cone — the paper's headline
inequality — depends on an incidence structure the reader is never given. The fix is a
one-paragraph statement of the coordinate-to-Restore-functional incidence, plus an explicit
additivity step ("deleting a `k`-coordinate zero-sum subsequence refunds `>= k·mu` and adds
`<= k·(b-1)t_R`").

**Refinement added after inspecting the A1 parent artifact.**
`research/extensions/orion-qg/PAPER_A_A1_MULTITAG_TARE_RESULTS_2026-08-24.json` carries
`objective_ledger.all_checks = true` over checks that include, verbatim:

```
per_coordinate_restore_penalty_2tR   = true
frame_refund_at_least_mu             = true
cone_mu_ge_2tR                       = true
tag_cost_unchanged                   = true
outside_means_proof_inapplicable_only = true
```

So the per-coordinate incidence and the refund/penalty additivity that A-F4 identifies as
missing **are** discharged — as checked ledger items in an artifact the manuscript never
points to. This changes the character of the finding without withdrawing it: A-F4 is a
**manuscript completeness gap, not a suspected mathematical hole**. The assumption is sound
and was checked by the authors; a referee reading the manuscript alone still cannot verify the
cone, because neither the incidence nor the artifact is named in the text. The repair is
correspondingly cheaper than first assessed — state the incidence and cite the objective
ledger.

### A-F5 — GAP — `A_R` is defined solution-relatively, which risks circularity

§7: "Let `A_R` be the alphabet **actually realized** by the local partner/Tag signatures of
frame `R`." If `A_R` is read as the alphabet realized *by the optimum being bounded*, the
bound `support(R) <= zsf(H_R;A_R)` is circular — the bounding object is defined by the
object bounded, and it may shrink under the very deletions the proof performs. Theorem 1
requires an alphabet fixed **before** the argument. Disambiguate to an instance-level
object: the set of signatures realizable by any admissible configuration of the instance.

### A-F6 — GAP — §5's nonzero-total invariant is asserted, not derived

"The XOR of the first components is one, so total signature is nonzero." This is the
standard symplectic fact that global anticommutation of `R` and `R'` equals the sum of local
symplectic products, but the manuscript states it as a stipulation. Since Assumption 1 of
Theorem 1 is discharged entirely by this sentence, it needs its one line of justification.

### A-F7 — DEFECT (scope) — the rank corollary is binary-only, and the general case is unbounded in rank

§2 sets up a general finite abelian `H`; §4 proves `zsf <= rank` only for `F_2^d`. A reader
carrying that intuition into the general setting is badly wrong: for `H = Z_n` and
`A = {1}`, the word `1,1,…,1` of length `n-1` has all subsequence sums in `1..n-1`, none
zero mod `n`, so `zsf(Z_n;{1}) = n-1` while `rank(Z_n) = 1`. The gap is unbounded. The
manuscript never says the corollary is binary-specific *for a reason*; one sentence naming
this example would close it.

### A-F8 — GAP — `zsf` is undefined when no positive-length zero-sum-free word exists

§2 defines `zsf(H;A) = max{|W| : W zero-sum-free over A}` without admitting the empty word.
For `A = {}` or `A ⊆ {0}` the set is empty and the max is undefined. The degenerate case is
harmless (such instances are inadmissible under Assumption 1) but the definition should
either admit `|W|=0` or state the non-degeneracy hypothesis.

### A-F9 — GAP — Lemma 3's attainment needs at least two nonidentity letters

"the bound is attained" requires leaving the all-equal state by changing one letter to a
**different** nonidentity Pauli. If the local letter alphabet had a single nonidentity
symbol, attainment fails and the sharpness claim is false. Over Paulis `{I,X,Y,Z}` the
hypothesis holds, and the verifier is described as exhausting Pauli tuples — so the
hypothesis is implicit in "Pauli", but it is a hypothesis and should be named.

---

## 2. Findings against Paper B

### B-F1 — DEFECT — `kappa` is defined with an epistemic clause, which makes the headline separation ill-formed

§2.1 defines intrinsic support `kappa(F,C)` as the least `k` such that every instance has an
exact optimum of support at most `k`, **"with an independent witness showing `k-1` cannot
suffice."**

The final clause makes `kappa` a function of what has been *proved*, not of `(F,C)`. On that
reading `kappa` changes when somebody finds a new proof, and the paper's central claim
`beta_rank-only(R6I) = 5 > 1 = kappa_R6I` compares a mathematical quantity against an
epistemic one. The intended object is clearly

> `kappa(F,C) = min{ k : every instance has an exact optimum of support <= k }`,

with the witness being the *evidence that `kappa=1`*, not part of the definition. As
written, §2.3's soundness statement `kappa <= beta_P` is also not derivable, because the
right-hand side is mathematical and the left-hand side is not.

**Alongside A-F1 this is the sharpest finding in the review**: the separation is the paper's
entire contribution, and its principal quantity is not currently a well-formed mathematical
object.

### B-F2 — GAP — Theorem 1's converse depends on an unstated convention

"Conversely, a maximum zero-sum-free word has nonzero total and admits no deletion."

This is correct **only** if a word counts as a subsequence of itself — then zero-sum-freeness
directly forbids zero total. Under a *proper*-subsequence reading of "zero-sum-free", a
maximum zero-sum-free word could have total zero, it would not be in the language of
nonzero-total words, and the terminal witness would not exist. Since §3's legal step is
explicitly about *proper* subwords while the zero-sum-free definition must be *improper*,
the two conventions sit one line apart and are never distinguished.

Two further steps are correct but unstated: (i) the language is closed on nonzero-total words
because deleting a zero-sum subsequence preserves the total; (ii) under nonzero total,
"terminal" coincides with "zero-sum-free" precisely because the whole word is excluded as a
witness. Both belong in the proof.

### B-F3 — GAP — the `beta` vs `kappa` comparison requires one objective, and §5 never names it

The separation `beta_rank-only(R6I)=5 > 1=kappa_R6I` is meaningful only if both quantities
are taken over the **same** `(F,C)`. §5 names no objective. The ledger does — `theory-B-CLAIM_LEDGER_R2.md`
row B2-C4 carries boundary "Frozen R6I unit objective" — but a manuscript claim should not
depend on a ledger the referee may not read. §4 has the same omission for R6M. One clause in
each section fixes it.

### B-F4 — GAP — the exactness of `beta` is a statement about a one-rule proof system, and the abstract oversells it

Corollary 2's second conjunct is "**no other certificate rule can reduce it**". For the
"rank-only" system that is true by construction: the system has exactly one rule. So
`beta_rank-only(R6I)=5` is exact for a deliberately impoverished formalism, and the result's
scientific weight rests entirely on an unargued premise — that rank-only is the system
practitioners actually use. The manuscript never argues this.

Limitation 3 concedes the point honestly ("No lower bound proved for every local,
syndrome-preserving, or unrestricted proof system"), but the abstract's framing — a
certificate "arbitrarily loose as a description of the compiler it certifies" — reaches
past it. This is a claim/limitation mismatch, not a mathematical error, and it is the
likeliest referee objection.

### B-F5 — GAP — Theorem 3 is close to definitional, and its proof never invokes the clause it needs

Line 109 **defines** the product: "Let `F_R6I^t` be the registered product of `t` independent
components on disjoint coordinates **with additive support budget and no cross-component
move**." Theorem 3's proof (line 117, read verbatim) is, in full:

> **Proof.** Componentwise upper bounds add. A realized basis obstruction in each component
> gives the certificate lower bound five per component. Support zero is infeasible in each
> component and the support-one normalization acts independently, giving intrinsic lower and
> upper value one per component. ∎

Two observations, the second sharper than the first.

1. `beta(F^t)=5t` and `kappa(F^t)=t` follow from how the product is **defined**. The lower
   bound `beta >= 5t` is not a discovered obstruction; it is the additive-budget clause read
   back. Ledger row B2-C8 already forbids the over-reading ("The product is a second
   independent compiler mechanism | FORBIDDEN | It amplifies the same mechanism"), and the
   manuscript should carry that sentence too, since Contribution 5 and the abstract both lead
   with `Theta(n^(4t))`.

2. **The proof states per-component lower bounds and then asserts the global one without
   composing them.** "A realized basis obstruction in each component gives the certificate
   lower bound five per component" is a statement about each component in isolation; that
   per-component bounds sum to a global lower bound is exactly what the "no cross-component
   move" clause buys, and the proof never cites it. (Contrast the upper direction, where
   "componentwise upper bounds add" is at least stated as its own step.) The repair is one
   clause — the missing hypothesis is already in the definition on line 109, so nothing new
   must be proved.

### B-F6 — GAP — two limits are taken in an unexamined order

§6.1's `Theta(n^(4t))` is asymptotic in `n` for **fixed** `t` (correctly stated). §7 then says
the certificate is "unboundedly loose in additive budget under products", which is a `t → ∞`
statement. The two limits are never related, and no uniformity in `t` is claimed or proved.
Harmless if separated explicitly; misleading if read together.

### B-F7 — NAMING — "certificate complexity" collides with an established TCS object

`beta_P(F,C)` is named *certificate complexity*. In complexity theory `C(f)` — the certificate
complexity of a Boolean function, sitting in the standard `s(f)` / `bs(f)` / `deg(f)` web — is
a long-established and differently-defined object. A TCS referee will read the title and
abstract against that meaning. Recommend an explicit disambiguating sentence at first use, or
a distinct name (e.g. *certifiable support budget*). Not a novelty loss; a guaranteed
misread.

---

## 3. Attacked and CLEAN

Recorded so coverage can be judged. Each was a live attack that failed.

| # | Attack | Outcome |
|---|---|---|
| C1 | `0 in A` forces `zsf=0`, breaking Theorem 1 | **CLEAN.** A word containing letter `0` is not zero-sum-free, but words avoiding `0` still are, so `zsf(H;A)=zsf(H;A\{0})`. No effect. Worth a remark; not a defect. |
| C2 | Deletion could break Assumption 1 for the next iteration | **CLEAN.** Deleting a zero-sum subsequence preserves the total sum, so nonzero-total is invariant. Unstated in both papers, but true. |
| C3 | Theorem 1's removable subword might be the whole word | **CLEAN.** Excluded exactly by Assumption 1. The argument is correct as given. |
| C4 | Theorem 1 might not terminate | **CLEAN.** Support strictly decreases and is a non-negative integer. |
| C5 | Lemma 3 might exceed `b-1` | **CLEAN.** Full case check: from all-equal-nonidentity to a different nonidentity letter gives `1 -> b`, i.e. `+(b-1)`; to identity gives `1 -> b-1`, i.e. `+(b-2)`; from any not-all-equal state `F` is nonidentity Hamming weight and one replacement gives at most `+1` (entering the all-equal state *decreases* to 1). Max is `max(b-1,1) = b-1` for `b>=2`. Exact and attained. |
| C6 | `b=1` breaks Lemma 3 | **CLEAN.** At `b=1` the bound is `0` and the value is constant at `1` for a nonidentity letter, so it holds. The `b>=2` restriction is unexplained but harmless. |
| C7 | `s=0` degenerates Theorem 4 | **CLEAN.** With `s=0`, `v_q in F_2^1` with total `1`, so `zsf<=1` and `support(R)<=1=s+1`. Consistent. |
| C8 | `t=0` breaks Theorem 3 | **CLEAN.** Theorem 3 states "for every `t>=1`", so `t=0` is excluded explicitly. `t=1` reproduces §5's `5` vs `1`. |
| C9 | `zsf <= rank(H_R) <= s+1` chain in Theorem 4 | **CLEAN.** `H_R` is an elementary abelian 2-subgroup of `F_2^(s+1)`, so both inequalities hold. |
| C10 | Manuscript prose is degraded | **CLEAN — NOT A DEFECT.** Both files render as elided text through this session's output-compression hook. Verified against a base64 round-trip of `theory-B-MANUSCRIPT_V2.md` lines 9, 47, 51-53 that the **on-disk bytes are well-formed English**. No prose defect exists; do not record one. |

---

## 4. Summary

| Paper | DEFECT | GAP | NAMING | CLEAN |
|---|---|---|---|---|
| A | A-F1, A-F7 | A-F2, A-F3, A-F4, A-F5, A-F6, A-F8, A-F9 | — | C1-C7, C9, C10 |
| B | B-F1 | B-F2, B-F3, B-F4, B-F5, B-F6 | B-F7 | C8, C10 |

**No finding falsifies a headline theorem.** Every gap above has a stated repair, and the two
DEFECTs (A-F1 terminology, B-F1 definition of `kappa`) are corrigible by rewriting
definitions rather than by retracting results. A-F7 is a scope clarification, not an error.

The two that would most likely stop a referee, in order:

1. **B-F1** — `kappa` is not a well-formed mathematical object, and it is one half of the
   paper's central inequality.
2. **A-F4** — the coordinate-to-Restore-functional incidence is never specified, so the
   objective cone `mu >= (b-1)t_R` cannot be independently checked *from the manuscript*. Per
   the refinement recorded under A-F4, the assumption is discharged in the A1 parent's
   objective ledger, so this is a completeness gap rather than a suspected error — but the
   referee still cannot close it without leaving the paper.

Both are corrigible by writing, not by retraction. B-F1 is the only finding that touches the
well-formedness of a headline claim.

Applying any of these repairs requires editing hash-pinned frozen files; see
`SIBLING_DECOUPLING_AUDIT_V1.md` §4 for the freeze constraint and the pins involved.
