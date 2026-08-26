# ORION-16 literature evidence

Retrieval records for the works ORION-16's related-work section names, mirroring
`papers/orion-12-open-world-scientific-discovery/evidence/literature/` and the
sibling directory under ORION-17.

## The gap this addresses, and how it differs from ORION-17's

ORION-17's §2.3 asserted what "planning research has long shown" and named **nobody**.
ORION-16 is in better shape: §2.1–2.5 name Doyle's TMS, de Kleer's ATMS, adaptive
functional programming and self-adjusting computation, dynamic epistemic logic
and AGM, separation and effect systems. The claims are attributed in prose.

What ORION-16 has is a **bibliography gap**, not an attribution gap: named works, zero
formal citations, no bibliography, and until now no retrieval records. A reader
can tell *which* work is meant but cannot check that ORION-16 read it, or which of
several same-author papers is intended — a live ambiguity for de Kleer, whose
1986 ATMS work spans multiple parts.

## Verdict vocabulary

`verdict` records **how the citation was checked**, never how good the work is.

| verdict | meaning |
|---|---|
| `VERIFIED` | the primary source was retrieved and its title/authors/venue read from it |
| `UNVERIFIED_SECONDARY` | identified from indexes or secondary sources; the primary source has **not** been read |

Only `VERIFIED` records may be cited in a manuscript. That rule is enforced by
`tests/unit/candidates/test_p7_literature_binding.py` for ORION-17 and extended to ORION-16
here.

**`UNVERIFIED_SECONDARY` is not a soft `VERIFIED`, and the strength of the
corroboration does not change that.** `doyle1979tms` carries four independent
corroborations — a BibTeX record, a ScienceDirect PII that structurally encodes
the same DOI, a handwritten annotation on a reprint scan, and the reprint's own
existence — and is still `UNVERIFIED_SECONDARY`, because the article's title page
was not read. The retrieved PDF turned out to be an image scan with no text
layer.

Keeping a strong lead and a weak lead in the same bucket is deliberate. A third
tier for "well corroborated" would become the tier everything lands in, and the
guard would stop meaning anything. The evidence is recorded in
`verdict_reason` instead, where it informs promotion without licensing citation.

## Current state

| key | verdict | named in |
|---|---|---|
| `doyle1979tms` | `UNVERIFIED_SECONDARY` | §2.1 dependency-directed revision |
| `dekleer1986atms` | `UNVERIFIED_SECONDARY` | §2.1 assumption sets, multiple environments |

Both are §2.1 only. §2.2 (self-adjusting computation), §2.3 (DEL/AGM), §2.4
(separation and effects) and §2.5 (authorization and provenance) name further
works and have no records yet. #334 stays open until they do.
