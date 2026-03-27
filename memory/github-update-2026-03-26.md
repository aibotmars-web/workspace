=== OpenClaw GitHub Monitor - 2026-03-26 ===

## Latest Release
v2026.3.24
openclaw 2026.3.24
### Breaking

### Changes

- Gateway/OpenAI compatibility: add `/v1/models` and `/v1/embeddings`, and forward explicit model overrides through `/v1/chat/completions` and `/v1/responses` for broader client and RAG compatibility. Thanks @vincentkoc.
- Agents/tools: make `/tools` show the tools the current agent can actually use right now, add a compact default view with an optional detailed mode, and add a live "Available Right Now" section in the Control UI so it is easier to see what will work before you ask.
- Microsoft Teams: migrate to the official Teams SDK and add AI-agent UX best practices including streaming 1:1 replies, welcome cards with prompt starters, feedback/reflection, informative status updates, typing indicators, and native AI labeling. (#51808)
- Microsoft Teams: add message edit and delete support for sent messages, including in-thread fallbacks when no explicit target is provided. (#49925)
- Skills/install metadata: add one-click install recipes to bundled skills (coding-agent, gh-issues, openai-whisper-api, session-logs, tmux, trello, weather) so the CLI and Control UI can offer dependency installation when requirements are missing. (#53411) Thanks @BunsDev.
- Control UI/skills: add status-filter tabs (All / Ready / Needs Setup / Disabled) with counts, replace inline skill cards with a click-to-detail dialog showing requirements, toggle switch, install action, API key entry, source metadata, and homepage link. (#53411) Thanks @BunsDev.
- Slack/interactive replies: restore rich reply parity for direct deliveries, auto-render simple trailing `Options:` lines as buttons/selects, improve Slack interactive setup defaults, and isolate reply controls from plugin interactive handlers. (#53389) Thanks @vincentkoc.
- CLI/containers: add `--container` and `OPENCLAW_CONTAINER` to run `openclaw` commands inside a running Docker or Podman OpenClaw container. (#52651) Thanks @sallyom.
- Discord/auto threads: add optional `autoThreadName: "generated"` naming so new auto-created threads can be renamed asynchronously with concise LLM-generated titles while keeping the existing message-based naming as the default. (#43366) Thanks @davidguttman.
- Plugins/hooks: add `before_dispatch` with canonical inbound metadata and route handled replies through the normal final-delivery path, preserving TTS and routed delivery semantics. (#50444) Thanks @gfzhx.
- Control UI/agents: convert agent workspace file rows to expandable `<details>` with lazy-loaded inline markdown preview, and add comprehensive `.sidebar-markdown` styles for headings, lists, code blocks, tables, blockquotes, and details/summary elements. (#53411) Thanks @BunsDev.
- Control UI/markdown preview: restyle the agent workspace file preview dialog with a frosted backdrop, sized panel, and styled header, and integrate `@create-markdown/preview` v2 system theme for rich markdown rendering (headings, tables, code blocks, callouts, blockquotes) that auto-adapts to the app's light/dark design tokens. (#53411) Thanks @BunsDev.
- macOS app/config: replace horizontal pill-based subsection navigation with a collapsible tree sidebar using disclosure chevrons and indented subsection rows. (#53411) Thanks @BunsDev.
- CLI/skills: soften missing-requirements label from "missing" to "needs setup" and surface API key setup guidance (where to get a key, CLI save command, storage path) in `openclaw skills info` output. (#53411) Thanks @BunsDev.

## Recent Releases (Last 5)
### v2026.3.24 - openclaw 2026.3.24
2026-03-25T16:35:52Z
https://github.com/openclaw/openclaw/releases/tag/v2026.3.24

### v2026.3.24-beta.2 - openclaw 2026.3.24-beta.2
2026-03-25T14:11:48Z
https://github.com/openclaw/openclaw/releases/tag/v2026.3.24-beta.2

### v2026.3.24-beta.1 - openclaw 2026.3.24-beta.1
2026-03-25T11:54:55Z
https://github.com/openclaw/openclaw/releases/tag/v2026.3.24-beta.1

### v2026.3.23 - 2026.3.23
2026-03-23T23:15:50Z
https://github.com/openclaw/openclaw/releases/tag/v2026.3.23

### v2026.3.22 - openclaw 2026.3.22
2026-03-23T11:11:22Z
https://github.com/openclaw/openclaw/releases/tag/v2026.3.22


## Recent Merged PRs (Last 10)
### #54694 fix(gateway): block silent reconnect scope-upgrade escalation
Merged: 2026-03-25T23:54:14Z
https://github.com/openclaw/openclaw/pull/54694

### #54693 fix: enforce localRoots sandbox on Feishu docx upload file reads
Merged: 2026-03-25T22:09:00Z
https://github.com/openclaw/openclaw/pull/54693

### #54684 refactor(sandbox): remove tool policy facade
Merged: 2026-03-25T21:03:24Z
https://github.com/openclaw/openclaw/pull/54684

### #54679 fix: allow msteams feedback and welcome config keys
Merged: 2026-03-26T00:00:52Z
https://github.com/openclaw/openclaw/pull/54679


*Generated at 2026-03-26 09:02:53*
