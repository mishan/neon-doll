#!/bin/sh
# Screenshot Claude Code's first-run theme picker in each Neon Doll theme,
# from claude-code/, in the matching terminal scheme: the picker lists the
# themes and draws a diff in the one chosen.
#
#   tools/claude-code-shoot.sh DIR      # writes DIR/claude-code-{dark,light}.png
#
# Claude Code runs in a scratch home with no account, so it stops at the
# picker; the sealed session keeps it off the network.
#
# Needs shotbox (https://github.com/mishan/shotbox) and claude on PATH.
set -eu
command -v shotbox >/dev/null || { echo "needs shotbox on PATH: pipx install --system-site-packages shotbox" >&2; exit 1; }
command -v claude >/dev/null || { echo "$0: needs claude on PATH" >&2; exit 1; }
dir=$(realpath -m "$1")
here=$(cd "$(dirname "$0")" && pwd)
root=$(dirname "$here")
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$dir" "$tmp/home/.claude/themes"
cp "$root"/claude-code/neon-doll-*.json "$tmp/home/.claude/themes/"

for v in dark light; do
  echo "{\"theme\": \"custom:neon-doll-$v\"}" > "$tmp/home/.claude/settings.json"
  shotbox term --shoot "$dir/claude-code-$v.png" --scheme "$root/tilix/neon-doll-$v.json" \
      --seed "$tmp/home" --size 84x31 --when 'Syntax theme' --sleep 1 -- claude
done
