# P15 — Fail-Closed Research Execution

**Status:** `FRAMEWORK_COMPLETE / NO_PROTECTED_PAPER_RESULT`

P15 is an independent framework paper on receipt semantics, execution attribution,
failure/evidence separation and graded independence claims. Its neutral manuscript
title is *Fail-Closed Research Execution: Receipt Semantics and Independence
Contracts*.

## Scientific identity

The paper asks which predicates must be verified before an execution record can
support progressively stronger claims about attribution and independence. It
defines:

- a typed request/result receipt model;
- a fail-closed scientific-evidence admission predicate;
- six agreement levels, from deterministic structural agreement to scientific
  corroboration;
- twelve adversarial attack families covering substitution, replay, leakage,
  forgery, stale state, partial writes, false success and selective omission.

The central formal properties are contract consequences: a typed capability-failure
terminal cannot enter scientific evidence, and an independence label cannot exceed
its weakest verified gate.

## Current evidence ceiling

No protected paper result exists. Unit tests and deterministic source scans are
implementation-conformance evidence only. They do not establish general
reliability, evidence quality, authenticated executor independence, model
independence or scientific corroboration.

## Manuscript package

- `manuscript/main.tex` is the canonical source;
- `manuscript/chapters/` contains 10 complete, tracked TeX chapters;
- `manuscript/references.bib` contains the claim-local bibliography;
- `CLAIM_LEDGER_V1.md` records the evidence ceiling and promotion gates;
- `BUILD.md` records the portable build command and verified PDF digest.

The manuscript is system-neutral: internal programme names, repository paths,
operational terminals and codebase branding do not carry its scientific argument.

## Promotion gate

An empirical result requires a prospectively frozen hostile protocol, authenticated
and appropriately separated custody, complete attribution, released attack fixtures
and receipt sets, and independent adjudication. General reliability additionally
requires multiple prospectively sampled task or campaign units with task-level
uncertainty. Until those gates pass, the paper remains a framework without a
performance or superiority result.
