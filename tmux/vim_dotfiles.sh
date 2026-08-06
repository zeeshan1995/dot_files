#!/usr/bin/env bash

set -euo pipefail

original_command="$1"
directory="$2"

if [ "$(uname -s)" != "Darwin" ]; then
    printf '%s\n' "$original_command"
    exit 0
fi

working_dir="$(cd "$directory" && pwd -P)"
session_id="$(printf '%s' "$working_dir" | shasum -a 256 | awk '{print $1}')"
session_file="$HOME/Library/Application Support/vim/sessions/$session_id.vim"

if [ -s "$session_file" ]; then
    printf 'vim -S %q\n' "$session_file"
else
    printf '%s\n' "$original_command"
fi
