#!/bin/sh
# Screenshot tools/preview.py in a sealed session, so the theme can be
# checked without installing it or touching the running session. CSS errors
# print to stderr.
#
#   tools/shoot.sh out.png [--menu] [--dialog] [--light]
#
# Needs shotbox (https://github.com/mishan/shotbox) on PATH.
set -eu
command -v shotbox >/dev/null || { echo "needs shotbox on PATH" >&2; exit 1; }
out=$1; shift
here=$(cd "$(dirname "$0")" && pwd)
shotbox shoot "$out" --screen 1240x1040 --log /dev/stderr \
    --wait window:preview.py --wait stable -- \
  "$here/preview.py" "$@" >/dev/null
