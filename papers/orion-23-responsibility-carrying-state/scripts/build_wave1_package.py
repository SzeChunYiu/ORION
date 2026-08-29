#!/usr/bin/env python3
"""Build deterministic anonymous archives and a private exact-byte binding."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PAPER = ROOT / "papers" / "orion-23-responsibility-carrying-state"
PUBLIC = PAPER / "journal_package" / "wave1_current"
SOURCE = PUBLIC / "source"
REVIEW = PUBLIC / "review_materials"
PRIVATE = PAPER / "wave1_closeout" / "private_evidence"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def deterministic_zip(output: Path, members: list[tuple[Path, str]]) -> None:
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path, name in sorted(members, key=lambda item: item[1]):
            info = zipfile.ZipInfo(name, date_time=(2026, 8, 28, 12, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())


def scan_text(label: str, text: str) -> list[str]:
    patterns = {
        "internal paper or round label": r"\b(?:ORION|QG)[-_ ]?\d+\b|\bP\d+\b|\bR\d+[A-Z]?(?:[-_]V?\d+)?\b|Wave[- ]?1",
        "repository or transport residue": r"github|pull request|\bPR\b|commit|branch|continuous integration|\bCI\b|issue\s*#|papers/|research/|src/|scripts/|tests/",
        "private or repository path": r"(?:^|[\s`])(?:/Users/|/home/|papers/|research/|src/|scripts/|tests/|development/)",
        "digest or machine terminal": r"sha-?256|checksum|CANNOT_CHECK|TOP_TIER|PEER_REVIEW_READY|FAIL_CLOSED|\bGREEN\b|\b[a-f0-9]{40}\b|\b[a-f0-9]{64}\b",
    }
    hits = []
    for kind, pattern in patterns.items():
        for match in re.finditer(pattern, text, flags=re.IGNORECASE | re.MULTILINE):
            excerpt = text[max(0, match.start() - 45) : match.end() + 45].replace("\n", " ")
            hits.append(f"{label}: {kind}: {excerpt}")
    return hits


def main() -> None:
    subprocess.run([sys.executable, str(PAPER / "scripts/build_wave1_review_evidence.py")], check=True)
    subprocess.run([sys.executable, "verify.py"], cwd=REVIEW, check=True)
    env = os.environ.copy()
    env["SOURCE_DATE_EPOCH"] = "1787928000"
    subprocess.run(["tectonic", "main.tex"], cwd=SOURCE, env=env, check=True)
    shutil.copy2(SOURCE / "main.pdf", PUBLIC / "manuscript.pdf")

    deterministic_zip(PUBLIC / "source.zip", [(SOURCE / name, name) for name in ("main.tex", "references.bib", "tmlr.sty")])
    deterministic_zip(PUBLIC / "review_materials.zip", [(REVIEW / name, name) for name in ("README.md", "evidence.json", "verify.py")])
    (SOURCE / "main.pdf").unlink()

    hits = []
    for path in (PUBLIC / "manuscript.pdf", PUBLIC / "COVER_LETTER.md", PUBLIC / "AVAILABILITY_STATEMENT.md"):
        text = subprocess.check_output(["pdftotext", str(path), "-"], text=True) if path.suffix == ".pdf" else path.read_text()
        hits.extend(scan_text(path.name, text))
    for archive_path in (PUBLIC / "source.zip", PUBLIC / "review_materials.zip"):
        with zipfile.ZipFile(archive_path) as archive:
            for member in archive.namelist():
                if member != Path(member).name:
                    hits.append(f"{archive_path.name}: non-generic member name: {member}")
                hits.extend(scan_text(f"{archive_path.name}:{member}", archive.read(member).decode("utf-8", "replace")))
    if hits:
        raise SystemExit("reader-surface scan failed:\n" + "\n".join(hits))

    PRIVATE.mkdir(parents=True, exist_ok=True)
    artifacts = []
    for path in (PUBLIC / "manuscript.pdf", PUBLIC / "source.zip", PUBLIC / "review_materials.zip", PUBLIC / "COVER_LETTER.md", PUBLIC / "AVAILABILITY_STATEMENT.md"):
        artifacts.append({"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size, "sha256": digest(path)})
    binding = {
        "schema": "ORION.Wave1PrivateSubmissionBinding.v1",
        "paper": "ORION-23",
        "public_upload_names": ["manuscript.pdf", "source.zip", "review_materials.zip"],
        "artifacts": artifacts,
        "reader_surface_scan": {"forbidden_hit_count": 0},
    }
    (PRIVATE / "EXACT_BYTE_BINDING.json").write_text(json.dumps(binding, indent=2) + "\n")
    print(json.dumps(binding, indent=2))


if __name__ == "__main__":
    main()
