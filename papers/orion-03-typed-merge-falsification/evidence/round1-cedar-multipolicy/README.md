# ORION-03 Round 1: Cedar multi-policy adjudication

This is the prospectively frozen real-domain Round-1 package for canonical
ORION-03. It compares native Cedar semantics with origin-erased and
origin-preserving projections on the complete official handwritten
multi-policy corpus at one immutable, permission-bearing source commit.

The package deliberately separates three questions:

1. does the pinned Cedar engine reproduce the official decisions, policy
   reasons, errors and validation outcomes?;
2. does typed origin retention change any decision on this official scope?;
3. does the corpus contain independently adjudicated upstream source licences,
   retractions or provenance capable of testing the claimed residual?

Injected hostile controls test the mechanism but do not become real-domain
evidence. The existing safe Agentgateway control remains safe.

Files are introduced chronologically: protocol/source/executables first; an
additive zero-request path-binding failure and correction second; then immutable
result receipts and the bounded scientific disposition. Dedicated CI replays
Python, Rust, native Cedar, Lean and hostile mutation checks.
