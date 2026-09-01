"""Independent CR-B full-census generator for the two declared NQ scopes.

This generator is written from the public mathematical definitions only.  It
does not import, read, or wrap any Engine-A module, canonicalized candidate
list, forbidden set, orbit manifest, or aggregate result.  The representation
is independent of the Engine-A shift-permuted bitboard enumerator: reachable
sums are carried as sorted byte-value sets translated through per-element
value-permutation tables, the depth prune uses only the public Lemma A bound
(no zero-sum of length <= T), and the leaf decision is made by the Engine-B
SAT encoding or by the disjoint-length argument, never by a ported DP.

D2 scope: every length-19 multiset over nonzero C_5^3 elements whose support
contains the fixed basis {e1, e2, e3} with 1 <= m(e1) <= m(e2) <= m(e3) <= 4,
with no zero-sum of length <= 6, and with no two disjoint nonempty zero-sum
sub-multisets.

D3 scope: for every D2 witness C, every 6-element zero-sum multiset A in
nondecreasing order with forced final element such that C + A has no
zero-sum of length <= 5; records are emitted as C ++ A with one record per
(C, A) pair and no deduplication.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any, Iterator, Mapping, Sequence

import batch_engine_b as batch
import engine_b as eb
import full_manifest as fm


class CensusGenerationMismatch(RuntimeError):
    """Raised when an independent census disagrees with its frozen contract."""


class ResourceBudgetExceeded(RuntimeError):
    """Raised when the generator passes its declared resource budget."""


BASIS = (1, 5, 25)
T_D2 = 6
T_D3 = 5
TARGET_LENGTH_D2 = 19
TARGET_LENGTH_D3 = 25
EXTENSION_LENGTH_D3 = 6
MAX_BASIS_MULTIPLICITY = 4
NONBASIS = tuple(v for v in range(1, 125) if v not in BASIS)

_ADD_TABLE = [[eb.add(a, b) for b in range(125)] for a in range(125)]
_NEG = [eb.negate(v) for v in range(125)]
_TRANSLATE = [bytes(_ADD_TABLE[v]) + bytes(range(125, 256)) for v in range(125)]
_MULTIPLE = [[0] * 125, list(range(125))]
for _ in range(3):
    _MULTIPLE.append([_ADD_TABLE[row_v][v] for v, row_v in enumerate(_MULTIPLE[-1])])
_NEGJ = [[_NEG[value] for value in row] for row in _MULTIPLE]
# Projective lines {g, 2g, 3g, 4g} partition the 124 nonzero elements into 31
# lines; a multiset restricted to one line is zero-sum-free up to length T_D2
# exactly when its multiplicity vector avoids every sub-count combination with
# 1 <= x+y+z+w <= T_D2 and (x + 2y + 3z + 4w) % 5 == 0.
_LINE_OF = [-1] * 125
_POS_IN_LINE = [0] * 125
_LINE_IDS: list[int] = []
for _v in range(1, 125):
    if _LINE_OF[_v] >= 0:
        continue
    _line = len(_LINE_IDS)
    _LINE_IDS.append(_line)
    for _c in range(1, 5):
        _u = _v
        for _ in range(_c - 1):
            _u = _ADD_TABLE[_u][_v]
        _LINE_OF[_u] = _line
        _POS_IN_LINE[_u] = _c - 1


def _line_admissible(a: int, b: int, c: int, d: int) -> bool:
    for x in range(a + 1):
        for y in range(b + 1):
            for z in range(c + 1):
                for w in range(d + 1):
                    total = x + y + z + w
                    if 1 <= total <= T_D2 and (x + 2 * y + 3 * z + 4 * w) % 5 == 0:
                        return False
    return True


_MAXLINE: list[list[list[list[int]]]] = [
    [
        [
            [
                max(
                    (
                        a + b + c + d
                        for a in range(u1 + 1)
                        for b in range(u2 + 1)
                        for c in range(u3 + 1)
                        for d in range(u4 + 1)
                        if _line_admissible(a, b, c, d)
                    ),
                    default=0,
                )
                for u4 in range(5)
            ]
            for u3 in range(5)
        ]
        for u2 in range(5)
    ]
    for u1 in range(5)
]


def _extend(state: tuple[bytes, ...], element: int, weights: int) -> tuple[bytes, ...] | None:
    """Add one element to a weighted reach board, failing closed on short sums.

    ``state[w]`` is the sorted set of group sums reachable with exactly ``w``
    elements.  The update writes ``state[w-1] + element`` into ``state[w]``
    for ``w`` from high to low and rejects the extension outright when a
    zero sum lands in any nonzero weight.
    """

    updated = list(state)
    translate = _TRANSLATE[element]
    shifted_by_weight: list[bytes] = [b""] * (weights + 1)
    for weight in range(weights, 0, -1):
        source = state[weight - 1]
        if not source:
            continue
        shifted = source.translate(translate)
        if 0 in shifted:
            return None
        shifted_by_weight[weight] = shifted
    for weight in range(weights, 0, -1):
        shifted = shifted_by_weight[weight]
        if not shifted:
            continue
        existing = updated[weight]
        updated[weight] = bytes(sorted(existing + shifted)) if existing else bytes(sorted(shifted))
    updated[0] = state[0]
    return tuple(updated)


def _empty_state(weights: int) -> tuple[bytes, ...]:
    return (b"\x00",) + (b"",) * weights


def _extend_d2_state(
    state: tuple[tuple[bytes, ...], frozenset[int], frozenset[int]],
    element: int,
) -> tuple[tuple[bytes, ...], frozenset[int], frozenset[int]] | None:
    """One exact step of the two-disjoint-pair dynamic program.

    The state carries the weighted reach board plus two pair views over the
    current multiset: ``r1`` the set of sums of nonempty sub-multisets, and
    ``r2`` the set of unordered pairs of sums realized by two DISJOINT
    nonempty sub-multisets, packed as ``s1 * 125 + s2`` with ``s1 <= s2``.
    Adding a fresh position ``element`` may add it to either side of an old
    pair or start a new side paired with any old complete sub-multiset, so
    every pair present corresponds to real disjoint sub-multisets (soundness)
    and every disjoint pair appears by the time its last element is inserted
    (completeness).  The multiset contains two disjoint nonempty zero sums
    exactly when the packed pair ``0`` (both sides zero) is present.

    Fails closed on either reject: a zero sum of length at most ``T_D2``
    inside the reach board, or the packed pair ``0`` inside ``r2``.
    """

    boards, r1, r2 = state
    extended_boards = _extend(boards, element, T_D2)
    if extended_boards is None:
        return None
    add_row = _ADD_TABLE[element]
    r1_new = {add_row[s] for s in r1}
    r1_new.add(element)
    r1_new |= r1
    # A fresh position joins exactly one side of an existing pair, starts a
    # new side against any old sub-multiset, or joins neither side; extending
    # BOTH sides at once would reuse the single new position twice and is not
    # a realizable transition, and dropping the untouched pairs would lose
    # every pair whose two sides complete at different steps.
    r2_new: set[int] = set(r2)
    add_pair = r2_new.add
    for packed in r2:
        s1, s2 = divmod(packed, 125)
        a = add_row[s1]
        add_pair(a * 125 + s2 if a <= s2 else s2 * 125 + a)
        b = add_row[s2]
        add_pair(s1 * 125 + b if s1 <= b else b * 125 + s1)
    for s in r1:
        add_pair(element * 125 + s if element <= s else s * 125 + element)
    if 0 in r2_new:
        return None
    return (extended_boards, frozenset(r1_new), frozenset(r2_new))


def _empty_d2_state() -> tuple[tuple[bytes, ...], frozenset[int], frozenset[int]]:
    return (_empty_state(T_D2), frozenset(), frozenset())


def _seed_d2_state(
    multiplicities: tuple[int, int, int],
) -> tuple[tuple[bytes, ...], frozenset[int], frozenset[int]]:
    """Full D2 state of the ordered basis seed block."""

    state: tuple[tuple[bytes, ...], frozenset[int], frozenset[int]] | None = _empty_d2_state()
    for element, count in zip(BASIS, multiplicities):
        for _ in range(count):
            assert state is not None
            state = _extend_d2_state(state, element)
    assert state is not None
    return state


def _prefix_unions(boards: tuple[bytes, ...]) -> tuple[bytes, ...]:
    """Prefix unions of a weighted reach board: ``pre[w] = r[0] | ... | r[w]``."""

    pre = [boards[0]]
    for weight in range(1, len(boards)):
        pre.append(bytes(sorted(pre[-1] + boards[weight])))
    return tuple(pre)


def _multiplicity_cap(pre: tuple[bytes, ...], element: int, max_copies: int) -> int:
    """Largest initial run j of copies of ``element`` that stays prune-clean.

    The (j+1)-st copy is rejected as soon as ``-(j * element)`` is reachable
    with at most ``T_D2 - j`` elements of the current prefix: together they
    close a zero sum of length at most ``T_D2``.  The returned cap bounds the
    number of future copies soundly (a longer run is impossible in any
    extension, regardless of what else is added later).
    """

    negj = _NEGJ
    cap = 0
    for j in range(1, max_copies + 1):
        limit = T_D2 - j
        if limit < 0:
            break
        if negj[j][element] in pre[limit]:
            break
        cap = j
    return cap


def _line_capacity_bound(boards: tuple[bytes, ...], start: int, length: int, remaining: int) -> int:
    """Admissible completion bound from per-line multiplicity caps.

    For every still-allowed non-basis value the multiplicity cap constrains
    its future count; a whole projective line can then hold at most
    ``_MAXLINE[cap(g)][cap(2g)][cap(3g)][cap(4g)]`` further elements without
    the line alone closing a zero sum of length at most ``T_D2``.  The sum of
    the 31 line maxima is an upper bound on every completion, so a node whose
    bound falls below the target length can be pruned without losing any
    witness.  (The line bound must aggregate the whole multiplicity vector:
    ``g`` and ``2g`` can coexist, so a single-value cap is not sound.)
    """

    pre = _prefix_unions(boards)
    caps: dict[int, list[int]] = {}
    max_copies = min(MAX_BASIS_MULTIPLICITY, remaining)
    for index in range(start, len(NONBASIS)):
        element = NONBASIS[index]
        cap = _multiplicity_cap(pre, element, max_copies)
        if not cap:
            continue
        line = _LINE_OF[element]
        vector = caps.get(line)
        if vector is None:
            vector = caps[line] = [0, 0, 0, 0]
        position = _POS_IN_LINE[element]
        if cap > vector[position]:
            vector[position] = cap
    maxline = _MAXLINE
    total = 0
    for vector in caps.values():
        total += maxline[vector[0]][vector[1]][vector[2]][vector[3]]
        if length + total >= length + remaining:
            break
    return length + total


def _full_reach(sequence: Sequence[int], weights: int) -> tuple[bytes, ...]:
    """Recompute a complete weighted reach board over a full sequence."""

    state = _empty_state(weights)
    for element in sequence:
        state = _extend(state, element, weights)
        if state is None:
            raise CensusGenerationMismatch(
                "declared witness contains a zero-sum inside its frozen prune"
            )
    return state


def _leaf_two_disjoint_fast_path(state: tuple[bytes, ...]) -> bool:
    """Sound witness fast path: no 7..9 zero-sum implies no two disjoint."""

    return not any(0 in state[weight] for weight in range(7, 10))


def _sat_two_disjoint_unsat(sequence: Sequence[int]) -> bool:
    """Exact leaf decision by the Engine-B SAT encoding with two bins."""

    try:
        from pysat.solvers import Solver
    except ImportError as error:  # pragma: no cover - environment guard
        raise ResourceBudgetExceeded("python-sat is not installed") from error
    encoded = eb.build_factorization_cnf(sequence, 2)
    with Solver(name="g4", bootstrap_with=encoded.cnf.clauses) as solver:
        return not solver.solve()


def zero_sum_lengths(sequence: Sequence[int], weights: int) -> set[int]:
    """Exact zero-sum length spectrum of a multiset up to ``weights``.

    This is the public reference view of the reach board used by the tests to
    validate the translation-table representation against independent
    brute-force subset enumeration.
    """

    state = _empty_state(weights)
    for element in sequence:
        updated = list(state)
        translate = _TRANSLATE[element]
        for weight in range(weights, 0, -1):
            source = state[weight - 1]
            if not source:
                continue
            shifted = source.translate(translate)
            existing = updated[weight]
            updated[weight] = (
                bytes(sorted(existing + shifted)) if existing else bytes(sorted(shifted))
            )
        updated[0] = state[0]
        state = tuple(updated)
    return {weight for weight in range(1, weights + 1) if 0 in state[weight]}


def _leaf_reach_spectrum(sequence: Sequence[int]) -> set[int]:
    """Zero-sum length spectrum of a length-19 leaf over weights one to nine.

    Unlike :func:`_extend`, this never rejects: leaves that survive the
    depth-six prune may legitimately carry zero sums of length seven through
    nine, which the leaf decision then adjudicates.
    """

    spectrum = zero_sum_lengths(sequence, 9)
    if spectrum & {1, 2, 3, 4, 5, 6}:
        raise CensusGenerationMismatch("leaf reached with a zero-sum inside its frozen depth prune")
    return spectrum


def _seed_state(multiplicities: tuple[int, int, int]) -> tuple[bytes, ...]:
    """Weighted reach board of the ordered basis seed block."""

    state: tuple[bytes, ...] | None = _empty_state(T_D2)
    for element, count in zip(BASIS, multiplicities):
        for _ in range(count):
            assert state is not None
            state = _extend(state, element, T_D2)
            if state is None:
                raise CensusGenerationMismatch(
                    "basis seed block contains a zero-sum inside the prune"
                )
    assert state is not None
    return state


def iter_seed_triples() -> Iterator[tuple[int, int, int]]:
    """Ordered basis multiplicity triples 1 <= m1 <= m2 <= m3 <= 4."""

    for m1 in range(1, MAX_BASIS_MULTIPLICITY + 1):
        for m2 in range(m1, MAX_BASIS_MULTIPLICITY + 1):
            for m3 in range(m2, MAX_BASIS_MULTIPLICITY + 1):
                yield (m1, m2, m3)


def d2_task_list(
    target_length: int = TARGET_LENGTH_D2,
) -> list[tuple[int, int, int, int, int]]:
    """Deterministic task partition: seed triple, first two non-basis indices.

    Every D2 multiset with at least two non-basis elements fixes exactly one
    seed triple and one nondecreasing (first, second) index pair, so the
    product partitions the search tree without overlap and balances the 48
    LUNARC workers far better than first-element sharding alone (the largest
    first-element shard would otherwise dominate the wall clock).  For
    reduced target lengths with fewer than two non-basis elements the
    partition degrades gracefully: one first-element task per first index
    (``second = -1``), and a single seed-only task (``first = second = -1``)
    when the target equals the seed length.
    """

    tasks: list[tuple[int, int, int, int, int]] = []
    for m1, m2, m3 in iter_seed_triples():
        seed_length = m1 + m2 + m3
        tail = target_length - seed_length
        if tail >= 2:
            for first in range(len(NONBASIS)):
                for second in range(first, len(NONBASIS)):
                    tasks.append((m1, m2, m3, first, second))
        elif tail == 1:
            for first in range(len(NONBASIS)):
                tasks.append((m1, m2, m3, first, -1))
        else:
            tasks.append((m1, m2, m3, -1, -1))
    return tasks


def _d2_task_worker(
    task: tuple[int, int, int, int, int],
    *,
    target_length: int = TARGET_LENGTH_D2,
    node_budget: int = 2_000_000_000,
    deadline: float | None = None,
) -> tuple[tuple[tuple[int, ...], ...], int, int, int]:
    """Enumerate one (first, second) shard of the normalized D2 census.

    The witness predicate is enforced exactly by the incremental
    two-disjoint-pair dynamic program (a leaf is a witness iff the pair
    ``(0, 0) never appeared), the Lemma-A depth prune rejects zero sums of
    length at most ``T_D2`` inside the reach board, and the projective-line
    capacity bound collapses branches that cannot reach the target length.

    Returns the witness multisets in depth-first discovery order, the number
    of candidate extensions attempted, the number of surviving search states
    visited, and the number of line-bound prunes.
    """

    m1, m2, m3, first, second = task
    state: tuple[tuple[bytes, ...], frozenset[int], frozenset[int]] | None = _seed_d2_state(
        (m1, m2, m3)
    )
    seed_length = m1 + m2 + m3
    records: list[tuple[int, ...]] = []
    chosen: list[int] = []
    nodes = 0
    states = 0
    bound_prunes = 0
    start = 0
    for index in (first, second):
        if index < 0:
            continue
        assert state is not None
        state = _extend_d2_state(state, NONBASIS[index])
        if state is None:
            return (), 0, 0, 0
        chosen.append(NONBASIS[index])
        start = index
    assert state is not None

    def dfs(
        current: tuple[tuple[bytes, ...], frozenset[int], frozenset[int]],
        start: int,
    ) -> None:
        nonlocal nodes, bound_prunes, states
        states += 1
        length = seed_length + len(chosen)
        remaining = target_length - length
        if remaining == 0:
            records.append(
                tuple(sorted([BASIS[0]] * m1 + [BASIS[1]] * m2 + [BASIS[2]] * m3 + chosen))
            )
            return
        extend = _extend_d2_state
        survivors: list[tuple[int, tuple[tuple[bytes, ...], frozenset[int], frozenset[int]]]] = []
        live_lines: set[int] = set()
        line_of = _LINE_OF
        for index in range(start, len(NONBASIS)):
            nodes += 1
            if not nodes & 0xFFF and deadline is not None and time.monotonic() > deadline:
                raise ResourceBudgetExceeded("D2 census exceeded its declared wall-clock budget")
            if nodes > node_budget:
                raise ResourceBudgetExceeded("D2 census exceeded its declared per-task node budget")
            extended = extend(current, NONBASIS[index])
            if extended is None:
                continue
            survivors.append((index, extended))
            live_lines.add(line_of[NONBASIS[index]])
        # Every live candidate has multiplicity cap >= 1 and every live line
        # contributes at least one element to the capacity bound, so when at
        # least ``remaining`` lines are live the bound cannot fall below the
        # target and the full cap computation is skipped.
        if (
            len(live_lines) < remaining
            and _line_capacity_bound(current[0], start, length, remaining) < target_length
        ):
            bound_prunes += 1
            return
        for index, extended in survivors:
            chosen.append(NONBASIS[index])
            dfs(extended, index)
            chosen.pop()

    dfs(state, start)
    return tuple(records), nodes, states, bound_prunes


def enumerate_d3_extensions(
    witness: Sequence[int],
    *,
    deadline: float | None = None,
) -> tuple[tuple[tuple[int, ...], ...], bool]:
    """Enumerate every admissible 6-element extension block for one D2 witness.

    Mirrors the public pass-1 definition exactly: A is built in nondecreasing
    order, its final element is forced to negate the running partial sum so
    that A is itself a zero sum, each candidate is skipped when its negation
    is reachable with at most four elements, and every state transition
    rejects a new zero-sum of length at most five.  Returns the extension
    tuples in enumeration order and whether the witness could host any
    extension at all (a witness with a zero-sum of length at most five
    cannot).
    """

    state: tuple[bytes, ...] | None = _empty_state(T_D3)
    for element in witness:
        assert state is not None
        state = _extend(state, element, T_D3)
        if state is None:
            return (), False
    assert state is not None
    extensions: list[tuple[int, ...]] = []
    chosen: list[int] = []

    def rec(current: tuple[bytes, ...], depth: int, minv: int, asum: int) -> None:
        if depth == 0:
            extensions.append(tuple(chosen))
            return
        if depth == 1:
            forced = _NEG[asum]
            if forced < minv or forced == 0:
                return
            low = high = forced
        else:
            low, high = minv, 124
        for value in range(low, high + 1):
            if deadline is not None and time.monotonic() > deadline:
                raise ResourceBudgetExceeded("D3 census exceeded its declared wall-clock budget")
            negative = _NEG[value]
            if any(negative in current[weight] for weight in range(T_D3)):
                continue
            extended = _extend(current, value, T_D3)
            if extended is None:
                continue
            chosen.append(value)
            rec(extended, depth - 1, value, _ADD_TABLE[asum][value])
            chosen.pop()

    rec(state, EXTENSION_LENGTH_D3, 1, 0)
    return tuple(extensions), True


_WORKER_CONFIG: dict[str, Any] = {}


def _initialize_worker(node_budget: int, deadline: float | None, target_length: int) -> None:
    _WORKER_CONFIG["node_budget"] = node_budget
    _WORKER_CONFIG["deadline"] = deadline
    _WORKER_CONFIG["target_length"] = target_length


def _run_d2_task(task: tuple[int, int, int, int]) -> tuple[Any, ...]:
    return _d2_task_worker(
        task,
        target_length=_WORKER_CONFIG["target_length"],
        node_budget=_WORKER_CONFIG["node_budget"],
        deadline=_WORKER_CONFIG["deadline"],
    )


def _run_d3_witness(
    payload: tuple[int, tuple[int, ...]],
) -> tuple[int, tuple[tuple[int, ...], ...], bool]:
    ordinal, witness = payload
    extensions, hostable = enumerate_d3_extensions(witness, deadline=_WORKER_CONFIG["deadline"])
    return ordinal, extensions, hostable


def _map_d3_chunk(
    chunk: list[tuple[int, tuple[int, ...]]],
) -> list[tuple[int, tuple[tuple[int, ...], ...], bool]]:
    return [_run_d3_witness(payload) for payload in chunk]


def _chunk_witnesses(
    witnesses: Sequence[tuple[int, ...]], size: int
) -> Iterator[list[tuple[int, tuple[int, ...]]]]:
    for start in range(0, len(witnesses), size):
        yield [
            (ordinal, witnesses[ordinal])
            for ordinal in range(start, min(start + size, len(witnesses)))
        ]


def generate_d2_records(
    *,
    threads: int,
    max_wall_seconds: int,
    node_budget: int,
    target_length: int = TARGET_LENGTH_D2,
    task_limit: int | None = None,
) -> tuple[list[tuple[int, ...]], dict[str, int]]:
    """Run the complete D2 census across the deterministic task partition."""

    tasks = d2_task_list(target_length)
    if task_limit is not None:
        tasks = tasks[:task_limit]
    deadline = time.monotonic() + max_wall_seconds if max_wall_seconds > 0 else None
    started = time.monotonic()
    records: list[tuple[int, ...]] = []
    nodes = 0
    states_visited = 0
    bound_prunes = 0
    if threads <= 1:
        _initialize_worker(node_budget, deadline, target_length)
        results = [_run_d2_task(task) for task in tasks]
    else:
        with ProcessPoolExecutor(
            max_workers=threads,
            initializer=_initialize_worker,
            initargs=(node_budget, deadline, target_length),
        ) as pool:
            results = list(pool.map(_run_d2_task, tasks, chunksize=1))
    for task_records, task_nodes, task_states, task_bound_prunes in results:
        records.extend(task_records)
        nodes += task_nodes
        states_visited += task_states
        bound_prunes += task_bound_prunes
    if len(records) != fm.D2_SPEC.expected_record_count:
        raise CensusGenerationMismatch(
            f"D2 census produced {len(records)} records, "
            f"expected {fm.D2_SPEC.expected_record_count}"
        )
    metrics = {
        "d2_tasks": len(tasks),
        "d2_nodes": nodes,
        "d2_states": states_visited,
        "d2_line_bound_prunes": bound_prunes,
        "d2_wall_seconds": round(time.monotonic() - started, 3),
    }
    return records, metrics


def generate_d3_records(
    witnesses: Sequence[tuple[int, ...]],
    *,
    threads: int,
    max_wall_seconds: int,
    chunk_size: int = 16,
) -> tuple[list[tuple[int, ...]], dict[str, int]]:
    """Run the complete D3 extension census over every D2 witness."""

    deadline = time.monotonic() + max_wall_seconds if max_wall_seconds > 0 else None
    started = time.monotonic()
    chunks = list(_chunk_witnesses(witnesses, chunk_size))
    records: list[tuple[int, ...]] = []
    skipped_witnesses = 0
    if threads <= 1:
        _initialize_worker(0, deadline, TARGET_LENGTH_D2)
        for chunk in chunks:
            for ordinal, extensions, hostable in map(_run_d3_witness, chunk):
                if not hostable:
                    skipped_witnesses += 1
                records.extend(tuple(witnesses[ordinal]) + extension for extension in extensions)
    else:
        with ProcessPoolExecutor(
            max_workers=threads,
            initializer=_initialize_worker,
            initargs=(0, deadline, TARGET_LENGTH_D2),
        ) as pool:
            for chunk_result in pool.map(_map_d3_chunk, chunks):
                for ordinal, extensions, hostable in chunk_result:
                    if not hostable:
                        skipped_witnesses += 1
                    records.extend(
                        tuple(witnesses[ordinal]) + extension for extension in extensions
                    )
    if len(records) != fm.D3_SPEC.expected_record_count:
        raise CensusGenerationMismatch(
            f"D3 census produced {len(records)} records, "
            f"expected {fm.D3_SPEC.expected_record_count}"
        )
    metrics = {
        "d3_witnesses_scanned": len(witnesses),
        "d3_witnesses_skipped_short_zero_sum": skipped_witnesses,
        "d3_wall_seconds": round(time.monotonic() - started, 3),
    }
    return records, metrics


SEQUENCE_SCHEMA = "ORION.NQ.EngineB.SequenceRecord.v1"
COVERAGE_SCHEMA = "ORION.NQ.EngineB.CoverageDeclaration.v1"
GENERATION_RECEIPT_SCHEMA = "ORION.NQ.EngineB.CensusGenerationReceipt.v1"
GENERATION_TERMINAL = "NQ_CR_B_FULL_CENSUS_GENERATED_INDEPENDENTLY"
MISMATCH_TERMINAL = "NQ_CR_B_CENSUS_GENERATION_MISMATCH"
RESOURCE_TERMINAL = "NQ_CR_B_CENSUS_GENERATION_RESOURCE_BOUND"
GENERATOR_IDENTITY = (
    "crb_census.py reach-board enumerator over C_5^3 (sorted byte-value "
    "sum sets with per-element value permutations, exact incremental "
    "two-disjoint-pair DP over unordered packed sum pairs, Lemma-A depth "
    "prune, per-candidate multiplicity caps and projective-line capacity "
    "bound, forced-final-element extensions; leaves carry no adjudication "
    "work -- the pair DP decides -- and the SAT two-bin encoding is a "
    "test-suite cross-validation instrument only)"
)
NORMALIZATION_IDENTITY_D2 = (
    "every length-19 multiset with support containing the fixed basis "
    "{e1,e2,e3} and 1 <= m(e1) <= m(e2) <= m(e3) <= 4, exactly once per "
    "multiset; GL(3,5) orbit reduction NOT performed (orbit_completeness "
    "NOT_CLAIMED)"
)
NORMALIZATION_IDENTITY_D3 = (
    "every (C, A) pair with C a D2 witness and A a nondecreasing "
    "6-element zero-sum extension block with forced final element and "
    "min zero-sum >= 6 in C + A, exactly once per pair; no deduplication "
    "across pairs"
)


def _digest_of(value: Any) -> str:
    import hashlib

    return hashlib.sha256(eb.canonical_json_bytes(value)).hexdigest()


def _sequence_record(spec: fm.CensusSpec, ordinal: int, sequence: Sequence[int]) -> dict[str, Any]:
    return {
        "schema": SEQUENCE_SCHEMA,
        "record_id": fm.record_identifier(spec, ordinal),
        "scope": spec.scope,
        "sequence": list(sequence),
        "required_bins": spec.required_bins,
    }


def _derivation_digest_d2(spec: fm.CensusSpec, ordinal: int, sequence: Sequence[int]) -> str:
    multiset = list(sequence)
    basis_counts = [multiset.count(element) for element in BASIS]
    nonbasis = [element for element in multiset if element not in BASIS]
    return _digest_of(
        {
            "generator": GENERATOR_IDENTITY,
            "scope": spec.scope,
            "basis_multiplicities": basis_counts,
            "nonbasis_multiset": nonbasis,
            "ordinal": ordinal,
        }
    )


def _derivation_digest_d3(spec: fm.CensusSpec, ordinal: int, sequence: Sequence[int]) -> str:
    return _digest_of(
        {
            "generator": GENERATOR_IDENTITY,
            "scope": spec.scope,
            "witness_prefix": list(sequence[:TARGET_LENGTH_D2]),
            "extension_block": list(sequence[TARGET_LENGTH_D2:]),
            "ordinal": ordinal,
        }
    )


def _coverage_declaration(
    spec: fm.CensusSpec, coverage_argument_sha256: str, normalization_identity: str
) -> dict[str, Any]:
    return {
        "schema": COVERAGE_SCHEMA,
        "subject_commit": eb.SUBJECT_COMMIT,
        "scope": spec.scope,
        "declared_complete": True,
        "expected_record_count": spec.expected_record_count,
        "coverage_argument_sha256": coverage_argument_sha256,
        "generator_identity": GENERATOR_IDENTITY,
        "normalization_identity": normalization_identity,
    }


def write_scope_streams(
    spec: fm.CensusSpec,
    records: Sequence[tuple[int, ...]],
    output_root: Path,
    *,
    coverage_argument_sha256: str,
    normalization_identity: str,
    matrix_manifest_sha256: str,
    derivation_digest,
) -> dict[str, Any]:
    """Write sequence stream, coverage, input manifest, candidates, shards.

    The sequence stream and coverage declaration are the byte-bound inputs
    that the execution phase later reparses independently; the candidate
    stream additionally carries the matrix/orbit/derivation digests and is
    the stream the frozen ordinal partitions are materialized from.
    """

    scope_dir = output_root / "input" / spec.scope
    scope_dir.mkdir(parents=True, exist_ok=True)
    candidates_dir = output_root / "candidates"
    candidates_dir.mkdir(parents=True, exist_ok=True)
    stream_path = scope_dir / "records.jsonl"
    coverage_path = scope_dir / "coverage.json"
    stream_path.write_bytes(
        b"".join(
            eb.canonical_json_bytes(_sequence_record(spec, ordinal, sequence)) + b"\n"
            for ordinal, sequence in enumerate(records)
        )
    )
    coverage_path.write_bytes(
        eb.canonical_json_bytes(
            _coverage_declaration(spec, coverage_argument_sha256, normalization_identity)
        )
        + b"\n"
    )
    manifest = batch.build_input_manifest(
        scope_dir, stream_path="records.jsonl", coverage_path="coverage.json"
    )
    (scope_dir / "input_manifest.json").write_bytes(eb.canonical_json_bytes(manifest) + b"\n")
    candidate_stream = candidates_dir / f"{spec.scope}.candidates.jsonl"
    candidate_stream.write_bytes(
        b"".join(
            eb.canonical_json_bytes(
                fm.build_candidate_record(
                    spec,
                    ordinal=ordinal,
                    sequence=sequence,
                    matrix_witness_sha256=matrix_manifest_sha256,
                    orbit_key_sha256=_digest_of({"scope": spec.scope, "sequence": list(sequence)}),
                    derivation_sha256=derivation_digest(spec, ordinal, sequence),
                )
            )
            + b"\n"
            for ordinal, sequence in enumerate(records)
        )
    )
    plan = fm.build_partition_plan()
    scope_plan = next(item for item in plan["scopes"] if item["scope"] == spec.scope)
    materialized = fm.materialize_scope(
        candidate_stream, scope_plan, output_root / "bundle" / spec.scope
    )
    fm.verify_materialized_scope(output_root / "bundle" / spec.scope, scope_plan, materialized)
    return {
        "scope": spec.scope,
        "record_count": len(records),
        "stream_file_sha256": _file_sha256(stream_path),
        "coverage_file_sha256": _file_sha256(coverage_path),
        "input_manifest_sha256": manifest["manifest_sha256"],
        "candidate_stream_sha256": _file_sha256(candidate_stream),
        "materialized_manifest_sha256": materialized["manifest_sha256"],
    }


def _file_sha256(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_generation_receipt(
    scope_reports: Sequence[Mapping[str, Any]],
    metrics: Mapping[str, int],
    *,
    threads: int,
    coverage_argument_sha256: str,
    matrix_manifest_sha256: str,
) -> dict[str, Any]:
    receipt: dict[str, Any] = {
        "schema": GENERATION_RECEIPT_SCHEMA,
        "terminal": GENERATION_TERMINAL,
        "generator_identity": GENERATOR_IDENTITY,
        "engine_a_inputs_consumed": False,
        "engine_a_imports": 0,
        "threads": threads,
        "coverage_argument_sha256": coverage_argument_sha256,
        "matrix_manifest_sha256": matrix_manifest_sha256,
        "scopes": list(scope_reports),
        "generation_metrics": dict(metrics),
        "counts_match_frozen_denominators": True,
        "predicate_execution": "NOT_RUN",
        "external_drup_verification": "NOT_RUN",
        "lunarc_execution": "NOT_SUBMITTED",
        "scientific_authority_delta": "NONE",
        "orbit_completeness": "NOT_CLAIMED",
        "normalization_completeness": "CANNOT_CHECK",
    }
    receipt["generation_receipt_sha256"] = _digest_of(
        {key: value for key, value in receipt.items() if key != "generation_receipt_sha256"}
    )
    return receipt


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope", choices=("d2", "both"), default="both")
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--coverage-argument", type=Path, required=True)
    parser.add_argument("--threads", type=int, default=os.cpu_count() or 1)
    parser.add_argument("--max-wall-seconds", type=int, default=82_800)
    parser.add_argument("--max-nodes-per-task", type=int, default=2_000_000_000)
    parser.add_argument("--task-limit", type=int, default=None)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    import hashlib

    coverage_argument_sha256 = hashlib.sha256(args.coverage_argument.read_bytes()).hexdigest()
    matrix_manifest = fm.build_matrix_action_manifest(3)
    output_root = args.output_root
    output_root.mkdir(parents=True, exist_ok=True)
    terminal = GENERATION_TERMINAL
    error: str | None = None
    scope_reports: list[dict[str, Any]] = []
    metrics: dict[str, int] = {}
    try:
        d2_records, d2_metrics = generate_d2_records(
            threads=args.threads,
            max_wall_seconds=args.max_wall_seconds,
            node_budget=args.max_nodes_per_task,
            task_limit=args.task_limit,
        )
        metrics.update(d2_metrics)
        scope_reports.append(
            write_scope_streams(
                fm.D2_SPEC,
                d2_records,
                output_root,
                coverage_argument_sha256=coverage_argument_sha256,
                normalization_identity=NORMALIZATION_IDENTITY_D2,
                matrix_manifest_sha256=matrix_manifest["matrix_sha256"],
                derivation_digest=_derivation_digest_d2,
            )
        )
        if args.scope == "both":
            d3_records, d3_metrics = generate_d3_records(
                d2_records,
                threads=args.threads,
                max_wall_seconds=args.max_wall_seconds,
            )
            metrics.update(d3_metrics)
            scope_reports.append(
                write_scope_streams(
                    fm.D3_SPEC,
                    d3_records,
                    output_root,
                    coverage_argument_sha256=coverage_argument_sha256,
                    normalization_identity=NORMALIZATION_IDENTITY_D3,
                    matrix_manifest_sha256=matrix_manifest["matrix_sha256"],
                    derivation_digest=_derivation_digest_d3,
                )
            )
    except CensusGenerationMismatch as failure:
        terminal = MISMATCH_TERMINAL
        error = str(failure)
    except ResourceBudgetExceeded as failure:
        terminal = RESOURCE_TERMINAL
        error = str(failure)
    receipt = build_generation_receipt(
        scope_reports,
        metrics,
        threads=args.threads,
        coverage_argument_sha256=coverage_argument_sha256,
        matrix_manifest_sha256=matrix_manifest["matrix_sha256"],
    )
    if error is not None:
        receipt["terminal"] = terminal
        receipt["counts_match_frozen_denominators"] = terminal == GENERATION_TERMINAL
        receipt["error"] = error
        receipt["generation_receipt_sha256"] = _digest_of(
            {key: value for key, value in receipt.items() if key != "generation_receipt_sha256"}
        )
    receipt_path = output_root / "census_generation_receipt.json"
    receipt_path.write_bytes(eb.canonical_json_bytes(receipt) + b"\n")
    print(json.dumps({"terminal": receipt["terminal"], "scopes": len(scope_reports)}))
    return 0 if error is None else (2 if terminal == MISMATCH_TERMINAL else 3)


if __name__ == "__main__":
    raise SystemExit(main())
