from __future__ import annotations

import hashlib
import importlib.util
import json
import random
import re
import sys
from collections import Counter, defaultdict
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Mapping, Sequence

ROOT = Path(__file__).resolve().parent
P1_ROOT = ROOT.parent
R2_ROOT = P1_ROOT / "gpt_r2"
R5_ROOT = P1_ROOT / "gpt_r5"
PROTOCOL = json.loads((ROOT / "NATIVE_PROTOCOL_V1.json").read_text())
R2_PROTOCOL = json.loads((R2_ROOT / "PROTOCOL_V1.json").read_text())
FIXED = json.loads((R5_ROOT / "FIXED_SOURCE_SET_V1.json").read_text())


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(name, None)
        raise
    return module


NATIVE = _load(ROOT / "native_orion.py", "p1_u_r6_native")
B3_POLICY = _load(R2_ROOT / "policy.py", "p1_u_r6_b3")
CORPUS = _load(R5_ROOT / "build_fixed_corpus.py", "p1_u_r6_fixed_corpus")

CONTROL = str(PROTOCOL["control_class"])
UNRESOLVED = str(PROTOCOL["unresolved_class"])
PROBES = set(PROTOCOL["probes"])
ALLOWED_OBS = set(PROTOCOL["probe_observations"])
HIGH = {"OBJECTIVE_OR_MODEL_CLASS", "PROBLEM_BOUNDARY"}
LOW = {
    "SEARCH_OR_EVIDENCE",
    "REPRESENTATION_OR_INTERFACE",
    "IMPLEMENTATION_OR_ENVIRONMENT",
    "MEASUREMENT_OR_EVALUATOR",
}
SUBSTANTIVE = LOW | HIGH
ALL_GOLD_CLASSES = SUBSTANTIVE | {CONTROL, UNRESOLVED}
EXPECTED_PAIRS = {r["source_id"]: r for r in FIXED["pair_sources"]}
EXPECTED_UNRES = {r["source_id"]: r for r in FIXED["unresolved_sources"]}

#: The primary year, read from the frozen source set rather than written here.
#:
#: This was the literal ``2020`` in two row checks. A replication corpus drawn
#: from any other year -- the obvious next experiment, and the one #723 asks for
#: -- therefore could not run through this evaluator at all: every row failed
#: the year check, every source id missed ``EXPECTED_PAIRS``, and the result came
#: back as a frozen-corpus CANNOT_CHECK with zero episodes scored and nothing
#: raised. The year the primary was drawn from is a property of the source set,
#: and the source set already declares it.
PRIMARY_YEAR = int(FIXED["primary_year"])

# P1-U-T3 repair 3. The frozen corpus mints episode ids as
# f"R5-{query_id}-{suffix}" (gpt_r5/build_fixed_corpus.py:172-180), so the
# trailing suffix *is* the pair role. Any payload carrying the episode id
# therefore carries the role, and for the 22 control episodes the role is a
# perfect predictor of the gold class.
ROLE_SUFFIX_TO_ROLE = {"-A": "adverse", "-C": "control", "-U": "unresolved"}
# Structural role assignment, e.g. '"pair_role": "adverse"' or 'role=control'.
# The bare English words are deliberately NOT tokens: two frozen control
# dossiers (R5-MEAS-P1-C, R5-OBJ-P2-C) use "quality-control" and
# "positive-control" as ordinary domain vocabulary, and a guard that fires on
# those is a guard nobody will believe. The role stays fully covered by the
# episode-id token, which does fire.
ROLE_ASSIGNMENT = re.compile(
    r"(?i)(pair[_-]?)?role[\"\s]*[:=][\"\s]*(adverse|control|unresolved)"
)


class B3ProbeGate(Mapping[str, str]):
    def __init__(self, hidden: Mapping[str, str]):
        if set(hidden) != PROBES:
            raise ValueError("B3 probe set mismatch")
        self._hidden = dict(hidden)
        self.revealed: list[tuple[str, str]] = []

    def __getitem__(self, key: str) -> str:
        if key not in self._hidden:
            raise KeyError(key)
        value = str(self._hidden[key])
        self.revealed.append((key, value))
        return value

    def __iter__(self):
        raise RuntimeError("B3 may not enumerate evaluator-owned probes")

    def __len__(self) -> int:
        return len(self._hidden)


def fixed_corpus() -> tuple[list[dict], list[dict]]:
    pairs, unresolved = CORPUS.build()
    return list(pairs), list(unresolved)


