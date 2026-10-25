=== OpenClaw GitHub Monitor - 2026-05-22 ===

## Latest Release
v2026.5.20
openclaw 2026.5.20

### Changes

- Exec approvals: remove the old `cat SKILL.md && printf ... && <skill-wrapper>` allowlist compatibility path so skill files must be loaded with the read tool and only the real skill executable is auto-allowed.
- Discord: let voice sessions follow configured Discord users into voice channels, with allowed-channel checks, multi-user handoff, bounded reconciliation, and DAVE recovery preservation. (#84264) Thanks @fuller-stack-dev.
- Discord/voice: include bounded `IDENTITY.md`, `USER.md`, and `SOUL.md` profile context in realtime voice session instructions by default, with `voice.realtime.bootstrapContextFiles: []` available to disable it. (#84499) Thanks @fuller-stack-dev.
- Dependencies: bump the bundled Codex harness to `@openai/codex` `0.132.0` and refresh the app-server model-list docs for the new catalog.
- CLI/policy: add the bundled Policy plugin for policy-backed channel conformance checks, doctor lint findings, and opt-in workspace repair. (#80407) Thanks @giodl73-repo.
- Agents/config: allow `agents.list[].experimental.localModelLean` so lean local-model mode can be enabled for one configured agent instead of globally.
- Providers/xAI: add device-code OAuth login so remote and headless setups can authorize xAI without a localhost browser callback. (#84005) Thanks @fuller-stack-dev.
- Providers/OpenRouter: honor provider-level `params.provider` routing policy for OpenRouter requests, with model and agent params overriding the defaults. Thanks @amknight.

### Fixes

- CLI/tasks: include stale-running task maintenance decisions in `openclaw tasks maintenance --json` so retained and reconcile candidates explain backing-session, cron, CLI, and wedged-subagent state. (#84691) Thanks @efpiva.
- Codex app-server: keep system-prompt reports working when bootstrap hooks provide workspace files with only a path and content, so hook-supplied SOUL/IDENTITY/TOOLS/USER context still reports injected characters correctly. (#84736) Thanks @JARVIS-Glasses.
- Providers/MiniMax music: stop advertising `durationSeconds` control and remove prompt-injected duration hints, so `music_generate` reports MiniMax duration as an unsupported override instead of suggesting MiniMax can enforce track length. Fixes #84508. Thanks @neeravmakwana.
- Doctor: warn when sandbox tool policy hides configured MCP server tools before provider requests. (#84699) Thanks @nxmxbbd.

## Recent Releases (Last 5)
### v2026.5.20 - openclaw 2026.5.20
2026-05-21T20:44:50Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.20

### v2026.5.20-beta.2 - openclaw 2026.5.20-beta.2
2026-05-21T15:57:15Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.20-beta.2

### v2026.5.20-beta.1 - openclaw 2026.5.20-beta.1
2026-05-21T00:11:21Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.20-beta.1

### v2026.5.19 - openclaw 2026.5.19
2026-05-20T20:20:53Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.19

### v2026.5.19-beta.2 - openclaw 2026.5.19-beta.2
2026-05-19T21:12:37Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.19-beta.2


## Recent Merged PRs (Last 10)
### #85143 fix(changelog): record provider setup trust fix
Merged: 2026-05-22T00:48:25Z
https://github.com/openclaw/openclaw/pull/85143

### #85142 perf: skip DTS for local launcher rebuilds
Merged: 2026-05-22T00:58:49Z
https://github.com/openclaw/openclaw/pull/85142

### #85137 Fix Matrix configured two-person room routing
Merged: 2026-05-22T00:40:18Z
https://github.com/openclaw/openclaw/pull/85137

### #85117 fix(codex): await computer use elicitation bridge
Merged: 2026-05-22T00:17:47Z
https://github.com/openclaw/openclaw/pull/85117

### #85107 Handle Codex turns missing completion
Merged: 2026-05-21T22:02:18Z
https://github.com/openclaw/openclaw/pull/85107

### #85100 Fix Discord session recovery abort ownership
Merged: 2026-05-21T21:34:19Z
https://github.com/openclaw/openclaw/pull/85100

### #85091 Fix Ollama cloud API key discovery
Merged: 2026-05-21T20:55:00Z
https://github.com/openclaw/openclaw/pull/85091

### #85074 fix(auth): load legacy Codex OAuth sidecars in embedded secrets-runtime loaders
Merged: 2026-05-21T20:07:50Z
https://github.com/openclaw/openclaw/pull/85074


*Generated at 2026-05-22 09:01:24*
