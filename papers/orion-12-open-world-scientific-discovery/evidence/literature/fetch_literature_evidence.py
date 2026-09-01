"""Fetch-and-record literature evidence for ORION Paper II bibliography.

One JSON per bibliography key under papers/orion-12-.../evidence/literature/.
Every field is copied from a live fetch; nothing is written from recall.
"""
from __future__ import annotations

import json
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import defusedxml.ElementTree as ET

# Repo-relative. The previous absolute path pointed at one machine's scratch
# worktree, so re-running this script anywhere else silently wrote its records
# into a directory the manuscript does not read -- a reproducibility script that
# only reproduces on the laptop it was written on.
OUT = Path(__file__).resolve().parent
UA = "ORION-P2-lit-audit/1.0 (mailto:sze-chun.yiu@fysik.su.se)"
ATOM = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}

# key -> (kind, identifier, claimed_title, claim_provenance)
#   pre_existing_independent_claim -> the title was already in bibliography.bib
#     before this audit, so the verdict is a genuine independent comparison.
#   derived_from_this_fetch -> new entry; the claim was written FROM the fetch,
#     so the record is provenance, not an independent test.
ENTRIES: dict[str, tuple[str, str, str, str]] = {
    "hazra2026crase": (
        "arxiv", "2608.24809",
        "Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch",
        "derived_from_this_fetch",
    ),
    "knowplan2026": (
        "arxiv", "2608.06530",
        "KNOWPLAN: Knowledge-Driven AI Agents for Smart Degree Pathway Planning",
        "pre_existing_independent_claim",
    ),
    "donotstopearly2026": (
        "arxiv", "2604.24978",
        "Don't Stop Early: Scalable Enterprise Deep Research with Controlled Information Flow and Evidence-Aware Termination",
        "pre_existing_independent_claim",
    ),
    "confidencebasedstop2026": (
        "arxiv", "2606.15380",
        "Confidence-Based Stopping Methods for Systematic Reviews",
        "pre_existing_independent_claim",
    ),
    "icore2026": (
        "arxiv", "2607.27429",
        "Auditing Emergent LLM-Agent Collaboration through Cooperation-Obligation Coupling",
        "pre_existing_independent_claim",
    ),
    "scienceintent2026": (
        "arxiv", "2604.25000",
        "Toward a Science of Intent: Closure Gaps and Delegation Envelopes for Open-World AI Agents",
        "pre_existing_independent_claim",
    ),
    # Added by 73e9505 ("P2 V2: widen architecture and close external acquisition
    # campaign"), which cited it from main.tex and put it in both bib files but
    # registered no evidence record, turning main red. The title here is taken from
    # the fetch rather than claimed independently, so the record is provenance.
    "micp2026": (
        "arxiv", "2604.01413",
        "Adaptive Stopping for Multi-Turn LLM Reasoning",
        "derived_from_this_fetch",
    ),
    # Added by the 2026-08-17 narrowing audit into manuscript/recent_work.bib
    # and cited by main.tex, but with no evidence record until now. The titles
    # below are copied from that bib, not from the fetch, so each verdict is a
    # genuine independent comparison against what the audit claimed.
    "agentir2026": (
        "arxiv", "2603.04384",
        "AgentIR: Reasoning-Aware Retrieval for Deep Research Agents",
        "pre_existing_independent_claim",
    ),
    "deepcontrol2026": (
        "arxiv", "2602.01672",
        "Adaptive Information Control for Search-Augmented LLM Reasoning",
        "pre_existing_independent_claim",
    ),
    "rethinkinglitsearch2026": (
        "arxiv", "2605.29234",
        "Rethinking Literature Search Evaluation: Deep Research Helps, and Human "
        "Citation Lists Are Not a Ground Truth",
        "pre_existing_independent_claim",
    ),
    "halt2026": (
        "arxiv", "2608.02009",
        "HALT: Verification-Aware Stopping for Retrieval-Augmented Search Agents",
        "pre_existing_independent_claim",
    ),
    "sieve2026": (
        "arxiv", "2608.02751",
        "Search, Inspect, Fetch: Exploiting Structure-Aware Boolean Retrieval for "
        "Deep-Research Agents",
        "pre_existing_independent_claim",
    ),
    "decisionstop2026": (
        "arxiv", "2606.07071",
        "Decision-Theoretic Stopping Rules for Document Screening",
        "pre_existing_independent_claim",
    ),
    "multiragstop2026": (
        "arxiv", "2608.13237",
        "When Should Multi-Round RAG Stop? Structured Stopping Judgments and "
        "Retrieval Reduction in Search-R1",
        "pre_existing_independent_claim",
    ),
    "memchain2026": (
        "arxiv", "2607.24097",
        "MemChain: Learning Interpretable Memory Traces for Memory-Augmented LLM "
        "Agents",
        "pre_existing_independent_claim",
    ),
    "autoresearchbench2026": (
        "arxiv", "2604.25256",
        "AutoResearchBench: Benchmarking AI Agents on Complex Scientific Literature Discovery",
        "pre_existing_independent_claim",
    ),
    "sage2026": (
        "arxiv", "2602.05975",
        "SAGE: Benchmarking and Improving Retrieval for Deep Research Agents",
        "pre_existing_independent_claim",
    ),
    "metasyn2026": (
        "arxiv", "2606.17041",
        "Benchmarking LLM Agents on Meta-Analysis Articles from Nature Portfolio",
        "pre_existing_independent_claim",
    ),
    "agentslr2026": (
        "arxiv", "2603.22327",
        "AgentSLR: Automating Systematic Literature Reviews in Epidemiology with Agentic AI",
        "pre_existing_independent_claim",
    ),
    "physicsreview2026": (
        "arxiv", "2607.25672",
        "AI's Capability in Assisting Scientific Research in Physics, Astrophysics, "
        "and Cosmology I: Literature Review",
        "pre_existing_independent_claim",
    ),
    "researcharena2024": (
        "arxiv", "2406.10291",
        "ResearchArena: Benchmarking Large Language Models' Ability to Collect and "
        "Organize Information as Research Agents",
        "derived_from_this_fetch",
    ),
    "openscholar2024": (
        "arxiv", "2411.14199",
        "OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs",
        "derived_from_this_fetch",
    ),
    "cormack2015autonomycal": (
        "arxiv", "1504.06868",
        "Autonomy and Reliability of Continuous Active Learning for Technology-Assisted Review",
        "derived_from_this_fetch",
    ),
    "kastner2009capturerecapture": (
        "doi", "10.1016/j.jclinepi.2008.06.001",
        "The capture-mark-recapture technique can be used as a stopping rule when "
        "searching in systematic reviews",
        "derived_from_this_fetch",
    ),
    "spoor1996capturerecapture": (
        "doi", "10.1136/bmj.313.7053.342",
        "Use of the capture-recapture technique to evaluate the completeness of "
        "systematic literature searches",
        "derived_from_this_fetch",
    ),
    "rucker2011boosting": (
        "doi", "10.1016/j.jclinepi.2011.03.008",
        "Boosting qualifies capture-recapture methods for estimating the "
        "comprehensiveness of literature searches for systematic reviews",
        "derived_from_this_fetch",
    ),
    "callaghan2020stopping": (
        "doi", "10.1186/s13643-020-01521-4",
        "Statistical stopping criteria for automated screening in systematic reviews",
        "derived_from_this_fetch",
    ),
    "li2020whentostop": (
        "doi", "10.1145/3411755",
        "When to Stop Reviewing in Technology-Assisted Reviews",
        "derived_from_this_fetch",
    ),
    "yang2021heuristicstopping": (
        "doi", "10.1145/3469096.3469873",
        "Heuristic stopping rules for technology-assisted review",
        "derived_from_this_fetch",
    ),
    "cormack2014tarprotocols": (
        "doi", "10.1145/2600428.2609601",
        "Evaluation of machine-learning protocols for technology-assisted review in "
        "electronic discovery",
        "derived_from_this_fetch",
    ),
    "wallace2010semiautomated": (
        "doi", "10.1186/1471-2105-11-55",
        "Semi-automated screening of biomedical citations for systematic reviews",
        "derived_from_this_fetch",
    ),
    "vandeschoot2021asreview": (
        "doi", "10.1038/s42256-020-00287-7",
        "An open source machine learning framework for efficient and transparent "
        "systematic reviews",
        "derived_from_this_fetch",
    ),
    "carbonell1998mmr": (
        "doi", "10.1145/290941.291025",
        "The use of MMR, diversity-based reranking for reordering documents and "
        "producing summaries",
        "derived_from_this_fetch",
    ),
    "agrawal2009diversifying": (
        "doi", "10.1145/1498759.1498766",
        "Diversifying search results",
        "derived_from_this_fetch",
    ),
    "santos2015diversification": (
        "doi", "10.1561/1500000040",
        "Search Result Diversification",
        "derived_from_this_fetch",
    ),
    "shokouhi2011federated": (
        "doi", "10.1561/1500000010",
        "Federated Search",
        "derived_from_this_fetch",
    ),
    "pirolli1999foraging": (
        "doi", "10.1037/0033-295x.106.4.643",
        "Information foraging",
        "derived_from_this_fetch",
    ),
    "pirolli1995foragingchi": (
        "doi", "10.1145/223904.223911",
        "Information foraging in information access environments",
        "derived_from_this_fetch",
    ),
    # Added with the public-screening transport section in 6474c521. The
    # titles already existed in the bibliography before this closure pass, so
    # these live fetches are independent comparisons rather than provenance
    # transcriptions. Zenodo DOIs are registered with DataCite, not Crossref.
    "dhrangadhariya2023citationdataset": (
        "datacite", "10.5281/zenodo.10423427",
        "Dataset for Machine Learning Assisted Citation Screening for Systematic Reviews",
        "pre_existing_independent_claim",
    ),
    "howard2016swiftreview": (
        "doi", "10.1186/s13643-016-0263-z",
        "SWIFT-Review: a text-mining workbench for systematic review",
        "pre_existing_independent_claim",
    ),
    "voorhees2020treccovid": (
        "doi", "10.1145/3451964.3451965",
        "TREC-COVID",
        "pre_existing_independent_claim",
    ),
}


