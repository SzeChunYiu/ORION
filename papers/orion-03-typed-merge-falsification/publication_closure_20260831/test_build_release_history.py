from __future__ import annotations

import hashlib
from pathlib import Path
import subprocess
import tempfile
import unittest

from build_integrity_ledger import reviewed_manuscript_fingerprint
from build_release import historical_file_hash
from verify_release import VerificationError, verify_historical_candidate_hashes


class HistoricalFileHashTests(unittest.TestCase):
    def test_frozen_revision_does_not_rebind_after_head_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            repo = Path(temp_name)
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            subprocess.run(
                ["git", "config", "user.email", "test@example.invalid"],
                cwd=repo,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Test"], cwd=repo, check=True
            )
            path = repo / "paper.md"
            path.write_bytes(b"historical bytes\n")
            subprocess.run(["git", "add", "paper.md"], cwd=repo, check=True)
            subprocess.run(["git", "commit", "-qm", "historical"], cwd=repo, check=True)
            frozen = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=repo,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            ).stdout.strip()

            path.write_bytes(b"current bytes\n")
            subprocess.run(["git", "commit", "-qam", "current"], cwd=repo, check=True)

            self.assertEqual(
                historical_file_hash(repo, frozen, "paper.md"),
                hashlib.sha256(b"historical bytes\n").hexdigest(),
            )

    def test_missing_historical_object_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            repo = Path(temp_name)
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            subprocess.run(
                ["git", "config", "user.email", "test@example.invalid"],
                cwd=repo,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Test"], cwd=repo, check=True
            )
            (repo / "paper.md").write_text("historical\n", encoding="utf-8")
            subprocess.run(["git", "add", "paper.md"], cwd=repo, check=True)
            subprocess.run(["git", "commit", "-qm", "historical"], cwd=repo, check=True)
            frozen = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=repo,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            ).stdout.strip()

            with self.assertRaisesRegex(RuntimeError, "missing historical object"):
                historical_file_hash(repo, frozen, "missing.md")


class HistoricalCandidateManifestTests(unittest.TestCase):
    def test_rebound_historical_candidate_hash_is_rejected(self) -> None:
        manifest = {
            "manuscript_candidates": [
                {
                    "manuscript_id": "ORION-03-BASE-V3-SOURCE",
                    "sha256": (
                        "sha256:"
                        "7181bd6d64c375a29fc2d037cfa5a03f67e6dc69d6b32d0af95961ce410fa1ee"
                    ),
                }
            ]
        }
        with self.assertRaisesRegex(
            VerificationError, "historical manuscript candidate hash mismatch"
        ):
            verify_historical_candidate_hashes(manifest)


class IndependentReviewFingerprintTests(unittest.TestCase):
    def test_fingerprint_is_copied_from_frozen_reviewer_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            manuscript = Path(temp_name) / "paper.pdf"
            manuscript.write_bytes(b"reviewed bytes\n")
            digest = hashlib.sha256(manuscript.read_bytes()).hexdigest()
            review = {
                "candidate": {
                    "immutable_objects": {"reader_pdf": {"sha256": digest}}
                }
            }

            self.assertEqual(
                reviewed_manuscript_fingerprint(review, manuscript),
                f"sha256:{digest}",
            )

    def test_reviewer_fingerprint_is_not_rebound_to_later_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            manuscript = Path(temp_name) / "paper.pdf"
            manuscript.write_bytes(b"later bytes\n")
            review = {
                "candidate": {
                    "immutable_objects": {"reader_pdf": {"sha256": "1" * 64}}
                }
            }

            with self.assertRaisesRegex(ValueError, "PDF binding mismatch"):
                reviewed_manuscript_fingerprint(review, manuscript)


if __name__ == "__main__":
    unittest.main()
