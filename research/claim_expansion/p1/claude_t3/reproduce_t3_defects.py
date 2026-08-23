"""Reproduce the three P1-U-T3 guard defects, with numbers, before repairing them.

Read-only with respect to the repository: it loads the frozen corpus, re-derives
the stratifier keys the broken guards would have built, and evaluates the
predecessor ``_leakage_free`` body verbatim on synthetic inputs.  It writes only
where ``--out`` points.

Defect 1 and 2 are reproduced against ``gpt_r6/evaluate_native.py``.
Defect 3 is reproduced against the predecessor implementation in
``research/claim_expansion/p1/gpt_r6_native_primary.py`` on the shadow ref
``origin/shadow/p1-u-gpt-r6-native-runtime-20260820``; that file is not on this
branch, so the three-line function body is inlined here and cited.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

HERE = Path(__file__).resolve().parent
EVAL_PATH = HERE.parent / "gpt_r6" / "evaluate_native.py"

PREDECESSOR_SOURCE = (
    "research/claim_expansion/p1/gpt_r6_native_primary.py:211-213 "
    "(ref origin/shadow/p1-u-gpt-r6-native-runtime-20260820)"
)


def _load(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(name, None)
        raise
    return module


def _predecessor_leakage_free(
    native: Mapping[str, object], forbidden_tokens: tuple[str, ...]
) -> bool:
    """Verbatim predecessor body. Do not repair this function; it is the exhibit."""
    serialized = json.dumps(native.get("request_payloads", []), sort_keys=True)
    return all(not token or token not in serialized for token in forbidden_tokens)


def defect_1_class_stratifier(evaluator: Any, pairs: list[Mapping[str, object]]) -> dict:
    as_is: dict[str, list[float]] = defaultdict(list)
    for pair in pairs:
        # evaluate_native.py:338 before the repair
        as_is[str(pair["adverse_class"])].append(0.0)
    by_gold: Counter[str] = Counter()
    for pair in pairs:
        for member in ("adverse", "control"):
            by_gold[str(pair[member]["gold_class"])] += 1
    return {
        "broken_stratifier_key": 'str(pair["adverse_class"]) for both members',
        "strata_created": sorted(as_is),
        "n_strata": len(as_is),
        "rows_per_stratum": {k: len(v) for k, v in sorted(as_is.items())},
        "control_class_label": evaluator.CONTROL,
        "control_stratum_present": evaluator.CONTROL in as_is,
        "control_episodes_in_corpus": by_gold[evaluator.CONTROL],
        "strata_that_should_exist_per_member_gold": dict(sorted(by_gold.items())),
        "episodes_filed_under_own_gold_class": 0,
    }


def defect_2_domain_stratifier(
    evaluator: Any,
    pairs: list[Mapping[str, object]],
    unresolved: list[Mapping[str, object]],
) -> dict:
    counts: Counter[str] = Counter()
    for pair in pairs:
        counts[str(pair["actual_domain"])] += 2
    for episode in unresolved:
        counts[str(episode["actual_domain"])] += 1
    floor = float(evaluator.PROTOCOL["decision_rule"]["domain_or_class_noninferiority_floor"])
    total = sum(counts.values())
    min_n = next((n for n in range(1, total + 1) if -1.0 / n >= floor), 0)
    sizes = Counter(counts.values())
    return {
        "n_strata": len(counts),
        "episodes_per_stratum": dict(sorted(counts.items())),
        "stratum_size_histogram": {str(k): v for k, v in sorted(sizes.items())},
        "n_episodes": total,
        "frozen_floor": floor,
        "smallest_negative_mean_attainable_by_size": {
            str(n): -1.0 / n for n in sorted(sizes)
        },
        "min_stratum_size_for_the_floor_to_admit_one_lost_episode": min_n,
        "stratum_sizes_present_that_are_large_enough": [
            n for n in sorted(sizes) if min_n and n >= min_n
        ],
        "floor_is_arithmetically_the_zero_loss_rule": all(
            -1.0 / n < floor for n in sizes
        ),
    }


def defect_3_leakage_guard(evaluator: Any) -> dict:
    tokens = ("R5-SEARCH-P1-A", "R5-SEARCH-P1", "SEARCH-P1", "SEARCH_OR_EVIDENCE")
    cases = {
        "request_payloads key absent": {},
        "request_payloads is None": {"request_payloads": None},
        "payloads present and clean": {"request_payloads": [{"user": "nothing here"}]},
        "payloads present and leaking": {
            "request_payloads": [{"user": "R5-SEARCH-P1-A"}]
        },
        "payloads leaking only pair role": {
            "request_payloads": [{"user": '{"pair_role": "adverse"}'}]
        },
    }
    behaviour = {}
    for name, native in cases.items():
        try:
            behaviour[name] = {"returns": _predecessor_leakage_free(native, tokens)}
        except Exception as exc:  # noqa: BLE001 - the exhibit may raise
            behaviour[name] = {"raised": f"{type(exc).__name__}: {exc}"}
    return {
        "predecessor_source": PREDECESSOR_SOURCE,
        "call_site_forbidden_tuple": [
            "str(ep['id'])",
            "pair_id",
            "query_id",
            "adverse_class",
            "str(ep['gold_class'])",
        ],
        "pair_role_in_forbidden_tokens": False,
        "behaviour": behaviour,
        "fail_open_on_absent_key": behaviour["request_payloads key absent"]["returns"],
        "guard_defined_in_evaluate_native_before_repair": False,
        "none_sentinel_trap": {
            "not None": not None,
            "int(not None)": int(not None),
            "note": (
                "a None sentinel for CANNOT_CHECK is read by a two-valued caller as an "
                "ordinary boolean; the repaired verdict raises TypeError on bool() instead"
            ),
        },
        "repaired_guard_now_present": hasattr(evaluator, "leakage_audit"),
    }


def measured_provider_payload_leak(evaluator: Any, pairs: list[Mapping[str, object]]) -> dict:
    """What a working guard finds on this evaluator, measured rather than asserted."""
    pair = pairs[0]
    episode = pair["adverse"]
    with evaluator.record_provider_payloads() as sink:
        evaluator.NATIVE.run_native_ard(
            episode, evidence_note=str(pair["pair_evidence"]["source_claim"])
        )
    blob = json.dumps(list(sink), sort_keys=True)
    probes = {
        "episode_id": str(episode["id"]),
        "pair_id": str(pair["pair_id"]),
        "query_id": str(pair["query_id"]),
        "source_id": str(pair["source_id"]),
        "adverse_class_label": str(pair["adverse_class"]),
        "gold_class_label": str(episode["gold_class"]),
    }
    return {
        "episode": str(episode["id"]),
        "provider_calls": len(sink),
        "payload_bytes": len(blob),
        "token_present_in_candidate_visible_payload": {
            name: token in blob for name, token in sorted(probes.items())
        },
        "pair_role_recoverable_from_episode_id_suffix": any(
            str(episode["id"]).endswith(suffix)
            for suffix in evaluator.ROLE_SUFFIX_TO_ROLE
        ),
    }


def main(argv: Sequence[str]) -> int:
    parser = argparse.ArgumentParser(prog="reproduce_t3_defects.py")
    parser.add_argument("--out", type=Path, help="write the reproduction record here")
    args = parser.parse_args(list(argv))

    evaluator = _load(EVAL_PATH, "p1_u_t3_reproduction_evaluator")
    pairs, unresolved = evaluator.fixed_corpus()

    record = {
        "schema": "P1U.T3PreRepairRecord.v1",
        "authority": "none; this measures the instrument, not a P1-U result",
        "defect_1_class_stratifier": defect_1_class_stratifier(evaluator, pairs),
        "defect_2_domain_stratifier": defect_2_domain_stratifier(
            evaluator, pairs, unresolved
        ),
        "defect_3_leakage_guard": defect_3_leakage_guard(evaluator),
        "measured_provider_payload_leak": measured_provider_payload_leak(evaluator, pairs),
    }
    text = json.dumps(record, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text)
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
