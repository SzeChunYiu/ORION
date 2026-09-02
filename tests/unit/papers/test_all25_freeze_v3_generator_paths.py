"""The V3 freeze generator must write where its manifest says it lives.

`ALL_25_BOUNDED_SCIENCE_FREEZE_V3.json` records `manifest_relative` and
`checker_relative` as its own identity, and `validate_exact_freeze_commit`
requires the freeze commit to add exactly those two paths. A generator whose
default output directory disagrees with those constants emits a manifest that
misdescribes where it is, and the freeze commit then adds files at paths the
manifest does not name.

Caught on 2026-09-02: `--out-dir` defaulted to the repository root while the
generator printed, and the manifest recorded, `papers/`-prefixed paths. The run
reported "wrote papers/..." and wrote to the root instead.
"""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
GENERATOR = ROOT / "papers/generate_all25_bounded_science_freeze_v3.py"


def _load():
    spec = importlib.util.spec_from_file_location("_freeze_v3_gen", GENERATOR)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _default_out_dir(module) -> Path:
    """Recover the parser's --out-dir default without running the generator."""
    parsers: list[argparse.ArgumentParser] = []
    real_init = argparse.ArgumentParser.__init__

    def capture(self, *args, **kwargs):
        real_init(self, *args, **kwargs)
        parsers.append(self)

    argparse.ArgumentParser.__init__ = capture  # type: ignore[method-assign]
    try:
        # main() builds the parser, then fails on the required --content-base.
        with pytest.raises(SystemExit):
            module.main([])
    finally:
        argparse.ArgumentParser.__init__ = real_init  # type: ignore[method-assign]

    assert parsers, "the generator built no ArgumentParser"
    namespace = parsers[0].parse_args(["--content-base", "HEAD"])
    return Path(namespace.out_dir)


def test_default_out_dir_matches_the_declared_relative_paths() -> None:
    module = _load()

    manifest_rel = Path(module.V3_MANIFEST_REL)
    checker_rel = Path(module.V3_CHECKER_REL)
    assert manifest_rel.parent == checker_rel.parent, (
        "the manifest and checker must be declared in the same directory, "
        f"got {manifest_rel.parent} and {checker_rel.parent}"
    )

    expected = (module.ROOT / manifest_rel).parent
    assert _default_out_dir(module) == expected, (
        "the default --out-dir must be the directory named by V3_MANIFEST_REL; "
        "otherwise the generator writes a manifest that misdescribes its own "
        "location and the freeze commit adds unnamed paths"
    )


def test_declared_relative_paths_are_repo_relative_and_under_papers() -> None:
    module = _load()

    for rel in (module.V3_MANIFEST_REL, module.V3_CHECKER_REL):
        path = Path(rel)
        assert not path.is_absolute(), f"{rel} must be repository-relative"
        assert path.parts[0] == "papers", (
            f"{rel} must live under papers/, alongside the V2 freeze it succeeds"
        )
