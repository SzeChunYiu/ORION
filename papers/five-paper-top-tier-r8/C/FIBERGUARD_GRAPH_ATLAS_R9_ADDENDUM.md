# FiberGuard R9 Addendum: Seven-Vertex Atlas Nontransfer and Exact Repair

**Status:** finite exact extension on the complete unlabeled simple-graph atlas at seven vertices.

## Research question

The R8 graph-colouring experiment found that, on all labelled six-vertex graphs, augmenting the base representation

`(sorted degree sequence, triangle count)`

with the induced four-cycle count removed every chromatic-number collision. This addendum tests whether that repair transfers one vertex higher and, when it does not, searches a frozen family of stronger exact refinements.

## Complete domain

The domain is the 1,044 seven-vertex graphs in the NetworkX 3.6.1 Graph Atlas slice. The Graph Atlas contains one representative of every unlabeled simple graph on at most seven vertices. Atlas indices 209 through 1252 are exactly the seven-vertex slice.

Every graph is solved twice:

1. exact bounded-colour backtracking, seeded by an exact clique lower bound; and
2. exact enumeration of partitions into independent sets.

The two target engines agree on all 1,044 graphs.

## Base collision result

For the base representation, the atlas contains:

- 622 representation fibres;
- 58 chromatically ambiguous fibres; and
- maximum fibre diameter 1.

A maximum-diameter fibre has feature

`((2,3,3,3,4,4,5), 5)`

and contains both a 3-chromatic and a 4-chromatic graph. Registered endpoint witnesses are Graph Atlas 961 (`FlZZ?`) and Graph Atlas 964 (`FllHo`).

## Nontransfer discriminator

The six-vertex repair does **not** transfer:

- induced `C4` count leaves 17 ambiguous fibres;
- clique number leaves 18 ambiguous fibres;
- the one-dimensional Weisfeiler--Leman trace leaves 20 ambiguous fibres.

This is a required negative result. The R8 statement is therefore retained only on its exact six-vertex domain; it is not a general repair theorem.

## Exact seven-vertex repairs

Two frozen refinements eliminate target ambiguity on the complete seven-vertex atlas:

1. the induced four-vertex graphlet profile: 1,034 refined fibres, zero ambiguous fibres;
2. the bundle `(induced C4 count, clique number, one-WL trace)`: 986 refined fibres, zero ambiguous fibres.

Adding the one-WL trace to the graphlet profile distinguishes all 1,044 atlas graphs, but graph identification is stronger than target sufficiency and is not required for exact chromatic prediction.

## Interpretation

The experiment supplies three publication-relevant facts.

First, a collision-guided feature that is exact on one bounded domain can fail immediately on the next complete domain. Second, exact repair need not require a graph identifier: the three-family bundle remains coarser than graph isomorphism while being sufficient for chromatic number on this domain. Third, target sufficiency and representation injectivity remain distinct; the graphlet profile is target-sufficient without identifying all 1,044 graphs.

These are finite exact statements. They do not establish prevalence on large random or production-derived graphs, a polynomial-time sufficiency theorem, learned-model performance, or external replay.

## Independent replay gate

A structurally independent replay should:

- generate the seven-vertex unlabeled graphs with `nauty/geng`, SageMath, or another source independent of the NetworkX atlas file;
- solve chromatic number with SAT/ILP or a different exact formulation;
- reconstruct induced four-vertex graphlet classes with an independent canonical labeller;
- compare the 1,044 graph digests, target vector, fibre partitions, endpoint witnesses, and refinement summaries; and
- preserve disagreement as a first-class terminal.

Allowed terminals:

- `C_GRAPH_ATLAS_N7_INDEPENDENT_REPLAY_PASS`;
- `C_GRAPH_ATLAS_N7_DISAGREEMENT`;
- `C_GRAPH_ATLAS_N7_SOURCE_COVERAGE_FAILURE`;
- `CANNOT_CHECK_INDEPENDENT_GENERATOR`.

A replay PASS upgrades bounded reproducibility only. It does not confer journal acceptance, external prevalence, or production authority.
