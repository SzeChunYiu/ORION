# Why this directory's strings say `paper-07` in a repository that says `orion-17`

**Status:** `INCIDENT_DIAGNOSED__SEAL_RESTORED__REPRODUCIBLE_FROM_COMMITTED_CODE`

The P7 substitute campaign is a sealed-label study. Its evidentiary force comes from one
fact: the labels were committed, signed and hashed **before** any prediction existed. That
fact is carried by an Ed25519 signature over specific bytes. Change the bytes and the claim
is gone, whoever changed them and for whatever reason.

## What happened

`3a1a83178` — *"ORION-01…25 namespace unification — 2734 renames, 1706 rebinds"* — rewrote
identifiers across the repository. It reached inside two artifacts that a rename pass must
never touch:

- `P7_SUBSTITUTE_SEALED_LABELS_V1.json`, whose `facts` block is signed content. Three path
  strings were rewritten. The signature, public key, `payload_digest` and outcome were left
  as they were, so the payload no longer hashed to the digest that had been signed.
- `P7_SUBSTITUTE_CAMPAIGN_PROTOCOL_V1.md`, which the sealed manifest binds by sha256. Nine
  lines changed and the file grew from 8611 to 8670 bytes.

`check_p7_substitute_campaign_v1.py` then reported three failures — custodian signature,
sealed facts digest, and the protocol binding — which is precisely what it exists to do.

## It was sound before, and the record proves where it broke

| commit | date | sealed facts digest | protocol binding |
|---|---|---|---|
| `93cf5f412` | 2026-08-24 | matches | matches |
| `45957e01c` | 2026-08-26 | matches | matches |
| `3a1a83178` | 2026-08-27 | **broken** | **broken** |

Nothing about the study changed. A mechanical rewrite invalidated a cryptographic seal it
had no key to reissue.

## One rename was not cosmetic

Protocol line 53 documents the corpus generator as
`sha256("P7-SUBSTITUTE-V1|<domain>|<family>|<k>")`. The unification rewrote that literal to
`ORION-17-SUBSTITUTE-V1`, while `p7_substitute_custodian_v1.py` kept `SEED_STEM =
"P7-SUBSTITUTE-V1"` and the sealed manifest kept `"stem": "P7-SUBSTITUTE-V1"`.

Code, manifest and seal agreed with each other. Only the published recipe disagreed — so a
replicator following the protocol as written would have generated a **different corpus** and
failed to reproduce, with nothing in the repository to tell them why.

## What was done, and what was deliberately not done

**Restored** both artifacts byte-for-byte from `45957e01c`, the last commit at which the
seal verified. The checker passes, and its own `--self-test` still catches all six targeted
mutations, so this is not a green bought by weakening anything.

**Restored** the three path literals in the custodian so that re-running it reproduces the
sealed manifest exactly. Verified: the regenerated file is byte-identical to the committed
one. That was not true before this change, and it is the property that makes the seal
independently checkable rather than merely present.

**Not re-signed.** The custodian's key is deterministic and committed, so re-sealing over
the new bytes was mechanically available and would have produced a green check in one step.
It would also have destroyed the thing the seal exists to establish. A manifest signed
today, with the reveal long public, cannot witness that the labels were fixed before the
predictions — no matter how honest the person running the command. Re-sealing after a
reveal is not a repair. It is the failure the protocol was built to make impossible.

## The rule this establishes

Signed and hash-bound artifacts are **frozen bytes**, not text. Path strings inside them are
a historical record of where the bytes lived at seal time, not references — the custodian
and the independent checker both locate files relative to their own directory and compare
digests, never paths.

`papers/PAPER_ALIASES.md` maps `paper-07-epistemic-navigation-open-worlds` to
`orion-17-epistemic-navigation-open-worlds`, and that registry is where the current name
belongs. `paper_id: "P7"` inside the manifest was correctly left alone by the same pass;
the three paths should have been treated identically.

`tests/unit/papers/test_orion17_substitute_seal_integrity.py` now fails if any of this
regresses, so the next mechanical rewrite is caught in CI rather than by an audit sweep
weeks later.
