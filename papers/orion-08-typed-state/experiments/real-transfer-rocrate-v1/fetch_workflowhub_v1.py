#!/usr/bin/env python3
"""Fetch WorkflowHub records read-only. Public JSON API, no credentials."""
from __future__ import annotations
import json, os, time, urllib.request, urllib.error

BASE="https://workflowhub.eu"
OUT=os.path.expanduser("~/wh_records.json")
def get(url, tries=3):
    for i in range(tries):
        try:
            req=urllib.request.Request(url, headers={"Accept":"application/json",
                                                     "User-Agent":"orion-research/1.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            if i==tries-1: return {"__err__":str(e)[:120]}
            time.sleep(1.5*(i+1))
    return None

ids=[]; page=1
while True:
    d=get(f"{BASE}/workflows.json?page={page}")
    if not d or "__err__" in d or not d.get("data"): break
    ids += [x["id"] for x in d["data"]]
    if page % 20 == 0: print(f"  listing page {page}, {len(ids)} ids", flush=True)
    page += 1
    if page > 200: break
    time.sleep(0.12)
print(f"listed {len(ids)} workflow ids over {page-1} pages", flush=True)

recs=[]
for i,wid in enumerate(ids):
    d=get(f"{BASE}/workflows/{wid}.json")
    if not d or "__err__" in d or "data" not in d:
        recs.append({"id":wid,"error":(d or {}).get("__err__","no data")}); continue
    a=d["data"].get("attributes",{})
    wc=a.get("workflow_class") or {}
    internals=a.get("internals") or {}
    recs.append({
        "id":wid,
        "workflow_class":(wc.get("key") or wc.get("title") or "UNKNOWN"),
        "license":(a.get("license") or "NONE"),
        "n_tags":len(a.get("tags") or []),
        "n_tools":len(a.get("tools") or []),
        "n_creators":len(a.get("creators") or []),
        "has_doi":bool(a.get("doi")),
        "version":a.get("version"),
        "internals_keys":sorted(internals.keys()) if isinstance(internals,dict) else [],
        "internals_nonempty":bool(internals),
    })
    if (i+1)%150==0: print(f"  fetched {i+1}/{len(ids)}", flush=True)
    time.sleep(0.10)

json.dump({"retrieved_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
           "source":"https://workflowhub.eu public JSON API",
           "n_listed":len(ids),"records":recs}, open(OUT,"w"), indent=1)
ok=[r for r in recs if "error" not in r]
print(f"\nfetched {len(ok)}/{len(ids)} records; errors {len(recs)-len(ok)}")
print("FETCH_DONE")
