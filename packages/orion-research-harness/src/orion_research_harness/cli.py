from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

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
        "# ORION Research Harness host handoff",
        "",
        f"Workspace: {workspace.root}",
        f"Project root: {workspace.project_root}",
        f"Session: {workspace.session_id}",
        "",
        "You are the external host worker for canonical ORION. Do not bypass ORION's verification, responsibility, authority, or saturation rules.",
        "",
        "Workflow:",
        "1. Run `orion-harness pending <workspace>`.",
        "2. Service each capability using tools actually available in this session.",
        "3. Ingest the exact result with `orion-harness ingest ...`.",
        "4. Re-run `orion-harness solve <workspace> <problem-id>` until COMPLETE.",
        "",
        "Capability contracts:",
        "- LLM_COMPLETE: return {content, model_id?, response_id?}; content must obey the requested schema.",
        "- WEB_SEARCH: use current web search and source inspection; return {items:[{content,source_uri,item_id?,domain_ids?}]}.",
        "- VERIFY_EVIDENCE: independently verify support; return {passed,certificate_ids,reason}; fail closed.",
        "- FILE_READ/FILE_WRITE/FILE_LIST/SHELL/PYTHON: can be serviced locally with `service-local` when appropriate.",
        "- GITHUB or other custom capabilities: use the corresponding host tool and return structured JSON.",
        "",
        "Never fabricate a source, certificate, command result, or tool output. Preserve negative/CANNOT_CHECK results.",
        "",
        f"Pending requests: {len(pending)}",
    ]
    for request in pending:
        lines.append(f"- {request.request_id} :: {request.capability}")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="orion-harness")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init")
    init.add_argument("workspace")
    init.add_argument("--project-root")

    add = sub.add_parser("problem-add")
    add.add_argument("workspace")
    add.add_argument("problem_id")
    add.add_argument("question")
    add.add_argument("--scope", default="")
    add.add_argument("--domain", action="append", default=[])
    add.add_argument("--criterion", action="append", default=[])

    problems = sub.add_parser("problems")
    problems.add_argument("workspace")

    solve = sub.add_parser("solve")
    solve.add_argument("workspace")
    solve.add_argument("problem_id")
    solve.add_argument("--max-iterations", type=int, default=3)
    solve.add_argument("--allow-provisional", action="store_true")

    pending = sub.add_parser("pending")
    pending.add_argument("workspace")

    show = sub.add_parser("show-request")
    show.add_argument("workspace")
    show.add_argument("request_id")

    ingest = sub.add_parser("ingest")
    ingest.add_argument("workspace")
    ingest.add_argument("request_id")
    ingest.add_argument("--json")
    ingest.add_argument("--file")
    ingest.add_argument("--executor", default="external-host")
    ingest.add_argument("--error")

    tool_request = sub.add_parser("request-tool")
    tool_request.add_argument("workspace")
    tool_request.add_argument("capability")
    tool_request.add_argument("--json", required=True)

    local = sub.add_parser("service-local")
    local.add_argument("workspace")
    local.add_argument("request_id", nargs="?")

    runs = sub.add_parser("runs")
    runs.add_argument("workspace")

    show_run = sub.add_parser("show-run")
    show_run.add_argument("workspace")
    show_run.add_argument("run_id")

    handoff = sub.add_parser("handoff")
    handoff.add_argument("workspace")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "init":
        workspace = ResearchWorkspace.initialize(
            args.workspace,
            project_root=args.project_root,
        )
        _print(
            {
                "status": "READY",
                "workspace": str(workspace.root),
                "project_root": str(workspace.project_root),
                "session_id": workspace.session_id,
            }
        )
        return 0

    workspace = ResearchWorkspace.load(args.workspace)

    if args.command == "problem-add":
        path = workspace.save_problem(
            problem_id=args.problem_id,
            question=args.question,
            scope=args.scope,
            initial_domain_ids=args.domain,
            success_criteria=args.criterion,
        )
        _print({"status": "SAVED", "path": str(path), "problem_id": args.problem_id})
        return 0

    if args.command == "problems":
        _print({"problems": list(workspace.problem_ids())})
        return 0

    if args.command == "solve":
        outcome = run_problem(
            workspace,
            workspace.load_problem(args.problem_id),
            max_iterations=args.max_iterations,
            require_verified_answer=not args.allow_provisional,
        )
        _print(outcome)
        return 2 if outcome["status"] == "PENDING_CAPABILITY" else 0

    if args.command == "pending":
        _print({"pending": [item.as_dict() for item in workspace.pending_requests()]})
        return 0

    if args.command == "show-request":
        _print(workspace.load_request(args.request_id).as_dict())
        return 0

    if args.command == "ingest":
        output = _load_json_argument(args.json, args.file)
        success = args.error is None
        result = workspace.ingest_result(
            args.request_id,
            success=success,
            output=output,
            error=args.error or "",
            executor=args.executor,
        )
        _print(result.as_dict())
        return 0

    if args.command == "request-tool":
        payload = json.loads(args.json)
        if not isinstance(payload, dict):
            raise SystemExit("--json must decode to an object")
        request = workspace.get_or_create_request(
            capability=args.capability,
            payload=payload,
        )
        _print(request.as_dict())
        return 0

    if args.command == "service-local":
        ids = [args.request_id] if args.request_id else [
            item.request_id for item in workspace.pending_requests()
        ]
        results = []
        for request_id in ids:
            try:
                result = service_local_request(workspace, request_id)
            except KeyError:
                continue
            results.append(result.as_dict())
        _print({"serviced": results})
        return 0

    if args.command == "runs":
        _print({"runs": list(workspace.run_ids())})
        return 0

    if args.command == "show-run":
        _print(workspace.load_run(args.run_id))
        return 0

    if args.command == "handoff":
        print(_handoff_prompt(workspace))
        return 0

    raise AssertionError(args.command)


if __name__ == "__main__":
    sys.exit(main())
