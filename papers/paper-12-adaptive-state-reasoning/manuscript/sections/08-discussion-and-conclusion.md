# Discussion and conclusion

P12 reframes test-time scaling as a **portfolio of computations**. “Think longer” is not the only adaptive action available to an intelligent system. It may be cheaper to parse, retrieve, compile, restructure or recover state so that less downstream search is required. Conversely, when state already exposes the relevant structure, additional preprocessing is wasteful and reasoning should receive the marginal budget.

The protected benchmark demonstrates the construction but does not establish the
key causal discriminator. Equal total budget was real; equal action capability
was not. Most of the margin was unreachable by the named baselines before their
signals were read.

This leaves a concrete systems hypothesis for P12B and real agents:
**test-time scaling curves may be two-dimensional, with state-work and
reasoning-work measured on a common receipt and with action capability held
fixed across signal ablations.**

Adaptive inference may need to decide not only **how much** computation to spend
but **where** to spend it. P12 supplies the formulation and an exact failure
analysis of its first empirical discriminator. Under
`P12A_COMPARISON_VALIDITY_ADJUDICATION_V1.json`, the active terminal is
`P12A_SUPERIORITY_AUTHORITY_WITHHELD`. The next step is a prospectively frozen
P12B with identical four-action capability; real end-to-end validation follows
only after that controlled contrast is sound.
