=== OpenClaw GitHub Monitor - 2026-05-18 ===

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
### v2026.5.16-beta.5 - openclaw 2026.5.16-beta.5
2026-05-17T17:59:02Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.16-beta.5

### v2026.5.16-beta.4 - openclaw 2026.5.16-beta.4
2026-05-17T04:22:04Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.16-beta.4

### v2026.5.16-beta.3 - openclaw 2026.5.16-beta.3
2026-05-16T19:46:18Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.16-beta.3

### v2026.5.16-beta.2 - openclaw 2026.5.16-beta.2
2026-05-16T11:29:05Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.16-beta.2

### v2026.5.16-beta.1 - openclaw 2026.5.16-beta.1
2026-05-16T01:33:32Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.16-beta.1


## Recent Merged PRs (Last 10)
### #83332 fix(cron): suppress source replies for announce delivery
Merged: 2026-05-18T00:41:17Z
https://github.com/openclaw/openclaw/pull/83332

### #83325 fix: seed control UI origins for bind aliases
Merged: 2026-05-18T00:21:33Z
https://github.com/openclaw/openclaw/pull/83325

### #83324 fix(cli): keep subcommand help lightweight
Merged: 2026-05-18T00:35:05Z
https://github.com/openclaw/openclaw/pull/83324

### #83321 fix: hide display-hidden chat transcript messages
Merged: 2026-05-18T00:04:48Z
https://github.com/openclaw/openclaw/pull/83321

### #83320 fix(telegram): bound isolated long-poll timeout
Merged: 2026-05-18T00:05:28Z
https://github.com/openclaw/openclaw/pull/83320

### #83318 fix(openai): allow available Codex OAuth models
Merged: 2026-05-18T00:04:15Z
https://github.com/openclaw/openclaw/pull/83318

### #83312 Keep legacy Codex OAuth sidecar profiles usable
Merged: 2026-05-17T23:41:07Z
https://github.com/openclaw/openclaw/pull/83312


*Generated at 2026-05-18 09:04:41*
