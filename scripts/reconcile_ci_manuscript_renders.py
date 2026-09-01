#!/usr/bin/env python3
"""Reconcile clean-CI manuscript renders without changing scientific authority.

The clipping workflow rebuilds every working manuscript in a pinned Ubuntu
24.04 / TeX Live 2023 environment.  This utility imports the nine derived PDFs
from one such run, updates only the checksums that explicitly bind those PDFs,
and then (in a second commit) re-pins the four V1 candidate manifests whose
subjects include a changed render.  The two phases must not be collapsed: the
subject commit has to contain the bytes and digest file before a manifest can
truthfully name it.

This is render reconciliation, not scientific reconciliation.  Source, claims,
tables, evidence, null results, and authority records are outside the allowed
change set.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
CI_SOURCE_COMMIT = "b380d807d11665698c5474bd07bde3f700206041"
CI_WORKFLOW_RUN = "33466273211"
CI_ARTIFACT_ID = "9784999811"
RENDER_DATE = "2026-09-01"

RENDERS = {
    "orion-09-compilation-regime-geometry": (
        "585e44e28d8c8dee6812c5a46d6a47fe625c129b0a7ebe5efc7f1474b40ed011",
        7,
    ),
    "orion-10-certified-static-forecasting": (
        "46eb117869a4614defca6eb4b6c89f01ad54990cc9e6725d0f96752d3b37ea14",
        7,
    ),
    "orion-11-recursive-epistemic-reconstruction": (
        "ec5e9b1b60eb085eda16d0218feb1648e84aec2ff12fbdc777d14255eedeb1c5",
        48,
    ),
    "orion-12-open-world-scientific-discovery": (
        "95c6944baebb31fbf4e9705ad41078df5fdcf63b959ed742e153e9240c6dcdd3",
        47,
    ),
    "orion-14-verified-scientific-discovery": (
        "76c9a0c43d2e53bceff04f1397fbe2cceb1427b16240bb5c0a6c6b3478445ea1",
        28,
    ),
    "orion-21-state-as-computation": (
        "c871ad57c5ce3440ab64afb79dfdeec7df4d691ce6c4fc75707298bdf6bd78eb",
        9,
    ),
    "orion-22-adaptive-state-reasoning": (
        "e15c48bd6aabe57be8ab772afbbf79188c60b6b4203c1ba9de180e21ab291a94",
        7,
    ),
    "orion-23-responsibility-carrying-state": (
        "d3a86ab98c877d2584b414518962d158ab459dd9c0ab6e305fde7944204e1c5c",
        6,
    ),
    "orion-25-orion-research-harness": (
        "1f2d73c6a3b69acb923711381221c2363a9ce621e3c37b33840499b84fdd52cd",
        12,
    ),
}

V1_BINDINGS = {
    "P11": "orion-21-state-as-computation",
    "P12": "orion-22-adaptive-state-reasoning",
    "P13": "orion-23-responsibility-carrying-state",
    "P15": "orion-25-orion-research-harness",
}

PRIOR_PDF_DIGESTS = {
    "orion-21-state-as-computation": (
        "16627f98acf4938ba1b670e83d5deab988cf3691e8457974ffb61f1ce1c516e7"
    ),
    "orion-22-adaptive-state-reasoning": (
        "a703ca1407df9d58421b9c2e5c33ba24fa90b6a80e4368996e4e1c32203cc010"
    ),
    "orion-23-responsibility-carrying-state": (
        "6411b6fa73bca8f892f211755ec4a937438c957b27b04ea7f6ce3ed32b2de87f"
    ),
    "orion-25-orion-research-harness": (
        "dbc9be631bcbec0a9a0d3551843c033eb970910353e5fcaf244cb99f8a73f877"
    ),
}

P4_PRIOR_MANIFEST_DIGEST = (
    "2d3841da6c0a70b169dcaf162fb126fc0e1b0c9c54d0a15fd897744239644f71"
)
P4_PRIOR_TRACKED_PDF_DIGEST = (
    "216d2d5aa0b0f51f15d2ad46623fc0589c5869f960157d406e91d7244af43eea"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_text(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, check=False
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip()


def git_bytes(commit: str, relative: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{commit}:{relative}"], cwd=ROOT, capture_output=True, check=False
    )
    if result.returncode:
        raise RuntimeError(f"{commit} does not contain {relative}")
    return result.stdout


def parse_sums(text: str) -> dict[str, str]:
    rows: dict[str, str] = {}
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        digest, separator, path = raw.partition("  ")
        if not separator or not re.fullmatch(r"[0-9a-f]{64}", digest) or not path:
            raise RuntimeError(f"malformed checksum row: {raw!r}")
        rows[path] = digest
    return rows


def replace_sum(path: Path, relative: str, digest: str, *, expected_old: str | None) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    matches = [i for i, line in enumerate(lines) if line.endswith(f"  {relative}")]
    if len(matches) != 1:
        raise RuntimeError(f"{path}: expected one checksum row for {relative}")
    index = matches[0]
    old = lines[index].split("  ", 1)[0]
    if expected_old is not None and old not in {expected_old, digest}:
        raise RuntimeError(f"{path}: unexpected prior digest for {relative}: {old}")
    lines[index] = f"{digest}  {relative}"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def verify_imported_renders(selected: set[str] | None = None) -> None:
    for slug, (expected, _pages) in RENDERS.items():
        if selected is not None and slug not in selected:
            continue
        pdf = ROOT / "papers" / slug / "manuscript" / "main.pdf"
        actual = sha256_file(pdf)
        if actual != expected:
            raise RuntimeError(f"{slug}: imported PDF digest {actual}, expected {expected}")


def prepare_digest_subject(selected: set[str] | None = None) -> None:
    verify_imported_renders(selected)

    if selected is not None:
        binding_slugs = set(V1_BINDINGS.values())
        unsupported = selected - binding_slugs
        if unsupported:
            raise RuntimeError(
                "targeted preparation supports V1-bound papers only: "
                + ", ".join(sorted(unsupported))
            )
        for slug in sorted(selected):
            paper = ROOT / "papers" / slug
            relative = f"papers/{slug}/manuscript/main.pdf"
            replace_sum(
                paper / "SHA256SUMS",
                relative,
                RENDERS[slug][0],
                expected_old=PRIOR_PDF_DIGESTS[slug],
            )
        print(f"prepared {len(selected)} targeted CI render checksum binding(s)")
        return

    p4 = ROOT / "papers" / "orion-14-verified-scientific-discovery"
    package = p4 / "journal_package"
    history = package / "history"
    history.mkdir(exist_ok=True)
    historical_sums = history / "SHA256SUMS_PRE_CI_RENDER_2026-09-01.txt"
    if not historical_sums.exists():
        historical_sums.write_bytes((package / "SHA256SUMS").read_bytes())

    manifest_path = package / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    prior_binding = manifest.get("pdf_render_binding")
    if not isinstance(prior_binding, dict):
        raise RuntimeError("ORION-14: pdf_render_binding is absent")
    history_rows = manifest.setdefault("pdf_render_binding_history", [])
    if not isinstance(history_rows, list):
        raise RuntimeError("ORION-14: malformed pdf_render_binding_history")
    target_digest = RENDERS["orion-14-verified-scientific-discovery"][0]
    if (
        prior_binding.get("sha256") != target_digest
        and not any(row.get("sha256") == prior_binding.get("sha256") for row in history_rows)
    ):
        history_rows.append(
            {
                **prior_binding,
                "superseded_reason": (
                    "Replaced by the pinned clean-CI pdfTeX render required by the "
                    "repository clipping and byte-equality gate."
                ),
                "scientific_authority_delta": "NONE",
                "preserved_manifest": "journal_package/history/MANIFEST_2026-08-24.json",
                "preserved_checksum_record": (
                    "journal_package/history/SHA256SUMS_PRE_CI_RENDER_2026-09-01.txt"
                ),
            }
        )
    for row in history_rows:
        if row.get("sha256") == P4_PRIOR_MANIFEST_DIGEST:
            row["tracked_pdf_sha256_at_reconciliation"] = P4_PRIOR_TRACKED_PDF_DIGEST
            row["binding_consistency_at_reconciliation"] = (
                "MISMATCH_RETAINED: the historical manifest named the local tectonic "
                "render, while the then-current tracked PDF and checksum record named a "
                "different PDF. Both records are preserved; neither mismatch is treated "
                "as scientific evidence or authority."
            )
    manifest["pdf_render_binding"] = {
        "note": (
            "Pinned clean-CI render imported from the manuscript-clipping-audit "
            "artifact. The render-only reconciliation changes no source, claim, "
            "table, evidence, null result, or authority state."
        ),
        "source_revision": CI_SOURCE_COMMIT,
        "rendered_utc_date": RENDER_DATE,
        "engine": "pdfTeX-1.40.25 via latexmk 4.83; pinned Ubuntu 24.04 TeX Live 2023",
        "source_date_epoch_policy": (
            "latest commit touching manuscript inputs, excluding manuscript/main.pdf"
        ),
        "workflow_run_id": CI_WORKFLOW_RUN,
        "artifact_id": CI_ARTIFACT_ID,
        "sha256": target_digest,
        "pages": RENDERS["orion-14-verified-scientific-discovery"][1],
    }
    missing = manifest.get("missing_artifacts", [])
    for row in missing:
        if row.get("path") == "journal_package/manuscript.pdf":
            row["reason"] = (
                "Intentionally not copied: COMPILE.md keeps the compiled working PDF at "
                "manuscript/main.pdf. That file is hash-bound by pdf_render_binding to "
                "the pinned clean-CI render dated 2026-09-01. The audited 12-page V2 "
                "release PDF remains historical and separately identified by its release hash."
            )
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    # Update every path owned by the legacy package checker.  This records the
    # current package documents after their render-provenance addendum as well as
    # the imported PDF, while leaving every scientific artifact byte untouched.
    package_docs = ("MANIFEST.json", "COMPILE.md", "LICENSE.md", "CLAIM_PDF_AUDIT.md", "README.md")
    required = [f"journal_package/{name}" for name in package_docs]
    required.extend(row["path"] for row in manifest["required_files"] if row["path"] not in required)
    (package / "SHA256SUMS").write_text(
        "".join(f"{sha256_file(p4 / relative)}  {relative}\n" for relative in required),
        encoding="utf-8",
    )

    for slug in V1_BINDINGS.values():
        paper = ROOT / "papers" / slug
        relative = f"papers/{slug}/manuscript/main.pdf"
        replace_sum(
            paper / "SHA256SUMS",
            relative,
            RENDERS[slug][0],
            expected_old=PRIOR_PDF_DIGESTS[slug],
        )

    print("prepared nine CI renders and reconciled five PDF checksum bindings")


def bind_subject(commit: str, selected: set[str] | None = None) -> None:
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise RuntimeError("--subject-commit must be a full lowercase Git commit ID")
    git_text("cat-file", "-e", f"{commit}^{{commit}}")
    git_text("merge-base", "--is-ancestor", commit, "HEAD")

    for candidate_id, slug in V1_BINDINGS.items():
        if selected is not None and slug not in selected:
            continue
        paper = ROOT / "papers" / slug
        manifest_path = paper / "CONTENT_MANIFEST_V1.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("candidate_id") != candidate_id:
            raise RuntimeError(f"{slug}: candidate identity mismatch")
        prior_subject = manifest.get("subject_commit")
        digest_relative = f"papers/{slug}/SHA256SUMS"
        committed_sums = parse_sums(git_bytes(commit, digest_relative).decode("utf-8"))
        for row in manifest.get("bound_files", []):
            relative = row.get("path")
            if not isinstance(relative, str) or relative not in committed_sums:
                raise RuntimeError(f"{slug}: bound path absent from committed sums: {relative}")
            committed = hashlib.sha256(git_bytes(commit, relative)).hexdigest()
            if committed != committed_sums[relative]:
                raise RuntimeError(f"{slug}: committed checksum mismatch: {relative}")

        history_rows = manifest.setdefault("publication_render_rebinding_history", [])
        if not isinstance(history_rows, list):
            raise RuntimeError(f"{slug}: malformed publication render history")
        if not any(row.get("new_subject_commit") == commit for row in history_rows):
            history_rows.append(
                {
                    "prior_subject_commit": prior_subject,
                    "new_subject_commit": commit,
                    "reason": (
                        "Imported the pinned clean-CI manuscript PDF required by the "
                        "clipping and byte-equality gate."
                    ),
                    "scientific_authority_delta": "NONE",
                    "workflow_run_id": CI_WORKFLOW_RUN,
                    "artifact_id": CI_ARTIFACT_ID,
                    "changed_derived_file": {
                        "path": f"papers/{slug}/manuscript/main.pdf",
                        "prior_sha256": PRIOR_PDF_DIGESTS[slug],
                        "new_sha256": RENDERS[slug][0],
                    },
                }
            )
        manifest["subject_commit"] = commit
        manifest["subject_commit_status"] = "BOUND"
        manifest["subject_commit_blocker"] = None
        manifest["subject_commit_unbound_paths"] = []
        manifest_path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        print(f"{candidate_id}: pinned render subject to {commit}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prepare", action="store_true")
    group.add_argument("--subject-commit")
    parser.add_argument(
        "--papers",
        default="",
        help="comma-separated V1 paper slugs for an incremental render reconciliation",
    )
    args = parser.parse_args()
    selected = {item.strip() for item in args.papers.split(",") if item.strip()} or None
    if args.prepare:
        prepare_digest_subject(selected)
    else:
        bind_subject(args.subject_commit, selected)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
