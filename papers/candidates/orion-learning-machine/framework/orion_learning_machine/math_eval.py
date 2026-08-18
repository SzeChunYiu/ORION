from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Mapping
import hashlib, json
from .types import Provenance, Verdict


def _sha(payload: Mapping[str, Any]) -> str:
    raw=json.dumps(payload,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True)
class FrozenMathTask:
    """Content-bound mathematical evaluation subject.

    P10 uses this as an evaluation harness only; theorem correctness and claim
    authority remain outside P10.  `source_revision` must identify the frozen
    benchmark/repository state used for the attempt.
    """
    task_id: str
    statement: str
    source: str
    source_revision: str
    status_at_freeze: str = 'unknown'
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @property
    def statement_sha256(self) -> str:
        return _sha({
            'task_id':self.task_id,'statement':self.statement,'source':self.source,
            'source_revision':self.source_revision,'status_at_freeze':self.status_at_freeze,
        })


@dataclass(frozen=True)
class MathAttempt:
    task_id: str
    statement_sha256: str
    solver_id: str
    solution: str
    resource_usage: Mapping[str, Any] = field(default_factory=dict)
    provenance: tuple[Provenance, ...] = ()

    @property
    def attempt_sha256(self) -> str:
        return _sha({
            'task_id':self.task_id,'statement_sha256':self.statement_sha256,
            'solver_id':self.solver_id,'solution':self.solution,
            'resource_usage':dict(self.resource_usage),
            'provenance':[
                {'donor':p.donor,'source_id':p.source_id,'revision':p.revision,'step':p.step}
                for p in self.provenance
            ],
        })


@dataclass(frozen=True)
class VerifierReceipt:
    task_id: str
    statement_sha256: str
    attempt_sha256: str
    verifier_id: str
    verifier_revision: str
    verdict: Verdict
    details: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BoundMathResult:
    task: FrozenMathTask
    attempt: MathAttempt
    receipt: VerifierReceipt

    @property
    def verified_success(self) -> bool:
        return self.receipt.verdict == Verdict.SUCCESS


def bind_verifier_receipt(
    task: FrozenMathTask,
    attempt: MathAttempt,
    receipt: VerifierReceipt,
) -> BoundMathResult:
    """Fail closed unless task, attempt, and verifier receipt have exact identity.

    The function does *not* infer that a verifier is independent or trustworthy;
    it only prevents receipt replay/misbinding.  External P4/P8 authority must
    decide whether the named verifier and custody are admissible.
    """
    if attempt.task_id != task.task_id:
        raise ValueError('attempt task identity mismatch')
    if attempt.statement_sha256 != task.statement_sha256:
        raise ValueError('attempt statement identity mismatch')
    if receipt.task_id != task.task_id or receipt.statement_sha256 != task.statement_sha256:
        raise ValueError('receipt subject identity mismatch')
    if receipt.attempt_sha256 != attempt.attempt_sha256:
        raise ValueError('receipt attempt identity mismatch')
    if not receipt.verifier_id or not receipt.verifier_revision:
        raise ValueError('verifier identity/revision required')
    return BoundMathResult(task,attempt,receipt)
