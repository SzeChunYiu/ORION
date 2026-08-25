# Threat model

What this system is defending, against whom, and where it does not defend.

The assets here are not credentials or user data. They are **claims and the
evidence that binds them**. The failure this design takes seriously is a
false claim surviving into a manuscript with a receipt that looks valid.

## What is protected

| Asset | Failure that matters |
|---|---|
| Frozen execution protocols | A protocol edited after seeing outcomes, so a gate moves to fit the result |
| Result receipts | A receipt claiming evidence it does not bind |
| Freeze chains (`sha256`) | An artifact changed while its receipt still reads valid |
| Adverse record | A negative or CANNOT_CHECK quietly dropped |
| Authority ledgers | A manuscript claiming an authority that has gone stale |

## Adversary model

The realistic adversary is **not** an external attacker. It is the ordinary
pressure of a research programme on itself: the wish for a result, applied
across many small decisions, none of which feels like misconduct.

Concretely:

1. **The optimistic author.** Re-runs a job until it passes, keeps the last
   run, and reports it. Countered by freezing protocols before outcomes and
   binding them by hash, so a re-run under a changed protocol is a
   *different job* rather than a better attempt at the same one.
2. **The vacuous test.** A check written so it cannot fail — a condition
   true by construction, a grid where only one outcome is reachable. This
   has occurred twice in this programme and both are recorded rather than
   quietly fixed. Countered by requiring non-vacuity evidence: both sides of
   a biconditional must occur in the grid, and every check names a negative
   fixture proving it rejects something.
3. **The flattering classifier.** A checker whose unmatched cases default to
   "fine". Countered by a distinct UNCLASSIFIED / CANNOT_CHECK outcome that
   is reported, never folded into PASS. This caught a real defect in the
   failure-ledger classifier.
4. **The silent drift.** A cosmetic edit to a file that some receipt binds
   by bytes. Countered by hash binding, which turns it into a loud failure.

## What is explicitly NOT defended

Stating these plainly matters more than a longer defended list, because a
threat model that omits its own boundary invites the reader to assume
coverage it does not have.

- **Independence.** Nothing here manufactures an independent adjudicator.
  Two implementations written in one programme are two implementations in
  one programme. Every receipt reads `external_validation: CANNOT_CHECK`
  and that is accurate, not pending.
- **A hostile author.** Every control assumes an author who wants to be
  caught making a mistake. Someone deliberately forging receipts and
  regenerating hashes would defeat all of it. The controls are against
  error and self-deception, not fraud.
- **Supply chain.** Dependency integrity is delegated to the package
  ecosystem. `THIRD_PARTY_NOTICES.md` records terms, not provenance
  attestation.
- **Secrets.** No credentials belong in this repository, and nothing here
  detects one if it is committed.
- **Availability.** Runs may be interrupted. Nothing guarantees a job
  completes; jobs that do not complete must terminate as CANNOT_CHECK
  rather than as a partial positive.
