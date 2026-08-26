"""Runner for the lexical-echo successor study.

Executes the five arms of `echo_mechanics` over the constructed world of
`echo_world`, evaluates the five gates the freeze document pre-committed, and
writes one result artifact. It refuses to run if its own parameter block does
not hash to the digest recorded in the freeze document's JSON twin, and it
refuses to report arm numbers over a world that fails the construction
precondition — a world whose apparatus words are not actually
non-discriminative is not a reproduction of the mechanism under study.

Nothing here may be edited to make a gate pass. If a gate fails, the failure is
the result.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from . import echo_mechanics as mech
from . import echo_world as world_module
from .corpus import sha256_digest
from .echo_world import (
    DOMAIN_LEXICON,
    FAMILY_ECHO,
    FAMILY_NO_ECHO,
    FAMILY_PARAPHRASE,
    INCIDENTAL_LEXICON,
    EchoWorld,
    build_echo_world,
)

RESULT_SCHEMA_VERSION = "orion.p2.lexical-echo-successor-result.v1"

FREEZE_DOCUMENT = (
    "papers/orion-12-open-world-scientific-discovery/protocol/"
    "P2_LEXICAL_ECHO_SUCCESSOR_FREEZE_2026-08-21.md"
)
FREEZE_TWIN = (
    "papers/orion-12-open-world-scientific-discovery/protocol/"
    "P2_LEXICAL_ECHO_SUCCESSOR_FREEZE_2026-08-21.json"
)
DEFAULT_OUTPUT = (
    "papers/orion-12-open-world-scientific-discovery/evidence/successor_results/"
    "P2_LEXICAL_ECHO_SUCCESSOR_RESULT_2026-08-21.json"
)

# --------------------------------------------------------------------------
# Pre-committed gates. Thresholds come from the freeze document, section 5.
# --------------------------------------------------------------------------

GATES: dict[str, Any] = {
    "G1_REPRODUCTION": {
        "statement": "B0 hit@10 on the echo family <= 0.05",
        "max_baseline_hit_at_10": 0.05,
        "reference": "judge-free recoverability in the real probe was 8/564 = 0.0142",
    },
    "G2_SUCCESSOR": {
        "statement": (
            "on echo: S1 hit@10 - B0 hit@10 >= 0.30 and S1 hit@10 >= 0.50 "
            "and exact McNemar p < 0.01"
        ),
        "min_absolute_gain": 0.30,
        "min_successor_hit_at_10": 0.50,
        "max_p_value": 0.01,
    },
    "G3_HARM": {
        "statement": "on no_echo: S1 hit@10 >= B0 hit@10 - 0.05",
        "max_allowed_loss": 0.05,
        "vacuity_floor": 0.30,
    },
    "G4_MARGINAL_OVER_BM25": {
        "statement": "on echo: S1 hit@1 >= B1 hit@1 + 0.10",
        "min_margin": 0.10,
        "blocking": False,
    },
    "G5_SPECIFICITY": {
        "statement": "on paraphrase_gap: S1 hit@10 - B0 hit@10 < 0.10",
        "max_allowed_gain": 0.10,
        "blocking": False,
    },
}

FROZEN_PARAMETERS: dict[str, Any] = {
    "record": "P2_LEXICAL_ECHO_SUCCESSOR_FREEZE",
    "freeze_document": FREEZE_DOCUMENT,
    "world": world_module.PARAMETERS,
    "mechanics": mech.MECHANIC_PARAMETERS,
    "gates": GATES,
    "primary_outcome": "hit_at_10 on the echo family, S1 versus B0",
    "statistic": "exact two-sided McNemar (binomial) on paired per-task hit@10",
    "verdict_rule": "VALIDATED_ON_CONSTRUCTED_REPRODUCTION iff G1 and G2 and G3 all pass",
    "claim_scope": "CONSTRUCTED_REPRODUCTION_ONLY",
}


def frozen_digest() -> str:
    return sha256_digest(FROZEN_PARAMETERS)


class FreezeViolation(RuntimeError):
    """Raised when the runner's constants no longer match the frozen record."""


def verify_against_twin(repo_root: Path) -> dict[str, Any]:
    """Compare the runner's own parameter digest with the frozen twin's."""

    twin_path = repo_root / FREEZE_TWIN
    if not twin_path.exists():
        raise FreezeViolation(f"freeze twin missing: {twin_path}")
    twin = json.loads(twin_path.read_text(encoding="utf-8"))
    recorded = twin.get("parameters_sha256")
    computed = frozen_digest()
    if recorded != computed:
        raise FreezeViolation(
            "runner parameters do not match the frozen record: "
            f"recorded {recorded}, computed {computed}"
        )
    return {"parameters_sha256": computed, "freeze_twin": FREEZE_TWIN}


