from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from orion.quantum.verification import reconstruct_s1a_campaign
from orion_research_harness.protocol import CapabilityRequest, CapabilityResult


DEFAULT_INPUT = Path("artifacts/orion-qn-vs1-s1a-harness.json")
DEFAULT_OUTPUT = Path("artifacts/orion-qn-vs1-s1a-verification.json")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    input_path = Path(args[0]) if args else DEFAULT_INPUT
    output_path = Path(args[1]) if len(args) > 1 else DEFAULT_OUTPUT
    envelope = json.loads(input_path.read_text(encoding="utf-8"))

    if envelope.get("schema") != "ORION.QN.VS1.S1A.HarnessEnvelope.v2":
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

    campaign_binding = envelope.get("campaign_artifact")
    standalone_campaign: dict | None = None
    if not isinstance(campaign_binding, dict):
        errors.append("standalone campaign artifact binding missing or malformed")
    else:
        path_raw = campaign_binding.get("path")
        if not isinstance(path_raw, str) or not path_raw:
            errors.append("campaign artifact path missing or malformed")
        else:
            campaign_path = Path(path_raw)
            if not campaign_path.is_file():
                errors.append("bound standalone campaign artifact does not exist")
            else:
                campaign_bytes = campaign_path.read_bytes()
                observed_sha256 = _sha256(campaign_bytes)
                if campaign_binding.get("sha256") != observed_sha256:
                    errors.append("standalone campaign SHA-256 does not match envelope binding")
                if campaign_binding.get("bytes") != len(campaign_bytes):
                    errors.append("standalone campaign byte count does not match envelope binding")
                try:
                    parsed = json.loads(campaign_bytes)
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    errors.append(f"standalone campaign JSON invalid: {type(exc).__name__}: {exc}")
                else:
                    if not isinstance(parsed, dict):
                        errors.append("standalone campaign JSON is not an object")
                    else:
                        standalone_campaign = parsed

    envelope_campaign = envelope.get("campaign")
    if not isinstance(envelope_campaign, dict):
        errors.append("envelope campaign payload missing or malformed")
    if standalone_campaign is not None and isinstance(envelope_campaign, dict):
        if standalone_campaign != envelope_campaign:
            errors.append("standalone campaign content differs from envelope campaign copy")

    campaign = standalone_campaign if standalone_campaign is not None else envelope_campaign
    if not isinstance(campaign, dict):
        reconstruction = {
            "schema": "ORION.QN.S1ACampaignReconstruction.v4",
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
        "schema": "ORION.QN.VS1.S1A.HarnessVerification.v2",
        "valid": not errors,
        "errors": errors,
        "request_id": request.request_id,
        "request_digest": request.request_digest,
        "result_digest": result.result_digest,
        "executor": result.executor,
        "sandboxed": (
            result.output.get("sandboxed") if isinstance(result.output, dict) else None
        ),
        "campaign_artifact": campaign_binding,
        "campaign_reconstruction": reconstruction,
        "authority_note": (
            "This verifier independently re-reads and hashes the standalone campaign bytes, "
            "checks equality with the envelope copy, then runs a separate scientific "
            "reconstruction path. It is not independent peer review or publication authority."
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
