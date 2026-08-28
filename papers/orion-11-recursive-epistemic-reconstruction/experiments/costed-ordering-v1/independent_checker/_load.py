"""Trace loading, purity screening and per-row invariants.

This is the deepest independent recomputation the checker can make: the cost
components are rebuilt from the `actions` audit trail rather than taken on
faith from the serialised `cost` object. A trace whose components do not
follow from its own actions is an instrument fault, not a datum.
"""

from __future__ import annotations

import json
import re
from typing import Any

from . import _constants as K
from . import _faults as F


# Keys naming a specific registered gate: "g3", "g3_pass", "G6_result", ...
_GATE_KEY_RE = re.compile(r"^g[1-7](\b|_|$)")


def _scan_keys(obj: Any, path: str = "") -> list[str]:
    """Every key name appearing anywhere in a nested structure, with paths."""
    found: list[str] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            here = f"{path}.{key}" if path else str(key)
            found.append(here)
            found.extend(_scan_keys(value, here))
    elif isinstance(obj, list):
        for item in obj:
            found.extend(_scan_keys(item, f"{path}[]"))
    return found


def _contamination_hits(row: dict[str, Any]) -> list[str]:
    """Key paths naming a gate outcome, an interval or a terminal."""
    hits: list[str] = []
    for path in _scan_keys(row):
        leaf = path.split(".")[-1].replace("[]", "").lower()
        if leaf in K.ROW_REQUIRED_KEYS or leaf in K.COST_FIELDS:
            continue
        if leaf in K.ACTION_REQUIRED_KEYS:
            continue
        if leaf in K.CONTAMINATION_EXACT_KEYS or _GATE_KEY_RE.match(leaf):
            hits.append(path)
            continue
        if any(token in leaf for token in K.CONTAMINATION_KEY_TOKENS):
            hits.append(path)
    return hits


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _canonical_stratum(raw: str, ledger: F.Ledger, seen_spellings: set[str]) -> str | None:
    if raw in K.CANONICAL_STRATA:
        seen_spellings.add(raw)
        return raw
    if raw in K.STRATUM_ALIASES:
        seen_spellings.add(raw)
        return K.STRATUM_ALIASES[raw]
    ledger.fault(F.FAULT_UNKNOWN_STRATUM, f"stratum not in the frozen set: {raw!r}", raw)
    return None


def _check_actions(row: dict[str, Any], line_no: int, ledger: F.Ledger) -> dict[str, float] | None:
    """Rebuild the cost components from the action audit trail."""
    actions = row.get("actions")
    if not isinstance(actions, list):
        ledger.fault(
            F.FAULT_MISSING_ACTIONS,
            "row has no `actions` list, so its cost decomposition cannot be derived",
            {"line": line_no, "world_id": row.get("world_id"), "arm_id": row.get("arm_id")},
        )
        return None

    rebuilt = {component: 0.0 for component in K.COST_COMPONENTS}
    for action in actions:
        if not isinstance(action, dict):
            ledger.fault(
                F.FAULT_MALFORMED_TRACE, "action entry is not an object", {"line": line_no}
            )
            return None
        missing = [k for k in K.ACTION_REQUIRED_KEYS if k not in action]
        if missing:
            ledger.fault(
                F.FAULT_MALFORMED_TRACE,
                f"action entry missing required keys: {sorted(missing)}",
                {"line": line_no, "world_id": row.get("world_id")},
            )
            return None
        component = action["cost_component"]
        if component not in K.COST_COMPONENTS:
            ledger.fault(
                F.FAULT_MALFORMED_TRACE,
                f"action cost_component not one of {list(K.COST_COMPONENTS)}: {component!r}",
                {"line": line_no, "world_id": row.get("world_id")},
            )
            return None
        if not _is_number(action["cost"]):
            ledger.fault(
                F.FAULT_MALFORMED_TRACE, "action cost is not a number", {"line": line_no}
            )
            return None
        if action["cost"] < 0.0:
            ledger.fault(
                F.FAULT_NEGATIVE_COST_COMPONENT,
                "negative action cost; cost accounting must stay non-negative even on "
                "the A4-violation stratum, where the violation is in the world's cost "
                "structure and not in the accounting",
                {
                    "line": line_no,
                    "world_id": row.get("world_id"),
                    "arm_id": row.get("arm_id"),
                    "cost": action["cost"],
                },
            )
            return None
        rebuilt[component] += float(action["cost"])
    return rebuilt


