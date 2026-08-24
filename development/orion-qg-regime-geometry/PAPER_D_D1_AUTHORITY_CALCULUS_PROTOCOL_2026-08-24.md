# Paper D / D1 — stratified certificate authority under exact falsification

Date: 2026-08-24

Base: `fa85599ad8ec057f98f935735ab02e30cbbb49ee`

Status: **FROZEN BEFORE THE D1 ANALYZER AND DUAL-HARNESS RUN; PARENT QG5/QG5B/PAPER-C OUTCOMES ALREADY KNOWN**

Primary owner: `PAPER_D`

Authority ceiling: formal stratified certificate calculus and the exact bound parent instantiations only.

## Scientific gap

The QG5 archive contains an exact counterexample to a static closed-form equality, a constructive upper bound that survives, an all-`n` support-family theorem that survives, and a separately frozen post-outcome repair. The current publication record describes these layers but does not give a formal, executable rule for the minimal retraction induced by a falsifier. Paper D requires that rule if it is to become more than a TARE-specific technical report.

This protocol is post-outcome formalization. It does not make QG5B prospective, does not change the original `9,545/9,546` denominator, and does not promote the repaired forecaster's benchmark to a prospective confirmation.

## Stratified certificate system

A registered certificate system is a finite acyclic hypergraph with:

- claim nodes in a fixed topological order;
- independently authorized seed claims;
- independently refuted claims;
- registered derivation rules `P -> c`, where every premise in the finite set `P` precedes the conclusion `c`;
- immutable provenance binding each seed, refutation, and rule to its evidence owner.

The authorized set after a falsifier is the least fixed point obtained from the non-refuted seeds by repeatedly applying a registered rule whose every premise is already authorized, never admitting a refuted conclusion.

## Minimal-retraction theorem

For every finite registered stratified certificate system:

1. the least fixed point exists and is unique;
2. rule-application order does not change it;
3. every admitted claim has a finite registered proof tree rooted in non-refuted seeds;
4. every registered proof-tree claim not rooted in a refuted seed is admitted;
5. adding refutations cannot add authority;
6. a claim whose complete registered ancestry is disjoint from the new refutations keeps its previous authority;
7. with alternative derivations, a claim survives exactly when at least one registered proof tree remains untainted.

Therefore the exact retraction is the pre-falsifier authorized set minus the post-falsifier authorized set. Descendant reachability alone is sufficient only for a single-derivation tree; an independent alternative proof may preserve a descendant.

The proof is elementary monotone induction on the topological order. It is donor mathematics. D1's residual scientific object is the exact typed instantiation to compiler-forecast authority, not a claim to have invented dependency tracking, fixed points, or belief revision.

## Machine corroboration

The source and independent lanes must separately:

1. exhaust every ordered conjunctive certificate DAG through five nodes;
2. exhaust every disjoint seed/refutation assignment;
3. compare iterative closure against a recursive proof-tree evaluator;
4. compare forward and reverse rule schedules;
5. verify monotonicity and ancestry noninterference;
6. verify fixed alternative-derivation rescue and failure cases.

Finite enumeration corroborates the proof; it is not the proof.

## QG5/QG5B instantiation

Bind the committed QG5 and QG5B receipts and protocol hashes. The registered claim nodes are:

- `FEASIBLE_UPPER_BOUND`, independently proved by constructive family feasibility;
- `SUPPORT_TWO_SUFFICIENCY`, independently proved all `n` in the frozen raw-support R6M scope;
- `ORIGINAL_CLOSED_FORM_EXACTNESS`, refuted by the exact `C_DP=10 < F=11` row;
- `ORIGINAL_REGIME_LABEL`, dependent on original closed-form exactness and refuted on the same row;
- `F2_EXACTNESS`, separately theorem-backed after executable-family binding;
- `REPAIRED_REGIME_LABEL`, dependent on F2 exactness and its registered binding.

Required exact result:

- original finite exact comparisons remain `9,545/9,546`, with one error;
- the original universal equality and original label retract;
- the feasible upper bound and support-two theorem survive;
- F2/repaired-label authority may be admitted only as separately supported, post-outcome repair evidence;
- QG5B's 9,547 panel entries include the refuting instance twice (standalone and inside the seeded panel) and must not replace the original unique-instance denominator.

## Cross-family noninterference check

Bind Paper C's all-`m>=5` decision theorem and its pair/r-wise value-information counterexamples. The decision claim is independently proved; the value/optimizer sufficiency claims are separately refuted. The calculus must preserve the decision theorem. These Paper C results remain owned by `PAPER_C`; D1 uses them only as a non-owner cross-family check of certificate noninterference. This is not a second forecasting family.

## Outcome branches

- Accept only if formal exhaustive checks, QG5/QG5B bindings, exact retraction, original denominator preservation, Paper C parent bindings, and every authority boundary pass.
- Reject on any digest mismatch, parent mismatch, relabeling of the QG5 counterexample, denominator change, prospective relabeling of QG5B, or transfer beyond the registered systems.

## Authority boundary

No claim is made about all static quantum-analysis frameworks, all proof systems, physical resource advantage, or novelty of generic fixed-point/retraction theory. D1 is not integrated with Qualtran, Qet, or another real resource framework. It has no second independent forecasting compiler family. Paper C theorem ownership stays with Paper C. QG5B remains post-outcome repair evidence. The harness grants no novelty or venue authority, and skipped CI is not evidence.
