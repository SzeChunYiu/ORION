"""Shared model integration for P3 baselines, ablations, and ORION_FULL.

Every P3 system (baseline, ablation, ORION_FULL) calls the frozen evaluation
model (deepseek-v4-pro via cmkey proxy) with a system-specific prompt.  This
module provides the integration layer so each system only implements its prompt.
"""
from __future__ import annotations

import json
from typing import Sequence

from orion.providers.llm import AnthropicMessagesConfig, AnthropicMessagesLLMProvider, LLMRequest
from orion.study.baselines import IntegrationResult, SourceDocument

# ── shared provider singleton ────────────────────────────────────────────────
# The frozen evaluation model family.  Initialised once at module load.
_MODEL: AnthropicMessagesLLMProvider | None = None
_CONFIG: AnthropicMessagesConfig | None = None


def _provider() -> AnthropicMessagesLLMProvider:
    global _MODEL, _CONFIG
    if _MODEL is None:
        _CONFIG = AnthropicMessagesConfig.from_env(model="deepseek-v4-pro", max_tokens=32768)
        _MODEL = AnthropicMessagesLLMProvider(_CONFIG)
    return _MODEL


# ── response schema (shared by all ORION systems) ────────────────────────────

ORION_RESPONSE_SCHEMA = json.dumps({
    "type": "object",
    "properties": {
        "referent_relation": {
            "type": "string",
            "enum": ["SAME", "DIFFERENT", "PARTIAL_OVERLAP", "UNRESOLVED"],
        },
        "construct_relation": {
            "type": "string",
            "enum": ["SAME", "RELATED_NOT_SAME", "DIFFERENT", "UNRESOLVED"],
        },
        "measurement_relation": {
            "type": "string",
            "enum": [
                "EQUIVALENT",
                "TRANSFORMABLE_WITH_CONDITIONS",
                "NON_EQUIVALENT",
                "NOT_APPLICABLE",
                "UNRESOLVED",
            ],
        },
        "context_relation": {
            "type": "string",
            "enum": [
                "ALIGNED",
                "CONDITIONED_COMPATIBLE",
                "DIFFERENT_STATE_OR_TIME",
                "INCOMPATIBLE",
                "UNRESOLVED",
            ],
        },
        "polarity_relation": {
            "type": "string",
            "enum": ["SAME", "OPPOSITE", "NOT_COMPARABLE", "UNRESOLVED"],
        },
        "modality_relation": {
            "type": "string",
            "enum": ["SAME", "DIFFERENT_STRENGTH", "NOT_COMPARABLE", "UNRESOLVED"],
        },
        "attribution_relation": {
            "type": "string",
            "enum": ["SAME_SPEAKER_OR_SOURCE", "DIFFERENT_ATTRIBUTION", "NOT_APPLICABLE", "UNRESOLVED"],
        },
        "discourse_relation": {
            "type": "string",
            "enum": ["ALIGNED", "CONTEXTUAL_DIFFERENCE", "NOT_COMPARABLE", "UNRESOLVED"],
        },
        "mapping_relation": {
            "type": "string",
            "enum": [
                "IDENTITY",
                "EQUIVALENCE",
                "CONDITIONAL_TRANSFORM",
                "SUBSUMPTION",
                "ASSOCIATION_ONLY",
                "NO_LICENSED_MAPPING",
                "UNRESOLVED",
            ],
        },
        "contradiction_verdict": {
            "type": "string",
            "enum": ["CONTRADICTION", "NO_CONTRADICTION", "CONTEXT_DEPENDENT", "UNRESOLVED"],
        },
        "integration_verdict": {
            "type": "string",
            "enum": ["GLUE_ALLOWED", "OBSTRUCTION", "PLURAL_VIEW", "UNRESOLVED"],
        },
        "preservation_conditions": {
            "type": "array",
            "items": {"type": "string"},
        },
        "recoverability_target": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": [
        "referent_relation",
        "construct_relation",
        "measurement_relation",
        "context_relation",
        "polarity_relation",
        "modality_relation",
        "attribution_relation",
        "discourse_relation",
        "mapping_relation",
        "contradiction_verdict",
        "integration_verdict",
        "preservation_conditions",
        "recoverability_target",
    ],
    "additionalProperties": False,
})


# ── source formatting ───────────────────────────────────────────────────────

