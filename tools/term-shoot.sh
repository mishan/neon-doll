#!/bin/sh
# Screenshot `ls` in each Neon Doll terminal scheme, with GNU's default
# LS_COLORS on the left of each pair and dircolors/neon-doll on the right.
#
#   tools/term-shoot.sh out.png
#
# The listing is a scratch directory holding one of every kind of file
# dircolors tells apart, odd permissions included. Needs shotbox
# on PATH.
set -eu
command -v shotbox >/dev/null || { echo "needs shotbox on PATH" >&2; exit 1; }
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

for v in dark light; do
  for mode in default neon-doll; do
    if [ $mode = neon-doll ]; then setup=". '$tmp/nd.sh'"; else setup="unset LS_COLORS"; fi
    shotbox shoot "$tmp/$v-$mode.png" --window shotbox-term --wait ready --crop 340x290+0+0 -- \
      shotbox term --scheme "$root/tilix/neon-doll-$v.json" --size 72x24 --when 'rwt.* tmp' -- \
        bash --norc -c "$setup; $cmd; sleep 60" >/dev/null
  done
done
# dark: default | neon-doll, then light: default | neon-doll
convert \( "$tmp/dark-default.png" "$tmp/dark-neon-doll.png" +append \) \
        \( "$tmp/light-default.png" "$tmp/light-neon-doll.png" +append \) -append -strip "$out"
echo "$out"
