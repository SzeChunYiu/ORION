from __future__ import annotations

import itertools
import random

import engine_b as eb
import crb_census as cc


def _brute_zero_sum_lengths(sequence, weights):
    lengths = set()
    for size in range(1, weights + 1):
        for combination in itertools.combinations(sequence, size):
            total = 0
            for element in combination:
                total = eb.add(total, element)
            if total == 0:
                lengths.add(size)
    return lengths


def test_tables_match_engine_b_group_laws() -> None:
    assert all(cc._ADD_TABLE[a][b] == eb.add(a, b) for a in range(125) for b in range(125))
    assert all(cc._NEG[v] == eb.negate(v) for v in range(125))
    assert len(cc._TRANSLATE) == 125


def test_reach_spectrum_matches_bruteforce_on_random_multisets() -> None:
    rng = random.Random(7)
    for _ in range(60):
        sequence = [rng.randrange(1, 125) for _ in range(rng.randint(2, 8))]
        assert cc.zero_sum_lengths(sequence, 6) == _brute_zero_sum_lengths(sequence, 6)


def _freeze_schmid_witness() -> tuple[int, ...]:
    triples = (
        [(1, 0, 0)] * 4
        + [(0, 1, 0)] * 4
        + [(0, 0, 1)] * 4
        + [(1, 1, 0)] * 2
        + [(1, 0, 1)] * 2
        + [(0, 1, 1)] * 3
    )
    return tuple(eb.encode_element(triple) for triple in triples)


def test_leaf_spectrum_and_sat_adjudicator_on_frozen_witness() -> None:
    pytest = __import__("pytest")
    pysat = pytest.importorskip("pysat.solvers")
    assert pysat is not None
    witness = _freeze_schmid_witness()
    assert len(witness) == 19
    spectrum = cc.zero_sum_lengths(witness, 9)
    assert not spectrum & {1, 2, 3, 4, 5, 6}
    assert spectrum & {7, 8, 9}
    assert cc._sat_two_disjoint_unsat(witness) is True
    extended = witness + (eb.encode_element((0, 0, 1)),)
    assert cc._sat_two_disjoint_unsat(extended) is False
    e1 = eb.encode_element((1, 0, 0))
    trivial = (e1, eb.negate(e1), e1, eb.negate(e1))
    assert cc._sat_two_disjoint_unsat(trivial) is False


def test_d2_reduced_length_enumeration_is_exact_and_deterministic() -> None:
    # Reduced target lengths test the machinery (partition, DP rejects,
    # determinism, record invariants); note the Lemma-A depth prune is only
    # predicate-implied at length >= 19, so reduced-length universes are the
    # artificial predicate "no zero-sum <= 6 and no two disjoint zero sums".
    records, nodes, states, prunes = cc._d2_task_worker(
        (1, 1, 1, 3, 3), target_length=8, node_budget=30_000_000
    )
    assert nodes > 0 and states > 0
    again, _, _, _ = cc._d2_task_worker((1, 1, 1, 3, 3), target_length=8, node_budget=30_000_000)
    assert records == again
    for record in records[:40]:
        assert len(record) == 8
        assert record == tuple(sorted(record))
        assert record.count(1) == 1 and record.count(5) == 1 and record.count(25) == 1
        assert not cc.zero_sum_lengths(record, 6)
        # every record is two-disjoint-free by the exact pair DP ...
        state = cc._empty_d2_state()
        for element in record:
            state = cc._extend_d2_state(state, element)
            assert state is not None
        assert 0 not in state[2]


def test_d2_pair_dp_agrees_with_sat_adjudicator_on_random_multisets() -> None:
    pytest = __import__("pytest")
    pytest.importorskip("pysat.solvers")
    rng = random.Random(23)
    for _ in range(25):
        length = rng.randint(8, 14)
        multiset = sorted(rng.randrange(1, 125) for _ in range(length))
        dp_state = cc._empty_d2_state()
        rejected = False
        for element in multiset:
            dp_state = cc._extend_d2_state(dp_state, element)
            if dp_state is None:
                rejected = True
                break
        if rejected:
            # a prune reject must be explained by a zero-sum of length <= 6
            # or by two genuinely disjoint zero sums (SAT-confirmed)
            assert cc.zero_sum_lengths(multiset, 6) or not cc._sat_two_disjoint_unsat(multiset)
            continue
        dp_clean = 0 not in dp_state[2]
        assert dp_clean == cc._sat_two_disjoint_unsat(multiset)


