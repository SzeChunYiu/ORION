"""Compatibility facade for the leak-resistant zero-error Jump benchmark V2.

V1 was superseded after PR #558 review found pre-experiment protected-class
leakage.  All executable imports now resolve to the V2 implementation.  The V1
protocol/expected artifacts remain in research history only and are not an
executable scientific authority.
"""

from .zero_error_jump_benchmark_v2 import *  # noqa: F401,F403
from .zero_error_jump_benchmark_v2 import __all__
