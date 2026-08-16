from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Mapping

from .canonical import canonical_json
from .manifest import load_and_validate_manifest
from .models import problem_signature_from_payload
from .portfolio import build_portfolio
from .registry import TransferRegistry


def _load_object(path: str) -> dict[str, object]:
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _write(payload: Mapping[str, object], output: str | None) -> None:
    text = canonical_json(payload) + "\n"
    if output is None:
        print(text, end="")
    else:
        Path(output).write_text(text, encoding="utf-8")


def run_portfolio(args: argparse.Namespace) -> int:
    registry = TransferRegistry.load(args.catalog)
    target_payload = _load_object(args.target)
    target = problem_signature_from_payload(target_payload)
    evidence = _load_object(args.evidence)
    if not all(isinstance(value, Mapping) for value in evidence.values()):
        raise ValueError("evidence values must be objects")
    receipt = build_portfolio(
        target,
        registry,
        evidence,  # type: ignore[arg-type]
        min_independent_domains=args.min_independent_domains,
    )
    receipt.verify()
    _write(receipt.to_payload(), args.output)
    return 0


def run_validate_manifest(args: argparse.Namespace) -> int:
    payload, digest = load_and_validate_manifest(args.manifest)
    _write({"manifest": payload, "manifest_digest": digest, "valid": True}, args.output)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m orion.transfer.v2")
    subparsers = parser.add_subparsers(dest="command", required=True)

    portfolio = subparsers.add_parser("portfolio", help="build a fail-closed transfer portfolio receipt")
    portfolio.add_argument("--catalog", required=True)
    portfolio.add_argument("--target", required=True)
    portfolio.add_argument("--evidence", required=True)
    portfolio.add_argument("--min-independent-domains", type=int, default=1)
    portfolio.add_argument("--output")
    portfolio.set_defaults(func=run_portfolio)

    manifest = subparsers.add_parser("validate-manifest", help="validate an additive paper V2 manifest")
    manifest.add_argument("--manifest", required=True)
    manifest.add_argument("--output")
    manifest.set_defaults(func=run_validate_manifest)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))
