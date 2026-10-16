#!/bin/sh
# A copy of this repo for a desktop shot's terminal and file manager to show:
# its committed files, under a short history of its own with fixed dates, so
# the shot shows neither the checkout's branches and untracked files nor how
# long ago they changed. The commits are empty, so their hashes don't change
# with the files.
#
#   tools/scene-repo.sh DIR
set -eu
here=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$1"
git -C "$(dirname "$here")" archive HEAD | tar -x -C "$1"
cd "$1"
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
export GIT_AUTHOR_NAME=Doll GIT_AUTHOR_EMAIL=doll@neon.test
export GIT_COMMITTER_NAME=Doll GIT_COMMITTER_EMAIL=doll@neon.test
commit() {
  export GIT_AUTHOR_DATE="2026-09-$1T17:00:00Z" GIT_COMMITTER_DATE="2026-09-$1T17:00:00Z"
  shift; git commit -q --allow-empty -m "$*"
}
git init -q -b main
commit 20 "Neon Doll: the tokens, GTK and the Shell"
commit 21 "Add the terminal schemes"
git tag v1.0
commit 22 "Add KDE: Plasma, Kvantum, Konsole and Kate"
commit 23 "High Contrast: solid edges on every control"
commit 24 "Add COSMIC: the desktop and its terminal"
commit 25 "Measure contrast on the surface a token lands on"
find . -path ./.git -prune -o -exec touch -h -d "2026-09-25 17:00 UTC" {} +
