# ORION-12 prospective discovery protocol

**Protocol:** `ORION-12.open-world-discovery.v1`  
**Status:** `DESIGN_FROZEN`  
**Outcome access:** false

The V1 design freezes the separation between Deep target discovery, Wide set discovery, complete-gold recall and route/task stopping. A headline result must include a strong lexical baseline and cannot infer completeness from a route label, route flatness, zero overlap or an unavailable provider.

AutoResearchBench code is reference-pinned to `CherYou/AutoResearchBench@a46c9bfb8968786f73f0a6a5b365b5384cd0f96d`. The actual released benchmark bundle must still be downloaded/decrypted under its documented license and content-hashed before `EXECUTION_FROZEN`; repository identity is not a substitute for dataset content identity.

`ROUTE_TRIAL_SCHEMA_V1.json` preserves route/backend/query/content identity and transport/censoring status so route diversity and stopping can be audited rather than inferred after the fact.
