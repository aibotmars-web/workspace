=== OpenClaw GitHub Monitor - 2026-05-16 ===

## Latest Release
v2026.5.12
openclaw 2026.5.12
### Highlights

- Leaner installs: WhatsApp, Slack, Amazon Bedrock, Anthropic Vertex, and related provider/plugin dependency cones moved out of the core runtime so installs only pull what you use.
- Telegram got much more resilient: isolated polling, durable local spooling, safer group-media handling, and preserved HTML/Markdown formatting in streamed and scheduled replies.
- Codex/OpenAI paths are smoother: auth-profile-backed media tools, MCP server projection, context-engine thread rotation, and better app-server/runtime fallback behavior.
- Plugin installs and updates are harder to wedge, with pnpm 11 support, peer-dependency preservation, safer runtime scans, and source/git install fixes.
- Gateway, browser, Slack, node pairing, sandbox, and transcript paths picked up a broad security/provenance hardening pass.
- UI and reply delivery improved across Control UI, WebChat, TUI, rich-only replies, session history, and streaming auto-scroll.

### Changes

- Amazon Bedrock: externalize the Bedrock and Bedrock Mantle provider packages so core installs no longer pull AWS SDK dependencies unless those providers are installed.
- Plugins: externalize Slack, OpenShell sandbox, and Anthropic Vertex so their runtime dependency cones install only when those plugins are installed.
- Control UI/WebChat: add a persisted auto-scroll mode selector so users can keep the current near-bottom behavior, always follow streaming output, or turn automatic streaming scroll off and use the New messages button manually. Fixes #7648 and #81287. Thanks @BunsDev.
- ACP: add `acp.fallbacks` so ACP turns can try configured backup runtime backends when the primary backend is unavailable before any output is emitted. (#69542) Thanks @kaseonedge.

### Fixes


## Recent Releases (Last 5)
### v2026.5.16-beta.1 - openclaw 2026.5.16-beta.1
2026-05-16T01:33:32Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.16-beta.1

### v2026.5.14-beta.2 - openclaw 2026.5.14-beta.2
2026-05-15T11:11:27Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.14-beta.2

### v2026.5.14-beta.1 - openclaw 2026.5.14-beta.1
2026-05-14T21:31:13Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.14-beta.1

### v2026.5.12 - openclaw 2026.5.12
2026-05-14T18:28:04Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.12

### v2026.5.12-beta.8 - openclaw 2026.5.12-beta.8
2026-05-14T11:16:04Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.12-beta.8


## Recent Merged PRs (Last 10)
### #82425 fix: repair source-only official plugin installs
Merged: 2026-05-16T04:04:16Z
https://github.com/openclaw/openclaw/pull/82425

### #82391 fix(config): warn for stale web search providers
Merged: 2026-05-16T02:14:58Z
https://github.com/openclaw/openclaw/pull/82391

### #82378 Fix Codex raw tool-output watchdog
Merged: 2026-05-16T02:06:39Z
https://github.com/openclaw/openclaw/pull/82378

### #82376 Start configured web search providers at gateway startup
Merged: 2026-05-16T01:56:05Z
https://github.com/openclaw/openclaw/pull/82376

### #82369 Recover stale embedded tool calls during gateway diagnostics
Merged: 2026-05-16T00:37:00Z
https://github.com/openclaw/openclaw/pull/82369

### #82363 Fix session fallback provenance across reloads
Merged: 2026-05-16T00:12:35Z
https://github.com/openclaw/openclaw/pull/82363

### #82362 feat: add xAI Grok OAuth
Merged: 2026-05-16T02:02:08Z
https://github.com/openclaw/openclaw/pull/82362


*Generated at 2026-05-16 12:04:27*
