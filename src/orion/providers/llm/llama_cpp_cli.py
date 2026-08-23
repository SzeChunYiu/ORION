from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .base import LLMProvider, LLMRequest, LLMResponse


_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def sha256_file(path: Path | str) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_sha256(value: str, field: str) -> None:
    if not _SHA256_RE.fullmatch(value):
        raise ValueError(f"{field} must be a lowercase SHA-256 hex digest")


@dataclass(frozen=True)
class LlamaCppCLIConfig:
    executable: str
    executable_sha256: str
    runtime_release_tag: str
    runtime_commit: str
    runtime_asset_sha256: str
    model_path: str
    model_sha256: str
    model_repo_id: str
    model_revision: str
    model_filename: str
    model_family: str
    context_size: int = 4096
    max_tokens: int = 512
    seed: int = 20260817
    timeout_seconds: float = 300.0

    def __post_init__(self) -> None:
        for field, value in (
            ("executable_sha256", self.executable_sha256),
            ("runtime_asset_sha256", self.runtime_asset_sha256),
            ("model_sha256", self.model_sha256),
        ):
            _require_sha256(value, field)
        if not self.runtime_release_tag.strip() or not self.runtime_commit.strip():
            raise ValueError("llama.cpp release tag and commit are required")
        if not self.model_repo_id.strip() or not self.model_revision.strip() or not self.model_filename.strip():
            raise ValueError("model repository, revision and filename are required")
        if not self.model_family.strip():
            raise ValueError("model_family is required")
        if self.context_size <= 0 or self.max_tokens <= 0 or self.timeout_seconds <= 0:
            raise ValueError("llama.cpp context, max tokens and timeout must be positive")
        executable = Path(self.executable)
        model = Path(self.model_path)
        if not executable.is_file():
            raise ValueError("llama.cpp executable does not exist")
        if not model.is_file():
            raise ValueError("llama.cpp model file does not exist")
        if sha256_file(executable) != self.executable_sha256:
            raise ValueError("llama.cpp executable SHA-256 mismatch")
        if sha256_file(model) != self.model_sha256:
            raise ValueError("llama.cpp model SHA-256 mismatch")

    @property
    def public_identity(self) -> dict[str, object]:
        return {
            "provider": "llama-cpp-cli-open-weight",
            "runtime_release_tag": self.runtime_release_tag,
            "runtime_commit": self.runtime_commit,
            "runtime_asset_sha256": self.runtime_asset_sha256,
            "runtime_binary_sha256": self.executable_sha256,
            "model_repo_id": self.model_repo_id,
            "model_revision": self.model_revision,
            "model_filename": self.model_filename,
            "model_sha256": self.model_sha256,
            "model_family": self.model_family,
            "context_size": self.context_size,
            "max_tokens": self.max_tokens,
            "seed": self.seed,
            "timeout_seconds": self.timeout_seconds,
            "tool_access": "NONE",
        }


class LlamaCppCLILLMProvider(LLMProvider):
    """Content-addressed local inference via a pinned llama.cpp binary/model.

    Calls execute in fresh empty directories with a minimal environment. The
    model has no tool/plugin surface; all retrieval is supplied through ORION's
    provider ports rather than by the model process itself.
    """

    def __init__(self, config: LlamaCppCLIConfig) -> None:
        self.config = config

    @staticmethod
    def _schema_contract(request: LLMRequest) -> tuple[str | None, str]:
        if not request.response_schema:
            return None, request.user
        try:
            schema = json.loads(request.response_schema)
        except json.JSONDecodeError as error:
            raise ValueError("LLMRequest response_schema must be valid JSON") from error
        if not isinstance(schema, dict):
            raise ValueError("LLMRequest response_schema must decode to a JSON object")
        if "type" in schema:
            return request.response_schema, request.user
        return (
            None,
            request.user
            + "\n\nOUTPUT CONTRACT: Return only JSON matching this example shape exactly: "
            + request.response_schema,
        )

    @staticmethod
    def _minimal_env(home: Path) -> dict[str, str]:
        return {
            "PATH": os.environ.get("PATH", ""),
            "HOME": str(home),
            "LC_ALL": "C.UTF-8",
            "LANG": "C.UTF-8",
            "NO_COLOR": "1",
        }

    def complete(self, request: LLMRequest) -> LLMResponse:
        formal_schema, user = self._schema_contract(request)
        prompt = f"TASK: {request.task}\n\n{user}"
        with tempfile.TemporaryDirectory(prefix="orion-llama-reasoner-") as directory:
            root = Path(directory)
            home = root / "home"
            work = root / "work"
            home.mkdir()
            work.mkdir()
            command = [
                self.config.executable,
                "-m",
                self.config.model_path,
                "-st",
                "--simple-io",
                "--no-warmup",
                "--no-display-prompt",
                "--no-show-timings",
                "--temp",
                "0",
                "--seed",
                str(self.config.seed),
                "-c",
                str(self.config.context_size),
                "-n",
                str(self.config.max_tokens),
                "-sys",
                request.system,
                "-p",
                prompt,
            ]
            if formal_schema is not None:
                command.extend(("--json-schema", formal_schema))
            try:
                completed = subprocess.run(
                    command,
                    cwd=work,
                    env=self._minimal_env(home),
                    capture_output=True,
                    text=True,
                    timeout=self.config.timeout_seconds,
                    check=False,
                )
            except subprocess.TimeoutExpired as error:
                raise RuntimeError("llama.cpp reasoner timed out") from error
        if completed.returncode != 0:
            stderr = completed.stderr.strip()
            raise RuntimeError(
                "llama.cpp reasoner failed: " + (stderr[:1000] or f"exit {completed.returncode}")
            )
        content = completed.stdout.strip()
        if not content:
            raise RuntimeError("llama.cpp reasoner returned empty output")
        response_id = "llama-cpp-response:" + hashlib.sha256(
            content.encode("utf-8")
        ).hexdigest()
        return LLMResponse(
            content=content,
            model_id=(
                f"{self.config.model_repo_id}@{self.config.model_revision}/"
                f"{self.config.model_filename}#{self.config.model_sha256}"
            ),
            response_id=response_id,
        )


__all__ = ["LlamaCppCLIConfig", "LlamaCppCLILLMProvider", "sha256_file"]
