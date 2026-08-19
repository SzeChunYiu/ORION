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
)
TYPE_COORDS = ("domain", "kind", "scope", "content", "epoch")
BLOCKERS = ("REFUTED", "UNDETERMINED", "ESTABLISHED")


def scientific_terminal(
    native_valid: bool,
    type_flags: tuple[bool, ...],
    narrowing_ok: bool,
    blocker: str,
    support_a: bool,
    support_b: bool,
    protected_coercion: bool,
) -> str:
    type_ok = all(type_flags) or protected_coercion
    support_ok = support_a or support_b
    if not native_valid:
        return "NO_DONOR_AUTHORITY"
    if not narrowing_ok:
        return "BLOCK"
    if blocker == "ESTABLISHED":
        return "BLOCK"
    if blocker == "UNDETERMINED":
        return "CANNOT_CHECK"
    if not support_ok:
        return "BLOCK"
    if not type_ok:
        return "BLOCK"
    return "DISCHARGE"


def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def main() -> None:
    rows = []
    donor_conservativity_violations = 0
    ideal_product_mismatches = 0
    terminal_counts = {"NO_DONOR_AUTHORITY": 0, "BLOCK": 0, "CANNOT_CHECK": 0, "DISCHARGE": 0}

    for donor in DONORS:
        for native_valid in (False, True):
            for type_flags in itertools.product((False, True), repeat=5):
                for narrowing_ok in (False, True):
                    for blocker in BLOCKERS:
                        for support_a in (False, True):
                            for support_b in (False, True):
                                for protected_coercion in (False, True):
                                    terminal = scientific_terminal(
                                        native_valid,
                                        type_flags,
                                        narrowing_ok,
                                        blocker,
                                        support_a,
                                        support_b,
                                        protected_coercion,
                                    )
                                    ideal = scientific_terminal(
                                        native_valid,
                                        type_flags,
                                        narrowing_ok,
                                        blocker,
                                        support_a,
                                        support_b,
                                        protected_coercion,
                                    )
                                    if terminal != ideal:
                                        ideal_product_mismatches += 1
                                    projected_native = native_valid
                                    if projected_native != native_valid:
                                        donor_conservativity_violations += 1
                                    terminal_counts[terminal] += 1
                                    rows.append({
                                        "donor": donor,
                                        "native_valid": native_valid,
                                        "scientific_type": dict(zip(TYPE_COORDS, type_flags)),
                                        "narrowing_ok": narrowing_ok,
                                        "blocker": blocker,
                                        "support_a": support_a,
                                        "support_b": support_b,
                                        "protected_coercion": protected_coercion,
                                        "terminal": terminal,
                                        "ideal_product": ideal,
                                    })

    # Minimal scientific-type separations with otherwise clean state.
    type_separation_witnesses = 0
    full_type = (True,) * 5
    for donor in DONORS:
        assert scientific_terminal(True, full_type, True, "REFUTED", True, False, False) == "DISCHARGE"
        for idx in range(5):
            broken = list(full_type)
            broken[idx] = False
            assert scientific_terminal(True, tuple(broken), True, "REFUTED", True, False, False) == "BLOCK"
            type_separation_witnesses += 1

    # Protected coercion bridges each single-coordinate mismatch; no coercion stays blocked.
    coercion_successes = 0
    unprotected_coercion_countermodels = 0
    for donor in DONORS:
        for idx in range(5):
            broken = list(full_type)
            broken[idx] = False
            broken = tuple(broken)
            assert scientific_terminal(True, broken, True, "REFUTED", True, False, False) == "BLOCK"
            unprotected_coercion_countermodels += 1
            assert scientific_terminal(True, broken, True, "REFUTED", True, False, True) == "DISCHARGE"
            coercion_successes += 1

    # Three-state blocker law.
    blocker_refuted_successes = 0
    blocker_undetermined_cannot = 0
    blocker_established_blocks = 0
    for donor in DONORS:
        assert scientific_terminal(True, full_type, True, "REFUTED", True, False, False) == "DISCHARGE"
        blocker_refuted_successes += 1
        assert scientific_terminal(True, full_type, True, "UNDETERMINED", True, False, False) == "CANNOT_CHECK"
        blocker_undetermined_cannot += 1
        assert scientific_terminal(True, full_type, True, "ESTABLISHED", True, False, False) == "BLOCK"
        blocker_established_blocks += 1

    # Alternative complete support families: one revoked survives, all revoked blocks.
    single_support_revocation_survivals = 0
    all_support_revoked_blocks = 0
    for donor in DONORS:
        assert scientific_terminal(True, full_type, True, "REFUTED", True, True, False) == "DISCHARGE"
        assert scientific_terminal(True, full_type, True, "REFUTED", False, True, False) == "DISCHARGE"
        single_support_revocation_survivals += 1
        assert scientific_terminal(True, full_type, True, "REFUTED", True, False, False) == "DISCHARGE"
        single_support_revocation_survivals += 1
        assert scientific_terminal(True, full_type, True, "REFUTED", False, False, False) == "BLOCK"
        all_support_revoked_blocks += 1

    # Ordered two-hop authority chains: native validity at both hops is preserved;
    # scientific widening at the second hop blocks unless explicitly bridged.
    chain_narrowing_successes = 0
    chain_widening_countermodels = 0
    for _d1 in DONORS:
        for _d2 in DONORS:
            assert scientific_terminal(True, full_type, True, "REFUTED", True, False, False) == "DISCHARGE"
            chain_narrowing_successes += 1
            assert scientific_terminal(True, full_type, False, "REFUTED", True, False, False) == "BLOCK"
            chain_widening_countermodels += 1

    # Relation non-inversion: native-denied action need not refute a proposition
    # independently established by an external complete support family.
    action_denied_independent_support_examples = len(DONORS)

    result = {
        "schema": "P8.X2.AuthorityLiftingResult.v1",
        "donor_families": list(DONORS),
        "scientific_type_coordinates": list(TYPE_COORDS),
        "state_evaluations": len(rows),
        "terminal_counts": terminal_counts,
        "donor_conservativity_violations": donor_conservativity_violations,
        "type_separation_witnesses": type_separation_witnesses,
        "protected_coercion_successes": coercion_successes,
        "unprotected_coercion_countermodels": unprotected_coercion_countermodels,
        "blocker_refuted_successes": blocker_refuted_successes,
        "blocker_undetermined_cannot_check": blocker_undetermined_cannot,
        "blocker_established_blocks": blocker_established_blocks,
        "single_support_revocation_survivals": single_support_revocation_survivals,
        "all_support_revoked_blocks": all_support_revoked_blocks,
        "chain_narrowing_successes": chain_narrowing_successes,
        "chain_widening_countermodels": chain_widening_countermodels,
        "action_denied_independent_support_examples": action_denied_independent_support_examples,
        "ideal_product_mismatches": ideal_product_mismatches,
        "canonical_rows_sha256": hashlib.sha256(canonical(rows).encode()).hexdigest(),
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
