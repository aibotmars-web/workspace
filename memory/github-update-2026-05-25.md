=== OpenClaw GitHub Monitor - 2026-05-25 ===

## Latest Release
v2026.5.22
openclaw 2026.5.22
## 2026.5.22

### Changes

- Gateway/perf: reuse process-stable channel catalog reads, avoid repeated bundled-channel boundary checks, and rotate gateway watch CPU profiles so benchmark runs do not accumulate unbounded artifacts.
- Gateway/perf: reuse immutable plugin metadata snapshots across startup, config, model, channel, setup, and secret metadata readers so hot paths avoid repeated plugin file stats and manifest registry reloads.
- Gateway/perf: lazy-load startup-idle plugin work, core gateway method handlers, and the embedded ACPX runtime so Gateway health and ready signals no longer wait on unused handler trees or ACPX probes.
- Gateway/perf: cache plugin SDK public-surface alias maps and skip irrelevant macOS Linuxbrew PATH probes so Gateway startup avoids repeated filesystem walks and slow missing-directory stats.
- Meeting Notes: add a source-only external meeting-notes plugin and SDK source-provider contract outside the core npm package, with auto-start capture config, manual transcript imports, read-only `openclaw meeting-notes` CLI access, and Discord voice as the first live source.
- Docs/channels/config: add Signal `configPath`, Telegram wildcard topic defaults, local-time backup archive names, Termux home fallback, include-path validation, secret-scanner-safe placeholder guidance, Gemini CLI/Antigravity media guidance, and macOS VM auto-login guidance. Thanks @NorseGaud, @yudistiraashadi, @huangqian8, @VibhorGautam, @maweibin, @tianxingleo, @IgnacioPro, and @xzcxzcyy-claw.
- Docs: clarify model-usage portability, Codex migration prerequisites, status bootstrap wording, thread-bound subagent limits, hook ownership, and config-preserving safety guidance. Thanks @aniruddhaadak80, @leno23, @TomDjerry, @matthewxmurphy, @vincentkoc, and @stablegenius49.
- Docs: clarify README onboarding and Gateway startup paths, WhatsApp QR/408 recovery, cron output language prompts, skill advanced features, gateway upstream 403 troubleshooting, and plugin fallback override guidance. Thanks @deepujain, @Zacxxx, @Jah-yee, @neyric, @usimic, @Renu-Cybe, @BigUncle, and @SeashoreShi.
- Docs: clarify context-pruning ratio bounds, local dashboard recovery, CLI env markers, remote onboarding token behavior, and Peekaboo Bridge permissions for subprocess agents. Thanks @ayesha-aziz123, @dishraters, @hougangdev, and @brandonlipman.
- Docs: clarify browser CDP diagnostics, Plugin SDK allowlist imports, status-reaction timing defaults, queue steering behavior, limited-tool troubleshooting, cron HEARTBEAT handling, Telegram multi-agent groups, Bitwarden SecretRef setup, and EasyRunner deployments. Thanks @Quratulain-bilal, @mbelinky, @Mickey-, @vancece, @xenouzik, @posigit, @surlymochan, @janaka, and @choiking.
- Crabbox/Testbox: run clean sparse-checkout Testbox syncs from a temporary full checkout and route remote changed gates through Corepack pnpm.
- Docs: clarify IPv4-only Gateway BYOH binding, trusted-proxy scope clearing, Android pairing approval, macOS Accessibility grants, Zalo profile env vars, password-store SecretRef setup, and Chinese memory navigation. Thanks @itskai-dev, @gwh7078, @longstoryscott, @MoeJaberr, and @yuaiccc.
- Docs: consolidate GLM under Z.AI, add the Upstash Box install guide and Gateway exposure runbook, clarify MEDIA directives, Copilot and Voyage setup, config path quoting, real behavior proof, and memory-file write guidance. Thanks @BobDu, @alitariksahin, @Jefsky, @musaabhasan, @OmerZeyveli, @leno23, @WuKongAI-CMU, @luoyanglang, and @majin1102.
- Docs: clarify media provider credentials, Codex/OpenClaw code-mode boundaries, Slack and Telegram ack reactions, Feishu dynamic agents, secrets plaintext boundaries, memory guidance, and Chinese glossary terms. Thanks @nielskaspers, @cosmopolitan033, @drclaw-iq, @alexgduarte, @zccyman, @chengoak, and @cassthebandit.

## Recent Releases (Last 5)
### v2026.5.24-beta.2 - openclaw 2026.5.24-beta.2
2026-05-24T23:49:30Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.24-beta.2

### v2026.5.24-beta.1 - openclaw 2026.5.24-beta.1
2026-05-24T14:42:58Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.24-beta.1

### v2026.5.22 - openclaw 2026.5.22
2026-05-24T01:12:56Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.22

### v2026.5.22-beta.1 - openclaw 2026.5.22-beta.1
2026-05-23T09:59:56Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.22-beta.1

### v2026.5.20 - openclaw 2026.5.20
2026-05-21T20:44:50Z
https://github.com/openclaw/openclaw/releases/tag/v2026.5.20


## Recent Merged PRs (Last 10)
### #86197 docs: add ClawSweeper review policy to AGENTS
Merged: 2026-05-24T21:22:17Z
https://github.com/openclaw/openclaw/pull/86197


*Generated at 2026-05-25 09:02:27*
