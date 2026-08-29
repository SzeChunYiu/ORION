#!/usr/bin/env python3
"""Pool the task-instruction vocabulary so no verb identifies a family.

The measured leak is not in the resource paths. `probe_corpus_leakage_v1.py`
finds that all eleven DECOMPOSITION prompts end in the *identical* sentence
"Diagnose the defect and specify the fix.", and all eleven EXECUTION prompts end
in a variant of "name the defect and give the repair" -- so `diagnose` and
`specify` each recover DECOMPOSITION 11/11 at precision 1.00, and `repair` and
`find` recover EXECUTION 11/11 at precision 0.92. Stripping the final sentence
removes five of the six leaking features, which is what makes this a
single-stage attribution rather than a diffuse one.

**Why pooling rather than flattening.** The two closers are synonyms: "diagnose
the defect and specify the fix" and "name the defect and give the repair" ask
for the same deliverable in disjoint words. The split carries no meaning, so
mixing the vocabularies costs the corpus nothing. Rewriting every case to one
sentence would instead erase a distinction other families genuinely have --
MEASUREMENT asks the solver to *report whether* something holds, which is not
the same request -- and that would change the task rather than remove the
shortcut. The standard is the audit's own: a failed-remedy case naming a remedy
artefact is legitimate; the *perfect* correlation is the defect.

Each phrasing is therefore assigned within each family, round-robin over sorted
case ids, so every phrasing appears in both families and no verb separates them.

Two invariants this script will not cross. It never touches `protected_gold`,
`task_family`, `adjudication_status` or `observable_resources` -- removing a
shortcut must not move an answer, and a repair that edited gold would be tuning
the outcome. And it rewrites only the terminal imperative clause: EXECUTION
prompts carry an endorsement prefix ("The working position: find the defect in
the migrated setup and repair it:") that marks them as negative controls, and
replacing the whole sentence would delete the framing `reframe_required` is
about.

Output goes to a separate tree. `protocol/cases/` is left untouched: it is the
evidence the leak was measured on, and a concurrent agent was rewording prompts
there throughout the original audit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

SHORT_FAMILY = {
    "hidden_decomposition_or_interface": "DECOMP",
    "execution_only_negative_control": "EXEC",
    "evidence_only_negative_control": "EVID",
}

#: Four ways to ask for the same deliverable: identify the defect, state the
#: remedy. Drawn from the wording the corpus already used in one family or the
#: other, so no new register is introduced.
INSTRUCTION_POOL = (
    "Diagnose the defect and specify the fix",
    "Name the defect and give the repair",
    "Identify the defect and state the correction",
    "Find the defect and describe the remedy",
)

#: `instrument` appears in six EVIDENCE prompts and nowhere else (precision 1.00,
#: recall 0.55). These endorse the measurement approach, so the noun is swapped
#: for synonyms rather than deleted; the endorsement is what makes the case a
#: control and must survive.
INSTRUMENT_SYNONYMS = ("instrument", "measure", "comparison", "test", "gauge", "check")

#: Families whose closer is rewritten. The other three vary their closing
#: sentence per case already and contribute no feature clearing the floors.
POOLED_FAMILIES = ("DECOMP", "EXEC")


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def split_sentences(prompt: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.?!])\s+", prompt.strip()) if s]


def rewrite_closer(prompt: str, replacement: str) -> str:
    """Swap the terminal imperative, keeping any endorsement prefix intact."""
    sentences = split_sentences(prompt)
    if not sentences:
        return prompt
    last = sentences[-1]
    trailing = "." if last.endswith(".") else ""
    body = last[: -len(trailing)] if trailing else last
    if ": " in body:
        head, _, _tail = body.rpartition(": ")
        new_last = f"{head}: {replacement[0].lower() + replacement[1:]}{trailing}"
    else:
        new_last = f"{replacement}{trailing}"
    sentences[-1] = new_last
    return " ".join(sentences)


def repair(source: Path, destination: Path) -> dict:
    before: dict[str, str] = {}
    payloads: dict[str, dict] = {}
    families: dict[str, str] = {}
    order: list[str] = []
    for split in ("pilot", "test"):
        for path in sorted((source / split).glob("*.json")):
            raw = path.read_text(encoding="utf-8")
            payload = json.loads(raw)
            key = f"{split}/{path.name}"
            before[key] = digest(raw)
            payloads[key] = payload
            families[key] = SHORT_FAMILY.get(payload["task_family"], "OTHER")
            order.append(key)

    edits = []
    for family in POOLED_FAMILIES:
        keys = sorted(k for k in order if families[k] == family)
        for index, key in enumerate(keys):
            payload = payloads[key]
            original = payload["public_prompt"]
            updated = rewrite_closer(original, INSTRUCTION_POOL[index % len(INSTRUCTION_POOL)])
            if updated != original:
                payload["public_prompt"] = updated
                edits.append({"case": payload["case_id"], "field": "public_prompt",
                              "kind": "pooled_instruction",
                              "from": split_sentences(original)[-1],
                              "to": split_sentences(updated)[-1]})

    evid = sorted(k for k in order if families[k] == "EVID"
                  and "instrument" in payloads[k]["public_prompt"].lower())
    for index, key in enumerate(evid):
        payload = payloads[key]
        synonym = INSTRUMENT_SYNONYMS[index % len(INSTRUMENT_SYNONYMS)]
        if synonym == "instrument":
            continue
        original = payload["public_prompt"]
        updated = re.sub(r"\binstrument\b", synonym, original)
        if updated != original:
            payload["public_prompt"] = updated
            edits.append({"case": payload["case_id"], "field": "public_prompt",
                          "kind": "instrument_synonym",
                          "from": "instrument", "to": synonym})

    guarded = ("protected_gold", "task_family", "adjudication_status",
               "observable_resources", "case_id", "budget_class")
    for key in order:
        split, name = key.split("/")
        target = destination / split
        target.mkdir(parents=True, exist_ok=True)
        (target / name).write_text(
            json.dumps(payloads[key], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Re-read both trees and confirm nothing outside `public_prompt` moved. The
    # check is on the written bytes, not on the objects in memory, so a bug in
    # serialisation cannot pass it.
    violations = []
    for key in order:
        split, name = key.split("/")
        original = json.loads((source / split / name).read_text(encoding="utf-8"))
        written = json.loads((destination / split / name).read_text(encoding="utf-8"))
        for field in guarded:
            if original.get(field) != written.get(field):
                violations.append(f"{key}: {field} changed")
        if set(original) != set(written):
            violations.append(f"{key}: key set changed")

    return {
        "cases": len(order),
        "edits": edits,
        "prompts_changed": len({e["case"] for e in edits}),
        "guarded_field_violations": violations,
        "source_digests": before,
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    arguments = parser.parse_args(argv)

    if not (arguments.source / "pilot").is_dir():
        print(f"CANNOT_CHECK: no pilot/ under {arguments.source}", file=sys.stderr)
        return 3
    result = repair(arguments.source, arguments.destination)
    if arguments.report:
        arguments.report.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                                    encoding="utf-8")
    print(f"repaired {result['prompts_changed']}/{result['cases']} prompts "
          f"({len(result['edits'])} edits) -> {arguments.destination}")
    if result["guarded_field_violations"]:
        for line in result["guarded_field_violations"][:10]:
            print(f"  VIOLATION: {line}")
        return 1
    print("  guarded fields (gold, family, resources, budget, id): unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
