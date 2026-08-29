#!/usr/bin/env python3
"""Build deterministic anonymous source and review-supplement archives."""
from __future__ import annotations

import json
import os
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "submission_tmlr"
FIXED_TIME = (2026, 8, 28, 0, 0, 0)


def add_file(zf: ZipFile, source: Path, archive_name: str, executable: bool = False) -> None:
    info = ZipInfo(archive_name, date_time=FIXED_TIME)
    info.compress_type = ZIP_DEFLATED
    mode = 0o755 if executable else 0o644
    info.external_attr = (mode & 0xFFFF) << 16
    zf.writestr(info, source.read_bytes())


def write_archive(path: Path, members: list[tuple[Path, str, bool]]) -> None:
    path.unlink(missing_ok=True)
    with ZipFile(path, "w", compression=ZIP_DEFLATED, compresslevel=9) as zf:
        for source, archive_name, executable in sorted(members, key=lambda row: row[1]):
            add_file(zf, source, archive_name, executable)


source_members = [
    (PACKAGE / "main.tex", "manuscript.tex", False),
    (PACKAGE / "references.bib", "references.bib", False),
    (PACKAGE / "tmlr.sty", "tmlr.sty", False),
    (PACKAGE / "tmlr.bst", "tmlr.bst", False),
    (PACKAGE / "fancyhdr.sty", "fancyhdr.sty", False),
]
review_root = PACKAGE / "review_materials"
review_members = [
    (review_root / "README.md", "README.md", False),
    (review_root / "case_series.json", "case_series.json", False),
    (review_root / "verify_case_series.py", "verify_case_series.py", True),
    (review_root / "LICENSES.txt", "LICENSES.txt", False),
]

write_archive(PACKAGE / "anonymous-source.zip", source_members)
write_archive(PACKAGE / "anonymous-review-supplement.zip", review_members)

print(json.dumps({
    "source_archive_bytes": (PACKAGE / "anonymous-source.zip").stat().st_size,
    "review_archive_bytes": (PACKAGE / "anonymous-review-supplement.zip").stat().st_size,
}, sort_keys=True))
