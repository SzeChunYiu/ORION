#!/usr/bin/env python3
"""Frozen v3 member-manifest normalization: exclude request-generated crate files.

The v2 normalization (bind_workflowhub_rocrate_content_v1.py, frozen and imported
verbatim below) digests every RO-Crate member. The member-manifest boundary
diagnosis (workflowhub-member-manifest-freeze-v1/RESULT_V1.json, sbatch 3569824 +
3569845 on LUNARC) showed that for 95 of the 128 frozen families the live
WorkflowHub registry regenerates two root members -- ro-crate-metadata.json and
ro-crate-preview.html -- at request time, so three fetches of the SAME version of
the same workflow yield three distinct v2 aggregates while every
workflow-content member stays byte-identical. v2 aggregates for those families
bound single-request bytes that are irretrievable.

v3 is one uniform rule on top of the frozen v2 walk, with nothing else changed:

  EXCLUDE exactly the two root members ro-crate-metadata.json and
  ro-crate-preview.html from the normalized member manifest and from its
  aggregate, for every crate of every family. The exclusion is by exact
  canonical root path only; any other member (including nested files that
  happen to share a basename) is retained.

What v3 deliberately keeps from v2, verbatim: canonical member-path validation
(no absolute paths, no "..", no ".", no backslashes), the ZIP duplicate-path
rejection, directory-member skipping, per-member Unix semantics (kind +
executable bit), entry sorting by path, and the canonical JSON SHA-256
aggregate. The RO-Crate structural requirement (exactly one root
ro-crate-metadata.json per crate) is retained as a validity gate even though
that member's bytes no longer enter the digest.

The rule has zero free parameters and resolves nothing at run time. It is not
per-family and not conditional on any observed outcome: families whose
generated members happened to be byte-stable under v2 (the stable 33) are
normalized by the same rule as the volatile 95.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any
import zipfile

HERE = Path(__file__).resolve().parent

REQUEST_GENERATED_ROOT_MEMBERS: tuple[str, ...] = (
    "ro-crate-metadata.json",
    "ro-crate-preview.html",
)
V3_NORMALIZATION_ID = "WORKFLOWHUB_MEMBER_MANIFEST_NORMALIZATION_V3"
V3_RULE = (
    "normalized member manifest = frozen v2 normalized_content_manifest minus "
    "entries whose canonical path is exactly one of "
    + "|".join(REQUEST_GENERATED_ROOT_MEMBERS)
    + "; aggregate = the frozen v2 canonical_json_sha over the retained entries"
)

_BINDING: Any = None


def _load_binding() -> Any:
    """Import the frozen v2 normalization module verbatim (once per process)."""
    global _BINDING
    if _BINDING is None:
        path = HERE / "bind_workflowhub_rocrate_content_v1.py"
        spec = importlib.util.spec_from_file_location("a3_rocrate_binding_v3_base", path)
        if spec is None or spec.loader is None:
            raise ValueError(f"cannot import frozen v2 binding: {path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules["a3_rocrate_binding_v3_base"] = module
        spec.loader.exec_module(module)
        _BINDING = module
    return _BINDING


def normalized_content_manifest_v3(zf: zipfile.ZipFile) -> tuple[list[dict[str, Any]], list[dict[str, Any]], bytes]:
    """v3 walk: the frozen v2 walk with the uniform root exclusion applied.

    Returns (retained_entries, excluded_entries, ro_crate_metadata_bytes).
    retained+excluded partitions exactly the v2 manifest entry list (same field
    set, same per-entry rules); only membership differs.
    """
    binding = _load_binding()
    infos = zf.infolist()
    seen: set[str] = set()
    retained: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    metadata_bytes: bytes | None = None
    metadata_count = 0
    for info in infos:
        path = binding.canonical_member_path(info.filename)
        if path in seen:
            raise ValueError(f"duplicate ZIP member path: {path}")
        seen.add(path)
        if info.is_dir():
            continue
        data = zf.read(info)
        kind, executable = binding.member_semantics(info)
        entry = {
            "path": path,
            "bytes": len(data),
            "sha256": binding.sha256_bytes(data),
            "kind": kind,
            "executable": executable,
        }
        if path in REQUEST_GENERATED_ROOT_MEMBERS:
            excluded.append(entry)
        else:
            retained.append(entry)
        if path == "ro-crate-metadata.json":
            metadata_count += 1
            metadata_bytes = data
    if metadata_count != 1 or metadata_bytes is None:
        raise ValueError("RO-Crate zip must contain exactly one root ro-crate-metadata.json")
    retained.sort(key=lambda x: x["path"])
    excluded.sort(key=lambda x: x["path"])
    return retained, excluded, metadata_bytes


def aggregate_v3(retained_entries: list[dict[str, Any]]) -> str:
    """v3 aggregate: the frozen v2 canonical JSON SHA-256 over retained entries."""
    return _load_binding().canonical_json_sha(retained_entries)


def v2_equivalent_manifest(retained: list[dict[str, Any]], excluded: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Re-derive the v2 manifest from a v3 split (cross-check helper).

    retained+excluded, each already path-sorted, merge to exactly the v2
    manifest list. Used by the harvester to prove the split is a faithful
    partition of the frozen v2 walk rather than a re-implementation.
    """
    return sorted(retained + excluded, key=lambda x: x["path"])