def _check_cost(row: dict[str, Any], line_no: int, ledger: F.Ledger) -> dict[str, float] | None:
    cost = row.get("cost")
    if not isinstance(cost, dict):
        ledger.fault(F.FAULT_MALFORMED_TRACE, "row `cost` is not an object", {"line": line_no})
        return None
    for name in K.COST_FIELDS:
        if name not in cost or not _is_number(cost[name]):
            ledger.fault(
                F.FAULT_MALFORMED_TRACE,
                f"row cost missing or non-numeric field {name!r}",
                {"line": line_no, "world_id": row.get("world_id")},
            )
            return None

    values = {name: float(cost[name]) for name in K.COST_FIELDS}
    ident = {
        "line": line_no,
        "world_id": row.get("world_id"),
        "arm_id": row.get("arm_id"),
        "stratum": row.get("stratum"),
    }

    negative = [name for name in K.COST_FIELDS if values[name] < 0.0]
    if negative:
        ledger.fault(
            F.FAULT_NEGATIVE_COST_COMPONENT,
            "negative cost component(s): " + ", ".join(sorted(negative)),
            {**ident, "cost": values},
        )
        return None

    residual = values["total"] - sum(values[c] for c in K.COST_COMPONENTS)
    if abs(residual) > K.DECOMPOSITION_TOLERANCE:
        ledger.fault(
            F.FAULT_UNDECOMPOSABLE_COST,
            f"|total - (inspection + intervention + reopening)| > {K.DECOMPOSITION_TOLERANCE}",
            {**ident, "cost": values, "residual": residual},
        )
        return None

    rebuilt = _check_actions(row, line_no, ledger)
    if rebuilt is None:
        return None
    for component in K.COST_COMPONENTS:
        drift = rebuilt[component] - values[component]
        if abs(drift) > K.DECOMPOSITION_TOLERANCE:
            ledger.fault(
                F.FAULT_ACTIONS_DISAGREE_WITH_COMPONENTS,
                f"component {component!r} does not follow from the action audit trail",
                {
                    **ident,
                    "serialised": values[component],
                    "rebuilt_from_actions": rebuilt[component],
                    "drift": drift,
                },
            )
            return None

    flag = row.get("budget_exceeded")
    if not isinstance(flag, bool):
        ledger.fault(
            F.FAULT_MALFORMED_TRACE, "row `budget_exceeded` is not a boolean", ident
        )
        return None
    over = values["total"] > K.BUDGET_CEILING + K.DECOMPOSITION_TOLERANCE
    under = values["total"] < K.BUDGET_CEILING - K.DECOMPOSITION_TOLERANCE
    # Rows sitting exactly on the ceiling are not adjudicated either way.
    if (over and not flag) or (under and flag):
        ledger.fault(
            F.FAULT_BUDGET_FLAG_INCONSISTENT,
            f"budget_exceeded disagrees with total vs ceiling {K.BUDGET_CEILING}",
            {**ident, "total": values["total"], "budget_exceeded": flag},
        )
        return None
    return values


