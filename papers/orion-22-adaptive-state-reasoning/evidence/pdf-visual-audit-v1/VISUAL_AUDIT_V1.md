# ORION-22 package binding + PDF visual audit V1

Discharges the #1701 box "Recover final package/source binding and visually
audit current PDF."

## 1. Package / source binding — intact

| check | result |
|---|---|
| `SHA256SUMS` verification (repo root) | **134 OK, 0 FAILED** |
| `CONTENT_MANIFEST_V1.json` bound files | **134 bound, 0 drifted** |
| `manuscript/main.pdf` covered by the binding | **yes** |

The PDF is not merely present, it is bound — a later silent rebuild would be
detected rather than absorbed.

## 2. Visual audit — pages 1-3 read directly

Read as rendered pages, not as extracted text, so layout and rendering defects
would be visible.

**No defects found.** Specifically checked and clear:

- **No placeholder or draft artefacts** — no `TODO`, `XXX`, `\ref{?}`, no
  unresolved citations or missing-figure boxes.
- **No internal-path or code leakage into reader-facing prose.** The
  fixed-width identifiers that do appear (`ADAPTIVE_STATE_ONLY`,
  `JOINT_STATE_REASONING`, `joint_gain(B)`, `c_i+r_i<=B`) are policy-class and
  notation names the paper defines, not repository paths or internal tooling.
- **Numbers carry their uncertainty.** The headline is stated as
  `0.253906` with a stratified family-block 95% interval
  `0.251221-0.256653` over 32 independent simulated family blocks, rather than
  as a bare point estimate.
- **Scope limits are in the abstract, not buried.** It states verbatim that
  these are *"bounded internal exact-domain results, not ScienceAgentBench,
  naturalistic-agent, forward-time-certificate, or external validation."*

## 3. What the audit found worth noting

Two things a referee would look for are present and prominent rather than
hidden:

**The withheld superiority claim is disclosed on page 2.** P12A's superiority
interpretation is withheld by its own comparison-validity adjudication
(`P12A_COMPARISON_VALIDITY_ADJUDICATION_V1.json`, active terminal
`P12A_SUPERIORITY_AUTHORITY_WITHHELD`), because signal count and permitted
allocations varied together. The paper then explains that the equal-action
successor P12B exists precisely to supply the controlled contract the withheld
result could not.

**The preregistered critical negative is carried in the abstract**: the
q-greedy rule's FLAT result replicates, *"but its price and distribution-shift
axes are both BROKEN."* A paper that puts its own broken axes in the abstract is
not laundering its result.

Donor subtraction is likewise explicit (§2.1 adaptive test-time compute and §2.2
dynamic state construction are both declared prior-owned, with §2.3 naming the
residual).

## Scope

Pages 1-3 of 1 PDF. This is a rendering//presentation audit and a binding check;
it verifies no scientific claim. `grants_authority: NONE`.

**Terminal:** `BINDING_INTACT_134_OF_134__PDF_VISUAL_AUDIT_CLEAN`
