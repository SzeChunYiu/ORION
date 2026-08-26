# Protected partition — access rules (FROZEN with the v1 suite)

This directory holds the adjudication gold for the external evaluation suite.
The suite is unusable as an external instrument if this partition leaks, so:

1. **Never** hand `p14_external_gold_v1.jsonl` (or any derivative of it beyond
   the per-packet `gold_record_digest` already inside the packets) to a system
   or person whose judgment is being evaluated.
2. **Adjudicators** may read it only after their independent judgment is sealed
   (worksheet column complete), to score agreement.
3. **Any edit** to this file after the receipt is bound invalidates the suite;
   the gold-file sha256 recorded in the worksheet and analytics makes silent
   edits detectable.
4. The generator and validator enforce that agent-visible partitions carry no
   adjudication token, programme name, or terminal label; keep those guards
   intact when authoring `external_v2/`.