def _validate_episode(ep: Mapping[str, object], expected_gold: str) -> None:
    for key in ("id", "dossier", "probes", "gold_class"):
        if key not in ep:
            raise ValueError(f"episode missing {key}")
    if str(ep["gold_class"]) != expected_gold:
        raise ValueError(f"episode {ep['id']} gold mismatch")
    if set(ep["probes"]) != PROBES:
        raise ValueError(f"episode {ep['id']} probe set mismatch")
    if any(str(value) not in ALLOWED_OBS for value in ep["probes"].values()):
        raise ValueError(f"episode {ep['id']} invalid probe observation")
    if len(str(ep["dossier"]).split()) > 90:
        raise ValueError(f"episode {ep['id']} dossier exceeds 90 words")


def validate_fixed_corpus(
    pairs: list[Mapping[str, object]], unresolved: list[Mapping[str, object]]
) -> dict[str, object]:
    errors: list[str] = []
    pair_sources = {str(row.get("source_id", "")) for row in pairs}
    unres_sources = {str(row.get("source_id", "")) for row in unresolved}
    if pair_sources != set(EXPECTED_PAIRS):
        errors.append("pair source set mismatch")
    if unres_sources != set(EXPECTED_UNRES):
        errors.append("unresolved source set mismatch")

    seen_sources: set[str] = set()
    seen_episodes: set[str] = set()
    classes: Counter[str] = Counter()
    domains: set[str] = set()

    for row in pairs:
        sid = str(row.get("source_id", ""))
        expected = EXPECTED_PAIRS.get(sid)
        if expected is None:
            continue
        if sid in seen_sources:
            errors.append(f"duplicate source {sid}")
        seen_sources.add(sid)
        if str(row.get("query_id")) != str(expected["query_id"]):
            errors.append(f"{sid} query mismatch")
        if str(row.get("adverse_class")) != str(expected["class"]):
            errors.append(f"{sid} class mismatch")
        if int(row.get("source_year", -1)) != PRIMARY_YEAR:
            errors.append(f"{sid} wrong year")
        cls = str(row.get("adverse_class", ""))
        classes[cls] += 1
        domains.add(str(row.get("actual_domain", "")))
        try:
            _validate_episode(row["adverse"], cls)
            _validate_episode(row["control"], CONTROL)
        except (KeyError, ValueError) as exc:
            errors.append(str(exc))
        for member in ("adverse", "control"):
            if member in row and isinstance(row[member], Mapping):
                eid = str(row[member].get("id", ""))
                if eid in seen_episodes:
                    errors.append(f"duplicate episode {eid}")
                seen_episodes.add(eid)

    for row in unresolved:
        sid = str(row.get("source_id", ""))
        expected = EXPECTED_UNRES.get(sid)
        if expected is None:
            continue
        if sid in seen_sources:
            errors.append(f"duplicate source {sid}")
        seen_sources.add(sid)
        if str(row.get("query_id")) != str(expected["query_id"]):
            errors.append(f"{sid} query mismatch")
        if int(row.get("source_year", -1)) != PRIMARY_YEAR:
            errors.append(f"{sid} wrong year")
        domains.add(str(row.get("actual_domain", "")))
        try:
            _validate_episode(row, UNRESOLVED)
        except ValueError as exc:
            errors.append(str(exc))
        eid = str(row.get("id", ""))
        if eid in seen_episodes:
            errors.append(f"duplicate episode {eid}")
        seen_episodes.add(eid)

    # Whether this is the frozen corpus at all, which is not the same question as
    # whether the frozen corpus is complete. A replication drawn from another year
    # shares no source ids with the freeze, so every row fell through the
    # ``EXPECTED_PAIRS.get(sid) is None`` continue above, nothing was scored, and
    # the result was reported as a frozen-corpus CANNOT_CHECK -- an undetermined
    # measurement. It is not undetermined: the evaluator was handed a different
    # object and can say so. ``DISJOINT`` is a determinate refusal.
    presented = pair_sources | unres_sources
    expected = set(EXPECTED_PAIRS) | set(EXPECTED_UNRES)
    if presented == expected:
        source_set = "FROZEN"
    elif presented and not (presented & expected):
        source_set = "DISJOINT"
    else:
        source_set = "PARTIAL"

    min_per_class = int(FIXED["minimum_pair_sources_per_substantive_class"])
    checks = {
        "exact_pair_sources": pair_sources == set(EXPECTED_PAIRS),
        "exact_unresolved_sources": unres_sources == set(EXPECTED_UNRES),
        "pair_count": len(pairs) == int(FIXED["expected_pair_source_count"]),
        "unresolved_count": len(unresolved) == int(FIXED["expected_unresolved_source_count"]),
        "episode_count": len(seen_episodes) == int(FIXED["expected_episode_count"]),
        "minimum_pairs_per_class": all(classes.get(cls, 0) >= min_per_class for cls in sorted(SUBSTANTIVE)),
        "minimum_domains": len(domains) >= int(FIXED["minimum_actual_domains"]),
        "no_errors": not errors,
    }
    return {
        "complete": all(checks.values()),
        "checks": checks,
        "errors": errors,
        "class_counts": dict(sorted(classes.items())),
        "n_domains": len(domains),
        "source_set": source_set,
        "primary_year": PRIMARY_YEAR,
    }


