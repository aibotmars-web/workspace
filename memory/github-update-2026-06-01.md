=== OpenClaw GitHub Monitor - 2026-06-01 ===

## Latest Release
v2026.5.28
openclaw 2026.5.28
### Highlights

- Agent and Codex runtime recovery is steadier: subagents keep cwd/workspace separation, hook context stays prompt-local, session locks release on timeout abort while live OpenClaw locks survive cleanup, stale restart continuations are avoided, and Codex app-server/helper failures no longer tear down shared runtime state. (#87218, #86875, #87409, #87399, #87375, #88129)
- Channel delivery and session identity got safer across outbound plugin hooks, Matrix room ids, iMessage reactions/approvals, Slack final replies, Discord recovered tool warnings, runtime-config message actions, WhatsApp profile auth roots, Telegram polling, and Microsoft Teams service URL trust checks. (#73706, #75670, #87366, #87451, #87334, #84535, #82492, #83304, #87160)
- Mobile and chat surfaces got a broader refresh: the iOS Pro UI, hosted push relay default, realtime Talk tab playback, Gateway chat transport, onboarding, Talk permissions, WebChat reconnect delivery, and session picker behavior now preserve more state across reconnects and empty searches. (#87367, #87531, #87682, #88096, #88105) Thanks @ngutman and @BunsDev.
- Browser, channel, and automation inputs are stricter: Browser tool timeouts, viewport/tab indices, Gateway ports, cron retry handling, Discord component ids, schema array refs, Telegram callback pages, and channel progress callbacks now reject malformed values earlier and preserve the intended delivery context. (#82887)
- Provider, media, and document coverage expands with Claude Opus 4.8, Fal Krea image schemas, NVIDIA featured models, MiniMax streaming music responses, encrypted PDF extraction, voice model catalogs, GitHub Copilot agent runtime support, and a Codex Supervisor plugin path for delegated Codex workflows. (#87845, #87890, #80775, #84764, #87751, #87794)
- CLI, auth, doctor, and provider paths fail faster and recover more clearly: malformed numeric/version options are rejected, workspace dotenv provider credentials are ignored, heartbeat defaults, OAuth/token lifetimes, and local service startup requests are bounded, agent auth health labels are clearer, legacy `api_key` auth profiles migrate to canonical form, and restart guidance is actionable. (#87398, #86281, #87361, #88133, #83655, #87559, #88088, #85924) Thanks @vincentkoc and @giodl73-repo.
- Plugin and Gateway hot paths do less repeated work while preserving cache correctness for install records, config JSON parsing, tool search catalogs, session stores, manifest model rows, auto-enabled plugin config, browser tokens, viewer assets, and release-split external plugin packages. (#86699)
- Release, QA, and E2E validation now bound more log, artifact, harness, and cross-OS waits so failing lanes produce proof instead of hanging or false-greening.

### Changes

- Status: show active subagent details in status output.
- Diffs: split the default language pack and expand default Diffs language coverage while keeping the host floor aligned. (#87370, #87372) Thanks @RomneyDa.
- ClawHub: add plugin display names plus skill verification and trust surfaces. (#87354, #86699) Thanks @thewilloftheshadow and @Patrick-Erichsen.
- iOS: refresh the dev app with Pro Command, Chat, Agents, Settings, hosted push relay defaults, and realtime Talk playback wired to gateway sessions, diagnostics, chat, and realtime Talk. (#87367, #88096, #88105) Thanks @Solvely-Colin and @ngutman.
- Docs: clarify Codex computer-use setup, paste-token stdin auth setup, macOS gateway sleep troubleshooting, native Codex hook relay recovery, container model auth, install deployment cards, device-token admin gating, CLI setup flow compatibility, Notte cloud browser CDP setup, and backport targets. (#87313, #63050, #87685) Thanks @bdjben, @liaoandi, and @thewilloftheshadow.

## Recent Releases (Last 5)
### v2026.5.31-beta.3 - openclaw 2026.5.31-beta.3
2026-05-31T19:19:39Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.31-beta.3

### v2026.5.31-beta.2 - openclaw 2026.5.31-beta.2
2026-05-31T18:17:21Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.31-beta.2

### v2026.5.31-beta.1 - openclaw 2026.5.31-beta.1
2026-05-31T17:44:50Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.31-beta.1

### v2026.5.30-beta.1 - openclaw 2026.5.30-beta.1
2026-05-31T02:39:53Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.30-beta.1

### v2026.5.28 - openclaw 2026.5.28
2026-05-30T20:06:10Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.28


## Recent Merged PRs (Last 10)
### #88827 Add Vertex API key model config regression coverage
Merged: 2026-06-01T00:51:51Z
https://github.com/openclaw/openclaw/pull/88827

### #88819 fix(workboard): wire task-backed board runs
Merged: 2026-06-01T00:41:22Z
https://github.com/openclaw/openclaw/pull/88819

### #88808 perf: hydrate chat history session metadata
Merged: 2026-05-31T22:31:15Z
https://github.com/openclaw/openclaw/pull/88808

### #88804 fix(agents): preserve stop-finished OpenAI tool calls
Merged: 2026-05-31T23:41:24Z
https://github.com/openclaw/openclaw/pull/88804

### #88802 test(agents): cover nonfatal trajectory flush timeout
Merged: 2026-06-01T00:01:12Z
https://github.com/openclaw/openclaw/pull/88802

### #88797 Migrate iMessage monitor state to SQLite
Merged: 2026-05-31T23:19:52Z
https://github.com/openclaw/openclaw/pull/88797


*Generated at 2026-06-01 09:00:11*
