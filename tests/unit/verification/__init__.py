"""Package marker so pytest does not collect this directory by basename.

``tests/unit/study/global_positive/test_schema.py`` and
``tests/unit/verification/test_schema.py`` share a basename. Without this file,
pytest imports both as ``test_schema`` and aborts collection for the whole
suite — the same trap recorded on PR #276.
"""
