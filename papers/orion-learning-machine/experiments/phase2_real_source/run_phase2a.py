from __future__ import annotations
from pathlib import Path
from collections import Counter, defaultdict
import hashlib, json, random, statistics, sys

HERE=Path(__file__).resolve().parent
FRAMEWORK=HERE.parent.parent/'framework'
sys.path.insert(0,str(FRAMEWORK))

from orion_learning_machine.adapters.lean_source import parse_lean_source, tactic_action
from orion_learning_machine.abstraction import mine_macros
from orion_learning_machine.runtime import LearningMachine


def donor_for(path: Path) -> str:
    name=path.parent.name
    if name=='YuanheZ_lean-stat-learning-theory': return 'YuanheZ/lean-stat-learning-theory'
    if name=='auto-res_lean-rademacher': return 'auto-res/lean-rademacher'
    return name


def load_trajectories():
    root=HERE/'corpus'; fam=[]; raw=[]
    for p in sorted(root.rglob('*.lean')):
        donor=donor_for(p); source=str(p.relative_to(root)); text=p.read_text(encoding='utf-8')
        for t in parse_lean_source(text,source):
            tid=f'{source}::{t.theorem_name}'
            fs=list(t.tactics)
            rs=[]
            for line in t.raw_lines:
                a=tactic_action(line)
                if a and (not rs or rs[-1]!=a): rs.append(a)
            if fs:
                fam.append({'trajectory_id':tid,'donor':donor,'source_id':source,'mechanics':fs,'theorem':t.theorem_name})
            if rs:
                raw.append({'trajectory_id':tid,'donor':donor,'source_id':source,'mechanics':rs,'theorem':t.theorem_name})
    return fam,raw


def ngrams(seq,n): return [tuple(seq[i:i+n]) for i in range(len(seq)-n+1)]


def seen_coverage(train,test,n):
    seen={g for t in train for g in ngrams(t['mechanics'],n)}
    gs=[g for t in test for g in ngrams(t['mechanics'],n)]
    return (sum(g in seen for g in gs)/len(gs)) if gs else None, len(gs)


def loo_coverage(rows,n):
    sources=sorted({r['source_id'] for r in rows}); hit=total=0
    per=[]
    for s in sources:
        tr=[r for r in rows if r['source_id']!=s]; te=[r for r in rows if r['source_id']==s]
        c,k=seen_coverage(tr,te,n)
        if k:
            hit += round(c*k); total += k; per.append((s,c,k))
    return (hit/total if total else None),total,per


def markov_eval(train,test):
    next_by=defaultdict(Counter); global_next=Counter()
    for r in train:
        for a,b in zip(r['mechanics'],r['mechanics'][1:]):
            next_by[a][b]+=1; global_next[b]+=1
    if not global_next: return {'markov':None,'unigram':None,'n':0}
    global_pred=global_next.most_common(1)[0][0]
    hm=hu=n=0
    for r in test:
        for a,b in zip(r['mechanics'],r['mechanics'][1:]):
            pred=next_by[a].most_common(1)[0][0] if next_by[a] else global_pred
            hm += pred==b; hu += global_pred==b; n+=1
    return {'markov':hm/n if n else None,'unigram':hu/n if n else None,'n':n}


def loo_markov(rows):
    M=U=N=0
    per=[]
    for s in sorted({r['source_id'] for r in rows}):
        e=markov_eval([r for r in rows if r['source_id']!=s],[r for r in rows if r['source_id']==s])
        if e['n']:
            M += e['markov']*e['n']; U += e['unigram']*e['n']; N+=e['n']; per.append((s,e))
    return {'markov':M/N if N else None,'unigram':U/N if N else None,'n':N,'per_source':per}


def cross_donor(rows):
    out={}
    donors=sorted({r['donor'] for r in rows})
    for d in donors:
        e=markov_eval([r for r in rows if r['donor']!=d],[r for r in rows if r['donor']==d])
        cov2,_=seen_coverage([r for r in rows if r['donor']!=d],[r for r in rows if r['donor']==d],2)
        out[d]={'train_on_other_test_on_this':e,'bigram_coverage':cov2}
    return out


