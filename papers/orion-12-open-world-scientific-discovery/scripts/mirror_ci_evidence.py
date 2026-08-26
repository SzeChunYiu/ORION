#!/usr/bin/env python3
"""Mirror expiring CI evidence into the repository, with verifiable digests.

The primary evidence for this paper's external probes — candidate outputs, route
traces, per-review results, the official evaluator output — lives in GitHub
Actions artifacts that **expire on 2026-09-15**. After that date only the digests
recorded in the repository survive, and a digest whose subject no longer exists
is a fingerprint of something unrecoverable. The availability section promises an
archive; this is what makes the promise true.

Two digests are recorded per mirrored file, and the distinction is the point:

``sha256_raw``
    Over the bytes as CI produced them. This is what a reader recomputes after
    unzipping the mirror.
``sha256_canonical_json``
    Over canonical JSON (sorted keys, compact separators) for files that parse.
    CI pretty-prints its JSON while the repository stores it compactly, so the
    same content has two different byte digests — the mirrored MetaSyn
    false-negative ledger is 23,902 bytes against the committed 18,656, and they
    are JSON-identical. Anyone binding a raw digest to a CI-produced JSON file
    sets a trap for the next reader, who recomputes it from the artifact and
    concludes tampering. The canonical digest is the content identity.

``--check`` verifies every mirrored archive against the manifest, which is the
only assertion that still means anything once the upstream artifacts are gone.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path
from typing import Any

PAPER = Path(__file__).resolve().parent.parent
MIRROR = PAPER / "evidence" / "ci_mirror"
MANIFEST = MIRROR / "MANIFEST.json"

#: Regenerable outputs are deliberately not mirrored: the compiled PDF and its
#: log rebuild from source, so archiving them would spend repository space on
#: something a reader can produce.
EXCLUDED = ("p2-manuscript-audit",)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_json_digest(data: bytes) -> str | None:
    try:
        payload = json.loads(data)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    canonical = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return _sha256(canonical)


def describe(archive: Path) -> dict[str, Any]:
    data = archive.read_bytes()
    entry: dict[str, Any] = {
        "archive": archive.name,
        "archive_bytes": len(data),
        "archive_sha256": _sha256(data),
        "files": [],
    }
    with zipfile.ZipFile(archive) as bundle:
        for info in sorted(bundle.infolist(), key=lambda item: item.filename):
            if info.is_dir():
                continue
            payload = bundle.read(info.filename)
            record = {
                "path": info.filename,
                "bytes": info.file_size,
                "sha256_raw": _sha256(payload),
            }
            canonical = _canonical_json_digest(payload)
            if canonical:
                record["sha256_canonical_json"] = canonical
            entry["files"].append(record)
    entry["file_count"] = len(entry["files"])
    return entry


def build(mirror: Path) -> dict[str, Any]:
    archives = sorted(
        path
        for path in mirror.glob("*.zip")
        if not any(path.stem.startswith(name) for name in EXCLUDED)
    )
    return {
        "schema_version": "orion.p2.ci-evidence-mirror.v1",
        "why": (
            "GitHub Actions artifacts for this paper's external probes expire on "
            "2026-09-15. Mirrored here so the evidence outlives the CI retention "
            "window rather than leaving digests that point at nothing."
        ),
        "digest_note": (
            "sha256_raw is over the bytes CI produced; sha256_canonical_json is over "
            "canonical JSON and is the content identity. CI pretty-prints JSON that the "
            "repository stores compactly, so the two byte digests of identical content "
            "differ — bind the canonical one."
        ),
        "excluded": {
            name: "regenerable from source; not archived" for name in EXCLUDED
        },
        "artifacts": [describe(path) for path in archives],
    }


def check(mirror: Path) -> tuple[int, list[str]]:
    if not MANIFEST.is_file():
        return 1, [f"no manifest at {MANIFEST}"]
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    problems: list[str] = []
    declared = {entry["archive"]: entry for entry in manifest.get("artifacts", [])}
    present = {path.name for path in mirror.glob("*.zip")}

    for name in sorted(set(declared) - present):
        problems.append(f"{name}: declared in the manifest but absent from the mirror")
    for name in sorted(present - set(declared)):
        problems.append(f"{name}: present in the mirror but undeclared")

    for name in sorted(set(declared) & present):
        entry = declared[name]
        observed = describe(mirror / name)
        if observed["archive_sha256"] != entry["archive_sha256"]:
            problems.append(f"{name}: archive digest changed since it was mirrored")
            continue
        declared_files = {item["path"]: item for item in entry["files"]}
        observed_files = {item["path"]: item for item in observed["files"]}
        for path in sorted(set(declared_files) ^ set(observed_files)):
            problems.append(f"{name}:{path}: file set differs from the manifest")
        for path in sorted(set(declared_files) & set(observed_files)):
            if declared_files[path]["sha256_raw"] != observed_files[path]["sha256_raw"]:
                problems.append(f"{name}:{path}: content digest differs from the manifest")
    return (1 if problems else 0), problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify the mirror against the manifest")
    parser.add_argument("--mirror", type=Path, default=MIRROR)
    args = parser.parse_args(argv)

    if args.check:
        code, problems = check(args.mirror)
        for problem in problems:
            print(f"CI_MIRROR {problem}")
        print("CI_MIRROR ok" if code == 0 else f"CI_MIRROR {len(problems)} problems")
        return code

    args.mirror.mkdir(parents=True, exist_ok=True)
    manifest = build(args.mirror)
    MANIFEST.write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    total = sum(entry["archive_bytes"] for entry in manifest["artifacts"])
    print(f"wrote {MANIFEST} ({len(manifest['artifacts'])} archives, {total} bytes)")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
