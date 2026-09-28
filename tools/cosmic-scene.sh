#!/bin/sh
# The COSMIC scene, in a Wayland shotbox session: tools/cosmic-shoot.sh runs
# it in its container, with VARIANT set to dark or light and SIZE to the
# screen's, WxH.
#
# COSMIC's compositor is a window of the session's sway, full screen, and
# COSMIC runs inside it. Pictures are of sway's output, so they're taken
# with the session's WAYLAND_DISPLAY; COSMIC's own is COSMIC_DISPLAY.
set -eu
V=$VARIANT; Name=$(echo "$V" | sed "s/./\U&/")
sb="python3 /shotbox/bin/shotbox"
export XDG_CURRENT_DESKTOP=COSMIC PYTHONPATH=/shotbox
cfg=$HOME/.config/cosmic
# With COSMIC_SHOOT_LOGS, the logs go straight to OUTDIR, so a run that
# fails keeps them too; sway's log and COSMIC's config join them at the end.
if [ -n "${COSMIC_SHOOT_LOGS:-}" ]; then
  logs=/out/logs-$V
  rm -rf "$logs"
  trap 'cp "$SHOTBOX_SCRATCH/sway.log" "$logs/" 2>/dev/null; cp -r "$cfg" "$logs/config" 2>/dev/null' EXIT
else
  logs=$SHOTBOX_SCRATCH/logs
fi
mkdir -p "$logs"

# launch NAME COMMAND...: start it inside COSMIC, then wait for the screen
# to change and hold still. What runs inside COSMIC isn't a window sway
# knows about, so the change on the screen is the sign it has come up:
# below the panel, whose clock changes by itself. (Not whether the program
# is still running: cosmic-files hands itself off and exits at once.)
launch() {
  python3 - "$logs/$1.log" "$@" <<'PY'
import os, subprocess, sys
import shotbox
from shotbox import wl
log, name, cmd = sys.argv[1], sys.argv[2], sys.argv[3:]
s = shotbox.here()
w, h = map(int, os.environ["SIZE"].split("x"))
below_panel = (0, "", w, h - 40, 0, 40)   # wl's window tuple: id, name, w, h, x, y
before = wl.fingerprint(s.env, below_panel)
subprocess.Popen(cmd, stdout=open(log, "ab"), stderr=subprocess.STDOUT,
                 env={**os.environ, "WAYLAND_DISPLAY": os.environ["COSMIC_DISPLAY"]})
try:
    s.until(f"{name} to show", lambda: wl.fingerprint(s.env, below_panel) != before,
            timeout=60)
except shotbox.SessionError as e:
    sys.exit(f"cosmic-scene: {e}")
try:
    s.wait_stable(1, timeout=60)
except shotbox.SessionError as e:
    sys.exit(f"cosmic-scene: {name} never held still: {e}")
PY
}

# sockets: the Wayland sockets in the runtime dir, by name.
sockets() {
  for f in "$XDG_RUNTIME_DIR"/wayland-[0-9]*; do
    case ${f##*/} in *.lock) ;; *) [ -e "$f" ] && echo "${f##*/}" ;; esac
  done
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
magick -size "$SIZE" "tile:$SHOTBOX_SCRATCH/tile.png" "$HOME/paper.png"
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
# The shell waits for its window to be tiled (up to 3s), so ls fits its
# columns, and says it's ready once its output is out.
cat > "$HOME/.bashrc" <<R
s=\$(stty size); n=0
while [ "\$(stty size)" = "\$s" ] && [ \$n -lt 30 ]; do sleep 0.1; n=\$((n + 1)); done
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
sockets > "$SHOTBOX_SCRATCH/sockets-before"
cosmic-comp >"$logs/comp.log" 2>&1 &
comp=$!
$sb wait window Smithay --timeout 60 \
  || { echo "cosmic-scene: cosmic-comp didn't come up:" >&2; tail -20 "$logs/comp.log" >&2; exit 1; }
swaymsg -q "[pid=$comp] fullscreen enable"
$sb wait stable 0.5 --window Smithay --timeout 30
COSMIC_DISPLAY=
n=0
while [ -z "$COSMIC_DISPLAY" ] && [ $n -lt 100 ]; do
  COSMIC_DISPLAY=$(sockets | grep -vxF -f "$SHOTBOX_SCRATCH/sockets-before" | head -1) || true
  [ -n "$COSMIC_DISPLAY" ] || sleep 0.1
  n=$((n + 1))
done
[ -n "$COSMIC_DISPLAY" ] || { echo "cosmic-scene: cosmic-comp made no socket" >&2; exit 1; }
export COSMIC_DISPLAY

launch bg cosmic-bg
launch panel cosmic-panel
launch files cosmic-files /repo
WAYLAND_DISPLAY=$COSMIC_DISPLAY cosmic-term >"$logs/term.log" 2>&1 &
$sb wait ready --timeout 60
$sb wait stable 1 --timeout 60
$sb capture "/out/cosmic-desktop-$V.png"

# Gone, not just asked to go: otherwise their windows closing could pass
# for Settings coming up. (Zombies don't count; docker's --init reaps them.)
pkill -x cosmic-files || true; pkill -x cosmic-term || true
n=0
while pgrep -r RSDT -x 'cosmic-files|cosmic-term' >/dev/null && [ $n -lt 100 ]; do
  sleep 0.1; n=$((n + 1))
done
$sb wait stable 1 --timeout 60
launch settings cosmic-settings appearance
$sb capture "/out/cosmic-settings-$V.png"
