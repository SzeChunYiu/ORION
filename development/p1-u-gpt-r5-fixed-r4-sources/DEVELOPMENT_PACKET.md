# P1-U GPT-R5 — fixed R4 source scoring

Parent: #649  
Campaign: #721  
Base: `main@1e462d16b006130c5ba93e3fe91635c5d47a55a5`

## Scientific purpose
R5 performs the first naturalistic ORION-vs-donor-complete P1 scoring attempt. Source selection is already complete and outcome-independent: all 26 qualifying R4 sources were selected before any policy outcome existed.

No primary source may be added, removed, replaced, duplicated or downweighted because of policy performance.

## Fixed data geometry
- 22 substantive source pairs: SEARCH 4, REPRESENTATION 4, IMPLEMENTATION 4, MEASUREMENT 3, OBJECTIVE/MODEL 4, PROBLEM_BOUNDARY 3;
- each pair contains one adverse member and one same-source `NO_HIGH_LEVEL_REFORMULATION` control;
- 4 source-disjoint `UNRESOLVED` episodes;
- 48 total episodes.

## Pre-outcome source encoding
Each fixed source is encoded before policy execution using only source-grounded evidence.

For every adverse/control pair:
- adverse target probe may be `SUPPORT` only with direct source support;
- matched control target probe may be `REFUTE` only with direct source support for adequacy/absence of the adverse factor;
- a non-target probe may be `REFUTE` only where the within-source comparison explicitly holds/rules that factor out;
- otherwise non-target probes are `INCONCLUSIVE`;
- candidate-visible dossiers contain only pre-resolution facts and no source identity, query ID, gold label or post-resolution conclusion.

Unresolved sources use `INCONCLUSIVE` wherever the source does not identify a responsibility.

## Candidate and comparator
Byte reuse from merged R2:
- `ORION_R2` candidate;
- `B3_HORIZON2_DONOR_COMPLETE` primary comparator;
- same priors, likelihoods, utilities, probe set and budget=2.

## Frozen primary tests
### Episode-level
Retain the full R2 rule unchanged:
- overall GRS difference >= +0.10;
- paired bootstrap lower 95% bound > 0;
- every actual-domain mean difference >= -0.10;
- ORION unnecessary high-level rate <= B3 and <= 0.05;
- zero harmful lower-level skips;
- zero false resolution of UNRESOLVED.

### Matched-pair selectivity
For each source pair, pair success requires both adverse and control correct.

Require:
- micro pair-selective ORION-B3 >= +0.10;
- ordinary pair bootstrap lower 95% bound > 0;
- equal-weight six-class macro pair difference >= +0.10;
- class-stratified bootstrap lower 95% bound for macro difference > 0;
- zero ORION harmful high-level escalation on any control;
- at least three classes with non-negative pair difference;
- no class below -0.10.

The macro is not a replacement for the episode/micro tests; all must pass.

## Replication
A passing 2020 result opens, but does not satisfy, #649. A disjoint 2019 replication with independent scorer/direct policy reconstruction must pass the same scientific margins before parent closure.

## Mutation boundary
The exact fixed source set and evaluator are frozen before candidate-visible source encoding. The completed source encoding is then frozen before first policy execution. After policy execution begins, no source, dossier, gold, probe, metric, margin, comparator or policy mutation is permitted in R5.
