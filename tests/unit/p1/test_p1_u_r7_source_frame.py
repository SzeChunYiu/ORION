from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
R7 = ROOT / "research" / "claim_expansion" / "p1" / "gpt_r7"


def _load(filename: str, name: str):
    spec = importlib.util.spec_from_file_location(name, R7 / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _identity(cluster: str):
    return {
        "normalized_url": f"https://example.invalid/{cluster}",
        "doi": f"10.9999/{cluster}",
        "stable_artifact_id": cluster,
        "title_first_author_year": f"title::{cluster}::author::2024",
        "official_repository_identity": f"repo::{cluster}",
        "shared_dataset_or_project_family": f"project::{cluster}",
    }


def _complete_frame(module):
    pairs = []
    for family in sorted(module.FAMILIES):
        for domain in sorted(module.DOMAINS):
            for index in range(module.PAIR_QUOTA):
                cluster = f"pair-{family}-{domain}-{index}"
                pairs.append(
                    {
                        "cluster_id": cluster,
                        "family": family,
                        "domain": domain,
                        "query_ids": [f"query-{family}-{domain}"],
                        "source_identity": _identity(cluster),
                        "members": {"adverse": f"{cluster}-a", "control": f"{cluster}-c"},
                    }
                )
    unresolved = []
    for domain in sorted(module.DOMAINS):
        for index in range(module.UNRESOLVED_QUOTA):
            cluster = f"unresolved-{domain}-{index}"
            unresolved.append(
                {
                    "cluster_id": cluster,
                    "domain": domain,
                    "query_ids": [f"query-unresolved-{domain}"],
                    "source_identity": _identity(cluster),
                }
            )
    return {"pairs": pairs, "unresolved": unresolved}


def test_query_frame_is_exact_deterministic_and_outcome_blind():
    module = _load("query_frame.py", "p1_r7_query_frame")
    first = module.build_query_frame()
    second = module.build_query_frame()
    assert first == second
    assert module.frame_digest(first) == module.frame_digest(second)
    assert len(first["pair_queries"]) == 8 * 4 * 4
    assert len(first["unresolved_queries"]) == 4 * 4 * 2
    assert first["sampling"]["outcome_access_during_search_eligibility_or_sampling"] is False


def test_complete_192_pair_64_unresolved_frame_passes():
    module = _load("source_frame.py", "p1_r7_source_frame")
    result = module.validate_source_frame(_complete_frame(module))
    assert result["complete"], result["errors"]
    assert result["terminal"] == "P1_R7_SOURCE_FRAME_COMPLETE"


def test_sparse_cell_cannot_be_backfilled_from_an_easier_cell():
    module = _load("source_frame.py", "p1_r7_source_frame_sparse")
    frame = _complete_frame(module)
    removed = frame["pairs"].pop(0)
    donor = dict(frame["pairs"][-1])
    donor["cluster_id"] = "backfill"
    donor["source_identity"] = _identity("backfill")
    frame["pairs"].append(donor)
    result = module.validate_source_frame(frame)
    assert not result["complete"]
    assert result["terminal"] == "P1_R7_CANNOT_CHECK_SOURCE_UNIVERSE"
    assert any(removed["family"] in error and removed["domain"] in error for error in result["errors"])


def test_source_family_alias_and_replication_overlap_fail():
    module = _load("source_frame.py", "p1_r7_source_frame_alias")
    frame = _complete_frame(module)
    frame["pairs"][1]["source_identity"]["doi"] = frame["pairs"][0]["source_identity"]["doi"]
    result = module.validate_source_frame(frame)
    assert not result["complete"]
    assert any("source identity" in error for error in result["errors"])

    clean = _complete_frame(module)
    excluded = {f"doi:{clean['pairs'][0]['source_identity']['doi']}"}
    result = module.validate_source_frame(clean, excluded_identity_tokens=excluded)
    assert not result["complete"]
    assert any("overlaps excluded" in error for error in result["errors"])


def test_missing_unresolved_sources_do_not_become_zero_false_resolutions():
    module = _load("source_frame.py", "p1_r7_source_frame_unresolved")
    frame = _complete_frame(module)
    frame["unresolved"] = frame["unresolved"][:-1]
    result = module.validate_source_frame(frame)
    assert not result["complete"]
    assert not result["checks"]["exact_unresolved_count"]

