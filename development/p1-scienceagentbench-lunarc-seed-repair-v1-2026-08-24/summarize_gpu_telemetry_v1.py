#!/usr/bin/env python3
"""Summarize sampled NVIDIA telemetry without treating it as billed cost."""

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--telemetry", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    rows = []
    with args.telemetry.open(newline="") as handle:
        for row in csv.reader(handle):
            if len(row) != 9:
                continue
            try:
                timestamp = None
                for fmt in ("%Y/%m/%d %H:%M:%S.%f", "%Y/%m/%d %H:%M:%S"):
                    try:
                        timestamp = datetime.strptime(row[0].strip(), fmt)
                        break
                    except ValueError:
                        pass
                if timestamp is None:
                    raise ValueError("unrecognized timestamp")
                rows.append({
                    "timestamp": timestamp,
                    "index": int(row[1]),
                    "uuid": row[2].strip(),
                    "name": row[3].strip(),
                    "driver_version": row[4].strip(),
                    "memory_used_mib": float(row[5]),
                    "memory_total_mib": float(row[6]),
                    "utilization_gpu_percent": float(row[7]),
                    "power_watts": float(row[8]),
                })
            except (ValueError, TypeError):
                continue
    if len(rows) < 2:
        raise SystemExit("fewer than two valid GPU telemetry samples")
    energy_joules = 0.0
    for left, right in zip(rows, rows[1:]):
        dt = (right["timestamp"] - left["timestamp"]).total_seconds()
        if 0 < dt < 5:
            energy_joules += ((left["power_watts"] + right["power_watts"]) / 2.0) * dt
    duration = (rows[-1]["timestamp"] - rows[0]["timestamp"]).total_seconds()
    receipt = {
        "schema": "orion.p1.scienceagentbench.lunarc-direct-seed-gpu-energy.v1",
        "status": "PASS_SAMPLED_TELEMETRY",
        "method": "trapezoidal integration of nvidia-smi power.draw samples; not a meter or billed-cost receipt",
        "sample_count": len(rows),
        "sample_interval_target_seconds": 0.2,
        "sampled_duration_seconds": duration,
        "gpu_seconds_sampled": duration,
        "energy_joules_estimate": energy_joules,
        "energy_wh_estimate": energy_joules / 3600.0,
        "max_memory_used_mib": max(row["memory_used_mib"] for row in rows),
        "memory_total_mib": rows[0]["memory_total_mib"],
        "max_utilization_gpu_percent": max(row["utilization_gpu_percent"] for row in rows),
        "mean_power_watts": sum(row["power_watts"] for row in rows) / len(rows),
        "max_power_watts": max(row["power_watts"] for row in rows),
        "gpu_uuid": rows[0]["uuid"],
        "gpu_name": rows[0]["name"],
        "driver_version": rows[0]["driver_version"],
        "billed_usd": None,
        "scientific_authority_delta": "NONE",
    }
    args.receipt.write_text(json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n")
    print(json.dumps({"samples": len(rows), "status": receipt["status"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

