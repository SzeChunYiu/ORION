# ORION-20 native-Lean protected runtime handoff V1

**Source programme:** PR #618 / issue #618 lane  
**Source run:** GitHub Actions `32346652258`  
**Disposition:** `CANNOT_CHECK_NATIVE_STATE_COVERAGE`  
**Purpose:** preserve the stronger real verifier-backed native-state attempt as authority-bearing negative/coverage evidence for the top-tier ORION-20 programme.

## What executed

The frozen native-Lean pipeline checked out the pinned Lean/mathlib source, traced the selected theorem/file population, generated native tactic/state/premise evidence, and reached the fit/analyze stage.

The run reported:

- selected/traced file count: `457`;
- total candidate transitions: `11,842`;
- transitions satisfying the frozen native-state eligibility contract: `0`;
- premise availability fraction: approximately `0.2107`;
- tactic availability fraction: approximately `0.0989`;
- state availability fraction: approximately `0.0818`;
- sampled discrepancy checks: zero material discrepancies;
- generator terminal: `CANNOT_CHECK_NO_ELIGIBLE_TRANSITIONS`;
- analysis terminal: `CANNOT_CHECK_NATIVE_STATE_COVERAGE`.

The cross-revision analysis therefore also lacked a valid complete winner/transition set for the intended comparative result.

## Scientific interpretation

This is **not** a timeout, a model failure, or evidence that native proof state is unhelpful. It is a coverage failure under the prospectively frozen eligibility contract: the extraction produced substantial partial trace information, but no transition simultaneously satisfied the prerequisites required for the registered native-state comparison.

ORION-20 must therefore not:

- relax the eligibility rule after seeing the zero count;
- promote partial premise/tactic/state coverage as if it were the registered full native-state experiment;
- reinterpret successful trace extraction as problem-solving superiority;
- use the failed eligibility gate as an obstruction certificate for method-language expansion.

The correct terminal remains `CANNOT_CHECK`.

## Consequence for the top-tier programme

ORION-20 now has two complementary authority objects:

1. `P10_OCME_FORMAL_NONVACUITY_V1_GREEN` — exact bounded OCME non-vacuity in two formal languages;
2. `CANNOT_CHECK_NATIVE_STATE_COVERAGE` — the stronger native-Lean empirical lane did not satisfy its own eligibility contract.

The next native verifier-backed study must be a **new prospectively frozen successor**, justified by a root-cause analysis of why full state/tactic/premise coverage failed. It may improve instrumentation or select an access model that can actually expose the registered state, but it cannot retroactively change #618's terminal.

## Upward claim consequence

The negative sharpens ORION-20's central separation:

> failure to obtain adequate native evidence is an **evidence/accessibility deficit**, not scientific authority to escalate search, change representation, or invent a method language.

Only after ORION-19/ORION-21 accessibility/state routes and strong prover/search/repair/synthesis/evolutionary routes receive first refusal may a real OCME gate classify a surviving target as method-language limited.
