from __future__ import annotations

import itertools
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
OUT = HERE / "results" / "STRUCTURAL_ACCESSIBILITY_THEORY_V2_VERIFICATION.json"
K_GRID = (1, 3, 5, 7, 9, 11, 13)


def sign(value: int) -> int:
    if value == 0:
        raise ValueError("odd-k sum unexpectedly zero")
    return 1 if value > 0 else -1


def encode(r: tuple[int, ...], block: int) -> tuple[int, ...]:
    u = list(r)
    k = len(r)
    for start in range(0, k, block):
        end = min(k, start + block)
        for j in range(start + 1, end):
            u[j] = r[j] * r[j - 1]
    return tuple(u)


def decode(u: tuple[int, ...], block: int) -> tuple[int, ...]:
    r = list(u)
    k = len(u)
    for start in range(0, k, block):
        end = min(k, start + block)
        for j in range(start + 1, end):
            r[j] = u[j] * r[j - 1]
    return tuple(r)


def frac(value: Fraction) -> dict[str, Any]:
    return {
        "numerator": value.numerator,
        "denominator": value.denominator,
        "float": float(value),
    }


def verify_k(k: int) -> dict[str, Any]:
    worlds = list(itertools.product((-1, 1), repeat=k))
    total = len(worlds)
    labels = [sign(sum(r)) for r in worlds]
    assert sum(labels) == 0, f"label balance failed at k={k}"

    expected_corr = Fraction(math.comb(k - 1, (k - 1) // 2), 2 ** (k - 1))
    correlations: list[Fraction] = []
    for i in range(k):
        corr = Fraction(sum(z * r[i] for z, r in zip(labels, worlds)), total)
        correlations.append(corr)
        assert corr == expected_corr, (k, i, corr, expected_corr)

    expected_abs = Fraction(k * expected_corr.numerator, expected_corr.denominator)
    observed_abs = Fraction(sum(abs(sum(r)) for r in worlds), total)
    assert observed_abs == expected_abs, (k, observed_abs, expected_abs)

    block_rows: list[dict[str, Any]] = []
    block_grid = sorted({1, 2, 4, 8, k})
    for block in block_grid:
        encoded = [encode(r, block) for r in worlds]
        assert len(set(encoded)) == total, f"encoding not bijective at k={k}, b={block}"
        assert all(decode(u, block) == r for r, u in zip(worlds, encoded)), (k, block)

        corr_u: list[Fraction] = []
        leading: list[int] = []
        for j in range(k):
            is_lead = j % block == 0
            if is_lead:
                leading.append(j)
            corr = Fraction(sum(z * u[j] for z, u in zip(labels, encoded)), total)
            corr_u.append(corr)
            if is_lead:
                assert corr == expected_corr, (k, block, j, corr, expected_corr)
            else:
                assert corr == 0, (k, block, j, corr)

        bcount = len(leading)
        # Signal norm squared is rational: B*a^2 versus k*a^2 canonically.
        norm_sq = Fraction(bcount, 1) * expected_corr * expected_corr
        canonical_norm_sq = Fraction(k, 1) * expected_corr * expected_corr
        ratio_sq = norm_sq / canonical_norm_sq
        assert ratio_sq == Fraction(bcount, k)
        block_rows.append({
            "block_length": block,
            "block_count": bcount,
            "leading_positions": leading,
            "nonzero_first_order_correlation_count": sum(c != 0 for c in corr_u),
            "expected_nonzero_count": bcount,
            "first_order_correlation": frac(expected_corr),
            "signal_norm_squared_ratio": frac(ratio_sq),
            "signal_norm_ratio": math.sqrt(float(ratio_sq)),
            "bijective": True,
            "decode_failures": 0,
        })

    return {
        "k": k,
        "world_count": total,
        "balanced_label": True,
        "relation_coordinate_correlation": frac(expected_corr),
        "expected_abs_random_walk": frac(expected_abs),
        "observed_abs_random_walk": frac(observed_abs),
        "all_relation_coordinate_correlations_equal": True,
        "blocks": block_rows,
    }


def main() -> None:
    rows = [verify_k(k) for k in K_GRID]
    result = {
        "schema": "P9P10.StructuralAccessibilityTheoryVerification.v2",
        "theory": "STRUCTURAL_ACCESSIBILITY_THEORY_V2.md",
        "arithmetic": "exact rational enumeration plus reported float projections",
        "k_grid": list(K_GRID),
        "rows": rows,
        "terminal": "STRUCTURAL_ACCESSIBILITY_THEORY_V2_ENUMERATION_VERIFIED",
        "claim_boundary": "Finite exact enumeration validates theorem identities on the stated grid; analytic proofs, not enumeration, carry the all-odd-k statements.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    OUT.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
