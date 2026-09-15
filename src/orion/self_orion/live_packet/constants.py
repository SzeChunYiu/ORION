"""Frozen identifiers, paths, exit codes and the one hashing primitive.

Everything here is content the packet fingerprint is computed over, or a
coordinate the rest of the package resolves against. `_sha256` is the single
digest function: one canonical JSON encoding, so a hash computed in one module
is reproducible in another.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
PROTOCOL_RELATIVE_PATH = (
    "papers/paper-05-self-orion/protocol/LIVE_TRIAL_PACKET_V1.json"
)
PROTOCOL_PATH = REPO_ROOT / PROTOCOL_RELATIVE_PATH

PACKET_SCHEMA = "orion.self-orion.live-research-packet.v1"
PACKET_ID = "P5.shadow-live-research.v1"
EVALUATION_EPOCH_ID = "P5.shadow-live-research.epoch-1"
BASELINE_ID = "simple_llm_retrieval_baseline.v1"

#: Sentinel for a field that cannot honestly be filled before execution. Copied
#: from the P5 protocol convention (`dataset_revisions: UNBOUND`): a result
#: reported against an unbound coordinate is unverifiable, so the coordinate is
#: named and left visibly empty rather than guessed at freeze time.
UNBOUND = "UNBOUND"

#: Deterministic stamp for pre-execution artifacts. Wall-clock time here would
#: make the refusal episodes and their fingerprints irreproducible, and a record
#: that cannot be recomputed cannot be checked.
PREFLIGHT_TIMESTAMP = "P5.shadow-live-research.preflight"

EXIT_OK = 0
EXIT_ERROR = 2
EXIT_CANNOT_CHECK = 3

SUCCESS_BOUNDARY = (
    "Exercising the governed loop and yielding interpretable failure evidence is "
    "the whole of the success claim. This packet does not establish autonomous-"
    "science capability, and it does not establish Self-ORION readiness."
)

#: The concrete stack this packet would run against. Named as a dotted path so
#: the one-command property is checkable by reading, not by trusting prose.
LIVE_STACK_CONSTRUCTOR = (
    "orion.providers.live_phase2.build_phase2_live_provider_stack_from_env"
)
LIVE_RUNNER = "orion.self_orion.live_trial.ShadowLiveTrialRunner.from_providers"


def _sha256(payload: object) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
