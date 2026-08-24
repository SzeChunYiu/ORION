# Release procedure

The package version is `0.1.0`. A release is valid only when the source commit is
on `main`, the commands below pass from a clean checkout, and the annotated tag
`orion-research-harness-v0.1.0` points to that exact `main` commit.

```bash
python -m venv .venv-release
. .venv-release/bin/activate
python -m pip install --upgrade pip build pytest
python -m pytest -q
python -m build ../.. --outdir dist/root
python -m build . --outdir dist/harness
python -m pip install --force-reinstall \
  dist/root/orion_research_os-0.1.0-py3-none-any.whl \
  dist/harness/orion_research_harness-0.1.0-py3-none-any.whl
orion-harness mechanics-coverage
orion-harness execution-coverage
```

Record SHA-256 digests for both packages' sdists and wheels and attach the four
files plus the digests to the release. Build artifacts are not committed to the
repository. The harness declares its exact `orion-research-os==0.1.0` runtime
dependency; it is not a misleading standalone wheel.

The tag and artifacts establish software identity only. They do not establish
that the P15 public workload/runtime gate passed, that Q3 is reliable outside its
frozen cases, or that another site independently reproduced either result. The
Apache-2.0 expression is a mechanical metadata declaration; rights-holder
relicensing authority for the pre-existing package remains `CANNOT_CHECK`.
