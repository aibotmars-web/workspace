=== OpenClaw GitHub Monitor - 2026-06-05 ===

## Latest Release
v2026.6.1
openclaw 2026.6.1

### Highlights

- Agents and CLI-backed runtimes recover more cleanly from interrupted tool calls, stale session bindings, compaction handoffs, and media delivery retries. (#88129, #88136, #88141, #88162, #88182)
- Channels and mobile delivery are steadier across Telegram, WhatsApp, iMessage, Slack, Discord, Microsoft Teams, Google Chat, Google Meet, and iOS realtime Talk. (#88096, #88105, #88183, #88231)
- Provider and plugin requests now bound more timers, retries, OAuth/device-code lifetimes, media downloads, local service probes, and generated-content polling paths before they can hang a run.
- Skills, session metadata, gateway runtime state, plugin metadata, memory watchers, and store writes do less repeated work on hot paths while keeping config, dispatch, and Linux file-watch behavior stable. (#89185, #89188, #85351) Thanks @RomneyDa and @NianJiuZst.
- Skills and plugin loading now handle stale disabled snapshots and loader failures more clearly, so channel turns avoid disabled SecretRefs and operators get better recovery guidance. (#79072, #79173) Thanks @zeus1959.
- Workboard, SecretRef plugin manifests, hosted iOS push relay, and external Copilot/Tokenjuice packaging add broader orchestration, integration, and plugin delivery surfaces. (#82326, #87469, #87796, #88107, #88117)
- Skill Workshop now has a fuller Control UI flow with proposal lists, today actions, revision handoff, searchable file previews, review states, locale coverage, and reusable session routing.
- Chat and Control UI startup paths keep sends alive through history loading, stream deltas incrementally, skip markdown work while streaming, keep drafts local while typing, clear the composer after sends, trace first-output latency, prioritize first connect, and expose calmer composer controls. (#88772, #88825, #88998, #89030, #89106) Thanks @vincentkoc and @sallyom.
- Provider coverage and model metadata now include MiniMax M3, account OAuth endpoints, Google/Vertex catalog fixes, OpenRouter SQLite model caching, Copilot Claude 1M capabilities, Foundry reasoning alignment, and OpenAI response replay guards. (#88480, #88512, #88851, #88860)
- iMessage monitor state, inbound queues, and plugin install ledgers moved toward SQLite-backed state so restarts and local monitors recover with less duplicate filesystem scanning. (#88794, #88797)
- Release, CI, Docker, E2E, plugin install, and diagnostics lanes now cap more logs, response bodies, readiness probes, artifact checks, status polling, child workflow waits, docker package cleanup, quiet test stalls, and rollback snapshots so failures report bounded proof instead of stalling. (#88966) Thanks @RomneyDa.

### Changes

- Docs: add a dedicated Skill Workshop guide covering governed skill creation, reviewable proposals, CLI, Gateway, agent tool behavior, approval policy, support files, and recovery, and refresh the ClawHub showcase cards. (#88734) Thanks @shakkernerd and @vyctorbrzezowski.

## Recent Releases (Last 5)
### v2026.6.2-beta.1 - openclaw 2026.6.2-beta.1
2026-06-03T23:46:41Z
https://github.com/openclaw/openclaw/releases/tag/v2026.6.2-beta.1

### v2026.6.1 - openclaw 2026.6.1
2026-06-03T19:35:12Z
https://github.com/openclaw/openclaw/releases/tag/v2026.6.1

### v2026.6.1-beta.3 - openclaw 2026.6.1-beta.3
2026-06-03T09:16:02Z
https://github.com/openclaw/openclaw/releases/tag/v2026.6.1-beta.3

### v2026.6.1-beta.2 - openclaw 2026.6.1-beta.2
2026-06-01T21:56:19Z
https://github.com/openclaw/openclaw/releases/tag/v2026.6.1-beta.2

### v2026.6.1-beta.1 - openclaw 2026.6.1-beta.1
2026-06-01T09:45:05Z
https://github.com/openclaw/openclaw/releases/tag/v2026.6.1-beta.1


## Recent Merged PRs (Last 10)
### #90486 fix(whastapp): bound connection startup waits
Merged: 2026-06-05T00:45:43Z
https://github.com/openclaw/openclaw/pull/90486

### #90436 Add NVIDIA Nemotron 3 Ultra default
Merged: 2026-06-04T19:13:07Z
https://github.com/openclaw/openclaw/pull/90436


*Generated at 2026-06-05 09:00:21*