def _b3(ep: Mapping[str, object]) -> dict[str, object]:
    gate = B3ProbeGate(ep["probes"])
    visible = {"dossier": str(ep["dossier"]), "probes": gate}
    result = B3_POLICY.donor_complete_policy(visible, horizon=2)
    trace_pairs = [(str(item["probe"]), str(item["observation"])) for item in result["trace"]]
    if gate.revealed != trace_pairs:
        raise AssertionError(f"B3 hidden-probe mismatch on {ep['id']}")
    if int(result["cost"]) != len(gate.revealed):
        raise AssertionError(f"B3 cost mismatch on {ep['id']}")
    if len(gate.revealed) > int(PROTOCOL["budget"]):
        raise AssertionError(f"B3 exceeded native-comparison budget on {ep['id']}")
    return {
        "choice": str(result["choice"]),
        "probe_accesses": [probe for probe, _ in gate.revealed],
        "cost": len(gate.revealed),
    }


def _verify_native_lineage(result: Mapping[str, object]) -> None:
    if result.get("grants_adoption_authority") is not False:
        raise AssertionError("native result unexpectedly grants adoption authority")
    if result.get("grants_promotion_authority") is not False:
        raise AssertionError("native result unexpectedly grants promotion authority")
    if result.get("grants_merge_authority") is not False:
        raise AssertionError("native result unexpectedly grants merge authority")
    root = result.get("root")
    if not isinstance(root, Mapping):
        raise AssertionError("native result missing root runtime lineage")
    required_root = set(PROTOCOL["root_runtime"]["required_operator_ids"])
    if not required_root <= set(map(str, root.get("operator_ids", []))):
        raise AssertionError("native root runtime lineage incomplete")
    required_probe = set(PROTOCOL["probe_runtime"]["required_operator_ids"])
    executions = result.get("probe_executions", [])
    if not isinstance(executions, list):
        raise AssertionError("native probe lineage malformed")
    for execution in executions:
        if not isinstance(execution, Mapping):
            raise AssertionError("native probe execution malformed")
        if not required_probe <= set(map(str, execution.get("operator_ids", []))):
            raise AssertionError("native child runtime lineage incomplete")
        if not str(execution.get("evidence_id", "")).startswith("evidence:p1-r6:"):
            raise AssertionError("native child runtime evidence identity missing")
    accesses = list(map(str, result.get("probe_accesses", [])))
    if len(accesses) > int(PROTOCOL["budget"]):
        raise AssertionError("native ARD exceeded probe budget")
    if accesses != [str(item.get("probe_id")) for item in executions]:
        raise AssertionError("native access/execution lineage mismatch")
    payload = {key: value for key, value in result.items() if key != "digest"}
    from orion.transfer.v2.canonical import content_digest

    if content_digest(payload) != str(result.get("digest", "")):
        raise AssertionError("native decision digest mismatch")


def _score(choice: str, gold: str) -> dict[str, int]:
    return {
        "grs": int(choice == gold),
        "false_high_level": int(choice in HIGH and gold not in HIGH),
        "harmful_lower_level_skip": int(choice in HIGH and gold in LOW),
        "false_resolution_of_unresolved": int(gold == UNRESOLVED and choice != UNRESOLVED),
    }


class LeakageVerdict:
    """Three-valued leakage verdict that refuses a two-valued reading.

    P1-U-T3 repair 3.  The predecessor guard returned a plain ``bool`` and
    treated a missing ``request_payloads`` key as "no leakage", i.e. it reported
    *ran* as *worked*.  Absence is now its own value.

    ``__bool__`` raises on purpose.  A ``None`` sentinel would let a two-valued
    caller write ``int(not verdict)`` or ``if verdict:`` and silently score a
    ``CANNOT_CHECK`` as clean; here that caller raises ``TypeError`` instead.
    Callers must branch on ``.status``.
    """

    PASS = "PASS"
    FAIL = "FAIL"
    CANNOT_CHECK = "CANNOT_CHECK"
    _STATUSES = (PASS, FAIL, CANNOT_CHECK)

    __slots__ = ("status", "reason", "hits", "records", "payload_bytes", "payload_digest")

    def __init__(
        self,
        status: str,
        *,
        reason: str = "",
        hits: Sequence[Mapping[str, str]] = (),
        records: int = 0,
        payload_bytes: int = 0,
        payload_digest: str = "",
    ) -> None:
        if status not in self._STATUSES:
            raise ValueError(f"unknown leakage status {status!r}")
        self.status = status
        self.reason = reason
        self.hits = [dict(hit) for hit in hits]
        self.records = int(records)
        self.payload_bytes = int(payload_bytes)
        self.payload_digest = str(payload_digest)

    def __bool__(self) -> bool:
        raise TypeError(
            "LeakageVerdict is three-valued; branch on .status "
            "(PASS / FAIL / CANNOT_CHECK) rather than on truthiness"
        )

    def __repr__(self) -> str:
        return f"LeakageVerdict({self.status!r}, hits={len(self.hits)})"

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "reason": self.reason,
            "hits": self.hits,
            "provider_call_records": self.records,
            "payload_bytes": self.payload_bytes,
            "payload_digest": self.payload_digest,
        }


