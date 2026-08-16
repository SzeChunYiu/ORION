import ast
import inspect
from pathlib import Path

import orion.kernel.apply as apply_module
import orion.kernel.driver as driver_module
import orion.kernel.gate as gate_module
import orion.kernel.round as round_module
from orion.kernel.host import ProtectedHostAuthorizationService


ROOT = Path(__file__).parents[3]
SRC = ROOT / "src" / "orion"
AUTHORIZED_CONSTRUCTOR = (SRC / "kernel" / "authorization.py").resolve()


def _transition_authorization_call_sites():
    sites = []
    for path in SRC.rglob("*.py"):
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = None
            if isinstance(node.func, ast.Name):
                name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                name = node.func.attr
            if name == "TransitionAuthorization":
                sites.append(path.resolve())
    return sites


def test_only_authorization_module_constructs_transition_authorization():
    sites = _transition_authorization_call_sites()
    assert sites
    assert set(sites) == {AUTHORIZED_CONSTRUCTOR}


def test_candidate_facing_kernel_modules_do_not_import_protected_authorization_or_host():
    for module in (apply_module, gate_module, round_module, driver_module):
        source = inspect.getsource(module)
        assert "kernel.authorization" not in source
        assert "kernel.host" not in source
        assert "TransitionAuthorization" not in source
        assert "ProtectedHostAuthorizationService" not in source


def test_candidate_facing_call_signatures_accept_no_authority_material():
    targets = []
    for module, names in (
        (gate_module, ("grade_answer",)),
        (apply_module, ("grade_and_apply",)),
        (round_module, ("run_round",)),
        (driver_module, ("replay_cells",)),
    ):
        for name in names:
            target = getattr(module, name, None)
            if target is not None:
                targets.append(target)
    forbidden = {
        "authorization",
        "assurance_service",
        "registry",
        "signing_key",
        "private_key",
        "trust_store",
        "evaluator",
        "evaluate",
        "authority_state",
        "support_state",
    }
    assert targets
    for target in targets:
        assert forbidden.isdisjoint(inspect.signature(target).parameters), target


def test_candidate_facing_modules_contain_no_direct_verified_authority_assignment():
    for module in (apply_module, gate_module, round_module, driver_module):
        source = inspect.getsource(module)
        assert "AnswerAuthority.VERIFIED" not in source


def test_protected_host_operation_accepts_frozen_plan_appraisal_and_expectation_not_raw_authority_material():
    parameters = set(inspect.signature(ProtectedHostAuthorizationService.authorize).parameters)
    assert {"plan", "appraisal", "current_expectation", "chronology_frozen_before_candidate"}.issubset(parameters)
    assert {
        "private_key",
        "signing_key",
        "registry",
        "trust_store",
        "evaluator",
        "evaluate",
        "public_key",
    }.isdisjoint(parameters)
