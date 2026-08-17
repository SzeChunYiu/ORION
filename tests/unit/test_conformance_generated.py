"""The generated-artifact check must fire, stay quiet, and refuse to be abused.

The check runs commands a data file names, so its failure modes are not only
"misses drift". It could also cry wolf on a paper that declares nothing, or
execute something it should not. Each of those is exercised here, together with
the no-alarm case, because a conformance check nobody trusts is switched off and
then the drift returns.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from orion.conformance import (
    ConformanceVerdict,
    check_generated_artifacts_regenerate,
)


def _paper(tmp_path: Path, registry: dict | str | None, *, script: str | None = None) -> Path:
    root = tmp_path / "paper-99-fixture"
    (root / "protocol").mkdir(parents=True)
    (root / "scripts").mkdir(parents=True)
    (root / "manuscript" / "generated").mkdir(parents=True)
    (root / "manuscript" / "generated" / "facts.tex").write_text("x\n", encoding="utf-8")
    if script is not None:
        (root / "scripts" / "render.py").write_text(script, encoding="utf-8")
    if registry is not None:
        payload = registry if isinstance(registry, str) else json.dumps(registry)
        (root / "protocol" / "GENERATED_ARTIFACTS_V1.json").write_text(payload, encoding="utf-8")
    return root


PASSING = "import sys\nsys.exit(0)\n"
FAILING = "import sys\nsys.stderr.write('facts.tex stale: regenerate\\n')\nsys.exit(1)\n"


def _entry(**overrides) -> dict:
    entry = {
        "output": "manuscript/generated/facts.tex",
        "generator": "scripts/render.py",
        "check": ["python3", "scripts/render.py", "--check"],
    }
    entry.update(overrides)
    return {"artifacts": [entry]}


def test_no_registry_means_the_question_is_not_asked(tmp_path):
    """Absent registry must not read as a pass."""

    root = _paper(tmp_path, None)
    assert check_generated_artifacts_regenerate(root, "P99") is None


def test_a_regenerating_artifact_is_satisfied(tmp_path):
    root = _paper(tmp_path, _entry(), script=PASSING)
    finding = check_generated_artifacts_regenerate(root, "P99")
    assert finding is not None
    assert finding.verdict is ConformanceVerdict.SATISFIED
    assert finding.observed == 1


def test_a_stale_artifact_is_violated_and_says_which(tmp_path):
    """The guard has to fire, or the whole exercise is decoration."""

    root = _paper(tmp_path, _entry(), script=FAILING)
    finding = check_generated_artifacts_regenerate(root, "P99")
    assert finding is not None
    assert finding.verdict is ConformanceVerdict.VIOLATED
    assert "facts.tex" in finding.detail


def test_an_empty_registry_is_cannot_check_not_satisfied(tmp_path):
    root = _paper(tmp_path, {"artifacts": []}, script=PASSING)
    finding = check_generated_artifacts_regenerate(root, "P99")
    assert finding is not None
    assert finding.verdict is ConformanceVerdict.CANNOT_CHECK


def test_unparseable_registry_is_violated(tmp_path):
    root = _paper(tmp_path, "{not json", script=PASSING)
    finding = check_generated_artifacts_regenerate(root, "P99")
    assert finding is not None
    assert finding.verdict is ConformanceVerdict.VIOLATED


def test_a_declared_output_that_does_not_exist_cannot_be_verified(tmp_path):
    root = _paper(tmp_path, _entry(output="manuscript/generated/absent.tex"), script=PASSING)
    finding = check_generated_artifacts_regenerate(root, "P99")
    assert finding is not None
    assert finding.verdict is ConformanceVerdict.CANNOT_CHECK
    assert "absent" in finding.detail


def test_a_missing_check_command_cannot_be_verified(tmp_path):
    root = _paper(tmp_path, _entry(check=[]), script=PASSING)
    finding = check_generated_artifacts_regenerate(root, "P99")
    assert finding is not None
    assert finding.verdict is ConformanceVerdict.CANNOT_CHECK


def test_the_registry_cannot_make_the_checker_run_arbitrary_things(tmp_path):
    """A data file must not be able to hand the checker a shell command."""

    shell = _paper(tmp_path, _entry(check=["rm", "-rf", "/"]), script=PASSING)
    finding = check_generated_artifacts_regenerate(shell, "P99")
    assert finding is not None
    assert finding.verdict is ConformanceVerdict.CANNOT_CHECK
    assert "paper-local python" in finding.detail

    escaping = _paper(
        tmp_path / "escape",
        _entry(check=["python3", "../../../outside.py", "--check"]),
        script=PASSING,
    )
    finding = check_generated_artifacts_regenerate(escaping, "P99")
    assert finding is not None
    assert finding.verdict is ConformanceVerdict.CANNOT_CHECK


def test_the_real_interpreter_is_accepted(tmp_path):
    """sys.executable must work, or CI with a venv python reports CANNOT_CHECK."""

    root = _paper(tmp_path, _entry(check=[sys.executable, "scripts/render.py"]), script=PASSING)
    finding = check_generated_artifacts_regenerate(root, "P99")
    assert finding is not None
    assert finding.verdict is ConformanceVerdict.SATISFIED
