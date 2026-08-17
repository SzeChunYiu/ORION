# P2 cover letter — draft

**Status:** draft for the recommended venue (TMLR; see `JOURNAL_SCOPE_CHECK.md`).
Every factual statement below is a row in `protocol/CLAIM_LEDGER_V1.json` and is
verified by `scripts/check_claim_ledger.py --check`. Nothing here claims more
than that checker will allow.

**Author/affiliation lines are deliberately absent.** TMLR review is double-blind
(<https://jmlr.org/tmlr/author-guide.html>, fetched 2026-08-17); add author
identity only if the venue changes to one that expects it in the letter. The
manuscript itself still carries the placeholder `\author{Working framework
draft}` and has not been put on the TMLR anonymised template.

---

## Draft text

Dear Editors,

We submit *Open-World Scientific Knowledge Discovery with Fail-Closed Coverage
Stopping* for consideration.

The paper addresses a control problem that sits around retrieval rather than
inside it. When a scientific-discovery agent searches heterogeneously, four
decisions determine whether its output can be trusted: whether two search routes
are genuinely independent evidence channels, what has already been read *for the
current question and content version*, when a single route may stop, and when
task-level coverage must remain open. We formalise these as typed states with one
governing rule — a route stop never certifies task-level completeness — and we
show that the rule is testable.

Our contribution is a mechanism and its measurement, not a performance result.
We state the boundary plainly, because it determines how the paper should be
read:

- The completed experiment runs on a **fully synthetic, frozen, complete-gold
  controlled index**. That design is deliberate: a complete denominator is what
  makes missed relevant material and premature closure *observable at all*. It is
  also what makes the numbers unsuitable as an estimate of real retrieval
  difficulty. The authored routes, public probe vocabulary and easy screening text
  are all easier than the open web.
- The campaign's authority is **`DESCRIPTIVE_ONLY`**. Our pre-registered
  statistical plan set a minimum task count for its lowest inferential tier
  before any outcome was inspected, and this suite is below it. We therefore
  report no confidence interval, *p*-value or superiority decision from it. The
  deterministic repeat seeds demonstrate harness stability; they do not increase
  the statistical unit, and we do not treat them as if they did.
- Negative and null results are reported as such. Removing the question
  coordinate from the read ledger changes reread behaviour but leaves aggregate
  recall unchanged; removing the unavailable-route open state changes closure
  semantics while leaving aggregate recall numerically unchanged. Both are
  retained as nulls rather than converted into a stronger claim. The route-stop
  oracle replay publishes both the false-positive **and** the false-negative
  table, including a null false-negative count.
- **Externally supported superiority over strong baselines remains
  `CANNOT_CHECK`.** We have not archived an AutoResearchBench Wide or Deep system
  result; SAGE cannot be reproduced as published because neither its retrieval
  corpus nor its official evaluator is available, and we decline to substitute an
  unofficial stand-in; and the cost-bearing live-provider campaign has not been
  run. One external evaluation *is* complete — a credential-free retrieval and
  screening probe scored by the pinned official MetaSyn ID-only evaluator over
  all released test reviews — but its candidate is a keyless lexical retriever
  with deterministic screening, **not** the matched multi-provider system, so it
  is not evidence of ORION's external superiority and we do not present it as
  such.

Four limits deserve the editors' attention up front:

1. **Synthetic controlled index.** The headline mechanism evidence comes from an
   authored world, not from real literature.
2. **External families under declared deviations.** Where an official artifact was
   unavailable, we recorded the deviation rather than manufacturing an
   "official" substitute. Two upstream families are additionally
   redistribution-blocked because no licence could be found in their pinned
   repositories, so they cannot be included in any archive we publish.
3. **One inherited unseeded upstream metric.** In the AutoResearchBench Wide
   evaluator, the exact IoU, recall and precision paths were bit-identical across
   repeated runs, but the sampled `max_iou_at_k` family is unseeded Monte-Carlo
   upstream. We inherit that nondeterminism; we did not fix it, and we do not
   report that metric family as reproducible.
4. **Live-provider mutability.** Scholarly providers are mutable, metered and
   sometimes unavailable. Our capture layer retains raw request and response
   bytes, timestamps and typed transport failures precisely so that such evidence
   is archived rather than re-derived — but provider unavailability is recorded as
   unavailability, never as evidence of absence.

What we offer in exchange for these limits is unusual auditability. Every
result-bearing sentence in the abstract, Results and conclusion is bound by
identifier to an immutable artifact and key, and a committed checker fails the
build when a claim drifts from its evidence, when a number in the prose no longer
matches the archived value it cites, or when a sentence asserts an outcome that
no archived artifact supports. The complete offline record set is bound by
SHA-256 and regenerates from committed data and code with no network access and
no third-party credentials; an independent clean continuous-integration job
rebuilds it and refuses drift.

We believe the paper is a good fit for a venue that evaluates whether claims are
supported by the evidence presented rather than whether the contribution is
large. Our claims are deliberately narrow, and we would rather they were
assessed as narrow than as more than they are.

We confirm that the manuscript is not under consideration elsewhere, and we
declare no competing interests.

Sincerely,

The authors

---

## Rules for editing this letter

- **No superlative claims.** "First", "state-of-the-art", "significantly
  outperforms" are unsupportable today and must not appear.
- **No invented endorsements** and **no suggested reviewers** — we have no
  grounded basis for naming any, and inventing one would be fabrication.
- Any number added here must exist as a bound row in
  `protocol/CLAIM_LEDGER_V1.json`. The current draft states no numeric result on
  purpose: the letter's job is scope, and the numbers live in the paper where the
  checker guards them.
- Re-run `scripts/check_claim_ledger.py --check` after any manuscript change
  before re-sending this letter, so the letter's scope statements cannot outlive
  the evidence.
- Two open manuscript defects (`P2-D01`, `P2-D02`) currently assert that MetaSyn
  is unexecuted, contradicting the archived probe. **Fix those before sending**,
  or the letter's fourth bullet will contradict the submitted paper.
