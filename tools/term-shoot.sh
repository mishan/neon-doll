#!/bin/sh
# Screenshot `ls` in each Neon Doll terminal scheme, with GNU's default
# LS_COLORS on the left of each pair and dircolors/neon-doll on the right.
#
#   tools/term-shoot.sh out.png
#
# The listing is a scratch directory holding one of every kind of file
# dircolors tells apart, odd permissions included.
set -eu
out=$(realpath -m "$1")
here=$(cd "$(dirname "$0")" && pwd)
root=$(dirname "$here")
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

f=$tmp/files
mkdir -p "$f/src" "$f/shared" "$f/tmp" "$f/sticky"
chmod 777 "$f/shared"
chmod 1777 "$f/tmp"
chmod 1755 "$f/sticky"
: > "$f/notes.txt"
: > "$f/build.sh" && chmod 755 "$f/build.sh"
: > "$f/sudo-ish" && chmod 4755 "$f/sudo-ish"
: > "$f/group-run" && chmod 2755 "$f/group-run"
for n in release.tar.xz photo.jpg song.flac draft.md.bak; do : > "$f/$n"; done
ln -s notes.txt "$f/link"
ln -s missing "$f/broken"
mkfifo "$f/pipe"

cmd="cd '$f' && ls -lgo --color=always --time-style=+ | sed 1d"
dircolors -b "$root/dircolors/neon-doll" > "$tmp/nd.sh"

shots=
for v in dark light; do
  for mode in default neon-doll; do
    png=$tmp/$v-$mode.png
    if [ $mode = neon-doll ]; then setup=". '$tmp/nd.sh'"; else setup="unset LS_COLORS"; fi
    xvfb-run -a -s "-screen 0 700x330x24" sh -c "
      $setup
      GDK_BACKEND=x11 '$here/term-preview.py' '$root/tilix/neon-doll-$v.json' \"$cmd\" >/dev/null 2>&1 &
      sleep 2
      import -window root -crop 340x290+0+0 '$png'
      kill %1
    " 2>/dev/null || true
    shots="$shots $png"
  done
done
# dark: default | neon-doll, then light: default | neon-doll
convert \( "$tmp/dark-default.png" "$tmp/dark-neon-doll.png" +append \) \
        \( "$tmp/light-default.png" "$tmp/light-neon-doll.png" +append \) -append -strip "$out"
echo "$out"
