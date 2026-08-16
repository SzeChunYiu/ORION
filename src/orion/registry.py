"""Canonical Shadow-ORION registry shared by runtime, tests and paper synchronization."""

FRAMEWORK_VERSION = "0.3.3-shadow"
PAPER_SYNC_EPOCH = "2026-08-16-typed-ignorance-v1"

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
    "AnswerRecord.v1",
    "NearestWorkCase.v1",
    "ScientificMeaningProjection.v1",
    "IgnoranceProjection.v1",
    "BenchmarkReport.v1",
    "FlagshipBenchmarkSuite.v1",
    "DevelopmentIssue.v1",
    "RaklTransferProfile.v1",
    "RaklAnswerTransfer.v1",
    "SelfOrionDevelopmentDriver.v1",
    "DevelopmentFibre.v1",
    "DevelopmentSaturationVector.v1",
    "DevelopmentNoveltyClassifier.v1",
    "InventionReadinessGate.v1",
    "DevelopmentChangeProposal.v1",
    "FrozenLiveTrialPacket.v1",
    "EvolutionArchive.v1",
    "ShadowSelfDrivingController.v1",
)