def _format_sources(sources: Sequence[SourceDocument]) -> str:
    parts = []
    for i, src in enumerate(sources):
        label = "A" if i == 0 else "B"
        parts.append(f"Source {label}: {src.text}")
    return "\n\n".join(parts)


# ── temperature per seed ────────────────────────────────────────────────────

def _temperature_for_seed(seed: int) -> float:
    """Map seed [0-4] to temperature values for stochastic output variation."""
    return 0.1 + seed * 0.2


# ── main integration function ────────────────────────────────────────────────

def model_integrate(
    system_id: str,
    system_prompt: str,
    sources: Sequence[SourceDocument],
    seed: int,
) -> IntegrationResult:
    """Call the frozen evaluation model and return a parsed IntegrationResult.

    Parameters
    ----------
    system_id:
        Identifier written into the result (e.g. ``ORION_FULL``).
    system_prompt:
        Baseline-specific system prompt describing the integration approach.
    sources:
        Source documents (text + metadata).
    seed:
        Stochastic seed [0-4] controlling temperature.

    Returns
    -------
    IntegrationResult with all fields populated from the model response,
    or UNRESOLVED defaults if parsing fails.
    """
    provider = _provider()
    source_text = _format_sources(sources)

    task = "Analyze these two source passages and determine how they can be integrated."
    user = (
        f"SEED: {seed}\n\n"
        f"{source_text}\n\n"
        "Analyze each coordinate and output the integration result as JSON."
    )

    try:
        resp = provider.complete(LLMRequest(
            task=task,
            system=system_prompt,
            user=user,
            response_schema=ORION_RESPONSE_SCHEMA,
        ))
        parsed = json.loads(resp.content)
    except Exception as exc:
        # If anything fails (JSON parse, API error, refusal), return UNRESOLVED.
        return IntegrationResult(
            system_id=system_id,
            case_id="",
            notes=f"MODEL_CALL_FAILED: {exc}",
        )

    # Validate all enum values against schema — any invalid → UNRESOLVED.
    schema = json.loads(ORION_RESPONSE_SCHEMA)
    for field_name, field_spec in schema["properties"].items():
        if "enum" in field_spec:
            val = parsed.get(field_name)
            if val not in field_spec["enum"]:
                parsed[field_name] = "UNRESOLVED"

    return IntegrationResult(
        system_id=system_id,
        case_id="",
        referent_relation=str(parsed.get("referent_relation", "UNRESOLVED")),
        construct_relation=str(parsed.get("construct_relation", "UNRESOLVED")),
        measurement_relation=str(parsed.get("measurement_relation", "UNRESOLVED")),
        context_relation=str(parsed.get("context_relation", "UNRESOLVED")),
        polarity_relation=str(parsed.get("polarity_relation", "UNRESOLVED")),
        modality_relation=str(parsed.get("modality_relation", "UNRESOLVED")),
        attribution_relation=str(parsed.get("attribution_relation", "UNRESOLVED")),
        discourse_relation=str(parsed.get("discourse_relation", "UNRESOLVED")),
        mapping_relation=str(parsed.get("mapping_relation", "UNRESOLVED")),
        contradiction_verdict=str(parsed.get("contradiction_verdict", "UNRESOLVED")),
        integration_verdict=str(parsed.get("integration_verdict", "UNRESOLVED")),
        preservation_conditions=tuple(
            str(c) for c in parsed.get("preservation_conditions", [])
        ),
        recoverability_target=tuple(
            str(t) for t in parsed.get("recoverability_target", [])
        ),
        notes=f"seed={seed}",
    )


# ── system prompt templates ──────────────────────────────────────────────────

