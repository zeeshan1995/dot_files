#!/usr/bin/env bash

set -euo pipefail

if [ "$(uname -s)" != "Darwin" ]; then
    echo "This installer only supports macOS." >&2
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOTFILES_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKUP_DIR="$HOME/.dotfiles-backup/$(date +%Y%m%d-%H%M%S)"

if command -v brew >/dev/null 2>&1; then
    BREW="$(command -v brew)"
elif [ -x /opt/homebrew/bin/brew ]; then
    BREW=/opt/homebrew/bin/brew
elif [ -x /usr/local/bin/brew ]; then
    BREW=/usr/local/bin/brew
else
    echo "Homebrew is required. Install it from https://brew.sh and rerun this script." >&2
    exit 1
fi

backup_and_link() {
    local source_path="$1"
    local target_path="$2"

    if [ -L "$target_path" ] && [ "$(readlink "$target_path")" = "$source_path" ]; then
        return
    fi

    if [ -e "$target_path" ] || [ -L "$target_path" ]; then
        mkdir -p "$BACKUP_DIR"
        mv "$target_path" "$BACKUP_DIR/"
    fi

    ln -s "$source_path" "$target_path"
}

packages=(
    bash
    bash-completion@2
    bat
    eza
    fd
    fzf
    gh
    git-delta
    jq
    just
    lazygit
    mise
    node
    ripgrep
    shellcheck
    shfmt
    starship
    tmux
    uv
    vim
    yq
    yazi
    zoxide
)
missing=()

for package in "${packages[@]}"; do
    "$BREW" list --formula "$package" >/dev/null 2>&1 || missing+=("$package")
done

if [ "${#missing[@]}" -gt 0 ]; then
    "$BREW" install "${missing[@]}"
fi

brew_prefix="$("$BREW" --prefix)"
export PATH="$brew_prefix/bin:$PATH"

clangd_target="$HOME/Library/Preferences/clangd"
starship_target="$HOME/Library/Application Support/starship/starship.toml"
vim_cache_dir="$HOME/Library/Caches/vim"
vim_session_dir="$HOME/Library/Application Support/vim/sessions"
tmux_resurrect_dir="$HOME/.local/share/tmux/resurrect"
launch_agent_label="com.zeeshan.dotfiles.tmux"
launch_agent="$HOME/Library/LaunchAgents/$launch_agent_label.plist"
launch_log_dir="$HOME/Library/Logs/dotfiles"

mkdir -p \
    "$(dirname "$clangd_target")" \
    "$(dirname "$starship_target")" \
    "$(dirname "$launch_agent")" \
    "$launch_log_dir" \
    "$HOME/.tmux/plugins" \
    "$tmux_resurrect_dir" \
    "$vim_session_dir" \
    "$vim_cache_dir/backup" \
    "$vim_cache_dir/swap" \
    "$vim_cache_dir/undo"

chmod 700 "$tmux_resurrect_dir" "$vim_session_dir"

backup_and_link "$DOTFILES_DIR/.bash_profile" "$HOME/.bash_profile"
backup_and_link "$DOTFILES_DIR/.bashrc" "$HOME/.bashrc"
backup_and_link "$DOTFILES_DIR/.gitignore_global" "$HOME/.gitignore_global"
backup_and_link "$DOTFILES_DIR/.shell_aliases" "$HOME/.shell_aliases"
backup_and_link "$DOTFILES_DIR/.tmux.conf" "$HOME/.tmux.conf"
backup_and_link "$DOTFILES_DIR/.vim" "$HOME/.vim"
backup_and_link "$DOTFILES_DIR/.vimrc" "$HOME/.vimrc"
backup_and_link "$DOTFILES_DIR/.zprofile" "$HOME/.zprofile"
backup_and_link "$DOTFILES_DIR/.zshrc" "$HOME/.zshrc"
backup_and_link "$DOTFILES_DIR/clangd" "$clangd_target"
backup_and_link "$DOTFILES_DIR/starship.toml" "$starship_target"

if ! git config --global --get-all include.path 2>/dev/null | grep -Fxq "$DOTFILES_DIR/.gitconfig"; then
    git config --global --add include.path "$DOTFILES_DIR/.gitconfig"
fi

if [ ! -d "$HOME/.tmux/plugins/tpm/.git" ]; then
    git clone https://github.com/tmux-plugins/tpm "$HOME/.tmux/plugins/tpm"
fi

if [ -d "$HOME/.vim/plugged/nerdtree/.git" ]; then
    git -C "$HOME/.vim/plugged/nerdtree" remote set-url origin https://github.com/preservim/nerdtree.git
fi

vim -Nu "$HOME/.vimrc" -n --not-a-term +'set nomore' +'silent! PlugInstall --sync' +qall </dev/null >/dev/null 2>&1

vim_plugins=(
    coc.nvim
    editorconfig-vim
    fzf
    fzf.vim
    jedi-vim
    lightline.vim
    molokai
    nerdtree
    targets.vim
    undotree
    vim-fugitive
    vim-gitgutter
    vim-obsession
    vim-sensible
    vim-sneak
    vim-unimpaired
    vim-visual-multi
)

for plugin in "${vim_plugins[@]}"; do
    if [ ! -d "$HOME/.vim/plugged/$plugin/.git" ]; then
        echo "Vim plugin installation failed: $plugin is missing." >&2
        exit 1
    fi
done

tmux start-server \; set-environment -g TMUX_PLUGIN_MANAGER_PATH "$HOME/.tmux/plugins"
"$HOME/.tmux/plugins/tpm/bin/install_plugins"

backup_and_link \
    "$DOTFILES_DIR/tmux/vim_dotfiles.sh" \
    "$HOME/.tmux/plugins/tmux-resurrect/strategies/vim_dotfiles.sh"

if tmux has-session 2>/dev/null; then
    tmux source-file "$HOME/.tmux.conf"
    "$HOME/.tmux/plugins/tmux-resurrect/scripts/save.sh" quiet
fi

start_script="$(printf '%s' "$DOTFILES_DIR/mac/start-tmux.sh" | sed 's/[&|]/\\&/g')"
stdout_log="$(printf '%s' "$launch_log_dir/tmux.out.log" | sed 's/[&|]/\\&/g')"
stderr_log="$(printf '%s' "$launch_log_dir/tmux.err.log" | sed 's/[&|]/\\&/g')"

sed \
    -e "s|__START_SCRIPT__|$start_script|g" \
    -e "s|__STDOUT_LOG__|$stdout_log|g" \
    -e "s|__STDERR_LOG__|$stderr_log|g" \
    "$DOTFILES_DIR/mac/$launch_agent_label.plist.in" >"$launch_agent"

plutil -lint "$launch_agent" >/dev/null

if launchctl print "gui/$UID/$launch_agent_label" >/dev/null 2>&1; then
    launchctl bootout "gui/$UID/$launch_agent_label"
fi
launchctl bootstrap "gui/$UID" "$launch_agent"

echo "Dotfiles configured. Bash: $("$BREW" --prefix bash)/bin/bash; default shell unchanged."
