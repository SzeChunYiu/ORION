#!/usr/bin/env python3
"""Equality selftest for max_r5h_streaming_combine.

The streaming combine must reproduce fast_combine_frontiers EXACTLY --
same output tuple, same order -- because the N2 fold's checkpoints were
produced by the reference combine and swapping implementations mid-fold
is only legal if every future combine is bit-identical to what the
reference would have returned.

Cases:
  * randomized frontiers and local windows (many sizes, forced tiny
    ORIONQ_R5H_STREAM_ROWS so the slice count is large and the exactness
    argument is exercised at its seams);
  * adversarial left operands containing dominated states and duplicate
    discrete keys (the states an intermediate prune drops);
  * empty operands (must mirror the reference's empty result, never
    pass-through);
  * determinism (same inputs twice).

Prints ORIONQ_R5H_STREAM_COMBINE_SELFTEST=PASS n_cases=... failures=0 on
success; any mismatch prints the divergent case and exits 1.

Standalone: python3 test_max_r5h_streaming_combine.py
"""
from __future__ import annotations

import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import max_r5h_mixed_cardinality_development as b  # noqa: E402
import max_r5h_mixed_cardinality_development_fast as accel  # noqa: E402
import max_r5h_streaming_combine as stream  # noqa: E402

KINDS = ("TA", "TB", "TARE", "TT", "TS")  # partition kind labels (arbitrary)


def rand_state(rng: random.Random, max_coord: int = 9) -> b.State:
    npart = rng.randint(0, 4)
    partition = tuple(
        (rng.choice(KINDS), tuple(rng.randint(0, max_coord)
                                  for _ in range(rng.randint(1, 3))))
        for _ in range(npart)
    )
    return b.State(
        rng.randrange(0, 40) + rng.choice([0.0, 0.5, 0.25]),
        rng.randrange(0, 20),
        rng.randrange(0, 20),
        rng.randrange(0, 6),
        rng.randrange(0, 4),
        partition,
    )


def dominated_pair(rng: random.Random) -> tuple[b.State, b.State]:
    """Return (dominator, dominated) with identical partition shape."""
    big = rand_state(rng)
    worse = b.State(
        big.lam + rng.choice([0.0, 1.5]),
        big.cnot + rng.randrange(0, 3),
        big.t + rng.randrange(0, 3),
        big.blocks + rng.randrange(0, 2),
        max(0, big.ancilla + rng.randrange(0, 2)) if big.ancilla else big.ancilla,
        big.partition,
    )
    return big, worse


def main() -> int:
    rng = random.Random(20260903)
    failures: list[str] = []
    n_cases = 0
    tiny_rows = 3  # forces many slices regardless of operand sizes

    for trial in range(400):
        n_a = rng.randint(1, 14)
        n_c = rng.randint(1, 16)
        a = tuple(rand_state(rng) for _ in range(n_a))
        c = tuple(rand_state(rng) for _ in range(n_c))
        if trial % 3 == 0:  # seed dominated states + duplicates into `a`
            dom, worse = dominated_pair(rng)
            a = a + (dom, worse, worse)
        n_cases += 1
        ref = accel.fast_combine_frontiers(a, c)
        got = stream.streaming_combine_frontiers(a, c, max_live_rows=tiny_rows)
        if ref != got:  # tuple equality: same states, same order
            failures.append(
                f"trial {trial}: |ref|={len(ref)} |got|={len(got)} "
                f"first-divergence={next((i for i, (r, g) in enumerate(zip(ref, got)) if r != g), None)}")
            break

    n_cases += 1
    empty_c = accel.fast_combine_frontiers((rand_state(rng),), ())
    if stream.streaming_combine_frontiers((rand_state(rng),), (), max_live_rows=tiny_rows) != empty_c:
        failures.append("empty c: did not mirror reference empty result")
    n_cases += 1
    empty_a = accel.fast_combine_frontiers((), (rand_state(rng),))
    if stream.streaming_combine_frontiers((), (rand_state(rng),), max_live_rows=tiny_rows) != empty_a:
        failures.append("empty a: did not mirror reference empty result")

    n_cases += 1
    a = tuple(rand_state(rng) for _ in range(8))
    c = tuple(rand_state(rng) for _ in range(9))
    if stream.streaming_combine_frontiers(a, c, max_live_rows=1) != \
            stream.streaming_combine_frontiers(a, c, max_live_rows=1):
        failures.append("nondeterministic at max_live_rows=1 (slice per state)")

    for f in failures:
        print(f"SELFTEST-FAIL {f}", file=sys.stderr)
    print(f"ORIONQ_R5H_STREAM_COMBINE_SELFTEST={'PASS' if not failures else 'FAIL'} "
          f"n_cases={n_cases} failures={len(failures)}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
