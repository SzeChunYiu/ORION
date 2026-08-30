# ORION-08 third decision family — RO-Crate workflow applicability

**Committed before any workflow record is fetched.** The binding, the utility and
the terminals below are fixed here, and the data they will be applied to has not
been looked at.

## Why a third family

#1701 lists this one as optional: *"Optional third family: E7 RO-Crate/workflow
applicability."* The two committed legs are CC18 (tabular classification under a
cost matrix) and Defects4J (selecting tests to run). Both are decisions *about a
computation the agent will perform itself*.

This one is different in kind: it is a decision about **whether an external
artifact is usable at all**, made from its description before paying to open it.
If the refinement theorem holds here too, it holds across three families that share
only the theorem.

## Source and gold

**WorkflowHub** (`workflowhub.eu`), a live public registry of RO-Crate-packaged
computational workflows. Each record carries a `workflow_class` (Nextflow, Galaxy,
CWL, Snakemake, …), a `license`, `tags`, `tools`, `creators`, and an `internals`
object.

**The gold is `internals`.** WorkflowHub populates it by parsing the workflow's
RO-Crate and extracting its structure — inputs, outputs, steps. A non-empty
`internals` means the crate was successfully parsed into a reusable description; an
empty one means it was not. This is an objective, externally-produced fact about
the artifact, computed by the registry rather than by this study, and it is exactly
the thing a would-be reuser wants to know before fetching.

## The decision

- **Observation**: the record's metadata *excluding* `internals` — workflow class,
  license, tag count, tool count, creator count, presence of a DOI.
- **Action**: `attempt` (fetch and try to reuse the crate) or `skip`.
- **Gold**: `internals` non-empty.
- **Utility**, frozen here:

```
utility(attempt, usable)     = +1
utility(attempt, not usable) = -0.25    a wasted fetch and parse
utility(skip,    usable)     = -1       a reusable artifact passed over
utility(skip,    not usable) =  0
```

A wasted fetch is cheap and a missed reusable workflow is expensive, which is the
real economics of artifact discovery. Under this matrix the optimal action for a
fibre is `attempt` iff `P(usable | fibre) > 0.25/2.25 ≈ 0.1111`.

## Bindings, frozen here

- **coarse** — `license`, normalised to its SPDX-style string, with missing
  licenses as their own class. What the record says about *terms of use*.
- **refined / typed** — `(license, workflow_class)`. Adds what *kind of thing* the
  artifact is.

The refinement adds exactly the artifact's type, which is the typed-state content.
Coarse is a strict coarsening by construction.

## Guards carried over from the earlier legs

Three defects were made and corrected on the CC18 and Defects4J legs. They are
pre-empted here rather than repeated:

1. **In-sample scoring.** The theorem governs the distribution its fibres are
   defined on. Out-of-sample transfer is reported separately as the different claim
   it is.
2. **`MIN_MASS = 1`,** applied to the prediction and the measurement alike. A
   threshold on one but not the other manufactures contradictions out of fibres the
   predictor never examined.
3. **A degeneracy gate.** If more than half the refined fibres hold one record, the
   terminal is `CANNOT_CHECK_DEGENERATE_BINDING`. A binding whose fibres are single
   records reproduces the record instead of estimating a fibre.

## Strata

Records are stratified by `workflow_class`. At least one class must be predicted
**value** and one predicted **no value**, or the terminal is
`CANNOT_CHECK_NO_CONTRAST`.

## Arms

`coarse`, `refined_typed`, `attempt_all` (the safe expensive default), `oracle`.
`attempt_all` matters: if it is not beaten, nothing here recommends looking at
metadata at all.

## Terminals

- `THEOREM_PREDICTS_REAL_TRANSFER_ROCRATE`
- `THEOREM_FAILS_ON_REAL_DATA_ROCRATE` — recorded with the fibre, not rescued by
  re-binding.
- `CANNOT_CHECK_NO_CONTRAST` / `CANNOT_CHECK_DEGENERATE_BINDING`

A pass makes the theorem's real-domain transfer supported on three structurally
different families. It does not claim the typed binding is a good way to triage
workflows, and the `attempt_all` arm is there to keep that question honest.

## Acquisition

Records are fetched read-only from the public JSON API, paginated, with the
retrieval date and record count recorded. Nothing is uploaded and no credential is
used.
