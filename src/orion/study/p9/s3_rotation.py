"""Prospective all-domain rotation helpers for P9 S3.

This module is downstream of the protected S3 access result.  It does not alter
S3's generic serialized binding operator.  It only rotates which existing D1
domain is held out while preserving D1 v1.2 generation semantics.
"""

from __future__ import annotations

from orion.transfer.v2.canonical import content_digest

# Apply the frozen D1 v1.2 dependency-mutation semantics before using the
# generator's private split helper.
from . import d1_data_runtime as _data_runtime  # noqa: F401
from . import d1 as _d1
from .d1 import D1Dataset, D1Domain, D1Split


DOMAIN_ORDER = (D1Domain.NUMERICAL, D1Domain.GRAPH, D1Domain.WORKFLOW)


def generate_rotation_dataset(
    holdout: D1Domain,
    *,
    seed: str = "p9-d1-method-transfer-v1",
    train_instances_per_base_pair: int = 48,
    dev_instances_per_base_pair: int = 16,
    test_instances_per_base_pair: int = 32,
) -> D1Dataset:
    if holdout not in DOMAIN_ORDER:
        raise ValueError(f"unsupported D1 holdout: {holdout}")
    train_domains = tuple(domain for domain in DOMAIN_ORDER if domain is not holdout)
    train = _d1._split_instances(
        seed=seed,
        split=D1Split.TRAIN,
        domains=train_domains,
        instances_per_base_pair=train_instances_per_base_pair,
        include_double=False,
    )
    dev = _d1._split_instances(
        seed=seed,
        split=D1Split.DEV,
        domains=train_domains,
        instances_per_base_pair=dev_instances_per_base_pair,
        include_double=False,
    )
    test = _d1._split_instances(
        seed=seed,
        split=D1Split.TEST,
        domains=(holdout,),
        instances_per_base_pair=test_instances_per_base_pair,
        include_double=True,
    )
    provisional = D1Dataset(
        seed=seed,
        train=train,
        dev=dev,
        test=test,
        manifest_digest="PENDING",
    )
    dataset = D1Dataset(
        seed=seed,
        train=train,
        dev=dev,
        test=test,
        manifest_digest=content_digest(provisional.manifest()),
    )
    dataset.verify()
    return dataset


def rotation_label_counts(dataset: D1Dataset) -> dict[str, dict[str, int]]:
    out: dict[str, dict[str, int]] = {}
    for name, rows in (("train", dataset.train), ("dev", dataset.dev), ("test", dataset.test)):
        counts: dict[str, int] = {}
        for row in rows:
            counts[row.label.value] = counts.get(row.label.value, 0) + 1
        out[name] = dict(sorted(counts.items()))
    return out


__all__ = ["DOMAIN_ORDER", "generate_rotation_dataset", "rotation_label_counts"]
