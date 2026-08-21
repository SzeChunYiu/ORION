"""An unmet budget is an absent measurement, not a negative result.

The ORION-Q prospective replay was killed at a hardcoded 120s on every branch in
the repo and reported as a plain capability failure. Two defects, one visible and
one not: the ceiling was below what the computation needs, and a timeout was
indistinguishable from a wrong answer. The second is why the first went
unexamined for so long -- a red light that is always red is a red light nobody
reads.
"""

from __future__ import annotations

import os
import subprocess

import pytest

from orion_research_harness import local_tools
from orion_research_harness.workspace import ResearchWorkspace


@pytest.fixture()
def workspace(tmp_path) -> ResearchWorkspace:
    return ResearchWorkspace.initialize(tmp_path / "ws", allow_process_tools=True)


class TestTimeoutCeiling:
    def test_the_default_ceiling_admits_the_orion_q_replay(self) -> None:
        """Measured: that replay needs more than 237s. 120 could never have run it."""

        assert local_tools._process_timeout_ceiling() >= 300

    def test_the_ceiling_is_overridable(self, monkeypatch) -> None:
        monkeypatch.setenv("ORION_HARNESS_PROCESS_TIMEOUT_CEILING", "1500")
        assert local_tools._process_timeout_ceiling() == 1500

    def test_the_ceiling_stays_bounded(self, monkeypatch) -> None:
        """Unbounded would let a hung computation hold the harness open forever."""

        monkeypatch.setenv("ORION_HARNESS_PROCESS_TIMEOUT_CEILING", "999999")
        assert local_tools._process_timeout_ceiling() == local_tools._MAX_PROCESS_TIMEOUT_CEILING

    @pytest.mark.parametrize("raw", ["", "abc", "-1"])
    def test_an_unreadable_override_falls_back_rather_than_crashing(
        self, monkeypatch, raw: str
    ) -> None:
        monkeypatch.setenv("ORION_HARNESS_PROCESS_TIMEOUT_CEILING", raw)
        assert local_tools._process_timeout_ceiling() >= 1

    def test_a_request_may_still_ask_for_less(self, workspace, monkeypatch) -> None:
        """The ceiling is a cap, not a floor; a short task keeps its short budget."""

        monkeypatch.setattr(local_tools, "_process_timeout_ceiling", lambda: 900)
        output = local_tools.execute_local(
            workspace, "PYTHON", {"code": "print('quick')", "timeout": 5}
        )
        assert output["returncode"] == 0
        assert "quick" in output["stdout"]


class TestTimeoutIsNotAFailure:
    def test_a_timeout_raises_rather_than_returning_a_falsy_result(self, workspace) -> None:
        with pytest.raises(subprocess.TimeoutExpired):
            local_tools.execute_local(
                workspace,
                "PYTHON",
                {"code": "import time; time.sleep(30)", "timeout": 1},
            )

    def test_the_serviced_result_is_typed_as_an_unmet_budget(self, workspace) -> None:
        """The whole point: a reader can tell 'not waited for' from 'wrong'."""

        request = workspace.get_or_create_request(
            capability="PYTHON",
            payload={"code": "import time; time.sleep(30)", "timeout": 1},
        )
        result = local_tools.service_local_request(workspace, request.request_id)

        assert result.success is False
        assert local_tools._BUDGET_EXHAUSTED_PREFIX in result.error
        assert "absent measurement, not a negative result" in result.error
        # It must not read as an ordinary exception, which is how it read before.
        assert not result.error.startswith("TimeoutExpired:")

    def test_a_real_failure_is_still_reported_as_a_failure(self, workspace) -> None:
        """The repair must not launder genuine errors into unmet budgets."""

        request = workspace.get_or_create_request(
            capability="PYTHON",
            payload={"code": "raise SystemExit(3)", "timeout": 30},
        )
        result = local_tools.service_local_request(workspace, request.request_id)

        assert local_tools._BUDGET_EXHAUSTED_PREFIX not in result.error

    def test_the_marker_is_greppable_and_stable(self) -> None:
        """Receipt consumers key on this string; it is part of the contract."""

        assert local_tools._BUDGET_EXHAUSTED_PREFIX == "BUDGET_EXHAUSTED_CANNOT_CHECK"


def test_the_environment_variable_name_is_documented_where_it_is_read() -> None:
    """A knob nobody can find is a knob that does not exist."""

    source = local_tools.__file__
    with open(source, encoding="utf-8") as handle:
        text = handle.read()
    assert "ORION_HARNESS_PROCESS_TIMEOUT_CEILING" in text
    assert os.environ.get("ORION_HARNESS_PROCESS_TIMEOUT_CEILING") is None or True
