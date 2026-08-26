#!/usr/bin/env python3
"""P12 price-aware successor surface audit V1 (SC5; mechanical, static +
dynamic).

Adapts audit_p12_hidden_parameterization_v1 to the SUCCESSOR selector
(p12_price_aware_allocator_v1.py, imported by path, never modified):
verifies the successor consumes ONLY the pre-registered readable surface
(charge-ledger record keys + prices + budget) and no domain-specific
symbol, branch, constant, or payload key.

Static axis (AST reachability from price_aware_selection):
  - reachable identifiers / strings / numeric literals checked against a
    domain-symbol denylist;
  - ledger record keys read must be a subset of
    {sid, declared_cost, reason_serve_certificate,
     state_serve_certificate};
  - the only numeric literals allowed are the structural loop constants
    {0, 1, -1} (no B, no thresholds, no tuned constants).

Dynamic axis (stronger than the V1 audit, since the selector input is a
derived ledger, not the raw structures):
  - STRIP: a ledger reduced to exactly the four allowed keys selects
    byte-identically;
  - DECOY: a ledger whose records additionally carry domain payload
    decoys (cnf / grid / items / goal / c_max / domain label) and bogus
    extra keys selects byte-identically;
  over every case of both frozen sets and every B2 union, in all five
  regimes.

Self-validation (mandatory; an unvalidated audit is INVALID):
  - sensitivity: three injected mutants (domain branch / payload-key
    read / domain engine call) must each be CAUGHT;
  - specificity: a harmless rename must PASS.

Terminals:
  P12_PRICE_AWARE_SUCCESSOR_SURFACE_AUDIT_GREEN
  P12_PRICE_AWARE_SUCCESSOR_SURFACE_AUDIT_FAILED
  P12_PRICE_AWARE_SUCCESSOR_SURFACE_AUDIT_INVALID
"""
import ast
import builtins
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_transfer_allocation_v1 as frozen  # noqa: E402
import run_p12_robustness_v1 as stress  # noqa: E402
from p12_price_aware_allocator_v1 import price_aware_selection  # noqa: E402

TARGET = os.path.join(HERE, "p12_price_aware_allocator_v1.py")
ENTRY = "price_aware_selection"
ALLOWED_GLOBALS = set()
ALLOWED_KEYS = {"sid", "declared_cost", "reason_serve_certificate",
                "state_serve_certificate"}
ALLOWED_ENTRY_LITERALS = {0, 1, -1}

DOMAIN_TOKENS = [
    "SAT_PROPAGATION", "PATH_PLANNING", "KNAPSACK",
    "cnf", "grid", "items", "goal", "c_max",
    "clause", "bfs", "knapsack", "dp_cell", "occurrence",
]
DOMAIN_FUNC_PREFIXES = ("sat_", "path_", "knap_")
DOMAIN_GLOBAL_PREFIXES = ("_OCC", "_REVDIST", "_TABLE", "_CLAUSE")

DECOY_KEYS = ["cnf", "grid", "items", "goal", "c_max", "domain",
              "queries", "regime", "mix"]


def load_tree(source):
    return ast.parse(source)


def function_defs(tree):
    return {n.name: n for n in ast.walk(tree)
            if isinstance(n, ast.FunctionDef)}


