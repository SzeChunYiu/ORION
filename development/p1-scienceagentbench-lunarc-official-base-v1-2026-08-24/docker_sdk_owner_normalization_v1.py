"""Normalize Docker SDK build-context tar ownership for single-map rootless runtimes.

Docker SDK 7.1.0 copies the invoking filesystem UID/GID into every context-tar
member.  A rootless Podman service without subordinate UID/GID ranges cannot
unpack those members.  This narrowly scoped adapter retains every path, byte,
mode, link, and timestamp while forcing only tar UID/GID metadata to zero.
"""

from __future__ import annotations

import shutil
import tarfile
import tempfile
from typing import Any


_INSTALLED = False


def install() -> None:
    global _INSTALLED
    if _INSTALLED:
        return

    import docker.utils.build as docker_build_utils

    original = docker_build_utils.create_archive

    def normalized_create_archive(*args: Any, **kwargs: Any):
        source = original(*args, **kwargs)
        normalized = tempfile.NamedTemporaryFile()
        with tarfile.open(mode="r:*", fileobj=source) as src, tarfile.open(
            mode="w", fileobj=normalized
        ) as dst:
            for member in src.getmembers():
                payload = src.extractfile(member) if member.isfile() else None
                member.uid = 0
                member.gid = 0
                member.uname = "root"
                member.gname = "root"
                dst.addfile(member, payload)
        try:
            source.close()
        except Exception:
            pass
        normalized.seek(0)
        return normalized

    docker_build_utils.create_archive = normalized_create_archive
    _INSTALLED = True
