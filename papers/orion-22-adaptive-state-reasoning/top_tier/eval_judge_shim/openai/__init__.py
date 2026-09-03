"""Drop-in ``openai`` module shim for the pinned ScienceAgentBench evaluator.

WHY THIS EXISTS
---------------
The pinned upstream evaluator (OSU-NLP-Group/ScienceAgentBench @
c26e151ed601ba109dc4d35e057ff8e73fec469d) scores plot tasks through
``gpt4_visual_judge.py``, which calls
``client.chat.completions.create(..., model="gpt-4o-2024-05-13", n=3)`` and
therefore requires an OPENAI_API_KEY (or Azure credentials). The P12 campaign
model-identity freeze (MODEL_IDENTITY_FREEZE_V1.json) pins TWO CLI lanes and
explicitly records that no API keys exist. The operator directive for this
campaign authorizes the CLI-lane pattern as the judge substitute.

WHAT THIS SHIM DOES
-------------------
When this directory is FIRST on PYTHONPATH, ``from openai import OpenAI,
AzureOpenAI`` inside the (unmodified) upstream ``gpt4_visual_judge.py``
imports this module instead. ``create()`` routes each of the ``n`` samples to
one ``codex exec`` invocation of the frozen GPT_CLASS lane, attaching the two
figures with ``-i`` (image input), and returns response objects shaped exactly
like the upstream client's (``choices[i].message.content``). The upstream
``[FINAL SCORE]`` regex parsing, the n-sample averaging, and the >= 60
threshold all remain the upstream code, byte for byte.

FIDELITY DEVIATIONS (recorded in P12_JUDGE_SUBSTITUTION_RECEIPT_V1.md)
----------------------------------------------------------------------
- judge model: gpt-5.5 via codex CLI (frozen lane) instead of
  gpt-4o-2024-05-13 via API; uniform across ALL judged cells of BOTH tested
  model families (the judge prompt is identity-blind: two figures + rubric).
- temperature/top_p/presence/frequency penalties are not controllable through
  the CLI (provider-default decoding); the n=3 sample averaging is preserved
  by issuing n separate CLI calls.
- a failed CLI call (nonzero rc / timeout / missing binary) raises, mirroring
  the upstream behavior on an API error, so the eval driver records an
  infrastructure failure instead of a silent zero.

This module performs NO campaign decisions, reads NO campaign artifacts, and
must only be placed on PYTHONPATH by campaign_eval_driver_v1.py.
"""

from __future__ import annotations

import base64
import datetime as _dt
import json
import os
import re
import subprocess
import tempfile
import time
from pathlib import Path

_SCORE_RE = re.compile(r"\[FINAL SCORE\]: (\d{1,3})", re.DOTALL)
_DATAURL_RE = re.compile(r"^data:image/[a-zA-Z0-9.+-]+;base64,(.*)$", re.DOTALL)

JUDGE_BIN = os.environ.get("P12_JUDGE_BIN", "codex")
JUDGE_TIMEOUT = int(os.environ.get("P12_JUDGE_TIMEOUT", "600"))
JUDGE_LOG_DIR = os.environ.get("P12_JUDGE_LOG_DIR", "")


def parse_final_score(text: str) -> int:
    """Upstream regex semantics: first [FINAL SCORE]: N in the response."""
    m = _SCORE_RE.search(text or "")
    return int(m.group(1).strip()) if m else 0


def _extract_content_parts(messages: list) -> tuple[str, list[str]]:
    """Return (text, [image file paths]) from the single user message."""
    text_parts: list[str] = []
    image_paths: list[str] = []
    for msg in messages:
        content = msg.get("content")
        if isinstance(content, str):
            text_parts.append(content)
            continue
        for part in content or []:
            t = part.get("type")
            if t == "text":
                text_parts.append(part.get("text", ""))
            elif t == "image_url":
                url = part.get("image_url", {}).get("url", "")
                m = _DATAURL_RE.match(url)
                if not m:
                    raise RuntimeError("judge shim: non-data-URL image part")
                suffix = ".png"
                f = tempfile.NamedTemporaryFile(
                    "wb", delete=False, suffix=suffix, prefix="p12_judge_img_"
                )
                f.write(base64.b64decode(m.group(1)))
                f.close()
                image_paths.append(f.name)
    return "\n".join(text_parts), image_paths


