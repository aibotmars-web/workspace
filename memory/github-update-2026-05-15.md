=== OpenClaw GitHub Monitor - 2026-05-15 ===

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
### v2026.5.14-beta.1 - openclaw 2026.5.14-beta.1
2026-05-14T21:31:13Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.14-beta.1

### v2026.5.12 - openclaw 2026.5.12
2026-05-14T18:28:04Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.12

### v2026.5.12-beta.8 - openclaw 2026.5.12-beta.8
2026-05-14T11:16:04Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.12-beta.8

### v2026.5.12-beta.7 - openclaw 2026.5.12-beta.7
2026-05-14T09:39:25Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.12-beta.7

### v2026.5.12-beta.6 - openclaw 2026.5.12-beta.6
2026-05-13T21:00:40Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.12-beta.6


## Recent Merged PRs (Last 10)
### #82059 refactor(auto-reply): centralize command turn context
Merged: 2026-05-15T07:41:10Z
https://github.com/openclaw/openclaw/pull/82059

### #82050 fix(control-ui): rotate service worker cache per build
Merged: 2026-05-15T06:59:30Z
https://github.com/openclaw/openclaw/pull/82050

### #82048 fix(macos): harden screen.snapshot validation and payload bounds
Merged: 2026-05-15T07:27:33Z
https://github.com/openclaw/openclaw/pull/82048

### #82042 fix(ci): unblock scheduled and publish checks
Merged: 2026-05-15T06:52:02Z
https://github.com/openclaw/openclaw/pull/82042

### #82036 feat(agents): support per-agent bootstrap profiles
Merged: 2026-05-15T07:42:22Z
https://github.com/openclaw/openclaw/pull/82036

### #82034 fix(ui): keep PWA chat controls above iOS home indicator
Merged: 2026-05-15T06:04:29Z
https://github.com/openclaw/openclaw/pull/82034

### #82033 refactor: centralize live provider drift policy
Merged: 2026-05-15T05:57:01Z
https://github.com/openclaw/openclaw/pull/82033

### #82030 Refactor shared channel status read model
Merged: 2026-05-15T05:39:19Z
https://github.com/openclaw/openclaw/pull/82030


*Generated at 2026-05-15 16:03:03*
