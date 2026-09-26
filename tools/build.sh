#!/bin/sh
# Rebuild every generated theme from tokens.toml, or check that none is stale.
#
#   tools/build.sh           # write them all
#   tools/build.sh --check   # fail if any would change
#
# The text schemes go first: the Ghostty, Windows Terminal, vim and VS Code
# builders read the Tilix schemes they write.
set -eu
here=$(cd "$(dirname "$0")" && pwd)
check=
[ "${1:-}" = --check ] && check=--check

if [ -n "$check" ]; then
  "$here/scheme-colors.py" --check
else
  "$here/scheme-colors.py" --write
fi
for b in palettes shell chrome firefox glow ghostty windows vim vscode irssi cursor; do
  "$here/build-$b.py" $check
done
if [ -n "$check" ]; then echo "all up to date"; fi
