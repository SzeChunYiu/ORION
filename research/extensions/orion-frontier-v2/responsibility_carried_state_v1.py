from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
import json
from typing import Mapping, Sequence

def canonical(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",",":"), ensure_ascii=False)

def digest(value) -> str:
    return "sha256:"+sha256(canonical(value).encode()).hexdigest()

class WitnessStatus(str,Enum):
    SUPPORTED="SUPPORTED"
    APPROXIMATE="APPROXIMATE"
    UNRESOLVED="UNRESOLVED"

class ConsumptionDecision(str,Enum):
    USE_COMPILED="USE_COMPILED"
    REOPEN_REQUIRED="REOPEN_REQUIRED"
    CANNOT_CHECK="CANNOT_CHECK"

@dataclass(frozen=True)
class ResponsibilityWitness:
    responsibility_id:str
    witness_id:str
    status:WitnessStatus
    resource_bound:tuple[tuple[str,float],...]
    authority_owner_id:str

    def unsigned(self):
        return {"responsibility_id":self.responsibility_id,"witness_id":self.witness_id,
                "status":self.status.value,"resource_bound":[list(x) for x in self.resource_bound],
                "authority_owner_id":self.authority_owner_id}

@dataclass(frozen=True)
class ResponsibilityCarryingState:
    source_digest:str
    compiler_digest:str
    compiled_state_digest:str
    responsibility_witnesses:tuple[ResponsibilityWitness,...]
    omitted_coordinate_classes:tuple[str,...]
    raw_source_available:bool
    reconstruction_witness_id:str|None
    frozen_context:tuple[tuple[str,str],...]
    required_same_coordinates:tuple[str,...]
    reopen_on_change_coordinates:tuple[str,...]
    evaluator_id:str
    authority_owner_id:str
    receipt_digest:str

    def unsigned(self):
        return {
          "version":"ResponsibilityCarryingState.v1",
          "source_digest":self.source_digest,"compiler_digest":self.compiler_digest,
          "compiled_state_digest":self.compiled_state_digest,
          "responsibility_witnesses":[w.unsigned() for w in self.responsibility_witnesses],
          "omitted_coordinate_classes":list(self.omitted_coordinate_classes),
          "raw_source_available":self.raw_source_available,
          "reconstruction_witness_id":self.reconstruction_witness_id,
          "frozen_context":[list(x) for x in self.frozen_context],
          "required_same_coordinates":list(self.required_same_coordinates),
          "reopen_on_change_coordinates":list(self.reopen_on_change_coordinates),
          "evaluator_id":self.evaluator_id,"authority_owner_id":self.authority_owner_id,
          "grants_scientific_authority":False,"grants_novelty_authority":False,
        }

    def verify(self):
        if self.evaluator_id==self.authority_owner_id:
            raise ValueError("evaluator cannot own authority")
        if not all(x.startswith("sha256:") for x in (self.source_digest,self.compiler_digest,self.compiled_state_digest)):
            raise ValueError("all state/compiler identities must be content digests")
        ids=[w.responsibility_id for w in self.responsibility_witnesses]
        if not ids or len(ids)!=len(set(ids)):
            raise ValueError("responsibility ids required and unique")
        if set(self.required_same_coordinates)&set(self.reopen_on_change_coordinates):
            raise ValueError("required-same and reopen coordinates overlap")
        context=dict(self.frozen_context)
        if not set(self.required_same_coordinates+self.reopen_on_change_coordinates)<=set(context):
            raise ValueError("context policy references absent frozen coordinate")
        if self.raw_source_available is False and self.reconstruction_witness_id:
            raise ValueError("reconstruction witness without retained/recoverable source")
        if digest(self.unsigned())!=self.receipt_digest:
            raise ValueError("receipt digest mismatch")

def _rows(values:Mapping[str,float]) -> tuple[tuple[str,float],...]:
    return tuple(sorted((str(k),float(v)) for k,v in values.items()))

