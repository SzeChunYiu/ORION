# Retained negative: first global support-7 enumeration attempt — V1

Status: **execution/resource failure; no scientific conclusion**.

A first attempt to enumerate all normalized length-37, support-7 candidates in `F_7^3` used incremental short-zero-sum state but rebuilt too much state at each extension. It exceeded the available 45-second host execution budget before completing the declared cover.

This failure MUST NOT be read as evidence for or against `D_3(C_7^3)=36`, nor as evidence that support 7 is difficult in principle.

Diagnosis: the bottleneck was implementation/state-update cost, not a proved lower bound on search complexity. A successor should either (i) derive a stronger analytic restriction before enumeration, or (ii) use precomputed forbidden-next-vector tables / incremental translated sumsets / meet-in-the-middle forced-sum completion, with a separately generated branch cover.

Retained lesson: resource exhaustion is `CANNOT_CHECK_RESOURCE_BOUND`, never saturation or refutation.