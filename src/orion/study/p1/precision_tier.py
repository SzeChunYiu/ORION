"""Power and precision tier enforcement for ORION-P1.

Binding N and margins BEFORE outcome access — the frozen TEST split (N=48)
cannot resolve the H1 +0.05 superiority margin. This module computes the achieved
tier and enforces the UNDERPOWERED gate.

Derived from PROSPECTIVE_POWER_V1.md, which itself is computed BEFORE any outcome
access using only the frozen margins and frozen N.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum

# Z-score for 95% confidence (two-sided)
Z_95 = 1.959963984540054

# From PROTOCOL_V1.json statistics.practical_margin
H1_SUPERIORITY_MARGIN = 0.05
H2_NON_INFERIORITY_MARGIN = 0.02


class Tier(str, Enum):
    """Precision tiers based on achieved half-width at p=0.5."""

    TIER_A_FULL = "TIER_A_full"
    TIER_B_COMMITTED = "TIER_B_committed"
    TIER_C_REDUCED = "TIER_C_reduced"
    TIER_D_MINIMUM_INFERENTIAL = "TIER_D_minimum_inferential"
    BELOW_TIER_D = "BELOW_TIER_D"


@dataclass(frozen=True)
class TierRule:
    """What a given tier licenses and what it does not."""

    tier: Tier
    half_width: float
    n: int
    #: At this half-width, H1 +0.05 superiority cannot be resolved.
    underpowered: bool
    #: Whether this tier can carry a promoted H1 superiority claim.
    licenses_h1_superiority: bool = False
    #: Whether this tier can carry a promoted H2 non-inferiority claim.
    licenses_h2_non_inferiority: bool = False

    @classmethod
    def from_n(cls, n: int) -> "TierRule":
        """Compute tier from N at the conservative p=0.5."""
        if n <= 0:
            return cls(
                tier=Tier.BELOW_TIER_D,
                half_width=float("inf"),
                n=n,
                underpowered=True,
                licenses_h1_superiority=False,
                licenses_h2_non_inferiority=False,
            )

        half_width = _half_width_at_p(n, 0.5)

        # Determine tier
        tier = Tier.BELOW_TIER_D
        if half_width <= 0.03:
            tier = Tier.TIER_A_FULL
        elif half_width <= 0.05:
            tier = Tier.TIER_B_COMMITTED
        elif half_width <= 0.075:
            tier = Tier.TIER_C_REDUCED
        elif half_width <= 0.10:
            tier = Tier.TIER_D_MINIMUM_INFERENTIAL

        # UNDERPOWERED if half-width exceeds the H1 margin
        underpowered = half_width > H1_SUPERIORITY_MARGIN

        # H1 superiority requires powered resolution at the frozen margin
        licenses_h1 = half_width <= H1_SUPERIORITY_MARGIN

        # H2 non-inferiority is even stricter (0.02 margin)
        licenses_h2 = half_width <= H2_NON_INFERIORITY_MARGIN

        return cls(
            tier=tier,
            half_width=half_width,
            n=n,
            underpowered=underpowered,
            licenses_h1_superiority=licenses_h1,
            licenses_h2_non_inferiority=licenses_h2,
        )

    def to_dict(self) -> dict:
        """Render as a record for the manifest and manuscript."""
        return {
            "tier": self.tier.value,
            "half_width": f"{self.half_width:.4f}",
            "n": self.n,
            "underpowered": self.underpowered,
            "licenses_h1_superiority": self.licenses_h1_superiority,
            "licenses_h2_non_inferiority": self.licenses_h2_non_inferiority,
            "h1_margin": H1_SUPERIORITY_MARGIN,
            "h2_margin": H2_NON_INFERIORITY_MARGIN,
        }


def _half_width_at_p(n: int, p: float) -> float:
    """Normal-approximation Wilson half-width for a binomial proportion."""
    if n <= 0:
        return float("inf")
    # Conservative: binomial variance is p(1-p)/n
    variance = p * (1.0 - p) / n
    return Z_95 * math.sqrt(variance)


def required_n_for_half_width(half_width: float, assumed_p: float = 0.5) -> int:
    """Invert the half-width formula to plan N."""
    if not 0 < half_width < 1:
        raise ValueError("half_width must be in (0, 1)")
    if not 0 < assumed_p < 1:
        raise ValueError("assumed_p must be in (0, 1)")
    return math.ceil((Z_95 * Z_95 * assumed_p * (1.0 - assumed_p)) / (half_width * half_width))


def achieved_tier(n: int) -> tuple[str, float]:
    """Convenience: (tier_name, half_width) for a given N."""
    rule = TierRule.from_n(n)
    return rule.tier.value, rule.half_width


__all__ = [
    "Z_95",
    "H1_SUPERIORITY_MARGIN",
    "H2_NON_INFERIORITY_MARGIN",
    "Tier",
    "TierRule",
    "achieved_tier",
    "required_n_for_half_width",
]
