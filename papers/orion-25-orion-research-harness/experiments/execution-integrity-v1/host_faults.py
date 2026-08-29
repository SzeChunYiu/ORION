#!/usr/bin/env python3
"""ORION-25 host/process fault injection — the in-runner class.

The artifact-corruption class is covered by fault_inject.py. This covers faults that
happen to the PROCESS and the HOST while the runner executes, which PROTOCOL.json lists
as needing a harness that did not exist.

Every fault is applied externally: the frozen runner and checker are unmodified.

The endpoint is FALSE PROMOTION AT PIPELINE LEVEL: after a host/process fault, can
anything downstream still be led to treat the run as successful?

  0 = every fault left a detectable state
  2 = a fault produced an undetectably-successful-looking state
  3 = could not check
"""
import json
import os
import pathlib
import signal
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
RUNNER = HERE / "run_attestation_composition_v2.py"
CHECKER = HERE / "check_attestation_composition_independent_v2.py"
OUT = HERE / "p15_attestation_composition_v2.json"
GREEN = "P15_ATTESTATION_COMPOSITION_V2_SECOND_CHECKER_GREEN"


def run_checker():
    r = subprocess.run([sys.executable, str(CHECKER)], capture_output=True, text=True, cwd=HERE)
    try:
        return r.returncode, json.loads(r.stdout).get("terminal", "")
    except Exception:
        return r.returncode, (GREEN if GREEN in r.stdout else "")


def produce(dest: pathlib.Path):
    """Run the frozen runner to completion, writing stdout to dest."""
    with dest.open("wb") as fh:
        p = subprocess.run([sys.executable, str(RUNNER)], stdout=fh,
                           stderr=subprocess.PIPE, cwd=HERE)
    return p.returncode


def main() -> int:
    if not (RUNNER.exists() and CHECKER.exists()):
        print(json.dumps({"terminal": "CANNOT_CHECK_SETUP_INCOMPLETE"})); return 3

    baseline = HERE / "_baseline.json"
    if produce(baseline) != 0:
        print(json.dumps({"terminal": "CANNOT_CHECK_BASELINE_RUN_FAILED"})); return 3
    good = baseline.read_bytes()
    OUT.write_bytes(good)
    rc0, t0 = run_checker()
    if t0 != GREEN:
        print(json.dumps({"terminal": "CANNOT_CHECK_BASELINE_NOT_GREEN", "observed": t0})); return 3

    results = []

    # G1 -- the stale-artifact fault. A previous good result is on disk; this run dies
    # before it can overwrite it. Does anything downstream notice the artifact is not
    # from this run?
    OUT.write_bytes(good)
    stale_before = OUT.read_bytes()
    proc = subprocess.Popen([sys.executable, str(RUNNER)],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=HERE)
    time.sleep(0.02)
    proc.send_signal(signal.SIGKILL)
    proc.wait()
    rc, term = run_checker()
    results.append({
        "fault": "G1_RUNNER_SIGKILL_WITH_STALE_ARTIFACT_PRESENT",
        "runner_exit": proc.returncode,
        "artifact_unchanged": OUT.read_bytes() == stale_before,
        "checker_rc": rc, "checker_terminal": term or "(none)",
        "checker_accepts_stale": term == GREEN,
        "tests": ("runner killed mid-execution while a previous good artifact sits on "
                  "disk; does the checker distinguish 'this run succeeded' from "
                  "'an older run succeeded'?"),
    })

    # G2 -- output path not writable
    OUT.write_bytes(good)
    ro = HERE / "_ro_out.json"
    ro.write_bytes(b"{}")
    os.chmod(ro, 0o444)
    try:
        rc_w = produce(ro)
        wrote = ro.stat().st_size > 2
    except PermissionError:
        rc_w, wrote = -1, False
    finally:
        os.chmod(ro, 0o644); ro.unlink(missing_ok=True)
    results.append({"fault": "G2_OUTPUT_PATH_READ_ONLY", "runner_exit": rc_w,
                    "silently_produced_output": bool(wrote),
                    "failed_loudly": rc_w != 0 or not wrote,
                    "tests": "read-only destination; does the runner fail loudly or silently produce nothing?"})

    # G3 -- output directory removed before the write
    OUT.write_bytes(good)
    missing = HERE / "_gone" / "out.json"
    try:
        rc_m = produce(missing)
    except (FileNotFoundError, NotADirectoryError):
        rc_m = -1
    results.append({"fault": "G3_OUTPUT_DIRECTORY_ABSENT", "runner_exit": rc_m,
                    "failed_loudly": rc_m != 0,
                    "tests": "destination directory does not exist"})

    # G4 -- SIGTERM instead of SIGKILL (graceful signal, same question as G1)
    OUT.write_bytes(good)
    before4 = OUT.read_bytes()
    p4 = subprocess.Popen([sys.executable, str(RUNNER)],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=HERE)
    time.sleep(0.02)
    p4.terminate(); p4.wait()
    rc4, t4 = run_checker()
    results.append({"fault": "G4_RUNNER_SIGTERM_WITH_STALE_ARTIFACT_PRESENT",
                    "runner_exit": p4.returncode,
                    "artifact_unchanged": OUT.read_bytes() == before4,
                    "checker_rc": rc4, "checker_terminal": t4 or "(none)",
                    "checker_accepts_stale": t4 == GREEN,
                    "tests": "graceful termination mid-execution with a stale artifact present"})

    OUT.write_bytes(good)
    baseline.unlink(missing_ok=True)

    stale_accepted = [r for r in results if r.get("checker_accepts_stale")]
    print(json.dumps({
        "schema": "orion.orion25.host-process-faults.v1",
        "successor_id": "ORION25.EXECUTION_INTEGRITY.v1",
        "box": "production-like host/process fault injection (in-runner class)",
        "authority": "MEASUREMENT_ONLY",
        "scientific_authority_delta": "NONE",
        "faults": len(results),
        "checker_accepted_stale_artifact_count": len(stale_accepted),
        "results": results,
        "finding": ("The checker verifies an ARTIFACT, not a RUN. It carries no binding "
                    "to the process that produced it, so after a mid-run kill it "
                    "re-certifies a previous good artifact as green. That is correct "
                    "behaviour for an artifact verifier and a real gap for a pipeline "
                    "that treats a green checker as evidence that THIS run succeeded. "
                    "Liveness must be established by the orchestrator, not inferred from "
                    "the checker."
                    if stale_accepted else
                    "No fault left a state a downstream consumer could mistake for success."),
        "terminal": ("STALE_ARTIFACT_ACCEPTED__LIVENESS_NOT_ATTESTED"
                     if stale_accepted else "ALL_HOST_FAULTS_DETECTABLE"),
    }, indent=2, sort_keys=True))
    return 2 if stale_accepted else 0


if __name__ == "__main__":
    raise SystemExit(main())
