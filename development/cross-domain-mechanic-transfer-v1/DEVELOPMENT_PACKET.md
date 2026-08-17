# Cross-domain mechanic-contract transfer — development packet (#286)

**Development question:** Can ORION freeze a content-addressed mechanic-contract transfer object, independent source/target family slots, and a fail-closed applicability receipt that refuses assumption mismatch — without treating the #136 local transfer substrate, toy ablations, or surface similarity as scientific cross-domain transfer?

**Base subject:** `origin/main` at packet authoring (`cfeff0b` lineage; exact HEAD recorded at merge).

**Tracking issue:** #286. Parent #284. Engineering substrate #136.

## Atomic development fibres

1. Bound existing `orion.transfer` / V2 tests as `LOCAL_ENGINEERING_ONLY`, not scientific transfer.
2. Freeze a versioned transfer-object schema: problem signature, I/O, obligations, assumptions, failure modes, verification hooks, authority boundaries, hashes; reject hidden target labels.
3. Freeze a benchmark design with independent source and target family slots (debugging, retrieval/stopping, semantic mapping, protected verification) plus positive/near-miss/negative/partial pair kinds and hostile falsifiers, with `outcomes_accessed=false`.
4. Implement an evidence-bound transfer receipt/selector that refuses assumption mismatch, omitted preconditions, stale evidence, unavailable tools, and corrupted falsifiers, while retaining every harmful candidate.
5. Keep surface-similarity selection as a baseline that cannot admit.
6. Known-answer toy: transferred mechanic gain disappears under ablation; NL insight is not authority.
7. Literature matrix from local docs/existing citations only, dispositions ADOPT/ADAPT/COMPOSE/DEFER/REJECT, two consecutive flat rounds.

## Incumbent mechanics and negative history

- V1/V2 transfer already fail-closes on false assumptions and unknown falsifiers, and treats structural score as non-authoritative (`src/orion/transfer/types.py`). #286 must not relabel that substrate as scientific transfer.
- Memory-transfer / skill-transfer / analogical-retrieval 2026 work already occupies high-level reuse and documents negative transfer from low-level traces (issue #286; FAR_DOMAIN_AUDIT).
- Harmful skill admission and held-out contamination are parent pressure (Verifier-as-Gatekeeper, Ratchet, PAST-Bench).

## Saturation assessment

Knowledge saturation for this *engineering freeze* is bounded by: issue #286 seeds, `FAR_DOMAIN_AUDIT_2026-08-16.md`, P5 nearest-work closure, P3 transport/obstruction audit, CROSS.EXPERIENCE, and the existing transfer types/receipts. No live arXiv API.

Search-universe saturation: the ten issue search terms are bound to local rows. Two consecutive local rounds added no new transfer-object field, applicability test, negative-transfer control, or benchmark family.

Formulation saturation: the bounded question is freeze-and-gate, not “does mechanic transfer work on held-out scientific targets?” That latter question remains `CANNOT_CHECK` until independent target authority exists.

## Challenge to the saturation basis

Saturation would be false if a local citation already supplied evidence-bound mechanic-contract transfer with authority boundaries (none found), if the frozen schema smuggled target labels, if surface similarity could admit, or if toy ablation were reported as held-out science.

## Miss hypotheses

1. Treating #136 green tests as cross-domain transfer evidence.
2. Admitting near-miss pairs because terminology overlaps.
3. Dropping refused candidates instead of retaining them.
4. Executing outcomes before freezing pairs/representations.
5. Claiming novelty that is actually memory/skill/analogy transfer.

## Frozen implementation hypothesis

> If transfer objects are content-addressed contracts with explicit assumptions, falsifiers and authority boundaries, and if admission is an evidence-bound receipt that cannot be overridden by surface similarity, then negative-transfer hostiles can be refused in a known-answer fixture without creating scientific transfer authority.

Local engineering hypothesis only.

## Frozen hostile tests

- assumption mismatch refuses even when surface similarity is high;
- omitted precondition, stale evidence, unavailable tool, corrupted falsifier refuse and are retained;
- different terms / same mechanic is not blocked by low surface similarity;
- surface-similarity selector never admits;
- ablating the transferred mechanic removes toy gain;
- NL insight is not transfer authority;
- schema rejects hidden target labels;
- benchmark payload has no outcome fields.

## Reopen triggers

Reopen if a receipt can admit on similarity alone, if source slots embed target slot identities, if literature rows are fetched live against the freeze, or if any scientific terminal other than `CANNOT_CHECK` is claimed from this packet.
