#!/usr/bin/env python3
"""Focused regressions for exact ZIP central-directory verification."""

from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
import unittest
import zipfile

from verify_release import VerificationError, verify_archive


class ExactArchiveInventoryTests(unittest.TestCase):
    def _record(self, archive: Path, member: str, data: bytes) -> dict[str, object]:
        return {
            "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
            "byte_count": archive.stat().st_size,
            "members": [{
                "member_path": member,
                "sha256": hashlib.sha256(data).hexdigest(),
                "byte_count": len(data),
            }],
        }

    def test_declared_file_only_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive = root / "ok.zip"
            expanded = root / "expanded"
            expanded.mkdir()
            data = b"evidence\n"
            (expanded / "declared.txt").write_bytes(data)
            with zipfile.ZipFile(archive, "w") as handle:
                handle.writestr("declared.txt", data)
            self.assertEqual(
                verify_archive(archive, self._record(archive, "declared.txt", data), expanded),
                1,
            )

    def test_payload_bearing_slash_entry_is_not_filtered(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive = root / "bad.zip"
            expanded = root / "expanded"
            expanded.mkdir()
            data = b"evidence\n"
            (expanded / "declared.txt").write_bytes(data)
            with zipfile.ZipFile(archive, "w") as handle:
                handle.writestr("declared.txt", data)
                info = zipfile.ZipInfo("undeclared/")
                info.external_attr = 0o100644 << 16
                handle.writestr(info, b"payload")
            with self.assertRaisesRegex(VerificationError, "ZIP membership mismatch"):
                verify_archive(archive, self._record(archive, "declared.txt", data), expanded)


if __name__ == "__main__":
    unittest.main()
