# ORION-17 — why the P7 substitute-campaign seal fails, and what that does not mean

`check_p7_substitute_campaign_v1.py` fails three checks on current `main`:

```
FAIL custodian signature verifies
FAIL sealed facts digest matches
FAIL sealed manifest binds the frozen protocol bytes
```

This matters more than a typical checker failure: the #1701 gap-closure packet names
ORION-17 as the **single** integration-stage top-tier candidate, and a sealed
manifest that does not bind its protocol bytes is the first thing a reviewer tests.

## The seal is not broken by tampering. It was broken by a rename.

Measured on current `main`:

| binding | recorded | actual | |
|---|---|---|---|
| corpus | `sha256:3f5830c6…` | `sha256:3f5830c6…` | **matches** |
| sealed facts | `sha256:d9feb9c9…` | `sha256:11bb54da…` | mismatch |
| protocol bytes | `sha256:5376317b…` | `sha256:1eabb013…` | mismatch |

The **corpus** — the actual campaign data — still binds. Only the manifest's own
`facts` and the protocol document drifted.

Both files were last modified by a single commit: **`3a1a83178`,
"papers(R0): ORION-01…25 namespace unification — 2734 renames, 1706 rebinds"**.
That commit rewrote paper identifiers across the repository, including *inside*
these two sealed artifacts.

## Verified against the pre-rename bytes

Recovering both files from `3a1a83178^`, at their pre-rename path
`papers/paper-07-epistemic-navigation-open-worlds/evidence/independent/`:

```
payload_digest recorded : sha256:d9feb9c9b612dbfc10df09435058db823fc0726e0d6d4512847bd46ac850b133
facts recomputed        : sha256:d9feb9c9b612dbfc10df09435058db823fc0726e0d6d4512847bd46ac850b133   MATCH

protocol_sha256 recorded: sha256:5376317b35b073848535287c215985c206d312b31bf2c09fecc8eef985c1ebc9
protocol actual         : sha256:5376317b35b073848535287c215985c206d312b31bf2c09fecc8eef985c1ebc9   MATCH
```

**The seal was cryptographically valid before R0 and is arithmetically intact.** The
current failure is a rename artifact, not evidence of altered results.

## Scope

`P7_SUBSTITUTE_SEALED_LABELS_V1.json` is the only sealed-label artifact in `papers/`,
and R0 touched it together with `p7_substitute_custodian_v1.py`. No other paper's
seal is affected.

## What I did not do

I did not re-seal, re-sign, or edit either file to make the checker pass. Re-sealing
requires the custodian key, and rewriting a sealed payload to match a checker is
precisely the move sealing exists to prevent. The recorded digests are left exactly
as they are.

## The decision this leaves open

Two defensible routes, and the choice is the paper owner's:

1. **Re-seal under the custodian key** at the current (post-R0) bytes, producing a new
   signature over the renamed artifacts, with this diagnosis as the audit trail for
   why the digests changed.
2. **Pin the checker to the pre-R0 blobs** for these two files, so the original seal
   continues to verify against the bytes it was actually computed over.

Route 1 needs a key I do not have. Route 2 changes verification scope and should be an
explicit decision, not a silent path edit. Either way the finding stands: **the
campaign evidence is intact, and ORION-17's seal failure is not a science defect.**
