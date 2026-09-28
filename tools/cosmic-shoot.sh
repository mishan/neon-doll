#!/bin/sh
# Screenshot the COSMIC theme in a throwaway COSMIC, so it can be checked
# without COSMIC installed.
#
#   tools/cosmic-shoot.sh OUTDIR [dark|light ...]
#
# Runs COSMIC's compositor nested in a Wayland shotbox session (a headless
# sway), in a Fedora container, built as neon-doll-cosmic (COSMIC_IMAGE_BASE
# picks another Fedora). tools/cosmic-scene.sh is what runs in it: the theme
# goes in the way a user would put it in, with `cosmic-settings appearance
# import`, so COSMIC derives the rest itself, and the terminal scheme is
# written into COSMIC Terminal's config, as its Import button would. Writes
# OUTDIR/cosmic-{desktop,settings}-VARIANT.png.
#
# COSMIC_SHOOT_LOGS=1 also keeps each run's logs and COSMIC config in
# OUTDIR/logs-VARIANT/. A wait that gives up leaves a picture of the screen
# as it was, OUTDIR/cosmic-failed-VARIANT.png.
#
# Needs docker, and shotbox (https://github.com/mishan/shotbox) checked out
# beside this repository or where SHOTBOX_DIR points. Everything renders in
# software; no GPU.
set -eu

out=$(realpath -m "$1"); shift
[ $# -gt 0 ] || set -- dark light
here=$(cd "$(dirname "$0")" && pwd)
repo=$(dirname "$here")
shotbox=$(realpath -m "${SHOTBOX_DIR:-$repo/../shotbox}")
image=neon-doll-cosmic
mkdir -p "$out"
[ -x "$shotbox/bin/shotbox" ] || {
  echo "$0: no shotbox at $shotbox; clone https://github.com/mishan/shotbox there, or set SHOTBOX_DIR" >&2
  exit 2
}

# Python for shotbox. The packaged sway has file capabilities a container
# refuses, and a copy doesn't, so the copy goes first on PATH.
docker build -q -t $image - >/dev/null <<EOF
FROM ${COSMIC_IMAGE_BASE:-fedora:44}
RUN dnf -y install --setopt=install_weak_deps=False \
      cosmic-comp cosmic-settings cosmic-term cosmic-files cosmic-panel cosmic-bg cosmic-applets \
      sway grim git ImageMagick mesa-dri-drivers dejavu-sans-fonts dejavu-sans-mono-fonts \
      dbus-daemon procps-ng python3 \
    && dnf clean all \
    && cp /usr/bin/sway /usr/local/bin/sway
EOF

for variant in "$@"; do
  case $variant in dark|light) ;; *) echo "variant must be dark or light" >&2; exit 2 ;; esac
  # --desktop: COSMIC starts its helpers over D-Bus activation.
  docker run --rm -v "$repo:/repo:ro" -v "$shotbox:/shotbox:ro" -v "$out:/out" $image \
    python3 /shotbox/bin/shotbox run --wayland --desktop --screen 1280x800 \
      --env VARIANT="$variant" --env COSMIC_SHOOT_LOGS="${COSMIC_SHOOT_LOGS:-}" \
      --env SHOTBOX_FAILED="/out/cosmic-failed-$variant.png" \
      -- sh /repo/tools/cosmic-scene.sh
  echo "$out/cosmic-desktop-$variant.png"
  echo "$out/cosmic-settings-$variant.png"
done
