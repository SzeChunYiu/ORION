from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from .campaign_control import decide_campaign, manifest_digest, validate_manifest
from .campaign_protocol import (
    CampaignState,
    CampaignTransition,
    ProtectedReference,
    authority_false,
)
from .campaign_store import CampaignStore
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


def _phase(manifest: Mapping[str, Any], phase_id: str) -> Mapping[str, Any]:
    phase = manifest["phases"][phase_id]
    if not isinstance(phase, Mapping):
        raise TypeError("campaign phase must be an object")
    return phase


def _scan_authority(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if str(key) in _FORBIDDEN_AUTHORITY_TRUE and item is True:
                raise ValueError(f"capability attempted authority escalation: {key}")
            _scan_authority(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _scan_authority(item)


def _extract(value: Any, path: list[str] | tuple[str, ...]) -> Any:
    cur = value
    for raw in path:
        key = str(raw)
        if isinstance(cur, Mapping):
            if key not in cur:
                raise KeyError(".".join(map(str, path)))
            cur = cur[key]
        elif isinstance(cur, (list, tuple)):
            cur = cur[int(key)]
        else:
            raise KeyError(".".join(map(str, path)))
    return cur


def _transform(value: Any, transform: str) -> str:
    if transform == "STRING":
        if not isinstance(value, str):
            raise TypeError("STRING transform requires a string")
        return value
    if transform == "BOOL_YES_NO":
        if not isinstance(value, bool):
            raise TypeError("BOOL_YES_NO requires boolean")
        return "YES" if value else "NO"
    if transform == "BOOL_TRUE_FALSE":
        if not isinstance(value, bool):
            raise TypeError("BOOL_TRUE_FALSE requires boolean")
        return "true" if value else "false"
    if transform == "JSON":
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    raise ValueError(f"unsupported evidence transform: {transform}")


def _parse_token(stdout: str, prefix: str) -> Mapping[str, Any]:
    rows = [line[len(prefix) :] for line in stdout.splitlines() if line.startswith(prefix)]
    if len(rows) != 1:
        raise ValueError(f"expected exactly one result token {prefix!r}, found {len(rows)}")
    payload = json.loads(rows[0])
    if not isinstance(payload, Mapping):
        raise TypeError("result token must contain an object")
    return payload


def _parsed_payload(result_output: Any, contract: Mapping[str, Any]) -> Mapping[str, Any]:
    kind = str(contract.get("kind", "DIRECT_JSON"))
    if kind == "DIRECT_JSON":
        if not isinstance(result_output, Mapping):
            raise TypeError("DIRECT_JSON capability output must be an object")
        payload = result_output
    elif kind == "SHELL_JSON_TOKEN":
        if not isinstance(result_output, Mapping):
            raise TypeError("SHELL_JSON_TOKEN output must be a local-tool object")
        returncode = result_output.get("returncode")
        if not isinstance(returncode, int) or isinstance(returncode, bool):
            raise TypeError("local process returncode must be an integer")
        if returncode != 0:
            raise RuntimeError(f"capability process failed: {result_output.get('stderr', '')}")
        payload = _parse_token(str(result_output.get("stdout", "")), str(contract["prefix"]))
    else:
        raise ValueError(f"unknown campaign result contract kind: {kind}")
    _scan_authority(payload)
    return payload


def _evidence_updates(payload: Mapping[str, Any], contract: Mapping[str, Any]) -> dict[str, str]:
    for row in contract.get("required_payload_values", ()):
        if not isinstance(row, Mapping):
            raise TypeError("required_payload_values entry must be an object")
        actual = _extract(payload, list(map(str, row["path"])))
        if actual != row["equals"]:
            raise ValueError(
                f"required payload condition failed at {'.'.join(map(str, row['path']))}: "
                f"{actual!r} != {row['equals']!r}"
            )
    updates: dict[str, str] = {}
    for row in contract.get("evidence_rules", ()):
        if not isinstance(row, Mapping):
            raise TypeError("evidence rule must be an object")
        key = str(row["evidence_key"])
        if key in updates:
            raise ValueError(f"duplicate evidence update: {key}")
        if "literal" in row:
            value = str(row["literal"])
        else:
            raw = _extract(payload, list(map(str, row["path"])))
            value = _transform(raw, str(row.get("transform", "STRING")))
        updates[key] = value
    return updates


def _resolved_python_script(project_root: Path, host_payload: Mapping[str, Any]) -> Path | None:
    argv = host_payload.get("argv")
    if not isinstance(argv, list) or len(argv) < 2:
        return None
    if str(argv[0]) not in {"python", "python3"}:
        return None
    cwd = (project_root / str(host_payload.get("cwd", "."))).resolve()
    script = (cwd / str(argv[1])).resolve()
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
    host_payload = capability_spec["payload"]
    if not isinstance(host_payload, Mapping):
        raise TypeError("capability payload must be an object")
    material = json.dumps(host_payload, sort_keys=True)
    material += "\n" + "\n".join(map(str, capability_spec.get("declared_read_paths", ())))
    if str(capability_spec["host_capability"]) == "SHELL":
        script = _resolved_python_script(workspace.project_root, host_payload)
        if script is not None:
            if not script.is_file():
                raise FileNotFoundError(script)
            material += "\n" + script.read_text(encoding="utf-8", errors="replace")
    for ref in protected_refs:
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
    release_ids = set(map(str, capability_spec.get("release_protected_refs_on_success", ())))
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
    store = CampaignStore(workspace)
    campaign_id = str(manifest["campaign_id"])
    store.freeze_manifest(campaign_id, manifest)
    existing = store.latest_state(campaign_id)
    if existing is not None:
        state = CampaignState.from_dict(existing)
        if state.manifest_digest != manifest_digest(manifest):
            raise ValueError("workspace contains campaign state for another manifest")
        return state
    initial_phase = str(manifest["initial_phase"])
    phase = _phase(manifest, initial_phase)
    protected = tuple(
        ProtectedReference.from_dict(item) for item in manifest.get("protected_refs", ())
    )
    initial_observations = manifest.get("initial_observations", {})
    if not isinstance(initial_observations, Mapping):
        raise TypeError("initial_observations must be an object")
    state = CampaignState.create(
        campaign_id=campaign_id,
        claim_id=str(manifest["claim_id"]),
        phase_id=initial_phase,
        cycle_index=0,
        manifest_digest=manifest_digest(manifest),
        observations={str(k): str(v) for k, v in initial_observations.items()},
        active_hard_obligations=tuple(map(str, phase.get("active_hard_obligations", ()))),
        protected_refs=protected,
        authority_ceiling=str(
            manifest.get("authority_ceiling", "NON_AUTHORIZING_RESEARCH_CONTROL")
        ),
    )
    store.save_state(campaign_id, state.as_dict())
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
        **authority_false(),
    }


def run_campaign_cycle(
    workspace: ResearchWorkspace,
    manifest: Mapping[str, Any],
    *,
    auto_service_local: bool = True,
) -> dict[str, Any]:
    store = CampaignStore(workspace)
    state = initialize_campaign(workspace, manifest)
    phase = _phase(manifest, state.phase_id)
    if phase.get("terminal") is True:
        return {
            "schema": "ORION.ResearchCampaignOutcome.v1",
            "status": "TERMINAL",
            "campaign_id": state.campaign_id,
            "phase_id": state.phase_id,
            "state": state.as_dict(),
            "terminal": str(phase.get("terminal_name", "TERMINAL")),
            **authority_false(),
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
            **authority_false(),
        }
    selected_map = phase.get("selected_capabilities", {})
    capability_id = selected_map.get(decision.selected_id)
    if capability_id is None:
        return {
            "schema": "ORION.ResearchCampaignOutcome.v1",
            "status": "CAPABILITY_UNREGISTERED",
            "campaign_id": state.campaign_id,
            "phase_id": state.phase_id,
            "selected_id": decision.selected_id,
            "decision": decision.as_dict(),
            **authority_false(),
        }
    capability_id = str(capability_id)
    capability_spec = manifest["capabilities"][capability_id]
    if not isinstance(capability_spec, Mapping):
        raise TypeError("capability spec must be an object")
    _protect_unreleased_refs(
        workspace=workspace,
        protected_refs=state.protected_refs,
        capability_spec=capability_spec,
    )
    request_payload = dict(capability_spec["payload"])
    request_payload.update(
        {
            "campaign_id": state.campaign_id,
            "phase_id": state.phase_id,
            "selected_id": decision.selected_id,
            "selected_kind": decision.selected_kind,
            "campaign_state_digest": state.state_digest,
            "campaign_decision_digest": decision.decision_digest,
        }
    )
    request = workspace.get_or_create_request(
        capability=str(capability_spec["host_capability"]),
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
            **authority_false(),
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
            **authority_false(),
        }
    contract = capability_spec.get("result_contract", {})
    if not isinstance(contract, Mapping):
        raise TypeError("result_contract must be an object")
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
    next_phase = str(capability_spec["next_phase"])
    if next_phase not in manifest["phases"]:
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
    after = CampaignState.create(
        campaign_id=state.campaign_id,
        claim_id=state.claim_id,
        phase_id=next_phase,
        cycle_index=state.cycle_index + 1,
        manifest_digest=state.manifest_digest,
        observations=observations,
        active_hard_obligations=tuple(map(str, next_phase_spec.get("active_hard_obligations", ()))),
        protected_refs=_released_refs(state.protected_refs, capability_spec),
        history_digests=history,
        authority_ceiling=state.authority_ceiling,
    )
    if after.state_digest == state.state_digest:
        raise RuntimeError("campaign transition did not change state")
    store.save_state(state.campaign_id, after.as_dict())
    terminal = (
        str(next_phase_spec.get("terminal_name", "TERMINAL"))
        if next_phase_spec.get("terminal") is True
        else "CONTINUE"
    )
    seed = CampaignTransition(
        campaign_id=state.campaign_id,
        cycle_index=state.cycle_index,
        before_state_digest=state.state_digest,
        decision_digest=decision.decision_digest,
        request_digest=request.request_digest,
        result_digest=result.result_digest,
        after_state_digest=after.state_digest,
        terminal=terminal,
        transition_digest="",
    )
    transition = CampaignTransition(
        **{**seed.__dict__, "transition_digest": content_digest(seed.unsigned())}
    )
    transition.validate()
    store.save_cycle(state.campaign_id, transition.as_dict())
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
        **authority_false(),
    }