def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as resp:  # noqa: S310 (fixed hosts)
        return resp.read()


def _norm(text: str) -> str:
    """Lowercase alphanumeric-only form for tolerant title comparison."""
    return "".join(ch for ch in text.lower() if ch.isalnum())


def fetch_arxiv(arxiv_id: str) -> tuple[str, dict]:
    url = f"https://export.arxiv.org/api/query?id_list={urllib.parse.quote(arxiv_id)}"
    entry = ET.fromstring(_get(url)).find("a:entry", ATOM)
    if entry is None:
        raise RuntimeError(f"no arXiv entry for {arxiv_id}")

    def txt(tag: str) -> str:
        return " ".join((entry.findtext(tag, default="", namespaces=ATOM) or "").split())

    return url, {
        "fetched_title": txt("a:title"),
        "fetched_authors": [
            " ".join((a.findtext("a:name", default="", namespaces=ATOM) or "").split())
            for a in entry.findall("a:author", ATOM)
        ],
        "fetched_year": int(txt("a:published")[:4]) if txt("a:published") else None,
        "fetched_venue": txt("arxiv:journal_ref") or "arXiv preprint",
        "arxiv_id": txt("a:id").rsplit("/", 1)[-1],
        "doi": txt("arxiv:doi") or None,
        "published": txt("a:published"),
        "updated": txt("a:updated"),
        "abstract": txt("a:summary"),
    }


