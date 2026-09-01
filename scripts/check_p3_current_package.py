#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path

repo = Path(__file__).resolve().parents[1]
paper = repo / "papers/orion-13-global-knowledge-portrait"
package = paper / "journal_package"
manifest = json.loads((package / "MANIFEST.json").read_text(encoding="utf-8"))
state = json.loads((package / "RENDER_CLOSURE_STATE.json").read_text(encoding="utf-8"))
authority = manifest.get("package_authority") or {}
binding = manifest.get("render_binding") or {}
claims = {
    claim.get("id"): claim
    for claim in manifest.get("claims", [])
    if isinstance(claim, dict)
}
errors: list[str] = []

expected = [
    (manifest, "package_status", "BOUNDED_PEER_REVIEW_READY"),
    (manifest, "scientific_authority_delta", "NONE"),
    (authority, "current_submission_authorized", True),
    (binding, "current_revision_binding", True),
    (binding, "binding_status", "CONTENT_MATCHED"),
    (state, "state", "CURRENT"),
    (state, "evidence", "RENDERED_PDF"),
]
for record, key, value in expected:
    if record.get(key) != value:
        errors.append(f"{key}: expected {value!r}, got {record.get(key)!r}")

expected_blob = "bd77cf84cef75bdb831544d7bc7a03650f439742"
source_blob = subprocess.check_output(
    [
        "git",
        "rev-parse",
        "HEAD:papers/orion-13-global-knowledge-portrait/manuscript/main.pdf",
    ],
    cwd=repo,
    text=True,
).strip()
packaged_blob = subprocess.check_output(
    ["git", "hash-object", str(package / "manuscript.pdf")],
    cwd=repo,
    text=True,
).strip()
if source_blob != expected_blob or packaged_blob != expected_blob:
    errors.append(f"PDF blob mismatch: source={source_blob}, packaged={packaged_blob}")
if authority.get("source_pdf_git_blob") != expected_blob:
    errors.append("manifest source_pdf_git_blob mismatch")
if authority.get("packaged_pdf_git_blob") != expected_blob:
    errors.append("manifest packaged_pdf_git_blob mismatch")
if binding.get("git_blob") != expected_blob or binding.get("pages") != 47:
    errors.append("render_binding identity/page mismatch")
if state.get("packaged_pdf_pages") != 47 or state.get("built_manuscript_pages") != 47:
    errors.append("render-closure page mismatch")

required_claims = {
    "P3.C7": "CANNOT_CHECK",
    "P3.C8": "CANNOT_CHECK",
    "P3.POLARITY_REDUCT": "ADVERSE_RETAINED",
    "P3.CURRENT_PACKAGE": "BOUND",
}
for claim_id, status in required_claims.items():
    actual = (claims.get(claim_id) or {}).get("status")
    if actual != status:
        errors.append(f"{claim_id}: expected {status}, got {actual}")

if errors:
    for error in errors:
        print(f"P3_CURRENT_PACKAGE_ERROR: {error}")
    raise SystemExit(1)
print("P3_CURRENT_PACKAGE_EXACTLY_BOUND_NEGATIVE_TERMINALS_RETAINED")
