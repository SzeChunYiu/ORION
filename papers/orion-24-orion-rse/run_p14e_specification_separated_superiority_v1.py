"""Execute the frozen P14E specification-separated governance superiority benchmark.

Gold is assigned by interpreting the frozen rule table P14E_ADJUDICATION_RULES_V1.json
with a generic condition evaluator. Policy arms are independently written functions
that receive facts only. Two fresh-subprocess replay must be byte-identical.
"""

from __future__ import annotations

import argparse
import json
import platform
import random
import subprocess
import sys
import tempfile
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
RULES = HERE / "P14E_ADJUDICATION_RULES_V1.json"
PROTOCOL = HERE / "P14E_SPECIFICATION_SEPARATED_SUPERIORITY_PROTOCOL_V1.md"
OUT = HERE / "P14E_SUPERIORITY_RESULT_V1.json"

SEED = 2026082401
N_FAMILIES = 12
CASES_PER_STRATUM = 80
BUDGET_CHECKS = 7
FREE_RATE_LO = 0.25
FREE_RATE_HI = 0.75

STRATA = (
    "SUPPORTED_CLEAN",
    "SUPPORTED_REOPEN",
    "RETAIN_NEGATIVE",
    "SUBSUMED",
    "INTERACTION_ONLY",
    "CANNOT_CHECK",
    "NEGATIVE",
)
SCREENING = ("evidence_integrity", "frozen_protocol", "identifiable")
FACTS = (
    "positive",
    "evidence_integrity",
    "frozen_protocol",
    "identifiable",
    "donor_owned",
    "interaction_only",
    "live_negative_history",
    "material_new_evidence",
)
PRIVATE_KEYS = {"gold_disposition", "stratum", "case_id", "rationale"}
SUPPORTED = "P14E_SPECIFICATION_SEPARATED_SUPERIORITY_SUPPORTED"
NOT_SUPPORTED = "P14E_SPECIFICATION_SEPARATED_SUPERIORITY_GATE_NOT_MET"

# Nonempty failing subsets of the three screening checks, frozen enumeration order.
FAILING_SUBSETS = [
    (False, True, True),
    (True, False, True),
    (True, True, False),
    (False, False, True),
    (False, True, False),
    (True, False, False),
    (False, False, False),
]

# Stratum -> registered gold disposition.
STRATUM_GOLD = {
    "SUPPORTED_CLEAN": "SUPPORTED_RESIDUAL",
    "SUPPORTED_REOPEN": "SUPPORTED_RESIDUAL",
    "RETAIN_NEGATIVE": "RETAIN_NEGATIVE",
    "SUBSUMED": "SUBSUMED",
    "INTERACTION_ONLY": "INTERACTION_ONLY",
    "CANNOT_CHECK": "CANNOT_CHECK",
    "NEGATIVE": "NEGATIVE",
}

# Stratum -> pinned facts (fully determined coordinates, rule-table semantics).
PINNED: dict[str, dict[str, bool]] = {
    "SUPPORTED_CLEAN": {
        "positive": True, "evidence_integrity": True, "frozen_protocol": True,
        "identifiable": True, "donor_owned": False, "interaction_only": False,
        "live_negative_history": False,
    },
    "SUPPORTED_REOPEN": {
        "positive": True, "evidence_integrity": True, "frozen_protocol": True,
        "identifiable": True, "donor_owned": False, "interaction_only": False,
        "live_negative_history": True, "material_new_evidence": True,
    },
    "RETAIN_NEGATIVE": {
        "positive": True, "evidence_integrity": True, "frozen_protocol": True,
        "identifiable": True, "donor_owned": False, "interaction_only": False,
        "live_negative_history": True, "material_new_evidence": False,
    },
    "SUBSUMED": {
        "positive": True, "evidence_integrity": True, "frozen_protocol": True,
        "identifiable": True, "donor_owned": True,
    },
    "INTERACTION_ONLY": {
        "positive": True, "evidence_integrity": True, "frozen_protocol": True,
        "identifiable": True, "donor_owned": False, "interaction_only": True,
    },
    "NEGATIVE": {
        "positive": False, "evidence_integrity": True, "frozen_protocol": True,
        "identifiable": True,
    },
    "CANNOT_CHECK": {},  # failing screening subset reminted per case
}


def canonical_text(obj) -> str:
    return json.dumps(obj, indent=2, sort_keys=True) + "\n"


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


# --------------------------------------------------------------------------
# Adjudication: generic interpreter over the frozen rule table. No policy arm
# may call these functions.
# --------------------------------------------------------------------------

