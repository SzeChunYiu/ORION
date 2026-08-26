"""The live arm must keep its answers (issue #985).

`ProviderBackedSystem.run()` used to send the prompt, receive ~1,205 tokens of
completion, and then construct a hardcoded-empty `SystemTrace` — `reframed=False`,
no responsibility, no coordinates, no reopen — while the completion itself was
archived nowhere. All 240 live records were empty regardless of provider health.

Three properties are pinned here:

1. a structured completion is *parsed into* the trace;
2. the raw text is archived alongside, and survives even a refusal;
3. a completion that cannot be parsed becomes a typed CANNOT_CHECK refusal and
   never a fabricated empty trace.

Property 3 is the one that decides whether this is a real fix: falling back to an
empty trace on a parse failure would reproduce the original defect one layer down,
and a fabricated zero is worse than honest emptiness. "Could not check" and
"checked and found wrong" are different facts.

No test here makes a network call; the provider is stubbed throughout.
"""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import pytest

from orion.study.p1.cases import PublicView
from orion.study.p1.provider import (
    ProviderBackedSystem,
    ProviderResponse,
    ProviderStatus,
    ProviderUnavailable,
)

VIEW = PublicView(
    case_id="p1-c001",
    public_prompt="The nightly batch reports a 4% shortfall against the ledger.",
    observable_resources=("dataset:ledger", "log:batch"),
    budget_class="standard",
)


class StubProvider:
    """Returns a canned completion. Records the prompt it was given."""

    model = "stub-model"

    def __init__(self, text: str, *, status: ProviderStatus = ProviderStatus.OK) -> None:
        self._text = text
        self._status = status
        self.prompts: list[str] = []

    def complete(self, prompt: str, *, system: str = "") -> ProviderResponse:
        self.prompts.append(prompt)
        return ProviderResponse(
            status=self._status,
            text=self._text,
            model=self.model,
            input_tokens=100,
            output_tokens=1105,
        )


WELL_FORMED = json.dumps(
    {
        "reframed": True,
        "responsibility_family": "MEASUREMENT",
        "target_coordinates": ["M.MEASUREMENT", "measurement:reconciliation_basis"],
        "reopened": ["dep.ledger_close", "dep.fx_rate"],
        "root_solved": True,
        "abstained": False,
        "max_recursion_depth": 2,
    }
)


def _system(text: str, **kwargs) -> ProviderBackedSystem:
    return ProviderBackedSystem(provider=StubProvider(text), **kwargs)


# --------------------------------------------------------------------------
# 1. The completion is parsed into the trace
# --------------------------------------------------------------------------


def test_structured_completion_is_parsed_into_the_trace() -> None:
    trace = _system(WELL_FORMED).run(VIEW, seed=0)

    assert trace.reframed is True
    assert trace.responsibility_family == "MEASUREMENT"
    assert trace.target_coordinates == (
        "M.MEASUREMENT",
        "measurement:reconciliation_basis",
    )
    assert trace.reopened == ("dep.ledger_close", "dep.fx_rate")
    assert trace.root_solved is True
    assert trace.abstained is False
    assert trace.max_recursion_depth == 2


def test_a_fenced_completion_is_parsed() -> None:
    """Models wrap JSON in prose and code fences; that is not a parse failure."""

    text = f"Here is my analysis.\n\n```json\n{WELL_FORMED}\n```\n\nHope that helps."
    trace = _system(text).run(VIEW, seed=0)

    assert trace.responsibility_family == "MEASUREMENT"
    assert trace.reframed is True


def test_the_prompt_asks_for_the_structure_it_parses() -> None:
    """An elicitation that does not name the schema is a parser with no source."""

    stub = StubProvider(WELL_FORMED)
    ProviderBackedSystem(provider=stub).run(VIEW, seed=0)

    assert stub.prompts, "the provider was never called"
    prompt = stub.prompts[0]
    for key in (
        "reframed",
        "responsibility_family",
        "target_coordinates",
        "reopened",
        "root_solved",
        "abstained",
    ):
        assert key in prompt, f"the elicitation never asks for {key!r}"
    assert VIEW.public_prompt in prompt


# --------------------------------------------------------------------------
# 2. The raw text is archived alongside
# --------------------------------------------------------------------------


def test_raw_completion_text_is_archived() -> None:
    system = _system(WELL_FORMED)
    system.run(VIEW, seed=0)

    assert len(system.transcripts) == 1
    entry = system.transcripts[0]
    assert entry.raw_text == WELL_FORMED
    assert entry.case_id == "p1-c001"
    assert entry.seed == 0
    assert entry.parsed is True


