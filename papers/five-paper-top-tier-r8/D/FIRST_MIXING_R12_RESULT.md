# Paper D R12 — first-mixing execution result

Exact theory parent: `f6b21c94b9cd372700d7a13ccc229e27637acef9`

Theory/verifier/workflow head: `7c1817ceb8339de97668818ce8b586b85f18ffd0`

Workflow run/job: `33017186963` / `98338314999`

Artifact SHA-256: `2abdefc62c248d1f528dcdbe8f69b90c425afda6fe2f10fc75511f5cc8271d58`

Result SHA-256: `df15ba9dce6fa471087819cd7b7f517d5125eef93adb8cfa150155dcca27e291`

Terminal:

`TYPED_AUTHORITY_FIRST_MIXING_R12_PASS`

## Exact finite result

- exhaustive three-atom/three-origin systems: `8,192`;
- deterministic generated systems: `2,000`;
- total systems: `10,192`;
- exhaustive hybrid atoms: `12`;
- generated hybrid atoms: `56`;
- total hybrid atoms: `68`;
- first-mixing certificates: `68/68`;
- unary origin-preserving controls: `2,000`;
- unary-control hybrids: `0`.

The direct topological witness recurrence agrees with separately computed independent Horn closure for every origin in every system. Pooled recurrence agrees with direct closure of pooled seeds. Every hybrid atom has a local first-mixing certificate with individually witnessed premises and an empty common-origin intersection.

## Source-bound bridge result

The workflow verified exact Git blobs and load-bearing source semantics at `agentgateway/agentgateway@e136c7458b0fe0f51378dd31ffd60ab2b6939fc2`:

- one validated token becomes one typed `Claims` request extension;
- the CEL executor exposes one typed `jwt` field;
- HTTP authorization evaluates one request executor;
- native authorization merge retains the R11 deny/require/allow composition.

The bound bridge is therefore a real SAFE single-slot control, not a coordinatewise union of claim maps.

## Hostile controls

- `{subject}` from origin A plus `{scope}` from origin B produces a pooled authorization with witness sets `{A}`, `{B}` and empty intersection;
- either single slot alone does not authorize;
- adding origin C with both premises yields witness set `{C}` and correctly suppresses the hybrid verdict;
- a declared bridge-license origin carrying both premises is not mislabeled splicing.

## Authority

The analytic theorems carry the finite mathematical claim; the workflow is implementation and source-binding corroboration. It is not external independence, a whole-gateway security certification, a deployed vulnerability, a novelty certificate or journal authority.

The remaining systems gate is an independently maintained integration where multiple real evidence records reach one decision under both origin-preserving and coordinate-erased implementations, with domain adjudication before outcome access.
