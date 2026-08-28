# Data, code, and reproducibility — ORION-08

## Data availability

Each mechanism study writes one immutable result artifact holding every arm's
outcome, the gate results, and a terminal string that states the study's scope.
Digests are SHA-256 over file bytes at the submitted revision.

| Artifact | Supports | SHA-256 |
|---|---|---|
| `research/extensions/orion-q/nlanes/N4_A_UNKNOWN_VOI_RESULTS.json` | Headline positive: 300 paired episodes; typed 3.291, uniform-prior 2.180, oracle 4.612, blind commitment -13.619 at 19% success; all five gates pass | `942582f0c1dd89e59ab02ad66556df1f18e61629c47245981e9296f914dc0197` |
| `research/extensions/orion-q/nlanes/N1_C_COSTLY_VERIFICATION_RESULTS.json` | Retained negative: an ideal allocator given the same typed facts matches the candidate exactly at 0.9866, closing the allocation-policy residual | `f9579b01fa97bc0c550ebb2ae108db19c91bffbcf6f3cd0c46cf1edab138b613` |
| `research/extensions/orion-q/nlanes/N2_F5B_DONOR_COMPARISON_RESULTS.json` | Retained donor tie: candidate and donor both 0.9948 on the original world; only the misspecified world separates them, 0.9844 against 0.9531 | `8befbaad00885bcc23935cf01f4b58e7a72e659ee7d56af8d9be600ce90db530` |
| `papers/orion-08-typed-state/CLAIM_LEDGER_V3.md` | The claim ceiling this manuscript is written to | `24e2fad28a416c2df9244aeaee90e60022a122e88a11b838bbb2886069582a87` |

The full N1--N4 family, including every study not cited in the headline, is
committed under `research/extensions/orion-q/nlanes/`.

## Code availability

Generating modules sit beside their results under
`research/extensions/orion-q/nlanes/`, and the frozen protocols under
`development/orion-q-nlane-closure/`. Each family runs from a frozen seed with
a deterministic decision path, so a rerun reproduces the recorded arm values
exactly rather than approximately.

## Reproducibility statement

1. Verify the protocol-to-result binding for each family before rerunning
   anything.
2. Rerun the world and every registered arm, including the oracle and the
   hostile arm. The oracle upper bound and the punishment of blind commitment
   are gates, not decoration: a run in which blind optimistic commitment is not
   driven to strongly negative utility has an invalid world, not a good result.
3. Recompute the matched comparator and the hostile validity gate for the
   headline family.
4. Verify the two negative families at equal prominence. The exact tie at
   0.9866 and the donor tie at 0.9948 are results, not noise.

## Scope of the digests

The digests bind exact-synthetic mechanism isolation. Every world is
constructed, and the terminals say so. Nothing here measures a deployed system,
and no result authorizes a promotion to a broader scientific claim, a novelty
claim, or a deployment decision.
