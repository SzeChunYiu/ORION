#!/usr/bin/env python3
"""Unit tests for the independent R23 receipt verifier."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


VERIFIER = Path(__file__).with_name("verify_fiberguard_pmlb_proposal_ordering_r23.py")


def load_verifier():
    spec = importlib.util.spec_from_file_location("orion02_r23_verifier", VERIFIER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load R23 verifier")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class IndependentMechanicsTests(unittest.TestCase):
    def test_f_star_uses_shield_mean_and_lexical_tie(self) -> None:
        verifier = load_verifier()
        outcomes = {
            "s1": {"a": 0.2, "b": 0.1},
            "s2": {"a": 0.0, "b": 0.1},
        }
        self.assertEqual(verifier.independent_f_star(["s1", "s2"], outcomes, ("a", "b")), "a")

    def test_backoff_is_exact_cell_else_two_hamming_nearest(self) -> None:
        verifier = load_verifier()
        query = (1, 1, 1)
        cells = {"a": (0, 0, 0), "b": (1, 1, 0), "c": (0, 0, 1)}
        members, used = verifier.independent_members(query, cells, mode="backoff", k=2)
        self.assertEqual(members, ["b", "c"])
        self.assertTrue(used)
        cells["d"] = query
        cells["e"] = query
        members, used = verifier.independent_members(query, cells, mode="backoff", k=2)
        self.assertEqual(members, ["d", "e"])
        self.assertFalse(used)


if __name__ == "__main__":
    unittest.main()
