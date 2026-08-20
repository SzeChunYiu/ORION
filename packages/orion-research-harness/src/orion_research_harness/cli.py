from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .campaign_protocol import CampaignState
from .campaign_runner import initialize_campaign, run_campaign
from .domains.registry import builtin_campaign_ids, load_builtin_campaign
from .local_tools import service_local_request
from .runner import run_problem
from .workspace import ResearchWorkspace


def _print(value: Any) -> None:
    print(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False))


def _load_json_argument(raw: str | None, path: str | None) -> Any:
    if raw is not None and path is not None:
        raise SystemExit("use only one of --json or --file")
    if path is not None:
        return json.loads(Path(path).read_text())
    if raw is None:
        return None
    return json.loads(raw)


def _handoff_prompt(workspace: ResearchWorkspace) -> str:
    pending = workspace.pending_requests()
    lines = [
        "# ORION Research Harness host handoff", "",
        f"Workspace: {workspace.root}", f"Project root: {workspace.project_root}",
        f"Session: {workspace.session_id}",
        f"Local process tools enabled: {workspace.allow_process_tools}", "",
        "You are the external host worker for canonical ORION. Do not bypass ORION's verification, responsibility, authority, or saturation rules.", "",
        "Workflow:", "1. Run `orion-harness pending <workspace>`.",
        "2. Service each capability using tools actually available in this session.",
        "3. Ingest the exact result with `orion-harness ingest ...`.",
        "4. Re-run the exact `solve` or `campaign-run` command until COMPLETE/TERMINAL/BLOCKED.", "",
        "Capability contracts:",
        "- LLM_COMPLETE: return {content, model_id?, response_id?}; content must obey the requested schema.",
        "- WEB_SEARCH: use current web search and source inspection; return {items:[{content,source_uri,item_id?,domain_ids?}]}.",
        "- VERIFY_EVIDENCE: independently verify support; return {passed,certificate_ids,reason}; fail closed.",
        "- FILE_READ/FILE_WRITE/FILE_LIST can be serviced locally with `service-local`.",
        "- SHELL/PYTHON require explicit workspace opt-in and are not OS-sandboxed; use only when the host has accepted that risk.",
        "- GITHUB or other custom capabilities: use the corresponding host tool and return structured JSON.", "",
        "Never fabricate a source, certificate, command result, or tool output. Preserve negative/CANNOT_CHECK results.", "",
        f"Pending requests: {len(pending)}",
    ]
    for request in pending:
        lines.append(f"- {request.request_id} :: {request.capability}")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="orion-harness")
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init"); init.add_argument("workspace"); init.add_argument("--project-root")
    init.add_argument("--allow-process-tools", action="store_true", help="opt in to local SHELL/PYTHON execution; subprocesses are not OS-sandboxed")
    add = sub.add_parser("problem-add"); add.add_argument("workspace"); add.add_argument("problem_id"); add.add_argument("question"); add.add_argument("--scope", default=""); add.add_argument("--domain", action="append", default=[]); add.add_argument("--criterion", action="append", default=[])
    problems = sub.add_parser("problems"); problems.add_argument("workspace")
    solve = sub.add_parser("solve"); solve.add_argument("workspace"); solve.add_argument("problem_id"); solve.add_argument("--max-iterations", type=int, default=3); solve.add_argument("--allow-provisional", action="store_true")
    pending = sub.add_parser("pending"); pending.add_argument("workspace")
    show = sub.add_parser("show-request"); show.add_argument("workspace"); show.add_argument("request_id")
    ingest = sub.add_parser("ingest"); ingest.add_argument("workspace"); ingest.add_argument("request_id"); ingest.add_argument("--json"); ingest.add_argument("--file"); ingest.add_argument("--executor", default="external-host"); ingest.add_argument("--error")
    tool_request = sub.add_parser("request-tool"); tool_request.add_argument("workspace"); tool_request.add_argument("capability"); tool_request.add_argument("--json", required=True)
    local = sub.add_parser("service-local"); local.add_argument("workspace"); local.add_argument("request_id", nargs="?")
    runs = sub.add_parser("runs"); runs.add_argument("workspace")
    show_run = sub.add_parser("show-run"); show_run.add_argument("workspace"); show_run.add_argument("run_id")
    handoff = sub.add_parser("handoff"); handoff.add_argument("workspace")
    builtins = sub.add_parser("campaign-builtins"); builtins.add_argument("workspace", nargs="?")
    start = sub.add_parser("campaign-start"); start.add_argument("workspace"); start.add_argument("campaign_id")
    campaigns = sub.add_parser("campaigns"); campaigns.add_argument("workspace")
    campaign_state = sub.add_parser("campaign-state"); campaign_state.add_argument("workspace"); campaign_state.add_argument("campaign_id")
    campaign_run = sub.add_parser("campaign-run"); campaign_run.add_argument("workspace"); campaign_run.add_argument("campaign_id"); campaign_run.add_argument("--max-cycles", type=int, default=32); campaign_run.add_argument("--no-auto-local", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "campaign-builtins":
        _print({"campaigns": list(builtin_campaign_ids())}); return 0
    if args.command == "init":
        workspace = ResearchWorkspace.initialize(args.workspace, project_root=args.project_root, allow_process_tools=args.allow_process_tools)
        _print({"status":"READY","workspace":str(workspace.root),"project_root":str(workspace.project_root),"session_id":workspace.session_id,"allow_process_tools":workspace.allow_process_tools}); return 0
    workspace = ResearchWorkspace.load(args.workspace)
    if args.command == "problem-add":
        path=workspace.save_problem(problem_id=args.problem_id,question=args.question,scope=args.scope,initial_domain_ids=args.domain,success_criteria=args.criterion); _print({"status":"SAVED","path":str(path),"problem_id":args.problem_id}); return 0
    if args.command == "problems": _print({"problems":list(workspace.problem_ids())}); return 0
    if args.command == "solve":
        outcome=run_problem(workspace,workspace.load_problem(args.problem_id),max_iterations=args.max_iterations,require_verified_answer=not args.allow_provisional); _print(outcome); return 2 if outcome["status"]=="PENDING_CAPABILITY" else 0
    if args.command == "pending": _print({"pending":[item.as_dict() for item in workspace.pending_requests()]}); return 0
    if args.command == "show-request": _print(workspace.load_request(args.request_id).as_dict()); return 0
    if args.command == "ingest":
        output=_load_json_argument(args.json,args.file); result=workspace.ingest_result(args.request_id,success=args.error is None,output=output,error=args.error or "",executor=args.executor); _print(result.as_dict()); return 0
    if args.command == "request-tool":
        payload=json.loads(args.json)
        if not isinstance(payload,dict): raise SystemExit("--json must decode to an object")
        request=workspace.get_or_create_request(capability=args.capability,payload=payload); _print(request.as_dict()); return 0
    if args.command == "service-local":
        ids=[args.request_id] if args.request_id else [item.request_id for item in workspace.pending_requests()]; results=[]
        for request_id in ids:
            try: result=service_local_request(workspace,request_id)
            except KeyError: continue
            results.append(result.as_dict())
        _print({"serviced":results}); return 0
    if args.command == "runs": _print({"runs":list(workspace.run_ids())}); return 0
    if args.command == "show-run": _print(workspace.load_run(args.run_id)); return 0
    if args.command == "handoff": print(_handoff_prompt(workspace)); return 0
    if args.command == "campaign-start":
        state=initialize_campaign(workspace,load_builtin_campaign(args.campaign_id)); _print({"status":"CAMPAIGN_READY","state":state.as_dict()}); return 0
    if args.command == "campaigns": _print({"campaigns":list(workspace.campaign_ids())}); return 0
    if args.command == "campaign-state":
        raw=workspace.load_latest_campaign_state(args.campaign_id)
        if raw is None: raise SystemExit(f"campaign has no state: {args.campaign_id}")
        _print(CampaignState.from_dict(raw).as_dict()); return 0
    if args.command == "campaign-run":
        outcome=run_campaign(workspace,workspace.load_campaign_manifest(args.campaign_id),max_cycles=args.max_cycles,auto_service_local=not args.no_auto_local); _print(outcome); status=outcome["status"]
        return 2 if status=="PENDING_CAPABILITY" else 1 if status in {"CAPABILITY_FAILED","CAPABILITY_UNREGISTERED","NO_SELECTED_ACTION","MAX_CYCLES_REACHED"} else 0
    raise AssertionError(args.command)


if __name__ == "__main__":
    sys.exit(main())
