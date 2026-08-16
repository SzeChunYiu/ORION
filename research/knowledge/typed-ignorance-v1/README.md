# Typed scientific ignorance V1

## Problem

ORION already has typed residuals, but source literature can explicitly state known unknowns: missing evidence, unresolved relations, controversies, anomalous observations, research barriers and future-work questions. Treating every such statement as the same generic gap loses action information; treating it as a globally true gap launders one source's epistemic position into ORION authority.

## Parent work absorbed

This round uses the scientific-ignorance / known-unknown literature as a parent discipline, especially:

- *Creating an Ignorance-Base: Exploring Known Unknowns in the Scientific Literature*;
- *Identifying and classifying goals for scientific knowledge*;
- ignorance-oriented research-direction recommendation work;
- scientific limitation/future-work extraction datasets such as BAGELS;
- the classical warning against arguments from ignorance: absence of evidence does not by itself establish falsity/absence.

The source taxonomies are richer than ORION needs at the control boundary. V1 therefore preserves the source's own taxonomy label but compresses to eight **action-relevant** classes.

## V1 representation

`IgnoranceProjection.v1` is source-local and proposal-level:

- source/span identity;
- action-relevant ignorance kind;
- implied knowledge goal;
- subjects and contexts;
- evidence bindings;
- original source taxonomy label;
- uncertainty note.

Invariant: `asserts_global_gap == False`.

An ignorance projection is evidence that a source characterized something as unknown/incomplete; it is not evidence that the unknown is current, global, exhaustive or even still unresolved.

## Action classes

| Ignorance kind | ORION action |
|---|---|
| full unknown | independent evidence search |
| explicit question | open candidate subquestion + parent-discipline search |
| incomplete evidence | evidence/citation-neighborhood acquisition |
| indefinite relationship | competing relation hypotheses + discriminator |
| alternative/controversy | adversarial alternatives + discriminator |
| anomalous observation | replicate / experiment |
| research barrier | tool/measurement/method repair research |
| future research | retain as source-proposed candidate + freshness check |

Every plan requires independent confirmation and creates no scientific authority.

## Frozen discriminator

`src/orion/benchmarks/ignorance.py` compares typed routing with a generic `gap -> SEARCH_EVIDENCE` baseline on five exact cases:

1. incomplete evidence;
2. competing explanations;
3. anomalous result;
4. instrument/research barrier;
5. future-work proposal.

Acceptance:

- typed action accuracy = 1.0;
- typed routing strictly exceeds generic-gap routing;
- no source projection asserts a global gap;
- all plans require independent confirmation and mint no authority;
- future-work language is retained/check-freshness, not promoted as an active gap;
- exact duplicate source-local projections collapse, but independent sources making the same ignorance statement remain distinct evidence.

This is a control/routing benchmark, not an NLP extraction benchmark. Real text-to-ignorance extraction precision/recall remains empirical-open.

## Reopen triggers

- a source taxonomy category requires a materially different ORION action not represented here;
- typed routing does not beat generic residual routing on fresh tasks;
- downstream experiment/search selection is harmed by the extra typing;
- extraction uncertainty cannot be represented without adding new coordinates;
- future-work/limitation statements are shown to require different authority semantics.
