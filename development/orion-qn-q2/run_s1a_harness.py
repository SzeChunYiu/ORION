from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace


WORKSPACE = Path(".orion-qn-vs1-s1a")
CAMPAIGN_ARTIFACT = Path("artifacts/orion-qn-vs1-s1a-campaign.json")
ARTIFACT = Path("artifacts/orion-qn-vs1-s1a-harness.json")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    if WORKSPACE.exists():
        shutil.rmtree(WORKSPACE)
    workspace = ResearchWorkspace.initialize(
        WORKSPACE,
        project_root=".",
        allow_process_tools=True,
    )
    code = """
import hashlib
import json
from pathlib import Path
from orion.quantum.vs1 import run_s1a_campaign_json

path = Path('artifacts/orion-qn-vs1-s1a-campaign.json')
path.parent.mkdir(parents=True, exist_ok=True)
payload = run_s1a_campaign_json().encode('utf-8')
path.write_bytes(payload)
print(json.dumps({
    'campaign_path': str(path),
    'campaign_sha256': hashlib.sha256(payload).hexdigest(),
    'campaign_bytes': len(payload),
}, sort_keys=True))
""".strip()
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
        raise RuntimeError("harness process produced no campaign binding metadata")
    binding = json.loads(stdout)
    if binding.get("campaign_path") != str(CAMPAIGN_ARTIFACT):
        raise RuntimeError("harness campaign path differs from frozen artifact path")

    campaign_bytes = CAMPAIGN_ARTIFACT.read_bytes()
    actual_sha256 = _sha256(campaign_bytes)
    if binding.get("campaign_sha256") != actual_sha256:
        raise RuntimeError("harness-reported campaign hash does not match actual campaign bytes")
    if binding.get("campaign_bytes") != len(campaign_bytes):
        raise RuntimeError("harness-reported campaign size does not match actual campaign bytes")
    campaign = json.loads(campaign_bytes)

    envelope = {
        "schema": "ORION.QN.VS1.S1A.HarnessEnvelope.v2",
        "request": request.as_dict(),
        "result": result.as_dict(),
        "campaign_artifact": {
            "path": str(CAMPAIGN_ARTIFACT),
            "sha256": actual_sha256,
            "bytes": len(campaign_bytes),
        },
        "campaign": campaign,
        "authority_note": (
            "Harness request/result digests and the independently recomputed campaign file hash "
            "bind execution provenance; they are not signatures or independent scientific authority."
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
                "campaign_artifact": str(CAMPAIGN_ARTIFACT),
                "campaign_sha256": actual_sha256,
                "campaign_bytes": len(campaign_bytes),
                "request_id": request.request_id,
                "request_digest": request.request_digest,
                "result_digest": result.result_digest,
                "case_count": len(campaign.get("cases", [])),
                "fixture_cases_used_for_advantage": campaign.get(
                    "fixture_cases_used_for_advantage"
                ),
                "advantage_adjudication_source": campaign.get(
                    "advantage_adjudication_source"
                ),
                "size_terminals": [
                    {
                        "n": item["n_qubits"],
                        "query_model_terminal": item["query_model_terminal"],
                        "ordinary_input_terminal": item["ordinary_input_terminal"],
                        "q_budget": item["quantum_query_budget"],
                        "classical_matching_budget": item[
                            "classical_matching_query_budget"
                        ],
                        "classical_matching_expected": item[
                            "classical_matching_expected_queries"
                        ],
                        "fixture_mean_q_diagnostic": item[
                            "mean_fixture_quantum_oracle_calls"
                        ],
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
