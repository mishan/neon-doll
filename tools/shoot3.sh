#!/bin/sh
# Screenshot tools/preview3.py under the GTK 3 theme on a throwaway Xvfb.
# themes/* is installed into a temporary XDG_DATA_HOME with cp -rL, the same
# way a user would install it, and XDG_CONFIG_HOME is emptied too, so neither
# an installed copy nor a personal ~/.config/gtk-3.0/gtk.css gets into the
# picture.
#
#   tools/shoot3.sh THEME out.png [--menu] [--context] [--dialog] [--states]
#
# THEME is Neon-Doll-Light, Neon-Doll-Light:dark or Neon-Doll-Dark. CSS
# errors print to stderr.
set -eu
theme=$1 out=$2; shift 2
here=$(cd "$(dirname "$0")" && pwd)
repo=$(dirname "$here")
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/data/themes" "$tmp/config"
cp -rL "$repo"/themes/* "$tmp/data/themes/"

XDG_DATA_HOME=$tmp/data XDG_CONFIG_HOME=$tmp/config GTK_THEME=$theme \
xvfb-run -a -s "-screen 0 1240x1040x24" sh -c "
  GDK_BACKEND=x11 '$here/preview3.py' $* &
  pid=\$!
  sleep 3
  import -window root '$out'
  kill \$pid
"
