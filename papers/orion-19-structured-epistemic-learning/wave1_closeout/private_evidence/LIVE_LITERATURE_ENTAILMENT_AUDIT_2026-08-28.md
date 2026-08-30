# Live literature and entailment audit — 2026-08-28

## Search boundary

Queries covered: test-time compute scaling; repeated sampling; failure diagnosis across information, representation, and computation; underspecified reasoning and information acquisition; serialization effects in structured tasks; metareasoning/value of computation; selective classification; graph/relational representation; and algorithmic reasoning.

Sources used: current arXiv metadata/API, OpenAlex discovery, the maintained exact TMLR contract, and primary source metadata. Search was venue-agnostic. Apparent neighbours were used to subtract component claims, not to infer acceptance probability.

## Selected source checks

| Source | Verified identity | Manuscript entailment |
|---|---|---|
| Russell and Wefald, *Do the Right Thing* (1991) | MIT Press book identity checked | Supports value-of-computation/metareasoning framing, not this diagnostic. |
| Snell et al., arXiv:2408.03314 | arXiv title and authors verified live | Supports the claim that optimized test-time compute can outperform simple parameter scaling in studied settings. |
| Brown et al., arXiv:2407.21787 | arXiv title and authors verified live | Supports repeated-sampling inference scaling, not a universal compute policy. |
| Ying et al., arXiv:2106.05234 | arXiv title and authors verified live | Supports graph-structural encoding as prior work. |
| Rampasek et al., arXiv:2205.12454 | arXiv title and authors verified live | Supports graph-transformer structural organization as prior work. |
| Velickovic et al., arXiv:2205.15659 | arXiv title and authors verified live | Supports algorithmic-reasoning benchmark context. |
| Bounsi et al., arXiv:2406.09308 | arXiv title and authors verified live | Supports hybrid learned/algorithmic reasoning context. |
| Li et al., arXiv:2503.22674 | arXiv title and authors verified live | Supports missing-information acquisition as established neighbouring work. |
| Liem, arXiv:2605.04243 | arXiv title and author verified live | Supports separating representation inconsistency from downstream temporal reasoning failure. |
| Lo et al., arXiv:2604.27272 | arXiv title and authors verified live | Supports serialization friction as an established effect; blocks a universal serialization novelty claim. |
| Geifman and El-Yaniv (NeurIPS 2017) | proceedings identity checked against known publication metadata | Supports selective-classification context only; the paper's indeterminate outcome is defined separately. |
| Qwen2.5 Technical Report, arXiv:2412.15115 | arXiv title and team identity verified live | Supports model-family identity only, not the paper's experimental result. |

## Nearest-work subtraction

- Adaptive test-time compute and repeated sampling own the proposition that additional inference can improve results.
- Metareasoning owns resource-aware deliberation as a general decision problem.
- Graph/relational and algorithmic-reasoning work owns the proposition that organization and explicit computation can be load-bearing.
- Missing-information benchmarks own the proposition that an underspecified task may require information acquisition rather than guessing.
- Selective classification owns general abstention/rejection framing.
- Serialization-friction work owns the broad observation that information-equivalent serializations can change performance.

The residual paper-level contribution is the prospective three-intervention diagnosis, protected causal-disposition recomputation, generic compute-escalation foil, vector-valued accounting, and symmetric retention of null/adverse/indeterminate outcomes on the fixed five-family study.

## Open boundary

The search does not prove global priority. No “first,” universal, broad-impact, or state-of-the-art wording is authorized. A submission-date refresh is required if filing occurs after the active freshness window.
