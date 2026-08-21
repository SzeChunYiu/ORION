from __future__ import annotations

import json
import shutil
from pathlib import Path

from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace


WORKSPACE = Path(".orion-qn-vs1-s1a")
ARTIFACT = Path("artifacts/orion-qn-vs1-s1a-harness.json")


def main() -> int:
    if WORKSPACE.exists():
        shutil.rmtree(WORKSPACE)
    workspace = ResearchWorkspace.initialize(
        WORKSPACE,
        project_root=".",
        allow_process_tools=True,
    )
    code = (
        "from orion.quantum.vs1 import run_s1a_campaign_json; "
        "print(run_s1a_campaign_json())"
    )
    request = workspace.get_or_create_request(
        capability="PYTHON",
        payload={"code": code, "cwd": ".", "timeout": 120},
    )
    result = service_local_request(workspace, request.request_id)
    if not result.success:
        raise RuntimeError(f"harness S1A process failed: {result.error}")
    if not isinstance(result.output, dict):
        raise TypeError("harness PYTHON output must be an object")
    if result.output.get("returncode") != 0:
        raise RuntimeError(f"S1A process returncode: {result.output.get('returncode')}")
    if result.output.get("sandboxed") is not False:
        raise RuntimeError("harness process receipt must explicitly record sandboxed=false")
    stdout = result.output.get("stdout")
    if not isinstance(stdout, str) or not stdout.strip():
        raise RuntimeError("harness process produced no campaign JSON")
    campaign = json.loads(stdout)

    envelope = {
        "schema": "ORION.QN.VS1.S1A.HarnessEnvelope.v1",
        "request": request.as_dict(),
        "result": result.as_dict(),
        "campaign": campaign,
        "authority_note": (
            "Harness digests bind request/result content but are not signatures or independent "
            "scientific authority."
        ),
    }
    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT.write_text(
        json.dumps(envelope, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "artifact": str(ARTIFACT),
                "request_id": request.request_id,
                "request_digest": request.request_digest,
                "result_digest": result.result_digest,
                "case_count": len(campaign.get("cases", [])),
                "size_terminals": [
                    {
                        "n": item["n_qubits"],
                        "terminal": item["terminal"],
                        "mean_q": item["mean_quantum_oracle_calls"],
                        "mean_c1": item["mean_classical_ordered_calls"],
                        "mean_c2": item["mean_classical_random_calls"],
                    }
                    for item in campaign.get("size_summaries", [])
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
