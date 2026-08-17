"""Optional live-model adapter for the ORION-P1 study.

Optional is load-bearing. Every mechanical system in `baselines.py` and
`orion_system.py` runs to completion with no credential, no network and this
module never imported. What the adapter adds is the ability to name the
*specific* reframe target, which the mechanical arm honestly declines to claim.

Credential rules, which are absolute:

* the key is read from ``os.environ.get("ANTHROPIC_API_KEY")`` and nowhere
  else — never a file, a keychain, a config, a CLI flag or another variable;
* the value is never stored on an instance, never placed in a dataclass field
  (so it cannot reach a ``repr``), never logged, printed, or written to the
  archive;
* absence is a typed refusal, not an exception to swallow and not a zero.
  ``ProviderStatus.NO_CREDENTIAL`` propagates to the harness as
  ``CANNOT_CHECK``, which is distinct from a failed run and from a low score.

"Could not check" and "checked and found wrong" are different facts. A study
that records the first as the second reports a system's score as zero on the
strength of a missing environment variable.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum

from .cases import PublicView
from .systems import ResourceUse, SystemTrace

CREDENTIAL_ENV_VAR = "ANTHROPIC_API_KEY"
#: The endpoint is taken from the environment so an Anthropic-compatible
#: gateway can be used without a code change. Never hardcode a host here: the
#: run manifest records which endpoint answered, and a value baked into source
#: would make that record a restatement of the source rather than an
#: observation of the run.
BASE_URL_ENV_VAR = "ANTHROPIC_BASE_URL"
#: Operator-directed subject model for the live arm (2026-08-16).
DEFAULT_MODEL = "glm-5.2"
DEFAULT_MAX_TOKENS = 1024


class ProviderStatus(str, Enum):
    """Why a live call did or did not produce an answer."""

    OK = "OK"
    NO_CREDENTIAL = "NO_CREDENTIAL"
    TRANSPORT_UNAVAILABLE = "TRANSPORT_UNAVAILABLE"
    PROVIDER_ERROR = "PROVIDER_ERROR"


@dataclass(frozen=True)
class ProviderResponse:
    """A live result, or a typed account of why there is none.

    No field of this object may carry the credential. `detail` is written from
    exception *types* and adapter-controlled strings rather than from raw
    provider payloads, which can echo request headers.
    """

    status: ProviderStatus
    text: str = ""
    model: str = DEFAULT_MODEL
    input_tokens: int = 0
    output_tokens: int = 0
    detail: str = ""

    @property
    def usable(self) -> bool:
        return self.status is ProviderStatus.OK


class ProviderUnavailable(RuntimeError):
    """Raised by a live system when the provider cannot answer.

    The harness maps this to ``CANNOT_CHECK`` and archives the record. It is
    deliberately not a silent skip: an unexecuted run that leaves no trace is
    indistinguishable from a run that never should have existed.
    """

    def __init__(self, status: ProviderStatus, detail: str = "") -> None:
        super().__init__(f"provider unavailable: {status.value}")
        self.status = status
        self.detail = detail


def credential_present() -> bool:
    """Whether a credential exists, without exposing or returning its value."""

    return bool(os.environ.get(CREDENTIAL_ENV_VAR))


@dataclass(frozen=True)
class AnthropicProvider:
    """Minimal live adapter. Holds configuration only — never the key."""

    model: str = DEFAULT_MODEL
    max_tokens: int = DEFAULT_MAX_TOKENS

    def complete(self, prompt: str, *, system: str = "") -> ProviderResponse:
        """Ask the model once, or explain in a typed way why we did not.

        The credential is read here, passed straight to the client, and never
        bound to anything that outlives the call.
        """

        if not credential_present():
            return ProviderResponse(
                status=ProviderStatus.NO_CREDENTIAL,
                model=self.model,
                detail=f"{CREDENTIAL_ENV_VAR} is not set in the environment",
            )
        try:  # Imported lazily: a missing SDK must not break collection of a
            # test suite that never makes a network call.
            from anthropic import Anthropic
        except ImportError:
            return ProviderResponse(
                status=ProviderStatus.TRANSPORT_UNAVAILABLE,
                model=self.model,
                detail="the anthropic client package is not installed",
            )
        try:
            base_url = os.environ.get(BASE_URL_ENV_VAR) or None
            client = Anthropic(
                api_key=os.environ.get(CREDENTIAL_ENV_VAR),
                **({"base_url": base_url} if base_url else {}),
                timeout=120.0,  # Bounded timeout prevents indefinite SSL-read stalls (P1 hang triage 2026-08-17)
            )
            message = client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system or "You are a research system under evaluation.",
                messages=[{"role": "user", "content": prompt}],
            )
        except Exception as error:  # noqa: BLE001 - the type is the whole report
            # Only the exception class name is recorded. Provider messages can
            # echo request material, and nothing from a provider payload is
            # allowed into the archive.
            return ProviderResponse(
                status=ProviderStatus.PROVIDER_ERROR,
                model=self.model,
                detail=type(error).__name__,
            )
        text = "".join(
            getattr(block, "text", "") for block in getattr(message, "content", [])
        )
        usage = getattr(message, "usage", None)
        return ProviderResponse(
            status=ProviderStatus.OK,
            text=text,
            model=self.model,
            input_tokens=int(getattr(usage, "input_tokens", 0) or 0),
            output_tokens=int(getattr(usage, "output_tokens", 0) or 0),
        )


def require_provider(response: ProviderResponse) -> ProviderResponse:
    """Turn a typed refusal into the harness's CANNOT_CHECK signal."""

    if not response.usable:
        raise ProviderUnavailable(response.status, response.detail)
    return response


@dataclass(frozen=True)
class ProviderBackedSystem:
    """A system under test whose answer requires the live model.

    Present so the refusal path is a real path rather than a claim: with no
    credential this raises `ProviderUnavailable` before any network object is
    constructed, and the harness records CANNOT_CHECK for the (case, system,
    seed) cell instead of a zero.
    """

    system_id: str = "orion_live_provider"
    provider: AnthropicProvider = AnthropicProvider()

    def run(self, view: PublicView, *, seed: int) -> SystemTrace:
        response = require_provider(
            self.provider.complete(
                "Name the coordinate that must change for this task, if any.\n\n"
                f"{view.public_prompt}\n\n"
                f"Resources: {', '.join(view.observable_resources)}"
            )
        )
        return SystemTrace(
            case_id=view.case_id,
            system_id=self.system_id,
            seed=seed,
            reframed=False,
            resources=ResourceUse(
                model_tokens=response.input_tokens + response.output_tokens,
                tool_calls=1,
            ),
            notes=f"model={response.model}",
        )


__all__ = [
    "BASE_URL_ENV_VAR",
    "CREDENTIAL_ENV_VAR",
    "DEFAULT_MAX_TOKENS",
    "DEFAULT_MODEL",
    "AnthropicProvider",
    "ProviderBackedSystem",
    "ProviderResponse",
    "ProviderStatus",
    "ProviderUnavailable",
    "credential_present",
    "require_provider",
]
