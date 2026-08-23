from __future__ import annotations
from dataclasses import dataclass
import re
from pathlib import Path

# Deliberately coarse action families.  This is an analysis projection, not a
# claim about Lean's grammar and not a replacement for kernel/elaborator traces.
TACTIC_FAMILIES = [
    ("rewrite", re.compile(r"\b(rw|nth_rewrite|simp_rw)\b")),
    ("simplify", re.compile(r"\b(simp|simpa|dsimp|norm_num)\b")),
    ("linear_arithmetic", re.compile(r"\b(linarith|nlinarith|omega)\b")),
    ("ring_normalize", re.compile(r"\b(ring|ring_nf)\b")),
    ("apply", re.compile(r"\b(apply|exact|refine|convert)\b")),
    ("introduce", re.compile(r"\b(intro|rintro|intros)\b")),
    ("cases", re.compile(r"\b(cases|rcases|by_cases|fin_cases)\b")),
    ("induction", re.compile(r"\b(induction|induction_on)\b")),
    ("constructor", re.compile(r"\b(constructor|left|right|use|exists)\b")),
    ("calculation", re.compile(r"\b(calc|have|haveI|show|suffices)\b")),
    ("extensionality", re.compile(r"\b(ext|funext)\b")),
    ("search", re.compile(r"\b(aesop|exact\?|apply\?|library_search|solve_by_elim)\b")),
    ("unfold", re.compile(r"\b(unfold|change)\b")),
    ("filter_reasoning", re.compile(r"\b(filter_upwards)\b")),
    ("logic_normalize", re.compile(r"\b(push|by_contra|exfalso|contradiction)\b")),
    ("congruence", re.compile(r"\b(gcongr|congr)\b")),
]

@dataclass(frozen=True)
class SourceTheorem:
    source_id: str
    theorem_name: str
    statement_head: str
    tactics: tuple[str, ...]
    raw_lines: tuple[str, ...]
    proof_start_line: int


def tactic_family(line: str) -> str | None:
    """Classify one candidate tactic line.

    `unknown` is intentionally a first-class return value.  Callers that mine
    source text may choose to *exclude* unknown lines rather than coercing them
    into a known family; raw source is retained so that a richer parser can
    revisit them later.
    """
    s=line.split("--",1)[0].strip()
    if not s:
        return None
    # Remove Lean bullet prefix before matching the actual command.
    s=re.sub(r"^[·*-]\s*", "", s)
    if not s:
        return None
    for name,pat in TACTIC_FAMILIES:
        if pat.search(s):
            return name
    # Equation/calc continuation lines are not independent tactic commands.
    if s.startswith(("_ =","_ ≤","_ <","_ ≥","_ >","_ ↔","_ →")):
        return None
    if s in {"by", "begin", "end"}:
        return None
    # Do not pretend an unrecognized command belongs to a known family.
    return "unknown"


DECL=re.compile(r"^\s*(?:theorem|lemma)\s+([A-Za-z0-9_'.]+)")
PROOF_START=re.compile(r"(?::=\s*by\s*$|\bby\s*$)")


def _proof_start(block: list[str]) -> int | None:
    """Return block-relative line containing the tactic-mode `by` opener."""
    for i,line in enumerate(block):
        code=line.split("--",1)[0].rstrip()
        if PROOF_START.search(code):
            return i
    return None


def _conservative_proof_end(block: list[str], proof_start: int, declaration_indent: int) -> int:
    """Stop when layout returns to the declaration level after ``by``.

    Lean tactic blocks are layout-sensitive. A proof command must be indented
    beyond its declaration; a later nonblank line at the declaration indent is
    therefore outside the projected proof. Stopping there is intentionally
    conservative: unusual formatting may lose actions, but later definitions,
    instances, namespace commands, and unrelated proofs cannot leak in.
    """
    for index in range(proof_start + 1, len(block)):
        line = block[index]
        code = line.split("--", 1)[0].rstrip()
        if not code.strip():
            continue
        indentation = len(line) - len(line.lstrip())
        if indentation <= declaration_indent:
            return index
    return len(block)


def parse_lean_source(text: str, source_id: str) -> list[SourceTheorem]:
    """Conservatively project tactic-style theorem source into action families.

    This parser is intentionally not a Lean parser.  It starts only *after* an
    explicit tactic-mode `by`, retains the whole raw theorem block, and drops
    unclassified lines from the mined sequence rather than fabricating a
    classification.  Kernel/elaborator traces remain the authority for future
    Phase-2/3 execution studies.
    """
    lines=text.splitlines(); starts=[]
    for i,l in enumerate(lines):
        m=DECL.match(l)
        if m:
            starts.append((i,m.group(1)))
    out=[]
    for j,(i,name) in enumerate(starts):
        e=starts[j+1][0] if j+1<len(starts) else len(lines)
        block=lines[i:e]
        ps=_proof_start(block)
        if ps is None:
            continue
        declaration_indent = len(lines[i]) - len(lines[i].lstrip())
        block = block[:_conservative_proof_end(block, ps, declaration_indent)]
        fam=[]
        for l in block[ps+1:]:
            f=tactic_family(l)
            # Unknown source lines are retained in raw_lines but are not
            # coerced into the learned vocabulary.
            if f in (None, "unknown"):
                continue
            if not fam or fam[-1]!=f:
                fam.append(f)
        if fam:
            out.append(SourceTheorem(
                source_id,name,block[0].strip(),tuple(fam),tuple(block),i+ps+1
            ))
    return out


def parse_paths(paths: list[Path]) -> list[SourceTheorem]:
    out=[]
    for p in paths:
        out.extend(parse_lean_source(p.read_text(encoding="utf-8"), str(p)))
    return out

# Exact-ish source command projection used only as a lower-level comparison for
# abstraction studies.  These are command heads, not semantic tactic IDs.
ACTION_HEADS = (
    'nth_rewrite','simp_rw','norm_num','nlinarith','linarith','omega','ring_nf','ring',
    'library_search','solve_by_elim','filter_upwards','by_contra','contradiction','exfalso',
    'haveI','suffices','rintro','intros','intro','by_cases','fin_cases','rcases','cases',
    'induction_on','induction','constructor','refine','convert','apply','exact','simpa','simp',
    'dsimp','rw','left','right','use','exists','calc','have','show','ext','funext','aesop',
    'unfold','change','push','gcongr','congr','obtain','choose'
)
_ACTION_HEAD_RE = re.compile(r'^(?:[·*-]\s*)?(' + '|'.join(re.escape(x) for x in ACTION_HEADS) + r')\b')


def tactic_action(line: str) -> str | None:
    """Return the observed tactic command head when confidently recognized."""
    s=line.split('--',1)[0].strip()
    if not s:
        return None
    m=_ACTION_HEAD_RE.match(s)
    return m.group(1) if m else None
