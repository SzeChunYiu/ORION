# ORION-12 live-provider execution preflight — 2026-08-16

Resolve the frozen live-campaign protocol's blocking provider precondition without exposing credentials. The Actions run records only whether a funded `OPENALEX_API_KEY` is available in the same-repository execution context. A missing key keeps the live three-route campaign at `CANNOT_CHECK`; a present key permits an execution-freeze wrapper to be created and run under the already-frozen provider/rate/retention policy.
