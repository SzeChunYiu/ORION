r"""Read the manuscript LaTeX actually builds, not just its entry file.

Splitting a paper into ``sections/`` moves every sentence out of ``main.tex``
and leaves the preamble behind. Anything that checked manuscript *content* by
reading ``main.tex`` therefore keeps working and stops checking: the required
phrases are absent, the forbidden ones are absent, and the assertion passes on
an empty reading. That is a guard reporting "nothing failed" for "nothing ran",
and splitting P9 introduced exactly it --- its audit polices citation keys,
pending markers and overclaim phrases, and after the split it read a preamble.

So the split and this module belong together. A caller that wants the
manuscript's prose asks for :func:`assemble`, and gets the same document
``pdflatex`` sees.
"""

from __future__ import annotations

import re
from pathlib import Path

#: ``\input{...}`` and ``\include{...}``, the two ways a LaTeX file pulls in
#: another. ``\usepackage`` is deliberately not here: a style file is not
#: manuscript prose.
_INCLUDE = re.compile(r"\\(?:input|include)\{([^}]+)\}")


def assemble(entry: Path, *, _seen: frozenset[Path] = frozenset()) -> str:
    r"""``entry`` with every file it includes, resolved recursively.

    Paths resolve relative to ``entry``'s own directory, which is how LaTeX
    resolves them when it is run there. A missing file or an include cycle
    leaves the unresolved line in place rather than raising: the caller's job is
    to judge manuscript content, and a broken include is the LaTeX build's
    failure to report, not this function's.
    """

    entry = Path(entry)
    text = entry.read_text(encoding="utf-8")
    seen = _seen | {entry.resolve()}
    root = entry.parent

    def expand(match: re.Match[str]) -> str:
        target = root / match.group(1)
        if target.suffix != ".tex":
            target = target.with_suffix(".tex")
        if not target.is_file() or target.resolve() in seen:
            return match.group(0)
        return match.group(0) + "\n" + assemble(target, _seen=seen)

    return _INCLUDE.sub(expand, text)


__all__ = ["assemble"]
