from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "run_p11c_stronger_decoder_attack_v1.py"
spec = importlib.util.spec_from_file_location("p11c_frozen", SOURCE)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load frozen P11C runner")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def parity_bank_vectorized(x: np.ndarray, subsets: list[tuple[int, ...]]) -> np.ndarray:
    indices = np.asarray(subsets, dtype=np.int16)
    return np.prod(x[:, indices], axis=2, dtype=np.int8)


mod.parity_bank = parity_bank_vectorized
mod.main()
