#!/bin/sh
# Build the release archives into dist/.
#
#   tools/dist.sh [VERSION]      # VERSION defaults to `git describe`
#
# neon-doll-themes-VERSION.tar.xz  the two theme dirs at the top level, links
#                                  resolved: what a theme site's one-click
#                                  install unpacks into ~/.themes (GTK 3 and
#                                  Shell only)
# neon-doll-VERSION.tar.xz         the whole tree at that commit, with
#                                  install.sh: every part, GTK 4 included
# neon-doll-{dark,light}-chrome-VERSION.zip
#                                  a Chrome theme each, as the Chrome Web
#                                  Store takes them
# neon-doll-firefox-VERSION.zip    the Firefox theme, light and dark in one,
#                                  unsigned, for addons.mozilla.org to sign
#
# The GTK 4 stylesheet is kept out of the theme dirs on purpose: a gtk-4.0/
# inside a theme dir is loaded as a complete theme by GTK 4 apps that don't
# use libadwaita, and this one only works layered over Adwaita.
set -eu

here=$(cd "$(dirname "$0")" && pwd)
root=$(dirname "$here")
cd "$root"

if [ -n "$(git status --porcelain)" ]; then
  echo "commit first: the archives are built from HEAD" >&2
  exit 1
fi
version=${1:-$(git describe --tags --always)}
mkdir -p dist
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

git archive --format=tar --prefix="neon-doll-$version/" HEAD | xz -9 > "dist/neon-doll-$version.tar.xz"

git archive --format=tar HEAD themes gtk-3.0 COPYING | tar -x -C "$tmp"
mkdir "$tmp/out"
for t in "$tmp"/themes/*/; do
  cp -RL "$t" "$tmp/out/"
  cp "$tmp/COPYING" "$tmp/out/$(basename "$t")/"
done
tar -C "$tmp/out" --owner=0 --group=0 --numeric-owner --sort=name \
  -cJf "dist/neon-doll-themes-$version.tar.xz" .

# Chrome Web Store uploads are a zip of the theme folder.
for t in chrome/*/; do
  name=$(basename "$t")
  git archive --format=zip HEAD:"chrome/$name" > "dist/$name-chrome-$version.zip"
done

# An AMO upload is a zip with manifest.json at the top. userChrome.css stays
# out: it isn't part of the add-on, and goes in by hand.
git archive --format=zip HEAD:firefox manifest.json images > "dist/neon-doll-firefox-$version.zip"

ls -l dist/*"$version"*
