from __future__ import annotations
from collections import Counter, defaultdict
from .types import TransitionObservation, EmpiricalMechanicContract, Verdict


class TransitionContractInducer:
    """Induce an inspectable empirical transition contract from real observations.

    This object deliberately separates *observed transition regularity* from
    semantic/authority claims.  A modal effect is an empirical summary, not a
    proof that the mechanic always has that effect.
    """
    def __init__(self, min_support: int = 2) -> None:
        self.min_support=min_support
        self._contracts: dict[str,EmpiricalMechanicContract]={}

    def fit(self, rows: list[TransitionObservation]) -> 'TransitionContractInducer':
        by=defaultdict(list)
        for r in rows:
            if r.verdict == Verdict.SUCCESS:
                by[r.mechanic_id].append(r)
        out={}
        for mid,rs in by.items():
            effects=Counter(r.effect for r in rs)
            modal=effects.most_common(1)[0][0] if len(rs)>=self.min_support else None
            keys=sorted({k for r in rs for k in r.context})
            ctx={k:tuple(sorted({str(r.context.get(k,'<missing>')) for r in rs})) for k in keys}
            out[mid]=EmpiricalMechanicContract(
                mid,len(rs),dict(effects),modal,
                tuple(sorted({r.donor for r in rs})),
                tuple(sorted({r.source_id for r in rs})),ctx
            )
        self._contracts=out
        return self

    def get(self, mechanic_id: str) -> EmpiricalMechanicContract | None:
        return self._contracts.get(mechanic_id)

    def predict_effect(self, mechanic_id: str) -> tuple[Verdict,str|None]:
        c=self.get(mechanic_id)
        if c is None or c.modal_effect is None:
            return Verdict.UNKNOWN,None
        return Verdict.SUCCESS,c.modal_effect

    @property
    def contracts(self) -> tuple[EmpiricalMechanicContract,...]:
        return tuple(self._contracts[k] for k in sorted(self._contracts))