def forbidden_tokens(
    *,
    episode_id: str,
    gold_class: str,
    pair_id: str | None = None,
    query_id: str | None = None,
    source_id: str | None = None,
    adverse_class: str | None = None,
) -> dict[str, str]:
    """Token -> category map for one episode's candidate-visible payloads.

    The episode id carries two categories at once because the frozen id format
    ends in the pair-role suffix, so leaking the id leaks the role.
    """
    tokens: dict[str, str] = {}
    episode_id = str(episode_id)
    role = next(
        (role for suffix, role in ROLE_SUFFIX_TO_ROLE.items() if episode_id.endswith(suffix)),
        None,
    )
    tokens[episode_id] = "episode_id_and_pair_role" if role else "episode_id"
    for value, category in (
        (pair_id, "pair_id"),
        (query_id, "query_id"),
        (source_id, "source_id"),
        (adverse_class, "adverse_class_label"),
        (gold_class, "gold_class_label"),
    ):
        if value:
            tokens.setdefault(str(value), category)
    for label in sorted(ALL_GOLD_CLASSES):
        tokens.setdefault(label, "p1_class_label")
    tokens.setdefault("pair_role", "pair_role")
    tokens.setdefault("gold_class", "gold_class_key")
    return tokens


def leakage_audit(
    payloads: object,
    forbidden: Mapping[str, str],
) -> LeakageVerdict:
    """Fail-closed, three-valued audit of one episode/arm's provider payloads.

    An absent, non-sequence or empty payload record is ``CANNOT_CHECK``: there
    is nothing to have audited, and saying "clean" about it is the defect this
    repair exists to remove.
    """
    if payloads is None:
        return LeakageVerdict(
            LeakageVerdict.CANNOT_CHECK, reason="no provider payload record was captured"
        )
    if not isinstance(payloads, (list, tuple)):
        return LeakageVerdict(
            LeakageVerdict.CANNOT_CHECK,
            reason=f"payload record is {type(payloads).__name__}, not a sequence",
        )
    if len(payloads) == 0:
        return LeakageVerdict(
            LeakageVerdict.CANNOT_CHECK,
            reason="payload record is empty; the provider boundary was never observed",
        )
    serialized = json.dumps(payloads, sort_keys=True, default=str)
    digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    hits: list[dict[str, str]] = []
    for token, category in sorted(forbidden.items()):
        if token and token in serialized:
            hits.append({"token": token, "category": category})
    for match in ROLE_ASSIGNMENT.finditer(serialized):
        hits.append({"token": match.group(0), "category": "pair_role"})
    status = LeakageVerdict.FAIL if hits else LeakageVerdict.PASS
    return LeakageVerdict(
        status,
        reason="forbidden token present in candidate-visible payload" if hits else "",
        hits=hits,
        records=len(payloads),
        payload_bytes=len(serialized),
        payload_digest=digest,
    )


@contextmanager
def record_provider_payloads() -> Iterator[list[dict[str, str]]]:
    """Record every request presented at the candidate's provider boundary.

    The wrapper appends and delegates; it changes no decision, no digest and no
    scored field.  It exists so the leakage guard audits what was actually sent
    rather than an artifact that may or may not have been populated.
    """
    core = NATIVE._CORE
    host = core.FrozenNativeProviderHost
    original = host.__call__
    sink: list[dict[str, str]] = []

    def recording(self, request):  # noqa: ANN001, ANN202 - frozen provider signature
        sink.append({"task": str(request.task), "user": str(request.user)})
        return original(self, request)

    host.__call__ = recording
    try:
        yield sink
    finally:
        host.__call__ = original


