from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
from .types import Verdict

@dataclass(frozen=True)
class ResidualCluster:
    signature: tuple[str, ...]
    count: int
    source_count: int
    eligible_for_invention: bool
    reason: str


def residual_clusters(records: list[dict], min_count: int = 5, min_sources: int = 3) -> list[ResidualCluster]:
    """Invention is gated by recurring fresh residuals, not by one failed problem."""
    c=Counter(); src={}
    for r in records:
        if r.get("verdict") not in {Verdict.FAIL.value, Verdict.UNKNOWN.value, "fail", "unknown"}:
            continue
        sig=tuple(r.get("residual_signature", ("unspecified",)))
        c[sig]+=1; src.setdefault(sig,set()).add(r.get("source_id","unknown"))
    out=[]
    for sig,n in c.items():
        ns=len(src[sig]); ok=n>=min_count and ns>=min_sources
        reason="recurring cross-source residual" if ok else "insufficient recurrence/source diversity"
        out.append(ResidualCluster(sig,n,ns,ok,reason))
    return sorted(out,key=lambda x:(-x.count,-x.source_count,x.signature))
