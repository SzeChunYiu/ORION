# P8-X2 scientific-authority lifting theorem family V1

Date: 2026-08-19
Parent: #535
Status: FROZEN_BEFORE_ENUMERATION

## Registered donor authority families
1. `FAVA_PERMISSION`
2. `PCAA_ACTION_CERT`
3. `HDP_DELEGATION`
4. `SENTINEL_DCC`
5. `APC_BOUNDED_AGENTS`
6. `ECA_TYPED_EVIDENCE`

Each donor has a native action/delegation/evidence-authority predicate. P8 does not alter the donor-native verdict.

## Scientific-discharge type
The bounded theorem instance retains the P8 complete type compatibility coordinates:

`(domain, kind, scope, content, epoch)`.

A direct scientific discharge requires compatibility on all five coordinates unless a complete protected coercion witness is registered.

## Additional authority state
- `narrowing_ok`: every relevant delegation/principal-chain hop preserves or narrows the scientific-discharge type;
- `blocker`: `REFUTED / UNDETERMINED / ESTABLISHED`;
- `support_A`, `support_B`: two alternative complete support families in the bounded model;
- `protected_coercion`: an explicit complete scientific-type bridge, not generic action composability.

## Scientific lifting terminal
Let `Native(d)` be the donor-native authorization/evidence verdict.
Let `TypeOK := all(domain,kind,scope,content,epoch) OR protected_coercion`.
Let `SupportOK := support_A OR support_B`.

The bounded scientific terminal is:
- `NO_DONOR_AUTHORITY` if `Native(d)=false` for the donor-derived judgment;
- `BLOCK` if delegation narrowing fails, a blocker is established, no complete support family survives, or scientific type is incompatible without protected coercion;
- `CANNOT_CHECK` if blocker state is `UNDETERMINED` after the other native authority is available;
- `DISCHARGE` only when donor authority is valid, scientific type is compatible/bridged, delegation is non-widening, blocker is `REFUTED`, and at least one complete support family survives.

The relation applies to a judgment derived through the donor authority chain. A proposition may be independently scientifically supported through another evidence route even when the donor action itself is denied; this is a separate relation-non-inversion countermodel.

## Frozen theorem obligations

### T1 — donor conservativity
Adding scientific-discharge semantics never changes the native FAVA/PCAA/HDP/Sentinel/APC/ECA authority verdict.

### T2 — action/delegation versus scientific-discharge separation
For every donor family and every non-inert scientific type coordinate, there exist native-authorized judgments differing only on that coordinate with different scientific-discharge terminals.

### T3 — monotone scientific authority through delegation
A native-valid delegation/principal chain whose scientific-discharge type widens beyond the inherited type cannot discharge the widened obligation without a protected coercion/authority bridge. A type-preserving/narrowing chain may proceed if the remaining scientific obligations are satisfied.

### T4 — protected coercion
A complete protected coercion may bridge scientific type incompatibility. The same mismatched judgment without the registered coercion remains blocked. Generic action permission, delegation reachability, confidence or intent similarity is not a coercion.

### T5 — blocker fail-closed law
With all other requirements satisfied: `REFUTED -> DISCHARGE`, `UNDETERMINED -> CANNOT_CHECK`, `ESTABLISHED -> BLOCK`. `UNDETERMINED` cannot be silently treated as `REFUTED`.

### T6 — alternative support-family revocation
When two independent complete support families establish the same target obligation, revoking one family preserves discharge through the other. Revoking all complete support families blocks discharge. This prevents both over-revocation and under-revocation.

### T7 — scientific authority composition
For each ordered pair of registered donor-authority families, a native-valid two-hop chain with compatible final type, non-widening scientific authority, refuted blocker and surviving support can discharge. The matched chain with a widening scientific hop cannot, even if both native donor-authority steps are valid.

### T8 — relation non-inversion
There exist cases where an action is native-denied but the scientific proposition is independently supported by a separate complete evidence family; scientific truth/support is therefore not the inverse of action permission. Conversely T2 shows action permission does not imply scientific discharge.

### T9 — ideal decentralized-product equivalence
A decentralized donor product supplied with the exact same scientific type, narrowing, blocker, support-family and coercion semantics is extensionally equivalent to the shared P8 calculus. No inherent centralization advantage is permitted.

## Falsifiers
- If a donor already carries an equivalent scientific type/support/blocker relation at the same scope, absorb it and move that embedding to the equivalence side.
- No P8 type coordinate is universally necessary if a domain derives the same distinction from other bound fields.
- A protected coercion must be explicit and subject/epoch bound; unregistered semantic similarity is insufficient.
- Native authorization failure is not scientific refutation.

## Intended widening
P8-X2 is a positive **authority-lifting and propagation calculus** over absorbed modern delegation/governance systems. It specifies how scientific authority can flow through their certificates/chains without scope laundering, how it can be explicitly transformed, and how it survives or revokes under alternative support.
