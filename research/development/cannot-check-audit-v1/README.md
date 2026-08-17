# CANNOT_CHECK audit — does every refusal name what would resolve it?

**Asked because a reviewer should ask it.** `CANNOT_CHECK` earns its place only
while it is distinguishable from "I did not bother". A state that says
*unknowable* but means *unfinished* is worse than a wrong answer, because it
looks like rigour.

The rule it is audited against: **every CANNOT_CHECK must name what would
resolve it** — a credential, a bound corpus, an ablation, a second observer, a
larger N. One that cannot say what would resolve it is hiding something.

## Result

| | count |
|---|---|
| CANNOT_CHECK **decisions** (a return that sets the verdict) | 180 |
| carry a reason, literal or computed | **148 (82%)** |
| genuinely bare | **32** |

The 32 are listed in `bare_sites.txt` and are real debt. They are not
unknowables; they are refusals that forgot to say why.

## The first measurement was wrong, and how it was wrong matters

A regex pass over every line containing `CANNOT_CHECK` reported **31%**
compliance and named `authority_attacks.py` as the worst offender. That number
was a false alarm, and the audit was rebuilt before any of it was reported.

Sampling the "unexplained" sites showed most were not decisions at all:

- `CANNOT_CHECK = "CANNOT_CHECK"` — enum definitions
- prose in docstrings explaining the semantics
- `if verdict is CANNOT_CHECK:` — *reads* of a verdict, not grants of one
- returns whose reason was computed into a variable (`tuple(missing)`) rather
  than written as a literal, which the regex could not see

Counting mentions instead of decisions produced a number five times too harsh,
and it pointed at exactly the file that had been written most carefully. This is
the failure mode the repository has hit repeatedly this session — a checker that
is locally reasonable and globally measuring the wrong thing — and it is the
reason the standing rule is to validate a checker against real data before
reporting any of its findings. Had the 31% been reported, the response would have
been to "fix" files that were already correct.

The rebuilt audit parses the AST and counts only `return` statements that set a
CANNOT_CHECK verdict, then asks whether the same expression carries a reason.

## What the 82% establishes, and what it does not

It establishes that most refusals in this codebase say what they are waiting on.
It does not establish that the named resolvers are *achievable*, and that is the
next question rather than this one. Three kinds appear:

- **Definitional** — `wilson_interval requires n > 0`. Nothing resolves this
  because 0/0 has no value. Naming a resolver here would be dishonest.
- **Externally blocked** — `missing_credential_env_vars`. Resolvable by the
  operator in one command.
- **Resolvable only by fabricating** — `ground_truth_unbound` on the
  wide-literature task. Naming the papers it should find means inventing them.

Only the second is work anyone can do. The first two are correctly terminal, and
a design that pretended otherwise would be the overclaim this state exists to
prevent.

## Follow-up

The 32 bare sites should each either gain a reason or be shown to be one of the
definitional cases, where the absence of a resolver is itself the honest answer.
Queued rather than fixed in this pass, because changing 32 refusal paths across
eight modules while other lanes are writing in them is how the shared-checkout
collisions in this session started.
