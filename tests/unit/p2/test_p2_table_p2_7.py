from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPT = Path(
    "papers/orion-12-open-world-scientific-discovery/scripts/render_table_p2_7.py"
)


def test_table_p2_7_matches_source_probe_json_files() -> None:
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--check"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr or completed.stdout
    assert "matches source probe JSON files" in completed.stdout


def test_table_p2_7_labels_not_claimed_items() -> None:
    table = Path(
        "papers/orion-12-open-world-scientific-discovery/protocol/TABLE_P2-7_wide_deep_comparison.md"
    )
    text = table.read_text(encoding="utf-8")
    assert "Not claimed:" in text
    assert "matched ORION-vs-baseline superiority" in text
    assert "DEEP_OFFICIAL_ARCHIVE_V1.json" in text