def build_witness(*,responsibility_id:str,witness_id:str,status:WitnessStatus,
                  resource_bound:Mapping[str,float],authority_owner_id:str)->ResponsibilityWitness:
    w=ResponsibilityWitness(str(responsibility_id),str(witness_id),WitnessStatus(status),_rows(resource_bound),str(authority_owner_id))
    if not w.responsibility_id or not w.witness_id or not w.authority_owner_id:
        raise ValueError("witness identities required")
    return w

def build_state(*,source_digest:str,compiler_digest:str,compiled_state_digest:str,
                responsibility_witnesses:Sequence[ResponsibilityWitness],
                omitted_coordinate_classes:Sequence[str]=(),raw_source_available:bool=False,
                reconstruction_witness_id:str|None=None,frozen_context:Mapping[str,str],
                required_same_coordinates:Sequence[str]=(),reopen_on_change_coordinates:Sequence[str]=(),
                evaluator_id:str,authority_owner_id:str)->ResponsibilityCarryingState:
    payload={
      "version":"ResponsibilityCarryingState.v1","source_digest":source_digest,"compiler_digest":compiler_digest,
      "compiled_state_digest":compiled_state_digest,"responsibility_witnesses":[w.unsigned() for w in responsibility_witnesses],
      "omitted_coordinate_classes":sorted(set(map(str,omitted_coordinate_classes))),
      "raw_source_available":bool(raw_source_available),"reconstruction_witness_id":reconstruction_witness_id,
      "frozen_context":[list(x) for x in sorted((str(k),str(v)) for k,v in frozen_context.items())],
      "required_same_coordinates":sorted(set(map(str,required_same_coordinates))),
      "reopen_on_change_coordinates":sorted(set(map(str,reopen_on_change_coordinates))),
      "evaluator_id":str(evaluator_id),"authority_owner_id":str(authority_owner_id),
      "grants_scientific_authority":False,"grants_novelty_authority":False,
    }
    s=ResponsibilityCarryingState(
      source_digest=source_digest,compiler_digest=compiler_digest,compiled_state_digest=compiled_state_digest,
      responsibility_witnesses=tuple(responsibility_witnesses),
      omitted_coordinate_classes=tuple(payload["omitted_coordinate_classes"]),
      raw_source_available=payload["raw_source_available"],reconstruction_witness_id=reconstruction_witness_id,
      frozen_context=tuple((str(a),str(b)) for a,b in payload["frozen_context"]),
      required_same_coordinates=tuple(payload["required_same_coordinates"]),
      reopen_on_change_coordinates=tuple(payload["reopen_on_change_coordinates"]),
      evaluator_id=payload["evaluator_id"],authority_owner_id=payload["authority_owner_id"],
      receipt_digest=digest(payload))
    s.verify(); return s

def assess(state:ResponsibilityCarryingState,*,responsibility_id:str,
           current_context:Mapping[str,str],requested_resource_bound:Mapping[str,float]) -> ConsumptionDecision:
    state.verify()
    ctx=dict(state.frozen_context)
    now={str(k):str(v) for k,v in current_context.items()}
    for key in state.required_same_coordinates:
        if key not in now or now[key]!=ctx[key]:
            return ConsumptionDecision.CANNOT_CHECK
    for key in state.reopen_on_change_coordinates:
        if key not in now:
            return ConsumptionDecision.CANNOT_CHECK
        if now[key]!=ctx[key]:
            if state.raw_source_available and state.reconstruction_witness_id:
                return ConsumptionDecision.REOPEN_REQUIRED
            return ConsumptionDecision.CANNOT_CHECK
    matches=[w for w in state.responsibility_witnesses if w.responsibility_id==responsibility_id]
    if len(matches)!=1:
        return ConsumptionDecision.CANNOT_CHECK
    w=matches[0]
    if w.status is not WitnessStatus.SUPPORTED:
        return ConsumptionDecision.CANNOT_CHECK
    if w.resource_bound!=_rows(requested_resource_bound):
        return ConsumptionDecision.CANNOT_CHECK
    return ConsumptionDecision.USE_COMPILED
