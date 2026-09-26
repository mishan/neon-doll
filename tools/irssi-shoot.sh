#!/bin/sh
# Screenshot irssi in each Neon Doll theme, in the matching Tilix scheme.
#
#   tools/irssi-shoot.sh DIR      # writes DIR/irssi-{dark,light}.png
#
# Needs shotbox (https://github.com/mishan/shotbox) on PATH. irssi runs in a
# sealed session with a scratch home, connected to tools/irssi-server.py on
# localhost, which plays a scripted channel; then a reply and an action are
# typed in, and a line is left unsent in the input.
set -eu
command -v shotbox >/dev/null || { echo "needs shotbox on PATH" >&2; exit 1; }
dir=$(realpath -m "$1")
here=$(cd "$(dirname "$0")" && pwd)
root=$(dirname "$here")
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$dir"

port=16667
for v in dark light; do
  theme=neon-doll; [ $v = light ] && theme=neon-doll-light
  home=$tmp/home-$v
  mkdir -p "$home/.irssi"
  cp "$root/irssi/$theme.theme" "$home/.irssi/"
  cat > "$home/.irssi/config" <<CONF
settings = {
  core = {
    nick = "doll"; real_name = "Doll"; user_name = "doll";
    timestamp_format = "%H:%M";
  };
  "fe-common/core" = { theme = "$theme"; };
  "fe-text" = { colors_ansi_24bit = "yes"; };
};
CONF
  port=$((port + 1))
  "$here/irssi-server.py" $port &
  server=$!
  # The server script joins doll to #neon-doll (window 2) and #cyberpunk,
  # and ends with a query; irssi doesn't switch to channels it was put in,
  # so go to window 2 first.
  shotbox shoot "$dir/irssi-$v.png" --window shotbox-term --wait ready \
      --seed "$home" --env COLORTERM=truecolor -- \
    shotbox term --scheme "$root/tilix/neon-doll-$v.json" --size 88x24 \
      --when 'End of MOTD' --type '/window 2\r' \
      --when 'Act: 3,4' --type "yes, it follows the terminal's scheme\r" \
      --when "doll> yes" --type '/me waves\r' \
      --when 'doll waves' --type "the prompt is fuchsia, since that's where you are" \
      --when 'where you are' \
      -- irssi -c 127.0.0.1 -p $port
  kill $server 2>/dev/null || true
done