def load_traces(path: str, ledger: F.Ledger) -> list[dict[str, Any]]:
    """Parse raw_traces.jsonl and enforce every per-row invariant."""
    try:
        with open(path, "r", encoding="utf-8") as handle:
            raw_lines = handle.readlines()
    except FileNotFoundError:
        ledger.fault(F.FAULT_MISSING_TRACE, f"trace file not found: {path}", path)
        return []
    except OSError as exc:  # unreadable, a directory, permissions
        ledger.fault(F.FAULT_MISSING_TRACE, f"trace file unreadable: {path} ({exc})", path)
        return []

    rows: list[dict[str, Any]] = []
    seen_spellings: set[str] = set()

    for line_no, line in enumerate(raw_lines, start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            ledger.fault(
                F.FAULT_MALFORMED_TRACE, f"line is not valid JSON ({exc.msg})", {"line": line_no}
            )
            continue
        if not isinstance(row, dict):
            ledger.fault(
                F.FAULT_MALFORMED_TRACE, "line is not a JSON object", {"line": line_no}
            )
            continue

        hits = _contamination_hits(row)
        if hits:
            ledger.fault(
                F.FAULT_CONTAMINATED_ROW,
                "row carries a gate outcome, an interval or a terminal; "
                "aggregation is the checker's job to redo",
                {"line": line_no, "world_id": row.get("world_id"), "keys": sorted(hits)},
            )
            continue

        missing = [k for k in K.ROW_REQUIRED_KEYS if k not in row]
        if missing:
            ledger.fault(
                F.FAULT_MALFORMED_TRACE,
                f"row missing required keys: {sorted(missing)}",
                {"line": line_no, "world_id": row.get("world_id")},
            )
            continue

        unexpected = [
            k
            for k in row
            if k not in K.ROW_REQUIRED_KEYS and k not in K.CONTAMINATION_EXACT_KEYS
        ]
        if unexpected:
            ledger.warn(
                "UNEXPECTED_ROW_FIELD",
                "row carries fields outside TRACE_SCHEMA_V1; they name no derived "
                "quantity, so they are reported rather than refused",
                {"line": line_no, "fields": sorted(unexpected)},
            )

        if not isinstance(row["world_id"], str) or not row["world_id"]:
            ledger.fault(
                F.FAULT_MALFORMED_TRACE, "world_id is not a non-empty string", {"line": line_no}
            )
            continue
        if not isinstance(row["seed"], int) or isinstance(row["seed"], bool):
            ledger.fault(
                F.FAULT_MALFORMED_TRACE, "seed is not an integer", {"line": line_no}
            )
            continue
        for flag_name in ("protected_root_task_success", "forbidden_high_level_mutation"):
            if not isinstance(row[flag_name], bool):
                ledger.fault(
                    F.FAULT_MALFORMED_TRACE, f"{flag_name} is not a boolean", {"line": line_no}
                )
                break
        else:
            if row["arm_id"] not in K.KNOWN_ARMS:
                ledger.fault(
                    F.FAULT_UNKNOWN_ARM,
                    f"arm_id not in the frozen arm set: {row['arm_id']!r}",
                    {"line": line_no, "arm_id": row["arm_id"]},
                )
                continue
            stratum = _canonical_stratum(row["stratum"], ledger, seen_spellings)
            if stratum is None:
                continue
            values = _check_cost(row, line_no, ledger)
            if values is None:
                continue
            rows.append(
                {
                    "line": line_no,
                    "world_id": row["world_id"],
                    "stratum": stratum,
                    "stratum_as_written": row["stratum"],
                    "arm_id": row["arm_id"],
                    "seed": row["seed"],
                    "success": row["protected_root_task_success"],
                    "forbidden": row["forbidden_high_level_mutation"],
                    "cost": values,
                    "budget_exceeded": row["budget_exceeded"],
                    "action_signature": tuple(
                        (a["kind"], a["level"], a["target"]) for a in row["actions"]
                    ),
                    "terminated_reason": row["terminated_reason"],
                }
            )

    a4_spellings = sorted(
        s for s in seen_spellings if s == K.STRATUM_A4 or s in K.STRATUM_ALIASES
    )
    if len(a4_spellings) > 1:
        ledger.fault(
            F.FAULT_STRATUM_ALIAS_COLLISION,
            "both frozen spellings of the A4-violation stratum appear in one trace file; "
            "stratum identity is ambiguous and cannot be canonicalised",
            {"spellings": a4_spellings},
        )
    elif a4_spellings and a4_spellings[0] != K.STRATUM_A4:
        ledger.defect(
            f"A4-violation stratum serialised as {a4_spellings[0]!r} (TRACE_SCHEMA_V1.json "
            f"spelling); PROTOCOL.json spells it {K.STRATUM_A4!r}. Canonicalised to the "
            "PROTOCOL spelling."
        )

    if not rows and not ledger.refused:
        ledger.fault(F.FAULT_MISSING_TRACE, f"trace file contains no rows: {path}", path)
    return rows
