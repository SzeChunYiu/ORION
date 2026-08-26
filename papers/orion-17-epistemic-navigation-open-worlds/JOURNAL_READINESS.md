# ORION-17 candidate journal-readiness plan — Epistemic Navigation in Open Worlds

**Current terminal:** computed per commit, not asserted here. See
`../PEER_REVIEW_READY_PACKAGE.md`, which defines

```text
PEER_REVIEW_READY := p6-p8-candidate-ci == success AND ci == success
                     on one immutable head
```

This line previously read `CANNOT_CHECK / not a promoted paper / not peer-review
ready`. That was written before the submission package existed and had gone
stale: it contradicted `JOURNAL_READINESS_V2_1.md`, which already deferred to the
computed terminal, so the two files in this directory disagreed about ORION-17.

It is deliberately **not** replaced with `PEER_REVIEW_READY`. The package file
states that it does not hard-code a claim that could become stale after a content
edit, and writing a terminal into this file would reintroduce the staleness being
removed. What follows is the last observation, not a standing claim.

**Last observed on `2f701036`** (merge of #402 into `main`):

| predicate | result |
|---|---|
| `p6-p8-candidate-ci` | success |
| `ci` | success |

The candidate workflow's four required steps all passed on that head: *Theory and
live-embedding gate*, *Peer-review submission gate*, *Build and audit submission
PDFs*, *Archive audited submission PDFs*. The PDF step compiled
`submission/AIJ_MANUSCRIPT.tex` with `latexmk` and rejected no overfull box, undefined
reference or undefined citation.

Any commit after `2f701036` — including the one carrying this sentence — has to be
re-evaluated against the same two predicates. That is the point of computing the
terminal rather than storing it.

**Not claimed:** `PEER_REVIEW_READY` means ready for external editorial and
referee evaluation. It does not mean `PEER_REVIEWED`, `ACCEPTED`,
`FLAGSHIP_PROMOTED`, or empirically superior to any baseline.

## 0. Earned local package state — 2026-08-17 wide pass

Present now:

- `manuscript/FORMAL_CORE_V1.md` widened from one topology to an epistemic atlas;
- stopping theorem repaired to use **extension ambiguity**, with an explicit richness corollary rather than equating certificate absence with ambiguity;
- `manuscript/DRAFT.md` rewritten around orientation, chart/objective change and support/closure transport;
- synchronized `CLAIM_LEDGER_V1.md` preserving the repaired theorem premise;
- internal ownership matrix marking ORION-11 reframe and ORION-12 route/stop mechanisms as prior internal ownership;
- parent/donor map expanded through planning abstraction/representation languages, POMDPs, goal evolution, world models and exploration breadth;
- deterministic countermodel checker plus small theorem-boundary falsifier;
- additive `CHECK_RESULTS_V2.md` with certificate/ambiguity negative control, evidence-vs-closure transport and no-reframe control;
- `REPRODUCE.md`;
- `PROSPECTIVE_EVALUATION_V1.md` with exact-ground-truth atlas families, donor baseline slots and mandatory non-retrieval/negative controls;
- five-role adversarial review log.

These artifacts do not establish novelty, benchmark superiority or real-world scientific-navigation completeness.

## 1. Distinct-object gate
- [ ] #343 proves ORION-17 is more than ORION-11 representation reconstruction + ORION-12 route-governance terminology.
- [x] exact ORION-11/ORION-12-owned native mechanics are listed and excluded from ORION-17 novelty in the ownership matrix.
- [x] the candidate atlas residual has a formal definition and a direct prospective discriminator (support/closure transport across chart/objective change).
- [ ] the discriminator survives external planning/representation literature saturation.

## 2. Nearest-work closure
- [ ] graph/KG navigation families dispositioned with atomic receipts.
- [ ] exploratory search/information-foraging families dispositioned.
- [ ] POMDP/active information acquisition families dispositioned.
- [ ] planning abstraction/homomorphism/representation-language families dispositioned.
- [ ] learned/adaptive planning representation families dispositioned.
- [ ] web/deep-search agent planning and stopping families dispositioned.
- [ ] model-revision/world-model/replanning families dispositioned.
- [ ] goal/objective revision/evolution families dispositioned.
- [ ] ontology/schema evolution and preservation-map families dispositioned.
- [ ] scientific-exploration breadth/concentration work dispositioned.
- [ ] hostile exact-composition search completed.
- [ ] two no-material-change rounds.
- [ ] #287 novelty certificate current.

## 3. Theory
- [ ] atlas/chart/navigation definitions frozen after saturation.
- [x] local route stop/task stop/defer/`CANNOT_CHECK`/reframe are separated formally, with ORION-12 ownership explicit.
- [x] representation/objective-change operator defines partial maps and support/obligation preservation/reopening conditions.
- [x] exploration utility is separated from task-completion authority in the current formal core.
- [x] certificate absence and extension ambiguity are explicitly distinguished.
- [x] evidence identity versus closure/obligation transport is explicitly distinguished.
- [ ] planning-abstraction donor mappings prove conservative embedding where feasible.
- [ ] at least one high-value atlas theorem receives independent/mechanized proof review where justified.

## 4. Benchmark
- [x] prospective benchmark protocol draft exists with hidden branches, orientation, unknown coverage, censored routes, deceptive route diversity, chart/objective changes, model-revision controls, breadth traps and negative controls.
- [ ] versioned generator implementation frozen before candidate results.
- [ ] hidden useful branches generated/replayed deterministically.
- [ ] unknown-coverage/extension-ambiguity paired cases generated at benchmark scale.
- [ ] censored-route cases generated.
- [ ] deceptive route-overlap/local-optimum cases generated.
- [ ] dead-end/revisit cases generated.
- [ ] chart/ontology-change cases generated.
- [ ] objective-change evidence/closure transport cases generated.
- [ ] negative controls where topology change is harmful/unnecessary generated.
- [ ] at least one non-retrieval transfer domain executed.
- [ ] gold/stop/support semantics frozen before system results.

## 5. Baselines/ablations
- [ ] fixed-chart graph-navigation baseline.
- [ ] Search-on-Graph-style iterative navigator where faithfully implementable.
- [ ] active-information/POMDP baseline where valid.
- [ ] planning abstraction/world-model/goal-evolution donor baseline appropriate to each family.
- [ ] exact ORION-11+ORION-12 native composition baseline.
- [ ] resource-matched exploratory baseline where meaningful.
- [ ] direct no-chart-change ablation.
- [ ] direct no-censored-obligation ablation.
- [ ] direct no-support-transport gate ablation.

## 6. Metrics/statistics
- [x] primary metric families are prospectively specified (task/closure correctness, navigation, reframe/transport, breadth, resource cost).
- [ ] root-task success results.
- [ ] obligation/frontier coverage results.
- [ ] useful structural breadth and redundant exploration results.
- [ ] premature-stop/false-independence rates.
- [ ] dead-end recovery/revisit results.
- [ ] unnecessary reframe rate.
- [ ] support-transport/reopening error rates.
- [ ] calibrated unresolved/`CANNOT_CHECK` results.
- [ ] prospective margins/statistical treatment frozen for sampled families.

## 7. Manuscript/reproducibility
- [x] working markdown draft exists.
- [x] formal core + synchronized claim ledger exist.
- [ ] full-text related-work section with atomic donor dispositions.
- [ ] claim ledger #346 terminal complete (ledger exists but open claims remain).
- [x] deterministic theorem/countermodel reproduction path documented.
- [ ] deterministic benchmark generator + full navigation-trace replay under #347.
- [ ] immutable benchmark records/tables/figures.
- [ ] every promoted empirical positive has #283 receipt.

## 8. Submission
- [ ] venue selected under #345 after result shape is known.
- [ ] final literature refresh under #344.
- [ ] independent PDF proofread and archive.

## Done definition

Promote ORION-17 only if atlas-level representation/objective change plus support/closure transport shows a distinct prospectively identified result beyond ORION-11+ORION-12 and strong navigation/planning donors, including a non-retrieval exact-ground-truth transfer test and low unnecessary-reframe behavior. Otherwise merge useful atlas framing into ORION-11/ORION-12/programme theory.