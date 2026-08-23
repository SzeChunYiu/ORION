"""Make the repository root importable for the candidate lane.

``tests/unit/candidates/test_p6_p10_evidence_closure.py`` imports
``papers.candidates.reproducibility_generators_v3`` as a package. ``pyproject``
puts only ``src`` on ``pythonpath``, so that import raised
``ModuleNotFoundError: No module named 'papers'`` and interrupted collection for
the whole ``fast`` lane -- one unimportable module reds every other test in the
job. ``papers`` and ``papers.candidates`` carry no ``__init__.py`` and resolve as
PEP 420 namespace packages once the root is on ``sys.path``.

Scoped to this directory rather than added to ``pythonpath`` globally: only the
candidate lane imports out of ``papers/``, and widening the root import path for
the entire suite would let ``tests/``, ``scripts/`` and ``research/`` shadow
installed distributions.

Mirrors ``tests/unit/verification/conftest.py``, which does the same for
``research/verification``.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
