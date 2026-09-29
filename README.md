# Dotfiles

Bash, zsh, Vim, tmux, clangd, and Git configuration for Linux and macOS.

## Install on Linux

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

## Linux reboot restoration

| Component | Saved state |
| --- | --- |
| tmux | Sessions, windows, pane layouts, scrollback and working directories; every minute while attached or detached, and again on a clean service shutdown |
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

## Diagnose on Linux

```bash
systemctl --user status tmux.service tmux-save.timer
systemctl --user list-timers tmux-save.timer
journalctl --user -u tmux.service -u tmux-save.service
loginctl show-user "$USER" -p Linger
```

Setup fails explicitly when prerequisites, downloads, plugin installation, or
user-service activation fail. A container without a systemd user manager cannot
provide this boot-restoration setup.

## Install on macOS

```sh
./mac/setup.sh
```

The macOS setup keeps the current login shell unchanged, backs up conflicting
files under `~/.dotfiles-backup`, and preserves the existing Vim, tmux, Bash,
and zsh key bindings.

On macOS, modern tools are installed under their own command names rather than
replacing standard commands:

- `bat`, `eza`, and `fd` for file inspection and search
- `ripgrep` and `fzf` for fast text and fuzzy search
- `zoxide` for directory navigation
- `starship` for the prompt
- `mise` for language/tool versions and per-project environments
- `uv` for Python projects
- `delta` for Git diffs
- `lazygit` for an optional full-screen Git workflow
- `gh` for pull requests, issues, Actions, and repository operations
- `yazi` for an optional terminal file manager
- `jq` and `yq` for structured data
- `just` for project commands
- `shellcheck` and `shfmt` for shell scripts

## macOS session persistence

The macOS setup keeps its separate `tmux-resurrect` and `tmux-continuum`
configuration:

- sessions, windows, panes, ordering, layouts, focus, and working directories
  are restored
- pane scrollback is captured
- Vim uses Obsession to continuously maintain private session files under
  `~/Library/Application Support/vim/sessions`, restoring open files, tabs,
  splits, folds, and the current directory
- safe interactive programs such as Vim, Copilot CLI, LazyGit, and Yazi are
  relaunched
- snapshots are written every five minutes and whenever the macOS setup runs
- a LaunchAgent starts tmux at login, which triggers automatic restoration

The macOS Vim session files are keyed by working directory, rather than by
individual editor instance. The Linux per-pane Copilot ID tracking and systemd
timer do not run on macOS; there, Copilot is relaunched with its saved command,
which only resumes a specific conversation if the command already selected one.

Project-local `Session.vim` files are globally ignored by Git for compatibility,
but the macOS setup does not create them. No new tmux or Vim key bindings are
added.

This is state reconstruction, not process checkpointing: arbitrary running
jobs, in-memory application state, unsaved Vim buffer contents, and network
connections cannot be resumed exactly after a reboot. Pane scrollback and Vim
swap/undo files provide recovery context, but important edits and job state
must still be saved by their applications.

Snapshots can contain terminal output and are stored locally in a
user-readable-only directory.

The macOS setup deliberately does not install or initialize:

- Atuin, because its default history bindings conflict with the existing fzf
  `Ctrl-R` binding
- Zellij, because it replaces tmux's key model
- Neovim, because obtaining its main benefits requires a separate editor
  migration rather than a safe Vim configuration update
- direnv, to avoid running a second environment manager alongside mise
- replacement aliases for `cat`, `ls`, or `cd`; `bat`, `eza`, and `zoxide`
  remain explicit commands

## Tests

```bash
python3 -m unittest discover -s tests -v
bash -n setup.sh mac/setup.sh mac/start-tmux.sh tmux/vim_dotfiles.sh
shellcheck setup.sh mac/setup.sh mac/start-tmux.sh tmux/vim_dotfiles.sh
```
