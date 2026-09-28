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
# OUTDIR/logs-VARIANT/, a failed run's too. A wait that gives up leaves a
# picture of the screen as it was, OUTDIR/cosmic-failed-VARIANT.png.
#
# Needs docker. shotbox (https://github.com/mishan/shotbox) is in the image,
# from PyPI at the version below; SHOTBOX_DIR runs a checkout of it instead,
# for working on shotbox. Everything renders in software; no GPU.
set -eu

out=$(realpath -m "$1"); shift
[ $# -gt 0 ] || set -- dark light
here=$(cd "$(dirname "$0")" && pwd)
repo=$(dirname "$here")
image=neon-doll-cosmic
size=1280x800
mkdir -p "$out"
# shotbox from PyPI, or a checkout of it where SHOTBOX_DIR points.
if [ -n "${SHOTBOX_DIR:-}" ]; then
  shotbox=$(realpath -m "$SHOTBOX_DIR")
  [ -x "$shotbox/bin/shotbox" ] || { echo "$0: no shotbox at $shotbox" >&2; exit 2; }
  mount="-v $shotbox:/shotbox:ro"; sb="python3 /shotbox/bin/shotbox"
else
  mount=; sb=shotbox
fi

# shotbox at a known version: a newer one is a change to make on purpose.
# The packaged sway has file capabilities a container refuses, and a copy
# doesn't, so the copy goes first on PATH.
docker build -q -t $image - >/dev/null <<EOF
FROM ${COSMIC_IMAGE_BASE:-fedora:44}
RUN dnf -y install --setopt=install_weak_deps=False \
      cosmic-comp cosmic-settings cosmic-term cosmic-files cosmic-panel cosmic-bg cosmic-applets \
      sway grim git ImageMagick mesa-dri-drivers dejavu-sans-fonts dejavu-sans-mono-fonts \
      dbus-daemon procps-ng python3 python3-pip \
    && dnf clean all \
    && pip install --no-cache-dir shotbox==0.3.0 \
    && cp /usr/bin/sway /usr/local/bin/sway
EOF

for variant in "$@"; do
  case $variant in dark|light) ;; *) echo "variant must be dark or light" >&2; exit 2 ;; esac
  failed=$out/cosmic-failed-$variant.png
  rm -f "$out/cosmic-desktop-$variant.png" "$out/cosmic-settings-$variant.png" "$failed"
  # --init reaps what the scene stops; --desktop: COSMIC starts its helpers
  # over D-Bus activation. It runs as root, which --desktop's bus needs
  # here, and hands what it wrote back to OUTDIR's owner on the way out.
  # shellcheck disable=SC2086 # $mount and $sb are meant to split
  docker run --rm --init -v "$repo:/repo:ro" $mount -v "$out:/out" $image \
    sh -c 'trap "chown -R $(stat -c %u:%g /out) /out" EXIT; "$@"' sh \
    $sb run --wayland --desktop --screen $size \
      --env VARIANT="$variant" --env SIZE=$size --env COSMIC_SHOOT_LOGS="${COSMIC_SHOOT_LOGS:-}" \
      --env SHOTBOX="$sb" \
      --env SHOTBOX_FAILED="/out/${failed##*/}" \
      -- sh /repo/tools/cosmic-scene.sh || {
    echo "$0: $variant failed" >&2
    [ -e "$failed" ] && echo "  the screen then: $failed" >&2
    if [ -n "${COSMIC_SHOOT_LOGS:-}" ]; then
      echo "  the logs: $out/logs-$variant/" >&2
    else
      echo "  COSMIC_SHOOT_LOGS=1 keeps the logs" >&2
    fi
    exit 1
  }
  echo "$out/cosmic-desktop-$variant.png"
  echo "$out/cosmic-settings-$variant.png"
done