ORION_FULL_PROMPT = """You are ORION, a cross-domain knowledge integration system. Your task is to analyze two scientific source passages and determine whether they can be integrated into a single coherent knowledge portrait.

For each of the following coordinates, determine the relationship between Source A and Source B:

1. referent_relation: Do the sources refer to the same real-world entity?
   - SAME: Both sources refer to the identical entity (e.g., same protein, same country, same physical quantity)
   - DIFFERENT: They refer to different entities, even if the names are similar
   - PARTIAL_OVERLAP: The referents overlap but are not identical (e.g., superset/subset)
   - UNRESOLVED: Cannot determine

2. construct_relation: Are the scientific constructs/concepts the same?
   - SAME: The construct is identical (e.g., both measure "economic growth")
   - RELATED_NOT_SAME: Related but distinct constructs (e.g., "income" vs "wealth")
   - DIFFERENT: Different constructs entirely
   - UNRESOLVED: Cannot determine

3. measurement_relation: Are the measurement/operationalization approaches equivalent?
   - EQUIVALENT: Same measurement approach; results directly comparable
   - TRANSFORMABLE_WITH_CONDITIONS: Different measurements but a transformation exists with stated conditions
   - NON_EQUIVALENT: Different measurements that cannot be equated
   - NOT_APPLICABLE: No measurement dimension in one or both sources
   - UNRESOLVED: Cannot determine

4. context_relation: Are the temporal/state contexts aligned?
   - ALIGNED: Same time period and state
   - CONDITIONED_COMPATIBLE: Compatible with stated conditions
   - DIFFERENT_STATE_OR_TIME: Different temporal or state context
   - INCOMPATIBLE: Contexts are fundamentally incompatible
   - UNRESOLVED: Cannot determine

5. polarity_relation: Is the polarity/direction of the claim the same?
   - SAME: Both make positive or both make negative claims
   - OPPOSITE: One positive, one negative
   - NOT_COMPARABLE: Polarity doesn't apply
   - UNRESOLVED: Cannot determine

6. modality_relation: Is the evidential strength/commitment the same?
   - SAME: Same level of certainty
   - DIFFERENT_STRENGTH: Different levels of certainty (e.g., "proves" vs "suggests")
   - NOT_COMPARABLE: Modality doesn't apply to one or both
   - UNRESOLVED: Cannot determine

7. attribution_relation: Are the sources of the claims the same?
   - SAME_SPEAKER_OR_SOURCE: Same author, research group, or institutional source
   - DIFFERENT_ATTRIBUTION: Different sources or speakers
   - NOT_APPLICABLE: Attribution not relevant
   - UNRESOLVED: Cannot determine

8. discourse_relation: Is the discourse context aligned?
   - ALIGNED: Both sources operate in the same discourse context
   - CONTEXTUAL_DIFFERENCE: Different discourse contexts (e.g., one is a primary study, the other a review)
   - NOT_COMPARABLE: Discourse contexts are not comparable
   - UNRESOLVED: Cannot determine

9. mapping_relation: What is the mapping between the two sources?
   - IDENTITY: Direct one-to-one mapping; the claims are about the same thing
   - EQUIVALENCE: Different representations of the same underlying quantity
   - CONDITIONAL_TRANSFORM: A mapping exists but requires stated conditions
   - SUBSUMPTION: One claim subsumes or is more general than the other
   - ASSOCIATION_ONLY: Only an associational relationship exists
   - NO_LICENSED_MAPPING: No valid mapping exists between the sources
   - UNRESOLVED: Cannot determine

10. contradiction_verdict: Is there a contradiction between the sources?
    - CONTRADICTION: The sources make genuinely contradictory claims
    - NO_CONTRADICTION: No contradiction (compatible, complementary, or orthogonal)
    - CONTEXT_DEPENDENT: Depends on context
    - UNRESOLVED: Cannot determine

11. integration_verdict: What is the integration verdict?
    - GLUE_ALLOWED: The sources can be integrated into a single knowledge portrait
    - OBSTRUCTION: Integration is not safe; the sources should not be merged
    - PLURAL_VIEW: Both perspectives are valid and should be co-presented
    - UNRESOLVED: Cannot determine

12. preservation_conditions: List any conditions that must be preserved for the integration to be valid (empty list if none).

13. recoverability_target: List the key source-provenance elements that must be recoverable (source IDs, relation types, etc.).

Output ONLY valid JSON matching the schema."""

VANILLA_LONG_CONTEXT_PROMPT = """You are a scientific text integration system. You are given two source passages. Your task is to determine whether they can be integrated into a single coherent statement.

Briefly analyze the relationship between the sources and output the integration result.

For each coordinate, select the appropriate value. The key question is: can these two passages be merged without introducing scientific error?

Output ONLY valid JSON matching the schema."""

SCIENTIFIC_RAG_PROMPT = """You are a retrieval-augmented generation system for scientific literature. You retrieve relevant passages from scientific documents and synthesize them into coherent answers.

You have been given two source passages that may discuss related topics. Analyze them as if they were retrieved passages for a scientific query. Determine whether they can be integrated into a single answer, or whether they should be kept separate due to referent, construct, measurement, or context differences.

Output ONLY valid JSON matching the schema."""

