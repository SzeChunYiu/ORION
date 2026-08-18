from __future__ import annotations
from pathlib import Path
from collections import Counter,defaultdict
import json,sys,math
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent.parent/'framework'))
from orion_learning_machine import TransitionObservation,TransitionContractInducer


def effect(after:int)->str:
    return 'closed' if after==0 else 'one_goal' if after==1 else 'branched'

def load():
    d=json.loads((HERE/'HF_MATHLIB_TACTICS_SAMPLE.json').read_text())
    return [TransitionObservation(r['tactic'],{'target':r['target']},effect(r['after']),d['source'],r['module'],f"viewer:{r['viewer_line']}") for r in d['rows']]

def globally_cross_module(rows):
    src=defaultdict(set); n=Counter()
    for r in rows: src[r.mechanic_id].add(r.source_id); n[r.mechanic_id]+=1
    return {m for m in n if n[m]>=2 and len(src[m])>=2}

def entropy(counts):
    n=sum(counts.values())
    return -sum((v/n)*math.log2(v/n) for v in counts.values()) if n else None

def main():
    rows=load(); eligible=globally_cross_module(rows)
    full=TransitionContractInducer(min_support=2).fit(rows)
    contracts=[]
    for c in full.contracts:
        if c.mechanic_id in eligible:
            contracts.append({
              'mechanic_id':c.mechanic_id,'support':c.support,'modules':len(c.source_ids),
              'effect_counts':dict(c.effect_counts),'modal_effect':c.modal_effect,
              'effect_entropy_bits':entropy(c.effect_counts),'context_values':dict(c.context_values)
            })
    global_effect=Counter(r.effect for r in rows).most_common(1)[0][0]
    known=correct=base_correct=unknown=0; per=[]
    for mod in sorted({r.source_id for r in rows}):
        tr=[r for r in rows if r.source_id!=mod]; te=[r for r in rows if r.source_id==mod]
        ind=TransitionContractInducer(min_support=1).fit(tr)
        k=c=b=u=0
        for r in te:
            if r.mechanic_id not in eligible: continue
            pred=ind.get(r.mechanic_id)
            if pred is None or pred.modal_effect is None:
                u+=1; unknown+=1; continue
            k+=1; known+=1
            c+=pred.modal_effect==r.effect; correct+=pred.modal_effect==r.effect
            b+=global_effect==r.effect; base_correct+=global_effect==r.effect
        if k or u: per.append({'held_out_module':mod,'known':k,'unknown':u,'contract_accuracy':c/k if k else None,'global_baseline_accuracy':b/k if k else None})
    results={
      'authority':'REAL GOAL->TACTIC->GOALS-AFTER VIEWER SAMPLE; SMALL SMOKE TEST; NO KERNEL REPLAY',
      'rows':len(rows),'modules':len({r.source_id for r in rows}),'effect_counts':dict(Counter(r.effect for r in rows)),
      'eligible_cross_module_mechanics':sorted(eligible),'contracts':contracts,
      'leave_module_out':{
        'eligible_rows_known':known,'unknown':unknown,
        'contract_accuracy':correct/known if known else None,
        'global_effect_baseline_accuracy':base_correct/known if known else None,
        'coverage_of_all_rows':known/len(rows),
        'per_module':per
      }
    }
    (HERE/'RESULTS_PHASE2B.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps(results,indent=2))
if __name__=='__main__': main()
