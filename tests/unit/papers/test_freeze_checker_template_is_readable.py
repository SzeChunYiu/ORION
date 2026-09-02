"""The emitted freeze checker must survive commits that land after the freeze.

The V2-derived checker validates a property of HEAD::

    head   = git.resolve_commit("HEAD")
    parent = git.resolve_commit(f"{head}^")
    require(parent == content_base, ...)

so it passes only while HEAD *is* the freeze commit. The generator now patches
that out, moving every attestation check onto the freeze commit -- located by
identity -- and reporting post-freeze paper movement instead of invalidating on
it.

The last test is the one that matters: it takes a simulated freeze in a scratch
worktree, lands two further commits, and requires the emitted checker to still
answer. Everything above it guards the patch machinery that makes that possible.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
GENERATOR = ROOT / "papers/generate_all25_bounded_science_freeze_v3.py"


def _load():
    spec = importlib.util.spec_from_file_location("_freeze_gen_v3", GENERATOR)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def gen():
    return _load()


@pytest.fixture(scope="module")
def template(gen):
    if not gen.V2_CHECKER.is_file():
        pytest.skip("the V2 checker is not present in this tree")
    source, _ = gen.load_v2()
    return gen.template_of(source)


def test_every_patch_applies_exactly_once(gen, template):
    for old, _new, expected in gen.READABLE_PATCHES:
        assert template.count(old) == expected, (
            "upstream checker fragment not found exactly as expected: "
            f"{old.splitlines()[0][:80]}"
        )


def test_patched_template_compiles_and_no_longer_reads_head(gen, template):
    patched = gen.readable_template(template)
    code = patched[patched.find("OID_RE =") :]
    assert "head" not in code, "the attestation is still tied to the reading position"
    for name in ("locate_freeze_commit", "measure_post_freeze_drift", "class CannotCheck"):
        assert name in patched, f"{name} missing from the patched template"
    _source, constants = gen.load_v2()
    emitted = patched.replace(gen.PLACEHOLDER, json.dumps(constants))
    compile(emitted, "emitted_checker.py", "exec")


def test_legacy_flag_leaves_the_template_unpatched(gen, template):
    patched = gen.readable_template(template)
    assert patched != template
    # build(..., legacy_checker=True) must not reach readable_template at all;
    # the template it emits is exactly template_of(source).
    assert "locate_freeze_commit" not in template


def test_a_drifted_upstream_fragment_fails_loudly(gen, template):
    """A half-patched validator must never be emitted silently."""
    old, _new, _count = gen.READABLE_PATCHES[0]
    mutant = template.replace(old, "# upstream drifted\n", 1)
    with pytest.raises(SystemExit) as excinfo:
        gen.readable_template(mutant)
    assert "cannot patch the checker template" in str(excinfo.value)


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["/usr/bin/git", *args], cwd=cwd, capture_output=True, text=True
    )


def test_emitted_checker_survives_commits_that_land_after_the_freeze(gen, tmp_path):
    """End to end: take a freeze, land two commits, require an answer at each."""
    manifest = json.loads(
        (ROOT / gen.V3_MANIFEST_REL).read_text(encoding="utf-8")
    ) if (ROOT / gen.V3_MANIFEST_REL).is_file() else None
    if manifest is None:
        pytest.skip("no committed V3 manifest to take a content base from")
    base = manifest["content_base_commit"]
    if _git(ROOT, "cat-file", "-e", f"{base}^{{commit}}").returncode != 0:
        pytest.skip("content base absent (shallow clone)")

    out = tmp_path / "emitted"
    out.mkdir()
    built = subprocess.run(
        [
            "python3", str(GENERATOR),
            "--content-base", base,
            "--disposition-unreachable",
            "--out-dir", str(out),
            "--date", "2026-01-01",
        ],
        cwd=ROOT, capture_output=True, text=True,
    )
    if built.returncode != 0:
        pytest.skip(f"generator refused: {built.stderr.strip()[:200]}")

    work = tmp_path / "sim"
    if _git(ROOT, "worktree", "add", "--detach", str(work), base).returncode != 0:
        pytest.skip("cannot create a scratch worktree")

    try:
        for name in (gen.V3_MANIFEST_REL, gen.V3_CHECKER_REL):
            shutil.copy(out / Path(name).name, work / name)
        checker = work / gen.V3_CHECKER_REL
        _git(work, "add", gen.V3_MANIFEST_REL, gen.V3_CHECKER_REL)
        assert _git(
            work, "-c", "user.email=t@t", "-c", "user.name=t",
            "commit", "-m", "simulated freeze take",
        ).returncode == 0

        def run(*extra: str) -> subprocess.CompletedProcess:
            return subprocess.run(
                ["python3", str(checker), "--repo", str(work), *extra],
                cwd=work, capture_output=True, text=True,
            )

        at_freeze = run()
        assert at_freeze.returncode == 0, at_freeze.stderr
        assert "BOUNDED_FREEZE_VALID" in at_freeze.stdout
        assert "drifted=0" in at_freeze.stdout

        # An unrelated later commit. The unpatched checker fails here.
        (work / "SIM_UNRELATED.txt").write_text("later\n", encoding="utf-8")
        _git(work, "add", "SIM_UNRELATED.txt")
        _git(work, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", "later")
        after = run()
        assert after.returncode == 0, after.stderr
        assert "BOUNDED_FREEZE_VALID" in after.stdout
        assert "drifted=0" in after.stdout

        # A commit that moves a paper: reported, still not an invalidation.
        paper = Path(manifest["papers"][0]["canonical_directory"])
        (work / paper / "SIM_NOTE.txt").write_text("moved\n", encoding="utf-8")
        _git(work, "add", str(paper))
        _git(work, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", "touch")
        drifted = run()
        assert drifted.returncode == 0, drifted.stderr
        assert "POST_FREEZE_DRIFT" in drifted.stdout
        assert "drifted=1" in drifted.stdout

        # ...unless the caller is taking a freeze and asks for strictness.
        strict = run("--require-no-drift")
        assert strict.returncode == 1
        assert "have moved since the freeze" in strict.stderr
    finally:
        _git(ROOT, "worktree", "remove", "--force", str(work))
