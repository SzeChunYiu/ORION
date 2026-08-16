import errno
import os
from pathlib import Path

from orion.kernel.evidence import EvidenceStatus, _classify_open_error_for_role


def test_parent_directory_permission_failure_is_unreadable_not_nonregular(tmp_path: Path):
    parent = tmp_path / "parent"
    parent.mkdir()
    root_fd = os.open(tmp_path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        status = _classify_open_error_for_role(
            OSError(errno.EACCES, "permission denied"),
            root_fd,
            "parent",
            require_directory=True,
        )
    finally:
        os.close(root_fd)
    assert status is EvidenceStatus.UNREADABLE_ARTIFACT


def test_parent_resource_failure_is_unreadable_not_nonregular(tmp_path: Path):
    parent = tmp_path / "parent"
    parent.mkdir()
    root_fd = os.open(tmp_path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        status = _classify_open_error_for_role(
            OSError(errno.EMFILE, "too many files"),
            root_fd,
            "parent",
            require_directory=True,
        )
    finally:
        os.close(root_fd)
    assert status is EvidenceStatus.UNREADABLE_ARTIFACT


def test_linux_enotdir_on_parent_symlink_remains_symlink_disallowed(tmp_path: Path):
    target = tmp_path / "target"
    target.mkdir()
    (tmp_path / "linked").symlink_to(target, target_is_directory=True)
    root_fd = os.open(tmp_path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        status = _classify_open_error_for_role(
            OSError(errno.ENOTDIR, "no-follow symlink"),
            root_fd,
            "linked",
            require_directory=True,
        )
    finally:
        os.close(root_fd)
    assert status is EvidenceStatus.SYMLINK_DISALLOWED


def test_regular_file_used_as_parent_is_nonregular_for_directory_role(tmp_path: Path):
    (tmp_path / "file").write_text("payload")
    root_fd = os.open(tmp_path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        status = _classify_open_error_for_role(
            OSError(errno.ENOTDIR, "not a directory"),
            root_fd,
            "file",
            require_directory=True,
        )
    finally:
        os.close(root_fd)
    assert status is EvidenceStatus.NON_REGULAR_FILE
