#!/bin/bash
#SBATCH -J p12-env
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH -t 04:00:00
#SBATCH -N 1
#SBATCH --tasks-per-node=1
#SBATCH -D /projects/hep/fs9/users/scyiu/orion-a2-p12
#SBATCH -o logs/p12-env-%j.out
# Idempotent: builds the two conda envs the pinned upstream evaluator needs.
# Mirrors billy-old's ~/a2-deps/p12_conda_setup.sh + the additions the driver
# env needs beyond upstream requirements.txt (scipy/sklearn/rasterio are
# imported by benchmark/eval_programs/*.py which run in-process via exec();
# pipreqs is invoked bare by run_eval.config_conda_env; pyarrow reads the
# frozen parquet).
set -x
P12BASE=/projects/hep/fs9/users/scyiu/orion-a2-p12
export PATH=$HOME/.local/bin:$PATH
module load nodejs/20.9.0

# Root causes fixed after jobs 3570021/3570031 failed:
# 1. The module system exports PYTHONPATH=/sw/.../python3.11/site-packages,
#    which leaks EasyBuild pluggy/conda remnants into every python (seen as
#    pluggy SyntaxWarnings + 'conda-pypi' entry-point errors). Kill it.
# 2. CondaToSNonInteractiveError on repo.anaconda.com defaults channels.
#    Fix: campaign-local condarc + --override-channels -c conda-forge on every
#    create (explicit CLI flags beat every config file). Leaves ~/.condarc
#    and the module environment untouched outside this job.
unset PYTHONPATH
export PYTHONNOUSERSITE=1
cat > "$P12BASE/condarc" <<'EOF'
channels:
  - conda-forge
channel_priority: flexible
pkgs_dirs:
  - /projects/hep/fs9/users/scyiu/orion-a2-p12/miniconda3/pkgs
envs_dirs:
  - /projects/hep/fs9/users/scyiu/orion-a2-p12/miniconda3/envs
EOF
export CONDARC="$P12BASE/condarc"

if [ ! -x "$P12BASE/miniconda3/bin/conda" ]; then
  wget -q https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/mc.sh \
    || curl -sSL -o /tmp/mc.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
  bash /tmp/mc.sh -b -p "$P12BASE/miniconda3"
fi
CONDA="$P12BASE/miniconda3/bin/conda"

if ! "$CONDA" env list | grep -q "^sci-agent "; then
  "$CONDA" create -y --override-channels -c conda-forge -n sci-agent \
    python=3.10 pip setuptools wheel || exit 10
  "$CONDA" run -n sci-agent pip install \
    -r "$P12BASE/a2-deps/ScienceAgentBench/requirements.txt" \
    scipy scikit-learn rasterio pipreqs pyarrow || exit 11
fi
if ! "$CONDA" env list | grep -q "^sci-agent-eval "; then
  "$CONDA" create -y --override-channels -c conda-forge -n sci-agent-eval \
    python=3.10 pip setuptools wheel || exit 12
  "$CONDA" run -n sci-agent-eval pip install pip-tools || exit 13
fi

"$CONDA" run -n sci-agent python -c "import pyarrow, scipy, sklearn, rasterio, pipreqs; print('P12_ENV_OK')" || exit 14
codex --version || exit 15
claude --version || exit 16
echo P12_ENV_SETUP_DONE
