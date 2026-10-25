=== OpenClaw GitHub Monitor - 2026-05-17 ===

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
### v2026.5.16-beta.3 - openclaw 2026.5.16-beta.3
2026-05-16T19:46:18Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.16-beta.3

### v2026.5.16-beta.2 - openclaw 2026.5.16-beta.2
2026-05-16T11:29:05Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.16-beta.2

### v2026.5.16-beta.1 - openclaw 2026.5.16-beta.1
2026-05-16T01:33:32Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.16-beta.1

### v2026.5.14-beta.2 - openclaw 2026.5.14-beta.2
2026-05-15T11:11:27Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.14-beta.2

### v2026.5.14-beta.1 - openclaw 2026.5.14-beta.1
2026-05-14T21:31:13Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.14-beta.1


## Recent Merged PRs (Last 10)
### #82814 fix: reuse plugin manifest metadata safely
Merged: 2026-05-17T00:55:17Z
https://github.com/openclaw/openclaw/pull/82814

### #82808 fix(codex): keep native hook relay config final
Merged: 2026-05-17T00:49:57Z
https://github.com/openclaw/openclaw/pull/82808

### #82805 fix(codex): isolate app-server clients per runtime key
Merged: 2026-05-17T00:46:40Z
https://github.com/openclaw/openclaw/pull/82805

### #82801 Fix Discord reply context at LLM boundary
Merged: 2026-05-17T00:54:25Z
https://github.com/openclaw/openclaw/pull/82801

### #82799 Fix Windows image model event loop stalls
Merged: 2026-05-17T00:49:12Z
https://github.com/openclaw/openclaw/pull/82799

### #82798 Fix infer SecretRef resolution for provider-backed commands
Merged: 2026-05-17T00:55:40Z
https://github.com/openclaw/openclaw/pull/82798

### #82795 Improve macOS pairing approval prompt
Merged: 2026-05-17T00:13:00Z
https://github.com/openclaw/openclaw/pull/82795

### #82777 Remove OAuth sidecar credential runtime support
Merged: 2026-05-17T00:33:31Z
https://github.com/openclaw/openclaw/pull/82777


*Generated at 2026-05-17 09:03:09*
