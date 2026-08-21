"""The instrument must separate "these files are intact" from "these are the files".

Every test here builds a tiny tree and asks the two questions independently. The
one that carries the finding is
``test_an_unnamed_file_in_scope_fails_membership_while_drift_passes``: that pair
of verdicts is the state P10's shipped binding is in, and no existing check in
this repository can report it.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from orion.programme.guard_exercise import GuardVerdictReason
from orion.programme.manifest_membership import (
    DigestAlgorithm,
    DigestBinding,
    ManifestMembershipNotClosed,
    ManifestScope,
    assess_drift,
    assess_membership,
    audit_from_registration,
    audit_membership,
    audit_outcome,
    audit_report,
    binding_from_manifest,
    binding_from_mapping,
    main,
    parse_digest_manifest,
    render_audit,
    require_closed_membership,
    scope_paths,
)
from orion.programme.records import Outcome

#: Git's own blob ids for two fixed inputs. Written as constants so the test
#: proves the algorithm rather than proving that this module agrees with itself.
EMPTY_BLOB = "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391"
HELLO_BLOB = "ce013625030ba8dba906f756967f9e9ca394464a"


def _write(root: Path, relative: str, text: str) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _manifest(root: Path, name: str, relatives: tuple[str, ...]) -> Path:
    lines = [
        f"{DigestAlgorithm.SHA256.digest((root / item).read_bytes())}  {item}"
        for item in relatives
    ]
    return _write(root, name, "\n".join(lines) + "\n")


def _tree(root: Path, files: dict[str, str]) -> None:
    for relative, text in files.items():
        _write(root, relative, text)


def _scope(root: Path) -> ManifestScope:
    return ManifestScope(
        scope_id="fixture",
        scope_definition="every file under the fixture root",
        paths=scope_paths([root]),
    )


def _binding(root: Path, manifest: Path, *, dereferenced_by: str = "a checker") -> DigestBinding:
    return binding_from_manifest(
        binding_id=manifest.name,
        manifest_path=manifest,
        base_dir=root,
        dereferenced_by=dereferenced_by,
    )


def test_git_blob_identity_is_gits_function_not_a_hash_of_the_bytes() -> None:
    assert DigestAlgorithm.GIT_BLOB_SHA1.digest(b"") == EMPTY_BLOB
    assert DigestAlgorithm.GIT_BLOB_SHA1.digest(b"hello\n") == HELLO_BLOB
    assert DigestAlgorithm.SHA256.digest(b"") != EMPTY_BLOB


def test_a_closed_binding_passes_both_guards(tmp_path: Path) -> None:
    _tree(tmp_path, {"a.txt": "one\n", "sub/b.txt": "two\n"})
    manifest = _manifest(tmp_path, "SUMS", ("a.txt", "sub/b.txt"))
    audit = audit_membership(_scope(tmp_path), (_binding(tmp_path, manifest),))

    assert assess_drift(audit).outcome is Outcome.PASS
    assert assess_membership(audit).outcome is Outcome.PASS
    assert audit_outcome(audit) is Outcome.PASS
    # The manifest itself is in scope and is enrolled by being the manifest.
    assert audit.unenrolled == ()
    require_closed_membership(audit)


def test_an_unnamed_file_in_scope_fails_membership_while_drift_passes(tmp_path: Path) -> None:
    """The P10 state: intact bytes over a set the artifact chose."""

    _tree(tmp_path, {"a.txt": "one\n", "experiments/run.py": "print(1)\n"})
    manifest = _manifest(tmp_path, "SUMS", ("a.txt",))
    audit = audit_membership(_scope(tmp_path), (_binding(tmp_path, manifest),))

    drift = assess_drift(audit)
    membership = assess_membership(audit)
    assert drift.outcome is Outcome.PASS
    assert drift.reason is GuardVerdictReason.HELD_UNDER_EXERCISE
    assert membership.outcome is Outcome.FAIL
    assert audit_outcome(audit) is Outcome.FAIL
    assert [path.name for path in audit.unenrolled] == ["run.py"]

    with pytest.raises(ManifestMembershipNotClosed, match="named by no enforced binding"):
        require_closed_membership(audit)


def test_adding_a_file_adds_an_opportunity(tmp_path: Path) -> None:
    """The property the shipped verifier does not have.

    ``VERIFY_LOCAL_CLOSURE.sh`` walks the manifest, so a new file leaves its
    count and its verdict untouched. Here the denominator is the tree.
    """

    _tree(tmp_path, {"a.txt": "one\n"})
    manifest = _manifest(tmp_path, "SUMS", ("a.txt",))
    before = audit_membership(_scope(tmp_path), (_binding(tmp_path, manifest),))
    assert audit_outcome(before) is Outcome.PASS

    _write(tmp_path, "added.txt", "three\n")
    after = audit_membership(_scope(tmp_path), (_binding(tmp_path, manifest),))
    assert audit_outcome(after) is Outcome.FAIL
    assert len(after.scope.paths) == len(before.scope.paths) + 1
    assert len(after.enrolled) == len(before.enrolled)


def test_a_manifest_nobody_reads_enrolls_nothing_and_its_drift_is_reported(
    tmp_path: Path,
) -> None:
    """P10's ``SCRIPT_MANIFEST_SHA256.txt``: committed, bound, dereferenced by nothing."""

    _tree(tmp_path, {"a.txt": "one\n", "experiments/run.py": "print(1)\n"})
    enforced = _manifest(tmp_path, "SUMS", ("a.txt",))
    historical = _manifest(tmp_path, "HISTORICAL", ("experiments/run.py",))
    _write(tmp_path, "experiments/run.py", "print(2)\n")  # drifts after the receipt was taken

    audit = audit_membership(
        _scope(tmp_path),
        (
            _binding(tmp_path, enforced),
            _binding(tmp_path, historical, dereferenced_by=""),
        ),
    )

    assert [path.name for path in audit.unenrolled] == ["HISTORICAL", "run.py"]
    assert [path.name for path in audit.stale_only] == ["run.py"]
    assert audit.unenforced_drift == (("HISTORICAL", "experiments/run.py"),)
    # The unread manifest's drift must not be scored as a violation of the guard
    # that actually runs; it is evidence about the manifest, not about the tree.
    assert audit.enforced_violations == 0
    assert assess_drift(audit).outcome is Outcome.PASS
    assert assess_membership(audit).outcome is Outcome.FAIL


