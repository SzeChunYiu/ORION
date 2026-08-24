"""P9: relational vs invertible serialization, with the arms the box names.

D1 already carries the two serializations the question is about.

``TYPED_RELATIONAL``
    The typed comparison coordinates as explicit relations.

``TYPED_SERIALIZED_BAG``
    ``_serialize_typed`` writes the *same* payload as a canonical token
    sequence. The paper calls this the same-information control. This module
    does not take that on trust: :func:`round_trip_typed` parses the token
    sequence back and compares it to the payload it came from, on every
    instance, so "same information" is a checked property rather than a claim.

That distinction is the whole point. If the round trip holds, then any gap
between the two arms is not missing information. It is missing *accessibility*:
the learner cannot reach through the encoding to the structure. Separating
those two is P9's stated job.

The oracle is deliberately not given a serialization column. It reads the
method structure directly, so a cell recording "oracle under relational
serialization" would be reporting a number the oracle did not earn from that
encoding. Those cells carry :data:`ORACLE_SERIALIZATION_NA` instead.
"""

from __future__ import annotations

import hashlib
import re
from typing import Any, Mapping, Sequence

ORACLE_SERIALIZATION_NA = "ARM_DOES_NOT_CONSUME_A_SERIALIZATION"

RELATIONAL_ARM = "relational"
INVERTIBLE_ARM = "invertible"
LEARNERS = ("linear", "tree", "graph_kernel")
ORACLE = "exact_oracle"


# ---------------------------------------------------------------------------
# invertibility, checked rather than asserted
# ---------------------------------------------------------------------------
def parse_serialized(tokens: Sequence[str]) -> Any:
    """Reconstruct the payload that ``_serialize_typed`` was given.

    Recursive descent mirroring the writer, which is depth-first and emits
    mapping keys in sorted order, a ``:LEN=`` marker before every sequence and
    ``path=value`` for every scalar. Each element of a sequence therefore owns
    one contiguous block of tokens, so a cursor walk recovers the nesting --
    including sequences of sequences, which a flat path split cannot.
    """
    value, cursor = _parse(list(tokens), 0, "root")
    if cursor != len(tokens):
        raise ValueError(f"unconsumed tokens at {cursor}/{len(tokens)}")
    return value


def _key_after(token: str, prefix: str) -> str:
    rest = token[len(prefix) + 1 :]
    return re.split(r"[.\[:=]", rest, maxsplit=1)[0]


def _parse(tokens: list[str], i: int, path: str) -> tuple[Any, int]:
    if i >= len(tokens):
        raise ValueError("token stream ended early")
    tok = tokens[i]
    if tok.startswith(path + ":LEN="):
        n = int(tok[len(path) + 5 :])
        i += 1
        out: list[Any] = []
        for _ in range(n):
            child, i = _parse(tokens, i, path + "[]")
            out.append(child)
        return out, i
    if tok.startswith(path + "="):
        raw = tok[len(path) + 1 :]
        return (None if raw == "<NONE>" else raw), i + 1
    mapping: dict[str, Any] = {}
    while i < len(tokens) and tokens[i].startswith(path + "."):
        key = _key_after(tokens[i], path)
        mapping[key], i = _parse(tokens, i, f"{path}.{key}")
    if not mapping:
        raise ValueError(f"cannot parse token {tok!r} at path {path!r}")
    return mapping, i


def _normalise(value: Any) -> Any:
    """Compare structure and scalars-as-text; the writer is text-valued."""
    if isinstance(value, Mapping):
        return {k: _normalise(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_normalise(v) for v in value]
    if value is None:
        return None
    return str(value)


def round_trip_typed(payload: Mapping[str, Any], tokens: Sequence[str]) -> bool:
    """True when the token sequence carries exactly the payload's information."""
    try:
        return _normalise(parse_serialized(tokens)) == _normalise(payload)
    except Exception:  # a parse failure is a failed round trip, not a crash
        return False


# ---------------------------------------------------------------------------
# graph-kernel arm: Weisfeiler-Lehman over the method-comparison graph
# ---------------------------------------------------------------------------
def comparison_graph(payload: Mapping[str, Any]) -> tuple[list[str], list[tuple[int, int]]]:
    """Bipartite graph: the two methods, and the coordinate-value atoms.

    A value atom shared by both methods becomes a degree-2 node; an atom held
    by one becomes degree-1. Agreement and disagreement are therefore local
    degree facts, which is exactly what WL refinement can see.
    """
    labels: list[str] = ["METHOD_L", "METHOD_R"]
    edges: list[tuple[int, int]] = []
    index: dict[str, int] = {}
    for side, anchor in (("left", 0), ("right", 1)):
        block = payload.get(side)
        if not isinstance(block, Mapping):
            continue
        for coord, value in block.items():
            atoms = value if isinstance(value, list) else [value]
            for atom in atoms:
                key = f"{coord}={_flat(atom)}"
                if key not in index:
                    index[key] = len(labels)
                    labels.append(key)
                edges.append((anchor, index[key]))
    return labels, edges


def _flat(atom: Any) -> str:
    if isinstance(atom, (list, tuple)):
        return "|".join(str(x) for x in atom)
    return str(atom)


def wl_histogram(
    labels: Sequence[str], edges: Sequence[tuple[int, int]], *, rounds: int = 2, dim: int = 512
) -> dict[str, float]:
    """Hashed WL subtree histogram as a sparse feature dict."""
    n = len(labels)
    adj: dict[int, list[int]] = {i: [] for i in range(n)}
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    # The initial colour is the coordinate NAME only, never the value. A
    # held-out domain shares zero value atoms with train, so value-keyed
    # colours could not transfer and the arm would only memorise. The cost is
    # real and measured: this bounds the arm to agreement-as-degree, and on
    # transactional_workflows it collapses to a single predicted class rather
    # than decoding imperfectly. See the correction block in
    # P9_SERIALIZATION_FOUR_DOMAIN_V1.json.
    colour = {i: (labels[i].split("=", 1)[0] if i > 1 else labels[i]) for i in range(n)}
    hist: dict[str, float] = {}
    for r in range(rounds + 1):
        for i in range(n):
            h = hashlib.blake2b(f"{r}|{colour[i]}".encode(), digest_size=8).hexdigest()
            key = f"wl{int(h, 16) % dim}"
            hist[key] = hist.get(key, 0.0) + 1.0
        colour = {
            i: colour[i] + "<" + ",".join(sorted(colour[j] for j in adj[i])) for i in range(n)
        }
    return hist