def _log_call(entry: dict) -> None:
    if not JUDGE_LOG_DIR:
        return
    try:
        d = Path(JUDGE_LOG_DIR)
        d.mkdir(parents=True, exist_ok=True)
        with open(d / "judge_calls.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass  # transcript logging must never break the judge path


class _Message:
    def __init__(self, content: str):
        self.content = content


class _Choice:
    def __init__(self, content: str):
        self.message = _Message(content)
        self.finish_reason = "stop"


class _Response:
    def __init__(self, contents: list[str]):
        self.choices = [_Choice(c) for c in contents]


class _Completions:
    def create(
        self,
        *,
        messages: list,
        temperature: float | None = None,
        max_tokens: int | None = None,
        n: int = 1,
        top_p: float | None = None,
        frequency_penalty: float | None = None,
        presence_penalty: float | None = None,
        model: str | None = None,
        **kwargs,
    ) -> _Response:
        text, image_paths = _extract_content_parts(messages)
        contents: list[str] = []
        for sample in range(max(1, n)):
            # `-i/--image <FILE>...` is VARIADIC in codex-cli 0.129.0-alpha.15:
            # a positional prompt appended after the images is consumed as
            # another image and codex falls back to stdin ("No prompt provided
            # via stdin", judge-smoke job 3570426). The prompt therefore goes
            # through stdin (`codex exec` reads it when no positional PROMPT
            # is given), which is also immune to dash-prefixed prompt text.
            # --skip-git-repo-check: the campaign tree is a plain mirror (not
            # a git repo) on the execution host; codex refuses otherwise
            # ("Not inside a trusted directory", judge-smoke job 3570430).
            cmd = [JUDGE_BIN, "exec", "--skip-git-repo-check"]
            for img in image_paths:
                cmd += ["-i", img]
            t0 = time.time()
            try:
                proc = subprocess.run(
                    cmd, input=text, capture_output=True, text=True,
                    timeout=JUDGE_TIMEOUT, check=False,
                )
            except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                _log_call(
                    {
                        "ts_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(),
                        "sample": sample,
                        "rc": None,
                        "seconds": round(time.time() - t0, 2),
                        "error": repr(e),
                        "prompt_chars": len(text),
                        "images": len(image_paths),
                    }
                )
                raise RuntimeError(f"judge shim: codex call failed: {e!r}")
            _log_call(
                {
                    "ts_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(),
                    "sample": sample,
                    "rc": proc.returncode,
                    "seconds": round(time.time() - t0, 2),
                    "stdout_tail": (proc.stdout or "")[-2000:],
                    "stderr_tail": (proc.stderr or "")[-2000:],
                    "prompt_chars": len(text),
                    "images": len(image_paths),
                }
            )
            if proc.returncode != 0:
                raise RuntimeError(
                    "judge shim: codex call rc="
                    f"{proc.returncode}: {(proc.stderr or '')[-500:]}"
                )
            contents.append(proc.stdout or "")
        return _Response(contents)


class _Chat:
    def __init__(self):
        self.completions = _Completions()


class OpenAI:
    """Minimal shape-compatible replacement for openai.OpenAI (judge path)."""

    def __init__(self, *args, **kwargs):
        self.chat = _Chat()


class AzureOpenAI(OpenAI):
    """Same codex-backed judge path as OpenAI.

    The unmodified upstream ``gpt4_visual_judge.py`` selects its client class
    at module level by ``os.getenv("OPENAI_API_KEY")``; this campaign sets no
    API key (MODEL_IDENTITY_FREEZE_V1.json: CLI lanes only), so upstream
    ALWAYS constructs ``AzureOpenAI`` — the raising constructor here made the
    frozen judge substitution unreachable in every real eval (14/68 cells in
    sbatch 3572226). P12_HARNESS_AMENDMENT_JUDGE_ENGAGEMENT_V1.json: delegate
    to the identical inherited ``_Chat`` instead of raising. The judge
    invocation (codex exec argv, stdin prompt, ``-i`` figures), lane identity,
    upstream ``[FINAL SCORE]`` parsing, and the >= 60 threshold are unchanged
    for both client classes.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


__all__ = ["OpenAI", "AzureOpenAI", "parse_final_score"]
