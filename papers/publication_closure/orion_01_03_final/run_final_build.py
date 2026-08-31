#!/usr/bin/env python3
from __future__ import annotations

import build_final_packages as b

_original_publication_markdown = b.publication_markdown


def publication_markdown(spec: b.Spec) -> str:
    text = _original_publication_markdown(spec)
    if spec.key == "ORION-02":
        text = text.replace(
            "The first counted revival attempt, the first study, asked",
            "The first counted held-out revival study asked",
        )
        text = text.replace(
            "The second counted attempt, the second study, evaluated",
            "The second counted held-out certificate study evaluated",
        )
        text = text.replace(
            "Against a corrected exact-cell parent",
            "Against the corrected exact-cell parent method",
        )
        text = text.replace(
            "Across both counted attempts the same negative control was at least as strong on the recorded criteria as the specified geometry.",
            "Across both counted attempts the same outcome-independent negative control was at least as strong as the specified geometry on the recorded criteria.",
        )
        text = text.replace(
            "A subsequent diagnostic on the same committed records",
            "A subsequent diagnostic on the same frozen records",
        )
        text = text.replace(
            "The preserved the second study result illustrates",
            "The preserved second-study result illustrates",
        )
    return text


b.publication_markdown = publication_markdown

if __name__ == "__main__":
    raise SystemExit(b.main())
