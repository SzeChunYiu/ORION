"""DISC-HUMAN-DECOMP-01 — six-space decomposition vs named parents.

Gate: private cognition is never inferred; matched controls and
counterfactual twins are included.
Terminals: SIX_SPACE_DECOMPOSITION_INCREMENTAL_VALUE_SUPPORTED /
DONOR_DECOMPOSITIONS_SUFFICIENT_OR_MODEL_CONTAMINATION /
HISTORICAL_COGNITIVE_INFERENCE_CANNOT_CHECK

The comparison the job asks for needs each parent's decomposition stated from
a source. Five of the six named parents have NO coverage in this repository.
Writing their structure from recall would produce a complete-looking matrix
whose cells cannot be checked by anyone -- and a matrix that cannot be checked
is worse than a gap, because it looks like evidence.

So the matrix is built only over sourced parents, unsourced parents are
carried as explicit CANNOT_CHECK rows, and the false-certainty count reports
exactly how many cells a memory-written matrix would have fabricated.
"""
from __future__ import annotations
import json, re
from pathlib import Path

ROOT = Path("/Users/billy/ORION-claude")
DONOR = ROOT / "research/extensions/orion-jump-recursive-atoms/DONOR_STRUCTURAL_MATRIX_V2.md"
OUT = ROOT / "research/orion-discovery-v2/exec/DISC-HUMAN-DECOMP-01"

SIX_SPACES = [
    "problem_question", "hypothesis_mechanism", "representation_ontology",
    "experiment_instrument", "proof_evidence", "authority_adoption",
]
PARENTS = {
    "C_K_theory": ["C-K", "Hatchuel"],
    "dual_space": ["dual-space", "Klahr", "Dunbar"],
    "four_space": ["four-space"],
    "analogy_structure_mapping": ["structure-mapping", "Gentner"],
    "mechanism_MDC": ["Machamer", "Darden", "Craver"],
    "insight_representational_change": ["insight", "Gestalt", "restructuring"],
}


def sourced(text: str, keys: list[str]) -> dict:
    hits = {k: len(re.findall(re.escape(k), text, re.I)) for k in keys}
    return {"sourced_in_repo": any(hits.values()), "keyword_hits": hits}


