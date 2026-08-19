# P1 saturation — Round A strict reference audit

Date: 2026-08-19  
Method: `nature-ref-verifier` style multi-source check, using primary arXiv/publisher records for the entries below. This is the first tranche, not the complete bibliography audit.

## Confirmed critical metadata defects

| Bib key | Current manuscript metadata | Verified primary metadata | Severity | Action |
|---|---|---|---|---|
| `whowhenpro2026` | first author `Liu, Ziyi`; title `Who&When Pro: Advancing Failure Attribution in Multi-Agent Systems` | first author **Jiale Liu**; title **Who&When Pro: Can LLMs Really Attribute Failures in AI Agents?**; arXiv:2607.09996 | Critical | fix BibTeX |
| `reformulation2023` | first author `Alarnaouti, Lama`; title `Reformulation in Automated Planning: A Survey` | **Diaeddin Alarnaouti**, George Baryannis, Mauro Vallati; **Reformulation Techniques for Automated Planning: A Systematic Review**; KER 38 (2023) e9; related DOI `10.1017/S0269888923000097` | Critical | fix BibTeX and add journal/DOI |
| `evigraph2026` | title `EviGraph: Dependencies Make AI Scientist Better`; first author `Ren, Xuanyu` | title **EviGraph: Evidence-Guided Autonomous Research Agents**; first author **Zhenjiang Ren**; arXiv:2608.04738 | Critical | fix BibTeX |
| `agentrewind2026` | first author `Zhuang, Wenyu`; coauthors mismatch | **Yu Zhuang, Kefei Chen, Yitong Duan, Shuxin Zheng, Jian Li, Xu-Yao Zhang**; title **AgentRewind: Recoverable Execution for Long-Horizon LLM Agents**; arXiv:2608.14380 | Critical | fix BibTeX |
| `scienceflow2026` | first author `Zhao, Zhenguo` | **Mingming Zhao** et al.; title **ScienceFlow: A long-horizon agent for ML research, scientific discovery and beyond**; arXiv:2608.14354 | Critical | fix BibTeX |

## Missing normal citations found by claim audit

### Dependency-guided rollback

Primary record: Caili Yu, Yiqi Wang, Jiaqi Zhang, Yiqun Duan, Mingkai Zheng, Zhangkai Wu, Kaize Shi, Taotao Cai. **From Faulty Memories to Corrected Actions: Dependency-Guided Rollback Repair for Memory-Augmented Agents.** arXiv:2608.10502 (2026).

P1 already treats this mechanism as donor-owned substrate in the successor design, but related-work prose names it without a BibTeX key and the nearest-work table has no dedicated row. Add `dependencyrollback2026` and use it in the successor/related-work/table surfaces.

### HarnessFix

Primary record: Mengzhuo Chen, Junjie Wang, Zhe Liu, Yawen Wang, Haiming Zheng, Qing Wang. **From Failed Trajectories to Reliable LLM Agents: Diagnosing and Repairing Harness Flaws.** arXiv:2606.06324v2 (2026).

This is a close donor because it maps failure attribution to **scoped repair operators**. Add `harnessfix2026`; revise the P1.D2 sentence that currently says every neighboring system stops at a descriptive label.

### Scientific-reasoning negative pressure

Primary record: Martiño Ríos-García et al. **AI scientists produce results without reasoning scientifically.** arXiv:2604.18805 (2026).

This is useful as `CLAIM_BOUNDARY / MOTIVATION`, not as evidence for P1's mechanism or performance.

## Citation-support findings

### Parnas sentence

Current: K/W/M separation `follows Parnas's principle`.

Audit: Parnas supports information hiding/modular separation of change-prone design decisions. It does not derive P1's epistemic coordinates. Recommended wording: **`is engineered in the spirit of information hiding`** or equivalent. Citation role: `FORMAL/ENGINEERING_PRECEDENT`, support grade `ANALOGICAL`, not `DIRECT`.

### AGM sentence

Current: P1 K-revision semantics `are an instance of the AGM belief-revision framework`.

Audit: that wording implies formal satisfaction of AGM postulates. The current P1 manuscript does not establish that theorem. Recommended wording: **`borrows AGM's minimal-change/revision distinction`** unless a formal postulate proof is added. Citation role: `FORMAL_PRECEDENT`, support grade `PARTIAL`.

## Metadata sources used in this tranche

- arXiv:2607.09996, primary arXiv record;
- arXiv:2301.10079, primary arXiv record + KER journal reference;
- arXiv:2608.04738, primary arXiv record;
- arXiv:2608.14380, primary arXiv record;
- arXiv:2608.14354, primary arXiv record;
- arXiv:2606.06324, primary arXiv record;
- arXiv:2608.10502, primary arXiv record;
- arXiv:2604.18805, primary arXiv record.

## Round-A terminal

`REFERENCE_AUDIT_PARTIAL__CRITICAL_FIXES_REQUIRED`.

Do not mark #489's complete reference-verification box yet. The full bibliography still needs field-by-field verification.