def fetch_doi(doi: str) -> tuple[str, dict]:
    url = f"https://api.crossref.org/works/{urllib.parse.quote(doi)}"
    msg = json.loads(_get(url))["message"]
    issued = msg.get("issued", {}).get("date-parts", [[None]])[0]
    return url, {
        "fetched_title": " ".join((msg.get("title") or [""])[0].split()),
        "fetched_authors": [
            f"{a.get('given', '')} {a.get('family', '')}".strip()
            for a in msg.get("author", [])
        ],
        "fetched_year": issued[0] if issued else None,
        "fetched_venue": (msg.get("container-title") or [""])[0],
        "arxiv_id": None,
        "doi": msg.get("DOI"),
        "volume": msg.get("volume"),
        "pages": msg.get("page"),
        "article_number": msg.get("article-number"),
        "publisher": msg.get("publisher"),
        "type": msg.get("type"),
    }


def fetch_datacite(doi: str) -> tuple[str, dict]:
    """Fetch DOI metadata from DataCite for repository-hosted research objects.

    Crossref returns 404 for Zenodo DOIs. Treating every DOI as a Crossref DOI
    would therefore turn an available primary-repository record into a false
    ``CANNOT_CHECK``. DataCite is the DOI registry named by the Zenodo record.
    """

    url = f"https://api.datacite.org/dois/{urllib.parse.quote(doi)}"
    attrs = json.loads(_get(url))["data"]["attributes"]
    titles = attrs.get("titles") or []
    issued = next(
        (item.get("date") for item in attrs.get("dates", []) if item.get("dateType") == "Issued"),
        None,
    )
    rights = attrs.get("rightsList") or []
    types = attrs.get("types") or {}
    return url, {
        "fetched_title": " ".join((titles[0].get("title", "") if titles else "").split()),
        "fetched_authors": [creator.get("name", "") for creator in attrs.get("creators", [])],
        "fetched_year": attrs.get("publicationYear"),
        "fetched_venue": attrs.get("publisher", ""),
        "arxiv_id": None,
        "doi": attrs.get("doi"),
        "publication_date": issued,
        "resource_type": types.get("resourceTypeGeneral") or types.get("resourceType"),
        "version": attrs.get("version"),
        "license": rights[0].get("rightsIdentifier") if rights else None,
        "landing_url": attrs.get("url"),
    }


