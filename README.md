# dot_files

## Install on a new machine

Use Ubuntu 22.04+/Debian 12+ with systemd, an ordinary login user, sudo access,
and network access to GitHub and the distribution package repositories:

```bash
git clone https://github.com/zeeshan1995/dot_files.git
cd dot_files
./setup.sh
tmux attach
```

Run the script **as your user, not `sudo ./setup.sh`**. It works from any working
directory. `./setup.sh --skip-packages` reuses already-installed dependencies.
If an XDG `tmux/tmux.conf` exists, setup stops rather than silently installing a
second config that TPM might ignore; merge or move that config first.

Setup installs the distribution packages, copies the Bash/Vim/tmux configuration,
installs TPM, tmux-resurrect, tmux-continuum and the configured Vim plugins, and
installs the Copilot hooks. It enables the tmux user service, a one-minute save
timer, and systemd lingering so restoration starts at boot, even before login.
The first periodic save waits one minute to allow startup restoration to finish.

Re-running setup preserves existing plugin checkouts and unrelated Copilot hooks.
Changed destination files are backed up beneath `~/.local/state/dot_files/backups/`.
Running tmux sessions are not killed or restarted. If the existing server wasn't
started by systemd, systemd takes ownership on the next boot.

This does not purge packages, upgrade the whole OS, add PPAs, enable SSH,
install language servers/Node, or change Git credentials. Those previously
disabled setup choices remain disabled. Install Node separately if you use CoC.
Copilot CLI itself and its sign-in are separate prerequisites; its restore hooks
are installed even when the CLI is not yet present.

## Reboot restoration

| Component | Saved state |
| --- | --- |
| tmux | Sessions, windows, pane layouts and working directories; every minute while attached or detached, and again on a clean service shutdown |
| Copilot CLI | The foreground conversation ID for each pane; reopened with `copilot --resume <id>` |
| Vim | A private file per editor containing its files, tabs, splits and cursor positions; updated on buffer changes, every 30 seconds, and on normal exit |

Use the default tmux server and launch the applications **inside tmux**.
After reboot, run `tmux attach`. Existing Ctrl-a bindings are unchanged;
Ctrl-a then Ctrl-s saves manually, and Ctrl-a then Ctrl-r restores.

Restart already-running Vim/Copilot instances once after setup. Copilot uses its
session-start, prompt-submitted and session-end hooks to track the real active
conversation; it does not select the global "most recent" conversation.
An empty, never-used Copilot welcome screen has no conversation to recover.
Copilot installations must expose the native `copilot` executable and support
user hooks with `sessionId` and `cwd`.

Saved data stays outside this repository:

- tmux snapshots: `~/.local/share/tmux/resurrect/`
- Vim sessions: `~/.local/state/tmux/vim/`
- Copilot hooks: `${COPILOT_HOME:-~/.copilot}/hooks/tmux-app-restore.json`
- user services: `${XDG_CONFIG_HOME:-~/.config}/systemd/user/tmux*`

This is **state reconstruction, not process checkpointing**: running jobs,
in-memory state, unsaved Vim buffer contents, and in-flight Copilot work do not
survive a reboot. Save edits normally. Power loss can discard changes since the
last snapshot. Multiple independently named tmux servers are not supported by
this default-server setup.

## Diagnose

```bash
systemctl --user status tmux.service tmux-save.timer
systemctl --user list-timers tmux-save.timer
journalctl --user -u tmux.service -u tmux-save.service
loginctl show-user "$USER" -p Linger
```

Setup fails explicitly when prerequisites, downloads, plugin installation, or
user-service activation fail. A container without a systemd user manager cannot
provide this boot-restoration setup.

## Tests

```bash
python3 -m unittest discover -s tests -v
bash -n setup.sh
shellcheck setup.sh
```
