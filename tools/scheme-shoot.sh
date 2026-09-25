#!/bin/sh
# Screenshot a text scheme on a throwaway X server, without installing it.
#
#   tools/scheme-shoot.sh out.png gsv [dark|light]     # tools/scheme-preview.py
#   tools/scheme-shoot.sh out.png emacs [dark|light]   # emacs -Q, emacs/ theme
set -eu
out=$1; what=$2; variant=${3:-dark}
here=$(cd "$(dirname "$0")" && pwd)
root=$(dirname "$here")
case $what in
  gsv)
    cmd="GDK_BACKEND=x11 GSK_RENDERER=cairo '$here/scheme-preview.py' $variant"
    size=1000x720 ;;
  emacs)
    cmd="GDK_BACKEND=x11 emacs -Q --no-site-file -geometry 110x46+0+0 -l '$here/scheme-emacs-sample.el' --eval \"(neon-doll-sample '$variant \\\"$root\\\")\""
    size=1006x856 ;;
  *) echo "usage: $0 out.png gsv|emacs [dark|light]" >&2; exit 2 ;;
esac
xvfb-run -a -s "-screen 0 ${size}x24" sh -c "
  $cmd &
  pid=\$!
  sleep 4
  import -window root '$out'
  kill \$pid
"
