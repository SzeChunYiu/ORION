# Cover letter — Quantum (quantum-journal.org)

**Manuscript:** *Support-Two Normal Forms for a Shared-Tag Pauli Compilation Grammar*
**Author:** Sze Chun Yiu, Department of Physics, Stockholm University, Stockholm, Sweden <sze-chun.yiu@fysik.su.se>
**Article type:** original research article
**Date prepared:** 2026-08-30

Dear Editors,

I submit *Support-Two Normal Forms for a Shared-Tag Pauli Compilation Grammar* for consideration as an original research article in Quantum.

## Contribution

The paper answers one structural question about a fixed compilation grammar: under
the declared six-target, three-block shared-tag Pauli grammar and its explicit
logical support-count objective, how much auxiliary-frame support does an exact
optimum actually need? Three results follow.

1. **A support-two normal form.** Every feasible solution can be transformed,
   without increasing cost under the declared objective, so that each auxiliary
   frame operator has support at most two.

2. **A sharp threshold at exactly two.** Support one is not uniformly sufficient:
   an exact two-qubit instance has unrestricted cost 5 against support-one cost 6.
   The uniform frame-support threshold for this grammar is therefore exactly two,
   and the obstruction is exhibited, not estimated.

3. **An exact algorithm induced by the threshold.** The sharp threshold yields a
   direct exact word-RAM algorithm for this fixed grammar, running in O(n^9) time
   and O(n^3) working memory.

Standalone finite checks corroborate the two local proof lemmas and recompute the
displayed sharpness instance.

## Adverse runtime comparison, stated up front

I would rather state this here than have a referee discover it. The manuscript
reports a prespecified runtime comparison whose outcome is adverse to the direct
implementation, and the abstract says so in these words:

> A prespecified runtime comparison is adverse: the direct support-two implementation timed out on all six full-subject cells under a 120-second limit, although both solvers agreed on every jointly completed cell.

The paper claims no performance benefit anywhere, and the adverse cell is reported
in the abstract rather than confined to a supplementary table. Agreement on every
jointly completed cell is reported as a correctness cross-check, not as evidence of
speed.

## Scope of the claim

The manuscript bounds itself explicitly, in these words:

> The result is therefore a grammar-specific normal form and algorithmic upper bound, not evidence of faster compilation, hardware benefit, fault-tolerant resource advantage, or general block-encoding optimality.

Nothing outside the frozen grammar and objective is claimed. In particular the
paper does not claim a full-circuit result, a hardware result, a fault-tolerant
resource result, or general block-encoding optimality, and a bounded literature
search that located no prior equivalent statement is reported as a search result
rather than as a novelty certificate.

## Fit and honest reservation

The contribution is a grammar-specific normal form, a sharp paired-instance
obstruction, and the exact upper bound they induce. An internal target-fit review
of Quantum's author guidance (observed 2026-08-28) recorded a reservation about
whether a result bounded to one fixed grammar and objective, with an adverse
implementation comparison and no external benchmark benefit, meets Quantum's
significance threshold. I submit it for the editors' judgement rather than
pre-empt that judgement, and I would welcome a transfer recommendation to a
specialist quantum-information or quantum-software venue if the editors judge the
scope too narrow for Quantum.

## Code and data

All code, exact counterexamples, and reproduction commands are in the public ORION
repository, and a review archive is available to anonymous referees on request.

## Declarations

Generative AI tools were used for drafting and editing assistance. The author is responsible for all scientific content.

Author contributions: Sze Chun Yiu is the sole author and performed all work reported.

Yours sincerely,

Sze Chun Yiu
Department of Physics, Stockholm University, Stockholm, Sweden
sze-chun.yiu@fysik.su.se
