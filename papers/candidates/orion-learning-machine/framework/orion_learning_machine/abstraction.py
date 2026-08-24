from __future__ import annotations
from collections import Counter, defaultdict
from .types import MacroSpec


def mine_macros(
    trajectories: list[dict],
    min_support: int = 3,
    min_len: int = 2,
    max_len: int = 5,
    require_multi_source: bool = True,
    require_multi_donor: bool = False,
) -> list[MacroSpec]:
    """Mine contiguous mechanic subsequences while preserving donor/source lineage.

    A trajectory contributes at most one support count to a given sequence, so
    a loop inside one proof cannot manufacture recurrence.  Cross-donor
    admission can be required when testing generalized abstractions.
    """
    supports: Counter[tuple[str, ...]] = Counter()
    trajs: dict[tuple[str, ...], set[str]] = defaultdict(set)
    donors: dict[tuple[str, ...], set[str]] = defaultdict(set)
    sources: dict[tuple[str, ...], set[str]] = defaultdict(set)
    for t in trajectories:
        seq = tuple(t["mechanics"])
        seen = set()
        for n in range(min_len, min(max_len, len(seq)) + 1):
            for i in range(len(seq)-n+1):
                s = seq[i:i+n]
                if s in seen:
                    continue
                seen.add(s)
                supports[s] += 1
                trajs[s].add(t["trajectory_id"])
                donors[s].add(t["donor"])
                sources[s].add(t["source_id"])
    out=[]
    for seq, n in supports.items():
        if n < min_support:
            continue
        if require_multi_source and len(sources[seq]) < 2:
            continue
        if require_multi_donor and len(donors[seq]) < 2:
            continue
        mid = "macro:" + ">".join(seq)
        out.append(MacroSpec(
            mid,seq,n,tuple(sorted(donors[seq])),tuple(sorted(trajs[seq])),tuple(sorted(sources[seq]))
        ))
    out.sort(key=lambda m: (-m.support, -len(m.sequence), m.macro_id))
    return out