def fetch_entry(kind: str, ident: str) -> tuple[str, dict]:
    """Dispatch a registered source kind without silently guessing."""

    if kind == "arxiv":
        return fetch_arxiv(ident)
    if kind == "doi":
        return fetch_doi(ident)
    if kind == "datacite":
        return fetch_datacite(ident)
    raise ValueError(f"unknown literature source kind: {kind}")


def main() -> None:
    """Fetch every key, or only the keys named on the command line.

    Existing records are content that later artifacts hash, so refetching all of
    them to add one rewrites bytes nothing asked to change. Passing keys keeps a
    top-up run scoped to the records that do not exist yet.
    """

    OUT.mkdir(parents=True, exist_ok=True)
    selected = [key for key in sys.argv[1:] if not key.startswith("-")]
    unknown = sorted(set(selected) - set(ENTRIES))
    if unknown:
        raise SystemExit(f"unknown bibliography keys: {unknown}")
    entries = {key: ENTRIES[key] for key in selected} if selected else dict(ENTRIES)
    report: list[str] = []
    for key, (kind, ident, claimed, provenance) in entries.items():
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        try:
            url, meta = fetch_entry(kind, ident)
        except Exception as exc:  # noqa: BLE001 - CANNOT_CHECK is a real outcome
            record = {
                "bib_key": key,
                "claimed_title": claimed,
                "claim_provenance": provenance,
                "fetch_url": (
                    f"https://export.arxiv.org/api/query?id_list={ident}"
                    if kind == "arxiv"
                    else (
                        f"https://api.datacite.org/dois/{ident}"
                        if kind == "datacite"
                        else f"https://api.crossref.org/works/{ident}"
                    )
                ),
                "fetched_utc": stamp,
                "verdict": "CANNOT_CHECK",
                "verdict_reason": f"fetch failed: {type(exc).__name__}: {exc}",
            }
            (OUT / f"{key}.json").write_text(
                json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            report.append(f"{key}\tCANNOT_CHECK\t{exc}")
            time.sleep(3)
            continue

        fetched = meta["fetched_title"]
        # Crossref appends float captions to some BMJ titles ("...: Table 1").
        fetched_core = fetched.split(":")[0] if fetched.lower().endswith(("table 1", "fig 1")) else fetched
        if _norm(claimed) == _norm(fetched):
            verdict, reason = "VERIFIED", "claimed title matches fetched title exactly (normalised)"
        elif _norm(claimed) in _norm(fetched) or _norm(fetched_core) in _norm(claimed):
            verdict, reason = "VERIFIED", "claimed title is a substring-equivalent of the fetched title (normalised)"
        else:
            verdict, reason = "MISMATCH", "claimed title differs from fetched title"

        record = {
            "bib_key": key,
            "claimed_title": claimed,
            "claim_provenance": provenance,
            "fetch_url": url,
            "fetched_utc": stamp,
            "verdict": verdict,
            "verdict_reason": reason,
            **meta,
        }
        (OUT / f"{key}.json").write_text(
            json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        report.append(f"{key}\t{verdict}\t{fetched[:70]}")
        time.sleep(3)

    # To stdout, not to one expired session's scratchpad directory. The previous
    # destination no longer exists, so every later run of this script ended in
    # FileNotFoundError after doing all of its network work.
    print("\n".join(report))


if __name__ == "__main__":
    main()
