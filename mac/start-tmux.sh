#!/usr/bin/env bash

set -euo pipefail

if [ -x /opt/homebrew/bin/tmux ]; then
    TMUX_BIN=/opt/homebrew/bin/tmux
elif [ -x /usr/local/bin/tmux ]; then
    TMUX_BIN=/usr/local/bin/tmux
elif command -v tmux >/dev/null 2>&1; then
    TMUX_BIN="$(command -v tmux)"
else
    echo "tmux is not installed." >&2
    exit 1
fi

if "$TMUX_BIN" has-session 2>/dev/null; then
    exit 0
fi

# Continuum restores the saved environment over this single bootstrap pane.
"$TMUX_BIN" new-session -d
