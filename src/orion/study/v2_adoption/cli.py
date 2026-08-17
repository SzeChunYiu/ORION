from __future__ import annotations

import argparse
import json
from pathlib import Path

from .validate import evaluate_incremental_decision, load_protocols, validate_protocol, verify_digest_registry


def _read_json(path: str | Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m orion.study.v2_adoption")
    sub = parser.add_subparsers(dest="command", required=True)
    p_validate = sub.add_parser("validate")
    p_validate.add_argument("--programme", default="research/paper-programme-v2")
    p_eval = sub.add_parser("evaluate")
    p_eval.add_argument("--protocol", required=True)
    p_eval.add_argument("--v1", required=True)
    p_eval.add_argument("--v2", required=True)
    args = parser.parse_args(argv)
    if args.command == "validate":
        programme = Path(args.programme)
        protocols = load_protocols(programme / "protocols")
        registry = _read_json(programme / "PROTOCOL_DIGESTS_V1.json")
        verify_digest_registry(protocols, registry)
        print(json.dumps({"status": "PASS", "protocol_count": len(protocols), "protocol_ids": [p["protocol_id"] for p in protocols], "authority": "LOCAL_ENGINEERING_ONLY"}, sort_keys=True))
        return 0
    protocol = _read_json(args.protocol)
    validate_protocol(protocol)
    result = evaluate_incremental_decision(protocol, _read_json(args.v1), _read_json(args.v2))
    print(json.dumps(result, sort_keys=True))
    return 0
