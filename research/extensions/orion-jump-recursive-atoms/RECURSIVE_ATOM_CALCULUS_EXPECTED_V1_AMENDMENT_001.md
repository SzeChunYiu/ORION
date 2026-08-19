# Recursive atom calculus expected amendment 001

Date: 2026-08-19

This amendment records a **post-implementation hostile-review correction**, not a new favorable scientific outcome.

Cursor Bugbot identified that the original interaction classifier compared `left_only` / `right_only` child deltas against each other and could therefore misclassify a case where both children had the same nonempty standalone delta versus the no-child regime, but their combination destroyed one of those reachable contracts.

The original four-witness packet did not contain that lossy-shared case. The protocol is therefore strengthened with a fifth frozen hostile witness:

```text
left delta     = {shared-a, shared-b}
right delta    = {shared-a, shared-b}
combined delta = {shared-a}
```

`#513 analyze_contract_interaction()` correctly reports `shared_individual_contract_ids` and `lost_in_combination_contract_ids`; the #507 interpretation layer now consumes that loss.

Expected disposition:

`OVERREACH_HARMFUL`

This preserves both scientific facts:

- each child has standalone bounded value relative to the no-child regime;
- the joint use is harmful because it loses a previously reachable contract.

No ownership-map row, saturation round, recursion stop, common result vocabulary, child terminal, or #507 candidate terminal changed. The expected interaction-witness count changes from **4 to 5** solely to bind the reviewer-discovered hostile case.
