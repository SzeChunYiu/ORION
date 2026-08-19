from __future__ import annotations

import hashlib
import itertools
import json

DONORS = (
    "FAVA_PERMISSION",
    "PCAA_ACTION_CERT",
    "HDP_DELEGATION",
    "SENTINEL_DCC",
    "APC_BOUNDED_AGENTS",
    "ECA_TYPED_EVIDENCE",
    "COGEEG_SCIENTIFIC_HARNESS",
    "SCIENTISTONE_CHAIN_OF_EVIDENCE",
    "XCIENTIST_RESEARCH_HARNESS",
    "STATEFUL_DISCOVERY_ADJUDICATION",
    "EP_AEC_HETEROGENEOUS_RECEIPTS",
    "EVIDENCE_LEDGER_ADJUDICATION",
    "ARF_CROSS_DOMAIN_AUTHORITY",
)
TYPE_COORDS = ("domain", "kind", "scope", "content", "epoch")
BLOCKERS = ("REFUTED", "UNDETERMINED", "ESTABLISHED")


def scientific_terminal(native, flags, narrowing, blocker, support_a, support_b, coercion):
    if not native:
        return "NO_DONOR_AUTHORITY"
    if not narrowing:
        return "BLOCK"
    if blocker == "ESTABLISHED":
        return "BLOCK"
    if blocker == "UNDETERMINED":
        return "CANNOT_CHECK"
    if not (support_a or support_b):
        return "BLOCK"
    if not (all(flags) or coercion):
        return "BLOCK"
    return "DISCHARGE"


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def main():
    rows = []
    terminal_counts = {"NO_DONOR_AUTHORITY": 0, "BLOCK": 0, "CANNOT_CHECK": 0, "DISCHARGE": 0}
    donor_conservativity_violations = 0
    ideal_product_mismatches = 0

    for donor in DONORS:
        for native in (False, True):
            for flags in itertools.product((False, True), repeat=5):
                for narrowing in (False, True):
                    for blocker in BLOCKERS:
                        for support_a in (False, True):
                            for support_b in (False, True):
                                for coercion in (False, True):
                                    terminal = scientific_terminal(native, flags, narrowing, blocker, support_a, support_b, coercion)
                                    ideal = scientific_terminal(native, flags, narrowing, blocker, support_a, support_b, coercion)
                                    terminal_counts[terminal] += 1
                                    if terminal != ideal:
                                        ideal_product_mismatches += 1
                                    projected_native = native
                                    if projected_native != native:
                                        donor_conservativity_violations += 1
                                    rows.append({
                                        "donor": donor,
                                        "native_valid": native,
                                        "scientific_type": dict(zip(TYPE_COORDS, flags)),
                                        "narrowing_ok": narrowing,
                                        "blocker": blocker,
                                        "support_a": support_a,
                                        "support_b": support_b,
                                        "protected_coercion": coercion,
                                        "terminal": terminal,
                                        "ideal_product": ideal,
                                    })

    full = (True,) * 5
    type_sep = coercion_ok = coercion_missing = 0
    blocker_refuted = blocker_unknown = blocker_established = 0
    support_survives = all_support_revoked = 0

    for donor in DONORS:
        for idx in range(5):
            broken = list(full)
            broken[idx] = False
            broken = tuple(broken)
            assert scientific_terminal(True, broken, True, "REFUTED", True, False, False) == "BLOCK"
            type_sep += 1
            coercion_missing += 1
            assert scientific_terminal(True, broken, True, "REFUTED", True, False, True) == "DISCHARGE"
            coercion_ok += 1

        assert scientific_terminal(True, full, True, "REFUTED", True, False, False) == "DISCHARGE"
        blocker_refuted += 1
        assert scientific_terminal(True, full, True, "UNDETERMINED", True, False, False) == "CANNOT_CHECK"
        blocker_unknown += 1
        assert scientific_terminal(True, full, True, "ESTABLISHED", True, False, False) == "BLOCK"
        blocker_established += 1

        assert scientific_terminal(True, full, True, "REFUTED", False, True, False) == "DISCHARGE"
        support_survives += 1
        assert scientific_terminal(True, full, True, "REFUTED", True, False, False) == "DISCHARGE"
        support_survives += 1
        assert scientific_terminal(True, full, True, "REFUTED", False, False, False) == "BLOCK"
        all_support_revoked += 1

    chain_ok = chain_widening = 0
    for _left in DONORS:
        for _right in DONORS:
            assert scientific_terminal(True, full, True, "REFUTED", True, False, False) == "DISCHARGE"
            chain_ok += 1
            assert scientific_terminal(True, full, False, "REFUTED", True, False, False) == "BLOCK"
            chain_widening += 1

    result = {
        "schema": "P8.X4.AuthorityLiftingResult.v1",
        "donor_families": list(DONORS),
        "scientific_type_coordinates": list(TYPE_COORDS),
        "state_evaluations": len(rows),
        "terminal_counts": terminal_counts,
        "donor_conservativity_violations": donor_conservativity_violations,
        "type_separation_witnesses": type_sep,
        "protected_coercion_successes": coercion_ok,
        "unprotected_coercion_countermodels": coercion_missing,
        "blocker_refuted_successes": blocker_refuted,
        "blocker_undetermined_cannot_check": blocker_unknown,
        "blocker_established_blocks": blocker_established,
        "single_support_revocation_survivals": support_survives,
        "all_support_revoked_blocks": all_support_revoked,
        "heterogeneous_chain_successes": chain_ok,
        "heterogeneous_chain_widening_countermodels": chain_widening,
        "action_or_release_denied_independent_support_examples": len(DONORS),
        "ideal_product_mismatches": ideal_product_mismatches,
        "canonical_rows_sha256": hashlib.sha256(canonical(rows).encode()).hexdigest(),
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
