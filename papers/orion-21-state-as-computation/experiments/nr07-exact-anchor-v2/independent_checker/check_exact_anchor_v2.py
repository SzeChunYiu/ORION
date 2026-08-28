#!/usr/bin/env python3
"""Independent transcript checker for ORION21.NR07.EXACT_ANCHOR.v2.

This checker does not import the generator and does not use NumPy. It verifies
the committed bit-packed labels and predictions, exact integer scores, support
worlds, mismatch row identities, and terminal precedence.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import itertools
import json
from pathlib import Path
import sys
from typing import Any, NoReturn


HERE = Path(__file__).resolve().parent
LANE = HERE.parent
DEFAULT_RESULT = LANE / "RESULT.json"
PROTOCOL = LANE / "PROTOCOL.json"


def fail(message: str) -> NoReturn:
    raise AssertionError(message)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        fail(f"{path}: expected object")
    return value


def unpack_bits(
    record: dict[str, Any],
    *,
    result_dir: Path,
    referenced_labels: list[int] | None = None,
) -> list[int]:
    encoding = record.get("encoding")
    bit_count = record.get("bit_count")
    expected_sha = record.get("sha256")
    if not isinstance(bit_count, int) or not isinstance(expected_sha, str):
        fail("malformed bit payload")

    if encoding == "reference/query-label":
        if referenced_labels is None:
            fail("label reference used without referenced labels")
        if len(referenced_labels) != bit_count:
            fail("label reference length mismatch")
        raw = bytes(
            sum((referenced_labels[offset + bit] & 1) << bit for bit in range(8))
            for offset in range(0, bit_count, 8)
        )
        if hashlib.sha256(raw).hexdigest() != expected_sha:
            fail("label reference hash mismatch")
        return list(referenced_labels)

    if encoding != "numpy.packbits/little+base64-file":
        fail("unexpected bit encoding")
    relative_path = record.get("path")
    if not isinstance(relative_path, str):
        fail("transcript path missing")
    transcript_path = result_dir / relative_path
    try:
        payload = transcript_path.read_text(encoding="ascii").strip()
    except OSError as exc:
        fail(f"cannot read transcript {relative_path}: {exc}")
    raw = base64.b64decode(payload, validate=True)
    if hashlib.sha256(raw).hexdigest() != expected_sha:
        fail(f"bit payload hash mismatch: {relative_path}")
    if len(raw) != (bit_count + 7) // 8:
        fail(f"bit payload byte length mismatch: {relative_path}")
    return [(raw[index // 8] >> (index % 8)) & 1 for index in range(bit_count)]


def hash_row_ids(row_ids: list[int]) -> str:
    payload = ",".join(str(row_id) for row_id in row_ids).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("result", nargs="?", type=Path, default=DEFAULT_RESULT)
    args = parser.parse_args()

    result = load_json(args.result)
    result_dir = args.result.resolve().parent
    protocol = load_json(PROTOCOL)

    if result.get("schema") != "ORION.ORION21.NR07.ExactAnchorResult.v2":
        fail("unexpected result schema")
    if protocol.get("schema") != "ORION.ORION21.NR07.ExactAnchorProtocol.v2":
        fail("unexpected protocol schema")
    if result.get("protocol_identity") != protocol.get("protocol_identity"):
        fail("protocol identity mismatch")
    if result.get("scientific_authority_delta") != "NONE":
        fail("scientific authority delta must remain NONE")
    if result.get("submission_authority") is not False:
        fail("submission authority must remain false")

    anchor = result.get("anchor")
    if not isinstance(anchor, dict):
        fail("anchor missing")
    n_queries = anchor.get("n_queries")
    n_test = anchor.get("n_test")
    denominator = anchor.get("denominator")
    if denominator != n_queries * n_test:
        fail("denominator does not equal query×row count")

    queries = result.get("queries")
    if not isinstance(queries, list) or len(queries) != n_queries:
        fail("query count mismatch")

    counts_by_query: list[list[int]] = []
    predictions_by_query: list[list[list[int]]] = []
    labels_by_query: list[list[int]] = []
    referenced_transcripts: set[str] = set()

    for expected_query_id, query in enumerate(queries):
        if query.get("query_id") != expected_query_id:
            fail("query ordering mismatch")
        label_record = query["label_bits"]
        if label_record.get("encoding") == "numpy.packbits/little+base64-file":
            referenced_transcripts.add(label_record["path"])
        labels = unpack_bits(label_record, result_dir=result_dir)
        if len(labels) != n_test:
            fail(f"query {expected_query_id}: label length mismatch")
        labels_by_query.append(labels)

        candidates = query.get("candidates")
        if not isinstance(candidates, list):
            fail(f"query {expected_query_id}: candidates missing")
        if query.get("candidate_count") != len(candidates):
            fail(f"query {expected_query_id}: candidate_count mismatch")

        counts: list[int] = []
        predictions: list[list[int]] = []
        for expected_candidate_id, candidate in enumerate(candidates):
            if candidate.get("candidate_id") != expected_candidate_id:
                fail(f"query {expected_query_id}: candidate ordering mismatch")
            prediction_record = candidate["prediction_bits"]
            if prediction_record.get("encoding") == "numpy.packbits/little+base64-file":
                referenced_transcripts.add(prediction_record["path"])
            pred = unpack_bits(
                prediction_record,
                result_dir=result_dir,
                referenced_labels=labels,
            )
            if len(pred) != n_test:
                fail(f"query {expected_query_id}: prediction length mismatch")
            mismatch_rows = [index for index, (p, y) in enumerate(zip(pred, labels)) if p != y]
            correct = n_test - len(mismatch_rows)
            if hash_row_ids(mismatch_rows) != candidate.get(
                "mismatch_test_row_ids_sha256"
            ):
                fail(f"query {expected_query_id}: mismatch row hash drift")
            if correct != candidate.get("correct_count"):
                fail(f"query {expected_query_id}: correct count drift")
            if len(mismatch_rows) != candidate.get("incorrect_count"):
                fail(f"query {expected_query_id}: incorrect count drift")
            counts.append(correct)
            predictions.append(pred)
        counts_by_query.append(counts)
        predictions_by_query.append(predictions)


    transcript_root = result_dir / "transcript"
    actual_transcripts = {
        str(path.relative_to(result_dir))
        for path in transcript_root.glob("*.bits.b64")
        if path.is_file()
    }
    if actual_transcripts != referenced_transcripts:
        fail(
            "transcript inventory drift: "
            f"expected {sorted(referenced_transcripts)}, got {sorted(actual_transcripts)}"
        )

    reconstructed_worlds: list[tuple[list[int], int]] = []
    for selection in itertools.product(*(range(len(x)) for x in counts_by_query)):
        numerator = sum(
            counts_by_query[query_id][candidate_id]
            for query_id, candidate_id in enumerate(selection)
        )
        reconstructed_worlds.append((list(selection), numerator))

    worlds = result.get("aggregate_worlds")
    if not isinstance(worlds, list) or len(worlds) != len(reconstructed_worlds):
        fail("aggregate world count mismatch")
    for world_id, ((selection, numerator), world) in enumerate(
        zip(reconstructed_worlds, worlds)
    ):
        if world.get("world_id") != world_id:
            fail("world ordering mismatch")
        if world.get("query_candidate_ids") != selection:
            fail(f"world {world_id}: selection drift")
        accuracy = world.get("accuracy")
        if not isinstance(accuracy, dict):
            fail(f"world {world_id}: accuracy missing")
        if accuracy.get("numerator") != numerator:
            fail(f"world {world_id}: numerator drift")
        if accuracy.get("denominator") != denominator:
            fail(f"world {world_id}: denominator drift")
        if accuracy.get("fraction") != f"{numerator}/{denominator}":
            fail(f"world {world_id}: exact fraction drift")
        if accuracy.get("decimal") != numerator / denominator:
            fail(f"world {world_id}: decimal drift")

    recorded = result.get("recorded_pair")
    if not isinstance(recorded, dict):
        fail("recorded pair missing")
    historical_num = recorded["historical_expected"]["numerator"]
    observed_num = recorded["lunarc_observed"]["numerator"]
    expected_ids = [
        world_id for world_id, (_, numerator) in enumerate(reconstructed_worlds)
        if numerator == historical_num
    ]
    observed_ids = [
        world_id for world_id, (_, numerator) in enumerate(reconstructed_worlds)
        if numerator == observed_num
    ]
    if expected_ids != result.get("historical_expected_matching_world_ids"):
        fail("historical world mapping drift")
    if observed_ids != result.get("lunarc_observed_matching_world_ids"):
        fail("observed world mapping drift")
    if len(expected_ids) != 1 or len(observed_ids) != 1:
        fail("recorded numerators do not map uniquely")

    expected_selection = reconstructed_worlds[expected_ids[0]][0]
    observed_selection = reconstructed_worlds[observed_ids[0]][0]
    disagreement_rows: list[dict[str, Any]] = []
    historical_correct = 0
    observed_correct = 0
    for query_id, (expected_candidate, observed_candidate) in enumerate(
        zip(expected_selection, observed_selection)
    ):
        expected_pred = predictions_by_query[query_id][expected_candidate]
        observed_pred = predictions_by_query[query_id][observed_candidate]
        labels = labels_by_query[query_id]
        diff = [
            row_id for row_id, (left, right) in enumerate(zip(expected_pred, observed_pred))
            if left != right
        ]
        if diff:
            old_correct = sum(expected_pred[row_id] == labels[row_id] for row_id in diff)
            new_correct = sum(observed_pred[row_id] == labels[row_id] for row_id in diff)
            historical_correct += old_correct
            observed_correct += new_correct
            disagreement_rows.append(
                {
                    "query_id": query_id,
                    "prediction_disagreement_count": len(diff),
                    "test_row_ids_sha256": hash_row_ids(diff),
                    "historical_expected_correct_on_disagreements": old_correct,
                    "lunarc_observed_correct_on_disagreements": new_correct,
                }
            )

    delta = result.get("transcript_delta")
    if not isinstance(delta, dict):
        fail("transcript delta missing")
    if disagreement_rows != delta.get("differing_queries"):
        fail("raw disagreement transcript drift")
    if sum(row["prediction_disagreement_count"] for row in disagreement_rows) != 1011:
        fail("expected 1011 prediction disagreements")
    if historical_correct != 505 or observed_correct != 506:
        fail("expected 505 versus 506 correct among disagreements")
    if observed_num - historical_num != 1:
        fail("aggregate numerator delta must be one")
    if delta["aggregate_numerator_delta"] != 1:
        fail("reported aggregate numerator delta drift")

    q0 = queries[0]
    if q0.get("boundary_tied_feature_indices") != [35, 93, 263]:
        fail("query-0 three-way boundary tie drift")
    q0_supports = [candidate["support_feature_indices"] for candidate in q0["candidates"]]
    q0_counts = [candidate["correct_count"] for candidate in q0["candidates"]]
    if q0_supports != [[16, 311, 35], [16, 311, 93], [16, 311, 263]]:
        fail("query-0 support worlds drift")
    if q0_counts != [3054, 3055, 3092]:
        fail("query-0 exact counts drift")

    expected_forensic = protocol["authority"]["expected_forensic_terminal"]
    if result.get("forensic_terminal") != expected_forensic:
        fail("forensic terminal drift")
    if result.get("controlling_scientific_terminal") != "CANNOT_CHECK_INSTRUMENT_DRIFT":
        fail("controlling science terminal drift")
    if result.get("source_custody_terminal") != "NR07_LUNARC_EXECUTABLE_BYTES_ABSENT":
        fail("source custody terminal drift")

    print(
        json.dumps(
            {
                "schema": "ORION.ORION21.NR07.ExactAnchorIndependentCheck.v2",
                "queries_checked": n_queries,
                "atomic_decisions_checked": denominator,
                "candidate_worlds_checked": len(worlds),
                "prediction_disagreements_checked": 1011,
                "aggregate_numerator_delta": 1,
                "scientific_authority_delta": "NONE",
                "terminal": "NR07_EXACT_ANCHOR_INDEPENDENT_CHECK_GREEN",
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(
            json.dumps(
                {
                    "schema": "ORION.ORION21.NR07.ExactAnchorIndependentCheck.v2",
                    "terminal": "NR07_EXACT_ANCHOR_INDEPENDENT_CHECK_RED",
                    "error": str(exc),
                },
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        raise SystemExit(1)