def tokenize(condition: str) -> list[str]:
    tokens: list[str] = []
    i = 0
    while i < len(condition):
        ch = condition[i]
        if ch.isspace():
            i += 1
            continue
        if ch in "()":
            tokens.append(ch)
            i += 1
            continue
        j = i
        while j < len(condition) and (condition[j].isalpha() or condition[j] == "_"):
            j += 1
        if j == i:
            raise AssertionError(f"unparsed condition text: {condition!r} at {i}")
        tokens.append(condition[i:j])
        i = j
    return tokens


def parse_condition(condition: str):
    """Parse the restricted grammar: or-expr := and-expr ('or' and-expr)*;
    and-expr := not-expr ('and' not-expr)*; not-expr := 'not' not-expr
    | '(' or-expr ')' | 'true' | fact-name. Returns a nested tuple AST."""
    tokens = tokenize(condition)
    pos = 0

    def parse_or():
        nonlocal pos
        node = parse_and()
        while pos < len(tokens) and tokens[pos] == "or":
            pos += 1
            node = ("or", node, parse_and())
        return node

    def parse_and():
        nonlocal pos
        node = parse_not()
        while pos < len(tokens) and tokens[pos] == "and":
            pos += 1
            node = ("and", node, parse_not())
        return node

    def parse_not():
        nonlocal pos
        tok = tokens[pos]
        if tok == "not":
            pos += 1
            return ("not", parse_not())
        if tok == "(":
            pos += 1
            node = parse_or()
            assert tokens[pos] == ")", condition
            pos += 1
            return node
        pos += 1
        if tok == "true":
            return ("const", True)
        return ("fact", tok)

    ast = parse_or()
    assert pos == len(tokens), condition
    return ast


def eval_ast(ast, facts: dict[str, bool]) -> bool:
    kind = ast[0]
    if kind == "const":
        return ast[1]
    if kind == "fact":
        return facts[ast[1]]
    if kind == "not":
        return not eval_ast(ast[1], facts)
    if kind == "or":
        return eval_ast(ast[1], facts) or eval_ast(ast[2], facts)
    if kind == "and":
        return eval_ast(ast[1], facts) and eval_ast(ast[2], facts)
    raise AssertionError(kind)


class Adjudicator:
    """Interprets the frozen rule table. Registered as the only gold source."""

    def __init__(self, table: dict):
        self.table = table
        self.rules = [
            {
                "order": rule["order"],
                "disposition": rule["disposition"],
                "condition": rule["condition"],
                "ast": parse_condition(rule["condition"]),
            }
            for rule in sorted(table["rules"], key=lambda r: r["order"])
        ]

    def adjudicate(self, facts: dict[str, bool]) -> str:
        for rule in self.rules:
            if eval_ast(rule["ast"], facts):
                return rule["disposition"]
        raise AssertionError("rule table has no terminal rule")


# --------------------------------------------------------------------------
# Policies: independently written, facts only.
# --------------------------------------------------------------------------

def facts_only(case: dict) -> dict[str, bool]:
    payload = {k: v for k, v in case.items() if k not in PRIVATE_KEYS}
    if "gold_disposition" in payload:
        raise AssertionError("gold leaked into policy input")
    return {k: bool(v) for k, v in payload.items()}


def full_policy(c: dict[str, bool]) -> str:
    """ORION_RSE_FULL, written from the protocol prose (not the rule table).

    Contract: screen admissibility first; a null observation is negative; a
    positive is donor-subsumed, interaction-only, or blocked by live negative
    history unless the new evidence is material; only the surviving residual is
    promotable."""
    if not c["evidence_integrity"] or not c["frozen_protocol"] or not c["identifiable"]:
        return "CANNOT_CHECK"
    if not c["positive"]:
        return "NEGATIVE"
    if c["donor_owned"]:
        return "SUBSUMED"
    if c["interaction_only"]:
        return "INTERACTION_ONLY"
    if c["live_negative_history"] and not c["material_new_evidence"]:
        return "RETAIN_NEGATIVE"
    return "SUPPORTED_RESIDUAL"


def raw_positive(c: dict[str, bool]) -> str:
    return "SUPPORTED_RESIDUAL" if c["positive"] else "NEGATIVE"


def reflection_checklist(c: dict[str, bool]) -> str:
    if not c["evidence_integrity"] or not c["frozen_protocol"] or not c["identifiable"]:
        return "CANNOT_CHECK"
    return "SUPPORTED_RESIDUAL" if c["positive"] else "NEGATIVE"


