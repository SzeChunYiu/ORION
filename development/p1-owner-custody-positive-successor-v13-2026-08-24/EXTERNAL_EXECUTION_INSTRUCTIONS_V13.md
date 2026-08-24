# P1 V13 external authority execution instructions

## Purpose

This packet is an executable request for external authority acts. It does **not** name an owner, delegate, host, rights holder or reviewer, and none of its unsigned templates carries authority. Candidate authors and AI agents must not fill external identities, ownership bases, keys, signatures, rights or review dispositions.

## Who must act

1. A separately verifiable owner of the R7 decision vocabulary, or a delegator with an independently verifiable ownership basis.
2. A named natural person or institution accepting the exact seven-target completion and ratification delegation.
3. A host authority able to bind recommendation, execution and adoption boundaries.
4. A target-corpus rights holder able to grant the exact listed acts over content-addressed bytes.
5. A semantic reviewer independent of the candidate-author and adapter lanes.

One person may not silently satisfy multiple roles. Any role combination must be expressly permitted by the frozen protocol and independently justified; V13 currently assumes separate acts and treats ambiguity as failure.

## Stage 0: verify the packet

Verify `SHA256SUMS`, then verify `EXECUTION_PACKET_MANIFEST_V13.json`. Do not use any file whose bytes disagree. The three entries under `semantic_inputs` are the complete precommitment semantic input set. Administrative forms may be supplied for signing, but they add no target semantics.

## Stage 1: delegation and adapter-blind precommitment

1. The delegator fills a copy of `OWNER_DELEGATION_AND_ACCEPTANCE_TEMPLATE_V13.json`, attaches an externally verifiable ownership basis, and signs the exact serialized output.
2. The named delegate separately signs acceptance of all seven target IDs, both powers, effective time and revocation rule.
3. Before receiving semantic work inputs, the delegate and proposed reviewer each fill and sign their stage-A entry from `ADAPTER_BLIND_CUSTODY_TEMPLATE_V13.json`.
4. Each stage-A receipt must list exactly the three semantic-input SHA-256 values. A recipient with prior access to adapter-side or outcome material must state that fact; the route then fails closed rather than replacing the person silently.

Accepted signature schemes are GPG, SSH and Sigstore. Each signed record must include the scheme, public key or certificate identity, verification material or stable verification URI, and UTC signing time. A typed name, issue comment, repository login or unsigned email is not a signature.

## Stage 2: owner/delegate completion

The accepted delegate receives only:

- the three exact allowlisted target-side artifacts;
- administrative forms in this packet; and
- primary public standards retrieved independently.

The delegate must not receive P1 source terminals, source-target crosswalks, compatibility matrices, survivor maps, audit results, cases, labels, models, scores or outcomes.

Follow `SIGNING_CANONICALIZATION_V13.json`. The delegate first produces the ratifiable algebra payload: every top-level V8 field except `ratification`, with exactly one complete profile for each required decision ID. Canonicalize it with RFC 8785, hash it with SHA-256, and sign the exact `ALGEBRA_PAYLOAD` domain message. This removes any self-hash or signature cycle.

After review, construct `OWNER_COMPLETED_R7_ALGEBRA_V13.json` by adding the V8 `ratification` object. Its `artifact_sha256` is the ratifiable-payload hash; its owner signature is the ALGEBRA_PAYLOAD signature; its reviewer fields bind the signed review-payload hash and disposition. Validate the resulting complete instance against the immutable V8 schema, then RFC8785-canonicalize, hash and separately sign the final envelope under `ALGEBRA_ENVELOPE`. Record both hashes and signatures in a completed coversheet.

## Stage 3: host and rights acts

The host authority and target-corpus rights holder independently fill and sign `HOST_AND_RIGHTS_ACCEPTANCE_TEMPLATE_V13.json`. The record must bind exact evidence and corpus/artifact digests. Repository licensing, employment or owner delegation does not substitute for either signature.

## Stage 4: independent semantic review

Only after the ratifiable-payload digest is sealed, deliver that payload, the three allowlisted target-side artifacts and independently retrieved primary standards to the reviewer. Do not deliver adapter-side or outcome material. The reviewer signs the stage-B delivery record and the RFC8785-canonical `review_payload` over the exact algebra-payload hash. The final V8 instance then binds that review-payload hash; the reviewer is not asked to sign a self-referential final envelope.

Only `CONFORMANT` passes. `NONCONFORMANT`, `CANNOT_CHECK`, an unsigned disposition, an algebra-hash mismatch or an independence failure stops the route.

## Return bundle

Return all seven files named by `PROTOCOL_V13.json` under `external_outputs_required_to_close_v13`, plus public-key/certificate verification material and every cited ownership/authority/rights evidence object or stable authorized URI. Do not send case text, labels, outcomes or adapter-side artifacts.

## Acceptance boundary

The candidate-author lane may verify signatures, identities, digests, ordering and schema conformance only after the complete bundle is returned. It may not repair external semantic values or signatures. The unchanged 117,649-map audit remains unauthorized until every frozen conjunct passes.
