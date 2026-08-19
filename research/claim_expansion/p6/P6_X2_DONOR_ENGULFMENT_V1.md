# P6-X2 donor engulfment and improvement map V1

Date: 2026-08-19
Parent: #533

## Doctrine
Nearest work is substrate. For each donor, P6 extracts the strongest unique mechanism, adopts it into the lower-level certificate stack, identifies the boundary relevant to scientific preservation, and improves the interface rather than claiming the donor mechanism as P6 novelty.

## Donor 1 — Proof of Execution (PoE)
**Unique part absorbed:** contract-bound runtime proof with authorization, path compliance, tamper-evident history, replay context and an execution attestation certificate.

**What P6 improves:** PoE answers whether an execution remains valid under its runtime contract. P6 treats a valid PoE certificate as a first-class lower-level certificate and adds a lift relation to scientific standing. A change can leave execution/path/history/replay valid while invalidating a measurement, evidential, inferential or scientific-epoch premise of a claim.

**No P6 ownership:** runtime authorization, trace integrity, replayability, execution attestation.

## Donor 2 — certified traces / Proposal–Certification–Execution
**Unique part absorbed:** generation is separated from permissibility certification; execution occurs only for a certified structured trace carrying intended steps, evidence, approvals, computations, credentials and conditions.

**What P6 improves:** a certified trace can be necessary but not sufficient for preservation of a scientific certificate after state change. P6 reuses the proposal/certification/execution separation and adds exact scientific continuity obligations that must be revalidated when affected.

**No P6 ownership:** no-certificate-no-execution doctrine or generic permissibility machines.

## Donor 3 — Proof-Carrying Agent Actions (PCAA)
**Unique part absorbed:** runtime-neutral action certificates with explicit action identity, approval semantics, runtime/outcome receipts, replay-ready proof and portability across heterogeneous runtimes.

**What P6 improves:** P6 uses PCAA-style portable action certificates as one certificate kind and adds a cross-layer lifting rule: portability of action authorization does not automatically imply portability of a scientific claim whose content, measurement semantics, evidence interpretation or epoch changed.

**No P6 ownership:** action canonicalization, approval binding, runtime portability or action-certificate governance.

## Donor 4 — scientific workflow execution signatures
**Unique part absorbed:** workflow/data provenance plus formal reproducibility tenets and cryptographic execution signatures for scientific workflows.

**What P6 improves:** P6 explicitly separates *reproducibility of the computational workflow* from *continued scientific standing of a claim*. Identical/reproducible computation can require scientific revalidation when source meaning, measurement semantics, inference obligations or scientific epoch changes.

**No P6 ownership:** workflow provenance, workflow reproducibility tenets or execution-signature generation.

## Donor 5 — certified purity / attested executor boundaries
**Unique part absorbed:** structural prevention of ungoverned effects, purity certificates, signed binary classification and remote attestation.

**What P6 improves:** a structurally pure, correctly attested executor can still operate on scientifically stale or semantically changed inputs. P6 therefore treats executor purity as a donor-native certificate coordinate, not a scientific-validity certificate.

**No P6 ownership:** purity certification, structural effect exclusion or remote attestation.

## Additional scientific-agent pressure
ScienceClaw/Infinite-style artifact DAGs and provenance-aware scientific discourse show that rich computational lineage can be maintained across autonomous scientific work. This strengthens the donor layer: P6 should consume full lineage when available rather than reconstruct a weaker provenance proxy. The remaining question is still whether lineage/certificate preservation entails scientific-standing preservation under a material semantic change.

## Absorbed product
The strong P6 donor product is therefore not one mechanism. It is a stack containing, where applicable:

`runtime permissibility + proof of execution + action identity/approval receipts + replay + workflow provenance/reproducibility + purity/attestation + dependency/effect semantics`.

P6-X2 grants that stack native validity. The only additional question is whether and how the stack lifts to a *scientific* certificate after change.

## Improvement over the donor product
P6-X2 adds four interface properties on top of the absorbed stack:

1. **scientific lift witness** — explicit bridge from donor certificate(s) to claim-specific scientific continuity coordinates;
2. **no-laundering product rule** — several valid donor certificates cannot infer an absent scientific coordinate merely by accumulation;
3. **exact selective revalidation** — when a scientific coordinate changes, revalidate that affected coordinate rather than discarding every valid lower-level certificate;
4. **ideal-product equivalence** — a donor product enriched with the same coordinates/rules ties exactly, making the contribution the reusable lifting semantics rather than centralized branding.

## Current novelty target
Candidate wider claim:

> P6 provides a conservative certificate-lifting semantics for dynamic scientific computation: strong proof-carrying execution, action, workflow and attestation certificates are reusable lower-level objects, while preservation of scientific standing requires explicit lifting across claim/content, measurement, evidence, inference and epoch coordinates; changes trigger exact revalidation of affected scientific coordinates without invalidating unrelated donor certificates.

This is broader than the V3 typed-erasure statement because it specifies how to *compose and reuse* strong donor certificates, not merely why erasing scientific coordinates loses information.

## Boundary
No deployed-agent superiority is claimed. No certificate coordinate is claimed universally minimal. If a donor certificate already carries an equivalent scientific coordinate and bridge semantics, P6 absorbs it and the ideal enriched donor product is extensionally equivalent.
