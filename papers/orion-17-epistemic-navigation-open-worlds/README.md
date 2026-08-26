# P7 candidate — Epistemic Navigation in Open Worlds

**Current science:** `SCIENCE_CLOSED_V3`; PDF/typesetting refresh deferred.  
**Current science manuscript:** `manuscript/FINAL_V4.md`.  
**Historical:** `manuscript/FINAL_V3.md` preserved as the prior scientific version.  
**Historical V2 submission source/PDF:** preserved and not relabelled V3.

**Parent:** #332. Theory #336. Literature #337. Evaluation #338. Anti-overlap #343. Claim-expansion successor #534.

## Current research question

How can scientific task closure be preserved, refined or reopened across heterogeneous navigation and representation changes while reusing the strongest planning/refinement, migration, replanning and terminal-commitment mechanisms already available?

## Current V3 contribution

P7 now treats mature navigation mechanisms as **donor transforms to absorb**:

- sound planning abstraction/refinement;
- counterexample-guided refinement/reopen;
- bidirectional/round-trip representation migration;
- world-model/replanning transitions;
- explicit achieved-world versus terminal-commitment state;
- explicit semantic/evidentiary/procedural/institutional closure contracts.

P7 does not replace those mechanisms. It adds a bounded **closure-carrying transform**: donor-native validity is preserved, while task-global scientific closure is transported through an explicit obligation carrier. Failed closure transport becomes a targeted refinement/reopen problem, and heterogeneous transforms compose scientifically only when their intermediate closure contracts are exactly bound or explicitly bridged.

This is intentionally wider than the older statement that evidence transport is weaker than closure transport. The donor machinery is retained and improved with a compositional scientific closure interface.

## Formal result

Registered closure coordinates: obligation totality, obligation unambiguity, material-frontier resolution, objective/question semantic continuity, closure epoch.

Exact bounded support:
- 320 donor-transform/closure states;
- 0 donor-conservativity violations;
- 25 minimal one-coordinate closure separations;
- 31 donor-product nonclosure countermodels;
- 155 exact full closure-refinement successes;
- 1,055 proper-subset closure-refinement failures;
- 25 heterogeneous transform-pair composition successes under exact bridge binding;
- 25 bridge-mismatch composition countermodels;
- 0 ideal-product mismatches;
- canonical row SHA-256 `25f40385714adb15bca298a8cfd2b7fe2b28c96bfe462f6b60583be8f735b95f`.

Read with their multiplicity. Neither `carries` nor `compose` takes the donor family as an argument, so the donor loops repeat every count under them: **320** is the 64-point (native verdict, closure vector) space enumerated once per family, **25** is 5 separations counted five times, **155** and **1,055** are 31 and 211 counted five times, and the **25** composition successes and **25** bridge countermodels are one of each counted once per ordered donor pair. Only the **31** nonclosure countermodels are 31 distinct facts. The `donor_axis` block of `research/claim_expansion/p7/P7_X2_CLOSURE_CARRYING_RESULT_V1.json` carries the same table, computed rather than asserted.

A separate implementation independently reconstructs the result.

## Wider allowed claim

> P7 provides closure-carrying scientific navigation: mature planning/refinement, counterexample-guided reopening, representation migration, replanning and terminal-commitment mechanisms remain reusable donor transforms, while task-global closure is explicitly transported, selectively refined and compositionally carried through typed obligation bridges.

## Ownership / donor boundary

P2 retains generic open-world retrieval/search stopping. P7 does **not** claim graph search, planning, abstraction/refinement, CEGAR, round-trip migration, world-model revision, terminal commitment, or generic closure-gap terminology as new. An ideal donor product carrying the exact same scientific closure fields and bridge rules ties P7 extensionally.

## Real regime-transport evidence (three change classes)

Witness-aware closure transport holds at exact accuracy `1.0` on three qualitatively distinct non-synthetic change classes, each against the same two donor-complete baselines (value-only transport and always-reopen):

