# P5 C2 source-native core, rights and lineage successor V12

Start with `SCIENTIFIC_REPORT_V12.md`, `P5_C2_V12_RESULT.json`, and
`P5_C2_V12_SOURCE_LINEAGE_ROUTE_RECEIPT.json`.

V12 is a distinct non-aggregated source-core successor. It binds exactly two
V6-authorized fields on the C2 V4 basis; it does not inherit V11 runtime state
or modify released MOSS.

Execution-free reproduction order:

1. `python build_p5_c2_v12_packet.py --phase freeze`
2. `python p5_c2_v12_source_lineage_route.py`
3. `python build_p5_c2_v12_packet.py --phase finalize`
4. `python validate_p5_c2_v12_packet.py`
