#!/bin/sh
# Screenshot irssi in each Neon Doll theme, in the matching Tilix scheme.
#
#   tools/irssi-shoot.sh DIR      # writes DIR/irssi-{dark,light}.png
#
# irssi runs with a scratch home, connected to tools/irssi-server.py on
# localhost, which plays a scripted channel; then a reply and an action are
# typed in, and a line is left unsent in the input.
set -eu
dir=$(realpath -m "$1")
here=$(cd "$(dirname "$0")" && pwd)
root=$(dirname "$here")
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$dir"

typed=$(printf "/window 2\ryes, it follows the terminal's scheme\r/me waves\rthe prompt is fuchsia, since that's where you are")
port=16667
for v in dark light; do
  theme=neon-doll; [ $v = light ] && theme=neon-doll-light
  home=$tmp/irssi-$v
  mkdir -p "$home"
  cp "$root/irssi/$theme.theme" "$home/"
  cat > "$home/config" <<CONF
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
  sleep 0.5
  env -u DISPLAY -u WAYLAND_DISPLAY -u DBUS_SESSION_BUS_ADDRESS -u STY -u TMUX \
    xvfb-run -a -s "-screen 0 1000x620x24" sh -c "
      COLORTERM=truecolor PREVIEW_SIZE=88x24 GDK_BACKEND=x11 \
        '$here/term-preview.py' '$root/tilix/neon-doll-$v.json' \
        \"irssi --home='$home' -c 127.0.0.1 -p $port\" \"$typed\" >/dev/null 2>&1 &
      sleep 6
      import -window root '$tmp/$v.png'
      kill %1
    " 2>/dev/null || true
  kill $server 2>/dev/null || true
  convert "$tmp/$v.png" -crop 800x440+0+0 +repage -strip "$dir/irssi-$v.png"
  echo "$dir/irssi-$v.png"
done
