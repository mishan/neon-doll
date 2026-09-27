#!/bin/sh
# Screenshot the COSMIC theme in a throwaway COSMIC, so it can be checked
# without COSMIC installed.
#
#   tools/cosmic-shoot.sh OUTDIR [dark|light ...]
#
# Runs COSMIC's compositor nested in a headless sway, in a Fedora container
# (built on first use as neon-doll-cosmic; COSMIC_IMAGE_BASE picks another
# Fedora). The theme goes in the way a user would put it in, with
# `cosmic-settings appearance import`, so COSMIC derives the rest itself. The
# terminal scheme is written into COSMIC Terminal's config, as its Import
# button would. Writes OUTDIR/cosmic-{desktop,settings}-VARIANT.png.
#
# COSMIC_SHOOT_LOGS=1 also keeps each run's logs and COSMIC config in
# OUTDIR/logs-VARIANT/.
#
# Needs docker. Everything renders in software; no GPU.
set -eu

out=$(realpath -m "$1"); shift
[ $# -gt 0 ] || set -- dark light
here=$(cd "$(dirname "$0")" && pwd)
repo=$(dirname "$here")
image=neon-doll-cosmic
mkdir -p "$out"

if ! docker image inspect $image >/dev/null 2>&1; then
  docker build -q -t $image - >/dev/null <<EOF
FROM ${COSMIC_IMAGE_BASE:-fedora:44}
RUN dnf -y install --setopt=install_weak_deps=False \
      cosmic-comp cosmic-settings cosmic-term cosmic-files cosmic-panel cosmic-bg cosmic-applets \
      sway grim git ImageMagick mesa-dri-drivers dejavu-sans-fonts dejavu-sans-mono-fonts \
      dbus-daemon procps-ng \
    && dnf clean all
EOF
fi

for variant in "$@"; do
  case $variant in dark|light) ;; *) echo "variant must be dark or light" >&2; exit 2 ;; esac
  docker run --rm -e VARIANT="$variant" -e COSMIC_SHOOT_LOGS -v "$repo:/repo:ro" -v "$out:/out" $image \
    dbus-run-session -- sh -eu -c '
V=$VARIANT; Name=$(echo $V | sed "s/./\U&/")
export HOME=/tmp/home XDG_RUNTIME_DIR=/tmp/run XDG_CURRENT_DESKTOP=COSMIC
mkdir -p $HOME/.config/sway && mkdir -m700 $XDG_RUNTIME_DIR
cfg=$HOME/.config/cosmic

cosmic-settings appearance import "/repo/cosmic/Neon-Doll-$Name.ron" >/tmp/import.log 2>&1 \
  || { cat /tmp/import.log; exit 1; }

# Tiled, so the shot shows the gaps and the focused window'"'"'s hint.
mkdir -p $cfg/com.system76.CosmicComp/v1
echo true > $cfg/com.system76.CosmicComp/v1/autotile

# The wallpaper: graph paper, the page and its 24px grid.
case $V in
  dark)  page="#0f0d14"; grid="rgba(180,140,255,0.09)" ;;
  light) page="#f7f4fa"; grid="rgba(106,63,208,0.07)" ;;
esac
magick -size 24x24 "xc:$page" -fill "$grid" \
  -draw "rectangle 0,0 23,0" -draw "rectangle 0,0 0,23" /tmp/tile.png
magick -size 1280x800 tile:/tmp/tile.png $HOME/paper.png
mkdir -p $cfg/com.system76.CosmicBackground/v1
cat > $cfg/com.system76.CosmicBackground/v1/all <<R
(output: "all", source: Path("$HOME/paper.png"), filter_by_theme: false, rotation_frequency: 3600,
 filter_method: Lanczos, scaling_mode: Zoom, sampling_method: Alphanumeric)
R

# COSMIC Terminal: the scheme, and the colors the rest of the repo gives a shell.
t=$cfg/com.system76.CosmicTerm/v1; mkdir -p $t
{ printf "{1: "; cat "/repo/cosmic/terminal/Neon Doll $Name.ron"; echo "}"; } \
  > $t/color_schemes_$V
echo "\"Neon Doll $Name\"" > $t/syntax_theme_$V
# Light or dark set outright: left to follow the system, it starts on its dark
# scheme here even when the desktop is light.
echo $Name > $t/app_theme
git config --global --add safe.directory "*"
cat > $HOME/.bashrc <<R
sleep 2   # until the window is tiled, so ls fits its columns
eval "\$(dircolors -b /repo/dircolors/neon-doll)"
PS1="doll@cosmic:\w\\\$ "
cd /repo
git -c include.path=/repo/git/neon-doll.gitconfig --no-pager log --oneline --graph --decorate --color -6
ls --color=auto
R

printf "output HEADLESS-1 resolution 1280x800\ndefault_border none\n" > $HOME/.config/sway/config
export WLR_BACKENDS=headless WLR_RENDERER=pixman WLR_LIBINPUT_NO_DEVICES=1
cp /usr/bin/sway /tmp/sway   # the packaged one has file capabilities a container refuses
/tmp/sway >/tmp/sway.log 2>&1 &
sleep 2
WAYLAND_DISPLAY=wayland-1 cosmic-comp >/tmp/comp.log 2>&1 &
sleep 4
export WAYLAND_DISPLAY=wayland-2
cosmic-bg >/tmp/bg.log 2>&1 &
cosmic-panel >/tmp/panel.log 2>&1 &
sleep 4

shot() { WAYLAND_DISPLAY=wayland-1 grim /out/cosmic-$1-$V.png; }

cosmic-files /repo >/tmp/files.log 2>&1 &
sleep 4
cosmic-term >/tmp/term.log 2>&1 &
sleep 6
shot desktop
pkill -x cosmic-files || true; pkill -x cosmic-term || true; sleep 2

cosmic-settings appearance >/tmp/settings.log 2>&1 &
sleep 6
shot settings
if [ -n "${COSMIC_SHOOT_LOGS:-}" ]; then
  mkdir -p /out/logs-$V && cp /tmp/*.log /out/logs-$V/ && cp -r $cfg /out/logs-$V/config
fi
'
  echo "$out/cosmic-desktop-$variant.png"
  echo "$out/cosmic-settings-$variant.png"
done
