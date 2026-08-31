from __future__ import annotations

import json
from pathlib import Path
import shutil
import tempfile
import unittest
import zipfile

from verify_release import (
    REVIEW_PROVENANCE,
    REVIEW_RECEIPT,
    VerificationError,
    sha256_file,
    verify_review_receipt_disposition,
)


class ReviewReceiptDispositionTests(unittest.TestCase):
    def make_fixture(self, root: Path) -> tuple[Path, Path, Path, Path]:
        repo = root / "repo"
        paper = repo / "papers" / "orion-03-typed-merge-falsification"
        closure = paper / "publication_closure_20260831"
        package = paper / "journal_package_final"
        submission = package / "submission"
        closure.mkdir(parents=True)
        submission.mkdir(parents=True)
        receipt = closure / REVIEW_RECEIPT
        receipt.write_text(
            json.dumps(
                {
                    "candidate": {
                        "directory": (
                            "papers/orion-03-typed-merge-falsification/"
                            "publication_closure_20260831/candidate_package"
                        )
                    }
                }
            )
            + "\n",
            encoding="utf-8",
        )
        (package / REVIEW_PROVENANCE).write_text(
            json.dumps(
                {
                    "disposition": "REPOSITORY_SIDE_PROVENANCE__EXCLUDED_FROM_UPLOAD_SET",
                    "repository_relative_path": receipt.relative_to(repo).as_posix(),
                    "sha256": sha256_file(receipt),
                    "byte_count": receipt.stat().st_size,
                }
            )
            + "\n",
            encoding="utf-8",
        )
        return repo, closure, package, submission

    def test_external_receipt_with_sanitized_provenance_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            repo, closure, package, submission = self.make_fixture(Path(temp_name))
            verify_review_receipt_disposition(
                repo=repo, closure=closure, package=package, submission=submission
            )

    def test_exact_receipt_copy_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            repo, closure, package, submission = self.make_fixture(Path(temp_name))
            shutil.copy2(closure / REVIEW_RECEIPT, package / REVIEW_RECEIPT)
            with self.assertRaisesRegex(VerificationError, "receipt leaked"):
                verify_review_receipt_disposition(
                    repo=repo, closure=closure, package=package, submission=submission
                )

    def test_repository_receipt_with_absolute_local_path_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            repo, closure, package, submission = self.make_fixture(Path(temp_name))
            receipt = closure / REVIEW_RECEIPT
            receipt.write_text(
                json.dumps(
                    {"candidate": {"directory": "/Users/reviewer/private/candidate"}}
                )
                + "\n",
                encoding="utf-8",
            )
            provenance_path = package / REVIEW_PROVENANCE
            provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
            provenance["sha256"] = sha256_file(receipt)
            provenance["byte_count"] = receipt.stat().st_size
            provenance_path.write_text(
                json.dumps(provenance) + "\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(
                VerificationError, "absolute local path leaked into repository receipt"
            ):
                verify_review_receipt_disposition(
                    repo=repo, closure=closure, package=package, submission=submission
                )

    def test_archive_member_with_absolute_local_path_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            repo, closure, package, submission = self.make_fixture(Path(temp_name))
            archive_path = submission / "source.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("review.json", '{"directory":"/Users/reviewer/private"}\n')
            with self.assertRaisesRegex(VerificationError, "absolute local path leaked into archive"):
                verify_review_receipt_disposition(
                    repo=repo, closure=closure, package=package, submission=submission
                )


if __name__ == "__main__":
    unittest.main()