def test_only_an_enforced_manifests_own_path_is_self_exempt(tmp_path: Path) -> None:
    """A second file repeating the same digests is decoration, not a binding."""

    _tree(tmp_path, {"a.txt": "one\n"})
    manifest = _manifest(tmp_path, "SUMS", ("a.txt",))
    _write(tmp_path, "SUMS_COPY", manifest.read_text(encoding="utf-8"))

    audit = audit_membership(_scope(tmp_path), (_binding(tmp_path, manifest),))
    assert [path.name for path in audit.unenrolled] == ["SUMS_COPY"]


def test_an_unenforced_manifest_does_not_exempt_itself(tmp_path: Path) -> None:
    _tree(tmp_path, {"a.txt": "one\n"})
    historical = _manifest(tmp_path, "HISTORICAL", ("a.txt",))
    audit = audit_membership(
        _scope(tmp_path), (_binding(tmp_path, historical, dereferenced_by=""),)
    )
    assert {path.name for path in audit.unenrolled} == {"HISTORICAL", "a.txt"}
    assert assess_drift(audit).outcome is Outcome.CANNOT_CHECK
    assert assess_drift(audit).reason is GuardVerdictReason.NEVER_EXERCISED


def test_drift_in_an_enforced_binding_fails(tmp_path: Path) -> None:
    _tree(tmp_path, {"a.txt": "one\n"})
    manifest = _manifest(tmp_path, "SUMS", ("a.txt",))
    _write(tmp_path, "a.txt", "edited\n")

    audit = audit_membership(_scope(tmp_path), (_binding(tmp_path, manifest),))
    assert assess_drift(audit).outcome is Outcome.FAIL
    assert audit.checks[0].drifted == ("a.txt",)
    with pytest.raises(ManifestMembershipNotClosed, match="no longer match their digests"):
        require_closed_membership(audit)


def test_a_named_path_that_is_gone_is_a_violation_not_a_silence(tmp_path: Path) -> None:
    _tree(tmp_path, {"a.txt": "one\n"})
    manifest = _manifest(tmp_path, "SUMS", ("a.txt",))
    (tmp_path / "a.txt").unlink()

    audit = audit_membership(_scope(tmp_path), (_binding(tmp_path, manifest),))
    assert audit.checks[0].missing == ("a.txt",)
    assert assess_drift(audit).outcome is Outcome.FAIL


def test_an_empty_scope_cannot_check_rather_than_pass(tmp_path: Path) -> None:
    empty = tmp_path / "empty"
    empty.mkdir()
    manifest = _write(tmp_path, "SUMS", "")
    scope = ManifestScope(
        scope_id="empty", scope_definition="nothing at all", paths=scope_paths([empty])
    )
    audit = audit_membership(
        scope,
        (
            DigestBinding(
                binding_id="SUMS",
                algorithm=DigestAlgorithm.SHA256,
                base_dir=tmp_path,
                manifest_path=manifest,
                entries=(),
                dereferenced_by="a checker",
            ),
        ),
    )
    assert audit_outcome(audit) is Outcome.CANNOT_CHECK
    assert assess_membership(audit).reason is GuardVerdictReason.NEVER_EXERCISED


def test_a_scope_definition_is_required() -> None:
    with pytest.raises(ValueError, match="scope definition is required"):
        ManifestScope(scope_id="x", scope_definition="   ", paths=frozenset())


def test_an_audit_with_no_bindings_is_refused(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="no bindings"):
        audit_membership(_scope(tmp_path), ())


def test_a_binding_cannot_name_one_path_twice(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="named twice"):
        DigestBinding(
            binding_id="SUMS",
            algorithm=DigestAlgorithm.SHA256,
            base_dir=tmp_path,
            manifest_path=tmp_path / "SUMS",
            entries=(("a.txt", "0" * 64), ("a.txt", "1" * 64)),
            dereferenced_by="a checker",
        )


