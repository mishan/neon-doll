#!/bin/sh
# Screenshot a text scheme in a sealed session, without installing it.
#
#   tools/scheme-shoot.sh out.png gsv [dark|light]     # tools/scheme-preview.py
#   tools/scheme-shoot.sh out.png emacs [dark|light]   # emacs -Q, emacs/ theme
#
# Needs shotbox (https://github.com/mishan/shotbox) on PATH.
set -eu
command -v shotbox >/dev/null || { echo "needs shotbox on PATH" >&2; exit 1; }
out=$1; what=$2; variant=${3:-dark}
here=$(cd "$(dirname "$0")" && pwd)
root=$(dirname "$here")
case $what in
  gsv)
    window="Neon Doll .*"
    wait=stable
    set -- "$here/scheme-preview.py" "$variant"
    size=1000x720 ;;
  emacs)
    # Emacs maps its frame before it paints it, so a still screen isn't
    # enough: it says it's ready once it has redrawn.
    window=".* - GNU Emacs at .*"
    set -- emacs -Q --no-site-file -geometry 110x46+0+0 -l "$here/scheme-emacs-sample.el" \
      --eval "(neon-doll-sample '$variant \"$root\")" \
      --eval '(progn (redisplay t) (write-region "" nil (expand-file-name "ready" (getenv "SHOTBOX_SCRATCH")) nil (quote silent)))'
    wait=ready
    size=1006x856 ;;
  *) echo "usage: $0 out.png gsv|emacs [dark|light]" >&2; exit 2 ;;
esac
shotbox shoot "$out" --screen "$size" --wait "window:$window" --wait $wait -- "$@" >/dev/null
