from pathlib import Path
import json
p=Path(__file__).resolve().parents[1]/"R8_PACKET_COMMIT.json"
print(json.loads(p.read_text())["packet_commit"])
