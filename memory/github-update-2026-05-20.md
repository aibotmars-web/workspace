=== OpenClaw GitHub Monitor - 2026-05-20 ===

## Latest Release
v2026.5.18
openclaw 2026.5.18

### Changes

- Agents: clarify that fixes should default to clean bounded refactors, lean internals, and explicit plugin SDK/API deprecation paths.
- Dependencies: update `@openclaw/proxyline` to 0.3.3.
- Dependencies: update Pi packages to 0.75.1 and raise the minimum supported Node.js 22 line to 22.19.
- Docker/Podman: add `OPENCLAW_IMAGE_APT_PACKAGES` as the runtime-neutral image build arg for extra apt packages while keeping `OPENCLAW_DOCKER_APT_PACKAGES` as a legacy fallback. (#62431) Thanks @urtabajev.
- Gateway/ACPX: attribute startup probe, config, runtime, and resource-count costs in restart traces without changing readiness behavior. (#83300) Thanks @samzong.
- Gateway: overlap startup logging and plugin-service startup with channel sidecars to reduce restart ready latency while preserving `/readyz` sidecar gating. (#83301) Thanks @samzong.
- Plugins/admin-http-rpc: allow trusted admin HTTP RPC clients to start and wait for web QR login flows. (#83259) Thanks @liorb-mountapps.
- Mac app: redesign Settings pages with consistent card layouts, cached navigation, cleaner permissions/voice/skills/cron/exec/debug panes, and steadier spacing around the native sidebar.
- Skills: rename the repo-local Codex closeout review skill and helper to `autoreview` while preserving the Codex-first fallback behavior.
- Skills: add a meme-maker skill for curated template search, local SVG/PNG rendering, Imgflip hosted rendering, and Know Your Meme provenance links.
- Browser: surface pending and recently handled modal dialogs in snapshots, return `blockedByDialog` when an action opens a modal, and allow `browser dialog --dialog-id` to answer pending dialogs.
- Agents/tools: shorten built-in tool descriptions and schema hints across media, messaging, sessions, cron, Gateway, web, image/PDF, TTS, nodes, and plan tools while preserving routing guardrails.
- Skills: add node inspector debugging, fused diagram generation, and throwaway spike workflow skills.
- CLI/plugins: add `defineToolPlugin` plus `openclaw plugins build`, `validate`, and `init` for typed simple tool plugins with generated manifest metadata, optional tool declarations, and context factories.
- Agents/skills: tighten bundled skill prompts and metadata, quote skill descriptions, refresh current CLI/API guidance, and update embedded sherpa-onnx runtime downloads.

## Recent Releases (Last 5)
### v2026.5.19-beta.2 - openclaw 2026.5.19-beta.2
2026-05-19T21:12:37Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.19-beta.2

### v2026.5.19-alpha.1 - openclaw 2026.5.19-alpha.1
2026-05-20T00:50:52Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.19-alpha.1

### v2026.5.19-beta.1 - openclaw 2026.5.19-beta.1
2026-05-18T22:58:13Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.19-beta.1

### v2026.5.18 - openclaw 2026.5.18
2026-05-18T18:54:22Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.18

### v2026.5.18-beta.1 - openclaw 2026.5.18-beta.1
2026-05-18T16:13:00Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.18-beta.1


## Recent Merged PRs (Last 10)
### #84482 fix(config): accept execApprovals.enabled="auto" in zod schema
Merged: 2026-05-20T07:16:42Z
https://github.com/openclaw/openclaw/pull/84482

### #84451 fix(cli): use active node for startup bench scripts
Merged: 2026-05-20T06:21:27Z
https://github.com/openclaw/openclaw/pull/84451

### #84442 Revert "fix: prompt Codex to send visible channel replies"
Merged: 2026-05-20T05:20:57Z
https://github.com/openclaw/openclaw/pull/84442

### #84437 fix(pi): keep message-tool delivery in session lock
Merged: 2026-05-20T05:20:04Z
https://github.com/openclaw/openclaw/pull/84437

### #84433 [AI-assisted] fix(cron): preserve legacy array stores
Merged: 2026-05-20T05:01:25Z
https://github.com/openclaw/openclaw/pull/84433

### #84420 docs(imessage): warn that cliPath wrappers must stream JSON-RPC stdio (#84330)
Merged: 2026-05-20T03:51:33Z
https://github.com/openclaw/openclaw/pull/84420


*Generated at 2026-05-20 16:02:19*
