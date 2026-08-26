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

import json
import os
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

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
    #: The model answered, but not in the structure the study can read. This is
    #: a distinct fact from "the model was not reached": the tokens exist and are
    #: archived, and only the structure is missing. It still propagates to
    #: CANNOT_CHECK, because an answer we cannot read is not an answer we may
    #: score as wrong.
    UNPARSEABLE_RESPONSE = "UNPARSEABLE_RESPONSE"


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
                timeout=30.0,  # Bounded timeout prevents indefinite SSL-read stalls (P1 hang triage 2026-08-17)
                max_retries=0,  # No retries: 30s timeout should raise immediately, not compound
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


# --------------------------------------------------------------------------
# Trace elicitation, parsing and raw archiving
#
# The live arm used to send a one-line prompt, receive ~1,205 tokens, and throw
# them away: `run()` returned a hardcoded-empty `SystemTrace` and the completion
# was archived nowhere, so all 240 live records read as empty regardless of
# provider health (issue #985). What follows is the missing half of the adapter.
#
# Two rules govern it, and they are the module's own:
#
# * Nothing is fabricated. If the completion cannot be read as a trace, the
#   adapter refuses with a typed status and the harness records CANNOT_CHECK.
#   Falling back to an empty trace would reproduce the original defect one layer
#   down, and a fabricated zero is worse than an honest absence.
# * The distinction between "could not check" and "checked and found wrong" is
#   drawn at *structure*, not at content. A structurally valid answer naming a
#   family outside the closed taxonomy has been observed and is simply wrong; it
#   is scored as wrong. Routing wrong-but-present answers to CANNOT_CHECK would
#   drop real failures out of the denominator and inflate the arm.
# --------------------------------------------------------------------------

#: The trace fields the live arm must supply, and their required Python types.
#: `SystemTrace` carries more, but everything else is either measured by the
#: harness (elapsed time) or accounted by the adapter (tokens); these seven are
#: the system's answer.
TRACE_SCHEMA: tuple[tuple[str, type | tuple[type, ...]], ...] = (
    ("reframed", bool),
    ("responsibility_family", str),
    ("target_coordinates", list),
    ("reopened", list),
    ("root_solved", bool),
    ("abstained", bool),
    ("max_recursion_depth", int),
)

#: The closed responsibility taxonomy, quoted to the model verbatim. This is the
#: same case-independent vocabulary the mechanical arm uses (see
#: `orion.core.residuals.Responsibility`), so naming it is matched treatment
#: rather than a leak: it says nothing about *this* case, and without a shared
#: vocabulary the live and mechanical arms would not be gold-comparable.
RESPONSIBILITY_VOCABULARY: tuple[str, ...] = (
    "QUESTION",
    "REPRESENTATION",
    "SEARCH",
    "ROUTING",
    "DECOMPOSITION",
    "INTERFACE",
    "MEASUREMENT",
    "EVALUATOR",
    "METHOD",
    "EVIDENCE",
    "EXECUTION",
)

_JSON_OBJECT = re.compile(r"\{.*\}", re.DOTALL)


class TraceParseError(ValueError):
    """The completion could not be read as a trace.

    Carries only adapter-controlled text. The raw completion is archived, but it
    is never spliced into an exception message that flows to the run archive's
    `error` field.
    """


def build_trace_prompt(view: PublicView) -> str:
    """Ask for a trace in the shape the study scores.

    The system is handed exactly `PublicView` — the public prompt and the
    observable resources. No gold, no family label, no case object: the
    access-control boundary is unchanged by eliciting more structure.
    """

    schema_keys = "\n".join(
        f'  "{name}": <{_type_hint(expected)}>' for name, expected in TRACE_SCHEMA
    )
    return (
        "You are a research system under evaluation. Diagnose the task below and "
        "name the coordinate that must change, if any.\n\n"
        f"TASK:\n{view.public_prompt}\n\n"
        f"OBSERVABLE RESOURCES: {', '.join(view.observable_resources)}\n\n"
        "Answer with a single JSON object and nothing else, with exactly these "
        "keys:\n"
        "{\n"
        f"{schema_keys}\n"
        "}\n\n"
        "Field meanings:\n"
        "- reframed: true if the task as stated must be reformulated to be solved.\n"
        "- responsibility_family: which part of the formulation owns the defect, "
        f"one of {', '.join(RESPONSIBILITY_VOCABULARY)}. Use \"\" if you make no "
        "claim.\n"
        # The example teaches the *shape* with placeholders only. Quoting a real
        # axis here would hand the answer to every case whose gold names that
        # axis — an earlier draft used "W.REPRESENTATIONS" and leaked it to
        # three PILOT cases, which is why the no-gold test compares against the
        # public view rather than trusting the scaffold to be neutral.
        "- target_coordinates: the specific coordinates that must change, as "
        '["<AXIS>", "<axis>:<specific_target>"].\n'
        "- reopened: identifiers of previously settled dependencies your answer "
        "reopens.\n"
        "- root_solved: true only if you actually solved the root task.\n"
        "- abstained: true if you decline to answer.\n"
        "- max_recursion_depth: how many levels of dependency you reopened.\n"
    )


def _type_hint(expected: type | tuple[type, ...]) -> str:
    names = expected if isinstance(expected, tuple) else (expected,)
    return " | ".join(item.__name__ for item in names)