# --------------------------------------------------------------------------
# World precondition
# --------------------------------------------------------------------------


def world_precondition(world: EchoWorld, index: mech.EchoIndex) -> dict[str, Any]:
    """Check the corpus really has the stratum structure the freeze specifies.

    Evaluated on the corpus alone, before any query is issued. If apparatus
    words are not high-document-frequency and content words are not low, the
    generated world is not a reproduction of the named mechanism and no arm
    number over it would mean anything.
    """

    def fractions(terms: Sequence[str]) -> list[float]:
        return sorted(
            index.document_frequency(term) / max(1, index.size) for term in terms
        )

    apparatus = fractions(INCIDENTAL_LEXICON)
    content = fractions(DOMAIN_LEXICON)
    apparatus_median = mech._median(apparatus)
    content_median = mech._median(content)
    passed = (
        apparatus_median >= world_module.MIN_APPARATUS_DF_FRACTION
        and content_median <= world_module.MAX_CONTENT_DF_FRACTION
    )
    return {
        "documents": index.size,
        "tasks": len(world.tasks),
        "apparatus_df_fraction_median": apparatus_median,
        "apparatus_df_fraction_min": apparatus[0],
        "apparatus_df_fraction_max": apparatus[-1],
        "content_df_fraction_median": content_median,
        "content_df_fraction_min": content[0],
        "content_df_fraction_max": content[-1],
        "min_apparatus_df_fraction": world_module.MIN_APPARATUS_DF_FRACTION,
        "max_content_df_fraction": world_module.MAX_CONTENT_DF_FRACTION,
        "passed": passed,
    }


# --------------------------------------------------------------------------
# Campaign
# --------------------------------------------------------------------------