def donor_aware_review(c: dict[str, bool]) -> str:
    verdict = reflection_checklist(c)
    if verdict == "SUPPORTED_RESIDUAL" and c["donor_owned"]:
        return "SUBSUMED"
    return verdict


def multi_review(c: dict[str, bool]) -> str:
    verdict = donor_aware_review(c)
    if verdict == "SUPPORTED_RESIDUAL" and c["interaction_only"]:
        return "INTERACTION_ONLY"
    return verdict


def ablated(field: str):
    def policy(c: dict[str, bool]) -> str:
        d = dict(c)
        if field in SCREENING:
            d[field] = True
        elif field in ("donor_owned", "interaction_only", "live_negative_history"):
            d[field] = False
        else:
            raise AssertionError(field)
        return full_policy(d)

    return policy


ARMS: dict[str, object] = {
    "RAW_POSITIVE": raw_positive,
    "REFLECTION_CHECKLIST": reflection_checklist,
    "DONOR_AWARE_REVIEW": donor_aware_review,
    "MULTI_REVIEW": multi_review,
    "ORION_RSE_FULL": full_policy,
    "ABLATE_EVIDENCE_INTEGRITY": ablated("evidence_integrity"),
    "ABLATE_FREEZE": ablated("frozen_protocol"),
    "ABLATE_IDENTIFIABILITY": ablated("identifiable"),
    "ABLATE_DONOR": ablated("donor_owned"),
    "ABLATE_INTERACTION": ablated("interaction_only"),
    "ABLATE_NEGATIVE_HISTORY": ablated("live_negative_history"),
}
BASELINES = ("RAW_POSITIVE", "REFLECTION_CHECKLIST", "DONOR_AWARE_REVIEW", "MULTI_REVIEW")
ABLATIONS = tuple(a for a in ARMS if a.startswith("ABLATE_"))


# --------------------------------------------------------------------------
# Generation
# --------------------------------------------------------------------------

def generate_family(rng: random.Random, adjudicator: Adjudicator, free_table: dict):
    """Generate one family: 7 strata x CASES_PER_STRATUM cases, then shuffle."""
    rates: dict[str, dict[str, float]] = {}
    for stratum in STRATA:
        rates[stratum] = {
            coord: rng.uniform(FREE_RATE_LO, FREE_RATE_HI)
            for coord in free_table[stratum]["free"]
        }
    cases: list[dict] = []
    for stratum in STRATA:
        stratum_rates = rates[stratum]
        for j in range(CASES_PER_STRATUM):
            facts: dict[str, bool] = dict(PINNED[stratum])
            if stratum == "CANNOT_CHECK":
                integrity, frozen, identifiable = FAILING_SUBSETS[rng.randrange(7)]
                facts.update(
                    evidence_integrity=integrity,
                    frozen_protocol=frozen,
                    identifiable=identifiable,
                )
            for coord in free_table[stratum]["free"]:
                facts[coord] = rng.random() < stratum_rates[coord]
            cases.append(
                {
                    "stratum": stratum,
                    "case_id": f"{stratum[:2]}-{j:02d}",
                    **{name: facts.get(name, False) for name in FACTS},
                    "gold_disposition": adjudicator.adjudicate(
                        {name: facts.get(name, False) for name in FACTS}
                    ),
                }
            )
    rng.shuffle(cases)
    return cases, rates


# --------------------------------------------------------------------------
# Core benchmark
# --------------------------------------------------------------------------

