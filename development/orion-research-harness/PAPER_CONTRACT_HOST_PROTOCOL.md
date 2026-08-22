# ORION paper-contract host protocol

Date: 2026-08-22
Scope: shared `packages/orion-research-harness`
Authority: host/orchestration instructions only; no scientific, novelty, adoption, promotion, merge, or global-stop authority.

## Purpose

The paper-contract runtime closes the distinction between a mechanic being discoverable and being executable. It provides raw-source method reconstruction, evidence-derived multi-axis saturation, Paper-VII navigation, P6 epistemic mechanics, P8 typed authority, P10 obstruction-certified method-language expansion, and host-callable P11-P14 decision laws.

## Install

```bash
python -m pip install -e '.[dev]'
python -m pip install -e 'packages/orion-research-harness[dev]'
```

## Semantic self-checks

Run both gates:

```bash
orion-harness-paper paper-contract-conformance
orion-harness-paper paper-programme-conformance
```

A release-ready result must report:

```text
ORION_HARNESS_PAPER_CONTRACT_P0_OPERATIONAL
ORION_HARNESS_P1_P15_OPERATIONAL
```

The first gate executes the P0 hostile semantic probes. The second executes a positive and a fail-closed decision probe for every registered P1-P15 paper owner. Neither terminal is a scientific benchmark, an extraction-accuracy claim, or promotion authority.

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

The harness does not pretend to own PDF/OCR semantics. It creates a `DOCUMENT_TEXT_EXTRACT` request containing the project-relative path, exact `sha256:` PDF digest, byte length and an instruction to extract searchable text without semantic summarization. The host result must carry the exact source digest. A digest mismatch fails closed.

### `LLM_COMPLETE` method extraction

Each deterministic source chunk produces task `paper_method_structure_extract_v1`. Return `content` containing JSON claims with `coordinate`, `value`, and an exact verbatim `quote`. Every populated scientific coordinate needs an exact source quote. Unsupported coordinates must be omitted and remain typed `UNKNOWN`. Dependencies are exact `[from_mechanic, to_mechanic]` pairs. The harness checks every quote before canonical P1/P3 construction.

### `VERIFY_EVIDENCE` method-structure verification

After canonical construction, a separate host capability independently checks the interpretation. A pass requires at least one meaningful certificate id. Failed support yields `CANNOT_CHECK_SOURCE_SUPPORT`, not verified structure.

## P6 host commands — epistemic mechanics

Execute a declarative P6 mechanic contract against a typed state:

```bash
orion-harness-paper mechanic-apply --file mechanic-input.json
```

The JSON object contains `state` and `contract`. The runtime enforces declared write footprints, hard evidence/authority premises, obligation persistence/discharge, non-escalating authority and recursive audit-rank constraints. `DENIED` and `CANNOT_CHECK` never mutate state.

Run root-inclusive certificate-aware dependency repair:

```bash
orion-harness-paper dependency-repair --file repair-input.json
```

The object contains `state`, `changed_ids`, and optional `certificates`. Changed certified roots cannot self-preserve; downstream preservation requires an exact current protected certificate.

## P7 host command — open-world navigation

```bash
orion-harness-paper navigation-plan --file navigation-state.json
```

The state carries an active chart, location/frontier, route contracts, obligations, budget, censoring, visited state, evidence and route-stop receipts. Core invariant:

```text
task_stop -> every mandatory obligation is satisfied, discharged, or certificate-covered
```

Route stop never implies task stop. Budget exhaustion, censored/unavailable route exhaustion, or an unmapped mandatory obligation remains `CANNOT_CHECK`. An unresolved start yields orientation.

## P8 host command — typed epistemic authority

```bash
orion-harness-paper authority-check --file authority-input.json
```

The object contains `effect` and `context`, plus optional confidence/expected utility. Authority requires exact typed obligation discharge, blocker refutation, fresh in-scope grant and exact content/epoch binding. Confidence and utility are not authority currency. Cross-domain/type changes require registered protected coercions. Scope widening is denied unless the coercion explicitly declares `allow_scope_widening=true`.

## Evidence-derived nine-axis research saturation

```bash
orion-harness-paper research-saturation --file rounds.json
```

Each round supplies executed route contracts, observed Self-ORION axes and observed item identities. Novelty counts are derived by set difference. Independent-flat credit is derived structurally and is one-route-per-round; a mixed bundle cannot manufacture a new independent route family. Missing axes, material residuals, dependent routes or resource bounds block bounded saturation. Bounded saturation never grants absolute completeness.

## P10 host command — obstruction-certified method-language expansion

```bash
orion-harness-paper ocme-assess --file ocme-episode.json
```

The runtime enforces O0-O6: freeze/custody, lower-level first-right-of-refusal, independently verified obstruction, candidate edit, independent outside-closure check, held-out transfer/false-expansion guard, donor comparison and independent reproduction. Timeout-only failure is not an obstruction certificate. A supported method expansion remains a non-authorizing research result; P4/P8/protected evaluation still own promotion.

## P11-P14 host-callable paper laws

```bash
orion-harness-paper p11-accessible-rank 20 3
orion-harness-paper p12-allocate 2 0 --budget 2
orion-harness-paper p13-action Z1 VERIFY --recoverable
orion-harness-paper p14-disposition --file governance-facts.json
```

These are lightweight deterministic decision kernels corresponding to the current paper contracts: P11 accessible-rank/optionality, P12 matched-budget state-reasoning allocation, P13 responsibility-scoped reuse/reopen/CANNOT_CHECK, and P14 specification-separated governance. They do not import publication outcomes as policy inputs; P14 explicitly rejects gold/private adjudication fields.

## Structural route contracts

A route contract carries route identity/family, obligation scope, critical failure/coverage assumption ids, coverage scope, optional censoring scope and availability. Different query strings, APIs, labels or result overlap do not establish structural independence. The bounded V1 sufficient test requires explicit structural identity and disjoint critical assumptions.

## Authority boundary

Paper extraction, mechanic execution, dependency repair, navigation, authority decisions, bounded saturation, OCME dispositions, P11-P14 law outputs and both conformance terminals are non-authorizing research-control evidence. Scientific conclusions still require normal ORION evidence, protected verification and authority machinery.
