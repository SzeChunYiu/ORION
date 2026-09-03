#!/bin/bash
#SBATCH -J p12-judge-smoke
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH -t 00:45:00
#SBATCH -N 1
#SBATCH --tasks-per-node=1
#SBATCH -D /projects/hep/fs9/users/scyiu/orion-a2-p12
#SBATCH -o logs/p12-judge-smoke-%j.out
# Validates the judge-substitution path on a LUNARC compute node BEFORE the
# full tuning eval: the eval_judge_shim openai module routing one n=3
# chat.completions.create call to three bare `codex exec -i <figs>` CLI calls
# (auth, writable CODEX_HOME, image input, [FINAL SCORE] parsing).
# Success criterion: no RuntimeError, 3 choices, each parses to an int 0..100,
# at least one nonzero, exit 0.
set -x
P12BASE=/projects/hep/fs9/users/scyiu/orion-a2-p12
export PATH=$HOME/.local/bin:$P12BASE/miniconda3/bin:$PATH
module load nodejs/20.9.0
unset PYTHONPATH
export PYTHONNOUSERSITE=1
TT="$P12BASE/worktree/papers/orion-22-adaptive-state-reasoning/top_tier"
cd "$TT" || exit 20
export P12_JUDGE_LOG_DIR="$TT/eval/judge_smoke_transcripts"

"$P12BASE/miniconda3/bin/conda" run -n sci-agent --no-capture-output python - <<'PY'
import base64, io, sys
sys.path.insert(0, "eval_judge_shim")
from openai import OpenAI, parse_final_score  # the shim, first on path
from PIL import Image

img = Image.new("RGB", (96, 96), (30, 144, 255))
buf = io.BytesIO()
img.save(buf, format="PNG")
url = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

prompt = (
    "You are a strict visual evaluator for scientific figures. Compare the "
    "single provided figure against this rubric: (1) axes labeled, (2) legend "
    "present, (3) readable layout. End your reply with a final line of exactly "
    "'[FINAL SCORE]: N' where N is 0-100."
)
messages = [{
    "role": "user",
    "content": [
        {"type": "text", "text": prompt},
        {"type": "image_url", "image_url": {"url": url}},
    ],
}]
resp = OpenAI().chat.completions.create(
    model="gpt-4o-2024-05-13", messages=messages, n=3
)
scores = [parse_final_score(c.message.content) for c in resp.choices]
print("JUDGE_SMOKE_SCORES:", scores)
assert len(scores) == 3, scores
assert all(isinstance(s, int) and 0 <= s <= 100 for s in scores), scores
assert any(s > 0 for s in scores), scores
print("P12_JUDGE_SMOKE_OK")
PY
RC=$?
echo "P12_JUDGE_SMOKE_RC=$RC"
echo P12_JUDGE_SMOKE_DONE
exit $RC