def test_raw_text_is_archived_even_when_parsing_fails() -> None:
    """The evidence must survive the refusal, or the refusal is unauditable."""

    system = _system("I think the ledger is fine, honestly.")
    with pytest.raises(ProviderUnavailable):
        system.run(VIEW, seed=0)

    assert len(system.transcripts) == 1
    entry = system.transcripts[0]
    assert entry.raw_text == "I think the ledger is fine, honestly."
    assert entry.parsed is False
    assert entry.parse_error


def test_transcripts_are_written_to_the_sidecar_archive(tmp_path: Path) -> None:
    path = tmp_path / "live_transcripts.jsonl"
    system = _system(WELL_FORMED, transcript_path=path)
    system.run(VIEW, seed=0)

    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line]
    assert len(lines) == 1
    payload = json.loads(lines[0])
    assert payload["raw_text"] == WELL_FORMED
    assert payload["case_id"] == "p1-c001"
    assert payload["output_tokens"] == 1105


def test_the_transcript_carries_no_credential() -> None:
    system = _system(WELL_FORMED)
    system.run(VIEW, seed=0)

    fields = {field.name for field in dataclasses.fields(system.transcripts[0])}
    assert "api_key" not in fields
    assert "key" not in repr(system.transcripts[0]).lower()


# --------------------------------------------------------------------------
# 3. An unparseable completion is CANNOT_CHECK, never an empty trace
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "text",
    [
        "The batch is fine.",
        "",
        "{not json at all",
        json.dumps({"reframed": True}),  # missing required keys
        json.dumps({**json.loads(WELL_FORMED), "reframed": "yes"}),  # wrong type
        json.dumps([1, 2, 3]),  # not an object
    ],
)
def test_unparseable_completion_is_cannot_check_not_an_empty_trace(text: str) -> None:
    system = _system(text)
    with pytest.raises(ProviderUnavailable) as error:
        system.run(VIEW, seed=0)

    assert error.value.status is ProviderStatus.UNPARSEABLE_RESPONSE
    assert error.value.detail


def test_a_parse_failure_never_yields_a_silently_empty_trace() -> None:
    """The original defect, stated directly rather than only as a consequence."""

    system = _system("no structure here")
    try:
        trace = system.run(VIEW, seed=0)
    except ProviderUnavailable:
        return
    raise AssertionError(
        f"a parse failure produced a trace instead of refusing: {trace!r}"
    )


# --------------------------------------------------------------------------
# The checked-and-wrong / could-not-check boundary
# --------------------------------------------------------------------------


def test_out_of_vocabulary_responsibility_is_a_wrong_answer_not_cannot_check() -> None:
    """Dropping wrong-but-present answers would select the arm on outcome.

    A structurally valid answer naming a family outside the closed taxonomy has
    been observed and is simply wrong. Routing it to CANNOT_CHECK would remove
    real failures from the denominator and inflate the live arm.
    """

    text = json.dumps({**json.loads(WELL_FORMED), "responsibility_family": "DATA_QUALITY"})
    trace = _system(text).run(VIEW, seed=0)

    assert trace.responsibility_family == "DATA_QUALITY"


def test_a_declared_abstention_is_preserved_not_repaired() -> None:
    text = json.dumps(
        {
            "reframed": False,
            "responsibility_family": "",
            "target_coordinates": [],
            "reopened": [],
            "root_solved": False,
            "abstained": True,
            "max_recursion_depth": 0,
        }
    )
    trace = _system(text).run(VIEW, seed=0)

    assert trace.abstained is True
    assert trace.reframed is False
    assert trace.responsibility_family == ""


def test_self_contradictory_claims_are_passed_through_for_the_fidelity_checker() -> None:
    """The parser must not launder a contradiction into a tidy trace."""

    text = json.dumps({**json.loads(WELL_FORMED), "abstained": True})
    trace = _system(text).run(VIEW, seed=0)

    assert trace.abstained is True
    assert trace.root_solved is True, "the contradiction belongs to trace fidelity, not the parser"


def test_a_provider_refusal_still_precedes_any_parsing(monkeypatch) -> None:
    system = ProviderBackedSystem(
        provider=StubProvider("", status=ProviderStatus.NO_CREDENTIAL)
    )
    with pytest.raises(ProviderUnavailable) as error:
        system.run(VIEW, seed=0)

    assert error.value.status is ProviderStatus.NO_CREDENTIAL
    assert system.transcripts == [], "no transcript exists when no answer was received"


# --------------------------------------------------------------------------
# End to end: the harness and the pipeline
# --------------------------------------------------------------------------


