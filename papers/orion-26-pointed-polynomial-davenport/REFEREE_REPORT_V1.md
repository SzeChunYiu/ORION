# Internal referee report — ORION-26 V1

Produced by applying the vendored `nature-reviewer` skill (`papers/skills/nature/nature-reviewer/SKILL.md`) as written protocol, the skill not being installed in this session. **This is a self-review and does not substitute for the independent mathematical review listed as a submission gate.** Its purpose is to find and fix defects before that review, not to claim it has happened.

## Review setup

- **Input scope:** full manuscript `MANUSCRIPT_V1.md`, claim ledger, and the evidence packet `research/experiments/davenport-c7-frontier/`.
- **Assessment boundary:** the reviewer has no access to the external literature (the host is network-blocked, confirmed by a 403 policy denial at the proxy for `arxiv.org:443`). **Originality against published work is therefore not assessable here** and is excluded from every judgement below.
- **Shared claim summary:** `D_2(C_p^3) = (9p−5)/2` for all primes `p ≥ 5`; `D_3(C_7^3) = 36`; an exact base-`p` digit criterion for the pointed system, from which a closed-form short-atom bound follows at every prime; a four-atom corridor for the open `D_4(C_5^3)` branch; a uniform three-special-length spectrum structure verified for `5 ≤ p ≤ 31`.
- **Visible evidence base:** six checkers, each with non-vacuity controls, dual decision procedures where a second exists, and real-object controls.
- **Missing materials affecting confidence:** the reference list is placeholders; no independent re-implementation of the `D_3` elimination step.

## Reviewer 1 — emphasis: technical soundness

The central new mathematics is Theorem G, and it is sound: Fredholm duality, Newton's forward-difference formula and Lucas are each applied correctly, and the delicate point — that `C(y,d)` is an integer-valued function and not a polynomial over `F_p` once `d ≥ p` — is handled properly, since the degree condition is imposed as `λ_e = 0` for `e > dmax` and transported to `μ_d = 0` through a bijective change of coefficients rather than through a notion of degree. The hypothesis `w ≥ p` is what makes the shifted window a single interval and is met throughout.

**Must fix.**

1. *(fixed)* §4.3 defined the lower-bound family with a literal `(corrections)` placeholder. A family that is not written down cannot support a lower bound. Now stated explicitly with its coordinate-sum proof.
2. *(fixed)* §4.2 presents three bullets as the proof of Theorem A. They are a summary. Now labelled as such, pointing to the record that carries the argument.
3. *(open, disclosed)* Theorem C step 5 is a finite computation with a single implementation. The end-to-end checker re-runs the authors' own enumeration, so it guards against regression and not against a systematic error. Now stated explicitly in §6.

**Assessment:** technically sound where checkable; one load-bearing computational step properly disclosed but not independently reproduced.

## Reviewer 2 — emphasis: significance and readership

`D_3(C_7^3) = 36` is a genuine new value on a line where values are settled one at a time, and obtaining it with Olson as the only external input is the right standard. Theorem G is the more transferable contribution: it converts a linear-algebra method into arithmetic, and the resulting generic bound — *any* long enough zero-sum over `C_p^3` whose atoms exceed `p` has an atom of at most about half the Davenport constant — is a statement about the group, not about the specific extremal problem, and will interest readers who do not care about `D_3` at all.

**Concerns.**

1. The `4 : 2 : 3` ratio in §7.3 is reported without explanation. Either explain it or move it to a remark; as written it reads as numerology.
2. Observation D is a verified range presented alongside theorems. The paper is careful about this, but a top-tier venue may still prefer it demoted to a remark plus a conjecture. **Recommendation:** keep it, because §7.3 now states the exact functional equation that would close it — that is a contribution in itself.
3. §5.3's methodological rule ("point when the window is two-sided") is the most quotable thing in the paper and is buried in a subsection.

## Reviewer 3 — emphasis: readability and claim discipline

Claim discipline is unusually good: the ledger grades every claim, the corrections are recorded rather than quietly patched, and the boundaries section says what is open without hedging the parts that are proved. The self-correction of the `23 ≤ |C| ≤ 29` range — caught by the authors' own generalization and propagated to the record, the manuscript and the cross-lane report — is the behaviour one wants and should be kept visible.

**Must fix.**

1. *(open, blocking)* References 3–5 are placeholders. No journal can receive this. This is not a writing defect but a consequence of the network-blocked host, and it must be cleared before submission.
2. *(fixed)* The abstract previously carried the short-atom bound both as a `p = 7` fact and as a general law, which read as two different claims.

**Assessment:** readable, honest about limits; blocked on references.

## Cross-review synthesis

**Consensus.** The mathematics that can be checked here is sound. Theorem G is the strongest and most transferable result and should be foregrounded. The manuscript's claim discipline is a strength, not padding.

**Weighting difference.** Reviewer 1 treats the `D_3` elimination step as the main risk; Reviewer 2 considers it secondary because Theorem G and the `D_2` result stand independently of it. Both agree the risk is disclosed rather than hidden.

**Blocking for submission** (unchanged by this review, and not clearable from this host):

1. prior-art pass against primary literature;
2. independent mathematical review;
3. independent re-implementation of the `D_3(C_7^3)` elimination step.

**Fixed in response to this review:** the `(corrections)` placeholder in §4.3; the proof-vs-summary labelling in §4.2; explicit disclosure of the computational weight in §6; abstract de-duplication.

**Not fixed, deliberately:** Observation D stays as a numbered verified-range result, because §7.3 states the exact obstacle; the `4 : 2 : 3` remark stays, flagged as unexplained.
