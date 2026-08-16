import hashlib

import pytest

from orion.providers.development.artifacts import FileSystemDevelopmentArtifactStore


def test_filesystem_development_artifact_store_is_content_addressed_and_durable(tmp_path):
    store = FileSystemDevelopmentArtifactStore(tmp_path / "artifacts")
    content = b"diff --git a/a.py b/a.py\n"
    first = store.put(content, media_type="text/x-diff")
    second = store.put(content, media_type="text/x-diff")

    assert first == second
    assert first.content_hash == hashlib.sha256(content).hexdigest()
    assert store.get(first.artifact_id) == content

    reopened = FileSystemDevelopmentArtifactStore(tmp_path / "artifacts")
    assert reopened.get(first.artifact_id) == content


def test_filesystem_development_artifact_store_detects_posthoc_content_mutation(tmp_path):
    store = FileSystemDevelopmentArtifactStore(tmp_path / "artifacts")
    ref = store.put(b"original", media_type="application/octet-stream")
    digest = ref.content_hash
    data_path = store.root / digest[:2] / digest[2:]
    data_path.write_bytes(b"tampered")

    with pytest.raises(RuntimeError, match="content hash mismatch"):
        store.get(ref.artifact_id)


def test_filesystem_development_artifact_store_refuses_metadata_reinterpretation(tmp_path):
    store = FileSystemDevelopmentArtifactStore(tmp_path / "artifacts")
    store.put(b"same-content", media_type="text/plain")
    with pytest.raises(RuntimeError, match="metadata mismatch"):
        store.put(b"same-content", media_type="application/octet-stream")