def self_test() -> dict[str, Any]:
    """Networkless self-test with mutation controls (teeth, not fixtures)."""
    binding = _load_binding()
    import io

    workflow = b"cwlVersion: v1.2\nclass: CommandLineTool\n"
    tool = b"#!/usr/bin/env python3\nprint('hi')\n"

    def build(generated_metadata: bytes, generated_preview: bytes, *, compression: int, order: list[str], date: tuple[int, int, int, int, int, int]) -> bytes:
        payloads = {
            "ro-crate-metadata.json": generated_metadata,
            "ro-crate-preview.html": generated_preview,
            "workflow.cwl": workflow,
            "tools/run.py": tool,
        }
        entries = [(name, payloads[name]) for name in order]
        return binding.make_zip(entries, compression=compression, date=date)

    gen_a = b'{"@graph": [{"id": "./"}]}'
    gen_b = b'{"@graph": [{"id": "./", "dateModified": "2026-09-03T10:00:00Z"}]}'
    prev_a = b"<html>rendered at 10:00:00</html>"
    prev_b = b"<html>rendered at 10:00:42</html>"

    order_one = ["ro-crate-metadata.json", "ro-crate-preview.html", "workflow.cwl", "tools/run.py"]
    order_two = ["tools/run.py", "workflow.cwl", "ro-crate-preview.html", "ro-crate-metadata.json"]

    crate_one = build(gen_a, prev_a, compression=zipfile.ZIP_STORED, order=order_one, date=(2020, 1, 1, 0, 0, 0))
    crate_two = build(gen_b, prev_b, compression=zipfile.ZIP_DEFLATED, order=order_two, date=(2026, 9, 3, 12, 0, 0))

    def v3_of(data: bytes) -> tuple[list[dict[str, Any]], list[dict[str, Any]], str, str]:
        with zipfile.ZipFile(io.BytesIO(data), "r") as zf:
            retained, excluded, _metadata = normalized_content_manifest_v3(zf)
        return retained, excluded, aggregate_v3(retained), binding.canonical_json_sha(v2_equivalent_manifest(retained, excluded))

    one_retained, one_excluded, one_v3, one_v2 = v3_of(crate_one)
    two_retained, two_excluded, two_v3, two_v2 = v3_of(crate_two)

    # 1. The observed volatility mechanism is neutralized under v3 ...
    assert one_v3 == two_v3, "regenerated crate files must not move the v3 aggregate"
    # ... while v2 over the same bytes DOES move (control: the test has teeth).
    assert one_v2 != two_v2, "control failed: generated-member volatility invisible to v2"
    # ... and v2 over the merged split reproduces the frozen v2 validator bitwise.
    assert one_v2 == binding.validate_rocrate_bytes(crate_one)["normalized_content_manifest_sha256"]
    assert two_v2 == binding.validate_rocrate_bytes(crate_two)["normalized_content_manifest_sha256"]

    # 2. The exclusion is exactly the two root members, uniformly.
    assert [e["path"] for e in one_excluded] == ["ro-crate-metadata.json", "ro-crate-preview.html"]
    assert [e["path"] for e in two_excluded] == ["ro-crate-metadata.json", "ro-crate-preview.html"]
    assert [e["path"] for e in one_retained] == ["tools/run.py", "workflow.cwl"]

    # 3. Workflow-content change still moves the v3 aggregate.
    buf = io.BytesIO()
    import stat as stat_module
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_STORED) as zf:
        for name, payload in (
            ("ro-crate-metadata.json", gen_a),
            ("ro-crate-preview.html", prev_a),
            ("workflow.cwl", workflow + b"# one real content edit\n"),
            ("tools/run.py", tool),
        ):
            info = zipfile.ZipInfo(name, date_time=(2020, 1, 1, 0, 0, 0))
            info.external_attr = (stat_module.S_IFREG | 0o644) << 16
            info.compress_type = zipfile.ZIP_STORED
            zf.writestr(info, payload)
    with zipfile.ZipFile(io.BytesIO(buf.getvalue()), "r") as zf:
        m_retained, _m_excluded, _ = normalized_content_manifest_v3(zf)
    assert aggregate_v3(m_retained) != one_v3, "content change must move the v3 aggregate"

    # 4. Nested members sharing the excluded basenames are retained (root-only rule).
    nested = io.BytesIO()
    with zipfile.ZipFile(nested, "w", compression=zipfile.ZIP_STORED) as zf:
        for name, payload in (
            ("ro-crate-metadata.json", gen_a),
            ("nested/ro-crate-metadata.json", b"{}"),
            ("nested/ro-crate-preview.html", b"<p>x</p>"),
            ("workflow.cwl", workflow),
        ):
            zf.writestr(name, payload)
    with zipfile.ZipFile(io.BytesIO(nested.getvalue()), "r") as zf:
        n_retained, n_excluded, _ = normalized_content_manifest_v3(zf)
    assert [e["path"] for e in n_excluded] == ["ro-crate-metadata.json"]
    assert [e["path"] for e in n_retained] == ["nested/ro-crate-metadata.json", "nested/ro-crate-preview.html", "workflow.cwl"]

    # 5. Structural RO-Crate validity is still enforced.
    no_meta = io.BytesIO()
    with zipfile.ZipFile(no_meta, "w") as zf:
        zf.writestr("workflow.cwl", workflow)
    try:
        with zipfile.ZipFile(io.BytesIO(no_meta.getvalue()), "r") as zf:
            normalized_content_manifest_v3(zf)
    except ValueError as exc:
        assert "exactly one root ro-crate-metadata.json" in str(exc)
    else:
        raise AssertionError("crate without root metadata accepted under v3")

    # 6. Entry field contract is exactly the frozen v2 entry contract.
    assert set(one_retained[0]) == {"path", "bytes", "sha256", "kind", "executable"}

    return {
        "decision": "GREEN",
        "normalization_id": V3_NORMALIZATION_ID,
        "request_generated_root_members": list(REQUEST_GENERATED_ROOT_MEMBERS),
        "free_parameters": [],
        "volatility_neutralized_v3_stable": True,
        "v2_control_moves_on_same_bytes": True,
        "split_reproduces_frozen_v2_validator_bitwise": True,
        "workflow_content_change_detected": True,
        "nested_same_basename_retained": True,
        "structural_rocrate_requirement_retained": True,
        "network_accessed": False,
    }


def main() -> int:
    print(json.dumps(self_test(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
