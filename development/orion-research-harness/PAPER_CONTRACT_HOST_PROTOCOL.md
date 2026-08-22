# ORION paper-contract host protocol

Date: 2026-08-22
Scope: shared `packages/orion-research-harness`
Authority: host/orchestration instructions only; no scientific, novelty, adoption, promotion, merge, or global-stop authority.

## Purpose

The paper-contract runtime closes the distinction between a mechanic being discoverable and being executable. It adds raw-source method reconstruction, evidence-derived multi-axis saturation, and Paper-VII epistemic navigation semantics to the shared research harness.

## Install

```bash
python -m pip install -e '.[dev]'
python -m pip install -e 'packages/orion-research-harness[dev]'
```

## Semantic self-check

Run:

```bash
orion-harness-paper paper-contract-conformance
```

A release-ready result must report:

```text
ORION_HARNESS_PAPER_CONTRACT_P0_OPERATIONAL
```

The command executes hostile semantic probes. It is not a scientific benchmark and does not establish arbitrary-paper extraction accuracy.

## Raw paper -> Paper-I/Paper-III structure

Initialize a normal harness workspace whose `project_root` contains the source:

```bash
orion-harness init .research --project-root .
orion-harness-paper paper-structure .research path/to/paper.txt method:example \
  --source-id paper:example \
  --source-version v1
```

The command is replayable. It returns exit code 2 whenever an external host capability is pending. Service the exact request and rerun the same command.

### Plain text, Markdown, TeX and other UTF-8 text

The harness reads the exact local bytes inside `project_root`, computes a SHA-256 source digest, chunks the text deterministically, and asks the host to propose source-local structure.

### PDF sources

The harness does not pretend to own PDF/OCR semantics. It creates a `DOCUMENT_TEXT_EXTRACT` request containing:

- project-relative source path;
- exact `sha256:` digest of the PDF bytes;
- byte length;
- an instruction to extract searchable text without semantic summarization.

The host result must be:

```json
{
  "text": "...extracted searchable text...",
  "source_digest": "sha256:...exact digest from the request..."
}
```

A digest mismatch fails closed. Do not service this capability from a different copy of a paper.

### `LLM_COMPLETE` method extraction

Each deterministic source chunk produces task `paper_method_structure_extract_v1`.

Return `content` containing JSON of the form:

```json
{
  "claims": [
    {
      "coordinate": "mechanics",
      "value": "measure_midpoint",
      "quote": "exact verbatim source text"
    },
    {
      "coordinate": "dependencies",
      "value": ["measure_midpoint", "discard_inconsistent_half"],
      "quote": "exact verbatim source text establishing the order/dependency"
    }
  ]
}
```

Rules:

- Every populated scientific coordinate needs an exact verbatim source quote from the supplied chunk.
- Do not paraphrase in `quote`.
- Do not infer a missing coordinate from analogy, common knowledge, or a similar method.
- Omit unsupported coordinates. The harness will preserve them as `UNKNOWN`/partial.
- For sequence-valued coordinates emit one atomic claim per value.
- A dependency value is exactly `[from_mechanic, to_mechanic]`.
- Explicit author rationale may be populated only when the author actually states it.
- Never grant method-fibre, scientific, novelty, adoption, promotion, merge, or global-stop authority.

The harness mechanically checks every quote against the exact source text before it calls the canonical Paper-I and Paper-III builders.

### `VERIFY_EVIDENCE` method-structure verification

After canonical construction, a second capability request independently checks the structured interpretation against the exact cited spans.

Return:

```json
{
  "passed": true,
  "certificate_ids": ["meaningful-independent-certificate-id"],
  "reason": "..."
}
```

A passing result requires at least one certificate id. Fail or return `passed:false` when a populated coordinate overstates the source, a quote does not establish the claimed semantics, or the support is otherwise insufficient.

A failed verification produces `CANNOT_CHECK_SOURCE_SUPPORT`, not a verified structure.

## Structural route contracts and saturation

The Paper-VII route runtime is `orion_research_harness.epistemic_navigation.RouteContract`.

A route contract carries:

- `route_id`;
- `route_family`;
- obligation scope;
- critical failure/coverage assumption ids;
- coverage scope ids;
- optional censoring scope;
- availability.

Different query strings, APIs, route-family labels, or observed result sets do not establish structural independence. V1 uses the conservative sufficient test that both routes have explicit critical-assumption/coverage identities and their critical-assumption sets are disjoint.

`orion_research_harness.research_saturation.ResearchRoundEvidence` records actual observed item identities per Self-ORION development axis. Novelty counts are derived by set difference. The caller cannot supply an `independent_route=True` bit; independence is derived from route contracts before invoking the canonical nine-axis Self-ORION saturation evaluator.

An unobserved required axis, material residual, dependent route family, or resource-bound round prevents bounded saturation. Bounded saturation never grants absolute completeness.

## Paper-VII navigation runtime

`orion_research_harness.epistemic_navigation` implements operational chart/navigation objects:

- `EpistemicChart`;
- `NavigationState`;
- `RouteContract`;
- `Obligation`;
- `ReframeMorphism`;
- route observations and local route-stop receipts;
- `plan_navigation`;
- `apply_reframe`.

Core invariant:

```text
task_stop -> every mandatory obligation is satisfied, discharged, or covered by a valid closure certificate
```

Consequences:

- route stop never implies task stop;
- budget exhaustion with an open mandatory obligation is `CANNOT_CHECK`;
- censored/unavailable/stopped routes with an open mandatory obligation remain `CANNOT_CHECK` unless another executable route exists;
- unresolved starting location produces an orientation action;
- evidence identity may survive a reframe while old closure authority reopens;
- an unmapped mandatory obligation becomes `CANNOT_CHECK` rather than disappearing;
- a previously closed obligation transports as closed only when the reframe explicitly carries a support-preservation proof flag for that obligation.

## Authority boundary

Paper extraction, a route contract, a navigation transition, a bounded-saturation report, and the conformance terminal are all non-authorizing research-control evidence. Scientific conclusions still require the normal ORION evidence/verification/authority machinery.
