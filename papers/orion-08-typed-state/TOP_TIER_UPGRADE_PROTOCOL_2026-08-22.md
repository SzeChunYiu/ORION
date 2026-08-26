# ORION-04 top-tier upgrade protocol — real scientific decision-state validation

**Freeze date:** 2026-08-22
**Status:** prospective research protocol; no outcome is claimed here.

## 1. Scientific question

When scientific decision systems receive **the same visible partial information**, does explicit typing/scoping of epistemic state improve decisions compared with matched-information untyped, retrieval-centric, or decision-agnostic representations?

The study tests representation/use of knowledge state, not raw model capability.

## 2. Why a real-domain study is required

The current ORION-04 suite deliberately uses exact synthetic worlds to isolate mechanisms. That is useful for causal/mechanistic control but does not establish transfer to real scientific workflows. Current 2026 literature already evaluates typed/provenance-aware memory, stale-memory behavior and VoI in real or naturalistic domains. A top-tier ORION-04 claim therefore requires decisions drawn from actual research records/frontiers.

## 3. Primary units of analysis

A primary item is a **scientific decision under incomplete information**, admitted before its resolution where possible.

Eligible decision types:

1. whether a previous failure/negative remains applicable after a representation/access/assumption change;
2. which uncertain claim/resource coordinate should receive a costly verification next;
3. whether a certificate/receipt/proof obligation remains transportable across an edit chain;
4. which candidate is Pareto-dominated when resource values are only interval-known;
5. which experiment/query should be acquired because it can change the downstream scientific decision;
6. whether a transformed scientific object requires remint/reverification or can reuse prior evidence.

## 4. Data sources

Primary target: >=100 decision items total across >=3 materially different research programmes, with at least 30 prospectively unresolved items if feasible.

Candidate sources:

- ORION quantum/QG programmes after the protocol freeze, excluding outcomes already known on 2026-08-22;
- ORION non-quantum mathematical/algorithmic programmes admitted after freeze;
- an external/open research corpus with versioned experiment/proof/review histories where state transitions and later outcomes can be independently reconstructed.

Historical ORION-Q items may be used for instrument development/control only and must be labeled retrospective.

## 5. State construction

For each item, create a canonical **fact bundle** containing the exact visible information available at decision time. All non-oracle arms receive the same bundle.

Derive multiple representations without adding facts:

### TYPED_SCOPED

Facts carry relevant structure such as:

- evidence/claim/assumption/obligation role;
- source/provenance pointer;
- representation/version id;
- applicability scope coordinates;
- VERIFIED/REFUTED/UNKNOWN status;
- interval/resource uncertainty;
- transport/remint dependencies;
- decision target(s) affected by the fact.

### UNTYPED_BAG

Same content/facts, but role/scope bindings are flattened where removal does not delete factual payload.

### RETRIEVAL_ONLY

Same underlying store accessed through a strong semantic/relevance retrieval baseline without the typed decision rules.

### STRONG_TASK_BASELINE

A domain-appropriate strong planner/agent that receives the same canonical fact bundle and tool budget. If a stronger donor matches or beats the typed mechanism, the result is donor-absorbed rather than counted as an ORION win.

### ORACLE

May use later-resolved truth only for evaluation/upper bound, never as a primary arm input.

## 6. Model/control separation

To isolate state representation from model capability:

- run at least two materially different reasoning backends where licensing permits;
- keep prompts/tool budgets constant across state-representation arms within a backend;
- include deterministic/rule-based arms for decision types where the mechanism can be exactly specified;
- report interactions between backend and state representation rather than pooling blindly.

ORION-04 may claim a representation effect only if it survives a strong matched-information baseline, not merely a weak heuristic.

## 7. Primary outcomes

Per decision type use a preregistered objective, such as:

- correct reopen/keep-closed decision;
- downstream regret under later resolved cost/feasibility;
- invalid evidence reuse / false escalation rate;
- verification efficiency at matched cost;
- infeasible/unsupported commit rate;
- laundering/transport error;
- probes spent on decision-irrelevant decoys;
- calibration/abstention under unresolved evidence.

Across types, report normalized regret/error and never collapse all dimensions into a single scalar without the per-task results.

## 8. Prospective scoring

For prospectively unresolved items:

1. freeze fact bundle + arm derivations + decisions;
2. commit result digest before later scientific work is read;
3. when the research item resolves, bind the resolving receipt/commit/public source;
4. score every arm under the original metric;
5. preserve `UNRESOLVED` where the later work does not decide the item.

No post-outcome rewriting of state scopes or decision metrics.

## 9. Hostile controls

The real-domain suite should deliberately include or prospectively wait for:

- irrelevant context/version changes that should **not** invalidate old evidence;
- real scope changes that should reopen it;
- high-uncertainty facts that are decision-irrelevant;
- low-entropy facts that are decision-critical;
- certificates valid on the last hop but invalid deeper in a transport chain;
- intervals where ranking is already determined versus genuinely Pareto ambiguous;
- regimes where remint/reverification is unnecessary and typed state should tie the strong baseline.

A claimed mechanism is invalid if its associated hostile control never bites or if it wins in a prespecified no-value regime where it should tie.

## 10. Related-work-aware hypotheses

Because typed memory, stale-memory repair and VoI are established neighboring topics, the main hypothesis is **not** “typing helps memory.”

Primary hypothesis:

> Explicit scientific applicability/provenance/uncertainty/decision-role bindings improve downstream research decisions under matched information, especially when validity depends on context changes or when information value is decision-specific.

Secondary hypotheses:

- scope binding improves stale-failure reuse beyond timestamp/update detection alone;
- decision-coupled acquisition beats generic uncertainty/information-gain selection when decoys exist;
- typed evidence transport reduces invalid reuse across representation edits beyond last-hop/source-only provenance checks;
- benefits disappear or tie where the typed coordinates are irrelevant.

## 11. Statistical plan

- paired comparisons within each item whenever arms share the same fact bundle;
- programme/item clustering in uncertainty estimates;
- report effect sizes and confidence intervals, not only p-values;
- multiplicity correction or clearly separated confirmatory/exploratory outcomes;
- no pooled “overall win” unless heterogeneity is modeled and per-family effects remain visible.

## 12. Stop rules

- If a strong task baseline matches the typed mechanism with identical information, record donor absorption.
- If benefits appear only on synthetic controls and not real items, publish the negative transfer result; do not promote ORION-04 as a real-agent paper.
- If typed representation adds facts rather than structure, invalidate that item for the matched-information analysis.
- If prospective item count remains too small, ORION-04 stays a synthetic mechanism/benchmark paper.

## 13. Top-tier success criterion

A strong terminal would be evidence that **the representation of scientific knowledge state itself**—not more information, more model calls, or weaker baselines—causally changes real research decisions across materially different scientific workflows, with predictable conditions for when typing/scoping helps and when it should not.
