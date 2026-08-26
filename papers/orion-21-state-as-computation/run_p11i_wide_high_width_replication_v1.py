"""P11I: wide fresh-seed replication of P11H's high-width regime."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
P11H_RUNNER = HERE / "run_p11h_pooled_sparsity_ladder_v1.py"

SCHEMA = "ORION.P11I.WideHighWidthReplication.v1"
PROTOCOL = "P11I_WIDE_HIGH_WIDTH_REPLICATION_PROTOCOL_V1.md"
SEEDS = (2026082241, 2026082242, 2026082243)
STATE_WIDTHS = (3, 7)
BANK_GEOMETRIES = ((14, 2), (14, 3), (19, 3))
LADDER = tuple((d, s, r) for r in STATE_WIDTHS for d, s in BANK_GEOMETRIES)

SUPPORTED = "P11I_HIGH_WIDTH_ADVANTAGE_REPLICATED_WIDE_PANEL"
NOT_REPLICATED = "P11I_HIGH_WIDTH_ADVANTAGE_NOT_REPLICATED"
PRECONDITION_FAILED = "P11I_INSTRUMENT_PRECONDITION_NOT_MET"
OUT = HERE / "P11I_WIDE_HIGH_WIDTH_REPLICATION_RESULT_V1.json"


def _p11h():
    spec = importlib.util.spec_from_file_location("p11h_frozen_runner_for_p11i", P11H_RUNNER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load the frozen P11H runner")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.LADDER = LADDER
    module.STATE_WIDTHS = STATE_WIDTHS
    module.BANK_GEOMETRIES = BANK_GEOMETRIES
    return module


def scientific_payload() -> dict[str, object]:
    p11h = _p11h()
    by_seed: list[dict[str, object]] = []
    high_width_units: list[dict[str, object]] = []
    low_width_controls: list[dict[str, object]] = []

    for seed in SEEDS:
        readings = p11h.measure_ladder(seed)
        by_seed.append({"seed": seed, "readings": readings})
        indexed = {tuple(row["cell"]): row for row in readings}
        for d, s in BANK_GEOMETRIES:
            low = indexed[(d, s, 3)]
            high = indexed[(d, s, 7)]
            high_width_units.append(
                {
                    "seed": seed,
                    "bank_geometry": [d, s],
                    "compiled_at_64": high["compiled_at_64"],
                    "pooled_best_below_256": high["pooled_best_below_gate"],
                    "delta64_vs_pool": high["delta64_vs_pool"],
                    "gates": {
                        "compiled_by_64": high["compiled_at_64"] >= p11h.TARGET_ACCURACY,
                        "pooled_below_target_before_256": (
                            high["pooled_best_below_gate"] < p11h.TARGET_ACCURACY
                        ),
                        "delta64_ge_0_20": (
                            high["delta64_vs_pool"] >= p11h.DELTA64_THRESHOLD
                        ),
                    },
                }
            )
            low_width_controls.append(
                {
                    "seed": seed,
                    "bank_geometry": [d, s],
                    "pooled_best_below_256": low["pooled_best_below_gate"],
                    "attack_live_at_low_width": (
                        low["pooled_best_below_gate"] >= p11h.TARGET_ACCURACY
                    ),
                }
            )

    no_laundering = all(
        not row["laundering_failures"]
        for seed_block in by_seed
        for row in seed_block["readings"]
    )
    attack_live = all(row["attack_live_at_low_width"] for row in low_width_controls)
    scientific_units_pass = all(
        all(unit["gates"].values()) for unit in high_width_units
    )
    instrument_gates = {
        "no_answer_laundering": no_laundering,
        "matched_low_width_attack_live": attack_live,
    }
    terminal = (
        PRECONDITION_FAILED
        if not all(instrument_gates.values())
        else SUPPORTED if scientific_units_pass else NOT_REPLICATED
    )
    return {
        "schema": "ORION.P11I.WideHighWidthReplication.ScientificPayload.v1",
        "protocol": PROTOCOL,
        "seeds": list(SEEDS),
        "state_widths": list(STATE_WIDTHS),
        "bank_geometries": [list(item) for item in BANK_GEOMETRIES],
        "ladder": [list(item) for item in LADDER],
        "independent_unit": "execution_seed_x_bank_geometry",
        "n_high_width_units": len(high_width_units),
        "n_matched_low_width_controls": len(low_width_controls),
        "n_queries_per_cell": p11h.N_QUERIES,
        "universal_pool": list(p11h.UNIVERSAL_POOL),
        "train_sizes": list(p11h.TRAIN_SIZES),
        "target_accuracy": p11h.TARGET_ACCURACY,
        "delta64_threshold": p11h.DELTA64_THRESHOLD,
        "by_seed": by_seed,
        "high_width_units": high_width_units,
        "low_width_controls": low_width_controls,
        "instrument_gates": instrument_gates,
        "scientific_units_pass": scientific_units_pass,
        "scientific_terminal": terminal,
    }


def canonical_text(payload: dict[str, object]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def write_once(path: Path) -> None:
    path.write_text(canonical_text(scientific_payload()), encoding="utf-8")


def authoritative_main() -> None:
    with tempfile.TemporaryDirectory(prefix="p11i-replay-") as directory:
        root = Path(directory)
        outputs = (root / "a.json", root / "b.json")
        runs = [
            subprocess.run(
                [sys.executable, str(Path(__file__).resolve()), "--once", str(path)],
                check=False,
                capture_output=True,
                text=True,
            )
            for path in outputs
        ]
        subprocesses_successful = all(run.returncode == 0 for run in runs)
        if not subprocesses_successful:
            raise SystemExit("P11I subprocess failed")
        payloads = [path.read_bytes() for path in outputs]
        digests = [hashlib.sha256(payload).hexdigest() for payload in payloads]
        byte_identical = payloads[0] == payloads[1] and digests[0] == digests[1]
        scientific = json.loads(payloads[0])
        terminal = scientific["scientific_terminal"] if byte_identical else PRECONDITION_FAILED
        result = {
            "schema": SCHEMA,
            "protocol": PROTOCOL,
            "scientific_payload": scientific,
            "replay": {
                "fresh_python_subprocesses": 2,
                "subprocesses_successful": subprocesses_successful,
                "byte_identical": byte_identical,
                "first_sha256": digests[0],
                "second_sha256": digests[1],
            },
            "terminal": terminal,
        }
        rendered = canonical_text(result)
        OUT.write_text(rendered, encoding="utf-8")
        print(
            json.dumps(
                {
                    "terminal": terminal,
                    "high_width_units": len(scientific["high_width_units"]),
                    "scientific_units_pass": scientific["scientific_units_pass"],
                    "replay": result["replay"],
                    "result_sha256": hashlib.sha256(rendered.encode()).hexdigest(),
                },
                indent=2,
                sort_keys=True,
            )
        )
        if terminal == PRECONDITION_FAILED:
            raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", type=Path)
    args = parser.parse_args()
    if args.once:
        write_once(args.once)
    else:
        authoritative_main()


if __name__ == "__main__":
    main()