def _responsibility_level(gold_class: str) -> str:
    """Coarsest partition already frozen in this module.

    Used only as the reported sensitivity for the domain-margin restatement.
    It invents no grouping: HIGH and LOW are module constants and the control /
    unresolved classes come from NATIVE_PROTOCOL_V1.json.
    """
    if gold_class in HIGH:
        return "HIGH_LEVEL_ADVERSE"
    if gold_class in LOW:
        return "LOWER_LEVEL_ADVERSE"
    if gold_class == CONTROL:
        return "CONTROL"
    return "UNRESOLVED"


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _bootstrap(values: list[float], *, reps: int, seed: int, interval: float) -> tuple[float, float]:
    if not values:
        return (0.0, 0.0)
    rng = random.Random(seed)
    n = len(values)
    stats = [sum(values[rng.randrange(n)] for _ in range(n)) / n for _ in range(reps)]
    stats.sort()
    alpha = 1.0 - interval
    return (
        stats[max(0, int((alpha / 2) * reps))],
        stats[min(reps - 1, int((1 - alpha / 2) * reps) - 1)],
    )


def _stratified_macro_bootstrap(
    by_class: Mapping[str, list[float]], *, reps: int, seed: int, interval: float
) -> tuple[float, float]:
    rng = random.Random(seed)
    classes = sorted(by_class)
    stats: list[float] = []
    for _ in range(reps):
        means = []
        for cls in classes:
            xs = by_class[cls]
            means.append(sum(xs[rng.randrange(len(xs))] for _ in range(len(xs))) / len(xs))
        stats.append(sum(means) / len(means))
    stats.sort()
    alpha = 1.0 - interval
    return (
        stats[max(0, int((alpha / 2) * reps))],
        stats[min(reps - 1, int((1 - alpha / 2) * reps) - 1)],
    )


