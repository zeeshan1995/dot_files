# Keep zsh as the macOS login shell without changing its keymap.

if ! command -v brew >/dev/null 2>&1 && [ -r "$HOME/.zprofile" ]; then
    source "$HOME/.zprofile"
fi

HISTFILE="$HOME/.zsh_history"
HISTSIZE=50000
SAVEHIST=100000
setopt append_history hist_ignore_all_dups share_history

case "$(uname -s)" in
    Darwin)
        export STARSHIP_CONFIG="$HOME/Library/Application Support/starship/starship.toml"
        export MISE_CONFIG_DIR="$HOME/Library/Application Support/mise"
        export GH_CONFIG_DIR="$HOME/Library/Application Support/gh"
        alias ls='ls -G'
        alias alert='osascript -e '\''display notification "Command finished" with title "Terminal"'\'''
        ;;
    Linux)
        export STARSHIP_CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}/starship.toml"
        alias ls='ls --color=auto'
        alias alert='notify-send --urgency=low "Terminal" "Command finished"'
        ;;
esac

if command -v fd >/dev/null 2>&1; then
    export FZF_DEFAULT_COMMAND='fd --type f --hidden --follow --exclude .git'
    export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"
    export FZF_ALT_C_COMMAND='fd --type d --hidden --follow --exclude .git'
fi

if command -v bat >/dev/null 2>&1; then
    export MANPAGER="sh -c 'col -bx | bat -l man -p'"
fi

if [ -r "$HOME/.shell_aliases" ]; then
    source "$HOME/.shell_aliases"
fi

command -v mise >/dev/null 2>&1 && eval "$(mise activate zsh)"
if command -v zoxide >/dev/null 2>&1; then
    eval "$(zoxide init zsh)"
    bindkey -r '\e[0n'
fi
command -v starship >/dev/null 2>&1 && eval "$(starship init zsh)"