def build_core() -> dict:
    table = json.loads(RULES.read_text(encoding="utf-8"))
    adjudicator = Adjudicator(table)
    free_table = table["stratum_free_coordinates"]
    rng = random.Random(SEED)

    zero = {
        "n": 0, "correct": 0, "false_promote": 0,
        "supported_total": 0, "supported_promoted": 0,
        "retain_total": 0, "retain_correct": 0,
        "reopen_total": 0, "reopen_correct": 0,
    }
    totals = {arm: dict(zero) for arm in ARMS}
    per_stratum = {
        arm: {s: {"n": 0, "correct": 0} for s in STRATA} for arm in ARMS
    }
    families = []
    remint_violations = 0
    determinism_violations = 0
    gold_stratum_violations = 0
    pinned_violations = 0
    gold_leak_checks = 0

    for family_index in range(N_FAMILIES):
        cases, rates = generate_family(rng, adjudicator, free_table)
        local = {arm: dict(zero) for arm in ARMS}
        cells = {s: list(c for c in cases if c["stratum"] == s) for s in STRATA}
        for s in STRATA:
            cell = cells[s]
            if len(cell) != CASES_PER_STRATUM:
                determinism_violations += 1
            for c in cell:
                if c["gold_disposition"] != STRATUM_GOLD[s]:
                    gold_stratum_violations += 1
                for k, v in PINNED[s].items():
                    if c[k] != v:
                        pinned_violations += 1
            free_coords = free_table[s]["free"]
            if free_coords:
                for coord in free_coords:
                    values = {c[coord] for c in cell}
                    if values != {True, False}:
                        remint_violations += 1
            else:
                first = cell[0]
                if any(
                    any(c[k] != first[k] for k in FACTS) for c in cell[1:]
                ):
                    determinism_violations += 1
        for c in cases:
            view = facts_only(c)
            gold = c["gold_disposition"]
            gold_leak_checks += int("gold_disposition" not in view)
            for arm, policy in ARMS.items():
                pred = policy(view)
                promote = pred == "SUPPORTED_RESIDUAL"
                row = local[arm]
                row["n"] += 1
                row["correct"] += int(pred == gold)
                row["false_promote"] += int(promote and gold != "SUPPORTED_RESIDUAL")
                row["supported_total"] += int(gold == "SUPPORTED_RESIDUAL")
                row["supported_promoted"] += int(promote and gold == "SUPPORTED_RESIDUAL")
                if c["stratum"] == "RETAIN_NEGATIVE":
                    row["retain_total"] += 1
                    row["retain_correct"] += int(pred == gold)
                if c["stratum"] == "SUPPORTED_REOPEN":
                    row["reopen_total"] += 1
                    row["reopen_correct"] += int(pred == gold)
                per_stratum[arm][c["stratum"]]["n"] += 1
                per_stratum[arm][c["stratum"]]["correct"] += int(pred == gold)
        families.append(
            {
                "family": family_index,
                "free_rates": rates,
                "stratum_counts": {s: len(cells[s]) for s in STRATA},
                "arm_correct": {
                    arm: local[arm]["correct"] / local[arm]["n"] for arm in ARMS
                },
            }
        )
        for arm in ARMS:
            for k, v in local[arm].items():
                totals[arm][k] += v

    total_cases = totals["ORION_RSE_FULL"]["n"]
    summary = {
        arm: {
            "n": row["n"],
            "disposition_accuracy": row["correct"] / row["n"],
            "false_promotion_rate": row["false_promote"] / row["n"],
            "useful_discovery_recall": (
                row["supported_promoted"] / row["supported_total"]
                if row["supported_total"] else 1.0
            ),
            "retain_negative_accuracy": (
                row["retain_correct"] / row["retain_total"]
                if row["retain_total"] else 1.0
            ),
            "supported_reopen_accuracy": (
                row["reopen_correct"] / row["reopen_total"]
                if row["reopen_total"] else 1.0
            ),
            "decision_budget_checks": BUDGET_CHECKS,
        }
        for arm, row in totals.items()
    }
    return {
        "schema": "ORION.P14E.SpecificationSeparatedSuperiority.Core.v1",
        "paper_id": "P14",
        "claim_id": "P14E_SPECIFICATION_SEPARATED_SUPERIORITY",
        "protocol": str(PROTOCOL.relative_to(REPO_ROOT)),
        "protocol_sha256": file_sha256(PROTOCOL),
        "adjudication_rules": str(RULES.relative_to(REPO_ROOT)),
        "adjudication_rules_sha256": file_sha256(RULES),
        "subject_identity": {
            "adjudicator": "generic interpreter of frozen rule table (parse + first-match)",
            "full_policy": "independently written facts-only policy from protocol prose",
            "circularity_control": "policy arms never call the adjudicator or see gold",
        },
        "environment": {
            "python_implementation": platform.python_implementation(),
            "python_version": platform.python_version(),
        },
        "design": {
            "seed": SEED,
            "n_families": N_FAMILIES,
            "strata": list(STRATA),
            "cases_per_stratum_per_family": CASES_PER_STRATUM,
            "total_cases": total_cases,
            "free_rate_range": [FREE_RATE_LO, FREE_RATE_HI],
            "decision_budget_checks": BUDGET_CHECKS,
            "rng": "stdlib random.Random",
        },
        "generation_audit": {
            "remint_violations": remint_violations,
            "determinism_violations": determinism_violations,
            "gold_stratum_violations": gold_stratum_violations,
            "pinned_violations": pinned_violations,
            "gold_leak_checks": gold_leak_checks,
        },
        "summary": summary,
        "per_stratum_accuracy": {
            arm: {
                s: per_stratum[arm][s]["correct"] / per_stratum[arm][s]["n"]
                for s in STRATA
            }
            for arm in ARMS
        },
        "families": families,
    }


