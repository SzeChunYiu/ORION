# Scientific novelty certificates (issue #287)

`ScientificNoveltyCertificate.v1` treats novelty as a bounded evidence object. An LLM novelty score may be recorded; it cannot set the final state.

## Authority

Final state is computed only from:

1. executed hostile already-solved route;
2. material source accessibility;
3. seven-route search saturation with two consecutive empty rounds;
4. overlap / absorption of the claimed mechanism;
5. whether the original claim shrank to a residual;
6. implementation evidence and an executed discriminator (required for `NOVELTY_SUPPORTED` only).

`CANNOT_CHECK` is mandatory when the hostile route is missing/unexecuted, required routes are incomplete, saturation is open, or inaccessible sources could absorb the claim.

Allowed states: `NOVELTY_SUPPORTED`, `NOVELTY_NARROWED`, `ALREADY_SOLVED`, `CANNOT_CHECK`.

This landing does **not** claim `NOVELTY_CERTIFICATE_SUPPORTED`. RINoBench / axiomatic-benchmark / held-out mechanism evaluation were not executed.

## Search saturation

Required routes, in order of the issue:

1. exact term
2. synonyms / function-only
3. problem decomposition
4. parent discipline / history
5. benchmark / implementation repositories
6. cited-by / related work
7. hostile “assume this is already solved — find it”

Stop only after two consecutive rounds that do not change the residual or its disposition, and only after all seven routes have been run.

No live arXiv API was used. Self-application search snapshots reuse the programme nearest-work audits already in-tree (`research/paper-programme-v1/`, `research/paper-programme-v2/NEAREST_WORK_V2_AUDIT_2026-08-16.md`).

## 2026-08-17 self-application

| Claim | Issue | Final state | Residual |
|---|---|---|---|
| P1 causal epistemic responsibility | #278 | `CANNOT_CHECK` | Who&When Pro / REFLECT / CAR full texts unread and could absorb the licensing residual |
| P2 censored stopping authority | #279 | `CANNOT_CHECK` | External Wide unexecuted; Super Research unread |
| P3 obstruction certificates | #280 | `NOVELTY_NARROWED` | Standalone obstruction absorbed (sheaf); typed-coordinate non-merge remains |
| P4 protected acquisition | #281 | `NOVELTY_NARROWED` | Proof-carrying/defeaters absorbed; acquisition-under-lattice remains untested |
| P5 non-compensatory self-improvement | #282 | `NOVELTY_NARROWED` | DGM/ADIAS/PACE components absorbed; four-stage lattice is the composition residual |
| Global-positive admission | #285 | `CANNOT_CHECK` | EvoDrive / compounding-optimizer full texts unread |
| Mechanic-cell transfer | #286 | `CANNOT_CHECK` | MTL / AGENTCL full texts unread |

Adversarial fixtures: new terminology for an old mechanism → `ALREADY_SOLVED`; composition of knowns → `NOVELTY_NARROWED`; broad claim / narrow residual → `NOVELTY_NARROWED`.

Hashes live in `self-application/INDEX.json`.
