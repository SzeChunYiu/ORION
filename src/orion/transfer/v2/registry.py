from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

from ..types import AlgorithmCell, ProblemSignature
from .canonical import content_digest, verify_digest
from .models import (
    algorithm_cell_from_payload,
    algorithm_cell_payload,
    problem_signature_from_payload,
    problem_signature_payload,
)

CATALOG_VERSION = "ORION_TRANSFER_CATALOG_V2"


class TransferRegistry:
    """Content-addressed registry with idempotent same-content registration."""

    def __init__(self) -> None:
        self._signatures: dict[str, tuple[str, ProblemSignature]] = {}
        self._cells: dict[str, tuple[str, AlgorithmCell]] = {}

    def register_signature(self, signature: ProblemSignature) -> str:
        digest = content_digest(problem_signature_payload(signature))
        prior = self._signatures.get(signature.problem_id)
        if prior is not None and prior[0] != digest:
            raise ValueError(f"signature id collision with different content: {signature.problem_id}")
        self._signatures[signature.problem_id] = (digest, signature)
        return digest

    def register_cell(self, cell: AlgorithmCell) -> str:
        self.register_signature(cell.source_signature)
        digest = content_digest(algorithm_cell_payload(cell))
        prior = self._cells.get(cell.cell_id)
        if prior is not None and prior[0] != digest:
            raise ValueError(f"cell id collision with different content: {cell.cell_id}")
        self._cells[cell.cell_id] = (digest, cell)
        return digest

    @property
    def signatures(self) -> tuple[ProblemSignature, ...]:
        return tuple(self._signatures[key][1] for key in sorted(self._signatures))

    @property
    def cells(self) -> tuple[AlgorithmCell, ...]:
        return tuple(self._cells[key][1] for key in sorted(self._cells))

    def get_cell(self, cell_id: str) -> AlgorithmCell:
        return self._cells[cell_id][1]

    def cell_digest(self, cell_id: str) -> str:
        return self._cells[cell_id][0]

    def to_catalog(self) -> dict[str, object]:
        return {
            "catalog_version": CATALOG_VERSION,
            "signatures": [
                {
                    "digest": self._signatures[key][0],
                    "payload": problem_signature_payload(self._signatures[key][1]),
                }
                for key in sorted(self._signatures)
            ],
            "cells": [
                {
                    "digest": self._cells[key][0],
                    "payload": algorithm_cell_payload(self._cells[key][1]),
                }
                for key in sorted(self._cells)
            ],
        }

    @property
    def digest(self) -> str:
        return content_digest(self.to_catalog())

    @classmethod
    def from_catalog(cls, catalog: Mapping[str, object]) -> "TransferRegistry":
        if set(catalog) != {"catalog_version", "signatures", "cells"}:
            raise ValueError("catalog fields mismatch")
        if catalog["catalog_version"] != CATALOG_VERSION:
            raise ValueError("unsupported transfer catalog version")
        signatures = catalog["signatures"]
        cells = catalog["cells"]
        if not isinstance(signatures, list) or not isinstance(cells, list):
            raise ValueError("catalog signatures/cells must be lists")
        registry = cls()
        for item in signatures:
            if not isinstance(item, Mapping) or set(item) != {"digest", "payload"}:
                raise ValueError("invalid signature catalog entry")
            payload = item["payload"]
            digest = item["digest"]
            if not isinstance(payload, Mapping) or not isinstance(digest, str):
                raise ValueError("invalid signature catalog entry types")
            verify_digest(payload, digest)
            registered = registry.register_signature(problem_signature_from_payload(payload))
            if registered != digest:
                raise ValueError("signature registration digest mismatch")
        for item in cells:
            if not isinstance(item, Mapping) or set(item) != {"digest", "payload"}:
                raise ValueError("invalid cell catalog entry")
            payload = item["payload"]
            digest = item["digest"]
            if not isinstance(payload, Mapping) or not isinstance(digest, str):
                raise ValueError("invalid cell catalog entry types")
            verify_digest(payload, digest)
            registered = registry.register_cell(algorithm_cell_from_payload(payload))
            if registered != digest:
                raise ValueError("cell registration digest mismatch")
        return registry

    @classmethod
    def load(cls, path: str | Path) -> "TransferRegistry":
        with Path(path).open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        if not isinstance(payload, Mapping):
            raise ValueError("catalog root must be an object")
        return cls.from_catalog(payload)
