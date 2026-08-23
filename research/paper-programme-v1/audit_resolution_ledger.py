"""Audit the P1-P15 recursive resolution ledger against real git objects.

Exit codes: 0 = all references resolve; 2 = at least one defect; 3 = could not check.
A missing branch, a missing path, or a PR head that disagrees with the ledger is a defect.
"""
import json, re, subprocess, sys

REPO = "/Users/billy/Desktop/projects/ORION-claude"
PATH_RE = re.compile(r"(?:tests|scripts|papers|research|src)/[\w/.\-]+")


def run(args):
    return subprocess.run(args, cwd=REPO, capture_output=True, text=True)


def ref_exists(ref):
    return run(["git", "rev-parse", "--verify", "--quiet", f"origin/{ref}^{{commit}}"]).returncode == 0


def path_on_ref(ref, path):
    """True if path exists as blob or tree on origin/ref."""
    r = run(["git", "cat-file", "-e", f"origin/{ref}:{path}"])
    return r.returncode == 0


def audit(ledger_path):
    d = json.load(open(ledger_path))
    base = d["base_revision"]
    defects, checked = [], 0
    for p in d["papers"]:
        for it in p["items"]:
            iid = it["item_id"]
            refs = []
            epr = it.get("existing_pr") or {}
            if epr.get("head"):
                refs.append(("existing_pr.head", epr["head"]))
            for i, s in enumerate(it.get("source_refs", [])):
                if s.get("ref"):
                    refs.append((f"source_refs[{i}].ref", s["ref"]))
            live = []
            for field, ref in refs:
                checked += 1
                if ref_exists(ref):
                    live.append(ref)
                else:
                    defects.append((iid, "MISSING_BRANCH", f"{field}={ref}"))
            # source_ref paths
            for i, s in enumerate(it.get("source_refs", [])):
                path, avail = s.get("path"), s.get("availability")
                if not path:
                    continue
                checked += 1
                target = s.get("ref") if avail == "EXISTING_PR" else base
                if avail == "EXISTING_PR" and target not in live:
                    continue  # already reported as missing branch
                ok = (path_on_ref(target, path) if avail == "EXISTING_PR"
                      else run(["git", "cat-file", "-e", f"{base}:{path}"]).returncode == 0)
                if not ok:
                    defects.append((iid, "MISSING_SOURCE_PATH", f"{path} @ {target}"))
            # command paths
            cmds = []
            if epr.get("verification_command"):
                cmds.append(("existing_pr.verification_command", epr["verification_command"]))
            nes = it.get("next_executable_step") or {}
            if nes.get("command"):
                cmds.append(("next_executable_step.command", nes["command"]))
            for field, cmd in cmds:
                for tok in PATH_RE.findall(cmd):
                    checked += 1
                    targets = live + [base]
                    if not any(path_on_ref(t, tok) if t in live else
                               run(["git", "cat-file", "-e", f"{base}:{tok}"]).returncode == 0
                               for t in targets):
                        defects.append((iid, "MISSING_COMMAND_PATH", f"{field}: {tok} (tried {targets})"))
    return d, checked, defects


if __name__ == "__main__":
    try:
        d, checked, defects = audit(sys.argv[1])
    except Exception as exc:  # cannot-check is not the same as clean
        print(f"CANNOT_CHECK: {exc}")
        sys.exit(3)
    n_items = sum(len(p["items"]) for p in d["papers"])
    print(f"items={n_items} references_checked={checked} defects={len(defects)}")
    for iid, kind, detail in defects:
        print(f"  {kind:22s} {iid}: {detail}")
    sys.exit(2 if defects else 0)