def evaluate(
    pairs: list[Mapping[str, object]],
    unresolved: list[Mapping[str, object]],
    *,
    payload_sink: dict[str, list[dict[str, str]]] | None = None,
) -> dict[str, object]:
    """Score the frozen primary.

    ``payload_sink``, when given, receives the raw candidate-visible provider
    payloads keyed ``"<episode_id>::<arm>"``.  The predecessor guard kept only a
    digest, so a leakage finding could never be re-audited from the artifact
    with a corrected token set; writing the payloads out makes that possible.
    """
    data = validate_fixed_corpus(pairs, unresolved)
    if not data["complete"]:
        return {
            "schema": "P1U.NativeOrionResult.v1",
            "data": data,
            "policy_outcomes_generated": False,
            "terminal": (
                "P1_R6_REFUSED_NOT_THE_FROZEN_SOURCE_SET"
                if data["source_set"] == "DISJOINT"
                else "P1_R6_CANNOT_CHECK_FIXED_CORPUS"
            ),
        }

    rows: list[dict[str, object]] = []
    episode_diffs: list[float] = []
    domain_diffs: dict[str, list[float]] = defaultdict(list)
    pair_diffs: list[float] = []
    pair_by_class: dict[str, list[float]] = defaultdict(list)
    # P1-U-T3 repair 1: every scored episode also accumulates under its OWN gold
    # class, so the NO_HIGH_LEVEL_REFORMULATION control stratum exists.
    episode_by_gold_class: dict[str, list[float]] = defaultdict(list)
    # P1-U-T3 repair 2, sensitivity only: the coarsest partition already frozen
    # in this module (HIGH / LOW / control / unresolved).
    episode_by_level: dict[str, list[float]] = defaultdict(list)
    # P1-U-T3 repair 3.
    leakage_verdicts: list[dict[str, object]] = []
    captured_payloads: dict[str, list[dict[str, str]]] = {}
    native_false_high = b3_false_high = 0
    native_lower_skips = native_false_unresolved = control_harm = 0
    native_base_differences = 0

    for pair in pairs:
        member_results: dict[str, object] = {}
        pair_native_correct = True
        pair_b3_correct = True
        for member in ("adverse", "control"):
            ep = pair[member]
            evidence_note = str(pair["pair_evidence"]["source_claim"])
            with record_provider_payloads() as ard_payloads:
                native = NATIVE.run_native_ard(ep, evidence_note=evidence_note)
            with record_provider_payloads() as base_payloads:
                base = NATIVE.run_native_base(ep)
            b3 = _b3(ep)
            tokens = forbidden_tokens(
                episode_id=str(ep["id"]),
                gold_class=str(ep["gold_class"]),
                pair_id=str(pair["pair_id"]),
                query_id=str(pair["query_id"]),
                source_id=str(pair["source_id"]),
                adverse_class=str(pair["adverse_class"]),
            )
            for arm, payloads in (
                ("ORION_NATIVE_ARD", list(ard_payloads)),
                ("ORION_NATIVE_BASE", list(base_payloads)),
            ):
                verdict = leakage_audit(payloads, tokens)
                leakage_verdicts.append(
                    {
                        "episode_id": str(ep["id"]),
                        "pair_role": member,
                        "arm": arm,
                        **verdict.as_dict(),
                    }
                )
                captured_payloads[f"{ep['id']}::{arm}"] = payloads
            _verify_native_lineage(native)
            _verify_native_lineage(base)
            gold = str(ep["gold_class"])
            native_score = _score(str(native["choice"]), gold)
            base_score = _score(str(base["choice"]), gold)
            b3_score = _score(str(b3["choice"]), gold)
            if str(native["choice"]) != str(base["choice"]):
                native_base_differences += 1
            pair_native_correct = pair_native_correct and bool(native_score["grs"])
            pair_b3_correct = pair_b3_correct and bool(b3_score["grs"])
            diff = native_score["grs"] - b3_score["grs"]
            episode_diffs.append(diff)
            domain_diffs[str(pair["actual_domain"])].append(diff)
            episode_by_gold_class[gold].append(diff)
            episode_by_level[_responsibility_level(gold)].append(diff)
            native_false_high += native_score["false_high_level"]
            b3_false_high += b3_score["false_high_level"]
            native_lower_skips += native_score["harmful_lower_level_skip"]
            if member == "control":
                control_harm += native_score["false_high_level"]
            member_results[member] = {
                "gold_class": gold,
                "native_ard": {"result": native, "score": native_score},
                "native_base": {"result": base, "score": base_score},
                "b3": {"result": b3, "score": b3_score},
            }
        pair_diff = int(pair_native_correct) - int(pair_b3_correct)
        pair_diffs.append(pair_diff)
        pair_by_class[str(pair["adverse_class"])].append(pair_diff)
        rows.append(
            {
                "pair_id": pair["pair_id"],
                "source_id": pair["source_id"],
                "adverse_class": pair["adverse_class"],
                "actual_domain": pair["actual_domain"],
                "pair_selective_native": int(pair_native_correct),
                "pair_selective_b3": int(pair_b3_correct),
                "members": member_results,
            }
        )

    unresolved_rows: list[dict[str, object]] = []
    for ep in unresolved:
        evidence_note = str(ep["admission_evidence"]["source_claim"])
        with record_provider_payloads() as ard_payloads:
            native = NATIVE.run_native_ard(ep, evidence_note=evidence_note)
        with record_provider_payloads() as base_payloads:
            base = NATIVE.run_native_base(ep)
        b3 = _b3(ep)
        tokens = forbidden_tokens(
            episode_id=str(ep["id"]),
            gold_class=UNRESOLVED,
            query_id=str(ep["query_id"]),
            source_id=str(ep["source_id"]),
        )
        for arm, payloads in (
            ("ORION_NATIVE_ARD", list(ard_payloads)),
            ("ORION_NATIVE_BASE", list(base_payloads)),
        ):
            verdict = leakage_audit(payloads, tokens)
            leakage_verdicts.append(
                {
                    "episode_id": str(ep["id"]),
                    "pair_role": "unresolved",
                    "arm": arm,
                    **verdict.as_dict(),
                }
            )
            captured_payloads[f"{ep['id']}::{arm}"] = payloads
        _verify_native_lineage(native)
        _verify_native_lineage(base)
        gold = UNRESOLVED
        native_score = _score(str(native["choice"]), gold)
        base_score = _score(str(base["choice"]), gold)
        b3_score = _score(str(b3["choice"]), gold)
        if str(native["choice"]) != str(base["choice"]):
            native_base_differences += 1
        diff = native_score["grs"] - b3_score["grs"]
        episode_diffs.append(diff)
        domain_diffs[str(ep["actual_domain"])].append(diff)
        episode_by_gold_class[gold].append(diff)
        episode_by_level[_responsibility_level(gold)].append(diff)
        native_false_high += native_score["false_high_level"]
        b3_false_high += b3_score["false_high_level"]
        native_false_unresolved += native_score["false_resolution_of_unresolved"]
        unresolved_rows.append(
            {
                "id": ep["id"],
                "source_id": ep["source_id"],
                "native_ard": {"result": native, "score": native_score},
                "native_base": {"result": base, "score": base_score},
                "b3": {"result": b3, "score": b3_score},
            }
        )

    cfg = PROTOCOL["decision_rule"]
    reps = int(cfg["bootstrap_replicates"])
    seed = int(cfg["bootstrap_seed"])
    interval = float(cfg["stability_interval"])
    episode_diff = _mean(episode_diffs)
    ep_lo, ep_hi = _bootstrap(episode_diffs, reps=reps, seed=seed, interval=interval)
    pair_micro = _mean(pair_diffs)
    pair_lo, pair_hi = _bootstrap(pair_diffs, reps=reps, seed=seed + 1, interval=interval)
    class_means = {cls: _mean(values) for cls, values in sorted(pair_by_class.items())}
    pair_macro = _mean(list(class_means.values()))
    macro_lo, macro_hi = _stratified_macro_bootstrap(
        pair_by_class, reps=reps, seed=seed + 2, interval=interval
    )
    domain_means = {domain: _mean(values) for domain, values in sorted(domain_diffs.items())}
    n_episodes = len(episode_diffs)
    native_false_high_rate = native_false_high / n_episodes
    b3_false_high_rate = b3_false_high / n_episodes
    nonnegative_classes = sum(value >= 0 for value in class_means.values())

    floor = float(cfg["domain_or_class_noninferiority_floor"])

    # ---- P1-U-T3 repair 1: member-level class strata, filed under own gold ----
    member_class_means = {
        cls: _mean(values) for cls, values in sorted(episode_by_gold_class.items())
    }
    member_class_counts = {
        cls: len(values) for cls, values in sorted(episode_by_gold_class.items())
    }
    class_noninferiority_pair_level = all(value >= floor for value in class_means.values())
    class_noninferiority_member_level = all(
        value >= floor for value in member_class_means.values()
    )

    # ---- P1-U-T3 repair 2: the domain margin, restated -----------------------
    # For per-episode diffs in {-1, 0, +1}, a stratum of size n that loses one
    # net episode has mean -1/n.  Clearing `floor` therefore needs n >= 1/|floor|.
    domain_counts = {
        domain: len(values) for domain, values in sorted(domain_diffs.items())
    }
    # Smallest stratum size at which one net lost episode still clears `floor`.
    # Searched rather than divided so the comparison is float-identical to the
    # one the guard itself performs.
    min_n_for_a_real_margin = next(
        (n for n in range(1, n_episodes + 1) if -1.0 / n >= floor), 0
    )
    domain_margin_is_a_margin = bool(min_n_for_a_real_margin) and any(
        n >= min_n_for_a_real_margin for n in domain_counts.values()
    )
    domain_frozen_floor_predicate = all(value >= floor for value in domain_means.values())
    domain_zero_loss_predicate = all(value >= 0.0 for value in domain_means.values())
    domain_restatement_is_verdict_identical = (
        domain_frozen_floor_predicate == domain_zero_loss_predicate
    )
    if not domain_restatement_is_verdict_identical:
        raise AssertionError(
            "domain margin restatement changed the verdict; the -0.10 floor and the "
            "zero-loss rule are not equivalent on this corpus and the repair is wrong"
        )
    level_means = {
        level: _mean(values) for level, values in sorted(episode_by_level.items())
    }
    level_counts = {
        level: len(values) for level, values in sorted(episode_by_level.items())
    }

    # ---- P1-U-T3 repair 3: three-valued leakage roll-up ----------------------
    leakage_status_counts = Counter(str(row["status"]) for row in leakage_verdicts)
    if leakage_status_counts.get(LeakageVerdict.CANNOT_CHECK, 0):
        leakage_status = LeakageVerdict.CANNOT_CHECK
    elif leakage_status_counts.get(LeakageVerdict.FAIL, 0):
        leakage_status = LeakageVerdict.FAIL
    elif leakage_verdicts:
        leakage_status = LeakageVerdict.PASS
    else:
        leakage_status = LeakageVerdict.CANNOT_CHECK
    leakage_hit_categories = Counter(
        str(hit["category"]) for row in leakage_verdicts for hit in row["hits"]
    )
    if payload_sink is not None:
        payload_sink.update(captured_payloads)

    checks = {
        "episode_margin": episode_diff >= float(cfg["episode_grs_margin"]),
        "episode_stability_lower_positive": ep_lo > 0,
        "pair_micro_margin": pair_micro >= float(cfg["pair_selective_margin"]),
        "pair_micro_stability_lower_positive": pair_lo > 0,
        "pair_macro_margin": pair_macro >= float(cfg["class_macro_pair_margin"]),
        "pair_macro_stability_lower_positive": macro_lo > 0,
        # P1-U-T3 repair 2.  Renamed to the rule it arithmetically is on this
        # corpus.  `domain_restatement_is_verdict_identical` above asserts that
        # the frozen -0.10 floor and this predicate cannot disagree here.
        "domain_zero_loss": domain_zero_loss_predicate,
        # P1-U-T3 repair 1.  Conjunction: the pre-existing pair-level component
        # is retained bit-for-bit, so this can only ever be stricter.
        "class_noninferiority": class_noninferiority_pair_level
        and class_noninferiority_member_level,
        "at_least_three_nonnegative_classes": nonnegative_classes >= 3,
        # P1-U-T3 repair 3.  CANNOT_CHECK is not PASS.
        "no_candidate_metadata_leakage": leakage_status == LeakageVerdict.PASS,
        "false_high_level_guard": native_false_high_rate <= b3_false_high_rate
        and native_false_high_rate <= float(cfg["max_false_high_level_rate"]),
        "zero_lower_level_skip": native_lower_skips
        <= int(cfg["harmful_lower_level_skip_tolerance"]),
        "zero_control_high_level_harm": control_harm == 0,
        "zero_false_unresolved_resolution": native_false_unresolved
        <= int(cfg["false_resolution_of_unresolved_tolerance"]),
        "native_ard_materially_differs_from_base": native_base_differences > 0,
    }
    terminal = (
        "P1_R6_NATIVE_PRIMARY_PASS_PENDING_2019_REPLICATION"
        if all(checks.values())
        else "P1_R6_NATIVE_PRIMARY_NOT_SUPPORTED"
    )
    return {
        "schema": "P1U.NativeOrionResult.v1",
        "data": data,
        "policy_outcomes_generated": True,
        "episode_orion_native_ard_minus_b3_grs": episode_diff,
        "episode_bootstrap_95_stability": [ep_lo, ep_hi],
        "pair_micro_orion_native_ard_minus_b3": pair_micro,
        "pair_micro_bootstrap_95_stability": [pair_lo, pair_hi],
        "pair_macro_equal_class_orion_native_ard_minus_b3": pair_macro,
        "pair_macro_bootstrap_95_stability": [macro_lo, macro_hi],
        "class_pair_differences": class_means,
        "class_episode_differences_by_gold_class": member_class_means,
        "class_episode_counts_by_gold_class": member_class_counts,
        "domain_episode_differences": domain_means,
        "domain_episode_counts": domain_counts,
        "guard_verdicts": {
            "class_noninferiority": {
                "pair_level_by_adverse_class": class_noninferiority_pair_level,
                "member_level_by_own_gold_class": class_noninferiority_member_level,
                "control_stratum_evaluated": CONTROL in member_class_means,
                "n_strata_pair_level": len(class_means),
                "n_strata_member_level": len(member_class_means),
                "floor": floor,
            },
            "domain_margin": {
                "governing_rule": "no actual_domain stratum may have a negative "
                "ARD-minus-B3 episode mean",
                "governing_verdict": domain_zero_loss_predicate,
                "frozen_floor": floor,
                "frozen_floor_verdict": domain_frozen_floor_predicate,
                "restatement_is_verdict_identical": domain_restatement_is_verdict_identical,
                "n_strata": len(domain_counts),
                # string keys so the in-memory dict and the JSON artifact agree
                "stratum_size_histogram": {
                    str(size): n for size, n in sorted(Counter(domain_counts.values()).items())
                },
                "min_stratum_size_for_the_floor_to_admit_one_lost_episode": (
                    min_n_for_a_real_margin
                ),
                "any_stratum_large_enough": domain_margin_is_a_margin,
                "sensitivity_widened_stratifier": {
                    "partition": "frozen HIGH / LOW / control_class / unresolved_class",
                    "means": level_means,
                    "counts": level_counts,
                    "one_lost_episode_threshold_per_stratum": {
                        level: -1.0 / n for level, n in level_counts.items()
                    },
                    "strata_where_floor_admits_one_lost_episode": [
                        level
                        for level, n in sorted(level_counts.items())
                        if -1.0 / n >= floor
                    ],
                    "verdict_at_frozen_floor": all(
                        value >= floor for value in level_means.values()
                    ),
                    "verdict_at_zero_loss": all(
                        value >= 0.0 for value in level_means.values()
                    ),
                },
            },
            "candidate_metadata_leakage": {
                "status": leakage_status,
                "status_counts": dict(sorted(leakage_status_counts.items())),
                "hit_categories": dict(sorted(leakage_hit_categories.items())),
                "n_audited_episode_arms": len(leakage_verdicts),
                "rows": leakage_verdicts,
            },
        },
        "native_false_high_level_rate": native_false_high_rate,
        "b3_false_high_level_rate": b3_false_high_rate,
        "native_base_choice_differences": native_base_differences,
        "checks": checks,
        "terminal": terminal,
        "pair_rows": rows,
        "unresolved_rows": unresolved_rows,
    }


def main(argv: Sequence[str]) -> int:
    import argparse

    parser = argparse.ArgumentParser(prog="evaluate_native.py")
    parser.add_argument("--out", type=Path)
    parser.add_argument(
        "--payloads-out",
        type=Path,
        help=(
            "write the raw candidate-visible provider payloads so a leakage "
            "finding can be re-audited later with a corrected token set"
        ),
    )
    args = parser.parse_args(list(argv))
    pairs, unresolved = fixed_corpus()
    payload_sink: dict[str, list[dict[str, str]]] = {}
    result = evaluate(pairs, unresolved, payload_sink=payload_sink)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text)
    if args.payloads_out:
        args.payloads_out.write_text(
            json.dumps(payload_sink, indent=2, sort_keys=True) + "\n"
        )
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