def parse_trace_payload(text: str) -> dict:
    """Read a trace object out of a completion, or refuse.

    Models wrap JSON in prose and code fences; that is not a failure to answer,
    so the outermost brace-delimited object is extracted before parsing. What is
    a failure: no object at all, a non-object, a missing key, or a key of the
    wrong type. Each of those means the answer was not observed.
    """

    if not text or not text.strip():
        raise TraceParseError("the completion was empty")
    match = _JSON_OBJECT.search(text)
    if match is None:
        raise TraceParseError("the completion contained no JSON object")
    try:
        payload = json.loads(match.group(0))
    except json.JSONDecodeError as error:
        raise TraceParseError(f"the JSON object did not parse: {error.msg}") from None
    if not isinstance(payload, dict):
        raise TraceParseError("the completion's JSON was not an object")

    missing = [name for name, _ in TRACE_SCHEMA if name not in payload]
    if missing:
        raise TraceParseError(f"required keys absent: {', '.join(sorted(missing))}")

    for name, expected in TRACE_SCHEMA:
        value = payload[name]
        # bool is a subclass of int; an int where a bool belongs is a wrong type.
        if expected is int and isinstance(value, bool):
            raise TraceParseError(f"{name} must be {_type_hint(expected)}")
        if not isinstance(value, expected):
            raise TraceParseError(f"{name} must be {_type_hint(expected)}")

    for name in ("target_coordinates", "reopened"):
        if not all(isinstance(item, str) for item in payload[name]):
            raise TraceParseError(f"{name} must contain only strings")
    if payload["max_recursion_depth"] < 0:
        raise TraceParseError("max_recursion_depth must not be negative")
    return payload


@dataclass(frozen=True)
class TraceTranscript:
    """One live exchange, archived verbatim.

    Holds the model's own words and the adapter's accounting. It never holds the
    credential, and it never holds the provider's error payload — only the
    completion text and adapter-controlled strings.
    """

    case_id: str
    system_id: str
    seed: int
    model: str
    input_tokens: int
    output_tokens: int
    raw_text: str
    parsed: bool
    parse_error: str = ""

    def to_json(self) -> str:
        return json.dumps(
            {
                "case_id": self.case_id,
                "system_id": self.system_id,
                "seed": self.seed,
                "model": self.model,
                "input_tokens": self.input_tokens,
                "output_tokens": self.output_tokens,
                "raw_text": self.raw_text,
                "parsed": self.parsed,
                "parse_error": self.parse_error,
            },
            sort_keys=True,
        )


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
    #: Where raw completions are archived. `None` keeps them in memory only,
    #: which is what the test suite uses; a campaign run points this at the
    #: `raw/` directory beside the run archive.
    transcript_path: Path | None = None
    #: Every exchange this instance has had, in order, parsed or not.
    transcripts: list[TraceTranscript] = field(default_factory=list)

    def run(self, view: PublicView, *, seed: int) -> SystemTrace:
        """Elicit a structured trace, archive the raw text, then parse it.

        Order matters. The raw completion is archived *before* parsing is
        attempted, so the evidence survives a refusal — otherwise an unparseable
        answer would leave nothing behind to audit, which is the state issue
        #985 describes.
        """

        response = require_provider(self.provider.complete(build_trace_prompt(view)))

        try:
            payload = parse_trace_payload(response.text)
        except TraceParseError as error:
            self._archive(view, seed=seed, response=response, parse_error=str(error))
            # A model that answered unreadably is not a model that answered
            # wrongly. This propagates to CANNOT_CHECK, and the tokens it cost
            # sit on the transcript rather than being invented into a zero.
            raise ProviderUnavailable(
                ProviderStatus.UNPARSEABLE_RESPONSE, str(error)
            ) from None

        self._archive(view, seed=seed, response=response)

        # Claims are carried across as made. A contradiction — abstaining while
        # claiming the root solved, coordinates without a reframe — is real data
        # about the system and belongs to `_trace_fidelity_faults` and the
        # harness integrity flags. Repairing it here would launder the finding.
        return SystemTrace(
            case_id=view.case_id,
            system_id=self.system_id,
            seed=seed,
            reframed=bool(payload["reframed"]),
            responsibility_family=str(payload["responsibility_family"]).strip(),
            target_coordinates=tuple(payload["target_coordinates"]),
            reopened=tuple(payload["reopened"]),
            root_solved=bool(payload["root_solved"]),
            abstained=bool(payload["abstained"]),
            max_recursion_depth=int(payload["max_recursion_depth"]),
            resources=ResourceUse(
                model_tokens=response.input_tokens + response.output_tokens,
                tool_calls=1,
            ),
            # `root_solved` here is the model's own self-report. The mechanical
            # arm never self-asserts it — it re-runs the shared detector against
            # its post-repair state — so the two arms reach the same field by
            # different routes, and the note keeps that visible to the grader.
            notes=f"model={response.model}; root_solved=self_reported",
        )

    def _archive(
        self,
        view: PublicView,
        *,
        seed: int,
        response: ProviderResponse,
        parse_error: str = "",
    ) -> None:
        transcript = TraceTranscript(
            case_id=view.case_id,
            system_id=self.system_id,
            seed=seed,
            model=response.model,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            raw_text=response.text,
            parsed=not parse_error,
            parse_error=parse_error,
        )
        self.transcripts.append(transcript)
        if self.transcript_path is not None:
            self.transcript_path.parent.mkdir(parents=True, exist_ok=True)
            with self.transcript_path.open("a", encoding="utf-8") as handle:
                handle.write(transcript.to_json() + "\n")


__all__ = [
    "BASE_URL_ENV_VAR",
    "CREDENTIAL_ENV_VAR",
    "DEFAULT_MAX_TOKENS",
    "DEFAULT_MODEL",
    "RESPONSIBILITY_VOCABULARY",
    "TRACE_SCHEMA",
    "AnthropicProvider",
    "ProviderBackedSystem",
    "ProviderResponse",
    "ProviderStatus",
    "ProviderUnavailable",
    "TraceParseError",
    "TraceTranscript",
    "build_trace_prompt",
    "parse_trace_payload",
    "credential_present",
    "require_provider",
]
