"""Canonical Shadow-ORION registry shared by runtime, tests and paper synchronization."""

FRAMEWORK_VERSION = "0.2.4-shadow"
PAPER_SYNC_EPOCH = "2026-08-15-post-merge-hostile-review-v4"

CORE_OPERATOR_IDS = (
    "FRAME.v1",
    "SEARCH.v1",
    "ABSORB.v1",
    "RECONSTRUCT.v1",
    "DETECT.v1",
    "DIAGNOSE.v1",
    "REFRAME.v1",
    "REOPEN.v1",
    "SATURATE_BOUNDED.v3",
)

CORE_STATE_COORDINATES = ("K", "W", "M")

MECHANICS_SUBSTRATE_IDS = (
    "MechanicCell.v1",
    "MechanicQuestion.v0",
    "MechanicReceipt.v1",
    "TaskEpisode.v1",
    "FailurePatternCandidate.v1",
    "PatternVerificationReceipt.v2",
    "MechanicTraceReceipt.v2",
    "MechanicGuard.v1",
)
