=== OpenClaw GitHub Monitor - 2026-05-21 ===

## Latest Release
v2026.5.19
openclaw 2026.5.19
## 2026.5.19

### Changes

- Agents: clarify that fixes should default to clean bounded refactors, lean internals, and explicit plugin SDK/API deprecation paths.
- Dependencies: update `@openclaw/proxyline` to 0.3.3.
- Dependencies: update Pi packages to 0.75.1 and raise the minimum supported Node.js 22 line to 22.19.
- Docker/Podman: add `OPENCLAW_IMAGE_APT_PACKAGES` as the runtime-neutral image build arg for extra apt packages while keeping `OPENCLAW_DOCKER_APT_PACKAGES` as a legacy fallback. (#62431) Thanks @urtabajev.
- Gateway/ACPX: attribute startup probe, config, runtime, and resource-count costs in restart traces without changing readiness behavior. (#83300) Thanks @samzong.
- Gateway: overlap startup logging and plugin-service startup with channel sidecars to reduce restart ready latency while preserving `/readyz` sidecar gating. (#83301) Thanks @samzong.
- Plugins/admin-http-rpc: allow trusted admin HTTP RPC clients to start and wait for web QR login flows. (#83259) Thanks @liorb-mountapps.
- Mac app: redesign Settings pages with consistent card layouts, cached navigation, cleaner permissions/voice/skills/cron/exec/debug panes, and steadier spacing around the native sidebar.
- Mac app: refine Voice & Talk recognition-language and wake-phrase settings so they use the same compact card rows as the rest of Settings.
- Skills: rename the repo-local Codex closeout review skill and helper to `autoreview` while preserving the Codex-first fallback behavior.
- Skills: add a meme-maker skill for curated template search, local SVG/PNG rendering, Imgflip hosted rendering, and Know Your Meme provenance links.
- Skills CLI: allow `openclaw skills install` and `openclaw skills update` to target shared managed skills with `--global`. (#74466) Thanks @Marvae.
- Browser: surface pending and recently handled modal dialogs in snapshots, return `blockedByDialog` when an action opens a modal, and allow `browser dialog --dialog-id` to answer pending dialogs.
- Browser CLI: add `openclaw browser evaluate --timeout-ms` so long-running page functions can extend both the evaluate action and request timeout budgets. (#83447) Thanks @eefreenyc.

## Recent Releases (Last 5)
### v2026.5.20-beta.1 - openclaw 2026.5.20-beta.1
2026-05-21T00:11:21Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.20-beta.1

### v2026.5.19 - openclaw 2026.5.19
2026-05-20T20:20:53Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.19

### v2026.5.19-beta.2 - openclaw 2026.5.19-beta.2
2026-05-19T21:12:37Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.19-beta.2

### v2026.5.19-alpha.1 - openclaw 2026.5.19-alpha.1
2026-05-20T00:50:52Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.19-alpha.1

### v2026.5.19-beta.1 - openclaw 2026.5.19-beta.1
2026-05-18T22:58:13Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.19-beta.1


## Recent Merged PRs (Last 10)
### #84863 fix(update): prune stale local bundled plugin shadows
Merged: 2026-05-21T07:49:20Z
https://github.com/openclaw/openclaw/pull/84863

### #84861 Fix Telegram isolated polling stall watchdog
Merged: 2026-05-21T07:19:10Z
https://github.com/openclaw/openclaw/pull/84861

### #84815 [Fix] Keep node systemd tokens out of unit files
Merged: 2026-05-21T06:48:16Z
https://github.com/openclaw/openclaw/pull/84815

### #84802 fix(memory-core): allow bounded dreaming session cleanup
Merged: 2026-05-21T04:45:19Z
https://github.com/openclaw/openclaw/pull/84802

### #84801 doctor: constrain legacy plugin cleanup paths [AI]
Merged: 2026-05-21T07:24:04Z
https://github.com/openclaw/openclaw/pull/84801


*Generated at 2026-05-21 15:51:37*
