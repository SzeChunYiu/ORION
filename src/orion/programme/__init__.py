"""Phase-4 programme scaffolding — pre-registration only.

This package is a **frozen protocol and schema layer for issue #210**, which is
blocked on #209, which is blocked on #76. Nothing here is wired into a runtime
path, no gate is closed by importing it, and no authority is granted by any
value it returns. It exists so that the Phase-4 record shapes, the dependency
invalidation model and the anti-collapse battery are pinned *before* protected
evidence exists, rather than shaped afterwards to fit whatever evidence arrives.

Layout
------
``identity``            content/lineage binding, schema ids, sealing
``records``             shared vocabulary: three-valued Outcome, authority, provenance
``coordinates``         typed K/W/M state coordinates, reused from ``orion.registry``
``object_knowledge``    layer 1 — claims, provenance, plural views, dependencies
``search_universe_knowledge``  layer 2 — versioned W, coverage, blind spots, reopen rules
``method_knowledge``    layer 3 — method identity, applicability, causal support, transfer
``dependency``          typed invalidation edges, reopen events, append-only ledger
``programme_state``     what the checks are allowed to observe
``hostile``             fail-closed check framework
``checks_evidence`` / ``checks_diversity`` / ``catalogue``  the anti-collapse battery
``protocol``            the versioned protocol document and constitutional invariants
"""

from orion.programme.catalogue import (
    ALL_CHECK_IDS,
    ALL_CHECKS,
    run_anti_collapse_battery,
    validate_catalogue,
)
from orion.programme.hostile import (
    CheckResult,
    HostileCheck,
    HostileCheckReport,
    run_hostile_checks,
)
from orion.programme.protocol import (
    CONSTITUTIONAL_INVARIANTS,
    PROGRAMME_STATUS,
    PROTOCOL_VERSION,
    ProgrammeReadinessReport,
    assess_programme_readiness,
    build_protocol_document,
)
from orion.programme.records import ObjectAuthority, Outcome, ProvenanceBinding, RouteAvailability

__all__ = [
    "ALL_CHECKS",
    "ALL_CHECK_IDS",
    "CONSTITUTIONAL_INVARIANTS",
    "PROGRAMME_STATUS",
    "PROTOCOL_VERSION",
    "CheckResult",
    "HostileCheck",
    "HostileCheckReport",
    "ObjectAuthority",
    "Outcome",
    "ProgrammeReadinessReport",
    "ProvenanceBinding",
    "RouteAvailability",
    "assess_programme_readiness",
    "build_protocol_document",
    "run_anti_collapse_battery",
    "run_hostile_checks",
    "validate_catalogue",
]
