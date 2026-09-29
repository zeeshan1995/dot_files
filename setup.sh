#!/usr/bin/env bash
set -Eeuo pipefail
trap 'printf "Setup failed at line %s (exit %s).\n" "$LINENO" "$?" >&2' ERR

repo_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
skip_packages=false
case "${1:-}" in
    --skip-packages) skip_packages=true; shift ;;
    --help|-h)
        printf 'Usage: %s [--skip-packages]\nRun as your normal user on Ubuntu/Debian with systemd and sudo.\n' "$0"
        exit 0
        ;;
esac
if (( $# )); then
    printf 'Unknown argument: %s\n' "$1" >&2
    exit 1
fi
if (( EUID == 0 )); then
    printf 'Run setup.sh as your normal user, not with sudo; it elevates only system operations.\n' >&2
    exit 1
fi
if [[ $(uname -s) != Linux ]] || [[ ! -d /run/systemd/system ]]; then
    printf 'Automatic reboot restoration requires Linux with systemd.\n' >&2
    exit 1
fi
systemctl --user show-environment >/dev/null
command -v sudo >/dev/null
if [[ -f "${XDG_CONFIG_HOME:-$HOME/.config}/tmux/tmux.conf" ]]; then
    printf 'An XDG tmux/tmux.conf would override this setup. Merge or move it before installing ~/.tmux.conf.\n' >&2
    exit 1
fi

if ! "$skip_packages"; then
    command -v apt-get >/dev/null
    sudo apt-get update
    sudo apt-get install -y ca-certificates curl git vim tmux python3 \
        gparted net-tools cifs-utils fzf ripgrep
fi
for tool in git vim tmux python3 curl; do
    if ! command -v "$tool" >/dev/null; then
        printf 'Missing dependency: %s. Rerun without --skip-packages.\n' "$tool" >&2
        exit 1
    fi
done
python3 -c 'import sys; sys.exit("Python 3.9 or newer is required") if sys.version_info < (3, 9) else None'

# Always target the default server, not an inherited nested/named tmux connection.
unset TMUX TMUX_PANE
export PATH="$HOME/.local/bin:$PATH"
export GIT_TERMINAL_PROMPT=0
backup_dir=""
install_file() {
    local source=$1 destination=$2 mode=${3:-644}
    if [[ -f "$destination" ]] && cmp -s "$source" "$destination"; then
        chmod "$mode" "$destination"
        return
    fi
    if [[ -e "$destination" || -L "$destination" ]]; then
        if [[ -z "$backup_dir" ]]; then
            install -d -m 700 "$HOME/.local/state/dot_files/backups"
            backup_dir="$(mktemp -d "$HOME/.local/state/dot_files/backups/$(date +%Y%m%dT%H%M%S).XXXXXX")"
        fi
        cp -a --parents -- "$destination" "$backup_dir"
    fi
    install -D -m "$mode" -- "$source" "$destination"
}

clone_plugin() {
    local name=$1 destination="$HOME/.tmux/plugins/$1"
    if [[ ! -e "$destination" ]]; then
        git clone --quiet "https://github.com/tmux-plugins/$name.git" "$destination"
    elif [[ ! -d "$destination/.git" ]]; then
        printf 'Expected a plugin Git checkout at %s; refusing to overwrite it.\n' "$destination" >&2
        exit 1
    fi
}

for file in .vimrc .bashrc .tmux.conf; do
    install_file "$repo_dir/$file" "$HOME/$file"
done
while IFS= read -r -d '' file; do
    install_file "$file" "$HOME/${file#"$repo_dir/"}"
done < <(find "$repo_dir/.vim" -type f ! -name .netrwhist -print0)
install_file "$repo_dir/.local/bin/tmux-app-state" "$HOME/.local/bin/tmux-app-state" 755
install_file "$repo_dir/.copilot/hooks/tmux-app-restore.json" \
    "${COPILOT_HOME:-$HOME/.copilot}/hooks/tmux-app-restore.json"
for unit in tmux.service tmux-save.service tmux-save.timer; do
    install_file "$repo_dir/.config/systemd/user/$unit" \
        "${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user/$unit"
done
install -d -m 700 "$HOME/.local/share/tmux/resurrect" "$HOME/.local/state/tmux/vim"
install -d "$HOME/.tmux/plugins"
for plugin in tpm tmux-resurrect tmux-continuum; do
    clone_plugin "$plugin"
done
for entry in tpm/tpm tmux-resurrect/resurrect.tmux tmux-continuum/continuum.tmux; do
    test -x "$HOME/.tmux/plugins/$entry"
done

printf 'Installing configured Vim plugins...\n'
vim -Nu NONE -n -es -S "$repo_dir/scripts/install-vim-plugins.vim"

# Lingering starts the user manager at boot, without requiring an SSH login first.
sudo loginctl enable-linger "$(id -un)"
systemctl --user daemon-reload
systemctl --user enable tmux.service tmux-save.timer
if tmux has-session 2>/dev/null; then
    tmux source-file "$HOME/.tmux.conf"
    if ! systemctl --user is-active --quiet tmux.service; then
        printf 'Existing tmux server kept running; systemd will own the server after the next reboot.\n'
    fi
else
    systemctl --user start tmux.service
fi
systemctl --user start tmux-save.timer
systemctl --user is-active --quiet tmux-save.timer
tmux has-session

printf 'Setup complete. Attach with: tmux attach\n'
if [[ -n "$backup_dir" ]]; then
    printf 'Replaced files backed up under: %s\n' "$backup_dir"
fi
printf 'Restart existing Vim/Copilot instances to load the new hooks.\n'
if ! command -v copilot >/dev/null; then
    printf 'Copilot restore hooks are installed. Install and sign in to Copilot CLI before using them.\n'
fi
