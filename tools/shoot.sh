#!/bin/sh
# Screenshot tools/preview.py on a throwaway X server, so the theme can be
# checked without installing it or touching the running session.
#
#   tools/shoot.sh out.png [--menu] [--dialog]
set -eu
out=$1; shift
here=$(cd "$(dirname "$0")" && pwd)
xvfb-run -a -s "-screen 0 1240x1040x24" sh -c "
  GDK_BACKEND=x11 GSK_RENDERER=cairo '$here/preview.py' $* &
  pid=\$!
  sleep 3
  import -window root '$out'
  kill \$pid
"
