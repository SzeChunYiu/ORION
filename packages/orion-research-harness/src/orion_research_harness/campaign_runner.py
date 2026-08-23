from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from .campaign_control import decide_campaign, manifest_digest, validate_manifest
from .campaign_protocol import (
    CampaignState,
    CampaignTransition,
    ProtectedReference,
)
from .local_tools import service_local_request
from .protocol import content_digest
from .workspace import ResearchWorkspace

_LOCAL_CAPABILITIES = {"FILE_READ", "FILE_WRITE", "FILE_LIST", "SHELL", "PYTHON"}
_FORBIDDEN_AUTHORITY_TRUE = {
    "r6_authority",
    "grants_scientific_authority",
    "grants_novelty_authority",
    "grants_revision_authority",
    "grants_adoption_authority",
    "grants_promotion_authority",
    "grants_merge_authority",
    "grants_global_task_stop_authority",
}


def _require_string(value: Any, *, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{name} must be a non-empty string")
    return value


def _phase(manifest: Mapping[str, Any], phase_id: str) -> Mapping[str, Any]:
    phases = manifest.get("phases")
    if not isinstance(phases, Mapping):
        raise TypeError("campaign phases must be an object")
    phase = phases.get(phase_id)
    if not isinstance(phase, Mapping):
        raise ValueError(f"campaign phase must be an object: {phase_id}")
    return phase


def _scan_authority(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError("capability payload keys must be strings")
            if key in _FORBIDDEN_AUTHORITY_TRUE and item is True:
                raise ValueError(f"capability attempted authority escalation: {key}")
            _scan_authority(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _scan_authority(item)


def _extract(value: Any, path: list[str] | tuple[str, ...]) -> Any:
    cur = value
    for raw in path:
        key = _require_string(raw, name="result path component")
        if isinstance(cur, Mapping):
            if key not in cur:
                raise KeyError(".".join(path))
            cur = cur[key]
        elif isinstance(cur, (list, tuple)):
            if not key.isdigit():
                raise KeyError(".".join(path))
            index = int(key)
            if index >= len(cur):
                raise KeyError(".".join(path))
            cur = cur[index]
        else:
            raise KeyError(".".join(path))
    return cur


def _transform(value: Any, transform: str) -> str:
    if transform == "STRING":
        if not isinstance(value, str):
            raise TypeError("STRING transform requires a string")
        return value
    if transform == "BOOL_YES_NO":
        if not isinstance(value, bool):
            raise TypeError("BOOL_YES_NO requires a boolean")
        return "YES" if value else "NO"
    if transform == "BOOL_TRUE_FALSE":
        if not isinstance(value, bool):
            raise TypeError("BOOL_TRUE_FALSE requires a boolean")
        return "true" if value else "false"
    raise ValueError(f"unsupported evidence transform: {transform}")


def _parse_token(stdout: str, prefix: str) -> Mapping[str, Any]:
    rows = [line[len(prefix) :] for line in stdout.splitlines() if line.startswith(prefix)]
    if len(rows) != 1:
        raise ValueError(f"expected exactly one result token {prefix!r}, found {len(rows)}")
    payload = json.loads(rows[0])
    if not isinstance(payload, Mapping):
        raise ValueError("result token must contain a JSON object")
    return payload


def _parsed_payload(result_output: Any, contract: Mapping[str, Any]) -> Mapping[str, Any]:
    if not isinstance(contract, Mapping):
        raise TypeError("campaign result contract must be an object")
    kind = contract.get("kind", "DIRECT_JSON")
    if not isinstance(kind, str):
        raise TypeError("campaign result contract kind must be a string")
    if kind == "DIRECT_JSON":
        if not isinstance(result_output, Mapping):
            raise TypeError("DIRECT_JSON capability output must be an object")
        payload = result_output
    elif kind == "SHELL_JSON_TOKEN":
        if not isinstance(result_output, Mapping):
            raise TypeError("SHELL_JSON_TOKEN output must be a local-tool object")
        returncode = result_output.get("returncode")
        if not isinstance(returncode, int) or isinstance(returncode, bool):
            raise TypeError("SHELL_JSON_TOKEN.returncode must be an integer")
        if returncode != 0:
            stderr = result_output.get("stderr", "")
            if not isinstance(stderr, str):
                raise TypeError("SHELL_JSON_TOKEN.stderr must be a string")
            raise RuntimeError(f"capability process failed: {stderr}")
        stdout = result_output.get("stdout")
        if not isinstance(stdout, str):
            raise TypeError("SHELL_JSON_TOKEN.stdout must be a string")
        prefix = _require_string(contract.get("prefix"), name="result token prefix")
        payload = _parse_token(stdout, prefix)
    else:
        raise ValueError(f"unknown campaign result contract kind: {kind}")
    _scan_authority(payload)
    return payload


def _contract_rows(contract: Mapping[str, Any], field: str) -> tuple[Mapping[str, Any], ...]:
    raw = contract.get(field, ())
    if isinstance(raw, (str, bytes)) or not isinstance(raw, (tuple, list)):
        raise TypeError(f"campaign result contract {field} must be an array")
    rows: list[Mapping[str, Any]] = []
    for row in raw:
        if not isinstance(row, Mapping):
            raise TypeError(f"campaign result contract {field} entries must be objects")
        rows.append(row)
    return tuple(rows)


def _path(row: Mapping[str, Any]) -> tuple[str, ...]:
    raw = row.get("path")
    if isinstance(raw, (str, bytes)) or not isinstance(raw, (tuple, list)) or not raw:
        raise TypeError("campaign result path must be a non-empty array")
    return tuple(_require_string(item, name="result path component") for item in raw)


def _evidence_updates(payload: Mapping[str, Any], contract: Mapping[str, Any]) -> dict[str, str]:
    for row in _contract_rows(contract, "required_payload_values"):
        path = _path(row)
        if "equals" not in row:
            raise ValueError("required_payload_values row requires equals")
        actual = _extract(payload, path)
        if actual != row["equals"] or type(actual) is not type(row["equals"]):
            raise ValueError(
                f"required payload condition failed at {'.'.join(path)}: "
                f"{actual!r} != {row['equals']!r}"
            )
    updates: dict[str, str] = {}
    for row in _contract_rows(contract, "evidence_rules"):
        key = _require_string(row.get("evidence_key"), name="evidence_key")
        if key in updates:
            raise ValueError(f"duplicate evidence update: {key}")
        if "literal" in row:
            literal = row["literal"]
            if not isinstance(literal, str):
                raise TypeError("evidence literal must be a string")
            value = literal
        else:
            raw = _extract(payload, _path(row))
            transform = row.get("transform", "STRING")
            if not isinstance(transform, str):
                raise TypeError("evidence transform must be a string")
            value = _transform(raw, transform)
        updates[key] = value
    return updates


def _resolved_python_script(project_root: Path, host_payload: Mapping[str, Any]) -> Path | None:
    argv = host_payload.get("argv")
    if not isinstance(argv, list) or len(argv) < 2:
        return None
    if any(not isinstance(value, str) for value in argv):
        raise TypeError("registered campaign argv entries must be strings")
    if argv[0] not in {"python", "python3"}:
        return None
    cwd_raw = host_payload.get("cwd", ".")
    if not isinstance(cwd_raw, str):
        raise TypeError("registered campaign cwd must be a string")
    cwd = (project_root / cwd_raw).resolve()
    script = (cwd / argv[1]).resolve()
    try:
        script.relative_to(project_root)
    except ValueError as exc:
        raise PermissionError("registered campaign script escapes project root") from exc
    return script


def _protect_unreleased_refs(
    *,
    workspace: ResearchWorkspace,
    protected_refs: tuple[ProtectedReference, ...],
    capability_spec: Mapping[str, Any],
) -> None:
    host_payload = capability_spec.get("payload")
    if not isinstance(host_payload, Mapping):
        raise TypeError("campaign capability payload must be an object")
    material = json.dumps(host_payload, sort_keys=True)
    read_paths = capability_spec.get("declared_read_paths", ())
    if isinstance(read_paths, (str, bytes)) or not isinstance(read_paths, (tuple, list)):
        raise TypeError("declared_read_paths must be an array")
    if any(not isinstance(value, str) for value in read_paths):
        raise TypeError("declared_read_paths entries must be strings")
    material += "\n" + "\n".join(read_paths)
    host_capability = _require_string(
        capability_spec.get("host_capability"), name="host_capability"
    )
    if host_capability == "SHELL":
        script = _resolved_python_script(workspace.project_root, host_payload)
        if script is not None:
            if not script.is_file():
                raise FileNotFoundError(script)
            material += "\n" + script.read_text(encoding="utf-8", errors="replace")
    for ref in protected_refs:
        ref.verify()
        if ref.released:
            continue
        if ref.path and ref.path in material:
            raise PermissionError(f"unreleased protected path used by capability: {ref.ref_id}")
        if ref.blob and ref.blob in material:
            raise PermissionError(f"unreleased protected blob used by capability: {ref.ref_id}")


def _released_refs(
    current: tuple[ProtectedReference, ...],
    capability_spec: Mapping[str, Any],
) -> tuple[ProtectedReference, ...]:
    raw_ids = capability_spec.get("release_protected_refs_on_success", ())
    if isinstance(raw_ids, (str, bytes)) or not isinstance(raw_ids, (tuple, list)):
        raise TypeError("release_protected_refs_on_success must be an array")
    if any(not isinstance(value, str) or not value for value in raw_ids):
        raise TypeError("release_protected_refs_on_success entries must be non-empty strings")
    release_ids = set(raw_ids)
    unknown = release_ids - {item.ref_id for item in current}
    if unknown:
        raise ValueError(f"capability attempted to release unknown protected refs: {sorted(unknown)}")
    return tuple(
        ProtectedReference(
            ref_id=item.ref_id,
            path=item.path,
            blob=item.blob,
            released=item.released or item.ref_id in release_ids,
        )
        for item in current
    )


def initialize_campaign(
    workspace: ResearchWorkspace,
    manifest: Mapping[str, Any],
) -> CampaignState:
    validate_manifest(manifest)
    campaign_id = manifest["campaign_id"]
    workspace.save_campaign_manifest(campaign_id, manifest)
    existing = workspace.load_latest_campaign_state(campaign_id)
    if existing is not None:
        state = CampaignState.from_dict(existing)
        if state.manifest_digest != manifest_digest(manifest):
            raise ValueError("workspace contains campaign state for another manifest")
        return state

    initial_phase = manifest["initial_phase"]
    phase = _phase(manifest, initial_phase)
    protected_raw = manifest.get("protected_refs", ())
    if isinstance(protected_raw, (str, bytes)) or not isinstance(protected_raw, (tuple, list)):
        raise TypeError("protected_refs must be an array")
    protected = tuple(ProtectedReference.from_dict(item) for item in protected_raw)
    observations = manifest.get("initial_observations", {})
    if not isinstance(observations, Mapping):
        raise TypeError("initial_observations must be an object")
    authority_ceiling = manifest.get(
        "authority_ceiling", "NON_AUTHORIZING_RESEARCH_CONTROL"
    )
    if not isinstance(authority_ceiling, str) or not authority_ceiling:
        raise TypeError("authority_ceiling must be a non-empty string")
    obligations = phase.get("active_hard_obligations", ())
    if isinstance(obligations, (str, bytes)) or not isinstance(obligations, (tuple, list)):
        raise TypeError("active_hard_obligations must be an array")
    state = CampaignState.create(
        campaign_id=campaign_id,
        claim_id=manifest["claim_id"],
        phase_id=initial_phase,
        cycle_index=0,
        manifest_digest=manifest_digest(manifest),
        observations=observations,
        active_hard_obligations=obligations,
        protected_refs=protected,
        authority_ceiling=authority_ceiling,
    )
    workspace.save_campaign_state(campaign_id, state.as_dict())
    return state


def _contract_failure(
    *,
    state: CampaignState,
    decision,
    request,
    result,
    exc: Exception,
) -> dict[str, Any]:
    return {
        "schema": "ORION.ResearchCampaignOutcome.v1",
        "status": "CAPABILITY_CONTRACT_FAILED",
        "campaign_id": state.campaign_id,
        "phase_id": state.phase_id,
        "decision": decision.as_dict(),
        "request": request.as_dict(),
        "result": result.as_dict(),
        "error": f"{type(exc).__name__}: {exc}",
        "state": state.as_dict(),
        "grants_scientific_authority": False,
        "grants_novelty_authority": False,
    }


def run_campaign_cycle(
    workspace: ResearchWorkspace,
    manifest: Mapping[str, Any],
    *,
    auto_service_local: bool = True,
) -> dict[str, Any]:
    state = initialize_campaign(workspace, manifest)
    phase = _phase(manifest, state.phase_id)
    if phase.get("terminal") is True:
        terminal_name = phase.get("terminal_name", "TERMINAL")
        if not isinstance(terminal_name, str) or not terminal_name:
            raise TypeError("terminal_name must be a non-empty string")
        return {
            "schema": "ORION.ResearchCampaignOutcome.v1",
            "status": "TERMINAL",
            "campaign_id": state.campaign_id,
            "phase_id": state.phase_id,
            "state": state.as_dict(),
            "terminal": terminal_name,
        }

    decision = decide_campaign(state, manifest)
    if decision.selected_id is None:
        return {
            "schema": "ORION.ResearchCampaignOutcome.v1",
            "status": "NO_SELECTED_ACTION",
            "campaign_id": state.campaign_id,
            "phase_id": state.phase_id,
            "state": state.as_dict(),
            "decision": decision.as_dict(),
        }

    selected_map = phase.get("selected_capabilities", {})
    if not isinstance(selected_map, Mapping):
        raise TypeError("selected_capabilities must be an object")
    capability_id = selected_map.get(decision.selected_id)
    if capability_id is None:
        return {
            "schema": "ORION.ResearchCampaignOutcome.v1",
            "status": "CAPABILITY_UNREGISTERED",
            "campaign_id": state.campaign_id,
            "phase_id": state.phase_id,
            "selected_id": decision.selected_id,
            "decision": decision.as_dict(),
        }
    capability_id = _require_string(capability_id, name="capability id")
    capabilities = manifest.get("capabilities")
    if not isinstance(capabilities, Mapping):
        raise TypeError("campaign capabilities must be an object")
    capability_spec = capabilities[capability_id]
    if not isinstance(capability_spec, Mapping):
        raise TypeError("campaign capability spec must be an object")
    _protect_unreleased_refs(
        workspace=workspace,
        protected_refs=state.protected_refs,
        capability_spec=capability_spec,
    )

    payload_spec = capability_spec.get("payload")
    if not isinstance(payload_spec, Mapping):
        raise TypeError("campaign capability payload must be an object")
    request_payload = dict(payload_spec)
    request_payload["campaign_id"] = state.campaign_id
    request_payload["phase_id"] = state.phase_id
    request_payload["selected_id"] = decision.selected_id
    request_payload["selected_kind"] = decision.selected_kind
    request = workspace.get_or_create_request(
        capability=_require_string(
            capability_spec.get("host_capability"), name="host_capability"
        ),
        payload=request_payload,
    )
    result = workspace.load_result(request.request_id)
    if result is None and auto_service_local and request.capability in _LOCAL_CAPABILITIES:
        service_local_request(workspace, request.request_id)
        result = workspace.load_result(request.request_id)
    if result is None:
        return {
            "schema": "ORION.ResearchCampaignOutcome.v1",
            "status": "PENDING_CAPABILITY",
            "campaign_id": state.campaign_id,
            "phase_id": state.phase_id,
            "decision": decision.as_dict(),
            "request": request.as_dict(),
        }
    if not result.success:
        return {
            "schema": "ORION.ResearchCampaignOutcome.v1",
            "status": "CAPABILITY_FAILED",
            "campaign_id": state.campaign_id,
            "phase_id": state.phase_id,
            "decision": decision.as_dict(),
            "request": request.as_dict(),
            "result": result.as_dict(),
            "state": state.as_dict(),
        }

    contract = capability_spec.get("result_contract", {})
    try:
        payload = _parsed_payload(result.output, contract)
        updates = _evidence_updates(payload, contract)
    except (KeyError, TypeError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        return _contract_failure(
            state=state,
            decision=decision,
            request=request,
            result=result,
            exc=exc,
        )

    next_phase = _require_string(capability_spec.get("next_phase"), name="next_phase")
    phases = manifest.get("phases")
    assert isinstance(phases, Mapping)
    if next_phase not in phases:
        raise ValueError(f"capability points to unknown next phase: {next_phase}")
    next_phase_spec = _phase(manifest, next_phase)
    observations = state.observation_map
    observations.update(updates)
    history = (
        *state.history_digests,
        decision.decision_digest,
        request.request_digest,
        result.result_digest,
        content_digest(payload),
    )
    next_obligations = next_phase_spec.get("active_hard_obligations", ())
    if isinstance(next_obligations, (str, bytes)) or not isinstance(
        next_obligations, (tuple, list)
    ):
        raise TypeError("active_hard_obligations must be an array")
    after = CampaignState.create(
        campaign_id=state.campaign_id,
        claim_id=state.claim_id,
        phase_id=next_phase,
        cycle_index=state.cycle_index + 1,
        manifest_digest=state.manifest_digest,
        observations=observations,
        active_hard_obligations=next_obligations,
        protected_refs=_released_refs(state.protected_refs, capability_spec),
        history_digests=history,
        authority_ceiling=state.authority_ceiling,
    )
    if after.state_digest == state.state_digest:
        raise RuntimeError("campaign transition did not change state")
    workspace.save_campaign_state(state.campaign_id, after.as_dict())

    terminal_name = next_phase_spec.get("terminal_name", "TERMINAL")
    if not isinstance(terminal_name, str) or not terminal_name:
        raise TypeError("terminal_name must be a non-empty string")
    terminal = terminal_name if next_phase_spec.get("terminal") is True else "CONTINUE"
    transition_base = {
        "schema": "ORION.ResearchCampaignTransition.v1",
        "campaign_id": state.campaign_id,
        "cycle_index": state.cycle_index,
        "before_state_digest": state.state_digest,
        "decision_digest": decision.decision_digest,
        "capability_request_digest": request.request_digest,
        "capability_result_digest": result.result_digest,
        "after_state_digest": after.state_digest,
        "terminal": terminal,
        "grants_scientific_authority": False,
        "grants_novelty_authority": False,
        "grants_adoption_authority": False,
        "grants_promotion_authority": False,
        "grants_merge_authority": False,
        "grants_global_task_stop_authority": False,
    }
    transition = CampaignTransition(
        campaign_id=state.campaign_id,
        cycle_index=state.cycle_index,
        before_state_digest=state.state_digest,
        decision_digest=decision.decision_digest,
        capability_request_digest=request.request_digest,
        capability_result_digest=result.result_digest,
        after_state_digest=after.state_digest,
        terminal=terminal,
        transition_digest=content_digest(transition_base),
    )
    transition.validate()
    workspace.save_campaign_cycle(state.campaign_id, transition.as_dict())
    return {
        "schema": "ORION.ResearchCampaignOutcome.v1",
        "status": "ADVANCED" if terminal == "CONTINUE" else "TERMINAL",
        "campaign_id": state.campaign_id,
        "phase_id": state.phase_id,
        "selected_id": decision.selected_id,
        "capability_id": capability_id,
        "evidence_updates": updates,
        "decision": decision.as_dict(),
        "request": request.as_dict(),
        "result_digest": result.result_digest,
        "transition": transition.as_dict(),
        "state": after.as_dict(),
        "terminal": terminal,
    }


def run_campaign(
    workspace: ResearchWorkspace,
    manifest: Mapping[str, Any],
    *,
    max_cycles: int = 32,
    auto_service_local: bool = True,
) -> dict[str, Any]:
    if not isinstance(max_cycles, int) or isinstance(max_cycles, bool) or max_cycles < 1:
        raise ValueError("max_cycles must be a positive integer")
    validate_manifest(manifest)
    outcomes = []
    for _ in range(max_cycles):
        outcome = run_campaign_cycle(
            workspace,
            manifest,
            auto_service_local=auto_service_local,
        )
        outcomes.append(outcome)
        if outcome["status"] != "ADVANCED":
            return {
                "schema": "ORION.ResearchCampaignRun.v1",
                "campaign_id": manifest["campaign_id"],
                "status": outcome["status"],
                "cycles": outcomes,
            }
    return {
        "schema": "ORION.ResearchCampaignRun.v1",
        "campaign_id": manifest["campaign_id"],
        "status": "MAX_CYCLES_REACHED",
        "cycles": outcomes,
    }
