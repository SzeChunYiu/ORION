"""Reusable typed-merge (typed authority) evaluator.

Domain-agnostic implementation of the positive conjunctive powerset-license
least-fixed-point calculus. Encode a domain as a SCHEMA_V1 JSON document and
evaluate it; nothing here is specific to any one domain.

The underlying mathematics is donor-owned. See README.md, "Scope and non-claims".
"""

from .analysis import Report, check_expectations, flat_instance, retraction_report
from .core import (
    Evaluation,
    Instance,
    InstanceError,
    Rule,
    flat_projection,
    least_fixed_point,
    proof_tree,
    retraction,
    transfer,
)
from .enumeration import all_fixed_points
from .model import Problem, SchemaError, SCHEMA_ID

__all__ = [
    "Evaluation", "Instance", "InstanceError", "Problem", "Report", "Rule",
    "SCHEMA_ID", "SchemaError", "all_fixed_points", "check_expectations",
    "flat_instance", "flat_projection", "least_fixed_point", "proof_tree",
    "retraction", "retraction_report", "transfer",
]
__version__ = "1.0.0"