1. **Representation change** — public RO-Crate `1.2 -> 1.3` standard transition, 14 frozen cases: witness-aware `1.0` with 4 correct `CANNOT_CHECK`; value-only `0.428571...` with 8 false closures; always-reopen `0.285714...` with 6 unnecessary reopens.
2. **Responsibility/ontology change** — UCI Wine recognition data, three fine classes coarsened to `class0_vs_other`, 712 protected rows: witness-aware `1.0` with 238 correct `CANNOT_CHECK`; value-only `0.665730...` with 238 false closures; always-reopen `0.0` with 474 unnecessary reopens.
3. **Objective/obligation change** — Wisconsin Diagnostic Breast Cancer, the obligation moves from `accuracy >= 0.95` to `malignant-class recall >= 0.95` after predictions are frozen, 5 protected stratified folds in 2 evidence states (10 cells): witness-aware `1.0` with 5 correct `CANNOT_CHECK`; value-only `0.3` with 5 false closures; always-reopen `0.1` with 4 unnecessary reopens.

Bound receipts: `top_tier/P7_REAL_REGIME_TRANSPORT_RESULT_RECEIPT_V1.md` (classes 1–2) and `top_tier/P7_OBJECTIVE_CHANGE_TRANSPORT_RESULT_RECEIPT_V1.md` (class 3).

**What the `1.0` is, and what it is not.** It is exact conformance to a finite,
frozen contract on the cases listed above: 14 RO-Crate transitions, 712
protected Wine rows, 5 protected WDBC strata. Every one of those sets is
enumerated in advance, so a perfect score means the rule was applied correctly
to each member, not that the rule holds beyond them. It is **not** universal
regime transport. No population is sampled here and no interval is estimated,
so there is nothing from which to project to unseen change classes, and a
reader who takes `1.0` as evidence of general transport is reading a
conformance result as a generalisation. The multi-repository retention study in
`transitions/` bears on the same boundary from the other side: exact
containment made 0 unnecessary reopenings on real histories, which is a second
finite result and not a wider one.

The third class closes the objective/world/obligation gap: the goal structure itself changes while representations and responsibilities are held fixed, so value-level preservation cannot even express the new obligation — accuracy-only summaries are `CANNOT_CHECK` — and the change cuts both ways (one fold satisfies the old accuracy obligation but fails the new recall obligation, a value-only false closure; one fold fails the old and satisfies the new, where value-only needlessly reopens).

This licenses the bounded claim that witness/evidence-aware closure transport — not value preservation alone, not unconditional reopening — survives all three executed change classes. It does **not** license universal scientific-regime transport across arbitrary world-model, objective or agent changes.

## Current source map

- `manuscript/FINAL_V3.md` — current science manuscript overlay;
- `CLAIM_LEDGER_V3.md` — current claim authority;
- `submission/P7_X2_CLOSURE_CARRYING_SECTION.tex` — render-ready successor section;
- `research/claim_expansion/p7/P7_X2_DONOR_ENGULFMENT_V1.md` — donor extraction/improvement map;
- `research/claim_expansion/p7/P7_X2_SCIENCE_TERMINAL_V1.md` — science terminal;
- `top_tier/P7_REAL_REGIME_TRANSPORT_PROTOCOL_V1.md` + `top_tier/P7_REAL_REGIME_TRANSPORT_RESULT_RECEIPT_V1.md` — classes 1–2;
- `top_tier/P7_OBJECTIVE_CHANGE_PROTOCOL_V1.md` + `top_tier/P7_OBJECTIVE_CHANGE_TRANSPORT_RESULT_RECEIPT_V1.md` — class 3.

## Explicit nonclaims

No universal completeness, deployed-agent superiority, universal minimality of the registered closure coordinates, inference that missing closure proof automatically establishes ambiguity, inherent centralization/expressivity advantage, or universal scientific-regime transport across arbitrary world-model/objective/agent changes beyond the three executed families. PDF/package generation is deferred.
