from __future__ import annotations

import json
import sys
from pathlib import Path

from orion.quantum.verification import reconstruct_s1a_campaign
from orion_research_harness.protocol import CapabilityRequest, CapabilityResult


DEFAULT_INPUT = Path("artifacts/orion-qn-vs1-s1a-harness.json")
DEFAULT_OUTPUT = Path("artifacts/orion-qn-vs1-s1a-verification.json")


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    input_path = Path(args[0]) if args else DEFAULT_INPUT
    output_path = Path(args[1]) if len(args) > 1 else DEFAULT_OUTPUT
    envelope = json.loads(input_path.read_text(encoding="utf-8"))

    if envelope.get("schema") != "ORION.QN.VS1.S1A.HarnessEnvelope.v1":
        raise ValueError("unsupported S1A harness envelope schema")
    request = CapabilityRequest.from_dict(envelope["request"])
    result = CapabilityResult.from_dict(envelope["result"])
    result.validate(request)
    errors: list[str] = []

    if request.capability != "PYTHON":
        errors.append("S1A harness request is not a PYTHON capability")
    if result.executor != "orion-harness-local":
        errors.append("S1A process was not serviced by the local harness executor")
    if not result.success:
        errors.append("S1A harness result is unsuccessful")
    if not isinstance(result.output, dict):
        errors.append("S1A harness process output is not an object")
    else:
        if result.output.get("returncode") != 0:
            errors.append("S1A harness process returncode is nonzero")
        if result.output.get("sandboxed") is not False:
            errors.append("S1A harness process did not preserve sandboxed=false fact")

    campaign = envelope.get("campaign")
    if not isinstance(campaign, dict):
        errors.append("campaign payload missing or malformed")
        reconstruction = {
            "schema": "ORION.QN.S1ACampaignReconstruction.v1",
            "valid": False,
            "errors": ["campaign unavailable"],
        }
    else:
        reconstruction = reconstruct_s1a_campaign(campaign)
        if not reconstruction["valid"]:
            errors.extend(
                f"P4 reconstruction: {item}" for item in reconstruction.get("errors", [])
            )

    verification = {
        "schema": "ORION.QN.VS1.S1A.HarnessVerification.v1",
        "valid": not errors,
        "errors": errors,
        "request_id": request.request_id,
        "request_digest": request.request_digest,
        "result_digest": result.result_digest,
        "executor": result.executor,
        "sandboxed": (
            result.output.get("sandboxed") if isinstance(result.output, dict) else None
        ),
        "campaign_reconstruction": reconstruction,
        "authority_note": (
            "This is an independent code path over serialized artifacts, not independent peer "
            "review or publication authority."
        ),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(verification, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(verification, indent=2, sort_keys=True))
    return 0 if verification["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
