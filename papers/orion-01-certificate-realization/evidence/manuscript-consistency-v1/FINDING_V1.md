# ORION-01 manuscript internal consistency after R0/name repairs

Discharges the #1701 box "Confirm bounded theorem/proof manuscript remains
internally correct after all R0/name repairs."

## Result: both manuscripts clean

| manuscript | numbered results | references | dangling | numbering gaps |
|---|---|---|---|---|
| `theory-A-MANUSCRIPT_V2.md` | Theorem 1, Corollary 2, Lemma 3, Theorem 4 | 4 | **none** | **none** |
| `theory-B-MANUSCRIPT_V2.md` | Theorem 1, Corollary 2, Theorem 3 | 3 | **none** | **none** |

Every referenced result is defined, and the numbering is contiguous from 1 in
both files. R0 renamed identifiers across the repository; a rename that missed a
cross-reference would surface here as a dangling reference, and none is present.

## The checker's own first result was a false positive

Reported for the record, because it is the more useful half.

The first version checked numbering gaps **per kind**. It reported
`theory-B: Theorem defined [1,3], missing [2]` — an apparently real defect of
exactly the shape an R0 repair would leave behind.

It is not a defect. Both manuscripts number results in **one shared sequence
across kinds**: theory-A runs Theorem 1 -> Corollary 2 -> Lemma 3 -> Theorem 4,
and theory-B runs Theorem 1 -> Corollary 2 -> Theorem 3. There is no Theorem 2
because position 2 is a Corollary. The per-kind rule was wrong; the manuscripts
were right.

The rule now checks the union across kinds, and the false positive is gone. The
episode is recorded rather than quietly fixed because a checker that alarms on
its first contact with real data is the failure mode that gets checkers switched
off — and because the manuscripts' numbering convention is now documented.

## Positive control

A synthetic file defining only `Theorem 1` while citing `Theorem 9` is fed to
the checker on every run. It must report `["Theorem 9"]` as dangling, and does.
Without this, "no dangling references" would be indistinguishable from a checker
whose regex silently matches nothing.

## Scope

- Structural consistency: cross-references and numbering. It does **not** verify
  that the proofs are correct — Lemma 3 is separately verified by exhaustive
  enumeration in `evidence/independent-proof-checker-v1/`.
- Covers the two `theory-*-MANUSCRIPT_V2.md` files, not the claim ledgers or
  audits.
- Symbol-level rename damage is only partially reachable this way; a rename
  applied *consistently but wrongly* is invisible to any purely internal check.

`scientific_authority_delta: NONE`.

**Terminal:** `MANUSCRIPTS_INTERNALLY_CONSISTENT__NO_DANGLING_REFS__NO_NUMBERING_GAPS`
