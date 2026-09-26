#!/bin/sh
# Screenshot ag in each Neon Doll terminal scheme, through the alias in
# ag/neon-doll.sh, searching a few scratch files.
#
#   tools/ag-shoot.sh DIR      # writes DIR/ag-{dark,light}.png
#
# Needs shotbox on PATH.
set -eu
command -v shotbox >/dev/null || { echo "needs shotbox on PATH" >&2; exit 1; }
dir=$(realpath -m "$1")
here=$(cd "$(dirname "$0")" && pwd)
root=$(dirname "$here")
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$dir" "$tmp/src/theme" "$tmp/docs"

cat > "$tmp/src/theme/palette.py" <<'PY'
PINK = "#ff2d95"     # position: where you are
PURPLE = "#b48cff"   # interactive, at rest

def cursor_color():
    return PINK
PY
cat > "$tmp/src/cursor.c" <<'C'
/* The cursor is pink, and nothing else is. */
static const char *cursor = "pink";
C
cat > "$tmp/docs/README.md" <<'MD'
# Roles

Fuchsia (pink) is where you are; purple is what you can touch.
MD

for v in dark light; do
  shotbox shoot "$dir/ag-$v.png" --window shotbox-term --wait ready --crop 600x250+0+0 -- \
    shotbox term --scheme "$root/tilix/neon-doll-$v.json" --size 72x24 --when 'return PINK' -- \
      bash --norc -c "shopt -s expand_aliases; . '$root/ag/neon-doll.sh'
        cd '$tmp' && ag -i pink; sleep 60"
done