def _brute_two_disjoint(multiset: list[int]) -> bool:
    """Exhaustive ground truth: two disjoint nonempty zero-sum sub-multisets."""
    from itertools import product as _product

    distinct = sorted(set(multiset))
    caps = [multiset.count(v) for v in distinct]
    vectors = [(v // 25, (v % 25) // 5, v % 5) for v in distinct]
    zero_sums: list[tuple[int, ...]] = []
    for counts in _product(*[range(c + 1) for c in caps]):
        if not any(counts):
            continue
        total = [0, 0, 0]
        for count, g in zip(counts, vectors):
            total[0] += count * g[0]
            total[1] += count * g[1]
            total[2] += count * g[2]
        if all(component % 5 == 0 for component in total):
            zero_sums.append(counts)
    for left in zero_sums:
        for right in zero_sums:
            if all(a + b <= c for a, b, c in zip(left, right, caps)):
                return True
    return False


def _pair_verdict(multiset: list[int]) -> str:
    """Isolate the pair predicate from the Lemma-A board prune."""
    state = cc._empty_d2_state()
    for element in sorted(multiset):
        board_admits = cc._extend(state[0], element, cc.T_D2) is not None
        extended = cc._extend_d2_state(state, element)
        if extended is None:
            return "board" if board_admits is False else "pair"
        state = extended
    return "pair" if 0 in state[2] else "clean"


def test_pair_dp_regression_classes_from_live_shard_audit() -> None:
    # 2026-08-27 audit: the pair-DP transitions once extended BOTH sides of a
    # pair with the single new position and dropped untouched pairs, so it
    # missed real pairs whose sides complete at different steps (the length-19
    # leaf below was emitted as a census record) and falsely pruned
    # equal-sum-pair completions.  Both classes are pinned here.
    leaf = [1, 1, 1, 1, 5, 5, 5, 5, 6, 6, 6, 25, 25, 25, 25, 26, 26, 26, 30]
    # two disjoint zero sums: {1x2, 5x2, 6x3} and {1x2, 25x2, 26x3}
    assert _brute_two_disjoint(leaf)
    assert _pair_verdict(leaf) == "pair"
    # [1, 1, 4] has exactly one zero sum ({1, 4}); it must fall to the
    # Lemma-A board reject, never to a false pair completion.
    assert not _brute_two_disjoint([1, 1, 4])
    assert _pair_verdict([1, 1, 4]) == "board"
    # the false-positive class proper: two copies of one value plus the
    # negation once completed a phantom pair on both sides at once.
    assert _pair_verdict([1, 1, 4, 6, 6, 6, 6, 6]) == "board"


def test_pair_dp_agrees_with_bruteforce_on_duplicate_heavy_multisets() -> None:
    # The original 25-draw agreement fixture sampled nearly-distinct
    # multisets and was structurally blind to both defect classes; this
    # variant draws small supports with multiplicities up to five, which is
    # where the transition defects lived.
    rng = random.Random(20260827)
    for _ in range(150):
        support = [rng.randrange(1, 125) for _ in range(rng.randint(2, 6))]
        multiset = [v for v in support for _ in range(rng.randint(1, 5))]
        verdict = _pair_verdict(multiset)
        brute = _brute_two_disjoint(multiset)
        if verdict == "pair":
            assert brute, multiset
        elif verdict == "clean":
            assert not brute, multiset
        else:  # board reject: sound for the census regardless of the pair
            assert cc.zero_sum_lengths(multiset, 6), multiset


def test_d2_task_list_partitions_the_normalized_universe() -> None:
    triples = list(cc.iter_seed_triples())
    assert len(triples) == 20
    # 20 seed triples x sum over first of (121 - first) second-element shards
    assert len(cc.d2_task_list()) == 20 * (121 * 122 // 2)
    reduced = cc.d2_task_list(13)
    # 19 triples have seed <= 11 (second-element shards); only (4,4,4) has
    # seed 12 and degrades to one task per first element.
    assert len(reduced) == 19 * (121 * 122 // 2) + 121


def test_d2_census_finds_the_frozen_schmid_witness_in_its_shard() -> None:
    witness = _freeze_schmid_witness()
    fs19 = tuple(sorted(witness))
    idx6 = cc.NONBASIS.index(6)
    records, nodes, states, prunes = cc._d2_task_worker(
        (4, 4, 4, idx6, idx6), target_length=19, node_budget=500_000_000
    )
    assert nodes > 0 and states > 0
    assert fs19 in records
    # the donor witness is a genuine length-19 two-disjoint-free multiset:
    # minimum zero-sum length exactly 7 (frozen instrument value)
    spectrum = cc.zero_sum_lengths(fs19, 9)
    assert 7 in spectrum and not spectrum & {1, 2, 3, 4, 5, 6}


def test_d3_extension_enumeration_on_frozen_witness() -> None:
    witness = _freeze_schmid_witness()
    extensions, hostable = cc.enumerate_d3_extensions(witness)
    assert hostable is True
    assert extensions
    for extension in extensions[:60]:
        assert len(extension) == 6
        assert list(extension) == sorted(extension)
        total = 0
        for element in extension:
            total = eb.add(total, element)
        assert total == 0
        merged = witness + extension
        assert not cc.zero_sum_lengths(merged, 5)
    again, _ = cc.enumerate_d3_extensions(witness)
    assert again == extensions


def test_d3_skips_witness_with_short_zero_sum() -> None:
    e1 = eb.encode_element((1, 0, 0))
    short = (e1, eb.negate(e1), e1, eb.negate(e1), e1, eb.negate(e1))
    assert cc.zero_sum_lengths(short, 5)
    extensions, hostable = cc.enumerate_d3_extensions(short)
    assert hostable is False
    assert extensions == ()