def test_a_malformed_digest_line_raises_rather_than_being_skipped() -> None:
    with pytest.raises(ValueError, match="malformed digest line 1"):
        parse_digest_manifest("not a digest row\n")
    with pytest.raises(ValueError, match="does not carry a lowercase SHA256"):
        parse_digest_manifest("abc  a.txt\n")
    with pytest.raises(ValueError, match="does not carry a lowercase GIT_BLOB_SHA1"):
        parse_digest_manifest(f"{'0' * 64}  a.txt\n", algorithm=DigestAlgorithm.GIT_BLOB_SHA1)


def test_a_declared_prose_header_is_skipped_and_nothing_after_it_is() -> None:
    text = "a bundle\nSource: /somewhere\nFiles: 1\n\n" + f"{'a' * 64}  a.txt\n"
    assert parse_digest_manifest(text, header_lines=3) == (("a.txt", "a" * 64),)
    with pytest.raises(ValueError, match="malformed digest line 1"):
        parse_digest_manifest(text)


def test_a_mapping_binding_rejects_a_digest_of_the_wrong_algorithm(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="does not carry a lowercase GIT_BLOB_SHA1"):
        binding_from_mapping(
            binding_id="OVERLAY",
            manifest_path=tmp_path / "OVERLAY.json",
            base_dir=tmp_path,
            entries={"a.txt": "0" * 64},
            algorithm=DigestAlgorithm.GIT_BLOB_SHA1,
        )


def test_build_output_is_excluded_from_the_denominator(tmp_path: Path) -> None:
    _tree(tmp_path, {"a.txt": "one\n", "__pycache__/a.cpython-311.pyc": "x", "b.pyc": "y"})
    paths = scope_paths(
        [tmp_path],
        excluded_dir_names={"__pycache__"},
        excluded_suffixes={".pyc"},
    )
    assert {path.name for path in paths} == {"a.txt"}


def test_the_report_names_both_denominators_and_refuses_the_pooled_read(
    tmp_path: Path,
) -> None:
    _tree(tmp_path, {"a.txt": "one\n", "unwatched.txt": "two\n"})
    manifest = _manifest(tmp_path, "SUMS", ("a.txt",))
    audit = audit_membership(_scope(tmp_path), (_binding(tmp_path, manifest),))
    report = audit_report(audit)

    assert report["outcome"] == "FAIL"
    assert report["files_in_scope"] == 3
    assert report["files_enrolled"] == 2
    assert report["files_unenrolled"] == 1
    assert report["drift_verdict"]["outcome"] == "PASS"  # type: ignore[index]
    assert "chosen by the artifact" in str(report["drift_verdict_is_not_the_answer"])
    assert "unwatched.txt" in render_audit(audit)


def test_a_registration_can_be_carried_beside_the_manifests(tmp_path: Path) -> None:
    """An exported package must be auditable with no ORION study module in the loop."""

    _tree(tmp_path, {"a.txt": "one\n", "unwatched.txt": "two\n"})
    manifest = _manifest(tmp_path, "SUMS", ("a.txt",))
    registration = {
        "scope_id": "exported",
        "scope_definition": "everything shipped in the package",
        "scope_roots": [str(tmp_path)],
        "excluded_dir_names": ["__pycache__"],
        "excluded_suffixes": [".pyc"],
        "bindings": [
            {
                "binding_id": "SUMS",
                "manifest_path": str(manifest),
                "base_dir": str(tmp_path),
                "dereferenced_by": "the package's own verifier",
            }
        ],
    }
    audit = audit_from_registration(registration)
    assert audit_outcome(audit) is Outcome.FAIL
    assert [path.name for path in audit.unenrolled] == ["unwatched.txt"]


def test_main_requires_its_argv_and_exits_nonzero_on_an_open_membership(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """``main`` must not read ``sys.argv``.

    ``test_constitutional_boundary.py`` invokes every zero-argument callable in
    ``orion.programme``; one that parsed the test runner's arguments would exit
    the interpreter, and ``SystemExit`` escapes that walker's guard.
    """

    import inspect

    parameter = inspect.signature(main).parameters["argv"]
    assert parameter.default is inspect.Parameter.empty

    _tree(tmp_path, {"a.txt": "one\n", "unwatched.txt": "two\n"})
    manifest = _manifest(tmp_path, "SUMS", ("a.txt",))
    registration = tmp_path / "registration.json"
    registration.write_text(
        json.dumps(
            {
                "scope_id": "exported",
                "scope_definition": "everything shipped in the package",
                "scope_roots": [str(tmp_path)],
                "bindings": [
                    {
                        "binding_id": "SUMS",
                        "manifest_path": str(manifest),
                        "base_dir": str(tmp_path),
                        "dereferenced_by": "the package's own verifier",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    # Two: the file nobody bound, and the registration itself. A registration
    # shipped inside the scope it describes is content like any other.
    assert main([str(registration), "--json"]) == 1
    assert json.loads(capsys.readouterr().out)["files_unenrolled"] == 2
