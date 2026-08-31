# ORION-03 manuscript-surface finding dispositions

The conservative scanners intentionally flag contextual candidates. Each remaining item was inspected in both source and final PDF.

| Finding | Disposition |
|---|---|
| `F_R` resembles an upper-snake internal token | Retain. It is the typeset mathematical operator \(F_R\), not a repository status. |
| Bold theorem/proof lead-ins | Retain. They are conventional theorem structure in a mathematical article and render as scholarly emphasis, not chat prose. |
| Repeated spaces in YAML | Retain. They are required YAML block indentation and do not appear as repeated prose spacing in the PDF. |
| `AGM` abbreviation | Retain. It is expanded as Alchourrón–Gärdenfors–Makinson before the parenthetical abbreviation in the same sentence. |
| Tuple punctuation in inline mathematics | Scanner false positive. Commas delimit the mathematical tuple \(\mathcal{S}=(Q,\Lambda,\sigma,\mathcal{R})\); they are not prose punctuation requiring following spaces. |
| SHA-256 | Retain in Reproducibility. It names the standard cryptographic digest used to bind release bytes. |
| ORION and repository URL | Retain only in Data/Code Availability, where the public repository identity and access URL perform their designated function. |
| URL substring reported as a local path | Scanner false positive. The complete token is an HTTPS repository URL in the availability section. |

An exact source commit identifier was removed from the scientific narrative because the official source tag and tarball digest are sufficient there; exact source binding remains in the artifact record. No unresolved placeholder, doubled heading, raw project terminal, overfull box, clipped content or code-font scientific prose remains.

**Decision:** `PASS__CONTEXTUAL_FINDINGS_RESOLVED`.
