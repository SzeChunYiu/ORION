#!/usr/bin/env python3
"""Quantify the inherited theorem-block overrun that invalidated P10 v2."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
FRAMEWORK = PAPER.parent / "orion-learning-machine" / "framework"
sys.path.insert(0, str(FRAMEWORK))

from orion_learning_machine.adapters import lean_source


MANIFEST_PATH = HERE / "MATHLIB_CORPUS_V2_MANIFEST.json"
CORPUS_ROOT = HERE / "corpus" / "mathlib4_e72c1e277f31"
OUTPUT = PAPER / "results" / "PARSER_CONTAMINATION_AUDIT_V2.json"
TOP_LEVEL = re.compile(
    r"^(?:@\[[^\]]+\]\s*)*"
    r"(?:(?:noncomputable|private|protected|scoped|local|unsafe)\s+)*"
    r"(?P<command>theorem|lemma|def|abbrev|instance|example|structure|class|"
    r"inductive|opaque|axiom|namespace|section|end|open|attribute|macro|syntax|elab)\b"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    blocks = contaminated = boundaries = 0
    commands: Counter[str] = Counter()
    examples = []
    for item in manifest["files"]:
        path = CORPUS_ROOT / item["path"]
        for theorem in lean_source.parse_lean_source(
            path.read_text(encoding="utf-8"), item["path"]
        ):
            blocks += 1
            proof_start = lean_source._proof_start(list(theorem.raw_lines))
            if proof_start is None:
                raise AssertionError("trajectory has no proof opener")
            hits = []
            for block_line, line in enumerate(
                theorem.raw_lines[proof_start + 1 :], start=proof_start + 2
            ):
                match = TOP_LEVEL.match(line)
                if match:
                    hits.append(
                        {
                            "block_line": block_line,
                            "command": match.group("command"),
                            "text": line[:200],
                        }
                    )
                    commands[match.group("command")] += 1
            if hits:
                contaminated += 1
                boundaries += len(hits)
                if len(examples) < 25:
                    examples.append(
                        {
                            "source_id": item["path"],
                            "theorem_name": theorem.theorem_name,
                            "boundaries": hits[:5],
                        }
                    )

    result = {
        "schema": "P10ParserContaminationAudit.v2",
        "status": "INVALIDATES_MATHLIB_TRANSFER_V2",
        "parser_sha256": sha256(Path(lean_source.__file__)),
        "manifest_sha256": sha256(MANIFEST_PATH),
        "trajectories": blocks,
        "contaminated_trajectories": contaminated,
        "contaminated_fraction": contaminated / blocks,
        "intervening_top_level_boundaries": boundaries,
        "boundary_commands": dict(sorted(commands.items())),
        "examples": examples,
        "reason": "The inherited parser ended a theorem/lemma block only at the next theorem/lemma. Intervening top-level commands could contribute unrelated tactic-like text to the prior trajectory.",
        "required_repair": "End a projected declaration at the next recognized top-level command and rerun under an amended, frozen protocol.",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in [
        "status",
        "trajectories",
        "contaminated_trajectories",
        "contaminated_fraction",
        "intervening_top_level_boundaries",
    ]}, indent=2))


if __name__ == "__main__":
    main()
