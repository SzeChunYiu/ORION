# Reproducibility contract

1. `SOURCE.md` and `CLAIM_LEDGER.md` must remain byte-identical to the canonical V3 files named in `SUBMISSION_MANIFEST.json`.
2. `verify_package.py` recomputes Git blob IDs and fails closed on source/ledger drift.
3. `build.sh` generates a fresh PDF, validates its structure and nonempty text extraction, records SHA-256 digests, and verifies the complete package.
4. The repository closeout workflow runs the `academic-paper-skills` manuscript-surface audit at pinned commit `a45568215d648e5d446a03980277d282b19e57d7` before rendering.
5. Filing-time formatting may change presentation only. Any scientific edit requires re-review of the canonical manuscript and claim ledger rather than an untracked package edit.
