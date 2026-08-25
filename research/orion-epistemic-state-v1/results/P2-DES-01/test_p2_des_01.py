#!/usr/bin/env python3
"""Outcome-free focused tests for the P2-DES-01 frozen runner."""

from __future__ import annotations

import ast
import importlib.util
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("p2_des_runner", HERE / "run_p2_des_01.py")
assert SPEC and SPEC.loader
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


class RunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.index = RUNNER.Bm25Index(
            [
                ("d1", "alpha alpha bridge corona"),
                ("d2", "alpha bridge virus"),
                ("d3", "beta bridge immune"),
                ("d4", "gamma remote immune"),
                ("d5", "delta unrelated"),
            ]
        )

    def test_tokenizer_is_frozen(self) -> None:
        self.assertEqual(RUNNER.tokenize("A COVID-19_test"), ("covid", "19", "test"))

    def test_bm25_is_deterministic(self) -> None:
        self.assertEqual(self.index.search("alpha", 3), self.index.search("alpha", 3))
        self.assertEqual(self.index.search("alpha", 3)[0], "d1")

    def test_rrf_uses_stable_tie_break(self) -> None:
        self.assertEqual(
            RUNNER.reciprocal_rank_fusion([["b", "a"], ["a", "b"]], 2),
            ["a", "b"],
        )

    def test_diversified_round_robin_deduplicates(self) -> None:
        self.assertEqual(
            RUNNER.diversified_round_robin([["a", "b"], ["a", "c"]], 3),
            ["a", "b", "c"],
        )

    def test_remote_merge_excludes_local_top_300(self) -> None:
        merged = RUNNER.merge_head_and_remote(["a", "b", "c"], ["a", "x", "y"])
        self.assertEqual(merged, ["a", "b", "c", "x", "y"])

    def test_bootstrap_empty_is_explicit(self) -> None:
        self.assertEqual(RUNNER.bootstrap_mean_interval([], seed=1)["n"], 0)

    def test_pre_score_envelope_uses_python_boolean(self) -> None:
        class StubIndex:
            count = 500
            doc_ids = [f"d{index:03d}" for index in range(500)]

            def search(self, query, depth=300):
                return self.doc_ids[:depth]

            def bridge_terms(self, feedback_doc_ids, excluded):
                return []

        topic = {
            "topic_id": "1",
            "question": "alpha question",
            "keyword_query": "alpha keyword",
            "narrative": "alpha narrative",
        }
        output = RUNNER.generate_policy_outputs(StubIndex(), [topic])
        self.assertIs(output["qrels_opened"], False)

    def test_runner_contains_no_json_literal_names(self) -> None:
        tree = ast.parse((HERE / "run_p2_des_01.py").read_text(encoding="utf-8"))
        names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
        self.assertTrue({"false", "true", "null"}.isdisjoint(names))


if __name__ == "__main__":
    unittest.main()
