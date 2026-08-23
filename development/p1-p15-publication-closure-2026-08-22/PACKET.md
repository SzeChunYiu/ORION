# P1-P15 publication-closure development packet

Date: 2026-08-22

## Fixed inputs

- Candidate manuscript ref: `cdea6eb85033e85e41e50242f44e28f6b9a0e423`
  (`refs/pull/831/head`).
- Repository base observed at freeze: `70c16e7e8f72b394f7da9b2e57288da7746ad4f0`.
- Academic-paper-skills ref: `9aaff6ec9f853cedf07d19ffe3d4374587e8ed2b`.
- Scope: P1-P15 only. Q1-Q4 are explicitly deferred.
- Target: no single journal has been authorized. Universal selective-venue
  technical criteria apply; target-specific formatting and priority criteria
  remain unresolved.

The candidate ref is read-only. PR #831 owns its manuscript edits. PR #871 owns
the shared harness-mechanics wave. This lane may add audits and independently
reviewable repairs, but it must not write either peer branch.

## Atomic development questions

1. Does every P1-P15 identity have a complete, independent, chapter-level TeX
   manuscript and a reproducible rendered PDF?
2. Does every central claim have a bounded claim type, authoritative evidence,
   a stated scope boundary and verified citation support where prior work is
   invoked?
3. Are negative, null, failed and `CANNOT_CHECK` results preserved without being
   mislabelled, and has each load-bearing failure either become a bounded result
   or triggered a prospectively frozen successor?
4. Could any reported outcome be recovered from construction cues, answer-bearing
   metadata, an unreachable gate, a circular grader or the underlying language
   model rather than the declared mechanism?
5. Do the manuscript specification, executable implementation, receipts and
   claim ledger agree at the frozen ref?
6. Can a clean independent environment reproduce every promoted result and
   distinguish infrastructure failure from scientific outcome?

## Initial bounded saturation assessment

Knowledge coverage is not saturated. Several readiness files require a filing-time
literature refresh, and no exact target-journal criteria have been fixed. Search-
universe coverage is not saturated until primary-source metadata and contradictory
or limiting evidence are checked for every central novelty claim. Formulation
coverage is not saturated until a hostile reviewer has tested construction-decided,
leakage, circularity, unreachable-gate and model-substitution explanations.

Observed structural facts at the fixed candidate ref:

| Paper | Chapter TeX tree | Canonical `main.tex` | PDF in manuscript tree | Initial disposition |
|---|---:|---:|---:|---|
| P1 | yes | yes | yes | send to technical review |
| P2 | yes | yes | yes | send to technical review |
| P3 | yes | yes | yes | send to technical review |
| P4 | yes | yes | yes | send to technical review |
| P5 | yes | yes | yes | send to technical review; readiness scope is narrower than a full external claim |
| P6 | yes | yes | yes | send to technical review |
| P7 | yes | yes | yes | send to technical review |
| P8 | yes | yes | yes | send to technical review |
| P9 | yes | yes | yes | send to technical review |
| P10 | yes | yes | yes | defer editorial promotion pending construction-decision audit |
| P11 | yes | yes | yes | send to technical review; arm-placement defect remains explicit |
| P12 | yes | yes | yes | send to technical review |
| P13 | yes | yes | yes | send to technical review |
| P14 | yes | yes | yes | send to technical review; branding and specification-conformance scope need review |
| P15 | no | no | no | editorial reject as incomplete manuscript |

`yes` records presence, not build success or scientific adequacy.

## Challenge to the saturation basis

Repository-local readiness labels are hypotheses, not editorial authority. A green
test can certify only the property encoded by that test. A receipted result can
still be unusable if its construction discloses the answer, its decision gate has
no failing region, its grader is the gold function, or its scientific byte is not
the byte executed. Literature matrices can appear saturated while missing an
adjacent field or using metadata-only candidates as evidence.

## Why prior searches and reviews may have missed knowledge

- project terminology can hide donor concepts under local names;
- computer-science evidence may be primarily in conference proceedings rather
  than journals;
- a title/abstract match can conceal a method or population mismatch;
- negative and contradictory work may use failure-specific vocabulary;
- repository reviews may share the same construction assumptions as the authors;
- a broad paper count target can encourage scope-preserving prose instead of
  paper-identity testing.

## Reopen triggers

Reopen a paper's research rather than polish it when any of the following occurs:

- a central gate is unreachable in either direction;
- a label, answer, terminal or gold decision is recoverable from candidate-visible
  construction cues;
- a comparator is not matched on information, compute or opportunity;
- a promoted terminal is absent from the executable path;
- a citation is metadata-only, contradicted, retracted or materially narrower;
- manuscript, claim ledger, receipt and executable semantics disagree;
- clean replay cannot separate host/capability failure from scientific outcome;
- the putative paper has no standalone residual after donor subtraction.

## Frozen implementation hypothesis

Publication closure is a fail-closed conjunction, not a prose label. A paper may
advance only when its independent TeX/build surface, claim-evidence-citation map,
hostile construction audit, statistical/reporting audit, replay evidence and
scope boundary all pass. Failed conjuncts produce a bounded repair or a new
prospectively frozen research protocol. They never become positive by relabelling.

The smallest implementation is therefore additive first: generate a portfolio
audit against the fixed ref, freeze three mutually blind referee reports, run
clean builds and hostile harness diagnostics, then issue paper-local repairs.
Shared harness mechanics remain with PR #871 unless a separately justified defect
requires a coordinated successor.
