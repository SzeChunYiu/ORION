# Bytes, builds and meaning: a revision-bound Lean evaluation closure note

## Abstract

We report a prospectively frozen source-level study of coarse tactic-family
recurrence in 457 files from an exact Mathlib revision and use its failure modes
to specify a fail-closed evaluation identity. A hostile audit invalidated the
first output because 26.52% of projected trajectories crossed intervening
top-level commands. After freezing a parser amendment, the corrected study
finds strong blocked next-action predictability across top-level modules
(Markov-minus-unigram `0.1046`, module-bootstrap 95% interval
`[0.0863, 0.1223]`) and significantly fewer distinct cross-module bigram and
trigram patterns than every frozen order/provenance null. This means recurrence
is concentrated in a small coarse vocabulary; it does not establish reusable
tactics or proof utility. Exact native Lean audit receipts and mutation controls
separate source identity, native acceptance and authority. Constructive review
shows that versioned benchmark packaging, native checking, statement
faithfulness and tactic mining are mature prior objects. We therefore retain
the work as a technical note merged into ORION's P4/P8 evaluation programme,
not as a standalone novelty claim.

## 1. Question and claim boundary

The narrow question is whether a Lean evaluation result can remain attached to
the exact source, revision, dependencies, attempt and verifier that produced
it. Three assertions are deliberately separate:

1. **identity:** these are the same bytes and environment;
2. **native acceptance:** this named Lean runtime exited successfully;
3. **meaning/authority:** this is the intended theorem and supports a scientific
   claim.

P10 implements the first boundary and records the second. It does not decide
the third; P4/P8 own that authority.

## 2. Frozen source and projection

The source population is Mathlib commit
`e72c1e277f31441626621f7d0c7207862fc25569`, toolchain
`leanprover/lean4:v4.34.0-rc1`. An outcome-blind path-hash rule selected up to
16 files per active top-level module, excluding `Deprecated` and `Testing`:
457 files, 31 labels and 5,655,364 bytes. Every source byte, selection rule,
license and dependency manifest is committed.

The analysis recognizes tactic-mode theorem/lemma bodies after an explicit
`by`, maps source lines into 16 coarse families, collapses consecutive
duplicates and excludes unknown lines. It is not a Lean grammar, elaborated
trace or semantic tactic identity.

## 3. A result that had to be invalidated

V2 initially appeared to pass its numerical condition. A hostile audit then
found that the inherited projector stopped only at the next theorem/lemma and
could absorb intervening definitions, instances, namespaces and other
top-level commands. Of 4,861 projected trajectories, 1,289 crossed at least one
such boundary (3,903 leaked boundaries). V2 remains archived with
`supports_claim=false`.

The V2.1 amendment was committed before the repaired outcome. It stops a proof
when indentation returns to declaration level, and hostile definition,
instance, namespace and `end` cases are unit-tested. On the exact corpus, no
recognized top-level command remains inside a projected proof body.

## 4. Corrected result

| Split | Bigram seen | Trigram seen | Markov accuracy | Unigram accuracy | Difference |
|---|---:|---:|---:|---:|---:|
| Leave source out | 0.9970 | 0.9521 | 0.3851 | 0.2796 | 0.1055 |
| Leave top module out | 0.9959 | 0.9450 | 0.3842 | 0.2796 | 0.1046 |

The leave-top-module difference has module-bootstrap 95% interval
`[0.0862935, 0.1223224]`. There are 151 cross-module bigrams and 518 trigrams.
For every frozen seed and both order-preserving/provenance-preserving null
families, both observed counts lie in the significant lower tail. The supported
interpretation is **concentrated recurrence in fewer distinct coarse patterns**.
It is not evidence that these patterns are executable custom tactics.

## 5. Native and mutation receipts

Before outcomes, eight top-module-stratified receipt subjects were selected by
hash from the 457-file population. Each exact upstream file is run with
`lake env lean <path>` inside the exact Mathlib checkout. Receipts bind the file
digest, Git revision, toolchain, dependency manifest, command, exit status and
stdout/stderr digests. A planted `False` proof must exit nonzero.

All eight subjects exited zero under Lean 4.34.0-rc1 (release commit
`3447a668783dbce1a8fdb97101dd067687b2b418`) and the negative control exited
one. Two complete replays produced the same receipt bytes (SHA-256
`1aed4fbfb7e9b83eda08bfe19b4d4348dcdbffba82b1db567d05a61aaa8c5b90`).
This establishes native acceptance only for those eight exact subjects.

The framework also includes a minimal task-id-only control: changing the source
revision leaves the stale `SUCCESS` lookup reachable. In the bound path, the
same mutation changes the environment and statement digests and receipt binding
fails. Source bytes, statement text and attempt substitutions fail similarly.

These controls show identity drift detection. They do not show theorem
faithfulness or scientific validity.

## 6. Knowledge assimilation and residual

The full receipt ledger is `SATURATION_LEDGER_2026-08-18.md`. Its main effects
on ORION are concrete:

- SorryDB/VeriSoftBench structures expanded the identity object from a statement
  hash to repository, revision, toolchain, dependencies, path and source bytes.
- Formal Conjectures' immutable version discipline caused V2 to remain visible
  and V2.1 to become a separate protocol.
- CSLibPremiseBench/LeanDojo forced source-visible projections and native traces
  to remain different evidence types.
- TacMiner and earlier sequential proof mining removed tactic-pattern mining
  from novelty and set a graph/state-aware baseline for any reopen.
- current faithfulness audits reinforced that native acceptance cannot become
  statement meaning or scientific authority.

After absorption, the residual identity/correctness/authority distinction is
useful but already belongs to P4/P8. The correct terminal is a merged technical
note.

## 7. Limitations and nonclaims

- The source projector excludes 6,097 unknown proof-body lines and cannot
  represent Lean elaboration, proof states, tactic semantics or dependencies.
- Native acceptance is claimed only for the eight prospectively selected audit
  files, not all 457 files.
- No TacMiner-class baseline or downstream proof-search study was run; that
  blocks any reusable-tactic headline.
- The unavailable Phase-2B Hugging Face sample is removed from this note.
- No theorem correctness, statement faithfulness, Mathlib-wide transfer,
  prover superiority, premise-selection or scientific-authority claim is made.

## 8. Reproducibility and disposition

Machine-readable protocols, source manifests, invalidated and corrected
results, null distributions, native receipts, exact environment versions and
one-command readiness checks are committed beside this note. The terminal is
`TECHNICAL_NOTE_MERGED_INTO_P4_P8_PROGRAMME`; reopen conditions are in
`FOLLOW_UPS.md`. Bibliographic metadata is in `references.bib`.
