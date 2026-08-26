# R8 packet identity and checkout binding

## Purpose

The original `R8_PACKET_COMMIT.json` required a commit to contain its own Git identity. That fixed point is impossible: changing the file to insert the commit changes both the tree and the commit. The literal v1 bytes are preserved unchanged as `R8_PACKET_COMMIT_V1_PRESERVED.json` and remain retrievable at their original publication commit.

The v2 contract separates three identities:

1. **Scientific subject** — immutable R8 snapshot commit `0c451e862a0eeddac7c673813c4dc499f134b088`, tree `dbf96cce53d21d25584479fb740473293fae75e0`. This is the only commit printed for exact execution checkout.
2. **Packet publication** — commit `a14dfe7872b1d3d814a0f784c359793e8bcadb3c`, tree `e8023f0b11b56d87ccfd222320995468ecabcef8`, which first contains the exact v2 packet at `papers/five-paper-top-tier-r8/R8_PACKET_COMMIT.json`; its blob, SHA-256 and byte count are recorded by the successor publication-binding file.
3. **Successor binding record** — `R8_PACKET_PUBLICATION_BINDING.json`, added only after the publication commit exists. It binds the prior publication object and deliberately excludes its own commit identity, so no self-reference remains.

The source remote ref was observed at the scientific subject commit before the child lane was created. Ref identity, commit identity, tree identity, path identity, blob identity, and file SHA-256 are validated independently.

## Validation

```bash
python papers/five-paper-top-tier-r8/harness/validate_r8_packet_binding.py --require-source-ref
python papers/five-paper-top-tier-r8/harness/read_packet_commit.py --require-source-ref
```

The reader validates the entire custody pair before printing the scientific subject commit. It never prints the packet publication or the successor binding commit as the executable subject.

The validator fails closed on:

- any surviving `TO_BE_BOUND_AFTER_MATERIALIZATION` placeholder in active v2 bytes;
- source-ref observation drift;
- subject commit/tree drift;
- packet publication commit/tree/path/blob/SHA/byte drift;
- current packet bytes differing from their publication commit;
- loss or mutation of preserved v1 bytes;
- a checkout that does not descend from the packet publication;
- added or removed schema fields;
- authority expansion.

## Authority boundary

This repair is engineering custody only. It does not execute or validate scientific algorithms, change any frozen result or manuscript, authorize LUNARC, grant scientific disposition, establish novelty, or change paper/publication readiness. The R8 scientific subject and all adverse/null/CANNOT_CHECK outcomes remain byte-identical at the bound subject commit.
