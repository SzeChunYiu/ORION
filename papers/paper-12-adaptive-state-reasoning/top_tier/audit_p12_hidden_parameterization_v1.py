#!/usr/bin/env python3
"""P12 hidden-parameterization audit V1 (mechanical, static + dynamic).

Verifies that the FROZEN V1 allocator (run_transfer_allocation_v1.py,
imported by path, never modified) consumes ONLY the unified P9-compatible
signal surface and no domain-specific symbol, branch, or constant.

Static axis (AST reachability):
  - entry point: allocator_selection
  - transitive closure over function calls + module-global loads
  - every identifier / string literal / numeric literal reachable from the
    entry point is collected and checked against a domain-symbol denylist
  - the structure keys the allocator body reads must be a subset of
    {sid, queries, declared_cost}; module globals a subset of {TAU, BUDGET}

Dynamic axis:
  - running the frozen allocator on structures stripped to
    {sid, queries, declared_cost} must reproduce its selection on the full
    structures byte-identically for every case of every domain

Self-validation (mandatory; an unvalidated audit is INVALID):
  - sensitivity: three injected mutants (domain branch / cnf key read /
    domain engine call) must each be CAUGHT
  - specificity: a harmless local-variable rename must PASS
Terminals:
  P12_HIDDEN_PARAMETERIZATION_AUDIT_GREEN
  P12_HIDDEN_PARAMETERIZATION_AUDIT_FAILED
  P12_HIDDEN_PARAMETERIZATION_AUDIT_INVALID
"""
import ast
import builtins
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FROZEN = os.path.join(HERE, "run_transfer_allocation_v1.py")
ENTRY = "allocator_selection"
ALLOWED_GLOBALS = {"TAU", "BUDGET"}
ALLOWED_KEYS = {"sid", "queries", "declared_cost"}
# 4/500 = frozen tau/B; 0/1 = neutral accumulator literals
ALLOWED_ENTRY_LITERALS = {0, 1, 4, 500}

DOMAIN_TOKENS = [
    "SAT_PROPAGATION", "PATH_PLANNING", "KNAPSACK",
    "cnf", "grid", "items", "goal", "c_max",
    "clause", "bfs", "knapsack", "dp_cell", "occurrence",
]
DOMAIN_FUNC_PREFIXES = ("sat_", "path_", "knap_")
DOMAIN_GLOBAL_PREFIXES = ("_OCC", "_REVDIST", "_TABLE", "_CLAUSE")


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

    # module-level constant bindings (TAU=4, BUDGET=500)
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
                    called.add(f.name)
                    if f.name in funcs:
                        stack.append(f.name)
            elif isinstance(node, ast.Attribute):
                seen_strings.add(node.attr)
            elif isinstance(node, ast.Subscript):
                sl = node.slice
                if isinstance(sl, ast.Constant) and isinstance(sl.value, str):
                    seen_keys.add(sl.value)
            elif isinstance(node, ast.Name):
                if isinstance(node.ctx, ast.Load):
                    seen_globals.add(node.name)
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
                local_vars.add(node.name)
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
        findings.append(f"non-unified structure key read: {k}")
    for g in sorted(bad_free_globals):
        findings.append(f"non-allocator global reachable: {g}")
    for n in sorted(bad_numbers):
        findings.append(f"non-frozen numeric literal reachable: {n}")

    return (not findings), findings


# --------------------------------------------------------------- dynamic axis

def dynamic_axis():
    sys.path.insert(0, HERE)
    import run_transfer_allocation_v1 as frozen
    ok = True
    detail = []
    for cases_name in ("p12_transfer_cases_v1.json",
                       "p12_transfer_cases_expanded_v1.json"):
        path = os.path.join(HERE, cases_name)
        if not os.path.exists(path):
            continue
        with open(path) as f:
            cases = json.load(f)
        for dom in cases["domains"]:
            for case in dom["cases"]:
                full = case["structures"]
                stripped = [{"sid": st["sid"],
                             "queries": st["queries"],
                             "declared_cost": st["declared_cost"]}
                            for st in full]
                if frozen.allocator_selection(full) != \
                        frozen.allocator_selection(stripped):
                    ok = False
                    detail.append(f"{cases_name}:{case['case_id']} "
                                  f"selection differs under stripping")
    return ok, detail


# ------------------------------------------------------------ self-validation

FROZEN_SRC = open(FROZEN).read()


def mutant_domain_branch():
    return FROZEN_SRC.replace(
        "def allocator_selection(structures):",
        'def allocator_selection(structures, domain=None):\n'
        '    if domain == "SAT_PROPAGATION":\n'
        '        return [s["sid"] for s in structures]\n', 1)


def mutant_key_read():
    return FROZEN_SRC.replace(
        'if len(st["queries"]) >= TAU',
        'if len(st["queries"]) + len(st["cnf"]) >= TAU', 1)


def mutant_engine_call():
    return FROZEN_SRC.replace(
        "def allocator_selection(structures):",
        "def allocator_selection(structures):\n"
        "    if structures and sat_occ_map(structures[0]['cnf']):\n"
        "        pass\n", 1)


def mutant_harmless_rename():
    return FROZEN_SRC.replace(
        "def allocator_selection(structures):",
        "def allocator_selection(structs_in):").replace(
        "for i, st in enumerate(structures)",
        "for i, st in enumerate(structs_in)").replace(
        "(i, st) for i, st in enumerate(structures)",
        "(i, st) for i, st in enumerate(structs_in)")


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
    static_ok, findings = analyze(FROZEN_SRC)
    dyn_ok, dyn_detail = dynamic_axis()
    valid, selfval = self_validate()

    surface = {
        "entry_point": ENTRY,
        "allowed_module_globals": sorted(ALLOWED_GLOBALS),
        "allowed_structure_keys": sorted(ALLOWED_KEYS),
        "domain_tokens_screened": DOMAIN_TOKENS,
        "domain_prefixes_screened": list(DOMAIN_FUNC_PREFIXES),
    }
    if not valid:
        terminal = "P12_HIDDEN_PARAMETERIZATION_AUDIT_INVALID"
    elif static_ok and dyn_ok:
        terminal = "P12_HIDDEN_PARAMETERIZATION_AUDIT_GREEN"
    else:
        terminal = "P12_HIDDEN_PARAMETERIZATION_AUDIT_FAILED"

    report = {
        "schema": "p12-hidden-parameterization-audit-v1",
        "study": "P12_ROBUSTNESS_STRESS_V1",
        "frozen_module": "run_transfer_allocation_v1.py",
        "static_axis_ok": static_ok,
        "static_findings": findings,
        "dynamic_stripped_input_ok": dyn_ok,
        "dynamic_findings": dyn_detail,
        "self_validation_valid": valid,
        "self_validation": {k: v for k, v in selfval.items()
                            if not k.endswith("_findings")},
        "self_validation_findings": {k: v for k, v in selfval.items()
                                     if k.endswith("_findings")},
        "signal_surface": surface,
        "terminal": terminal,
    }
    sys.stdout.write(json.dumps(report, indent=1, sort_keys=True) + "\n")
    return 0 if terminal == "P12_HIDDEN_PARAMETERIZATION_AUDIT_GREEN" else 1


if __name__ == "__main__":
    sys.exit(main())
