from __future__ import annotations
from dataclasses import asdict, dataclass
from pathlib import Path
import hashlib, json
from .types import Experience, Verdict

GENESIS='0'*64


def _experience_payload(e: Experience) -> dict:
    # Fail closed when evidence/features cannot be represented deterministically.
    d=asdict(e); d['verdict']=e.verdict.value
    json.dumps(d,sort_keys=True,separators=(',',':'))
    return d


def _hash(prev: str, payload: dict) -> str:
    raw=json.dumps({'prev':prev,'experience':payload},sort_keys=True,separators=(',',':')).encode()
    return hashlib.sha256(raw).hexdigest()

@dataclass(frozen=True)
class LedgerEntry:
    index: int
    prev_hash: str
    content_hash: str
    experience: Experience


class ExperienceLedger:
    """Append-only hash-chained local history for success/failure/unknown evidence."""
    def __init__(self) -> None:
        self._entries: list[LedgerEntry]=[]

    def append(self,e:Experience)->LedgerEntry:
        prev=self._entries[-1].content_hash if self._entries else GENESIS
        payload=_experience_payload(e); h=_hash(prev,payload)
        ent=LedgerEntry(len(self._entries),prev,h,e); self._entries.append(ent); return ent

    @property
    def entries(self)->tuple[LedgerEntry,...]: return tuple(self._entries)

    def verify(self)->bool:
        prev=GENESIS
        for i,e in enumerate(self._entries):
            if e.index!=i or e.prev_hash!=prev or e.content_hash!=_hash(prev,_experience_payload(e.experience)):
                return False
            prev=e.content_hash
        return True

    def write_jsonl(self,path:Path)->None:
        path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('w',encoding='utf-8') as f:
            for e in self._entries:
                row={'index':e.index,'prev_hash':e.prev_hash,'content_hash':e.content_hash,'experience':_experience_payload(e.experience)}
                f.write(json.dumps(row,sort_keys=True)+'\n')

    @classmethod
    def read_jsonl(cls,path:Path)->'ExperienceLedger':
        led=cls()
        for line in Path(path).read_text(encoding='utf-8').splitlines():
            if not line.strip(): continue
            row=json.loads(line); d=row['experience']; d['verdict']=Verdict(d['verdict'])
            e=Experience(**d); ent=led.append(e)
            if ent.index!=row['index'] or ent.prev_hash!=row['prev_hash'] or ent.content_hash!=row['content_hash']:
                raise ValueError('ledger integrity failure')
        return led
