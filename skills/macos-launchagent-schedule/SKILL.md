---
name: "macos-launchagent-schedule"
description: "Schedule recurring shell scripts via macOS LaunchAgent when `crontab` hangs or exits SIGKILL. Writes the plist in Python and activates it with `launchctl load`."
---

Use when `crontab` invocations consistently exit with SIGKILL, hang without output, or block until exec timeout, but a recurring job must run on this macOS host.

Procedure:
1. Pick a reverse-DNS label (e.g., `com.openclaw.kb-crawl`).
2. Write a plist to `~/Library/LaunchAgents/<label>.plist` containing:
   - `Label` = the label string
   - `ProgramArguments` = array whose first element is `/bin/bash` and whose second element is the absolute script path
   - `StartCalendarInterval` = dict with integer `Hour` and `Minute` keys for the desired fire time
   - `StandardOutPath` and `StandardErrorPath` = absolute log file paths
   - `WorkingDirectory` = absolute working directory
3. `os.makedirs(os.path.expanduser("~/Library/LaunchAgents"), exist_ok=True)` before writing the file.
4. Activate with `subprocess.run(["launchctl", "load", plist_path], capture_output=True, text=True, timeout=10)`. rc=0 means success.
5. Verify with `subprocess.run(["launchctl", "list"], capture_output=True, text=True, timeout=10)`; the label must appear in the output (typically as `-	0	<label>`).
6. To remove: `launchctl unload <plist_path>` then `os.remove(plist_path)`.

Pitfalls (evidenced in this trajectory):
- Every `crontab` invocation exited with SIGKILL after timeout. Do not retry variants like `crontab -l | grep -v ... | crontab -`; switch to launchctl immediately.
- `/var/at/tabs/<user>`, `/var/spool/cron/tabs/<user>`, and `/usr/lib/cron/tabs/<user>` did not exist on this host, so editing the cron spool file directly is unreliable. Skip that approach.
- A wide `find /` search for the cron file or `qmd` binary will exceed the exec timeout and leave the command hanging. Keep locate steps narrow (specific dirs) or skip them.
- The deprecated cron entry left over after switching to LaunchAgent does no real harm because the deprecated script just `exit 0`s. Leaving the stale cron line in place is safer than fighting a broken `crontab` command.
- LaunchAgent runs as the current user, matching user-level cron semantics for log ownership and permissions.

Verification:
- After `launchctl load`, `launchctl list | grep <label>` shows the label with PID `-` and last-exit-status `0`.
- The plist file exists on disk at `~/Library/LaunchAgents/<label>.plist` and contains the expected `Label` and `ProgramArguments`.
- For immediate testing without waiting for the schedule, run `launchctl start <label>` and check that the `StandardOutPath` log file is created and written to.
