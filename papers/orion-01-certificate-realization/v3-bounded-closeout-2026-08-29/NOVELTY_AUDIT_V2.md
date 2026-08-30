# ORION-01 primary-source novelty subtraction V2

**Audit date:** 2026-08-29  
**Scope:** bounded author-side claim subtraction for Paper A V3 and Paper B V3  
**Authority:** targeted primary-source audit; not an external novelty opinion, systematic review, or legal patent search

## Method

The audit started from the strongest apparent parent works rather than from title similarity. For each manuscript statement, it asked:

1. Is the mathematical object already standard under another name?
2. Does a donor compiler already state the same semantic transfer?
3. Is the statement an elementary consequence or definitional amplification?
4. What compiler-specific conjunction, if any, remains after subtraction?

Primary sources were inspected at the paper or publisher level. Secondary summaries were not used as authority.

## Primary sources inspected

1. N. Schillo, A. Sturm, and R. Quay, **Towards Ancilla-Free Quantum Block Encoding: A Divide-and-Conquer Method**, arXiv:2601.05740, current arXiv version inspected 2026-08-29. The donor discusses TARE, non-unique Tag solutions, and minimum-weight/joint optimization directions.
2. A. Plagne and S. Tringali, **The Davenport Constant of a Box**, *Acta Arithmetica* 171 (2015), DOI `10.4064/aa171-3-1`. This source defines a Davenport constant for a subset/box: the least sequence length over the subset forcing a nonempty zero-sum subsequence.
3. M. Freeze and W. A. Schmid, **Remarks on a Generalization of the Davenport Constant**, arXiv:0905.4248. This is higher-order Davenport-constant context, not the nearest source for ORION's restricted alphabet object.
4. I. Aliev, J. A. De Loera, F. Eisenbrand, T. Oertel, and R. Weismantel, **The Support of Integer Optimal Solutions**, *SIAM Journal on Optimization* 28 (2018), DOI `10.1137/17M1162792`. This establishes broad sparse-support context for integer optimization.

The release manifest must pin exact versions/identifiers. A later external review may add stronger parents and further narrow the claims.

## Claim-by-claim subtraction

| Candidate statement | Primary-source subtraction | V3 disposition |
|---|---|---|
| `zsf(H;A)` as a restricted alphabet zero-sum invariant | Subset/restricted Davenport-type constants are established prior art; ORION's notation is a maximum-length reformulation. | `PRIOR_ART__USE_ONLY`; no novelty claim. |
| `zsf(F_2^d;A)<=d` | Elementary binary linear dependence and classical zero-sum theory. | `TEXTBOOK__USE_ONLY`. |
| Equality when `A` contains a basis | Immediate basis obstruction plus the binary upper bound. | `ELEMENTARY_COROLLARY__USE_ONLY`. |
| A generic “delete zero-sum subsequences until bounded” argument | Abstractly elementary once global feasibility and objective dominance are assumed. | Not claimed alone; V3 states it as the transfer skeleton. |
| Exact one-argument Restore increase `b-1` | A finite case analysis for the declared functional. | Supporting lemma, not headline mathematical novelty. |
| MultiTag semantic signature plus whole-instance deletion soundness plus exact Restore cone | Not found as a theorem in the inspected TARE donor; the donor motivates weight optimization but does not state ORION's restricted-zero-sum support certificate with this Restore accounting. | `RESIDUAL_CANDIDATE`, bounded to the explicit grammar and assumptions. |
| R6M exact support two under the frozen objective | An ORION exact upper/lower result, not supplied by the inspected donor papers. | `RESIDUAL_CANDIDATE`, provided parent artifacts remain hash-bound and independently checked. |
| “Rank bound equals intrinsic support” in general | False as a general framing; a proof-system ceiling need not be intrinsic. | Removed. |
| R6I intrinsic one versus rank-only budget five | The inspected donors do not state this compiler/proof-language separation. | `RESIDUAL_CANDIDATE`, relative only to the named objective, family, and rank-only proof system. |
| Product amplification over independent copies | Follows definitionally from additive objective/support and no cross-component move/rule. | `DERIVED__NOT_INDEPENDENT_CONTRIBUTION`. |
| General sparse optimal support | Strong broad prior context exists in integer optimization. | No generic sparsity novelty claim. |
| Physical resource or quantum advantage from structural support | Not implied by the bounded support statements. | Prohibited absent separate resource evidence. |
| Production move completeness | Round-3 ended `CANNOT_CHECK_MOVE_COMPLETENESS`; no inspected source repairs that empirical terminal. | Excluded from both manuscripts. |

## TARE-specific boundary

The current TARE donor recognizes that Tag solutions can be non-unique and points toward minimum-weight or joint optimization. That is relevant parent context and must be credited. The inspected paper does not, however, supply the complete ORION conjunction of:

- the fixed MultiTag signature alphabet used here;
- the global zero-total deletion semantics for all named constraints;
- the exact coordinate/Restore incidence and `b-1` accounting;
- the R6M exact support-two lower/upper control;
- the R6I intrinsic-versus-rank-only separation.

This is a bounded negative finding from the inspected source, not proof that no other source contains a closer result.

## Corrected historical attribution

The earlier novelty ledger treated Freeze–Schmid as the nearest subset-alphabet donor. That is inaccurate. Their paper concerns a higher-order generalization of Davenport constants. Plagne–Tringali is a materially closer primary source for a Davenport constant attached to a subset/box. V3 therefore cites the latter for the restricted-alphabet object and retains Freeze–Schmid only as broader context.

## Residual claim set

After subtraction, the defensible candidate contribution is:

1. a compiler-specific semantic transfer from a fixed restricted zero-sum language to the explicit MultiTag grammar;
2. exact Restore incidence and objective-cone accounting;
3. a hash-bound R6M equality control under the frozen objective;
4. a hash-bound R6I strict separation between intrinsic support and a named rank-only deletion language;
5. an explicit authority boundary preventing certificate budgets, capped enumeration, or structural support from being promoted to stronger claims.

Every item remains conditional on the stated grammar, objective, evidence bindings, and independent checking. The standard invariant, binary rank result, generic descent, and product arithmetic are not residual contributions.

## Prohibited claim language

The V3 package must not say or imply:

- “we introduce a new Davenport constant”;
- “binary rank is the compiler's intrinsic minimum” without a separate lower witness;
- “TARE lacks support optimization”;
- “the capped Round-3 execution proved move completeness”;
- “structural support proves a physical quantum advantage”;
- “author-side search is an external novelty certificate.”

## Audit terminal

`NOVELTY_NARROWED__RESIDUAL_CANDIDATE_ONLY`

`BOUNDED_PAPER_RETAINED`
