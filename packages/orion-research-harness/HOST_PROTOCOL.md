# Host protocol for ChatGPT / Claude / Codex sessions

When a session is asked to operate an ORION Research Harness workspace:

1. Open the repository and the workspace's `.orion-harness/session.json`.
2. Run or inspect `orion-harness pending <workspace>`.
3. Service **only** the requested capability. Never infer hidden capability output from benchmark labels.
4. Use real host tools:
   - `LLM_COMPLETE`: reason from the supplied system/user/schema.
   - `WEB_SEARCH`: search the current web; inspect sources; preserve URLs.
   - `VERIFY_EVIDENCE`: independently compare contribution to retrieved source; fail closed.
   - `GITHUB`: use repository/issue/PR/file APIs and return exact structured observations.
   - `PYTHON`, `SHELL`, `FILE_*`: prefer `orion-harness service-local` when the request is safely confined.
5. Ingest a JSON result with executor identity.
6. Rerun the ORION solve command.
7. Repeat until the solve is COMPLETE or canonical ORION returns BLOCKED/CANNOT_CHECK.

Never:
- invent a web result, source URI, certificate, file content or command output;
- turn an unavailable host tool into scientific evidence against ORION;
- bypass a native ORION authority/revision/saturation gate;
- rewrite historical negative results;
- weaken a preregistered comparator, margin or endpoint after seeing outcomes.

A host result is evidence/proposal input. It does not by itself grant scientific authority.