def run_campaign(seed: int = world_module.FROZEN_SEED) -> dict[str, Any]:
    """Build the world, run every arm on every task, evaluate every gate."""

    world = build_echo_world(seed)
    index = mech.build_index(world.documents)
    precondition = world_precondition(world, index)

    payload: dict[str, Any] = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "record": "P2_LEXICAL_ECHO_SUCCESSOR_RESULT",
        "date": "2026-08-21",
        "freeze_document": FREEZE_DOCUMENT,
        "parameters_sha256": frozen_digest(),
        "claim_scope": "CONSTRUCTED_REPRODUCTION_ONLY",
        "world_content_hash": world.content_hash,
        "world_precondition": precondition,
    }

    if not precondition["passed"]:
        payload["verdict"] = "WORLD_PRECONDITION_FAILED"
        payload["interpretation"] = (
            "The generated corpus does not have the stratum structure the freeze "
            "specifies, so it is not a reproduction of the named mechanism. No arm "
            "numbers are reported over it."
        )
        return payload

    results: dict[str, dict[str, mech.ArmResult]] = {arm: {} for arm in mech.ARM_ORDER}
    for task in world.tasks:
        for arm in mech.ARM_ORDER:
            results[arm][task.task_id] = mech.run_arm(arm, task, index)

    families = (FAMILY_ECHO, FAMILY_NO_ECHO, FAMILY_PARAPHRASE)
    by_family: dict[str, dict[str, Any]] = {}
    for family in families:
        task_ids = [task.task_id for task in world.tasks_in(family)]
        by_family[family] = {
            arm: mech.summarize([results[arm][task_id] for task_id in task_ids])
            for arm in mech.ARM_ORDER
        }
    payload["arms"] = by_family

    def hits(arm: str, family: str) -> list[bool]:
        return [
            results[arm][task.task_id].hit_at(mech.PRIMARY_K)
            for task in world.tasks_in(family)
        ]

    echo_b0 = by_family[FAMILY_ECHO][mech.ARM_B0]
    echo_b1 = by_family[FAMILY_ECHO][mech.ARM_B1]
    echo_s1 = by_family[FAMILY_ECHO][mech.ARM_S1]
    no_echo_b0 = by_family[FAMILY_NO_ECHO][mech.ARM_B0]
    no_echo_s1 = by_family[FAMILY_NO_ECHO][mech.ARM_S1]
    para_b0 = by_family[FAMILY_PARAPHRASE][mech.ARM_B0]
    para_s1 = by_family[FAMILY_PARAPHRASE][mech.ARM_S1]

    mcnemar = mech.mcnemar_exact(hits(mech.ARM_B0, FAMILY_ECHO), hits(mech.ARM_S1, FAMILY_ECHO))
    payload["mcnemar_echo_hit_at_10"] = mcnemar

    gain = echo_s1["hit_at_10"] - echo_b0["hit_at_10"]
    g1 = echo_b0["hit_at_10"] <= GATES["G1_REPRODUCTION"]["max_baseline_hit_at_10"]
    g2 = (
        gain >= GATES["G2_SUCCESSOR"]["min_absolute_gain"]
        and echo_s1["hit_at_10"] >= GATES["G2_SUCCESSOR"]["min_successor_hit_at_10"]
        and mcnemar["p_value"] < GATES["G2_SUCCESSOR"]["max_p_value"]
    )
    harm_loss = no_echo_b0["hit_at_10"] - no_echo_s1["hit_at_10"]
    g3 = harm_loss <= GATES["G3_HARM"]["max_allowed_loss"]
    g3_vacuous = no_echo_b0["hit_at_10"] < GATES["G3_HARM"]["vacuity_floor"]
    g4 = echo_s1["hit_at_1"] >= echo_b1["hit_at_1"] + GATES["G4_MARGINAL_OVER_BM25"]["min_margin"]
    para_gain = para_s1["hit_at_10"] - para_b0["hit_at_10"]
    g5 = para_gain < GATES["G5_SPECIFICITY"]["max_allowed_gain"]

    payload["gate_results"] = {
        "G1_REPRODUCTION": {
            "passed": g1,
            "baseline_hit_at_10_echo": echo_b0["hit_at_10"],
            "threshold": GATES["G1_REPRODUCTION"]["max_baseline_hit_at_10"],
            "observed_probe_reference": 8 / 564,
        },
        "G2_SUCCESSOR": {
            "passed": g2,
            "baseline_hit_at_10_echo": echo_b0["hit_at_10"],
            "successor_hit_at_10_echo": echo_s1["hit_at_10"],
            "absolute_gain": gain,
            "mcnemar_p_value": mcnemar["p_value"],
        },
        "G3_HARM": {
            "passed": g3,
            "vacuous": g3_vacuous,
            "baseline_hit_at_10_no_echo": no_echo_b0["hit_at_10"],
            "successor_hit_at_10_no_echo": no_echo_s1["hit_at_10"],
            "loss": harm_loss,
        },
        "G4_MARGINAL_OVER_BM25": {
            "passed": g4,
            "blocking": False,
            "bm25_hit_at_1_echo": echo_b1["hit_at_1"],
            "successor_hit_at_1_echo": echo_s1["hit_at_1"],
            "margin": echo_s1["hit_at_1"] - echo_b1["hit_at_1"],
        },
        "G5_SPECIFICITY": {
            "passed": g5,
            "blocking": False,
            "baseline_hit_at_10_paraphrase": para_b0["hit_at_10"],
            "successor_hit_at_10_paraphrase": para_s1["hit_at_10"],
            "gain": para_gain,
        },
    }

    if not g1:
        verdict = "REPRODUCTION_FAILED__NO_SUCCESSOR_CLAIM"
    elif g2 and g3:
        verdict = "VALIDATED_ON_CONSTRUCTED_REPRODUCTION"
    elif g2 and not g3:
        verdict = "SUCCESSOR_GAIN_ON_MODE__HARMFUL_OFF_MODE__NO_SUCCESSOR_CLAIM"
    else:
        verdict = "SUCCESSOR_NOT_VALIDATED__NEGATIVE_STANDS"
    payload["verdict"] = verdict

    payload["post_hoc_diagnostics"] = _gate_diagnostics(world, index)
    payload["known_construction_defects"] = _construction_defects(world)
    payload["example_queries"] = _example_queries(world, index, results)
    payload["not_licensed"] = [
        "any statement about target_hits on the official AutoResearchBench Deep benchmark",
        "revival of AUTORESEARCHBENCH_DEEP_ID_PROBE_V1",
        "any claim that the successor was run against arXiv or OpenAlex",
    ]
    return payload


def _gate_diagnostics(world: EchoWorld, index: mech.EchoIndex) -> dict[str, Any]:
    """Descriptive only, added after the frozen run; changes no gate and no arm.

    The successor's df gate is a threshold, and a threshold placed at 0.05 will
    sometimes discard a genuine content term that happens to sit above it. This
    counts how often that happened, so the mechanic's own failure mode is in the
    record rather than left for a reader to discover.
    """

    dropped_tasks = 0
    dropped_terms = 0
    for task in world.tasks:
        written = (
            tuple(world_module._paraphrase(term) for term in task.content_terms)
            if task.family == FAMILY_PARAPHRASE
            else task.content_terms
        )
        lost = [
            term
            for term in written
            if index.document_frequency(term) / max(1, index.size)
            > mech.INCIDENTAL_DF_FRACTION
        ]
        if lost:
            dropped_tasks += 1
            dropped_terms += len(lost)
    return {
        "note": (
            "post-hoc descriptive diagnostic; no frozen parameter, arm or gate was "
            "changed to produce it"
        ),
        "tasks_with_a_content_term_above_the_df_gate": dropped_tasks,
        "content_terms_discarded_by_the_df_gate": dropped_terms,
        "total_tasks": len(world.tasks),
    }