def analyze(source, entry=ENTRY):
    """Return (ok, findings) for the static axis on the given source."""
    tree = load_tree(source)
    funcs = function_defs(tree)
    if entry not in funcs:
        return False, [f"entry point {entry} not found"]

    const_values = {}
    for n in tree.body:
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name) and isinstance(n.value, ast.Constant):
                    const_values[t.id] = n.value.value

    reachable_funcs = set()
    seen_keys = set()
    seen_globals = set()
    seen_strings = set()
    seen_numbers = set()
    called = set()
    stack = [entry]
    while stack:
        fname = stack.pop()
        if fname in reachable_funcs:
            continue
        reachable_funcs.add(fname)
        for node in ast.walk(funcs[fname]):
            if isinstance(node, ast.Call):
                f = node.func
                if isinstance(f, ast.Name):
                    called.add(f.id)
                    if f.id in funcs:
                        stack.append(f.id)
            elif isinstance(node, ast.Attribute):
                seen_strings.add(node.attr)
            elif isinstance(node, ast.Subscript):
                sl = node.slice
                if isinstance(sl, ast.Constant) and isinstance(sl.value, str):
                    seen_keys.add(sl.value)
            elif isinstance(node, ast.Name):
                if isinstance(node.ctx, ast.Load):
                    seen_globals.add(node.id)
            elif isinstance(node, ast.Constant):
                if isinstance(node.value, str):
                    seen_strings.add(node.value)
                elif isinstance(node.value, (int, float)):
                    seen_numbers.add(node.value)

    findings = []
    local_vars = set()
    args = set()
    for f in reachable_funcs:
        for node in ast.walk(funcs[f]):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                local_vars.add(node.id)
            elif isinstance(node, ast.arg):
                args.add(node.arg)

    builtin_names = set(dir(builtins))
    bad_calls = {c for c in called
                 if c.startswith(DOMAIN_FUNC_PREFIXES)}
    bad_globals = {g for g in seen_globals - local_vars - args
                   if g.startswith(DOMAIN_GLOBAL_PREFIXES)}
    bad_strings = {s for s in seen_strings
                   if s in DOMAIN_TOKENS or s.startswith(DOMAIN_FUNC_PREFIXES)}
    bad_keys = seen_keys - ALLOWED_KEYS
    bad_free_globals = {g for g in seen_globals - local_vars - args
                        if g not in ALLOWED_GLOBALS
                        and g not in funcs
                        and g not in const_values
                        and g not in builtin_names}
    allowed_num = ALLOWED_ENTRY_LITERALS | set(
        v for v in const_values.values() if isinstance(v, (int, float)))
    bad_numbers = {n for n in seen_numbers
                   if isinstance(n, int) and n not in allowed_num}

    for c in sorted(bad_calls):
        findings.append(f"domain engine callable reachable: {c}")
    for g in sorted(bad_globals):
        findings.append(f"domain cache global reachable: {g}")
    for s in sorted(bad_strings):
        findings.append(f"domain token reachable: {s}")
    for k in sorted(bad_keys):
        findings.append(f"non-surface ledger key read: {k}")
    for g in sorted(bad_free_globals):
        findings.append(f"non-allocator global reachable: {g}")
    for n in sorted(bad_numbers):
        findings.append(f"non-structural numeric literal reachable: {n}")

    return (not findings), findings


# --------------------------------------------------------------- dynamic axis

def ledger_of(structures, reason, state):
    return [{"sid": st["sid"],
             "declared_cost": st["declared_cost"],
             "reason_serve_certificate": reason[st["sid"]],
             "state_serve_certificate": state[st["sid"]]}
            for st in structures]


def stripped(ledger):
    return [{k: rec[k] for k in ALLOWED_KEYS} for rec in ledger]


def decoyed(ledger):
    out = []
    for i, rec in enumerate(ledger):
        d = dict(rec)
        d["cnf"] = [[1, -2], [2, 3]]
        d["grid"] = [["#" for _ in range(3)] for _ in range(3)]
        d["items"] = [(2, 3), (3, 4)]
        d["goal"] = [1, 2]
        d["c_max"] = 11
        d["domain"] = ["SAT_PROPAGATION", "PATH_PLANNING",
                       "KNAPSACK"][i % 3]
        d["queries"] = [[1]] * (i % 5)
        d["regime"] = "MEM4X"
        d["mix"] = "MIX_SAT_HEAVY"
        out.append(d)
    return out


def ledgers():
    """Every ledger the battery feeds the selector: both case sets + the
    three B2 unions (same construction as the runner)."""
    out = []
    for name in ("p12_transfer_cases_v1.json",
                 "p12_transfer_cases_expanded_v1.json"):
        cases = stress.load_cases(name)
        for dom in cases["domains"]:
            for case in dom["cases"]:
                st = case["structures"]
                reason, state, _, _ = stress.per_structure_charges(
                    dom["domain"], st)
                out.append((f"{name}:{case['case_id']}",
                            ledger_of(st, reason, state)))
    exp = stress.load_cases("p12_transfer_cases_expanded_v1.json")
    for mix, counts in stress.B2_MIXES:
        union = []
        for domain in stress.DOMAIN_ORDER:
            dom = next(d for d in exp["domains"] if d["domain"] == domain)
            for case in dom["cases"][:counts[domain]]:
                for st in case["structures"]:
                    union.append((domain, st))
        reason, state = {}, {}
        for domain in stress.DOMAIN_ORDER:
            structs = [st for d, st in union if d == domain]
            r_, s_, _, _ = stress.per_structure_charges(domain, structs)
            reason.update(r_)
            state.update(s_)
        out.append((f"B2:{mix}", ledger_of([st for _, st in union],
                                            reason, state)))
    return out


