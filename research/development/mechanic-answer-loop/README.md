# Development packet — the mechanic-answer loop

**Status:** development question packet (pre-implementation). Prepared per `development/README.md`; implementation is deliberately deferred until the `shadow/self-orion-v0` → `shadow/mechanics-completion-v1` stack (PR #12/#14) lands, because it must build on that stack's cell/questioning/completion surface.

## Root development question

The mechanics program can already, without an LLM: decompose the workflow into cells, expose every unfilled dimension as a typed question, prioritize questions, and convert them into provider-neutral research tasks. What it cannot yet do is **hold an answer**. Today an answered question becomes a hand-written Python edit (`apply_default_*_plans` waves) authored by an LLM-led session. The loop

```text
plan questions -> research -> ANSWER -> apply to cell -> persist -> re-audit -> plan again
```

is open at ANSWER→apply→persist. Until it closes, ORION's self-development is LLM-led by construction, and Phase 2 (Shadow Self-ORION) cannot be demonstrated on the machine's own development.

**Question:** what typed, persistent, auditable representation turns an answered mechanic question into a mechanic-cell update — with evidence binding, without an LLM in the authority path, and safely under concurrent multi-agent development?

## Atomized development fibers

1. **ANSWER.STORAGE** — What is the persistent record of one dimension answer (`AnswerRecord`: cell id, dimension, contract payload, evidence refs, author lane, supersession id)? Append-only or mutable? Where does it live so that Git history is its provenance chain?
2. **ANSWER.MERGE** — What pure function maps `(cells, answer records) -> cells`? Which cell fields may a record set; when does a `provisional` marker clear; who may mint a `DimensionWaiver`? (Waivers are an authority operation, not a convenience.)
3. **ANSWER.EVIDENCE** — What distinguishes a step-specific contract from a re-labeled universal envelope? Minimum evidence classes per dimension (incumbent-RAKL citation, parent-domain source, hostile test, known-answer run).
4. **ANSWER.EXECUTOR** — Who answers? Routing per `capability_router`: mechanical recovery first (RAKL incumbents via `provenance/rakl/PAPER_SALVAGE_LEDGER.md` bindings, existing failure records, existing docs), semantic/LLM proposal only for the remainder, and always proposal-only.
5. **ANSWER.AUDIT_DELTA** — After merge, the re-audit must show a monotone open-question decrease **or** emit a typed residual explaining why not. Question count is workload, not target: the false-progress guard must reject count reductions produced by waiver-minting or envelope re-labeling.
6. **ANSWER.CONCURRENCY** — Multiple sessions answer concurrently. Single-writer-per-file lanes (`answers/<lane>/…`) with a deterministic, commutative reduce at load time; conflicting answers for the same (cell, dimension) become a typed contradiction residual, not a last-writer win.
7. **ANSWER.REOPEN** — An applied answer is staled when its cited evidence is superseded, its cell's parent contract changes, or a fresh hostile failure implicates the dimension. Staling reopens the question; it does not delete the record (negative/superseded history stays addressable).

## Incumbent recovery (done before this packet was written)

- **ORION (shadow stack):** `MechanicCell` + 27-dimension audit grammar, deterministic question generator, `MechanicResearchTask` bridge, completion layers, claim ledger SM-01..SM-06 (authority: implementation/CI only). The stack answers *question generation*; it does not answer *answer persistence* — `current_program_cells()` is rebuilt from code literals every call.
- **RAKL incumbents:** Paper III method-evolution lesson stores (episode→lesson typing with protected promotion); RSHEA P7 `serialize/restore_resumable_state` (content-hash tamper-evident persistence — the strongest incumbent for ANSWER.STORAGE); the audited RAKL defect class *ledger-staleness by omission* (frozen JSON inventories never written back) — which is precisely the failure mode ANSWER.STORAGE must not reproduce; and the RAKL SessionLedger persistence gap (state classes with no save/restore path), the same gap class this packet closes for mechanic cells.
- **Failure records:** `2026-08-git-object-ref-identity-mixup` (ref-precondition rule → ANSWER.CONCURRENCY), `2026-08-program-frontier-assumption`, `2026-08-pr12-*` (authority binding of experience → ANSWER.EVIDENCE).

## Parent-domain hypotheses (search obligations before freeze)

- **Event sourcing / append-only logs with projections** (databases): answers as immutable events, cells as derived projections — candidate resolution of the ledger-staleness class.
- **Incremental build systems** (staleness, dirty-bit propagation): candidate mechanics for ANSWER.REOPEN.
- **Knowledge-base population / slot filling with provenance** (information extraction): candidate evidence-class typing for ANSWER.EVIDENCE.
- **Desired-state reconciliation** (configuration management): candidate loop semantics for plan→apply→re-audit.
- **CRDTs / mergeable replicated data** (distributed systems): candidate commutative reduce for ANSWER.CONCURRENCY — likely overkill; the adversarial-omission challenge must test whether per-lane files + typed conflict residuals already suffice.

## False-saturation challenges

- Nearby-query flatness: reading only this repo's own docs would miss all five parent domains above; the packet is not saturated until each has been searched or explicitly waived.
- Waiver laundering: a loop that "closes" questions by minting waivers would show perfect audit deltas while learning nothing — ANSWER.AUDIT_DELTA must treat waiver-driven decreases as a separate, gated category.
- Envelope laundering: copying a universal envelope's text into a cell-specific field without new evidence must not clear the provisional marker.

## Reopen triggers

- PR #12/#14 land with a different cell/plan surface than this packet assumes → re-audit fibers 1–2 against the merged code.
- The owning sessions introduce their own persistence design → merge or supersede this packet explicitly (no parallel competing stores).
- Any hostile test shows the reduce is order-sensitive → fiber 6 reopens as blocking.

## Frozen implementation hypothesis (V0)

Append-only JSONL answer ledger under `research/development/mechanic-answer-loop/answers/<lane>/`, one file per lane per cell; a pure `apply_answer_records(cells, records)` reducer in a new `orion.mechanics.answers` module (no edits to existing modules; registry wiring queued for the owning wave per `AGENTS.md`); deterministic load order (cell id, dimension, record id); conflicting (cell, dimension) pairs emit a typed contradiction residual; audit-delta check asserts monotone-or-residual with waiver-driven decreases reported separately; known-answer + hostile tests (order permutation, conflict injection, waiver-laundering attempt, envelope-laundering attempt). LLM sessions participate only by appending records through ordinary lane PRs.

### Authority hardening after hostile review

The first merged reducer failed its own waiver-laundering and evidence-binding
challenges; see `research/failures/2026-08-answer-authority-laundering/`.
Hardened V0 therefore has **no active waiver application path**. A waiver record
is retained as a proposal but emits `UNAUTHORIZED_WAIVER` and cannot reduce the
frontier until a protected subject-bound waiver attestor exists.

Content answers now require an exact binding to a resolved canonical
`EvidenceRecord`; a non-empty citation string is not evidence. Supersession is
accepted only when every record in the coordinate forms one complete linear
chain. These repairs establish answer-application conformance only. They do not
make an answered mechanic executable, empirically supported or scientifically
authoritative; those transitions belong to the step-verification lifecycle.

Implementation begins only after the shadow stack merges and this hypothesis is re-audited against the merged surface.
