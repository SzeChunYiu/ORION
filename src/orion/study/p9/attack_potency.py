"""Which of P9's hostile attacks could have succeeded, and which could not.

``P9_U_T4_HOSTILE_ATTACK_RESULT_2026-08-21`` runs three hostile dataset
variants against eight representation arms and reports that one component
succeeded. The other twenty-three cells report no violation. This asks a prior
question the battery does not: for each of those cells, did the attack change
anything the learner can see?

For fourteen of the twenty-four it did not, and one whole variant is inert
against every arm.

======================  ========================================
variant                 instances whose feature vector changed
======================  ========================================
``ORDER_PERMUTATION``   0 of 512, on **all eight** arms
``EQUAL_LENGTH``        112 of 512 on seven arms, 0 on one
``SEMANTIC_ORBIT``      512 of 512 on two arms, 0 on six
======================  ========================================

``ORDER_PERMUTATION`` is not merely invisible to the arms. Its dataset is
*identical* to the base, manifest digest included, and the reason is worth more
than the finding.

The variant reverses every sequence-valued comparison coordinate and then
rebuilds the method through ``build_method_realization``, which normalises each
of those coordinates with::

    tuple(sorted({str(x) for x in (values or ())}))

A sorted set. The reversal is undone by the rebuild on the line after it is
applied, and duplicates would be dropped the same way. So the transform is a
no-op by construction, and the first draft of this module said the opposite ---
that the transform was real and only the feature functions were order-blind ---
until a test asserting the reordered dataset differs from the base failed.

The consequence is larger than a wiring bug, and it is the part that matters.
Ordering is not representable in ``MethodRealization`` at all: the coordinates
the battery's ``SEQUENCE_COORDINATES`` constant names as sequences are stored as
sorted sets. Repairing the wiring would not produce an order attack. There is no
order to attack until the representation carries one, and every downstream
feature family is order-blind for the same reason rather than by coincidence.

One precondition passes vacuously as a result. ``PC-2_GOLD_PRESERVATION``
reports ``labels_changed: 0`` over 512 instances for this variant, which is
trivially true of a dataset that was never changed.

Why this is not a complaint about the battery
---------------------------------------------
The battery is careful. It carries six preconditions and a round-trip check, and
it already refuses a contrast whose comparator answered with a single label,
under the rule that "an attack cannot fail against a margin that was never
measured". That rule is exactly right and this is the same rule applied one
level earlier: an attack cannot fail against an input it did not change.

What is missing is a precondition, not a principle. ``PC-2`` checks that the
transform preserved every label, which is what stops a corrupted variant from
being a different benchmark. Nothing checks the other side --- that it changed
something. A transform can satisfy every existing precondition perfectly while
changing nothing at all, and ``ORDER_PERMUTATION`` does: it passes gold
preservation, cardinality match and index reversibility because it is the
identity.

This module measures that directly rather than arguing it, and reads only: the
frozen parameter block is not touched, so the committed result keeps its
digest and its authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

SCHEMA_VERSION = "orion.p9.attack-potency.v1"

#: The base dataset key in the committed runner's variant map.
BASE_VARIANT = "BASE"


@dataclass(frozen=True)
class CellPotency:
    """One (variant, arm) cell of the attack grid."""

    variant: str
    arm: str
    instances: int
    changed: int

    @property
    def attacked(self) -> bool:
        """Did the transform change anything this arm can see?"""

        return self.changed > 0

    def as_json(self) -> dict[str, Any]:
        return {
            "variant": self.variant,
            "arm": self.arm,
            "instances": self.instances,
            "changed": self.changed,
            "attacked": self.attacked,
        }


def _instances(dataset: Any) -> list[Any]:
    return list(dataset.train) + list(dataset.dev) + list(dataset.test)


def measure_potency() -> tuple[CellPotency, ...]:
    """Rebuild the frozen variants and compare feature vectors cell by cell.

    Compares the extracted features rather than the datasets, because that is
    the only comparison that answers the question. Two datasets can differ in
    every byte while producing identical feature vectors, and then the attack
    reached the file and not the model.
    """

    from orion.study.p9 import hostile_representation_attacks as battery

    datasets = battery.build_datasets()
    base = _instances(datasets[BASE_VARIANT])

    cells: list[CellPotency] = []
    for variant, dataset in sorted(datasets.items()):
        if variant == BASE_VARIANT:
            continue
        transformed = _instances(dataset)
        if len(transformed) != len(base):
            raise ValueError(
                f"{variant} has {len(transformed)} instances against the base's {len(base)}; "
                "a variant with a different case count is a different benchmark"
            )
        for arm, extract in sorted(battery.FEATURE_FUNCTIONS.items()):
            changed = sum(
                1
                for original, mutated in zip(base, transformed)
                if extract(original) != extract(mutated)
            )
            cells.append(
                CellPotency(variant=variant, arm=arm, instances=len(base), changed=changed)
            )
    return tuple(cells)


def canonicalisation_undoes_reordering() -> dict[str, Any]:
    """Show, on one method, that the rebuild reverses the reversal.

    Demonstrated rather than argued, because the claim is about a normaliser two
    modules away and a reader should not have to take it on trust. Also checks
    the duplicate case, since ``tuple(sorted(set(...)))`` drops repeats as well
    as order --- a second class of transform this data model cannot express.
    """

    from orion.study.p9 import hostile_representation_attacks as battery

    datasets = battery.build_datasets()
    method = _instances(datasets[BASE_VARIANT])[0].left
    original = tuple(method.preconditions)
    reversed_input = tuple(reversed(original))
    after_reversal = tuple(battery._rebuild_with(method, preconditions=reversed_input).preconditions)
    duplicated_input = original + original[:1]
    after_duplication = tuple(
        battery._rebuild_with(method, preconditions=duplicated_input).preconditions
    )

    base = _instances(datasets[BASE_VARIANT])
    order = _instances(datasets["ORDER_PERMUTATION"])

    return {
        "original": list(original),
        "reversed_input": list(reversed_input),
        "after_rebuild": list(after_reversal),
        "reversal_survives_the_rebuild": after_reversal != original,
        "duplicated_input": list(duplicated_input),
        "after_rebuild_with_duplicate": list(after_duplication),
        "duplicate_survives_the_rebuild": len(after_duplication) != len(original),
        "order_variant_is_identical_to_base": all(a == b for a, b in zip(base, order)),
        "manifest_digests_equal": (
            datasets[BASE_VARIANT].manifest_digest == datasets["ORDER_PERMUTATION"].manifest_digest
        ),
        "normaliser": "tuple(sorted({str(x) for x in (values or ())}))",
        "reading": (
            "The rebuild normalises every sequence coordinate to a sorted set, so the "
            "reversal is undone on the line after it is applied and duplicates are "
            "dropped. Ordering is not representable in MethodRealization, so repairing "
            "the wiring would not produce an order attack -- the representation would "
            "have to carry an order first."
        ),
    }


def build_report(*, date: str) -> dict[str, Any]:
    """Everything this module establishes, with what it does not."""

    cells = measure_potency()
    canonicalisation = canonicalisation_undoes_reordering()
    inert = [cell for cell in cells if not cell.attacked]
    variants = sorted({cell.variant for cell in cells})
    fully_inert = sorted(
        variant
        for variant in variants
        if all(not cell.attacked for cell in cells if cell.variant == variant)
    )
    per_variant = {
        variant: {
            "arms": sum(1 for cell in cells if cell.variant == variant),
            "arms_actually_attacked": sum(
                1 for cell in cells if cell.variant == variant and cell.attacked
            ),
            "instances_changed_by_arm": {
                cell.arm: cell.changed for cell in cells if cell.variant == variant
            },
        }
        for variant in variants
    }

    return {
        "schema_version": SCHEMA_VERSION,
        "record": "P9_ATTACK_POTENCY",
        "date": date,
        "cells": [cell.as_json() for cell in cells],
        "canonicalisation": canonicalisation,
        "per_variant": per_variant,
        "cells_total": len(cells),
        "cells_inert": len(inert),
        "inert_cells": [f"{cell.variant}/{cell.arm}" for cell in inert],
        "fully_inert_variants": fully_inert,
        "every_cell_attacked_something": not inert,
        "what_this_establishes": (
            f"{len(inert)} of the {len(cells)} (variant, arm) cells in P9's hostile "
            "representation battery leave the arm's feature vector unchanged on every "
            "one of the 512 instances, so the attack could not have produced a violation "
            "there whatever the arm did. ORDER_PERMUTATION is inert against all eight "
            "arms for a stronger reason than order-blind features: its dataset is "
            "identical to the base, manifest digest included. It reverses sequence "
            "coordinates and then rebuilds through a normaliser that maps each of them "
            "to tuple(sorted(set(...))), so the reversal is undone on the following "
            "line. Ordering is not representable in MethodRealization at all -- the "
            "coordinates the battery names as sequences are stored as sorted sets -- so "
            "repairing the wiring would not produce an order attack, and the "
            "order-blindness of every feature family follows from the same fact rather "
            "than being a separate coincidence. PC-2_GOLD_PRESERVATION reports zero "
            "labels changed over 512 instances for this variant, which is trivially "
            "true of an identity. EQUAL_LENGTH reaches seven of eight arms on 112 instances "
            "each and SEMANTIC_ORBIT reaches two of eight on all 512, so the battery does "
            "perturb in general and this is a statement about specific cells rather than "
            "about the battery as a whole. The battery already refuses a contrast whose "
            "comparator answered with one label, under the rule that an attack cannot "
            "fail against a margin that was never measured; the missing precondition is "
            "that same rule one level earlier."
        ),
        "not_licensed": [
            "any claim that the arms are not robust to reordering; no ordering was ever "
            "presented to them, and none can be until the representation carries one",
            "any claim that the committed result is wrong; every number in it is what "
            "its stated procedure produces, and its one reported success stands",
            "any change to the frozen parameter block, which this module only reads",
            "any empirical claim about a language model, a scale or a second family; "
            "the committed study's BOUNDED_D1_ONLY scope carries over unchanged",
        ],
    }


def main(argv: list[str]) -> int:
    """CLI entry point. ``argv`` is required: there is no implicit run."""

    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(
        prog="orion-p9-attack-potency",
        description="Measure which of P9's hostile attacks could have succeeded.",
    )
    parser.add_argument("--date", required=True)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)

    report = build_report(date=args.date)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"written: {args.output}")

    for variant, summary in sorted(report["per_variant"].items()):
        reached = summary["arms_actually_attacked"]
        flag = "!" if reached == 0 else " "
        print(f"  {flag} {variant}: reached {reached} of {summary['arms']} arms")
        for arm, changed in sorted(summary["instances_changed_by_arm"].items()):
            mark = "  <- inert" if changed == 0 else ""
            print(f"        {arm:24s} {changed:4d} instances changed{mark}")
    print(f"  inert cells: {report['cells_inert']} of {report['cells_total']}")
    canon = report["canonicalisation"]
    print(
        "  reversal survives the rebuild: "
        f"{canon['reversal_survives_the_rebuild']}; "
        f"order variant identical to base: {canon['order_variant_is_identical_to_base']}"
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    import sys

    raise SystemExit(main(sys.argv[1:]))
