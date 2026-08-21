# Relation to current adaptive-compute literature and limitations

Strategic test-time-compute allocation treats inference budget as a learnable or bandit decision across examples. Constrained policy approaches optimize accuracy under average compute. Adaptive in-context demonstration and generation methods jointly alter conditioning and generation effort. Recent “when to think” work likewise emphasizes selective reasoning to reduce unnecessary inference.

These results strengthen, rather than weaken, P12's motivation: **adaptive inference is crowded; the novel discriminator must be where the resource can be spent.** P12's result is specifically about a budget portfolio containing state construction and reasoning as distinct actions and about strict dominance over both corresponding one-axis adaptive policies.

## Limitations and real-system promotion gate

1. The protected benchmark is a controlled resource world, not an LLM, prover or production agent.
2. The pre-outcome signals are constructed measurements of resource need. Real signal quality may be substantially worse.
3. Scalar units are commensurate by construction. Real compiler work, tokens, verifier calls and latency are heterogeneous.
4. The joint policy is a simple frozen nearest-allocation rule; the paper does not claim it is optimal.
5. A real-system result must include strong compute-only and state-only adaptive baselines, not merely fixed context and fixed reasoning.
6. A broad superiority claim requires at least one held-out real LLM/procedural domain or verifier-backed search domain under matched end-to-end resource receipts.
7. If real tasks overwhelmingly favor one resource locus, a simpler one-axis policy may be preferable; P12 predicts this as a regime condition rather than denying it.