# P1 ScienceAgentBench LUNARC official public-base V1 — development packet

## Question

Can the exact public base Dockerfile emitted by pinned ScienceAgentBench commit
`c26e151ed601ba109dc4d35e057ff8e73fec469d` be built, boundedly inspected and
fully removed on the merged LUNARC rootless runtime route without opening an
archive entry, task, prediction, gold/evaluator/rubric/result body or
credential?

## Exact public source

- Upstream path: `evaluation/harness/dockerfiles.py`.
- Git blob SHA-1: `d0e11f6a2beb89080a242eb77a9f211dabf74069`.
- Source bytes / SHA-256: `5,851` /
  `b0122b82a64165389a134216dffda8d6e9d3ff8bfc3ebb3795a00d54f2194b25`.
- The `_DOCKERFILE_BASE` literal was evaluated through the Python AST and
  formatted with the official x86 arguments `platform=linux/x86_64` and
  `conda_arch=x86_64`.
- Rendered Dockerfile bytes / SHA-256: `1,251` /
  `08045fc892652a6835adb808ee6db4dc5715ae64f65878eb0d0140e7d8c29a15`.

`OFFICIAL_BASE_DOCKERFILE_V1` retains the exact leading newline, two trailing
newlines and all intervening bytes. Runtime adapters did not modify it.

## Successful Slurm witness

Job `3533859` completed `0:0` in `00:07:07` on `cn121`, partition `lu48`, with
four CPUs, 32 GiB requested memory and `25,610,608K` batch MaxRSS.

- Docker SDK `7.1.0` connected to Podman `5.8.2`, API `1.44`.
- Node-local job root: `/local/slurmtmp.3533859/orion-sab-official-base-v1`.
- Resolved Ubuntu image ID:
  `sha256:4d0600e5088ac5da5119401c70292ea3a9d9dc71f76a234ad5390c1f6a8e5669`.
- Built image ID:
  `sha256:97ddb423711d704e3564bc812cd90f8eb5a61c6802825ab1819fd039abd61a25`.
- Built image size: `10,625,808,427` bytes.
- The build stream was reduced to `34,072` normalized JSON events,
  `838,041` bytes, SHA-256
  `71a9f845380231f3146d5bb0c6372066bbceeb36b42b1c284f055687ee06ac59`;
  raw build output is not in ORION.

Bounded inspection resolved Python `3.10.20`, Conda `26.7.1`, the 14 package
versions in `SLURM_OFFICIAL_BASE_RECEIPT_V1.json`, and the named `nonroot`
account as UID/GID `1000`. This is runtime inspection only, not a benchmark
task or outcome.

## Rootless single-map adapter and exact limitations

LUNARC provides no subordinate UID/GID range. The exact Dockerfile requests
package privilege drops and multi-owner filesystem changes that the one-ID
namespace cannot represent. The final route therefore composes the already
merged Docker SDK context-owner normalization with four content-bound,
ephemeral adapters:

1. a read-only apt setting keeps the apt sandbox at the mapped root identity;
2. a compiled LD_PRELOAD shim acknowledges unrepresentable identity syscalls;
3. read-only `/usr/bin/chown` and `/usr/bin/chgrp` no-op mounts cover package
   maintainers that sanitize LD_PRELOAD;
4. a fail-closed `/usr/local/sbin/adduser` adapter accepts only the exact
   `--disabled-password --gecos dog nonroot` command and creates the named
   account without claiming home-owner fidelity.

These adapters are smoke-only. Multi-owner filesystem fidelity and package
privilege-drop fidelity remain `CANNOT_CHECK`. They are not equivalent to an
ordinary subordinate-ID Docker build.

## Recursively retained failures

`FAILURE_ATLAS_V1.json` and `failure-receipts/` bind eight cleaned failed jobs
before the pass:

| Job | Discriminator | Repair |
|---|---|---|
| `3533829` | `_apt` `setgroups(65534)` failed `EPERM`; HTTP method died. | Read-only apt root-sandbox setting. |
| `3533832` | Package maintainer ownership changes failed `EINVAL`. | Add single-map identity shim. |
| `3533835`, `3533838` | Simple adapter probe passed, but package ownership still failed. | Add bounded command-path adapter. |
| `3533841`, `3533843` | Package scripts used a sanitized PATH and bypassed `/usr/local` wrappers. | Mount no-op wrappers at `/usr/bin/chown` and `/usr/bin/chgrp`. |
| `3533844` | Apt, Conda and pip completed; exact final `adduser` failed on `chown 1000:1000 /home/nonroot`. | Add exact-command account adapter. |
| `3533851` | `/usr/sbin/adduser` placement intercepted an openssh maintainer call and correctly refused it. | Move adapter to `/usr/local/sbin`; sanitized package PATH retains upstream adduser. |
| `3533859` | PASS. | No further repair. |

All eight failure receipts record node-local job-root removal, zero credentials,
zero official tasks and zero official outcomes.

## Cleanup

The successful receipt verifies removal of the inspection container, built
image, resolved Ubuntu image and every remaining image ID before service
shutdown. It then verifies removal of the runtime socket root and entire
node-local job root. The successful lane retained only small scripts, bounded
receipts and hashes in protected project storage; container layers were never
placed in ORION or project NFS.

## CANNOT_CHECK boundary

- benchmark archive retention/extraction and every archive entry;
- official instance images and official evaluator import/invocation;
- credentials and judge route;
- any of 102 official tasks or outcomes;
- multi-owner and privilege-drop fidelity under a normal subordinate-ID map;
- exact rebuild reproducibility, because the official Dockerfile uses mutable
  apt/Conda/pip resolutions and an unhashed Miniconda installer URL.

Scientific authority delta: `NONE`.

## Terminals

`P1_SAB_LUNARC_OFFICIAL_PUBLIC_BASE_SMOKE_PASS__EXACT_PINNED_DOCKERFILE_BOUND__IMAGE_AND_NODE_LOCAL_LAYERS_REMOVED__ZERO_TASKS_RUN__ZERO_OUTCOMES_OPENED`

`P1_SAB_LUNARC_OFFICIAL_PUBLIC_BASE_FAILURE_CHAIN_BOUND__8_FAILURES_REPAIRED_TO_1_PASS__ZERO_TASKS_RUN__ZERO_OUTCOMES_OPENED`
