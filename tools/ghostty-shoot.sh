#!/bin/sh
# Screenshot Ghostty in each Neon Doll theme, from ghostty/themes/, over a
# listing in the ls colors and a prompt.
#
#   tools/ghostty-shoot.sh DIR      # writes DIR/ghostty-{dark,light}.png
#
# Ghostty runs undecorated, 82 by 22 cells, in a sealed session with a scratch
# home, so neither an installed theme nor your config gets in. The files'
# dates and the prompt are fixed, and the listing leaves out owner and
# group, so a reshoot changes only with the theme.
#
# Needs shotbox (https://github.com/mishan/shotbox) and ghostty on PATH.
set -eu
command -v shotbox >/dev/null || { echo "needs shotbox on PATH: pipx install --system-site-packages shotbox" >&2; exit 1; }
command -v ghostty >/dev/null || { echo "$0: needs ghostty on PATH" >&2; exit 1; }
dir=$(realpath -m "$1")
here=$(cd "$(dirname "$0")" && pwd)
root=$(dirname "$here")
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$dir" "$tmp/proj/src"
: > "$tmp/proj/notes.md"; : > "$tmp/proj/photo.jpg"; : > "$tmp/proj/release.tar.xz"
touch -d "2026-09-25 17:24 UTC" "$tmp/proj"/*

cat > "$tmp/scene.sh" <<EOF
eval "\$(dircolors -b '$root/dircolors/neon-doll')"
cd '$tmp/proj' && TZ=UTC ls -lgo --color=always --time-style='+%b %d %H:%M'
e=\$(printf '\\033')
printf '\\n%s[35mSYNOPSIS%s[0m  a man page in a terminal that never existed\\n' "\$e" "\$e"
printf '%s[90m[17:24:58]%s[0m [%s[35mdoll@neon%s[0m:%s[95m~/proj%s[0m]\\n$ ' "\$e" "\$e" "\$e" "\$e" "\$e" "\$e"
exec cat >/dev/null
EOF

for v in dark light; do
  name="Neon Doll $(echo "$v" | sed 's/./\U&/')"
  shotbox shoot "$dir/ghostty-$v.png" --window '.*' --wait stable -- \
    ghostty --config-default-files=false --theme="$root/ghostty/themes/$name" \
      --window-width=82 --window-height=22 --window-decoration=false --gtk-titlebar=false \
      --cursor-style-blink=false \
      -e sh "$tmp/scene.sh" >/dev/null
done