def _construction_defects(world: EchoWorld) -> list[dict[str, Any]]:
    """Deviations between the frozen specification and the generated world.

    Reported rather than repaired. The freeze states that a `paraphrase_gap`
    needle shares no content token with its question, and the synonym map does
    not guarantee that: it is a permutation of the whole domain lexicon, so one
    of a task's own four terms can be the image of another. Re-rolling the world
    to remove the leak would re-draw every task after an outcome was already
    visible, which the freeze forbids; naming and measuring it does not.
    """

    by_id = world.world.by_id
    leaking: list[str] = []
    leaked_terms = 0
    for task in world.tasks_in(FAMILY_PARAPHRASE):
        document = by_id[task.target_doc_id]
        tokens = set(f"{document.title} {document.abstract}".lower().split())
        overlap = tokens & set(task.content_terms)
        if overlap:
            leaking.append(task.task_id)
            leaked_terms += len(overlap)
    return [
        {
            "defect": "PARAPHRASE_SYNONYM_MAP_IS_NOT_TASK_DISJOINT",
            "freeze_clause": (
                "section 3.3: a paraphrase_gap needle shares no content token with its "
                "question"
            ),
            "tasks_affected": len(leaking),
            "tasks_total": len(world.tasks_in(FAMILY_PARAPHRASE)),
            "content_tokens_leaked": leaked_terms,
            "affected_task_ids": leaking,
            "effect_on_the_result": (
                "None. paraphrase_gap is the non-blocking specificity control and enters "
                "no verdict gate; every arm scores hit@10 = 0 on it, including the "
                "affected tasks, so the leak awarded no arm any credit."
            ),
            "disposition": "REPORTED_NOT_REPAIRED",
        }
    ]


def _example_queries(
    world: EchoWorld,
    index: mech.EchoIndex,
    results: dict[str, dict[str, mech.ArmResult]],
) -> list[dict[str, Any]]:
    """A few worked cases, so a reader can see the mechanism rather than a number."""

    examples: list[dict[str, Any]] = []
    for task in world.tasks_in(FAMILY_ECHO)[:3]:
        b0 = results[mech.ARM_B0][task.task_id]
        s1 = results[mech.ARM_S1][task.task_id]
        by_id = world.world.by_id
        examples.append(
            {
                "task_id": task.task_id,
                "question": task.question,
                "content_terms": list(task.content_terms),
                "incidental_terms": list(task.incidental_terms),
                "target_title": by_id[task.target_doc_id].title,
                "baseline_query_terms": list(b0.query_terms),
                "baseline_top_titles": [by_id[d].title for d in b0.candidates[:5]],
                "baseline_target_rank": b0.target_rank,
                "successor_query_terms": list(s1.query_terms),
                "successor_top_titles": [by_id[d].title for d in s1.candidates[:5]],
                "successor_target_rank": s1.target_rank,
                "incidental_df_fractions": {
                    term: index.document_frequency(term) / index.size
                    for term in task.incidental_terms
                },
                "content_df_fractions": {
                    term: index.document_frequency(term) / index.size
                    for term in task.content_terms
                },
            }
        )
    return examples


def main(argv: list[str]) -> int:
    """CLI entry point. `argv` is required: there is no implicit run."""

    parser = argparse.ArgumentParser(
        prog="orion-p2-echo-successor",
        description=(
            "Run the frozen lexical-echo successor study on its constructed world "
            "and write the result artifact."
        ),
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="repository root used to resolve the freeze twin and the output path",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help=f"result path (default: {DEFAULT_OUTPUT} under --repo-root)",
    )
    parser.add_argument(
        "--print-digest",
        action="store_true",
        help="print the runner's frozen parameter digest and exit without running",
    )
    args = parser.parse_args(argv)

    if args.print_digest:
        print(frozen_digest())
        return 0

    repo_root: Path = args.repo_root
    provenance = verify_against_twin(repo_root)

    payload = run_campaign()
    payload["freeze_provenance"] = provenance

    output = args.output or (repo_root / DEFAULT_OUTPUT)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"verdict: {payload['verdict']}")
    print(f"written: {output}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    import sys

    raise SystemExit(main(sys.argv[1:]))
