# The all-25 freeze cannot be re-taken yet: two papers cite provenance that no longer exists

**Date:** 2026-09-02 · **Scientific authority delta:** `NONE`. No theorem, bound, count or
terminal changes. This reports what a re-take found and refuses to emit a freeze around it.

## Why a re-take, not a repair

`check_all25_bounded_science_freeze_v2.py` reports `FREEZE_INVALID: freeze commit parent is
not the declared content base`. The valid freeze commit is `fe5da5332`, whose parent **is**
the declared `content_base` `5ba3e6ef6992` — but it sits on
`origin/codex/all25-bounded-freeze-v2-20260828`, **639 commits behind main and never merged**.

Re-anchoring is not available, because the freeze is substantively stale:

| check | result |
|---|---|
| papers whose canonical tree still matches `final_tree_oid` | **0 of 25** |
| immutable V1 receipts unchanged | **23 of 23** |
| identity registry unchanged | yes |

The audited evidence base held perfectly; only the working content moved. That makes a V3
re-take legitimate rather than a cover-up — so `generate_all25_bounded_science_freeze_v3.py`
was written to take one.

## What the generator found, and why it refuses

**Two of 16 source result commits no longer exist** — absent locally and refused by the remote
as `not our ref`, against a control commit from the same record that resolves normally:

| paper | commit | state |
|---|---|---|
| ORION-15 | `b6b1e2734dc72048af4f9bed81122a3296a4d09d` | unreachable |
| ORION-19 | `6bc611ed1572a051d46c8e791b81c8163a1e1210` | unreachable |

No re-derivation can repair this. The V2 record validated in August because those commits were
reachable then; they are not now. **The generator refuses rather than emitting a freeze that
cites provenance nobody can fetch**, which would be a freeze weaker than no freeze.

This needs a disposition, not a re-run: recover the commits if they exist elsewhere, or record
the provenance as `CANNOT_CHECK` with the reason retained.

## What the generator does once that is dispositioned

- Carries over every **judgement** unchanged — boundary, `bounded_terminal`, donors,
  `forbidden_promotions`, retained adverse/null/`CANNOT_CHECK` records, `integration_state`,
  authority ceiling.
- Re-derives only what is **derived** — the content anchor and each paper's `final_tree_oid`.
- Leaves the **audited base fixed**, because its receipts were verified unchanged, so
  `baseline_tree_oid` stays as audited.
- Re-pins moved evidence blobs **and reports every one** (2 found, both the ORION-02 R24
  record), because a freeze that silently absorbs a changed negative is worse than none.
- **Refuses to re-pin a record whose `required_terminal_tokens` no longer appear** — the bytes
  may move, the meaning may not. ORION-02's tokens
  `C_R24_ARM_CONDITIONAL_CERTIFICATE_INVALID` and `20/44` were both verified still present.

## Note on the one evidence change found

ORION-02's retained adverse record moved `2fbbf8b54c → 1f7d578d40`. Reviewed: it is an
append-only correction that **retracts a false `CANNOT_CHECK`**, supplying the deterministic
reconstruction (20/44 vs 14/44, paired contingency (14, 6, 0, 24), exact two-sided McNemar
`p = 0.03125`), preserves the retracted reading as historical provenance, and states that both
policies still exceed the registered 0.10 maximum and **remain adverse**. The negative was
sharpened, not weakened.

Validated against the checker's own validators: `validate_manifest_shape` **PASS**,
`validate_checker_template_binding` **PASS**.