CROSS_DOMAIN_RAG_PROMPT = """You are a cross-domain translation and retrieval-augmented generation system. You process source passages from different scientific domains and map them into a common representation space before integration.

The two source passages may come from different domains, terminologies, or paradigms. Your task is to determine whether a cross-domain mapping exists that allows safe integration, or whether the domain differences constitute an obstruction.

Output ONLY valid JSON matching the schema."""

FLAT_UNIVERSAL_SCHEMA_PROMPT = """You are a universal-schema integration system. You map all information from scientific sources into a single flat universal schema, ignoring source boundaries and domain-specific ontologies.

Your task is to merge the two passages into a single flat representation. If they cannot be merged, indicate the obstruction.

Output ONLY valid JSON matching the schema."""

SCOPE_SCION_PROMPT = """You are a projection-based schema integration system, inspired by SCOPE and SCION. You process each source through schema induction, project the claims into structured representations, and then fuse the schemas together.

For each source, identify the key claims and their structure. Then determine whether the schemas can be fused into a single coherent representation.

Output ONLY valid JSON matching the schema."""

PROVENANCE_SCHEMA_PROMPT = """You are a provenance-aware schema-contract integration system. Every integration decision must be traced back to the exact source passage.

Maintain strict lineage tracking for each coordinate determination. The integration result must preserve which source informed each decision.

Output ONLY valid JSON matching the schema."""

# ── ablation prompts ────────────────────────────────────────────────────────

def _ablation_prompt(removed_coordinate: str, description: str) -> str:
    """Build the ORION_FULL prompt minus one coordinate family."""
    return (
        ORION_FULL_PROMPT
        + f"\n\nIMPORTANT — ABLATION: {description}\n"
        f"Do NOT analyze or output the '{removed_coordinate}' coordinate. "
        f"Set it to 'UNRESOLVED' in your output. Focus on the remaining coordinates."
    )


ABLATION_PROMPTS: dict[str, str] = {
    "ORION_no_referent": _ablation_prompt(
        "referent_relation",
        "The referent identity coordinate is removed. Integration proceeds without distinguishing referent identity.",
    ),
    "ORION_no_construct": _ablation_prompt(
        "construct_relation",
        "The construct identity coordinate is removed. Integration proceeds without distinguishing constructs.",
    ),
    "ORION_no_measurement": _ablation_prompt(
        "measurement_relation",
        "The measurement/operationalization coordinate is removed. Tests whether measurement equivalence is necessary.",
    ),
    "ORION_no_context": _ablation_prompt(
        "context_relation",
        "The temporal/state context coordinate is removed. Tests the effect of context awareness.",
    ),
    "ORION_no_modality_polarity_attribution_discourse": _ablation_prompt(
        "modality_relation",
        "The modality, polarity, attribution, and discourse coordinates are removed together. Tests the discourse-modality complex.",
    ),
    "ORION_no_obstruction": _ablation_prompt(
        "integration_verdict",
        "The explicit obstruction state is removed. The system must produce GLUE_ALLOWED or PLURAL_VIEW for every case.",
    ),
    "ORION_no_recoverability": _ablation_prompt(
        "recoverability_target",
        "The recoverability target is removed. The system does not track non-preserved coordinates.",
    ),
    "ORION_no_W_expansion": _ablation_prompt(
        "mapping_relation",
        "The W-expansion feedback loop is removed. The search universe is static — only direct mappings are considered.",
    ),
}


# ── prompt map ───────────────────────────────────────────────────────────────

SYSTEM_PROMPTS: dict[str, str] = {
    "ORION_FULL": ORION_FULL_PROMPT,
    "VanillaLongContext": VANILLA_LONG_CONTEXT_PROMPT,
    "ScientificRAG": SCIENTIFIC_RAG_PROMPT,
    "CrossDomainRAG": CROSS_DOMAIN_RAG_PROMPT,
    "FlatUniversalSchema": FLAT_UNIVERSAL_SCHEMA_PROMPT,
    "SCOPE_SCION_Like": SCOPE_SCION_PROMPT,
    "ProvenanceSchema": PROVENANCE_SCHEMA_PROMPT,
}
SYSTEM_PROMPTS.update(ABLATION_PROMPTS)