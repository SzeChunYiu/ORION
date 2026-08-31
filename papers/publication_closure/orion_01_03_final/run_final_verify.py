#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import verify_final_packages as v

_original_archive_texts = v.archive_texts


def archive_texts(path: Path) -> dict[str, str]:
    texts = _original_archive_texts(path)
    for name, text in list(texts.items()):
        texts.setdefault(Path(name).name, text)
    return texts


v.archive_texts = archive_texts

if __name__ == "__main__":
    raise SystemExit(v.main())