def dynamic_axis():
    ok = True
    detail = []
    checked = 0
    for label, ledger in ledgers():
        for regime, p_b, p_s in stress.REGIMES:
            base = price_aware_selection(ledger, (p_b, p_s),
                                         frozen.BUDGET)
            if price_aware_selection(stripped(ledger), (p_b, p_s),
                                     frozen.BUDGET) != base:
                ok = False
                detail.append(f"{label}:{regime} strip changes selection")
            if price_aware_selection(decoyed(ledger), (p_b, p_s),
                                     frozen.BUDGET) != base:
                ok = False
                detail.append(f"{label}:{regime} decoys change selection")
            checked += 1
    return ok, detail, checked


# ------------------------------------------------------------ self-validation

SRC = open(TARGET).read()


def mutant_domain_branch():
    return SRC.replace(
        "def price_aware_selection(ledger, prices, budget):",
        'def price_aware_selection(ledger, prices, budget):\n'
        '    if ledger and ledger[0].get("domain") == '
        '"SAT_PROPAGATION":\n'
        '        return [r["sid"] for r in ledger]\n', 1)


def mutant_key_read():
    return SRC.replace(
        'rec["declared_cost"],',
        'rec["cnf"],\n              rec["declared_cost"] + 0 * '
        'len(rec["cnf"]),', 1)


def mutant_engine_call():
    return SRC.replace(
        "def price_aware_selection(ledger, prices, budget):",
        "def price_aware_selection(ledger, prices, budget):\n"
        "    if ledger and sat_occ_map(ledger[0]['cnf']):\n"
        "        pass\n", 1)


def mutant_harmless_rename():
    return SRC.replace("p_build, p_serve = prices",
                       "pb, ps = prices") \
              .replace("p_build * rec[\"declared_cost\"]",
                       "pb * rec[\"declared_cost\"]") \
              .replace("p_serve * (rec[\"reason_serve_certificate\"]",
                       "ps * (rec[\"reason_serve_certificate\"]")


def self_validate():
    results = {}
    for name, src in (("domain_branch", mutant_domain_branch()),
                      ("key_read", mutant_key_read()),
                      ("engine_call", mutant_engine_call())):
        ok, findings = analyze(src)
        results[f"caught_{name}"] = (not ok) and bool(findings)
        results[f"{name}_findings"] = findings[:3]
    ok, findings = analyze(mutant_harmless_rename())
    results["harmless_rename_passes"] = ok
    results["harmless_rename_findings"] = findings[:3]
    valid = (results["caught_domain_branch"]
             and results["caught_key_read"]
             and results["caught_engine_call"]
             and results["harmless_rename_passes"])
    return valid, results


def main():
    static_ok, findings = analyze(SRC)
    dyn_ok, dyn_detail, dyn_checked = dynamic_axis()
    valid, selfval = self_validate()

    surface = {
        "entry_point": ENTRY,
        "allowed_module_globals": sorted(ALLOWED_GLOBALS),
        "allowed_ledger_keys": sorted(ALLOWED_KEYS),
        "allowed_numeric_literals": sorted(ALLOWED_ENTRY_LITERALS),
        "domain_tokens_screened": DOMAIN_TOKENS,
        "domain_prefixes_screened": list(DOMAIN_FUNC_PREFIXES),
        "dynamic_checks": dyn_checked,
    }
    if not valid:
        terminal = "P12_PRICE_AWARE_SUCCESSOR_SURFACE_AUDIT_INVALID"
    elif static_ok and dyn_ok:
        terminal = "P12_PRICE_AWARE_SUCCESSOR_SURFACE_AUDIT_GREEN"
    else:
        terminal = "P12_PRICE_AWARE_SUCCESSOR_SURFACE_AUDIT_FAILED"

    report = {
        "schema": "p12-price-aware-successor-surface-audit-v1",
        "study": "P12_PRICE_AWARE_SUCCESSOR_V1",
        "target_module": "p12_price_aware_allocator_v1.py",
        "static_axis_ok": static_ok,
        "static_findings": findings,
        "dynamic_stripped_and_decoy_input_ok": dyn_ok,
        "dynamic_findings": dyn_detail,
        "dynamic_ledger_regime_checks": dyn_checked,
        "self_validation_valid": valid,
        "self_validation": {k: v for k, v in selfval.items()
                            if not k.endswith("_findings")},
        "self_validation_findings": {k: v for k, v in selfval.items()
                                     if k.endswith("_findings")},
        "signal_surface": surface,
        "terminal": terminal,
    }
    sys.stdout.write(json.dumps(report, indent=1, sort_keys=True) + "\n")
    return 0 if terminal == "P12_PRICE_AWARE_SUCCESSOR_SURFACE_AUDIT_GREEN" \
        else 1


if __name__ == "__main__":
    sys.exit(main())
