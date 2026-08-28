#!/usr/bin/env python3
"""Hostile reproducibility tests for the frozen ORION-02 R22 executor."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

import numpy as np

EXECUTOR = Path(__file__).with_name("fiberguard_pmlb_proposal_ordering_r22.py")


def load_executor():
    spec = importlib.util.spec_from_file_location("orion02_r22_executor", EXECUTOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load R22 executor")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SelfTestBridge(unittest.TestCase):
    def test_executor_self_test_passes(self) -> None:
        module = load_executor()
        module.run_self_test()  # raises AssertionError on any failure


class ShieldMechanicsTests(unittest.TestCase):
    def test_hand_computed_worst_case_table(self) -> None:
        module = load_executor()
        syn, _ = module.synthetic_fixture()
        adm, wc = syn.shield_query("queryA", (), module.TAU)
        self.assertEqual(adm, ["dct"])
        self.assertAlmostEqual(wc["dct"], 0.0, places=12)
        self.assertAlmostEqual(wc["gnb"], 0.21, places=12)
        self.assertAlmostEqual(wc["hgb"], 0.10, places=12)
        adm_b, wc_b = syn.shield_query("queryB", (), module.TAU)
        self.assertEqual(adm_b, ["dct", "hgb"])
        self.assertAlmostEqual(wc_b["gnb"], 0.16, places=12)

    def test_admissibility_survives_hostile_scorer(self) -> None:
        module = load_executor()
        syn, info = module.synthetic_fixture()

        def hostile(c, arm, name, acq):
            a, _ = c.shield_query(name, acq, module.TAU)
            if not a:
                return {x: 0.0 for x in module.PORTFOLIO}
            pick = max(a, key=lambda x: c.excess_member(name, x))
            return {x: (0.0 if x == pick else 1.0) for x in module.PORTFOLIO}

        for name in info["queries"]:
            dec = module.walk_with_scorer(syn, name, "STATIC_ADAPTIVE", module.TAU, hostile, None)
            a_final, _ = syn.shield_query(name, tuple(sorted(dec["acquired"])), module.TAU)
            self.assertTrue(dec["committed"] == "F_STAR" or dec["committed"] in a_final)

    def test_tie_break_on_bin_edge_goes_to_lower_bin(self) -> None:
        module = load_executor()
        syn, _ = module.synthetic_fixture()
        # queryA G0[0]=0.15 < edge 0.435 -> lower cell
        state = tuple(syn.state_indices(()))
        self.assertEqual(syn.cell_of("queryA", state)[0], 0)
        self.assertEqual(syn.cell_of("queryB", state)[0], 1)


class CorpusLoadingTests(unittest.TestCase):
    """Label-column rule: FIRST 'target' header occurrence is the label.

    Guards the post-freeze resource-schema correction: three frozen PMLB
    datasets place the label first/mid-file, and 'schizo' carries a duplicate
    trailing 'target' header that its metadata.yaml enumerates as the feature
    'target.1'. Loading is positional, never by-name-dict or last-position.
    """

    @staticmethod
    def _write_tsv(directory: Path, name: str, header: list[str], rows: list[list[str]]) -> Path:
        import gzip

        path = directory / f"{name}.tsv.gz"
        with gzip.open(path, "wt", encoding="utf-8", newline="") as handle:
            handle.write("\t".join(header) + "\n")
            for row in rows:
                handle.write("\t".join(row) + "\n")
        return path

    def test_label_is_first_target_and_position_independent(self) -> None:
        import tempfile

        module = load_executor()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # Label first (auto_insurance_symboling layout).
            first = self._write_tsv(
                root,
                "lab_first",
                ["target", "f1", "f2"],
                [["0", "1.0", "a"], ["1", "2.0", "b"], ["0", "3.0", "a"], ["1", "1.0", "b"]],
            )
            d = module.load_dataset(first)
            self.assertEqual(d["n_features"], 2)
            self.assertEqual(d["n_classes"], 2)
            # Label mid-file (breast_cancer_wisconsin_diagnostic layout).
            mid = self._write_tsv(
                root,
                "lab_mid",
                ["f1", "target", "f2"],
                [["1.0", "0", "a"], ["2.0", "1", "b"], ["3.0", "0", "a"], ["1.0", "1", "b"]],
            )
            d_mid = module.load_dataset(mid)
            self.assertEqual(d_mid["n_features"], 2)
            self.assertEqual(d_mid["n_classes"], 2)

    def test_duplicate_target_header_first_occurrence_is_label(self) -> None:
        import tempfile

        module = load_executor()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # schizo layout: trailing duplicate 'target' header = feature target.1.
            dup = self._write_tsv(
                root,
                "dup_target",
                ["ID", "target", "g1", "sex", "target"],
                [
                    ["7.0", "0", "10", "0", "1"],
                    ["8.0", "1", "11", "1", "0"],
                    ["9.0", "2", "12", "0", "1"],
                    ["10.0", "1", "13", "1", "0"],
                ],
            )
            d = module.load_dataset(dup)
            self.assertEqual(d["n_features"], 4)  # ID, g1, sex, target.1
            self.assertEqual(d["n_classes"], 3)  # first target column: {0,1,2}
            self.assertEqual(d["n_instances"], 4)

    def test_missing_target_column_fails_closed(self) -> None:
        import tempfile

        module = load_executor()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bad = self._write_tsv(
                root,
                "no_target",
                ["a", "b"],
                [["1", "2"], ["3", "4"], ["5", "6"], ["7", "8"]],
            )
            with self.assertRaises(ValueError):
                module.load_dataset(bad)


class FoldCustodyTests(unittest.TestCase):
    def test_role_partition_disjoint_and_covering(self) -> None:
        module = load_executor()
        names = [f"d{i:02d}" for i in range(45)]
        fold_of = module.assign_folds(names)
        for t in range(module.N_FOLDS):
            roles = module.role_names(t, fold_of)
            union = sorted(sum(roles.values(), []))
            self.assertEqual(union, names)
            self.assertEqual(len(union), len(set(union)))
            for role in ("proposer_train", "shield_table", "threshold_select"):
                self.assertFalse(set(roles["test"]) & set(roles[role]))

    def test_fold_assignment_is_seed_deterministic(self) -> None:
        module = load_executor()
        names = [f"d{i:02d}" for i in range(45)]
        self.assertEqual(module.assign_folds(names), module.assign_folds(names))


class NumericsTests(unittest.TestCase):
    def test_direct_difference_distances_match_elementwise(self) -> None:
        module = load_executor()
        rng = np.random.default_rng(20260827)
        q, X = rng.normal(size=4), rng.normal(size=(50, 4))
        direct = np.sqrt(((X - q) ** 2).sum(axis=1))
        ref = np.array([module.math.sqrt(float(np.sum((X[i] - q) ** 2))) for i in range(50)])
        np.testing.assert_array_equal(direct, ref)

    def test_bootstrap_is_seed_deterministic(self) -> None:
        module = load_executor()
        d = np.array([0.1, -0.2, 0.3, 0.05, -0.1, 0.2] * 5)
        self.assertEqual(module.paired_bootstrap(d), module.paired_bootstrap(d))

    def test_terminal_precedence_sign_convention(self) -> None:
        module = load_executor()

        def payload(mean_diff, ci_upper, pmean, smean, pg=1.0, sg=2.0, viol=0, cov=1.0):
            hostile = {k: True for k in ("a", "b", "c", "d", "e", "f", "g", "h", "i")}
            return {
                "hostile_controls": hostile,
                "coverage": {"primary_tau_full_state": cov},
                "arms_summary": {
                    "PRIMARY_LEARNED": {"violations_strict": viol, "n": 45},
                    "STATIC_ADAPTIVE": {"mean_excess": smean},
                },
                "primary_test": {
                    "mean_diff": mean_diff, "ci_upper": ci_upper, "primary_mean_excess": pmean,
                    "mean_groups_acquired_primary": pg, "mean_groups_acquired_static": sg,
                },
            }

        self.assertEqual(module.decide_terminal(payload(-0.010, -0.001, 0.09, 0.10)), "C_R22_PMLB_PROPOSAL_ORDERING_VALUE")
        self.assertEqual(module.decide_terminal(payload(-0.004, -0.001, 0.096, 0.10)), "C_R22_PMLB_PROPOSAL_ORDERING_STRICT_BUT_NOT_MATERIAL")
        self.assertEqual(module.decide_terminal(payload(-0.001, 0.002, 0.099, 0.10)), "C_R22_PMLB_PROPOSAL_ORDERING_STRICT_BUT_NOT_MATERIAL")
        self.assertEqual(module.decide_terminal(payload(0.0, 0.0, 0.10, 0.10)), "C_R22_PMLB_PROPOSAL_ORDERING_NULL")
        self.assertEqual(module.decide_terminal(payload(0.01, 0.005, 0.11, 0.10)), "C_R22_PMLB_PROPOSAL_ORDERING_ADVERSE")
        self.assertEqual(module.decide_terminal(payload(-0.010, -0.001, 0.09, 0.10, pg=2.5, sg=1.0)), "C_R22_PMLB_PROPOSAL_ORDERING_STRICT_BUT_NOT_MATERIAL")
        self.assertEqual(module.decide_terminal(payload(-0.010, -0.001, 0.09, 0.10, viol=6)), "C_R22_PMLB_PROPOSAL_ORDERING_CERTIFICATE_INVALID")
        self.assertEqual(module.decide_terminal(payload(-0.010, -0.001, 0.09, 0.10, cov=0.80)), "C_R22_PMLB_PROPOSAL_ORDERING_NO_CERTIFIED_COVERAGE")


if __name__ == "__main__":
    unittest.main()
