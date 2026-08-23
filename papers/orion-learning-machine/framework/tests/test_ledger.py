from pathlib import Path
import pytest
from orion_learning_machine import *

def test_ledger_preserves_failure_and_roundtrips(tmp_path:Path):
    l=ExperienceLedger()
    l.append(Experience('m',{'x':1.},Verdict.FAIL,'s','d','t',0,{'why':'counterexample'}))
    l.append(Experience('m',{'x':2.},Verdict.UNKNOWN,'s2','d2','t2',0,{}))
    assert l.verify()
    p=tmp_path/'ledger.jsonl'; l.write_jsonl(p)
    l2=ExperienceLedger.read_jsonl(p)
    assert l2.verify() and [e.experience.verdict for e in l2.entries]==[Verdict.FAIL,Verdict.UNKNOWN]

def test_ledger_tampering_fails(tmp_path:Path):
    l=ExperienceLedger(); l.append(Experience('m',{'x':1.},Verdict.FAIL,'s','d','t',0,{}))
    p=tmp_path/'ledger.jsonl'; l.write_jsonl(p)
    txt=p.read_text().replace('"x": 1.0','"x": 2.0'); p.write_text(txt)
    with pytest.raises(ValueError): ExperienceLedger.read_jsonl(p)
