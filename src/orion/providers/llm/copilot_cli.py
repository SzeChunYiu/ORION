from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from .base import LLMProvider, LLMRequest, LLMResponse


@dataclass(frozen=True)
class CopilotCLIConfig:
    model: str
    token: str = field(repr=False)
    cli_version: str
    executable: str = "copilot"
    timeout_seconds: float = 180.0

    def __post_init__(self) -> None:
        if not self.model.strip() or not self.token.strip() or not self.cli_version.strip():
            raise ValueError("Copilot CLI model, token and frozen CLI version are required")
        if self.executable != "copilot":
            raise ValueError("Copilot CLI executable identity is frozen to 'copilot'")
        if self.timeout_seconds <= 0:
            raise ValueError("Copilot CLI timeout must be positive")

    @property
    def public_identity(self) -> dict[str, object]:
        return {
            "provider": "github-copilot-cli",
            "model": self.model,
            "cli_version": self.cli_version,
            "programmatic": True,
            "tool_access": "DENIED",
            "timeout_seconds": self.timeout_seconds,
        }


class CopilotCLILLMProvider(LLMProvider):
    """Prompt-only GitHub Copilot CLI adapter for protected Actions runs.

    Each request executes in a fresh empty directory with a minimal environment.
    Built-in MCPs and all shell/read/write/url/memory tools are denied. The
    GitHub token is transport-only and never enters prompts or public identity.
    """

    def __init__(self, config: CopilotCLIConfig) -> None:
        self.config = config

    @staticmethod
    def _prompt(request: LLMRequest) -> str:
        pieces = [
            "SYSTEM INSTRUCTION:\n" + request.system,
            "TASK:\n" + request.task,
            "USER REQUEST:\n" + request.user,
        ]
        if request.response_schema:
            try:
                schema = json.loads(request.response_schema)
            except json.JSONDecodeError as error:
                raise ValueError("LLMRequest response_schema must be valid JSON") from error
            if not isinstance(schema, dict):
                raise ValueError("LLMRequest response_schema must decode to a JSON object")
            pieces.append(
                "OUTPUT CONTRACT:\nReturn only valid JSON matching this contract. "
                "Do not use Markdown fences.\n" + request.response_schema
            )
        return "\n\n".join(pieces)

    def _environment(self, home: Path) -> dict[str, str]:
        path = os.environ.get("PATH", "")
        return {
            "PATH": path,
            "HOME": str(home),
            "CI": "true",
            "NO_COLOR": "1",
            "COPILOT_AUTO_UPDATE": "false",
            "COPILOT_GITHUB_TOKEN": self.config.token,
            "GITHUB_TOKEN": self.config.token,
        }

    def complete(self, request: LLMRequest) -> LLMResponse:
        prompt = self._prompt(request)
        with tempfile.TemporaryDirectory(prefix="orion-copilot-reasoner-") as directory:
            root = Path(directory)
            home = root / "home"
            work = root / "work"
            home.mkdir()
            work.mkdir()
            command = [
                self.config.executable,
                "-s",
                "-p",
                prompt,
                "--model",
                self.config.model,
                "--no-ask-user",
                "--disable-builtin-mcps",
                "--deny-tool=shell",
                "--deny-tool=write",
                "--deny-tool=read",
                "--deny-tool=url",
                "--deny-tool=memory",
                "--excluded-tools=task,skill,web_fetch,bash,edit,view,grep,glob",
                "--secret-env-vars=COPILOT_GITHUB_TOKEN,GITHUB_TOKEN",
            ]
            try:
                completed = subprocess.run(
                    command,
                    cwd=work,
                    env=self._environment(home),
                    capture_output=True,
                    text=True,
                    timeout=self.config.timeout_seconds,
                    check=False,
                )
            except subprocess.TimeoutExpired as error:
                raise RuntimeError("Copilot CLI reasoner timed out") from error
            if completed.returncode != 0:
                stderr = completed.stderr.strip()
                raise RuntimeError(
                    "Copilot CLI reasoner failed: " + (stderr[:1000] or f"exit {completed.returncode}")
                )
            content = completed.stdout.strip()
            if not content:
                raise RuntimeError("Copilot CLI reasoner returned empty output")
            response_id = "copilot-cli-response:" + hashlib.sha256(
                content.encode("utf-8")
            ).hexdigest()
            return LLMResponse(
                content=content,
                model_id=self.config.model,
                response_id=response_id,
            )


__all__ = ["CopilotCLIConfig", "CopilotCLILLMProvider"]
