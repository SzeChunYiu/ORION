# P1 ScienceAgentBench protected artifact staging V1 — development packet

## Question

Can the already identity-bound public `benchmark_verified.zip` be transferred
to owner-only LUNARC storage, mechanically decrypted, byte-hashed entry by
entry, and quarantined without exposing entry names or bodies, running a task,
or opening any benchmark outcome?

## Frozen source boundary

- ORION integration base at lane creation:
  `adf76040815e71218776793e2f1a7d1afdb6e9d2`.
- Official source: `OSU-NLP-Group/ScienceAgentBench` commit
  `c26e151ed601ba109dc4d35e057ff8e73fec469d`.
- Archive identity from merged PR #1102:
  `1,769,478,786` bytes and SHA-256
  `46e715d3b2196d459d2dff52aa487f506a95ec44b44262e82208d086ea879610`.
- Protected remote root:
  `/projects/hep/fs10/scratch/scyiu/orion_scienceagentbench_v1`, mode `0700`.
- The archive, extracted tree, path-bearing manifest and all payload bytes stay
  off-repository. Only aggregate counts, byte totals, cryptographic hashes,
  job metadata and source scripts enter this packet.

## Negative-result recursion retained

The first Slurm download attempt, job `3533824` on `cn121`, failed after 18
seconds with exit `22:0`. Its exact repeated terminal was:

```text
curl: (22) The requested URL returned error: 401
curl: (22) The requested URL returned error: 401
curl: (22) The requested URL returned error: 401
curl: (22) The requested URL returned error: 401
curl: (22) The requested URL returned error: 401
```

Mechanism: SharePoint's public download redirect required the `FedAuth` cookie
set during the redirect chain, while the original curl command did not retain
cookies. Repair: use an owner-only ephemeral cookie jar with both
`--cookie-jar` and `--cookie`, remove it on exit, and keep the already required
TLS, redirect, retry, size and SHA-256 gates. This is a transport failure and
repair, not a benchmark result.

## Staging operation

Slurm job `3533828` performs only mechanical operations:

1. require the full archive byte count and SHA-256;
2. reject unsafe, empty, absolute, dot-component, backslash and symlink ZIP
   paths;
3. decrypt each member using the password published by the pinned official
   README;
4. verify each decrypted byte count against ZIP metadata;
5. write a path-bearing JSONL manifest with per-file bytes and SHA-256 to
   owner-only remote storage;
6. commit only aggregate counts plus the manifest's bytes/SHA-256 in
   `LUNARC_ARTIFACT_STAGE_RECEIPT_V1.json`;
7. rename the completed extraction atomically and set its root mode to `0000`.

The script never prints an entry name or entry body. No semantic inspection,
candidate generation, program execution or evaluator call occurs.

## Mechanical result

Job `3533828` completed on `cn121` with state `COMPLETED`, exit `0:0`, elapsed
`00:18:32`, and batch `MaxRSS=5721644K`. The archive contained 955 ZIP entries:
845 encrypted files and 110 directories. Mechanical decryption yielded
4,071,815,117 file bytes. The off-repository path-bearing manifest is 132,464
bytes with SHA-256
`003412e023b576333b9b72e4d0875d50378dec44b13fcd2141987dc4cdaecb15`.
The final extracted root reports mode `0000`.

## Scientific boundary

Successful staging closes the remaining mechanical archive identity/extraction
part of PF-01. It does not close the official base build, verified task runner,
generation-route bindings, evaluator credential route, protocol signatures,
candidate generation, official scoring or statistical gate. It creates no
scientific outcome and changes no claim authority.

Scientific authority delta: `NONE`.
