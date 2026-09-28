#!/bin/sh
# The COSMIC scene, in a Wayland shotbox session: tools/cosmic-shoot.sh runs
# it in its container, with VARIANT set to dark or light.
#
# COSMIC's compositor is a window of the session's sway, full screen, and
# COSMIC runs inside it. Pictures are of sway's output, so they're taken
# with the session's WAYLAND_DISPLAY; COSMIC's own is COSMIC_DISPLAY.
set -eu
V=$VARIANT; Name=$(echo "$V" | sed "s/./\U&/")
sb="python3 /shotbox/bin/shotbox"
export XDG_CURRENT_DESKTOP=COSMIC PYTHONPATH=/shotbox
cfg=$HOME/.config/cosmic
logs=$SHOTBOX_SCRATCH/logs
mkdir -p "$logs"

# launch NAME COMMAND...: start it inside COSMIC, then wait for the screen
# to change and hold still. What runs inside COSMIC isn't a window sway
# knows about, so the change on the screen is the sign it has come up:
# below the panel, whose clock changes by itself.
launch() {
  python3 - "$logs/$1.log" "$@" <<'PY'
import os, subprocess, sys
import shotbox
from shotbox import wl
s = shotbox.here()
below_panel = (0, "", 1280, 760, 0, 40)   # as a window: id, name, w, h, x, y
before = wl.fingerprint(s.env, below_panel)
subprocess.Popen(sys.argv[3:], stdout=open(sys.argv[1], "ab"), stderr=subprocess.STDOUT,
                 env={**os.environ, "WAYLAND_DISPLAY": os.environ["COSMIC_DISPLAY"]})
try:
    s.until(f"{sys.argv[2]} to show",
            lambda: wl.fingerprint(s.env, below_panel) != before, timeout=60)
    s.wait_stable(1, timeout=60)
except shotbox.SessionError as e:
    sys.exit(f"cosmic-scene: {e}")
PY
}

cosmic-settings appearance import "/repo/cosmic/Neon-Doll-$Name.ron" >"$logs/import.log" 2>&1 \
  || { cat "$logs/import.log"; exit 1; }

# Tiled, so the shot shows the gaps and the focused window's hint.
mkdir -p "$cfg/com.system76.CosmicComp/v1"
echo true > "$cfg/com.system76.CosmicComp/v1/autotile"

# The wallpaper: graph paper, the page and its 24px grid.
case $V in
  dark)  page="#0f0d14"; grid="rgba(180,140,255,0.09)" ;;
  light) page="#f7f4fa"; grid="rgba(106,63,208,0.07)" ;;
esac
magick -size 24x24 "xc:$page" -fill "$grid" \
  -draw "rectangle 0,0 23,0" -draw "rectangle 0,0 0,23" "$SHOTBOX_SCRATCH/tile.png"
magick -size 1280x800 "tile:$SHOTBOX_SCRATCH/tile.png" "$HOME/paper.png"
mkdir -p "$cfg/com.system76.CosmicBackground/v1"
cat > "$cfg/com.system76.CosmicBackground/v1/all" <<R
(output: "all", source: Path("$HOME/paper.png"), filter_by_theme: false, rotation_frequency: 3600,
 filter_method: Lanczos, scaling_mode: Zoom, sampling_method: Alphanumeric)
R

# COSMIC Terminal: the scheme, and the colors the rest of the repo gives a shell.
t=$cfg/com.system76.CosmicTerm/v1; mkdir -p "$t"
{ printf "{1: "; cat "/repo/cosmic/terminal/Neon Doll $Name.ron"; echo "}"; } \
  > "$t/color_schemes_$V"
echo "\"Neon Doll $Name\"" > "$t/syntax_theme_$V"
# Light or dark set outright: left to follow the system, it starts on its dark
# scheme here even when the desktop is light.
echo "$Name" > "$t/app_theme"
git config --global --add safe.directory "*"
# The shell says it's ready once its output is out.
cat > "$HOME/.bashrc" <<R
sleep 2   # until the window is tiled, so ls fits its columns
eval "\$(dircolors -b /repo/dircolors/neon-doll)"
PS1="doll@cosmic:\w\\\$ "
cd /repo
git -c include.path=/repo/git/neon-doll.gitconfig --no-pager log --oneline --graph --decorate --color -6
ls --color=auto
touch "$SHOTBOX_SCRATCH/ready"
R

# COSMIC's compositor, as a window of sway's (Smithay's, by its title; it
# has no app id), made full screen; its own socket is the one that wasn't
# there before it.
ls "$XDG_RUNTIME_DIR" > "$SHOTBOX_SCRATCH/sockets-before"
cosmic-comp >"$logs/comp.log" 2>&1 &
comp=$!
$sb wait window Smithay --timeout 60
swaymsg -q "[pid=$comp] fullscreen enable"
for i in $(seq 100); do
  COSMIC_DISPLAY=$(ls "$XDG_RUNTIME_DIR" | grep -x 'wayland-[0-9]*' \
    | grep -vxF -f "$SHOTBOX_SCRATCH/sockets-before" | head -1) || true
  [ -n "$COSMIC_DISPLAY" ] && break
  sleep 0.1
done
[ -n "$COSMIC_DISPLAY" ] || { echo "cosmic-comp made no socket; see $logs/comp.log" >&2; exit 1; }
export COSMIC_DISPLAY

launch bg cosmic-bg
launch panel cosmic-panel
launch files cosmic-files /repo
WAYLAND_DISPLAY=$COSMIC_DISPLAY cosmic-term >"$logs/term.log" 2>&1 &
$sb wait ready --timeout 60
$sb wait stable 1 --timeout 60
$sb capture "/out/cosmic-desktop-$V.png"

pkill -x cosmic-files || true; pkill -x cosmic-term || true
$sb wait stable 1 --timeout 60
launch settings cosmic-settings appearance
$sb capture "/out/cosmic-settings-$V.png"

if [ -n "${COSMIC_SHOOT_LOGS:-}" ]; then
  mkdir -p "/out/logs-$V" && cp "$logs"/*.log "$SHOTBOX_SCRATCH/sway.log" "/out/logs-$V/" \
    && cp -r "$cfg" "/out/logs-$V/config"
fi
