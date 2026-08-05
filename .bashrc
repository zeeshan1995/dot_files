# shellcheck shell=bash

# Interactive Bash configuration for Linux and macOS.

case $- in
    *i*) ;;
    *) return ;;
esac

if [ -x /opt/homebrew/bin/brew ]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
elif [ -x /usr/local/bin/brew ]; then
    eval "$(/usr/local/bin/brew shellenv)"
fi

HISTCONTROL=ignoreboth:erasedups
HISTSIZE=50000
HISTFILESIZE=100000
shopt -s checkwinsize cmdhist histappend

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
        if command -v dircolors >/dev/null 2>&1; then
            if [ -r "$HOME/.dircolors" ]; then
                eval "$(dircolors -b "$HOME/.dircolors")"
            else
                eval "$(dircolors -b)"
            fi
            alias ls='ls --color=auto'
            alias grep='grep --color=auto'
            alias fgrep='fgrep --color=auto'
            alias egrep='egrep --color=auto'
        fi
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
    # shellcheck source=/dev/null
    . "$HOME/.shell_aliases"
fi

if [ -r "$HOME/.bash_aliases" ]; then
    # shellcheck source=/dev/null
    . "$HOME/.bash_aliases"
fi

if command -v brew >/dev/null 2>&1; then
    completion_file="$(brew --prefix)/etc/profile.d/bash_completion.sh"
    # shellcheck source=/dev/null
    [ -r "$completion_file" ] && . "$completion_file"

    fzf_shell_dir="$(brew --prefix)/opt/fzf/shell"
    # shellcheck source=/dev/null
    [ -r "$fzf_shell_dir/completion.bash" ] && . "$fzf_shell_dir/completion.bash"
    # shellcheck source=/dev/null
    [ -r "$fzf_shell_dir/key-bindings.bash" ] && . "$fzf_shell_dir/key-bindings.bash"
elif [ -r /usr/share/bash-completion/bash_completion ]; then
    # shellcheck source=/dev/null
    . /usr/share/bash-completion/bash_completion
elif [ -r /etc/bash_completion ]; then
    # shellcheck source=/dev/null
    . /etc/bash_completion
fi

command -v mise >/dev/null 2>&1 && eval "$(mise activate bash)"
if command -v zoxide >/dev/null 2>&1; then
    eval "$(zoxide init bash)"
    bind -r '"\e[0n"' 2>/dev/null || true
fi

if command -v starship >/dev/null 2>&1; then
    eval "$(starship init bash)"
else
    parse_git_branch() {
        git branch --show-current 2>/dev/null | sed 's/^/ (/; s/$/)/'
    }

    if command -v tput >/dev/null 2>&1 && tput setaf 1 >/dev/null 2>&1; then
        PS1='\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[01;90m\]$(parse_git_branch)\[\033[01;34m\]\n\$ \[\033[00m\]'
    else
        PS1='\u@\h:\w\$ '
    fi
fi

case "$TERM" in
    xterm* | rxvt* | screen* | tmux*)
        PS1="\[\e]0;\u@\h: \w\a\]$PS1"
        ;;
esac

unset completion_file fzf_shell_dir
