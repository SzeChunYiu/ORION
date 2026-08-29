"""SCHEMA_V1 encodings of the round-2 X.509 trust-store merge domain.

X.509 encoding convention
-------------------------
Licenses are the trust stores (origins). A store derives a leaf exactly when it
holds every certificate on some chain from that leaf to an anchor it trusts.
That is expressed directly:

  * the anchor claim is seeded with the stores that *trust* it;
  * each issuance link `issuer -> subject` is a rule capped by the stores that
    *hold* the subject certificate.

The capped transfer (cap intersect the body labels) therefore accumulates the
intersection of "stores trusting the anchor" with "stores holding each
certificate down the chain" -- precisely the set of stores whose independent
closure derives the leaf. This is the witness set W(x) of PROTOCOL_V2 section 3.

Scope limit, stated up front
----------------------------
This structural encoding models chain *derivability*. It does not model the
engine's policy layer (purpose/EKU/trust admission), which PROTOCOL_V2 section 9
leaves deliberately unmodeled. In the committed round-2 results, 45 of the 46
hybrids are recorded `structural_kind: "POLICY"` and only 1 is `"STRUCTURAL"`:
for the 45, at least one store *can* build the chain structurally and the engine
denies it on policy grounds. Those cases are representable here only by seeding
the engine's per-origin verdicts as oracle facts, which is what
`FU-0379-policy-oracle` does and labels as such.
"""

R2 = "papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore"


def _base(doc_id, title, note):
    return {
        "schema": "ORION.TypedMerge.Instance.v1",
        "id": f"x509-truststore/{doc_id}",
        "title": title,
        "provenance": {
            "domain": "X.509 trust-store merge",
            "upstream_material": "openssl/openssl @ openssl-3.6.4 test/certs (Apache-2.0)",
            "encoded_from": f"{R2}/ROUND2_RESULTS_V2.json and {R2}/TASK_MANIFEST_V2.json",
            "note": note,
        },
    }


def structural_first_mixing():
    """C6-HOSTILE-SPLIT: the one committed hybrid of structural_kind STRUCTURAL.

    Committed engine verdicts: vA=false, vB=false, vU=true, vI=false;
    M1_FLAT_UNION=true, M5_TYPED_WITNESS=false; first_mixing_link
    ["ca-cert","root-cert"], anchor_side_origin "A", leaf_side_held_by ["B"].
    Store A trusts the root; store B holds the intermediate; neither alone can
    build the chain and the textual union can.
    """
    doc = _base(
        "C6-HOSTILE-SPLIT",
        "Round 2 hostile control: structural first mixing across two trust stores",
        "Derived structurally from the committed chain and holdings; reproduces the "
        "committed M1/M5 decisions without invoking any engine.",
    )
    doc.update({
        "licenses": ["A", "B"],
        "claims": ["anchor:root-cert", "chain:ca-cert", "chain:ee-cert"],
        "seeds": {"anchor:root-cert": ["A"]},
        "rules": [
            {"id": "root-issues-ca", "body": ["anchor:root-cert"],
             "head": "chain:ca-cert", "cap": ["B"]},
            {"id": "ca-issues-ee", "body": ["chain:ca-cert"],
             "head": "chain:ee-cert", "cap": "ALL"},
        ],
        "refuted": [],
        "targets": ["chain:ee-cert"],
        "expect": {
            "typed_authorized": {"chain:ee-cert": False},
            "flat_authorized": {"chain:ee-cert": True},
            "first_mixing": {"chain:ee-cert": True},
            "typed_licenses": {"chain:ee-cert": []},
        },
    })
    doc["provenance"]["cap_rationale"] = (
        "root-issues-ca is capped to [B] because only store B holds ca-cert; "
        "ca-issues-ee is capped ALL because the leaf is supplied to the engine as "
        "the file argument rather than drawn from a store."
    )
    return doc


def single_origin_no_alarm():
    """No-alarm control: one store holds the whole chain, so nothing is flagged."""
    doc = _base(
        "single-origin-complete-no-alarm",
        "Round 2 no-alarm control: a complete single-origin chain must not be flagged",
        "Same shape as C6-HOSTILE-SPLIT except that store A holds the intermediate "
        "too. A detector that flagged this would be unusable, so the negative case "
        "is asserted explicitly rather than assumed.",
    )
    doc.update({
        "licenses": ["A", "B"],
        "claims": ["anchor:root-cert", "chain:ca-cert", "chain:ee-cert"],
        "seeds": {"anchor:root-cert": ["A"]},
        "rules": [
            {"id": "root-issues-ca", "body": ["anchor:root-cert"],
             "head": "chain:ca-cert", "cap": ["A", "B"]},
            {"id": "ca-issues-ee", "body": ["chain:ca-cert"],
             "head": "chain:ee-cert", "cap": "ALL"},
        ],
        "refuted": [],
        "targets": ["chain:ee-cert"],
        "expect": {
            "typed_authorized": {"chain:ee-cert": True},
            "flat_authorized": {"chain:ee-cert": True},
            "first_mixing": {"chain:ee-cert": False},
            "typed_licenses": {"chain:ee-cert": ["A"]},
        },
    })
    return doc