def adjudicate(core: dict, *, byte_identical_replay: bool) -> dict:
    summary = core["summary"]
    audit = core["generation_audit"]
    full = summary["ORION_RSE_FULL"]
    strongest = max(BASELINES, key=lambda a: summary[a]["disposition_accuracy"])
    best = summary[strongest]
    gates = {
        "full_disposition_accuracy_one": full["disposition_accuracy"] == 1.0,
        "full_zero_false_promotion": full["false_promotion_rate"] == 0.0,
        "full_useful_discovery_recall_one": full["useful_discovery_recall"] == 1.0,
        "retain_and_reopen_exact": (
            full["retain_negative_accuracy"] == 1.0
            and full["supported_reopen_accuracy"] == 1.0
        ),
        "strongest_baseline_false_promotion_ge_0_05": (
            best["false_promotion_rate"] >= 0.05
        ),
        "accuracy_gain_ge_0_08": (
            full["disposition_accuracy"] - best["disposition_accuracy"] >= 0.08
        ),
        "strongest_baseline_is_multi_review": strongest == "MULTI_REVIEW",
        "every_ablation_strictly_worse": all(
            summary[a]["false_promotion_rate"] > 0.0
            or summary[a]["disposition_accuracy"] < full["disposition_accuracy"]
            for a in ABLATIONS
        ),
        "matched_decision_budget": all(
            summary[a]["decision_budget_checks"] == BUDGET_CHECKS for a in summary
        ),
        "gold_never_enters_policy_input": (
            audit["gold_leak_checks"] == core["design"]["total_cases"]
        ),
        "nuisance_reminting_and_determinism_verified": (
            audit["remint_violations"] == 0
            and audit["determinism_violations"] == 0
            and audit["gold_stratum_violations"] == 0
            and audit["pinned_violations"] == 0
        ),
        "byte_identical_two_subprocess_replay": byte_identical_replay,
    }
    terminal = SUPPORTED if all(gates.values()) else NOT_SUPPORTED
    return {
        "schema": "ORION.P14E.SpecificationSeparatedSuperiority.Result.v1",
        "core": core,
        "strongest_non_orion_baseline": strongest,
        "accuracy_gain_vs_strongest": (
            full["disposition_accuracy"] - best["disposition_accuracy"]
        ),
        "gates": gates,
        "terminal": terminal,
    }


def _worker(path: Path) -> None:
    path.write_text(canonical_text(build_core()), encoding="utf-8")


def _supervise(path: Path) -> dict:
    with tempfile.TemporaryDirectory(prefix="p14e-replay-") as directory:
        outputs = [Path(directory) / "a.json", Path(directory) / "b.json"]
        runs = [
            subprocess.run(
                [sys.executable, str(Path(__file__).resolve()), "--worker", str(out)],
                cwd=str(REPO_ROOT),
                capture_output=True,
                text=True,
                check=False,
            )
            for out in outputs
        ]
        if not all(run.returncode == 0 for run in runs):
            raise RuntimeError(
                "P14E protected worker failed: "
                + "; ".join(r.stderr[-400:] for r in runs)
            )
        raw = [out.read_bytes() for out in outputs]
        digests = [sha256(item).hexdigest() for item in raw]
        byte_identical = raw[0] == raw[1]
        result = adjudicate(json.loads(raw[0]), byte_identical_replay=byte_identical)
        result["replay"] = {
            "fresh_python_subprocesses": 2,
            "byte_identical": byte_identical,
            "first_core_sha256": digests[0],
            "second_core_sha256": digests[1],
        }
        path.write_text(canonical_text(result), encoding="utf-8")
        return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", type=Path)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    if args.worker:
        _worker(args.worker)
        return
    result = _supervise(args.out)
    print(
        json.dumps(
            {
                "terminal": result["terminal"],
                "strongest_non_orion_baseline": result["strongest_non_orion_baseline"],
                "accuracy_gain_vs_strongest": result["accuracy_gain_vs_strongest"],
                "summary": result["core"]["summary"],
                "generation_audit": result["core"]["generation_audit"],
                "gates": result["gates"],
                "replay": result["replay"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    if result["terminal"] == NOT_SUPPORTED:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
