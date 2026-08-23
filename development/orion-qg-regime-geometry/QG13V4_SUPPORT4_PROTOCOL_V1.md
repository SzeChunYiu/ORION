# QG-13 V4 / QG-9 — R6I all-n support<=4 spectator-safe theorem

Issue: SzeChunYiu/ORION#790
Frozen base: `afe7994bd5e362b2e8d40482f2dde9689e6ef708`
Branch: `shadow/orion-qg-qg13-v4-r6i-support4-theorem`
Status: FROZEN BEFORE PROTECTED MACHINE OUTCOME.

This is a confirmatory theorem packet. Exploratory post-V3 work used to formulate the theorem found 324 necessary anchored support-five slices per generator orientation and cumulative E2/E3 coverage 324/324. The protected run independently re-derives those domains and either verifies or refutes the proof.

Theorem target: every exact optimum of the frozen R6I rank-2 dependent-triple shared-2-bit-Tag grammar has a representative with all four independent generators of support <=4, for every n.

Proof obligations:
1. Bind the five-coordinate single-block syndrome to production R6I `_DELTA` for both block orientations.
2. Re-derive all A/B/AB single-column resource classes and globally safe E2/E3 classes from production semantics; V2/V3 result files are forbidden.
3. Parent QG-1: in lexicographic `(cost,total generator support)` minimum, the already-earned SOLO/PAIR theorem excludes support >5 and implies zero-sum-free N/C class subsets.
4. If selected generator g has support five, restrict to S=supp(Rg). Outside S, Rg=I, so S carries all anticommutation parity and both Tag-syndrome bits of Rg. The selected label is nonzero; the partner slice label need not be accepted because partner-only spectators may complete it.
5. Enumerate every five-column anchored slice separately for g=0 and g=1 with selected generator active everywhere, alpha XOR 1, selected two-bit label nonzero, and N0/N1/C subsets zero-sum-free. This is a necessary-condition superset of all globally irreducible support-five slices.
6. Every anchored slice must admit E2 or E3 with total five-bit syndrome delta zero, exact worst summed local delta <=0, and >=1 deleted selected-generator letter.
7. Spectator extension: zero five-bit block-syndrome delta preserves the full global R6I acceptance state when the other block/outside columns are unchanged. R6I objective is column-additive apart from unchanged Tag/global constants; there is no cross-column Restore factor. Hence the exact local nonincrease survives arbitrary outside columns.
8. The move lowers selected support 5-><=4 and total generator support with no cost increase, contradicting lexicographic minimality.

Positive terminal: `QG13V4_R6I_ALL_N_SUPPORT4_SUFFICIENCY_MACHINE_CHECKED`.
Honest alternatives: anchored-slice counterexample, spectator-extension gap, parent-binding failure, semantic-binding failure, CANNOT_CHECK.

Parent QG-1 receipt may be opened only after the anchored-slice local lemma has been digest-sealed in memory. No chemistry/protected subject/network. `new_theorem_authority` is bounded to this frozen R6I theorem only; `novelty_authority=false`; no physical quantum-advantage claim.
