#!/usr/bin/env python3
"""Serialization-only execution shim for the independent QG-7d J7 generic verifier.

The frozen generic verifier computes some check values with NumPy scalar boolean
results.  This shim only converts NumPy scalar objects via `.item()` for JSON
serialization; no scientific computation, expected fingerprint, or gate changes.
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
runpy.run_path(
    "development/orion-qg-regime-geometry/qg7d_j7_pa_generic_verify.py",
    run_name="__main__",
)
