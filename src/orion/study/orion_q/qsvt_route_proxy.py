"""Donor-complete asymptotic proxy for a two-route QSVT diagnostic.

This module deliberately encodes only the published scaling forms frozen in the
QC-4A development packet. It exists to test whether a learned P9 route selector
has any scientific role in the simplest standard-vs-randomized abstraction.

The proxy ignores hidden constants and polylogarithmic factors and therefore has
no authority over a concrete workload. It also does not erase route-specific
access assumptions. Those limitations are part of every receipt.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math

from orion.transfer.v2.canonical import content_digest


class QSVTRoute(str, Enum):
    STANDARD_BLOCK_ENCODED = "STANDARD_BLOCK_ENCODED"
    RANDOMIZED = "RANDOMIZED"


class DepthPreference(str, Enum):
    STANDARD = "STANDARD_DEPTH_PROXY_LOWER"
    RANDOMIZED = "RANDOMIZED_DEPTH_PROXY_LOWER"
    NO_DOMINANCE = "NO_DEPTH_PROXY_DOMINANCE"


@dataclass(frozen=True)
class QSVTProxyParameters:
    """Common LCU/LCH proxy parameters for the frozen two-route comparison."""

    term_count: int
    lambda_l1: float
    polynomial_degree: int

    def verify(self) -> None:
        if not isinstance(self.term_count, int) or isinstance(self.term_count, bool):
            raise ValueError("term_count must be an integer")
        if self.term_count <= 0:
            raise ValueError("term_count must be positive")
        if not math.isfinite(self.lambda_l1) or self.lambda_l1 <= 0:
            raise ValueError("lambda_l1 must be finite and positive")
        if not isinstance(self.polynomial_degree, int) or isinstance(
            self.polynomial_degree, bool
        ):
            raise ValueError("polynomial_degree must be an integer")
        if self.polynomial_degree <= 0:
            raise ValueError("polynomial_degree must be positive")

    @property
    def standard_depth_proxy(self) -> float:
        """Return the stripped scaling proxy L * lambda * d."""

        self.verify()
        return float(self.term_count * self.lambda_l1 * self.polynomial_degree)

    @property
    def randomized_depth_proxy(self) -> float:
        """Return the stripped scaling proxy lambda^2 * d^2."""

        self.verify()
        return float((self.lambda_l1 * self.polynomial_degree) ** 2)

    @property
    def crossover_term_count(self) -> float:
        """Return the algebraic crossover L = lambda*d for the stripped proxies."""

        self.verify()
        return float(self.lambda_l1 * self.polynomial_degree)

    def depth_preference(self) -> DepthPreference:
        """Compare only the frozen stripped depth proxies."""

        standard = self.standard_depth_proxy
        randomized = self.randomized_depth_proxy
        if randomized < standard:
            return DepthPreference.RANDOMIZED
        if standard < randomized:
            return DepthPreference.STANDARD
        return DepthPreference.NO_DOMINANCE

    def algebraic_depth_preference(self) -> DepthPreference:
        """Use the closed-form donor crossover rather than evaluating both proxies."""

        self.verify()
        crossover = self.crossover_term_count
        if self.term_count > crossover:
            return DepthPreference.RANDOMIZED
        if self.term_count < crossover:
            return DepthPreference.STANDARD
        return DepthPreference.NO_DOMINANCE

    def receipt(self) -> dict[str, object]:
        """Return a non-authorizing diagnostic receipt with caveats made explicit."""

        self.verify()
        payload: dict[str, object] = {
            "schema": "ORIONQ.QSVTTwoRouteAsymptoticProxy.v1",
            "parameters": {
                "term_count_L": self.term_count,
                "lambda_l1": self.lambda_l1,
                "polynomial_degree_d": self.polynomial_degree,
            },
            "depth_proxy": {
                QSVTRoute.STANDARD_BLOCK_ENCODED.value: self.standard_depth_proxy,
                QSVTRoute.RANDOMIZED.value: self.randomized_depth_proxy,
            },
            "depth_scaling_forms": {
                QSVTRoute.STANDARD_BLOCK_ENCODED.value: "O_tilde(L * lambda * d)",
                QSVTRoute.RANDOMIZED.value: "O_tilde(lambda^2 * d^2)",
            },
            "ancilla_information": {
                QSVTRoute.STANDARD_BLOCK_ENCODED.value: "O(log L)",
                QSVTRoute.RANDOMIZED.value: 1,
            },
            "crossover_rule": "randomized depth proxy lower iff L > lambda*d",
            "crossover_term_count": self.crossover_term_count,
            "depth_preference": self.depth_preference().value,
            "limitations": {
                "asymptotic_proxy_only": True,
                "hidden_constants_unresolved": True,
                "polylogarithmic_factors_unresolved": True,
                "access_model_matching_required": True,
                "compiled_resource_claim_authorized": False,
                "scientific_route_authority": False,
            },
        }
        payload["receipt_digest"] = content_digest(payload)
        return payload


__all__ = [
    "DepthPreference",
    "QSVTProxyParameters",
    "QSVTRoute",
]
