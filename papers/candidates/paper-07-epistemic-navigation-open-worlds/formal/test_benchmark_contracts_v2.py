import unittest

from check_benchmark_contracts_v2 import (
    ObligationStatus,
    ObservationHistory,
    Route,
    Topology,
    World,
    certificate_transfers,
    evaluate_benchmark_case,
    observationally_equivalent,
    reachable,
    route_stop_authorized,
    structurally_independent,
    task_stop_authorized,
    topology_change_witness,
    unseen_relevant_extension,
)


class P7CheckerTests(unittest.TestCase):
    def test_open_world_extension_is_indistinguishable_on_history(self):
        topology = Topology(
            frozenset({"s", "seen", "boundary"}),
            frozenset({("s", "seen"), ("s", "boundary")}),
            "s",
            frozenset(),
        )
        world = World(topology, frozenset({"seen"}))
        history = ObservationHistory(frozenset({"s"}), topology.edges)
        extension = unseen_relevant_extension(world, history)
        self.assertTrue(observationally_equivalent(world, extension, history))
        self.assertIn("__hidden_relevant__", extension.relevant)

    def test_topology_change_witness_is_strict(self):
        fixed, reframed, _ = topology_change_witness()
        self.assertFalse(reachable(fixed, next(iter(fixed.goals))))
        self.assertTrue(reachable(reframed, next(iter(reframed.goals))))

    def test_certificate_transfer_requires_complete_support_preservation(self):
        self.assertTrue(certificate_transfers(
            {"a", "b"}, {("a", "b")}, {"a": "a'", "b": "b'"}, {("a'", "b'")}, True
        ))
        self.assertFalse(certificate_transfers(
            {"a", "b"}, {("a", "b")}, {"a": "a'"}, {("a'", "b'")}, True
        ))
        self.assertFalse(certificate_transfers(
            {"a", "b"}, {("a", "b")}, {"a": "a'", "b": "b'"}, {("a'", "b'")}, False
        ))

    def test_output_overlap_does_not_define_independence(self):
        same_output_1 = Route("r1", "a", "d1", "c1", frozenset({"x"}))
        same_output_2 = Route("r2", "b", "d2", "c2", frozenset({"x"}))
        self.assertTrue(structurally_independent(same_output_1, same_output_2))
        disjoint_1 = Route("r3", "a", "d", "c", frozenset({"x"}))
        disjoint_2 = Route("r4", "a", "d", "c", frozenset({"y"}))
        self.assertFalse(structurally_independent(disjoint_1, disjoint_2))

    def test_route_stop_does_not_imply_task_stop(self):
        self.assertTrue(route_stop_authorized(True))
        self.assertFalse(task_stop_authorized({
            "route_a": ObligationStatus.SATISFIED,
            "route_b": ObligationStatus.OPEN,
        }))

    def test_censored_obligation_blocks_task_stop(self):
        self.assertFalse(task_stop_authorized({
            "known": ObligationStatus.SATISFIED,
            "unavailable": ObligationStatus.CENSORED,
        }))

    def test_benchmark_terminal_oracle_is_fail_closed(self):
        censored = {
            "family": "censored_route",
            "topology_change_required": False,
            "censored_regions": ["provider"],
        }
        reframe = {
            "family": "topology_change",
            "topology_change_required": True,
            "censored_regions": [],
        }
        self.assertEqual(evaluate_benchmark_case(censored), "CANNOT_CHECK")
        self.assertEqual(evaluate_benchmark_case(reframe), "REFRAME")


if __name__ == "__main__":
    unittest.main()
