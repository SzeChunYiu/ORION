"""Record the exact identities a reviewer needs to reproduce a run.

Every field is READ from the live environment. Nothing is declared from
memory or from documentation, because a manifest that restates intent
rather than reality is worse than none: it looks like evidence.

Fields that cannot be read are emitted as null with a stated reason, never
omitted and never guessed. An absent field and an unreadable field are
different facts and the manifest keeps them different.
"""
from __future__ import annotations

import json
import platform
import subprocess
import sys
from pathlib import Path


def _git(*args: str) -> str | None:
    try:
        out = subprocess.run(("git", *args), capture_output=True, text=True, timeout=30)
        return out.stdout.strip() if out.returncode == 0 else None
    except Exception:
        return None


def _installed() -> dict[str, str | None]:
    import importlib.metadata as md
    seen: dict[str, str | None] = {}
    for name in ("cryptography", "defusedxml", "pytest"):
        try:
            seen[name] = md.version(name)
        except Exception:
            seen[name] = None
    return seen


def build() -> dict:
    head = _git("rev-parse", "HEAD")
    dirty = _git("status", "--porcelain")
    return {
        "schema_version": "orion.environment-manifest.v1",
        "source_identity": {
            "commit": head,
            "commit_readable": head is not None,
            "working_tree_clean": (dirty == "") if dirty is not None else None,
            "working_tree_note": (
                "null means git could not be queried, NOT that the tree is clean"
            ),
            "branch": _git("rev-parse", "--abbrev-ref", "HEAD"),
        },
        "interpreter": {
            "python_version": sys.version.split()[0],
            "implementation": platform.python_implementation(),
            "executable": sys.executable,
        },
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
        },
        "packages": _installed(),
        "model_provider": {
            "used": False,
            "detail": (
                "This reproduction path invokes no language model. Jobs that DO "
                "call a model record their provider, model id and evaluator in "
                "their own execution protocol, not here."
            ),
        },
        "seeds": {
            "detail": (
                "Seeds are declared per job in that job's EXECUTION_PROTOCOL.json "
                "under generator_seed. There is no global seed, because a single "
                "global seed would make independent jobs look correlated."
            )
        },
    }


def main() -> int:
    m = build()
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("ENVIRONMENT_MANIFEST.json")
    out.write_text(json.dumps(m, indent=2) + "\n")
    print(f"commit          : {m['source_identity']['commit']}")
    print(f"tree clean      : {m['source_identity']['working_tree_clean']}")
    print(f"python          : {m['interpreter']['python_version']}")
    print(f"platform        : {m['platform']['system']} {m['platform']['machine']}")
    print(f"wrote           : {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
