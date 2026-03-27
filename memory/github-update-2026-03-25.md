=== OpenClaw GitHub Monitor - 2026-03-25 ===

## Latest Release
v2026.3.23
2026.3.23
### Breaking

### Changes

- ModelStudio/Qwen: add standard (pay-as-you-go) DashScope endpoints for China and global Qwen API keys alongside the existing Coding Plan endpoints, and relabel the provider group to `Qwen (Alibaba Cloud Model Studio)`. (#43878)
- UI/clarity: consolidate button primitives (`btn--icon`, `btn--ghost`, `btn--xs`), refine the Knot theme to a black-and-red palette with WCAG 2.1 AA contrast, add config icons for Diagnostics/CLI/Secrets/ACP/MCP sections, replace the roundness slider with discrete stops, and improve accessibility with aria-labels across usage filters. (#53272) Thanks @BunsDev.
- CSP/Control UI: compute SHA-256 hashes for inline `<script>` blocks in the served `index.html` and include them in the `script-src` CSP directive, keeping inline scripts blocked by default while allowing explicitly hashed bootstrap code. (#53307) Thanks @BunsDev.

### Fixes

- Plugins/bundled runtimes: ship bundled plugin runtime sidecars like WhatsApp `light-runtime-api.js`, Matrix `runtime-api.js`, and other plugin runtime entry files in the npm package again, so global installs stop failing on missing bundled plugin runtime surfaces.
- CLI/channel auth: auto-select the single configured login-capable channel for `channels login`/`logout`, harden channel ids against prototype-chain and control-character abuse, and fall back cleanly to catalog-backed channel installs, so channel auth works again for single-channel setups and on-demand channel installs. (#53254) Thanks @BunsDev.
- Auth/OpenAI tokens: stop live gateway auth-profile writes from reverting freshly saved credentials back to stale in-memory values, and make `models auth paste-token` write to the resolved agent store, so Configure, Onboard, and token-paste flows stop snapping back to expired OpenAI tokens. Fixes #53207. Related to #45516.
- Control UI/auth: preserve operator scopes through the device-auth bypass path, ignore cached under-scoped operator tokens, and show a clear `operator.read` fallback message when a connection really lacks read scope, so operator sessions stop failing or blanking on read-backed pages. (#53110) Thanks @BunsDev.
- Plugins/ClawHub: resolve plugin API compatibility against the active runtime version at install time, and add regression coverage for current `>=2026.3.22` ClawHub package checks so installs no longer fail behind the stale `1.2.0` constant. (#53157) Thanks @futhgar.
- Plugins/uninstall: accept installed `clawhub:` specs and versionless ClawHub package names as uninstall targets, so `openclaw plugins uninstall clawhub:<package>` works again even when the recorded install was pinned to a version.
- Browser/Chrome MCP: wait for existing-session browser tabs to become usable after attach instead of treating the initial Chrome MCP handshake as ready, which reduces user-profile timeouts and repeated consent churn on macOS Chrome attach flows. Fixes #52930. Thanks @vincentkoc.
- Browser/CDP: reuse an already-running loopback browser after a short initial reachability miss instead of immediately falling back to relaunch detection, which fixes second-run browser start/open regressions on slower headless Linux setups. Fixes #53004. Thanks @vincentkoc.

## Recent Releases (Last 5)
### v2026.3.23 - 2026.3.23
2026-03-23T23:15:50Z
https://github.com/openclaw/openclaw/releases/tag/v2026.3.23

### v2026.3.22 - openclaw 2026.3.22
2026-03-23T11:11:22Z
https://github.com/openclaw/openclaw/releases/tag/v2026.3.22

### v2026.3.22-beta.1 - openclaw 2026.3.22-beta.1
2026-03-23T09:37:57Z
https://github.com/openclaw/openclaw/releases/tag/v2026.3.22-beta.1

### v2026.3.13-1 - openclaw 2026.3.13
2026-03-14T18:04:28Z
https://github.com/openclaw/openclaw/releases/tag/v2026.3.13-1

### v2026.3.13-beta.1 - openclaw 2026.3.13-beta.1
2026-03-14T05:17:09Z
https://github.com/openclaw/openclaw/releases/tag/v2026.3.13-beta.1


## Recent Merged PRs (Last 10)
### #54097 fix: require operator.admin for mutating internal /allowlist commands
Merged: 2026-03-25T00:05:59Z
https://github.com/openclaw/openclaw/pull/54097


*Generated at 2026-03-25 09:05:29*