def test_harness_records_cannot_check_for_an_unparseable_answer(tmp_path: Path) -> None:
    """The refusal must reach the archive as CANNOT_CHECK, not as a zero.

    Scoring an unreadable answer as a failure would put it in the denominator
    and understate the arm; dropping it would overstate the arm. It belongs in
    neither, which is what CANNOT_CHECK means.
    """

    from orion.study.p1.cases import Split, load_cases
    from orion.study.p1.harness import RunStatus, run_study
    from orion.study.p1.run_trial import CASES_ROOT

    cases = load_cases(CASES_ROOT, split=Split.PILOT)[:2]
    assert cases, "CANNOT_CHECK: no PILOT cases available to drive the harness"

    system = _system("the ledger looks fine to me")
    archive = run_study(
        cases, (system,), seeds=(0,), archive_path=tmp_path / "runs.jsonl"
    )

    assert len(archive.records) == len(cases)
    for record in archive.records:
        assert record.status is RunStatus.CANNOT_CHECK
        assert record.trace is None
        assert record.error.startswith(ProviderStatus.UNPARSEABLE_RESPONSE.value)

    # The tokens were still spent, and the text still exists.
    assert len(system.transcripts) == len(cases)
    assert all(entry.raw_text for entry in system.transcripts)


def test_harness_scores_a_parsed_answer_as_a_real_trace(tmp_path: Path) -> None:
    from orion.study.p1.cases import Split, load_cases
    from orion.study.p1.harness import RunStatus, run_study
    from orion.study.p1.run_trial import CASES_ROOT

    cases = load_cases(CASES_ROOT, split=Split.PILOT)[:2]
    assert cases, "CANNOT_CHECK: no PILOT cases available to drive the harness"

    archive = run_study(
        cases,
        (_system(WELL_FORMED),),
        seeds=(0,),
        archive_path=tmp_path / "runs.jsonl",
    )

    for record in archive.records:
        assert record.status is RunStatus.OK
        assert record.trace is not None
        assert record.trace.responsibility_family == "MEASUREMENT"
        assert record.trace.reframed is True


def test_the_campaign_pipeline_wires_the_transcript_archive(tmp_path: Path) -> None:
    """A parser with no archive behind it is unauditable after the run."""

    from orion.study.p1.run_trial import _systems

    live = [
        system
        for system in _systems(live=True, transcript_path=tmp_path / "t.jsonl")
        if system.system_id == "orion_live_provider"
    ]
    assert len(live) == 1
    assert live[0].transcript_path == tmp_path / "t.jsonl"


@pytest.mark.parametrize("split_name", ["PILOT", "TEST"])
def test_the_elicitation_adds_no_gold_beyond_the_public_view(split_name: str) -> None:
    """The access-control boundary is unchanged by asking for more structure.

    The prompt may repeat anything already inside `PublicView` — that is what
    the system is entitled to read, and gold identifiers such as the closure
    names deliberately appear there, because the hidden part is *which* closures
    must be reopened, not what they are called. What the prompt must never do is
    introduce a gold token the public view does not already contain.
    """

    from orion.study.p1.cases import Split, load_cases
    from orion.study.p1.provider import build_trace_prompt
    from orion.study.p1.run_trial import CASES_ROOT

    cases = load_cases(CASES_ROOT, split=Split[split_name])
    assert cases, f"CANNOT_CHECK: no {split_name} cases available"

    checked = 0
    for case in cases:
        view = case.public_view
        prompt = build_trace_prompt(view)
        public = view.public_prompt + " " + " ".join(view.observable_resources)
        gold = case.protected_gold
        tokens = (
            *gold.target_coordinates,
            *gold.dependencies_to_reopen,
            gold.root_success_rubric,
        )
        for token in tokens:
            if token and token not in public:
                assert token not in prompt, f"{case.case_id}: prompt introduced {token!r}"
                checked += 1

    assert checked, "CANNOT_CHECK: no gold token was outside the public view to test"


def test_the_elicitation_scaffold_is_case_independent() -> None:
    """Whatever varies between cases comes from `PublicView` and nowhere else.

    Blanking the public view out of the prompt must leave a byte-identical
    scaffold for every case. If any case-specific text survived that removal, it
    entered the prompt from somewhere other than the public view.
    """

    from orion.study.p1.cases import Split, load_cases
    from orion.study.p1.provider import build_trace_prompt
    from orion.study.p1.run_trial import CASES_ROOT

    cases = load_cases(CASES_ROOT, split=Split.PILOT)
    assert cases, "CANNOT_CHECK: no PILOT cases available"

    scaffolds = set()
    for case in cases:
        view = case.public_view
        prompt = build_trace_prompt(view)
        prompt = prompt.replace(view.public_prompt, "<PUBLIC_PROMPT>")
        prompt = prompt.replace(", ".join(view.observable_resources), "<RESOURCES>")
        scaffolds.add(prompt)

    assert len(scaffolds) == 1, "the elicitation scaffold varies by case"
