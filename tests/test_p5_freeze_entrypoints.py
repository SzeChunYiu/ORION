from __future__ import annotations

import os

import pytest

from orion.study.p5 import freeze, freeze_cli


@pytest.mark.parametrize("entrypoint", [freeze.main, freeze_cli.main])
def test_every_p5_freeze_entrypoint_rejects_input_output_aliasing(
    tmp_path,
    entrypoint,
) -> None:
    protected = tmp_path / "protected.json"
    commitment = tmp_path / "commitment.json"

    with pytest.raises(ValueError, match="must be distinct"):
        entrypoint(
            [
                "--protected-suite",
                str(protected),
                "--candidate-packet",
                str(protected),
                "--commitment",
                str(commitment),
            ]
        )


@pytest.mark.skipif(not hasattr(os, "O_NOFOLLOW"), reason="requires no-follow filesystem support")
@pytest.mark.parametrize("entrypoint", [freeze.main, freeze_cli.main])
def test_every_p5_freeze_entrypoint_rejects_symlinked_protected_input(
    tmp_path,
    entrypoint,
) -> None:
    target = tmp_path / "target.json"
    target.write_text("{}\n", encoding="utf-8")
    protected = tmp_path / "protected.json"
    protected.symlink_to(target)

    with pytest.raises(OSError):
        entrypoint(
            [
                "--protected-suite",
                str(protected),
                "--candidate-packet",
                str(tmp_path / "candidate.json"),
                "--commitment",
                str(tmp_path / "commitment.json"),
            ]
        )
