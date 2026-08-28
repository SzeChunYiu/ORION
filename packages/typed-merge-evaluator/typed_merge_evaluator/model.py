"""SCHEMA_V1 serialisation for typed merge problem instances.

A third party encodes their own domain as a SCHEMA_V1 JSON document and runs the
evaluator on it. Nothing in this module refers to ORION, Cedar or X.509.

See SCHEMA_V1.json for the normative JSON Schema.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, FrozenSet, List, Mapping, Optional, Tuple

from .core import Instance, InstanceError, Rule

SCHEMA_ID = "ORION.TypedMerge.Instance.v1"

#: A rule cap of "ALL" is shorthand for the whole license universe. It is a
#: notational convenience only: it always expands to the declared `licenses`
#: list, never to an implicit or inferred set.
CAP_ALL = "ALL"


class SchemaError(ValueError):
    """Raised when a document does not conform to SCHEMA_V1."""


def _require(doc: Mapping[str, Any], key: str, kind: type) -> Any:
    if key not in doc:
        raise SchemaError(f"missing required field {key!r}")
    value = doc[key]
    if not isinstance(value, kind):
        raise SchemaError(f"field {key!r} must be {kind.__name__}, got {type(value).__name__}")
    return value


def _str_list(value: Any, where: str) -> Tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(x, str) and x for x in value):
        raise SchemaError(f"{where} must be a list of non-empty strings")
    return tuple(value)


class Problem:
    """A parsed SCHEMA_V1 document: a core instance plus its declared views."""

    def __init__(self, doc: Mapping[str, Any]) -> None:
        schema = doc.get("schema")
        if schema != SCHEMA_ID:
            raise SchemaError(f"schema must be {SCHEMA_ID!r}, got {schema!r}")
        self.id: str = _require(doc, "id", str)
        self.title: str = str(doc.get("title", self.id))
        self.provenance: Mapping[str, Any] = doc.get("provenance", {})
        licenses = _str_list(_require(doc, "licenses", list), "licenses")
        claims = _str_list(_require(doc, "claims", list), "claims")
        if len(set(licenses)) != len(licenses):
            raise SchemaError("licenses contains duplicates")
        if len(set(claims)) != len(claims):
            raise SchemaError("claims contains duplicates")
        self.licenses: FrozenSet[str] = frozenset(licenses)
        self.claims: FrozenSet[str] = frozenset(claims)

        seeds_doc = doc.get("seeds", {})
        if not isinstance(seeds_doc, dict):
            raise SchemaError("seeds must be an object")
        seeds: Dict[str, FrozenSet[str]] = {}
        for claim, label in seeds_doc.items():
            seeds[claim] = frozenset(_str_list(label, f"seeds[{claim!r}]"))
        self.seeds = seeds

        rules: List[Rule] = []
        for index, raw in enumerate(doc.get("rules", [])):
            if not isinstance(raw, dict):
                raise SchemaError(f"rules[{index}] must be an object")
            cap_raw = raw.get("cap", CAP_ALL)
            if cap_raw == CAP_ALL:
                cap = self.licenses
            else:
                cap = frozenset(_str_list(cap_raw, f"rules[{index}].cap"))
            rules.append(
                Rule(
                    id=str(raw.get("id", f"rule{index}")),
                    body=_str_list(_require(raw, "body", list), f"rules[{index}].body"),
                    head=_require(raw, "head", str),
                    cap=cap,
                )
            )
        self.rules: Tuple[Rule, ...] = tuple(rules)
        self.refuted: FrozenSet[str] = frozenset(
            _str_list(doc.get("refuted", []), "refuted")
        )
        flat_raw = doc.get("flat_seeded_claims")
        self.flat_seeded_claims: Optional[FrozenSet[str]] = (
            None if flat_raw is None else frozenset(_str_list(flat_raw, "flat_seeded_claims"))
        )
        self.targets: Tuple[str, ...] = _str_list(doc.get("targets", []), "targets")
        for target in self.targets:
            if target not in self.claims:
                raise SchemaError(f"target {target!r} is not a declared claim")
        self.expect: Mapping[str, Any] = doc.get("expect", {})
        self.instance = Instance(
            licenses=self.licenses,
            claims=self.claims,
            seeds=self.seeds,
            rules=self.rules,
            refuted=self.refuted,
        )
        try:
            self.instance.validate()
        except InstanceError as exc:
            raise SchemaError(str(exc)) from exc
        if self.flat_seeded_claims is not None:
            unknown = self.flat_seeded_claims - self.claims
            if unknown:
                raise SchemaError(
                    f"flat_seeded_claims names unknown claims {sorted(unknown)}"
                )

    @classmethod
    def load(cls, path: "str | Path") -> "Problem":
        with open(path, "r", encoding="utf-8") as handle:
            return cls(json.load(handle))

    @classmethod
    def loads(cls, text: str) -> "Problem":
        return cls(json.loads(text))
