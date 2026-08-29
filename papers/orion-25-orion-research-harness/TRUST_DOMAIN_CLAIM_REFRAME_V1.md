# ORION-25 — the claim the evidence now supports

**Status:** `REFRAME_READY__NOT_APPLIED_TO_MANUSCRIPT`
**Authority:** `scientific_authority_delta = NONE`

The measurements in `experiments/execution-integrity-v1/` change what this paper should
claim. This records the reframe. It is **not** applied to `MANUSCRIPT.md`, for the reason
in the last section.

## What was measured

| experiment | result |
|---|---|
| H1 — detection vs chain length `k` (d=1) | **flat**: 1.000 at k=1, 2, 3 |
| H2 — false promotion vs trust domains `d` (k=3, 1 domain compromised) | **1.00 → 0.00 → 0.00** for d = 1, 2, 3 |
| false promotion under artifact corruption | 0/6 |
| false rejection under semantics-preserving re-encoding | 0/6 |
| host/process faults | stale artifact accepted after mid-run kill |
| cross-site replay | scientific fields identical across two interpreters |
| overhead | 111.6 µs per link, 13.8×, 1.39× bytes |

## The claim that follows

> Integrity strength in this construction comes from the number of **independent trust
> domains**, not from attestation **chain length**. Adding links to a chain whose keys all
> derive from one seed does not increase resistance to compromise, because a single
> compromise yields every key. Separating key custody does.

The current manuscript frames the contribution around chain composition. On the evidence
that is the wrong axis: `k` is measured to buy nothing, and `d` is measured to buy the
entire difference between total forgeability and none.

## Three specific corrections the manuscript needs

1. **The configuration is d = 1, and the paper should say so.** Every role key derives
   from `sha256(b"P15-…-KEY-" + role + cid)`. Anyone who can run the runner derives every
   key. All `k` roles therefore share one trust domain regardless of `k`.

2. **The recorded full-compromise boundary is not a caveat, it is the d = 1 row.**
   `A-COMPROMISE-FULL chain_as_science_false_promotions = 6` follows arithmetically from
   single-domain custody and disappears at d = 2. It should be presented as a measured
   property of the configuration rather than as an unexplained limit.

3. **"Execution integrity" overstates what is attested.** The checker verifies an
   *artifact*, not a *run*: after the runner is killed mid-execution, a stale artifact
   still verifies green. Content integrity is attested; **liveness is not**. That
   boundary should be in the claim, not discovered by a reader.

## What must not be claimed

- No general trust-domain theorem. d = 1 → 2 is measured on n = 4 receipts under
  single-domain compromise; d = 2 vs d = 3 is flat only because one compromise already
  fails to forge.
- k = 5 is untested and stays untested. H1 makes it uninteresting rather than blocked:
  it would re-probe a mechanism already measured flat.
- Nothing here licenses a security claim beyond the modelled threat.

## Why this is not applied to `MANUSCRIPT.md`

`MANUSCRIPT.md`, `CLAIM_LEDGER_V1.md` and `CLAIM_EVIDENCE_LEDGER_V1.md` are all bound by
digest in `papers/orion-25-orion-research-harness/SHA256SUMS`. Editing any of them makes
that manifest stop describing its own files, which
`tests/unit/programme/test_content_binding_drift_ratchet.py` refuses:

> Reconcile the paper — **do not regenerate its digests to match the new bytes**, and do
> not add it to the baseline.

There is no sanctioned regeneration path for a paper-level `SHA256SUMS`.
`src/orion/programme/content_binding_coverage.py` surveys and asserts; it has no writer.
`check_journal_package.py --write-hashes` covers only papers in the journal-package
registry, and ORION-25 is not one.

So the correction is recorded here, where it is unbound, and the manuscript edit waits
on the decision described in the tracker issue. This is the same structure that defers
ORION-01's sibling decoupling, ORION-02's language correction and ORION-20's claim
narrowing.