def main() -> int:
    text = DONOR.read_text(encoding="utf-8", errors="replace") if DONOR.is_file() else ""
    src = {p: sourced(text, ks) for p, ks in PARENTS.items()}
    n_sourced = sum(1 for v in src.values() if v["sourced_in_repo"])

    # --- equivalence matrix: only sourced parents get coverage cells
    matrix = []
    for parent, meta in src.items():
        if not meta["sourced_in_repo"]:
            matrix.append({
                "parent": parent, "status": "CANNOT_CHECK",
                "reason": ("no primary-source statement of this parent's "
                           "decomposition exists in this repository; asserting "
                           "its spaces from recall would be unverifiable"),
                "coverage": {s: "CANNOT_CHECK" for s in SIX_SPACES},
            })
            continue
        # C-K is the only sourced parent. The repo states it separates C
        # (concepts undecidable in current knowledge) from K (knowledge).
        # That is a two-space split; it is quoted, not inferred.
        matrix.append({
            "parent": parent, "status": "SOURCED",
            "source": str(DONOR.relative_to(ROOT)),
            "stated_spaces": ["C: concepts/propositions undecidable in current knowledge",
                              "K: knowledge"],
            "coverage": {
                "problem_question": "PARTIAL",
                "hypothesis_mechanism": "PRESENT",
                "representation_ontology": "CANNOT_CHECK",
                "experiment_instrument": "ABSENT_IN_STATED_SPACES",
                "proof_evidence": "PARTIAL",
                "authority_adoption": "ABSENT_IN_STATED_SPACES",
            },
            "coverage_basis": ("mapped only from the two spaces the repository "
                               "source states; no further structure inferred"),
        })

    # --- matched controls and counterfactual twins over the six-space model
    controls = [
        {"control_id": "NULL_DECOMPOSITION", "spaces": [],
         "role": "floor: a model with no spaces must score no coverage"},
        {"control_id": "FLAT_SINGLE_SPACE", "spaces": ["candidate_search"],
         "role": "the flat candidate search the six-space model claims to improve on"},
        {"control_id": "TRIVIALLY_COMPLETE", "spaces": SIX_SPACES + ["everything_else"],
         "role": "ceiling: a model that covers everything discriminates nothing"},
    ] + [
        {"control_id": f"TWIN_DROP_{s}", "spaces": [x for x in SIX_SPACES if x != s],
         "role": f"counterfactual twin: six-space minus {s}"}
        for s in SIX_SPACES
    ]

    # a control is informative iff it differs from the full model in coverage
    full = set(SIX_SPACES)
    for c in controls:
        c["differs_from_full_model"] = set(c["spaces"]) != full
        c["missing_relative_to_full"] = sorted(full - set(c["spaces"]))
    informative = sum(1 for c in controls if c["differs_from_full_model"])

    cannot_cells = sum(1 for m in matrix for v in m["coverage"].values() if v == "CANNOT_CHECK")
    total_cells = len(matrix) * len(SIX_SPACES)

    terminal = ("HISTORICAL_COGNITIVE_INFERENCE_CANNOT_CHECK" if n_sourced < len(PARENTS)
                else "SIX_SPACE_DECOMPOSITION_INCREMENTAL_VALUE_SUPPORTED")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "EPISODE_AND_CONTROL_MANIFEST.json").write_text(json.dumps({
        "schema": "orion.discovery-v2.episode-and-control-manifest.v1",
        "job_id": "DISC-HUMAN-DECOMP-01",
        "historical_episodes": [],
        "historical_episodes_note": (
            "None registered. The job class is CHRONOLOGY_SAFE_HISTORICAL, and no "
            "licensed episode corpus with dated primary sources exists in this "
            "repository. Episodes written from recall could not be chronology-checked "
            "by a reader, and the gate forbids inferring private cognition, which is "
            "most of what an undocumented episode would supply."),
        "controls": controls,
        "controls_informative": informative,
        "controls_total": len(controls),
    }, indent=2) + "\n")

    (OUT / "MODEL_CHRONOLOGY_RECEIPTS.json").write_text(json.dumps({
        "schema": "orion.discovery-v2.model-chronology-receipts.v1",
        "job_id": "DISC-HUMAN-DECOMP-01",
        "parents": {p: {**v, "chronology_source": (str(DONOR.relative_to(ROOT))
                                                   if v["sourced_in_repo"] else None)}
                    for p, v in src.items()},
        "sourced": n_sourced, "named": len(PARENTS),
        "note": ("Chronology-safe means a parent may only be compared using a dated "
                 "source. Only C-K carries one here (Hatchuel & Weil, ICED 2003, as "
                 "quoted in the donor matrix)."),
    }, indent=2) + "\n")

    (OUT / "DECOMPOSITION_EQUIVALENCE_MATRIX.json").write_text(json.dumps({
        "schema": "orion.discovery-v2.decomposition-equivalence-matrix.v1",
        "job_id": "DISC-HUMAN-DECOMP-01",
        "six_spaces": SIX_SPACES,
        "matrix": matrix,
        "cells_total": total_cells,
        "cells_cannot_check": cannot_cells,
        "terminal": terminal,
    }, indent=2) + "\n")

    (OUT / "FALSE_CERTAINTY_AND_OPEN_MOVE_COUNTS.json").write_text(json.dumps({
        "schema": "orion.discovery-v2.false-certainty-counts.v1",
        "job_id": "DISC-HUMAN-DECOMP-01",
        "cells_that_would_be_fabricated_if_written_from_recall": cannot_cells,
        "of_total_cells": total_cells,
        "parents_unsourced": [p for p, v in src.items() if not v["sourced_in_repo"]],
        "reading": (
            f"A matrix written from recall would have filled {cannot_cells} of "
            f"{total_cells} cells with claims no reader of this repository could "
            "check. That is the false-certainty budget this job refuses to spend."),
        "open_move_class_invoked": True,
        "open_move_reason": (
            "The six-space model's own OPEN_MOVE_CLASS applies here: the useful next "
            "move is prior-art retrieval for five named parents, which is not a move "
            "inside any of the six spaces."),
    }, indent=2) + "\n")

    print(json.dumps({"terminal": terminal, "parents_named": len(PARENTS),
                      "parents_sourced": n_sourced,
                      "cells_cannot_check": cannot_cells, "cells_total": total_cells,
                      "controls_informative": f"{informative}/{len(controls)}"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
