=== OpenClaw GitHub Monitor - 2026-05-12 ===

## Latest Release
v2026.5.7
openclaw 2026.5.7

### Fixes

- Release/plugin publishing: retry transient ClawHub CLI dependency install failures, keep preview-passing plugins publishable when one preview cell flakes, and verify every expected ClawHub package version after publish so maintenance releases are faster to recover and less likely to hide partial plugin publishes.
- OpenAI: support `openai/chat-latest` as an explicit direct API-key model override for trying the moving ChatGPT Instant API alias without changing the stable default model.
- Cron CLI: include computed `status` in `cron list --json` and `cron show --json` output so external tooling can read disabled/running/ok/error/skipped/idle state without reimplementing cron status derivation. (#78701) Thanks @aweiker.
- Channels CLI: make `openclaw channels list` channel-only, add `--all` for bundled and catalog channels, render installed/configured/enabled state, and move model auth/usage details to `openclaw models auth list`, `openclaw status`, and `openclaw models list`. (#78456) Thanks @sliverp.
- Native commands: honor owner enforcement for native command handlers. (#78864) Thanks @pgondhi987.
- Active Memory: require admin scope for global memory toggles. (#78863) Thanks @pgondhi987.
- Gateway/sessions: clear cached skills snapshots during `/new` and `sessions.reset` so long-lived channel sessions rebuild the visible skill list after skills change. (#78873) Thanks @Evizero.
- Auto-reply: gate inline skill tool dispatch through before-tool-call authorization hooks. (#78517) Thanks @pgondhi987.
- Tavily: resolve dedicated `tavily_search` and `tavily_extract` tool credentials from the active runtime config snapshot, so `exec` SecretRef-backed API keys do not reach the tools unresolved. (#78610) Thanks @VACInc.
- Plugins/install: use the same absolute POSIX npm lifecycle shell for managed plugin install, rollback, repair, and uninstall npm operations as staged package updates, preventing restricted PATH shells from breaking cleanup. Thanks @vincentkoc.
- Agents/context engine: invalidate cached assembled context views when source history shrinks or assembly fails, preventing stale pre-reset history from being reused. Fixes #77968. (#78163) Thanks @brokemac79 and @ChrisBot2026.
- Discord/message: parse provider-prefixed targets like `discord:channel:<id>` as channel sends instead of legacy Discord DM targets, so cross-channel agent `message(action="send")` calls no longer misroute channel IDs into misleading `Unknown Channel` failures. Fixes #78572.
- Agents/compaction: clamp compaction summary reserve tokens to each model's output limit so high-context compaction no longer requests invalid `max_tokens` values. (#54392) Thanks @adzendo.
- Commands/BTW: show the `/btw` missing-question usage placeholder with brackets so outbound channel sanitization keeps it visible. Fixes #62877. Thanks @RajvardhanPatil07.
- Cron/doctor: repair persisted cron jobs whose `payload.model` was stored as `"default"`, `"null"`, blank, or JSON `null` by removing the bad override during `openclaw doctor --fix` while keeping cron runtime model validation strict. Fixes #78549. Thanks @bizzle12368239.

## Recent Releases (Last 5)
### v2026.5.10-beta.5 - openclaw 2026.5.10-beta.5
2026-05-11T16:38:39Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.10-beta.5

### v2026.5.10-beta.4 - openclaw 2026.5.10-beta.4
2026-05-11T16:04:13Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.10-beta.4

### v2026.5.10-beta.3 - openclaw 2026.5.10-beta.3
2026-05-11T03:28:30Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.10-beta.3

### v2026.5.10-beta.2 - openclaw 2026.5.10-beta.2
2026-05-10T18:18:58Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.10-beta.2

### v2026.5.10-beta.1 - openclaw 2026.5.10-beta.1
2026-05-10T14:02:46Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.10-beta.1


## Recent Merged PRs (Last 10)
### #80822 fix(onboarding): fix onboarding hangs instead of exiting
Merged: 2026-05-12T00:59:49Z
https://github.com/openclaw/openclaw/pull/80822

### #80816 fix(onboarding): treat already-installed codex as success, update in place
Merged: 2026-05-12T00:26:41Z
https://github.com/openclaw/openclaw/pull/80816

### #80803 test: stabilize core fast tests
Merged: 2026-05-11T23:40:52Z
https://github.com/openclaw/openclaw/pull/80803

### #80798 feat(onboarding): featured provider tier in interactive picker
Merged: 2026-05-12T00:09:33Z
https://github.com/openclaw/openclaw/pull/80798

### #80797 fix(cli/completion): re-apply shell-profile source-line guard (re-#78659)
Merged: 2026-05-11T23:01:00Z
https://github.com/openclaw/openclaw/pull/80797

### #80792 fix(codex): default plugin destructive actions on
Merged: 2026-05-11T23:50:15Z
https://github.com/openclaw/openclaw/pull/80792

### #80791 docs: add refactor docs skill
Merged: 2026-05-11T22:03:54Z
https://github.com/openclaw/openclaw/pull/80791

### #80790 Make OpenAI auth login use ChatGPT by default
Merged: 2026-05-11T23:17:14Z
https://github.com/openclaw/openclaw/pull/80790


*Generated at 2026-05-12 09:02:48*
