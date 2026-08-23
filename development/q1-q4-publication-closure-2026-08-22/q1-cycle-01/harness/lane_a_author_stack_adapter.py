#!/usr/bin/env python3
"""Finite Q1-C1 adapter over the frozen R6M/R6P/R6O author stack.

The adapter binds production ``C_DP``, support-two ``C_2`` and support-one
``C_1`` outputs to exactly the prospective Q1-C1 fixture corpus: all 4^6
one-qubit rows and the declared 65 two-qubit rows.  It is corroborative finite
implementation evidence only.  It neither reads Lane B nor claims arbitrary-n
production equivalence.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import socket
import sys
from pathlib import Path
from typing import Any


CANDIDATE_REF = "158fcb08b612ffc82f5a5d2bed4917409084ded8"
PROTOCOL_ID = "Q1-C1"
PROTOCOL_VERSION = "1.0"
PYTHON = str(Path(sys.executable).resolve())
FIXTURE_SHA256 = "50d60befaab71dbbacf2d32fe4502705023f3cede34d5e61d101564cbf5113b9"
AUTHOR_SOURCE_SHA256 = {
    "research/extensions/orion-q/max_r6m_exact_three_tare2_shared_factor_dp.py": "7c6579db5f4afbc1738e8b3d96aa3730023bc3831d1fc4950ab34e071c0e3d90",
    "research/extensions/orion-q/max_r6p_weight2_frame_donor_closure.py": "1006ab0293727ebb994b1202118bc60e779eb5432f820222c6ffbf22304d5965",
    "research/extensions/orion-q/max_r6o_enlarged_tag_donor_closure.py": "37cfd64201312e4c7e670e2beefede0961c7dd6a4cd1e3bb2f1fb74afbdf8c17",
}


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_path(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def _json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    item = getattr(value, "item", None)
    if callable(item):
        return item()
    return value


def _exclusive_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(_json_ready(value), indent=2, sort_keys=True, allow_nan=False) + "\n"
    with path.open("x", encoding="utf-8") as handle:
        handle.write(data)


def _inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _forbidden_lane_b_path(raw: Any) -> bool:
    if isinstance(raw, int):
        return False
    try:
        parts = {part.lower().replace("-", "_") for part in Path(raw).parts}
    except (TypeError, ValueError):
        return False
    return "lane_b" in parts


def _audit(event: str, args: tuple[Any, ...]) -> None:
    if event.startswith("socket."):
        raise PermissionError(f"Q1-C1 adapter network audit denied {event}")
    if event == "open" and args and _forbidden_lane_b_path(args[0]):
        raise PermissionError(f"Q1-C1 adapter denied Lane B read: {args[0]}")


def _socket_negative_control() -> dict[str, str]:
    try:
        socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except PermissionError as exc:
        return {"status": "PASS", "exception": f"{type(exc).__name__}: {exc}"}
    raise AssertionError("AF_INET negative control was not denied")


def _validated_paths(argv: list[str]) -> tuple[Path, Path, Path]:
    if len(argv) != 3:
        raise SystemExit(
            "usage: lane_a_author_stack_adapter.py ARCHIVE_ROOT FIXTURE_PATH RESULT_PATH"
        )
    archive, fixture, result = (Path(item).expanduser().resolve() for item in argv)
    if not archive.is_dir():
        raise NotADirectoryError(archive)
    if not fixture.is_file():
        raise FileNotFoundError(fixture)
    if _forbidden_lane_b_path(fixture) or _forbidden_lane_b_path(result):
        raise ValueError("Lane A adapter paths may not enter Lane B custody")
    if _inside(result, archive):
        raise ValueError("adapter output must be outside ARCHIVE_ROOT")
    if result.exists():
        raise FileExistsError(result)
    return archive, fixture, result


def _verify_sources(archive: Path) -> dict[str, dict[str, Any]]:
    records = {}
    for relative, expected in AUTHOR_SOURCE_SHA256.items():
        path = archive / relative
        actual = _sha256_path(path) if path.is_file() else "MISSING"
        if actual != expected:
            raise ValueError(
                {"source": relative, "expected_sha256": expected, "actual_sha256": actual}
            )
        records[relative] = {"sha256": actual, "bytes": path.stat().st_size}
    return records


def _load_author_stack(archive: Path):
    module_root = archive / "research/extensions/orion-q"
    sys.path.insert(0, str(module_root))
    import max_r6_p10_candidate_blind_frame_optimizer as p10
    import max_r6m_exact_three_tare2_shared_factor_dp as r6m
    import max_r6o_enlarged_tag_donor_closure as r6o
    import max_r6p_weight2_frame_donor_closure as r6p

    expected_files = {
        "r6m": module_root / "max_r6m_exact_three_tare2_shared_factor_dp.py",
        "r6p": module_root / "max_r6p_weight2_frame_donor_closure.py",
        "r6o": module_root / "max_r6o_enlarged_tag_donor_closure.py",
        "p10": module_root / "max_r6_p10_candidate_blind_frame_optimizer.py",
    }
    modules = {"r6m": r6m, "r6p": r6p, "r6o": r6o, "p10": p10}
    for name, module in modules.items():
        if Path(module.__file__).resolve() != expected_files[name].resolve():
            raise ImportError(f"{name} resolved outside candidate archive: {module.__file__}")
    return p10, r6m, r6p, r6o, {
        name: {"path": str(expected_files[name]), "sha256": _sha256_path(expected_files[name])}
        for name in sorted(expected_files)
    }


def _target_pairs(
    p10: Any, targets: list[list[int]], encoding: str
) -> tuple[Any, Any, Any]:
    if len(targets) != 6 or len({len(row) for row in targets}) != 1:
        raise ValueError("targets must be six equal-length Pauli-code strings")
    if encoding == "LOCAL_PAULI_CODES_Q0_FIRST":
        keys = tuple(
            p10.key_from_codes(tuple(int(letter) for letter in row)) for row in targets
        )
    elif encoding == "GLOBAL_XZ_KEYS":
        if any(len(row) != 2 for row in targets):
            raise ValueError("GLOBAL_XZ_KEYS requires six [x,z] pairs")
        keys = tuple(tuple(int(component) for component in row) for row in targets)
    else:
        raise ValueError(f"unknown target encoding: {encoding}")
    return ((keys[0], keys[1]), (keys[2], keys[3]), (keys[4], keys[5]))


def _cost_row(
    p10: Any,
    r6p: Any,
    r6o: Any,
    fixture_id: str,
    targets: list[list[int]],
    n: int,
    *,
    target_encoding: str,
    sharpness: bool = False,
) -> tuple[dict[str, Any], tuple[Any, Any, Any], dict[str, Any], dict[str, Any]]:
    target_pairs = _target_pairs(p10, targets, target_encoding)
    if n == 1:
        p6 = tuple(int(row[0]) for row in targets)
        c_dp = int(r6p.dp_cost_n1_reader(p6))
    elif n == 2:
        c_dp = int(r6p.dp_cost_n2_reader(target_pairs))
    else:
        raise ValueError("Q1-C1 production adapter authority is restricted to n=1,2")
    dxx = r6p.dxx_search(target_pairs, n, want_witness=sharpness)
    dplus = r6o.dplus_pairs(target_pairs, n)
    c_2 = int(dxx["C_Dxx"])
    c_1 = int(dplus["C_Dplus"])
    row = {
        "fixture_id": fixture_id,
        "n": n,
        "targets": targets,
        "target_encoding": target_encoding,
        "target_pairs": _json_ready(target_pairs),
        "C_DP": c_dp,
        "C_2": c_2,
        "C_1": c_1,
        "C_2_equals_C_DP": c_2 == c_dp,
        "C_1_equals_C_DP": c_1 == c_dp,
    }
    return row, target_pairs, dxx, dplus


def _run_n1(p10: Any, r6m: Any, r6p: Any, r6o: Any) -> list[dict[str, Any]]:
    rows = []
    for index, p6 in enumerate(itertools.product(range(4), repeat=6)):
        if index % 256 == 0:
            r6m._local_table.cache_clear()
        targets = [[int(letter)] for letter in p6]
        row, _, _, _ = _cost_row(
            p10,
            r6p,
            r6o,
            f"N1_EXHAUSTIVE_{index:04d}",
            targets,
            1,
            target_encoding="LOCAL_PAULI_CODES_Q0_FIRST",
        )
        rows.append(row)
    r6m._local_table.cache_clear()
    if len(rows) != 4096:
        raise AssertionError("n=1 generator did not produce exactly 4096 rows")
    return rows


def _run_n2(
    p10: Any, r6m: Any, r6p: Any, r6o: Any, fixture: dict[str, Any]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    source_rows = fixture["n2_fixed"]["rows"]
    if len(source_rows) != 65:
        raise ValueError("n=2 fixture must contain exactly 65 rows")
    rows = []
    sharpness_evidence: dict[str, Any] | None = None
    for index, source in enumerate(source_rows):
        fixture_id = str(source["fixture_id"])
        if index == 0 and fixture_id != "N2_SHARPNESS_000":
            raise ValueError("first n=2 row is not the frozen sharpness fixture")
        if index > 0 and fixture_id != f"N2_SEEDED_{index - 1:03d}":
            raise ValueError(f"unexpected seeded row ordering at {index}")
        targets = [[int(letter) for letter in row] for row in source["targets"]]
        target_encoding = (
            "GLOBAL_XZ_KEYS" if source.get("kind") == "SHARPNESS"
            else "LOCAL_PAULI_CODES_Q0_FIRST"
        )
        row, target_pairs, dxx, dplus = _cost_row(
            p10,
            r6p,
            r6o,
            fixture_id,
            targets,
            2,
            target_encoding=target_encoding,
            sharpness=(index == 0),
        )
        rows.append(row)
        if index == 0:
            terms = r6m._synthetic_terms(target_pairs)
            dp_witness = r6m.exact_r6m_matching(
                terms, r6m._SYNTHETIC_MATCHING, 2, list(range(6))
            )
            dxx_valid = bool(r6p.verify_dxx_witness(target_pairs, 2, dxx["witness"]))
            dplus_valid = bool(r6o.verify_dplus_witness(target_pairs, 2, dplus))
            if int(dp_witness["C_R6M"]) != row["C_DP"]:
                raise AssertionError("sharpness unrestricted witness cost mismatch")
            if not dxx_valid or not dplus_valid:
                raise AssertionError("sharpness author-stack witness verification failed")
            expected = source.get("source_object", {})
            if (
                int(expected.get("C_unrestricted_dp", -1)) != row["C_DP"]
                or int(expected.get("C_Dplus", -1)) != row["C_1"]
                or int(expected.get("dxx_witness", {}).get("C_Dxx", -1)) != row["C_2"]
            ):
                raise AssertionError("sharpness source-object cost binding failed")
            sharpness_evidence = {
                "fixture_id": fixture_id,
                "costs": {"C_DP": row["C_DP"], "C_2": row["C_2"], "C_1": row["C_1"]},
                "unrestricted_witness": dp_witness,
                "support_two_witness": dxx["witness"],
                "support_one_witness": dplus,
                "witness_checks": {
                    "unrestricted_cost_recomputed": True,
                    "support_two_witness_verified": dxx_valid,
                    "support_one_witness_verified": dplus_valid,
                    "strict_C_DP_below_C_1": row["C_DP"] < row["C_1"],
                },
            }
    r6m._local_table.cache_clear()
    cache = getattr(r6o, "_block_cache", None)
    if cache is not None:
        cache.clear()
    if sharpness_evidence is None:
        raise AssertionError("sharpness evidence was not produced")
    return rows, sharpness_evidence


def main(argv: list[str] | None = None) -> int:
    archive, fixture_path, result_path = _validated_paths(
        list(sys.argv[1:] if argv is None else argv)
    )
    if Path(sys.executable).resolve() != Path(PYTHON).resolve():
        raise ValueError(f"unexpected interpreter: {sys.executable}")
    if sys.version.split()[0] != "3.12.13":
        raise ValueError(f"unexpected Python version: {sys.version.split()[0]}")
    python_sha256 = _sha256_path(Path(sys.executable).resolve())
    if _sha256_path(fixture_path) != FIXTURE_SHA256:
        raise ValueError("small-domain fixture digest mismatch")
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    if fixture.get("candidate_ref") != CANDIDATE_REF:
        raise ValueError("fixture candidate ref mismatch")
    source_records = _verify_sources(archive)

    sys.addaudithook(_audit)
    network_control = _socket_negative_control()
    p10, r6m, r6p, r6o, module_files = _load_author_stack(archive)
    import numpy as np

    if np.__version__ != "2.3.5":
        raise ValueError(f"unexpected NumPy version: {np.__version__}")
    n1_rows = _run_n1(p10, r6m, r6p, r6o)
    n2_rows, sharpness = _run_n2(p10, r6m, r6p, r6o, fixture)
    output = {
        "schema_version": "q1-c1-lane-a-author-stack-adapter-v1",
        "protocol_id": PROTOCOL_ID,
        "protocol_version": PROTOCOL_VERSION,
        "candidate_ref": CANDIDATE_REF,
        "role": "FINITE_PRODUCTION_AUTHOR_STACK_ADAPTER",
        "input_digests": {
            "fixture": {"path": str(fixture_path), "sha256": FIXTURE_SHA256},
            "author_sources": source_records,
            "loaded_modules": module_files,
        },
        "interpreter": {
            "path": str(Path(sys.executable).resolve()),
            "python_version": sys.version.split()[0],
            "python_sha256": python_sha256,
            "numpy_version": np.__version__,
        },
        "network_control": {
            "socket_negative_control": network_control,
            "sandboxed": False,
        },
        "corpus": {
            "n1": {
                "generator": "itertools.product(range(4), repeat=6)",
                "row_count": len(n1_rows),
                "rows_sha256": _sha256_bytes(_canonical_bytes(n1_rows)),
                "rows": n1_rows,
            },
            "n2": {
                "row_order": "SHARPNESS_THEN_SEEDED_000_TO_063",
                "row_count": len(n2_rows),
                "rows_sha256": _sha256_bytes(_canonical_bytes(n2_rows)),
                "rows": n2_rows,
            },
        },
        "sharpness_evidence": sharpness,
        "summary": {
            "rows": len(n1_rows) + len(n2_rows),
            "C_2_equals_C_DP_rows": sum(
                row["C_2_equals_C_DP"] for row in n1_rows + n2_rows
            ),
            "C_1_strictly_above_C_DP_rows": sum(
                row["C_1"] > row["C_DP"] for row in n1_rows + n2_rows
            ),
        },
        "authority_limits": {
            "fixture_authority": "n=1 exhaustive plus exactly 65 declared n=2 rows",
            "grants_arbitrary_n_production_equivalence": False,
            "grants_mathematical_authority": False,
            "grants_novelty_authority": False,
            "grants_physical_resource_authority": False,
            "grants_runtime_superiority_authority": False,
            "grants_submission_authority": False,
            "grants_merge_authority": False,
        },
    }
    _exclusive_json(result_path, output)
    print(
        "Q1_C1_LANE_A_AUTHOR_STACK_ADAPTER="
        + json.dumps(
            {
                "result_path": str(result_path),
                "result_sha256": _sha256_path(result_path),
                "rows": output["summary"]["rows"],
                "authority": "FINITE_FIXTURE_ONLY",
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
