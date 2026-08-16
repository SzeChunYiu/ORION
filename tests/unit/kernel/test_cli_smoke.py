from __future__ import annotations

import json
from pathlib import Path

import pytest

from orion.kernel.cli import main


@pytest.mark.parametrize("command", ["status", "verify", "report", "request", "run"])
def test_every_cli_command_executes(command: str, tmp_path: Path, capsys) -> None:
    """Smoke coverage for the entrypoint itself.

    Added after a regression that broke `run` on main and passed CI: a local
    re-import inside the `request` branch shadowed a module-level name, so every
    other branch raised UnboundLocalError before reaching its own use of it.
    Nothing caught it because no test invoked the CLI — the suite tested the
    library the CLI calls, not the CLI.
    """

    code = main(
        [
            command,
            "--state",
            str(tmp_path / "state"),
            "--repo-root",
            ".",
            "--rounds",
            "1",
            "--selection-limit",
            "4",
        ]
    )
    assert code == 0
    captured = capsys.readouterr().out
    assert json.loads(captured)


def test_an_unparsable_evidence_root_is_refused(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        main(
            [
                "run",
                "--state",
                str(tmp_path / "state"),
                "--evidence-root",
                "no-equals-sign",
            ]
        )
