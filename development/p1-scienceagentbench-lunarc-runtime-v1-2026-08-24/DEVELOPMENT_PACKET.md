# P1 ScienceAgentBench LUNARC runtime V1 — development packet

## Question

Can the unavailable local Docker/storage route be replaced by an isolated
LUNARC Slurm runtime that exposes the Docker SDK surface used by the pinned
ScienceAgentBench harness, without opening a benchmark entry, outcome, gold,
evaluator or rubric body?

## Frozen source boundary

- ORION integration base: `530d5ac79fa005099f9f03e647eeb2718d479e98`.
- Official source remains `OSU-NLP-Group/ScienceAgentBench` commit
  `c26e151ed601ba109dc4d35e057ff8e73fec469d`.
- Full archive identity is already bound by merged PR #1102 as
  `1,769,478,786` bytes and SHA-256
  `46e715d3b2196d459d2dff52aa487f506a95ec44b44262e82208d086ea879610`.
- This packet uses only a public Alpine image and one fixed synthetic file. It
  does not download, extract or read the ScienceAgentBench archive.

## Runtime discovered

- Login: `cosmos2.int.lunarc`; Slurm job `3533810` ran on `cn121` in `lu48`
  under account `lu2026-2-51`.
- Owner path:
  `/projects/hep/fs10/scratch/scyiu/orion_scienceagentbench_v1`, mode `0700`.
- Project filesystem reported 240 TB available. Container layers cannot live
  there because the NFS path rejected required extended attributes.
- Slurm supplied node-local `$TMPDIR` on `/local`; the audited node reported a
  1.6 TB filesystem with about 1.5 TB free.
- Compute nodes expose Apptainer but not Podman. A content-hashed userland copy
  of Podman 5.8.2 and its helpers was staged off-repository in the owner path.
- Docker SDK 7.1.0 connected to the Podman API 1.44 Unix socket, built a public
  Alpine context, created/started a container, executed the fixed command, and
  verified container plus built-image removal.

## Negative-result recursion retained

The shortest successful route was found by treating each failed Slurm job as a
new runtime discriminator rather than hiding it.

| Job | Exact blocking evidence | Mechanism-specific repair |
|---|---|---|
| `3533794` | `/var/spool/slurm/slurmd/job3533794/slurm_script: line 41: podman: command not found` | Stage a hash-bound userland Podman/helper toolchain outside ORION. |
| `3533799` | Podman could not create the Unix socket under the long project path. | Move only the runtime socket to short node-local `/tmp`. |
| `3533800`, `3533801` | `potentially insufficient UIDs or GIDs available in user namespace ... lchown /Dockerfile: invalid argument` | Normalize only Docker SDK build-context tar UID/GID metadata to zero; retain paths, bytes, modes, links and timestamps. |
| `3533802`, `3533803` | `creating build container: no policy.json file found` | Install a fail-closed transport policy that rejects by default and admits only public `docker.io` for this smoke. |
| `3533804` | `lsetxattr ... operation not supported` on the project filesystem | Put ephemeral container graph/run roots on Slurm node-local `$TMPDIR`; retain only bounded receipts on project storage. |
| `3533806`, `3533810` | PASS | Repeat pass after adding cleanup verification and resolved base-image digests. |

These are runtime-engineering failures, not benchmark outcomes and not
scientific evidence for P1.

## Synthetic pass

`SLURM_SYNTHETIC_RECEIPT_V1.json` records:

- Docker SDK 7.1.0 and Podman 5.8.2/API 1.44;
- resolved Alpine repository digests and built-image identity;
- Docker SDK build, create, start, exec and cleanup success;
- all five OpenAI/Azure credential-presence flags false;
- zero official tasks, zero outcomes and no benchmark/evaluator bodies opened.

Terminal:

`P1_SAB_LUNARC_PODMAN_DOCKER_SDK_SYNTHETIC_SMOKE_PASS__ZERO_TASKS_RUN__ZERO_OUTCOMES_OPENED`

## What remains fail-closed

This does **not** establish that the full official evaluator is runnable. The
exact official Ubuntu/Conda base build, every instance build, verified-split
evaluator import, full archive extraction/manifest, judge calls and credentials
remain untested. Rootless single-map ownership normalization is an additive
runtime adapter and must be byte-bound in any future official run. The visual
judge remains stochastic. Credentials remain absent. Scientific authority
delta is `NONE`.

## Next discriminators

1. Build and remove the exact pinned public official base Dockerfile on the
   same node-local route without a benchmark instance or credentials.
2. Stream the already hash-bound archive directly to the protected owner path,
   verify bytes/SHA-256, and extract mechanically without displaying entry
   bodies; retain a hash-only directory manifest.
3. Bind the generation-route packet, prompts, matched budgets and unsupported
   seed/tokenizer guarantees before any official task is opened.
4. Obtain an owner-controlled OpenAI/Azure evaluator route; preserve only
   credential presence/route hash, never secret values.
5. Only then freeze signatures and execute all 102 matched tasks.
