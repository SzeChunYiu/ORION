#!/usr/bin/env python3
"""Hostile reproducibility tests for the frozen ORION-02 R21 executor."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

import numpy as np


EXECUTOR = Path(__file__).with_name("fiberguard_cspmzn_direct_relative_r21.py")


def load_executor():
    spec = importlib.util.spec_from_file_location("orion02_r21_executor", EXECUTOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load R21 executor")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ExactDuplicateTieTests(unittest.TestCase):
    def test_high_norm_exact_duplicates_are_zero_and_lexical_in_a_large_batch(self) -> None:
        module = load_executor()
        rng = np.random.default_rng(20_260_827)
        train = rng.normal(size=(465, 288))
        queries = rng.normal(size=(464, 288))

        duplicate = rng.normal(size=288)
        duplicate[:24] *= 25_000
        duplicate[24:48] *= 1_000
        train[-30:] = duplicate
        queries[-17:] = duplicate

        order, distances = module.neighbour_order(train, queries, maximum_k=9)
        expected = np.arange(435, 444, dtype=np.int64)
        expected_order = np.broadcast_to(expected, (17, len(expected)))

        np.testing.assert_array_equal(order[-17:], expected_order)
        np.testing.assert_array_equal(distances[-17:], np.zeros((17, 9)))


if __name__ == "__main__":
    unittest.main()
