#!/usr/bin/env python3
from __future__ import annotations
import argparse,itertools,json
from pathlib import Path
P=7
INV=[0]+[pow(i,-1,P) for i in range(1,P)]
def norm(v):
 v=tuple(x%P for x in v)
 for x in v:
  if x:
   s=INV[x];return tuple(y*s%P for y in v)
 raise ValueError
def det(a,b,c):
 return (a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0]))%P
def dot(a,b):return sum(x*y for x,y in zip(a,b))%P
def build():
 points=sorted({norm((a,b,c)) for a in range(P) for b in range(P) for c in range(P) if (a,b,c)!=(0,0,0)});assert len(points)==57
 pid={q:i for i,q in enumerate(points)}
 line_masks=[]
 for line in points:
  mask=0
  for i,q in enumerate(points):
   if dot(line,q)==0:mask|=1<<i
  assert mask.bit_count()==8;line_masks.append(mask)
 e1,e2,e3,u=map(norm,[(1,0,0),(0,1,0),(0,0,1),(1,1,1)])
 frame_ids={pid[e1],pid[e2],pid[e3],pid[u]};frame_mask=sum(1<<i for i in frame_ids);remainder=[i for i in range(57) if i not in frame_ids]
 candidates=[]
 for extra in itertools.combinations(remainder,3):
  mask=frame_mask
  for i in extra:mask|=1<<i
  if all((mask&lm).bit_count()<=3 for lm in line_masks):candidates.append(tuple(sorted((*frame_ids,*extra))))
 assert len(candidates)==18451;candidate_set=set(candidates)
 d=[[[0]*57 for _ in range(57)] for _ in range(57)]
 for i,a in enumerate(points):
  for j,b in enumerate(points):
   for k,c in enumerate(points):d[i][j][k]=det(a,b,c)
 def norm_id(v):return pid[norm(v)]
 def frame_images(sids):
  s=list(sids);images=set()
  for a in s:
   for b in s:
    if b==a:continue
    for c in s:
     if c in (a,b) or d[a][b][c]==0:continue
     for f in s:
      if f in (a,b,c):continue
      den1,den2,den3=d[f][b][c],d[a][f][c],d[a][b][f]
      if not den1 or not den2 or not den3:continue
      i1,i2,i3=INV[den1],INV[den2],INV[den3];image=[]
      for x in s:image.append(norm_id((d[x][b][c]*i1%P,d[a][x][c]*i2%P,d[a][b][x]*i3%P)))
      images.add(tuple(sorted(image)))
  return images
 covered={};reps=[]
 for candidate in candidates:
  if candidate in covered:continue
  orbit=frame_images(candidate)&candidate_set;canonical=min(orbit)
  for image in orbit:covered[image]=canonical
  reps.append(canonical)
 reps=sorted(set(reps));assert len(covered)==18451 and len(reps)==54
 def maxline(sids):
  mask=sum(1<<i for i in sids);return max((mask&lm).bit_count() for lm in line_masks)
 ml=[maxline(r) for r in reps];stats={'projective_points':57,'frame_containing_candidate_arcs':18451,'projective_equivalence_classes':54,'classes_with_a_collinear_triple':sum(v==3 for v in ml),'classes_with_no_three_collinear':sum(v==2 for v in ml)}
 assert stats['classes_with_a_collinear_triple']==53 and stats['classes_with_no_three_collinear']==1
 return reps,stats,points
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write-reps',type=Path);ap.add_argument('--json',action='store_true');a=ap.parse_args();reps,stats,points=build()
 if a.write_reps:a.write_reps.write_text(''.join(' '.join(','.join(map(str,points[i])) for i in r)+'\n' for r in reps))
 print(json.dumps(stats,sort_keys=True) if a.json else 'SUPPORT7_PROJECTIVE_COVER_GREEN '+' '.join(f'{k}={v}' for k,v in stats.items()))
if __name__=='__main__':main()