def retraction_non_resurrection():
    """C4 shape: retracting the intermediate withdraws exactly the dependent pairs.

    The committed round-2 C4 control records `resurrections: 0` and requires that
    parents, union, the operational cert-only flat merge and the intersection all
    deny once the retraction applies. This instance therefore does NOT diverge the
    flat view: retraction is honoured in both readings, and the evaluator must
    report no authorization and no first mixing after refutation.

    The `expect.retraction` block pins Theorem 5 exactly: refuting the intermediate
    withdraws the four claim-license pairs that depended on it and withdraws
    nothing else -- the anchor keeps both licenses, because it is still safely
    derivable. That is the minimality half of D-C6.
    """
    doc = _base(
        "C4-retraction-non-resurrection",
        "Round 2 retraction control: revoked intermediate withdraws exactly its dependents",
        "Exercises the retraction operator A_pre \\ A_post. Faithful to the committed "
        "C4 outcome, in which no method resurrects the revoked chain "
        "(resurrections: 0, upstream_mirrors_ok: true).",
    )
    doc.update({
        "licenses": ["A", "B"],
        "claims": ["anchor:root-cert", "chain:ca-cert", "chain:ee-cert"],
        "seeds": {"anchor:root-cert": ["A", "B"]},
        "rules": [
            {"id": "root-issues-ca", "body": ["anchor:root-cert"],
             "head": "chain:ca-cert", "cap": ["A", "B"]},
            {"id": "ca-issues-ee", "body": ["chain:ca-cert"],
             "head": "chain:ee-cert", "cap": "ALL"},
        ],
        "refuted": [],
        "targets": ["anchor:root-cert", "chain:ca-cert", "chain:ee-cert"],
        "expect": {
            "typed_authorized": {"chain:ee-cert": True, "anchor:root-cert": True},
            "flat_authorized": {"chain:ee-cert": True},
            "first_mixing": {"chain:ee-cert": False},
            "typed_licenses": {"chain:ee-cert": ["A", "B"]},
            "retraction": {
                "refute": ["chain:ca-cert"],
                "pairs": [
                    ["chain:ca-cert", "A"], ["chain:ca-cert", "B"],
                    ["chain:ee-cert", "A"], ["chain:ee-cert", "B"],
                ],
            },
        },
    })
    doc["provenance"]["committed_control"] = {
        "resurrections": 0,
        "upstream_mirrors_ok": True,
        "source": f"{R2}/ROUND2_RESULTS_V2.json retraction_control_C4",
    }
    return doc


def policy_oracle_hybrid():
    """FU-0379: a POLICY-kind hybrid, representable only by seeding engine verdicts.

    Committed manifest state: A trusts [ca-root2, root-cert, root2+clientAuth] and
    holds ca-cert; B trusts [root-cert2] and holds ca-cert. Structurally A alone
    can build ee-cert <- ca-cert <- root-cert, yet the engine denies both origins
    and authorizes the union, so the hybrid arises in the policy layer, not the
    issuance graph.
    """
    doc = _base(
        "FU-0379-policy-oracle",
        "Round 2 POLICY-kind hybrid consumed as an oracle fact",
        "This instance derives nothing. It records the engine's per-origin verdicts "
        "as seeds and shows what the calculus adds on top of them: the union "
        "authorization is not carried by any single origin. 45 of the 46 committed "
        "hybrids are of this kind, so the calculus's contribution on them is the "
        "typed combination rule, not chain derivation.",
    )
    doc.update({
        "licenses": ["A", "B"],
        "claims": ["engine-authorizes:ee-cert"],
        "seeds": {"engine-authorizes:ee-cert": []},
        "rules": [],
        "refuted": [],
        "flat_seeded_claims": ["engine-authorizes:ee-cert"],
        "targets": ["engine-authorizes:ee-cert"],
        "expect": {
            "typed_authorized": {"engine-authorizes:ee-cert": False},
            "flat_authorized": {"engine-authorizes:ee-cert": True},
            "first_mixing": {"engine-authorizes:ee-cert": True},
        },
    })
    doc["provenance"]["committed_verdicts"] = {
        "vA": False, "vB": False, "vU": True,
        "structural_kind": "POLICY",
        "source": f"{R2}/ROUND2_RESULTS_V2.json hybrid_tasks[FU-0379]",
    }
    return doc


def x509_instances():
    return [
        structural_first_mixing(),
        single_origin_no_alarm(),
        retraction_non_resurrection(),
        policy_oracle_hybrid(),
    ]
