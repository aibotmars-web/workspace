=== OpenClaw GitHub Monitor - 2026-05-28 ===

## Latest Release
v2026.5.26
openclaw 2026.5.26

### Highlights

- Faster Gateway and replies: startup avoids repeated plugin, channel, session, usage-cost, warning, scheduled-service, and filesystem scans; visible replies separate user-facing sends from slower follow-up work; Gateway runtime/session caches churn less under load.
- Transcripts are core: transcript-backed meeting summaries, source-provider chunks, cleaned user turns, media provenance, Codex mirrors, WebChat replies, and CLI/TUI replay now use one more reliable transcript path.
- More channels are production-ready: Telegram keeps typing/progress context and forum topics, iMessage handles attachment roots, remote media staging, and duplicate local Messages sources, WhatsApp restores group/media behavior, Discord improves voice playback and model picking, and Signal/iMessage/WhatsApp get reaction approvals.
- Better voice and Talk: realtime Talk runs can be inspected, steered, cancelled, or followed up from Web UI and Discord voice; wake-name handling is more tolerant without letting ambient speech trigger agents.
- Safer content boundaries: Browser snapshot reads honor SSRF policy, system-event text cannot spoof nested prompt markers, fetched file text is wrapped as external content, ClickClack inbound sender allowlists run before agent dispatch, stale device tokens are rejected, and serialized tool-call text is scrubbed from replies.
- Providers, Codex, and local models are steadier: named auth profiles, OpenAI sampling params, Codex app-server resume/timeout/usage-limit recovery, dynamic tool-schema guards, xAI usage-limit surfacing, Ollama top-p normalization, and local approval resolution reduce provider-specific dead ends.
- More reliable install/update/release paths: Alpine installs, trusted runtime fallback roots, stable update channels, Docker/package timeouts, Windows Scheduled Tasks, Windows/macOS proof lanes, Testbox/Crabbox delegation, plugin publish checks, and macOS runner bootstraps all got hardened.
- Better observability: Activity tab, gateway secret-prep traces, tool/model stream progress, explicit fast-mode status, systemd Gateway hygiene, OpenTelemetry LLM spans, release performance evidence, and richer telemetry signals make failures easier to inspect.

### Changes

- Transcripts: add core transcript capture and source-provider support for transcript-backed meeting summaries, including the renamed Transcripts docs, CLI surface, source-provider chunks, and cleaned user-turn persistence.
- Auth: add named model login profiles and supported credential migration for Hermes, OpenCode, and Codex auth profiles, with explicit opt-out and non-interactive controls. (#85667) Thanks @fuller-stack-dev.
- Diagnostics: trace gateway secret preparation, classify skill/tool usage, surface model stream progress, add OpenTelemetry LLM content spans, and expose alertable telemetry for blocked tools, failover, stale sessions, liveness, oversized payloads, and webhook ingress. (#83019, #80370, #86191)
- Channels: add Signal reaction approvals, iMessage thumb approval reactions, and WhatsApp thumb approval reaction support so mobile approval flows work without textual `/approve` commands. (#85894, #85952, #85477)

## Recent Releases (Last 5)
### v2026.5.26 - openclaw 2026.5.26
2026-05-27T11:27:24Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.26

### v2026.5.26-beta.2 - openclaw 2026.5.26-beta.2
2026-05-27T05:46:50Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.26-beta.2

### v2026.5.26-beta.1 - openclaw 2026.5.26-beta.1
2026-05-26T21:10:33Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.26-beta.1

### v2026.5.25-beta.1 - openclaw 2026.5.25-beta.1
2026-05-26T09:41:10Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.25-beta.1

### v2026.5.24-beta.2 - openclaw 2026.5.24-beta.2
2026-05-24T23:49:30Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.24-beta.2


## Recent Merged PRs (Last 10)
### #87465 fix(discord): fence tool warning fallback delivery
Merged: 2026-05-28T00:39:15Z
https://github.com/openclaw/openclaw/pull/87465

### #87454 test(discord): use reply payload SDK test helper
Merged: 2026-05-27T23:57:23Z
https://github.com/openclaw/openclaw/pull/87454

### #87452 fix(discord): backport recovered tool warning suppression
Merged: 2026-05-28T00:41:44Z
https://github.com/openclaw/openclaw/pull/87452

### #87451 fix(discord): suppress recovered tool warnings
Merged: 2026-05-27T23:32:29Z
https://github.com/openclaw/openclaw/pull/87451

### #87448 fix(imessage): backport native approval reactions to .27
Merged: 2026-05-27T23:42:09Z
https://github.com/openclaw/openclaw/pull/87448

### #87439 fix(agents): resolve Codex runtime models first
Merged: 2026-05-27T22:37:31Z
https://github.com/openclaw/openclaw/pull/87439

### #87435 fix(web-search): backport runtime-only provider config fix
Merged: 2026-05-27T22:19:49Z
https://github.com/openclaw/openclaw/pull/87435


*Generated at 2026-05-28 09:00:13*
