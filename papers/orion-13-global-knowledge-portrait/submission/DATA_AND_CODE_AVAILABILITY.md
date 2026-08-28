# Data, code, and reproducibility — ORION-13

The manuscript carries its own availability section, which now also holds the
source-provenance chain for the repair line. This file is the submission-side
summary.

## Data availability

| Artifact | Supports | SHA-256 |
|---|---|---|
| `CLAIM_LEDGER_V1.md` | The claim ceiling the manuscript is written to | `aba9ba39c7269636b19cbe75dff080dc04956de506e684e63686e315cf823f0f` |
| `CLAIM_LEDGER_MANUSCRIPT_MAP_V1.md` | Mapping from ledgered claims to manuscript locations | `ab42034112b63d8a790a6cf2ea0d83ce96397f9585e56d15c6d24fff78700a9c` |
| `SCOPED_PUBLICATION_TRACK_V1.md` | The scoped track, including the two identifiers held as not claimed | `a5728db6170bb4a04dca1fb8c955098424e65fe1c287ec6cd101f54fa56df03e` |
| `evidence/PEER_REVIEW_READY_SCOPED_V1.md` | The scoped readiness record and its condition | `40009441f8260640fa8935a3e03901074f25f61d14a9fcf2210b4f875ba1a6f0` |

Evidence bundles under `evidence/` carry their own `SHA256SUMS`, including the
public-reference protocol runs and the coordinate-obstruction study. Gold-track
licence manifests sit under `gold/`.

## Code availability

- `scripts/check_bounded_publication_track.py` — validates the bounded track;
  reports `P3_BOUNDED_PUBLICATION_TRACK: PASS`.
- `gold/check_oaei_track_license_manifest_v1.py` — validates the licence
  manifest for the ontology-matching track.
- `.github/workflows/p3-manuscript-audit.yml` — the repository CI job that
  compiles the manuscript, refuses unresolved or duplicate references, and
  audits the headline sections. It is the operative gate for this paper.

## Reproducibility statement

1. Run the bounded publication track checker and the licence manifest checker.
2. Compile the manuscript and confirm 45 pages with no undefined references and
   no overfull boxes.
3. Reproduce the repair line through the source-provenance list in the
   availability section: the pinned upstream commits, the unrepaired source
   digest, the patch digest, the repaired source digest, and the decoded
   artifact digest. The patch changes one attribute access; its digest is what
   makes that minimality checkable.
4. Reproduce the retained negatives. Coverage reaching its ceiling did not imply
   benefit, and the comparative outcome was no harm superiority. A reproduction
   that recovers the coverage result alone has not reproduced the paper.

## Scope of the digests

These digests bind evidence and provenance. They do not establish the broad
study, which the limitations state has not been executed, and they do not
convert the two identifiers held as not claimed into results.
