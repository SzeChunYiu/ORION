#!/usr/bin/env python3
"""Build a self-contained, presentation-only interactive HTML atlas."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def build(atlas_path: Path, output: Path) -> None:
    atlas = json.loads(atlas_path.read_text(encoding="utf-8"))
    data = {
        "paper_states": atlas["paper_states"],
        "metric_records": atlas["metric_records"],
        "anomalies": atlas["anomalies"],
        "des_execution": atlas["des_execution"],
        "sources": atlas["sources"],
    }
    encoded = json.dumps(data, sort_keys=True, separators=(",", ":")).replace("</", "<\\/")
    boundary = html.escape(atlas["authority_boundary"])
    document = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ORION P1-P15 evidence atlas</title>
<style>
:root{{--ink:#18212b;--muted:#5c6875;--line:#d8dee6;--paper:#fff;--wash:#f3f6f8;--blue:#0072b2;--fail:#d55e00;--cc:#6f2dbd;--adv:#cc79a7}}
*{{box-sizing:border-box}} body{{margin:0;font:15px/1.45 system-ui,sans-serif;color:var(--ink);background:var(--wash)}}
header,main{{max-width:1220px;margin:auto;padding:24px}} header{{padding-bottom:8px}} h1{{margin:.1em 0}} .boundary{{background:#fff3cd;border-left:5px solid #e69f00;padding:12px}}
.boundary{{overflow-wrap:anywhere}}
.controls{{display:flex;flex-wrap:wrap;gap:12px;background:var(--paper);padding:14px;border:1px solid var(--line);border-radius:10px;position:sticky;top:0;z-index:2}}
label{{font-weight:650}} select,input{{font:inherit;padding:6px 8px;margin-left:5px}} section{{background:var(--paper);margin:18px 0;padding:18px;border:1px solid var(--line);border-radius:10px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:10px}} .card{{border:1px solid var(--line);border-left:6px solid var(--blue);padding:10px;border-radius:7px}}
.FAIL{{border-left-color:var(--fail)}} .CANNOT_CHECK{{border-left-color:var(--cc)}} .ADVERSE,.MIXED{{border-left-color:var(--adv)}}
.bar-row{{display:grid;grid-template-columns:minmax(170px,1fr) 4fr 90px;gap:8px;align-items:center;margin:6px 0}} .track{{position:relative;background:#e9eef2;height:16px;overflow:hidden}} .bar{{position:absolute;top:0;background:var(--blue);height:100%}} .bar.negative{{background:var(--fail)}} .zero{{position:absolute;top:0;bottom:0;width:1px;background:var(--ink);opacity:.65}}
.des-track{{position:relative;background:#e5e7eb;height:20px;overflow:hidden}} .des-observed{{position:absolute;inset:3px auto 3px 0;background:#56b4e9}} .des-valid{{position:absolute;inset:7px auto 7px 0;background:#009e73}} .des-zero{{position:absolute;inset:0 auto 0 0;width:2px;background:var(--ink)}}
table{{border-collapse:collapse;width:100%;font-size:13px}} th,td{{border-bottom:1px solid var(--line);text-align:left;padding:7px;vertical-align:top}} th{{background:white}}
.source-scroll{{max-width:100%;overflow-x:auto;overscroll-behavior-inline:contain}} .source-table{{min-width:880px;table-layout:auto}} .source-path code{{overflow-wrap:normal;word-break:normal}} .source-hash{{white-space:nowrap}}
.card small,.card p{{overflow-wrap:anywhere}} .card small{{display:block}} .muted{{color:var(--muted)}} .empty{{padding:12px;color:var(--muted)}}
@media(max-width:650px){{header,main{{padding:12px}} .controls{{display:grid;grid-template-columns:minmax(0,1fr);position:static}} .controls label{{display:grid;gap:4px}} .controls select,.controls input{{margin-left:0;max-width:100%;width:100%;min-width:0}} .controls button{{justify-self:start}} .bar-row{{grid-template-columns:1fr}} th{{position:static}}}}
</style>
</head>
<body><header><h1>ORION P1-P15 evidence atlas</h1>
<p class="boundary"><strong>Claim ceiling:</strong> {boundary}. Interactive filtering changes only presentation; it never changes a terminal or grants authority.</p></header>
<main><div class="controls">
<label>Paper <select id="paper"><option value="ALL">All</option></select></label>
<label>Status contains <input id="status" placeholder="e.g. FAIL"></label>
<label>Metric <select id="metric"><option value="ALL">All exact metrics</option></select></label>
<button id="reset">Reset</button></div>
<section><h2>Paper terminals</h2><div id="states" class="grid"></div></section>
<section><h2>Exact metric records</h2><p class="muted">Bars scale within the visible exact metric only. Different units are never combined into one bar scale.</p><div id="bars"></div></section>
<section><h2>Frozen #1332 DES execution coverage</h2><p class="muted">Gray = planned, blue = observed/executed, green = valid at the registered internal scope. Each row uses its own denominator; coverage is not performance or authority.</p><div id="des-execution"></div></section>
<section><h2>Anomalies and adverse boundaries</h2><div id="anomalies" class="grid"></div></section>
<section><h2>Source bindings</h2><p class="muted">On narrow screens, scroll this table horizontally; paths and digests are kept readable.</p><div class="source-scroll" tabindex="0"><table class="source-table"><thead><tr><th>Paper</th><th>ID</th><th>Path</th><th>SHA-256</th><th>Authority tier</th></tr></thead><tbody id="sources"></tbody></table></div></section>
</main>
<script id="atlas-data" type="application/json">{encoded}</script>
<script>
const D=JSON.parse(document.getElementById('atlas-data').textContent), byId=id=>document.getElementById(id);
const paper=byId('paper'), status=byId('status'), metric=byId('metric');
for(let i=1;i<=15;i++) paper.add(new Option('P'+i,'P'+i));
const pretty=s=>String(s??'').replace(/[_-]+/g,' ').replace(/\\s+/g,' ').trim();
const metrics=[...new Set(D.metric_records.map(x=>x.metric))].sort(); metrics.forEach(x=>metric.add(new Option(pretty(x),x)));
const esc=s=>String(s??'').replace(/[&<>\"']/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}}[c]));
const keep=x=>(paper.value==='ALL'||x.paper_id===paper.value)&&(!status.value||String(x.status||x.terminal||'').toUpperCase().includes(status.value.toUpperCase()));
function render(){{
 const states=D.paper_states.filter(keep); byId('states').innerHTML=states.length?states.map(x=>`<article class="card ${{esc(x.status)}}"><b>${{esc(x.paper_id)}} · ${{esc(x.title)}}</b><div>${{esc(x.status)}}</div><small>${{esc(x.terminal)}}</small></article>`).join(''):'<p class="empty">No matching states.</p>';
 const rows=D.metric_records.filter(x=>keep(x)&&(metric.value==='ALL'||x.metric===metric.value));
 const units=[...new Set(rows.map(x=>x.unit))], exact=[...new Set(rows.map(x=>x.metric))];
 if(rows.length && exact.length===1 && units.length===1){{const lo=Math.min(0,...rows.map(x=>x.value)),hi=Math.max(0,...rows.map(x=>x.value)),span=Math.max(hi-lo,1e-12),zero=100*(0-lo)/span;byId('bars').innerHTML=rows.slice(0,120).map(x=>{{const left=100*(Math.min(0,x.value)-lo)/span,width=100*Math.abs(x.value)/span;return `<div class="bar-row"><span>${{esc(x.paper_id)}} · ${{esc(pretty(x.arm||x.case_id||x.name))}}</span><span class="track"><span class="zero" style="left:${{zero}}%"></span><span class="bar ${{x.value<0?'negative':''}}" style="left:${{left}}%;width:${{width}}%"></span></span><code>${{Number(x.value).toPrecision(5)}} ${{esc(x.unit)}}</code></div>`}}).join('')}}
 else byId('bars').innerHTML=`<p class="empty">Choose one exact metric to enable a unit-preserving bar view. ${{rows.length}} records currently match.</p>`;
 const desRows=D.des_execution.filter(keep);byId('des-execution').innerHTML=desRows.length?desRows.map(x=>{{const observed=100*x.observed/x.planned,valid=100*x.valid/x.planned;return `<div class="bar-row"><span>${{esc(x.paper_id)}} · ${{esc(x.status)}}</span><span class="des-track"><span class="des-observed" style="width:${{observed}}%"></span><span class="des-valid" style="width:${{valid}}%"></span>${{valid===0?'<span class="des-zero"></span>':''}}</span><code>${{x.valid}}/${{x.observed}}/${{x.planned}} ${{esc(x.unit)}}</code></div>`}}).join(''):'<p class="empty">No frozen DES rows match. Filtering never changes the underlying denominators.</p>';
 const anomalies=D.anomalies.filter(keep);byId('anomalies').innerHTML=anomalies.length?anomalies.map(x=>`<article class="card ${{esc(x.severity)}}"><b>${{esc(x.paper_id)}} · ${{esc(x.severity)}}</b><p>${{esc(x.finding)}}</p><small>Sources: ${{esc((x.source_ids||[x.source_id]).join(', '))}}</small></article>`).join(''):'<p class="empty">No matching anomalies. Unfiltered atlas retains '+D.anomalies.length+'.</p>';
 const sources=D.sources.filter(x=>paper.value==='ALL'||x.paper===paper.value);byId('sources').innerHTML=sources.map(x=>`<tr><td>${{esc(x.paper)}}</td><td>${{esc(x.id)}}</td><td class="source-path"><code>${{esc(x.path)}}</code></td><td class="source-hash"><code>${{esc(x.sha256)}}</code></td><td>${{esc(x.authority_tier)}}</td></tr>`).join('');
}}
[paper,status,metric].forEach(x=>x.addEventListener('input',render));byId('reset').onclick=()=>{{paper.value='ALL';status.value='';metric.value='ALL';render()}};render();
</script></body></html>"""
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(document, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--atlas", type=Path, default=ROOT / "visualization/data/derived/atlas.json"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "visualization/figures/interactive/evidence_atlas.html",
    )
    args = parser.parse_args()
    build(args.atlas, args.output)
    print(args.output)
    print("SCIENTIFIC_AUTHORITY=REPOSITORY_RECEIPTS_ONLY__NO_EXTERNAL_AUTHORITY_DELTA")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
