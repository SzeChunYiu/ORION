"""Live LLM evaluator for the ORION-P4 protected authority campaign.

Calls GLM-5.2 (via cmkey.cn) with only candidate_visible content per manifest
case, producing semantic-support, claim-correctness, and source-ownership
judgments that replace protected_gold in the guarded pipeline.

The API key is read from the CMKEY_API_KEY environment variable.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class LiveJudgment:
    """Judgments produced by a live model call from candidate_visible content only."""

    semantic_support: str  # SUPPORTED | CONTRADICTED | INSUFFICIENT
    claim_correct: bool | None
    source_owner_correct: bool | None
    contaminated: bool  # always False for a live model; propagates from manifest
    prompt_tokens: int
    completion_tokens: int
    latency_seconds: float


# ---------------------------------------------------------------------------
# API configuration
# ---------------------------------------------------------------------------

BASE_URL = "https://api2.cmkey.cn/v1"
MODEL = "glm-5.2"

JUDGMENT_PROMPT = """You are a rigorous scientific claim verifier. Given a claim, a cited source, and evidence text, produce three judgments:

1. **semantic_support**: Does the evidence *directly support* the claim?
   - "SUPPORTED" — the evidence clearly supports the claim
   - "CONTRADICTED" — the evidence directly contradicts the claim
   - "INSUFFICIENT" — the evidence is ambiguous, weak, irrelevant, or does not clearly support or contradict the claim

2. **claim_correct**: Regardless of the evidence, is the claim itself factually correct based on established scientific knowledge? (true / false / null if uncertain)

3. **source_owner_correct**: Does the evidence text actually come from the cited source, or is the evidence about a different paper/study than the one cited? (true / false / null if uncertain)

Respond with ONLY a valid json object (no markdown, no explanation):
{"semantic_support": "SUPPORTED|CONTRADICTED|INSUFFICIENT", "claim_correct": true|false|null, "source_owner_correct": true|false|null}"""


def _api_key() -> str:
    key = os.environ.get("CMKEY_API_KEY")
    if not key:
        raise RuntimeError(
            "CMKEY_API_KEY environment variable not set. "
            "Set it to your cmkey.cn API key before running the live campaign."
        )
    return key


def _build_messages(claim_text: str, evidence_text: str, source_text: str) -> list[dict[str, Any]]:
    return [
        {
            "role": "system",
            "content": JUDGMENT_PROMPT,
        },
        {
            "role": "user",
            "content": (
                f"Claim: {claim_text}\n\n"
                f"Cited source: {source_text}\n\n"
                f"Evidence: {evidence_text}"
            ),
        },
    ]


def _parse_judgment(raw: str) -> dict[str, Any]:
    """Parse the model's JSON response, tolerating markdown fences."""
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        # Strip markdown code fences
        cleaned = cleaned.strip("`")
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()
    return json.loads(cleaned)


def _validate_judgment(parsed: dict[str, Any]) -> dict[str, Any]:
    """Validate that the parsed judgment has the expected fields."""
    support = parsed.get("semantic_support", "")
    if support not in ("SUPPORTED", "CONTRADICTED", "INSUFFICIENT"):
        raise ValueError(f"Invalid semantic_support: {support!r}")
    cc = parsed.get("claim_correct")
    if cc not in (True, False, None):
        raise ValueError(f"Invalid claim_correct: {cc!r}")
    soc = parsed.get("source_owner_correct")
    if soc not in (True, False, None):
        raise ValueError(f"Invalid source_owner_correct: {soc!r}")
    return {
        "semantic_support": support,
        "claim_correct": cc,
        "source_owner_correct": soc,
    }


def _post_chat_completion(
    body: dict[str, Any],
    key: str,
    *,
    timeout: float = 60.0,
) -> dict[str, Any]:
    """POST a chat-completions request to cmkey.cn using only the stdlib.

    Uses urllib.request directly (the repo deliberately keeps dependencies
    minimal); the body is JSON, the response is JSON, and error surfaces as
    HTTPError with the provider's status text in it.
    """
    req = urllib.request.Request(
        f"{BASE_URL}/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} from {BASE_URL}: {detail[:400]}") from exc
    if not raw.strip():
        raise RuntimeError("Empty response body from provider (retryable)")
    return json.loads(raw)


