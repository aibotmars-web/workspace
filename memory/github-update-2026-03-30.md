=== OpenClaw GitHub Monitor - 2026-03-30 ===

## Latest Release
v2026.3.28
openclaw 2026.3.28

### Breaking

- Providers/Qwen: remove the deprecated `qwen-portal-auth` OAuth integration for `portal.qwen.ai`; migrate to Model Studio with `openclaw onboard --auth-choice modelstudio-api-key`. (#52709) Thanks @pomelo-nwu.
- Config/Doctor: drop automatic config migrations older than two months; very old legacy keys now fail validation instead of being rewritten on load or by `openclaw doctor`.

### Changes

- xAI/tools: move the bundled xAI provider to the Responses API, add first-class `x_search`, and auto-enable the xAI plugin from owned web-search and tool config so bundled Grok auth/configured search flows work without manual plugin toggles. (#56048) Thanks @huntharo.
- xAI/onboarding: let the bundled Grok web-search plugin offer optional `x_search` setup during `openclaw onboard` and `openclaw configure --section web`, including an x_search model picker with the shared xAI key.
- MiniMax: add image generation provider for `image-01` model, supporting generate and image-to-image editing with aspect ratio control. (#54487) Thanks @liyuan97.
- Plugins/hooks: add async `requireApproval` to `before_tool_call` hooks, letting plugins pause tool execution and prompt the user for approval via the exec approval overlay, Telegram buttons, Discord interactions, or the `/approve` command on any channel. The `/approve` command now handles both exec and plugin approvals with automatic fallback. (#55339) Thanks @vaclavbelak and @joshavant.
- ACP/channels: add current-conversation ACP binds for Discord, BlueBubbles, and iMessage so `/acp spawn codex --bind here` can turn the current chat into a Codex-backed workspace without creating a child thread, and document the distinction between chat surface, ACP session, and runtime workspace.
- OpenAI/apply_patch: enable `apply_patch` by default for OpenAI and OpenAI Codex models, and align its sandbox policy access with `write` permissions.
- Plugins/CLI backends: move bundled Claude CLI, Codex CLI, and Gemini CLI inference defaults onto the plugin surface, add bundled Gemini CLI backend support, and replace `gateway run --claude-cli-logs` with generic `--cli-backend-logs` while keeping the old flag as a compatibility alias.
- Plugins/startup: auto-load bundled provider and CLI-backend plugins from explicit config refs, so bundled Claude CLI, Codex CLI, and Gemini CLI message-provider setups no longer need manual `plugins.allow` entries.
- Podman: simplify the container setup around the current rootless user, install the launch helper under `~/.local/bin`, and document the host-CLI `openclaw --container <name> ...` workflow instead of a dedicated `openclaw` service user.
- Slack/tool actions: add an explicit `upload-file` Slack action that routes file uploads through the existing Slack upload transport, with optional filename/title/comment overrides for channels and DMs.

## Recent Releases (Last 5)
### v2026.3.28 - openclaw 2026.3.28
2026-03-29T01:34:30Z
https://github.com/openclaw/openclaw/releases/tag/v2026.3.28

### v2026.3.28-beta.1 - OpenClaw 2026.3.28-beta.1
2026-03-28T22:25:05Z
https://github.com/openclaw/openclaw/releases/tag/v2026.3.28-beta.1

### v2026.3.24 - openclaw 2026.3.24
2026-03-25T16:35:52Z
https://github.com/openclaw/openclaw/releases/tag/v2026.3.24

### v2026.3.24-beta.2 - openclaw 2026.3.24-beta.2
2026-03-25T14:11:48Z
https://github.com/openclaw/openclaw/releases/tag/v2026.3.24-beta.2

### v2026.3.24-beta.1 - openclaw 2026.3.24-beta.1
2026-03-25T11:54:55Z
https://github.com/openclaw/openclaw/releases/tag/v2026.3.24-beta.1


## Recent Merged PRs (Last 10)
### #57354 fix(memory): add QMD sync parity hooks
Merged: 2026-03-30T00:25:37Z
https://github.com/openclaw/openclaw/pull/57354

### #57351 fix(memory): support QMD --glob collection flag compatibility
Merged: 2026-03-30T00:30:49Z
https://github.com/openclaw/openclaw/pull/57351

### #57350 feat(status): surface task run pressure
Merged: 2026-03-30T00:09:10Z
https://github.com/openclaw/openclaw/pull/57350

### #57342 chore: remove xAI auth trace logging
Merged: 2026-03-30T00:29:51Z
https://github.com/openclaw/openclaw/pull/57342

### #57338 Control UI: clear queued connect timeout on stop
Merged: 2026-03-30T00:54:21Z
https://github.com/openclaw/openclaw/pull/57338

### #57324 refactor(tasks): unify the shared task run registry
Merged: 2026-03-29T23:28:17Z
https://github.com/openclaw/openclaw/pull/57324

### #57322 fix(cron): deliver full announce output instead of last chunk only
Merged: 2026-03-29T23:24:45Z
https://github.com/openclaw/openclaw/pull/57322

### #57316 [codex] Move internal development notes to maintainers
Merged: 2026-03-29T22:15:08Z
https://github.com/openclaw/openclaw/pull/57316

### #57315 fix: wire memorySearch.extraPaths to QMD indexing
Merged: 2026-03-29T23:58:42Z
https://github.com/openclaw/openclaw/pull/57315


*Generated at 2026-03-30 09:05:00*