def run_campaign(
    workspace: ResearchWorkspace,
    manifest: Mapping[str, Any],
    *,
    max_cycles: int = 64,
    auto_service_local: bool = True,
) -> dict[str, Any]:
    if not isinstance(max_cycles, int) or isinstance(max_cycles, bool) or max_cycles < 1:
        raise ValueError("max_cycles must be a positive integer")
    outcomes = []
    for _ in range(max_cycles):
        outcome = run_campaign_cycle(
            workspace,
            manifest,
            auto_service_local=auto_service_local,
        )
        outcomes.append(outcome)
        if outcome["status"] != "ADVANCED":
            projection = {
                key: outcome[key]
                for key in ("phase_id", "terminal", "state", "error")
                if key in outcome
            }
            return {
                "schema": "ORION.ResearchCampaignRun.v1",
                "campaign_id": str(manifest["campaign_id"]),
                "status": outcome["status"],
                "cycles": outcomes,
                **projection,
                **authority_false(),
            }
    return {
        "schema": "ORION.ResearchCampaignRun.v1",
        "campaign_id": str(manifest["campaign_id"]),
        "status": "MAX_CYCLES_REACHED",
        "cycles": outcomes,
        **authority_false(),
    }


__all__ = ["initialize_campaign", "run_campaign", "run_campaign_cycle"]