def call_glm_judge(
    claim_text: str,
    evidence_text: str,
    source_text: str,
    *,
    timeout: float = 60.0,
    retries: int = 2,
) -> LiveJudgment:
    """Call GLM-5.2 via cmkey.cn to produce judgments for one case.

    Returns a LiveJudgment dataclass containing the three judgments plus
    token usage and latency.
    """
    key = _api_key()
    messages = _build_messages(claim_text, evidence_text, source_text)
    body = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.0,
        "max_tokens": 4096,
    }

    last_error: Exception | None = None
    for attempt in range(1 + retries):
        t0 = time.monotonic()
        try:
            data = _post_chat_completion(body, key, timeout=timeout)
        except Exception as exc:
            last_error = exc
            time.sleep(1.0 * (attempt + 1))
            continue

        latency = time.monotonic() - t0
        usage = data.get("usage", {}) or {}
        prompt_tokens = usage.get("prompt_tokens", 0) or 0
        completion_tokens = usage.get("completion_tokens", 0) or 0

        raw_content = data["choices"][0]["message"]["content"]
        try:
            parsed = _parse_judgment(raw_content)
            validated = _validate_judgment(parsed)
        except (json.JSONDecodeError, ValueError, KeyError) as exc:
            last_error = exc
            continue

        return LiveJudgment(
            semantic_support=validated["semantic_support"],
            claim_correct=validated["claim_correct"],
            source_owner_correct=validated["source_owner_correct"],
            contaminated=False,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            latency_seconds=latency,
        )

    raise RuntimeError(
        f"All {1 + retries} attempts to call GLM-5.2 failed. "
        f"Last error: {last_error}"
    )


def judge_case(
    attack_case: dict[str, Any],
    *,
    timeout: float = 60.0,
    retries: int = 2,
) -> LiveJudgment:
    """Produce a LiveJudgment for a single manifest attack case.

    Extracts only candidate_visible content (claim_text, evidence_text, source_text)
    and calls the live model. The protected_gold is *not* passed to the model.
    """
    cv = attack_case.get("candidate_visible", {})
    return call_glm_judge(
        claim_text=cv.get("claim_text", ""),
        evidence_text=cv.get("evidence_text", ""),
        source_text=cv.get("source_text", ""),
        timeout=timeout,
        retries=retries,
    )


def enrich_case_with_live_judgments(
    attack_case: dict[str, Any],
    judgment: LiveJudgment,
) -> dict[str, Any]:
    """Return a copy of the attack case with protected_gold replaced by live judgments.

    Preserves all structural fields (case_id, attack_family, evidence_objects,
    candidate_visible, etc.) but replaces the protected_gold values with
    the model's judgments. The original protected_gold is kept under
    ``protected_gold_original`` for audit.
    """
    case = dict(attack_case)
    pg = case.get("protected_gold", {})

    case["protected_gold_original"] = dict(pg)
    case["protected_gold"] = {
        "claim_correct": judgment.claim_correct,
        "source_owner_correct": judgment.source_owner_correct,
        "semantic_support": judgment.semantic_support,
        "contaminated": pg.get("contaminated", False),
        "expected_authority_terminal": pg.get("expected_authority_terminal", "CANNOT_CHECK"),
    }
    return case


def run_judgments_on_manifest(
    manifest_path: str,
    *,
    timeout: float = 60.0,
    retries: int = 2,
) -> list[tuple[dict[str, Any], LiveJudgment]]:
    """Run GLM-5.2 judgments on every case in a JSONL manifest.

    Returns a list of (enriched_case, judgment) tuples.
    """
    import json
    from pathlib import Path

    cases = []
    for line in Path(manifest_path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        cases.append(json.loads(line))

    results: list[tuple[dict[str, Any], LiveJudgment]] = []
    for idx, case in enumerate(cases):
        cid = case.get("case_id", f"case-{idx}")
        print(f"[{idx + 1}/{len(cases)}] {cid} ... ", end="", flush=True)
        judgment = judge_case(case, timeout=timeout, retries=retries)
        enriched = enrich_case_with_live_judgments(case, judgment)
        results.append((enriched, judgment))
        print(
            f"support={judgment.semantic_support} "
            f"claim={judgment.claim_correct} "
            f"source={judgment.source_owner_correct} "
            f"({judgment.prompt_tokens}+{judgment.completion_tokens} tok, "
            f"{judgment.latency_seconds:.1f}s)"
        )

    return results


__all__ = [
    "BASE_URL",
    "JUDGMENT_PROMPT",
    "LiveJudgment",
    "MODEL",
    "call_glm_judge",
    "enrich_case_with_live_judgments",
    "judge_case",
    "run_judgments_on_manifest",
]