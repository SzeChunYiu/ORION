"""Canonical Shadow-ORION registry shared by runtime, tests and paper synchronization."""

FRAMEWORK_VERSION = "0.2.1-shadow"
PAPER_SYNC_EPOCH = "2026-08-15-mechanics-authority-hardening-v1"

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
    "MechanicCell.v0",
    "MechanicQuestion.v0",
    "MechanicReceipt.v0",
    "TaskEpisode.v0",
    "FailurePatternCandidate.v0",
    "PatternVerificationReceipt.v1",
    "MechanicTraceReceipt.v0",
)
