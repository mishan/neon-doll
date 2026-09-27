#!/bin/sh
# Screenshot tools/preview3.py under the GTK 3 theme in a sealed session.
# themes/* goes into the session's scratch ~/.local/share/themes with cp -rL,
# the same way a user would install it, so neither an installed copy nor a
# personal ~/.config/gtk-3.0/gtk.css gets into the picture.
#
#   tools/shoot3.sh THEME out.png [--menu] [--context] [--dialog] [--states]
#
# THEME is Neon-Doll-Light, Neon-Doll-Light:dark or Neon-Doll-Dark. CSS
# errors print to stderr. Needs shotbox (https://github.com/mishan/shotbox)
# on PATH.
set -eu
command -v shotbox >/dev/null || { echo "needs shotbox on PATH" >&2; exit 1; }
theme=$1 out=$2; shift 2
here=$(cd "$(dirname "$0")" && pwd)
repo=$(dirname "$here")
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/home/.local/share/themes"
cp -rL "$repo"/themes/* "$tmp/home/.local/share/themes/"

shotbox shoot "$out" --screen 1240x1040 --seed "$tmp/home" --env "GTK_THEME=$theme" \
    --log /dev/stderr --wait window:photos --wait stable -- \
  "$here/preview3.py" "$@" >/dev/null