def recurring_cross_donor_count(rows,n):
    donors=defaultdict(set); support=Counter()
    for r in rows:
        for g in set(ngrams(r['mechanics'],n)):
            support[g]+=1; donors[g].add(r['donor'])
    return sum(1 for g,k in support.items() if k>=2 and len(donors[g])>=2)


def shuffle_test(rows,n,seed=20260818,reps=1000):
    obs=recurring_cross_donor_count(rows,n); rng=random.Random(seed+n); vals=[]
    for _ in range(reps):
        rr=[]
        for r in rows:
            seq=list(r['mechanics']); rng.shuffle(seq)
            rr.append({**r,'mechanics':seq})
        vals.append(recurring_cross_donor_count(rr,n))
    p=(1+sum(v>=obs for v in vals))/(reps+1)
    return {'observed':obs,'shuffle_mean':statistics.mean(vals),'shuffle_sd':statistics.pstdev(vals),'empirical_p_ge':p,'reps':reps}


def provenance_audit(rows,macros):
    byid={r['trajectory_id']:r for r in rows}; failures=[]
    for m in macros:
        supporters=[]
        for r in rows:
            if m.sequence in set(ngrams(r['mechanics'],len(m.sequence))): supporters.append(r)
        exp_t=tuple(sorted(r['trajectory_id'] for r in supporters))
        exp_d=tuple(sorted({r['donor'] for r in supporters})); exp_s=tuple(sorted({r['source_id'] for r in supporters}))
        if m.support!=len(supporters) or m.source_trajectories!=exp_t or m.donors!=exp_d or m.source_ids!=exp_s:
            failures.append(m.macro_id)
    return {'macros_checked':len(macros),'failures':failures,'pass':not failures}


def main():
    fam,raw=load_trajectories()
    macros=mine_macros(fam,min_support=2,min_len=2,max_len=4,require_multi_source=True,require_multi_donor=True)
    lm=LearningMachine.empty(); lm.absorb_action_families(fam)
    fam_counts=Counter(x for r in fam for x in r['mechanics']); raw_counts=Counter(x for r in raw for x in r['mechanics'])
    results={
      'authority':'REAL-SOURCE STRUCTURE-MINING ONLY; NO LEAN KERNEL REPLAY',
      'files':len({r['source_id'] for r in fam}), 'donors':sorted({r['donor'] for r in fam}),
      'theorem_trajectories':len(fam),'family_actions':sum(map(lambda r:len(r['mechanics']),fam)),
      'raw_actions':sum(map(lambda r:len(r['mechanics']),raw)),
      'unique_families':len(fam_counts),'unique_raw_actions':len(raw_counts),
      'family_counts':fam_counts,'raw_counts':raw_counts,
      'loo':{},'cross_donor':{},
      'cross_donor_macros':[m.__dict__ for m in macros],
      'provenance_audit':provenance_audit(fam,macros),
      'library':{
        'mechanics':len(lm.library.mechanics),
        'mechanics_with_both_donors':sum(len({p.donor for p in m.provenance})>=2 for m in lm.library.mechanics),
        'macros':len(lm.library.macros),
      },
      'shuffle':{'bigram':shuffle_test(fam,2),'trigram':shuffle_test(fam,3)},
    }
    for label,rows in [('family',fam),('raw',raw)]:
        results['loo'][label]={
          'bigram_coverage':loo_coverage(rows,2)[0],
          'trigram_coverage':loo_coverage(rows,3)[0],
          'markov':loo_markov(rows),
        }
        results['cross_donor'][label]=cross_donor(rows)
    # Serialize counters/tuples cleanly.
    def conv(x):
        if isinstance(x,Counter): return dict(x)
        if isinstance(x,tuple): return list(x)
        raise TypeError(type(x))
    (HERE/'RESULTS_PHASE2A.json').write_text(json.dumps(results,indent=2,default=conv)+'\n')
    print(json.dumps(results,indent=2,default=conv))

if __name__=='__main__': main()
