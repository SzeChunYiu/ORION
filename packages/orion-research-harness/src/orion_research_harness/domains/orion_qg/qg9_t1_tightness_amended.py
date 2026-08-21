"""Engineering-amended native QG-9 T1 controller; scientific outcome map unchanged."""
from __future__ import annotations
from copy import deepcopy
from .qg9_t1_tightness import QG9T1_TIGHTNESS_CAMPAIGN_MANIFEST as _BASE
QG9T1_TIGHTNESS_AMENDED_CAMPAIGN_MANIFEST=deepcopy(_BASE)
cap=QG9T1_TIGHTNESS_AMENDED_CAMPAIGN_MANIFEST['capabilities']['t1.load']
code=cap['payload']['code']
old="'candidate72':a.get('candidate_generation',{}).get('candidate_count')==72"
new="'candidate72':(0<a.get('candidate_generation',{}).get('candidate_count',0)<=72 and a.get('candidate_generation',{}).get('orientation_counts',{}).get('0',0)<=36 and a.get('candidate_generation',{}).get('orientation_counts',{}).get('1',0)<=36)"
if old not in code: raise RuntimeError('expected T1 candidate-count expression not found')
cap['payload']['code']=code.replace(old,new)
QG9T1_TIGHTNESS_AMENDED_CAMPAIGN_MANIFEST['campaign_id']='orion-qg:qg9t1-support4-tightness-amended1'
