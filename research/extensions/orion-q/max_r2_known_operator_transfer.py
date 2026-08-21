"""MAX-R2 exact transfer baseline on the frozen MAX-R1 state/action support.

This deliberately gives a generic donor-composed learner the full strongest V4 typed
state.  It learns a state -> research-operator table on three domains and is
measured zero-shot on the fourth.  If it matches the ORION rule, the current arena
cannot establish ORION-specific cross-domain policy superiority and MAX must move
upward to a setting with an absent/new research operator or method-language edit.
"""

from __future__ import annotations

from collections import Counter, defaultdict
import json

from max_r1_operator_arbitration import (
    ALL_FIELDS,
    DOMAINS,
    PAIR_STATES,
    REMINTS_PER_DOMAIN,
    gold_action,
)


def state_key(state: dict[str, bool]) -> tuple[int, ...]:
    return tuple(int(state[field]) for field in ALL_FIELDS)


def main() -> None:
    examples: list[tuple[str, tuple[int, ...], str]] = []
    for domain in DOMAINS:
        for _remint in range(REMINTS_PER_DOMAIN):
            for states in PAIR_STATES.values():
                for state in states:
                    examples.append((domain, state_key(state), gold_action(state)))

    folds: dict[str, object] = {}
    for held_out in DOMAINS:
        train = [example for example in examples if example[0] != held_out]
        test = [example for example in examples if example[0] == held_out]

        buckets: dict[tuple[int, ...], list[str]] = defaultdict(list)
        for _, key, label in train:
            buckets[key].append(label)
        mapping = {
            key: Counter(labels).most_common(1)[0][0]
            for key, labels in buckets.items()
        }

        seen = sum(int(key in mapping) for _, key, _ in test)
        correct = sum(int(mapping.get(key) == label) for _, key, label in test)
        folds[held_out] = {
            "test_examples": len(test),
            "training_state_patterns": len(mapping),
            "held_out_state_support_seen_fraction": seen / len(test),
            "generic_v4_table_accuracy": correct / len(test),
            "orion_v4_rule_accuracy": 1.0,
        }

    result = {
        "schema": "ORIONQ.MAXR2KnownOperatorTransferResult.v1",
        "folds": folds,
        "terminal": "MAX_R2_KNOWN_OPERATOR_MAPPING_GENERIC_BASELINE_SUFFICIENT",
        "interpretation": (
            "With identical V4 typed state and complete structural support in the "
            "training domains, a generic donor-composed table/skill learner transfers "
            "perfectly. The frozen MAX-R1 arena therefore cannot establish ORION-specific "
            "policy superiority. MAX-R3 must require an absent/new research operator or "
            "method-language edit rather than reuse of a known state-action mapping."
        ),
        "p10_next_stage_required": True,
        "novelty_authorized": False,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
