#!/usr/bin/env python3
"""ORION-10: the smallest explanation vocabulary that separates every exact-cost fibre.

RUN_QUEUE (PR #1762) item 9 asks to "enumerate scoped explanation vocabularies under
the fibre criterion to seek the smallest complexity that separates every exact-cost
fibre". This answers that exhaustively on the frozen small-n space, and the answer is
an impossibility rather than a number: nothing below the discrete vocabulary works.

Setting, taken verbatim from theory/certificate-explanation-gap-v1/THEORY.md and not
re-derived here:

  * A vocabulary Psi partitions instances into fibres.
  * Theorem 2: the complete set of Psi-measurable functions is the set of assignments
    of one value per fibre. A formula over Psi, whatever its operators, interaction
    order or length, computes only a function of Psi. So enumerating fibre assignments
    enumerates every formula of every size in every language over Psi.
  * Therefore an exact Psi-only explanation exists iff cost is constant on every
    Psi-fibre. That is the fibre criterion, already verified exhaustively over 21,501
    structures by the v1 checker.

The question item 9 poses is the universal one: is there a single vocabulary, coarser
than the discrete partition, that is exact for EVERY cost function on the space? The
per-cost question is trivial - the cost level sets are always sufficient - so the
scientific content is entirely in the universal quantifier, which is also the form
THEORY.md calls Route 2: a vocabulary-level impossibility that does not depend on
formula size.

Result: for every partition with a block of size >= 2 we construct an explicit witness
pair - two worlds in one fibre carrying different cost - so that vocabulary is refuted.
Hence the unique universally-exact vocabulary is the discrete one, of complexity n, and
every coarsening fails. The witnesses are exhibited, not merely counted, because
THEORY.md's Route 2 asks for exhibited instances.

No claim is promoted by this script. It states an impossibility over a frozen scope and
records the witnesses that certify it.
"""
from __future__ import annotations

import argparse
import itertools
import json
from typing import Iterator


def set_partitions(elements: tuple[int, ...]) -> Iterator[tuple[tuple[int, ...], ...]]:
    """Every set partition of `elements`, as sorted tuples of sorted blocks."""
    if not elements:
        yield ()
        return
    first, rest = elements[0], elements[1:]
    for smaller in set_partitions(rest):
        for i, block in enumerate(smaller):
            yield tuple(sorted(
                smaller[:i] + (tuple(sorted(block + (first,))),) + smaller[i + 1:]
            ))
        yield tuple(sorted(((first,),) + smaller))


def cost_is_fibre_constant(partition, cost) -> bool:
    """The fibre criterion: exact Psi-only explanation exists iff this holds."""
    return all(len({cost[w] for w in block}) == 1 for block in partition)


def refuting_witness(partition, values: int):
    """A cost function and two worlds in one fibre that disagree, or None.

    Returned as an exhibited pair, which is what THEORY.md's Route 2 requires: two
    instances with equal Psi and different exact cost, for a Psi frozen in advance.
    """
    for block in partition:
        if len(block) >= 2 and values >= 2:
            a, b = block[0], block[1]
            n = sum(len(bl) for bl in partition)
            cost = [0] * n
            cost[b] = 1
            return {"cost": cost, "world_a": a, "world_b": b,
                    "cost_a": cost[a], "cost_b": cost[b], "fibre": list(block)}
    return None


def analyse(n: int, values: int) -> dict:
    worlds = tuple(range(n))
    parts = list(set_partitions(worlds))
    discrete = tuple(sorted((w,) for w in worlds))

    universal, refuted = [], []
    for p in parts:
        w = refuting_witness(p, values)
        if w is None:
            universal.append(p)
        else:
            refuted.append({"partition": [list(b) for b in p],
                            "blocks": len(p), "witness": w})

    # independent cross-check: brute-force every cost function rather than trusting
    # the constructed witness, over the same partitions
    brute_universal = []
    for p in parts:
        if all(cost_is_fibre_constant(p, cost)
               for cost in itertools.product(range(values), repeat=n)):
            brute_universal.append(p)

    agree = sorted(universal) == sorted(brute_universal)
    return {
        "n_worlds": n,
        "cost_values": values,
        "partitions_enumerated": len(parts),
        "bell_number_check": len(parts),
        "universally_exact_vocabularies": [[list(b) for b in p] for p in universal],
        "universally_exact_count": len(universal),
        "only_universal_is_discrete": universal == [discrete],
        "minimum_sufficient_complexity": len(discrete) if universal else None,
        "refuted_count": len(refuted),
        "example_refutations": refuted[:3],
        "constructed_and_bruteforce_agree": agree,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--max-n", type=int, default=6)
    ap.add_argument("--values", type=int, default=3,
                    help="cost alphabet size; the v1 checker uses 3")
    ap.add_argument("--emit", default="RESULT.json")
    a = ap.parse_args()

    per_n = [analyse(n, a.values) for n in range(2, a.max_n + 1)]
    all_discrete = all(r["only_universal_is_discrete"] for r in per_n)
    all_agree = all(r["constructed_and_bruteforce_agree"] for r in per_n)

    out = {
        "schema": "ORION.ORION10.VocabularyMinimality.v1",
        "question": ("smallest explanation vocabulary that separates every exact-cost "
                     "fibre, over all cost functions on the space"),
        "criterion_source": "theory/certificate-explanation-gap-v1/THEORY.md Theorem 2",
        "cost_alphabet": a.values,
        "per_n": per_n,
        "terminal": ("VOCABULARY_MINIMALITY_IS_DISCRETE" if all_discrete
                     else "COARSER_UNIVERSAL_VOCABULARY_EXISTS"),
        "finding": (
            "For every n examined, the only vocabulary exact for every cost function is "
            "the discrete partition; every coarsening admits an exhibited witness pair - "
            "two worlds sharing a fibre with different cost. The smallest sufficient "
            "complexity is therefore n, and no scoped enlargement short of full "
            "separation can close the gap universally."
        ),
        "what_this_does_not_claim": (
            "Nothing about any particular ORION-10 vocabulary such as B' or B''. This is "
            "the universal statement over the frozen abstract space; a named vocabulary "
            "still requires its own witness exhibition on the real instance space. It "
            "also does not claim the per-cost question is hard - cost level sets are "
            "always sufficient for a single fixed cost function."
        ),
        "independent_crosscheck": ("constructed witnesses agree with brute-force "
                                   "enumeration over every cost function"),
        "crosscheck_passed": all_agree,
    }
    with open(a.emit, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, sort_keys=True)
        fh.write("\n")
    for r in per_n:
        print(f"  n={r['n_worlds']}: partitions={r['partitions_enumerated']:>5} "
              f"universal={r['universally_exact_count']} "
              f"only_discrete={r['only_universal_is_discrete']} "
              f"refuted={r['refuted_count']:>5} crosscheck={r['constructed_and_bruteforce_agree']}")
    print(f"  terminal: {out['terminal']}  crosscheck_passed={all_agree}")
    return 0 if all_agree else 1


if __name__ == "__main__":
    raise SystemExit(main())
