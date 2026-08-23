#!/usr/bin/env python3
"""Serialization-only execution shim for the frozen QG-7d J7 analyzer.

NumPy 2.x scalar booleans are not accepted by the stdlib JSON encoder.  The
scientific analyzer intentionally remains unchanged; this shim only teaches the
process JSON encoder to convert NumPy scalar objects via `.item()` before
executing that frozen analyzer.
"""
from __future__ import annotations

import json
import runpy

import numpy as np

_ORIGINAL_DEFAULT = json.JSONEncoder.default


def _numpy_scalar_default(self, obj):
    if isinstance(obj, np.generic):
        return obj.item()
    return _ORIGINAL_DEFAULT(self, obj)


json.JSONEncoder.default = _numpy_scalar_default
runpy.run_path("research/extensions/orion-qg/qg7d_j7_pa_confirm.py", run_name="__main__")
