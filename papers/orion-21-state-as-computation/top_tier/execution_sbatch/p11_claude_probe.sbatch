#!/usr/bin/env bash
#SBATCH -J p11clprobe
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH -t 01:00:00
#SBATCH -n 1
#SBATCH -c 4
#SBATCH --mem=8G
#SBATCH -o /home/scyiu/orion-p11-campaign/logs/clprobe_%j.out
# Claude lane same-window echo probe: run at/after 03:10 Stockholm (window start),
# exact sentinel P11CLAUDEPROBE; on PASS flips the model-identity freeze entry to
# VERIFIED (the manifest emitter hard-gates on this).
set -uo pipefail
export HOME=/home/scyiu
module load nodejs/20.9.0 2>/dev/null || true
export PATH=/home/scyiu/orion-p11-campaign/npm-prefix/bin:$PATH
echo "NODE=$(hostname) UTC=$(date -u +%FT%TZ)"
command -v claude && claude --version
echo ---SESSIONS_BEGIN
claude sessions list 2>&1 | head -5 || true
echo ---SESSIONS_END
echo ---ECHO_BEGIN
OUT=$(claude -p "Reply with exactly: P11CLAUDEPROBE" --model claude-fable-5 --output-format text 2>&1)
RC=$?
echo "rc=$RC out=$OUT"
echo ---ECHO_END
python3 - "$OUT" "$RC" << 'PYEOF'
import json, sys, datetime
out, rc = sys.argv[1], sys.argv[2]
ok = (rc == "0" and out.strip().endswith("P11CLAUDEPROBE")
      and len(out.strip()) <= 40)
from pathlib import Path
p = Path("/home/scyiu/orion-p11-campaign/scripts/P11_EXTERNAL_MODEL_IDENTITY_FREEZE_V1.json")
d = json.loads(p.read_text())
for e in d["model_identities"]:
    if e["model_identity_id"] == "claude-fable-5-cli":
        v = e["verification"]
        v = v if isinstance(v, dict) else {}
        if ok:
            v.update({"status": "VERIFIED",
                      "result": "PASS — exact sentinel P11CLAUDEPROBE returned at window start",
                      "verified_on": f"probe rc=0 sentinel-exact at {datetime.datetime.now(datetime.timezone.utc).isoformat()}"})
        else:
            v.update({"status": "PROBE_FAILED",
                      "result": f"FAIL rc={rc} out={out[:200]}",
                      "verified_on": datetime.datetime.now(datetime.timezone.utc).isoformat()})
        e["verification"] = v
p.write_text(json.dumps(d, indent=2, sort_keys=True))
print("FREEZE_UPDATED status=", v["status"])
PYEOF
