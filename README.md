# Dotfiles

Bash, zsh, Vim, tmux, clangd, and Git configuration for Linux and macOS.

## Install

The original Linux installer remains at the repository root:

```sh
./setup.sh
```

The modern macOS installer is separate:

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

## Session persistence

The macOS setup uses `tmux-resurrect` and `tmux-continuum`, the established
dynamic snapshot solution for tmux:

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

The setup deliberately does not install or initialize:

- Atuin, because its default history bindings conflict with the existing fzf
  `Ctrl-R` binding
- Zellij, because it replaces tmux's key model
- Neovim, because obtaining its main benefits requires a separate editor
  migration rather than a safe Vim configuration update
- direnv, because mise officially recommends not activating both environment
  managers together
- replacement aliases for `cat`, `ls`, or `cd`; `bat`, `eza`, and `zoxide`
  remain explicit commands
