#!/bin/sh
# Screenshot GNOME Text Editor in each Neon Doll variant: the GtkSourceView
# scheme on the text, the GTK 4 stylesheet on the window around it.
#
#   tools/text-editor-shoot.sh DIR    # writes DIR/text-editor-{dark,light}.png
#
# Both go in a scratch home the way install.sh puts them, and the editor's
# settings are a keyfile there, so nothing installed or set on the desktop
# gets in. It opens tools/check-tokens.py.
#
# Needs shotbox (https://github.com/mishan/shotbox) and gnome-text-editor
# on PATH.
set -eu
command -v shotbox >/dev/null || { echo "needs shotbox on PATH: pipx install --system-site-packages shotbox" >&2; exit 1; }
command -v gnome-text-editor >/dev/null || { echo "$0: needs gnome-text-editor on PATH" >&2; exit 1; }
dir=$(realpath -m "$1")
here=$(cd "$(dirname "$0")" && pwd)
root=$(dirname "$here")
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
home=$tmp/home
mkdir -p "$dir" "$home/.config/gtk-4.0" "$home/.config/glib-2.0/settings" \
  "$home/.local/share/gtksourceview-5/styles"
cp "$root/gtk-4.0/gtk.css" "$home/.config/gtk-4.0/"
cp "$root"/gtksourceview/neon-doll-*.xml "$home/.local/share/gtksourceview-5/styles/"
cp "$here/check-tokens.py" "$home/check-tokens.py"

# A session's settings live in each program's memory, so the editor's are a
# keyfile it reads for itself.
for v in dark light; do
  printf "[org/gnome/TextEditor]\nstyle-scheme='neon-doll-%s'\nstyle-variant='%s'\nrestore-session=false\nspellcheck=false\n" \
    "$v" "$v" > "$home/.config/glib-2.0/settings/keyfile"
  style=; [ "$v" = dark ] && style=--dark
  shotbox shoot "$dir/text-editor-$v.png" $style --seed "$home" --env GSETTINGS_BACKEND=keyfile \
      --window 'check-tokens.py.*' --wait stable -- \
    sh -c 'exec gnome-text-editor --standalone "$HOME/check-tokens.py"' >/dev/null
done
