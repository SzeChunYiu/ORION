"""Canonical Shadow-ORION registry shared by runtime, tests and paper synchronization."""

FRAMEWORK_VERSION = "0.3.8-shadow"
PAPER_SYNC_EPOCH = "2026-08-16-rakl-donor-saturation-v2"

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
    "FunctionalOperationSignature.v1",
    "ParentDisciplineProfile.v1",
    "EpistemicContextCompiler.rakl-v1",
    "SimilarityWitness.rakl-v1",
    "MeasurementRelation.rakl-v1",
    "GeneratorTransport.rakl-v1",
    "BenchmarkReport.v1",
    "FlagshipBenchmarkSuite.v1",
    "ExternalEvidenceManifest.v1",
    "FormalEngineReadiness.v1",
    "DevelopmentIssue.v1",
    "ReadinessEvidenceRecord.v1",
    "SelfOrionReadinessGate.v2",
    "MetaOverfitVerdict.v1",
    "RaklTransferProfile.v1",
    "RaklAnswerTransfer.v1",
    "RaklDonorAudit.v1",
    "DonorBeforeInventionGate.v1",
    "SelfOrionDevelopmentDriver.v1",
    "DevelopmentFibre.v1",
    "DevelopmentSaturationVector.v1",
    "DevelopmentNoveltyClassifier.v1",
    "InventionReadinessGate.v2",
    "DevelopmentChangeProposal.v1",
    "FrozenLiveTrialPacket.v1",
    "EvolutionArchive.v1",
    "ShadowSelfDrivingController.v1",
)
