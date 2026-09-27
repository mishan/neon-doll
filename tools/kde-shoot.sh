#!/bin/sh
# Screenshot the KDE themes in a throwaway Plasma, so they can be checked
# without Plasma installed.
#
#   tools/kde-shoot.sh OUTDIR [dark|light ...]
#
# Runs KWin nested in an Xvfb, with plasmashell on it, in a Fedora container
# (built on first use as neon-doll-kde; KDE_IMAGE_BASE picks another Fedora).
# Everything goes in the way a user would put it in: install.sh copies the
# parts into a home, the global theme is applied with
# plasma-apply-lookandfeel, and Kvantum is set with kvantummanager.
# Writes OUTDIR/plasma-{desktop,kate,widgets,settings}-VARIANT.png.
#
# KDE_SHOOT_LOGS=1 also keeps each run's logs and config in
# OUTDIR/logs-VARIANT/. KDE_SHOOT_PREVIEWS=1 also writes the global themes'
# preview images, which System Settings shows, from the desktop shot into
# kde/look-and-feel/; a run after that shows them on the settings shot.
#
# Needs docker. Everything renders in software; no GPU. KWin needs
# CAP_SYS_NICE, which its binary carries as a file capability.
set -eu

out=$(realpath -m "$1"); shift
[ $# -gt 0 ] || set -- dark light
here=$(cd "$(dirname "$0")" && pwd)
repo=$(dirname "$here")
image=neon-doll-kde
mkdir -p "$out"

if ! docker image inspect $image >/dev/null 2>&1; then
  docker build -q -t $image - >/dev/null <<EOF
FROM ${KDE_IMAGE_BASE:-fedora:44}
RUN dnf -y install --setopt=install_weak_deps=False \
      plasma-workspace plasma-desktop plasma-integration plasma-breeze kwin \
      kactivitymanagerd kvantum konsole kate dolphin systemsettings breeze-icon-theme \
      xorg-x11-server-Xvfb xdotool ImageMagick mesa-dri-drivers git \
      google-noto-sans-fonts google-noto-sans-mono-fonts dbus-daemon procps-ng util-linux \
    && dnf clean all && useradd -m doll
EOF
fi

# A worktree's .git names its git dir by absolute path: mount that there too.
gitdir=$(git -C "$repo" rev-parse --path-format=absolute --git-common-dir)

for variant in "$@"; do
  case $variant in dark|light) ;; *) echo "variant must be dark or light" >&2; exit 2 ;; esac
  docker run --rm --cap-add SYS_NICE -e VARIANT="$variant" -e KDE_SHOOT_LOGS \
    -e HOST_ID="$(id -u):$(id -g)" -v "$repo:/repo:ro" -v "$gitdir:$gitdir:ro" -v "$out:/out" $image sh -eu -c '
mkdir -m777 /tmp/shots
runuser -u doll -- env VARIANT=$VARIANT KDE_SHOOT_LOGS="${KDE_SHOOT_LOGS:-}" dbus-run-session -- sh -eu -c '"'"'
V=$VARIANT; Name=$(echo $V | sed "s/./\U&/")
export LANG=C.UTF-8 HOME=/tmp/home XDG_RUNTIME_DIR=/tmp/run SHELL=/bin/bash
export XDG_CURRENT_DESKTOP=KDE KDE_SESSION_VERSION=6 KDE_FULL_SESSION=true
# Plasma writes a global theme into kdedefaults, a config layer its session
# puts on XDG_CONFIG_DIRS.
export XDG_CONFIG_DIRS=$HOME/.config/kdedefaults:/etc/xdg
mkdir -p $HOME && mkdir -m700 $XDG_RUNTIME_DIR
cfg=$HOME/.config

sh /repo/install.sh kde kvantum konsole kate cursor >/dev/null
QT_QPA_PLATFORM=offscreen plasma-apply-lookandfeel -a io.github.mishan.neon-doll-$V >/tmp/lookandfeel.log 2>&1
QT_QPA_PLATFORM=offscreen kvantummanager --set NeonDoll >/tmp/kvantum.log 2>&1
kwriteconfig6 --file kdeglobals --group General --key font "Noto Sans,10,-1,5,400,0,0,0,0,0,0,0,0,0,0,1"
kwriteconfig6 --file kdeglobals --group General --key fixed "Noto Sans Mono,10,-1,5,400,0,0,0,0,0,0,0,0,0,0,1"

# The wallpaper: graph paper, the page and its 24px grid.
case $V in
  dark)  page="#0f0d14"; grid="rgba(180,140,255,0.09)" ;;
  light) page="#f7f4fa"; grid="rgba(106,63,208,0.07)" ;;
esac
magick -size 24x24 "xc:$page" -fill "$grid" \
  -draw "rectangle 0,0 23,0" -draw "rectangle 0,0 0,23" /tmp/tile.png
magick -size 1280x800 tile:/tmp/tile.png $HOME/paper.png

# Konsole on the Neon Doll profile, with the colors the rest of the repo
# gives a shell; Kate on the Neon Doll color theme.
kwriteconfig6 --file konsolerc --group "Desktop Entry" --key DefaultProfile "Neon Doll $Name.profile"
kwriteconfig6 --file konsolerc --group KonsoleWindow --key ShowMenuBarByDefault true
# Dolphin in its details view, as the COSMIC shot has Files.
kwriteconfig6 --file dolphinrc --group General --key GlobalViewProps true
mkdir -p $HOME/.local/share/dolphin/view_properties/global
printf "[Dolphin]\nViewMode=1\nVersion=4\n" > $HOME/.local/share/dolphin/view_properties/global/.directory
kwriteconfig6 --file katerc --group "KTextEditor Renderer" --key "Color Theme" "Neon Doll $Name"
git config --global --add safe.directory "*"
cat > $HOME/.bashrc <<R
eval "\$(dircolors -b /repo/dircolors/neon-doll)"
PS1="doll@plasma:\w\\\$ "
cd /repo
git -c include.path=/repo/git/neon-doll.gitconfig --no-pager log --oneline --graph --decorate --color -6
ls --color=auto
R

Xvfb :9 -screen 0 1280x800x24 >/dev/null 2>&1 &
sleep 1
DISPLAY=:9 kwin_wayland --x11-display :9 --width 1280 --height 800 --no-lockscreen >/tmp/kwin.log 2>&1 &
for i in $(seq 50); do [ -S $XDG_RUNTIME_DIR/wayland-0 ] && break; sleep 0.2; done
export WAYLAND_DISPLAY=wayland-0 QT_QPA_PLATFORM=wayland
/usr/libexec/kactivitymanagerd >/tmp/kamd.log 2>&1 &
sleep 1
QT_QUICK_BACKEND=software plasmashell >/tmp/plasmashell.log 2>&1 &
sleep 12
plasma-apply-wallpaperimage $HOME/paper.png >/tmp/wallpaper.log 2>&1
sleep 2

# KWin takes its pointer from the Xvfb it runs in: park it on the right
# edge, where it hovers nothing.
shot() {
  DISPLAY=:9 xdotool mousemove 1279 400; sleep 1
  DISPLAY=:9 import -window root /tmp/shots/plasma-$1-$V.png
}

# Lay the windows out side by side in the space the panel leaves, the last
# one focused: arrange CLASS... by resource class, first match of each.
n=0
arrange() {
  cat > /tmp/arrange.js <<J
const area = workspace.clientArea(KWin.PlacementArea, workspace.activeScreen, workspace.currentDesktop);
const classes = "$*".split(" "), gap = 8;
const width = Math.floor((area.width - (classes.length + 1) * gap) / classes.length);
for (const w of workspace.windowList()) {
  const i = classes.findIndex(c => c && (w.resourceClass.includes(c) || w.resourceName.includes(c)));
  if (i < 0 || !w.normalWindow) continue;
  w.frameGeometry = {x: area.x + gap + i * (width + gap), y: area.y + gap,
                     width: width, height: area.height - 2 * gap};
  if (i === classes.length - 1) workspace.activeWindow = w;
  classes[i] = null;
}
J
  n=$((n + 1))
  id=$(gdbus call --session --dest org.kde.KWin --object-path /Scripting \
        --method org.kde.kwin.Scripting.loadScript /tmp/arrange.js arrange$n | tr -dc 0-9)
  gdbus call --session --dest org.kde.KWin --object-path /Scripting/Script$id \
    --method org.kde.kwin.Script.run >/dev/null
  sleep 2
}

dolphin --select /repo/kde >/tmp/dolphin.log 2>&1 &
sleep 4
konsole >/tmp/konsole.log 2>&1 &
sleep 5
arrange org.kde.dolphin org.kde.konsole
sleep 2
shot desktop
pkill -x dolphin || true; pkill -x konsole || true; sleep 2

kate /repo/tools/tokens.py >/tmp/kate.log 2>&1 &
sleep 7
arrange org.kde.kate
shot kate
pkill -x kate || true; sleep 2

kvantumpreview >/tmp/kvantumpreview.log 2>&1 &
sleep 5
arrange kvantumpreview
# Its Containers tab: views, tabs, a table, group boxes, an MDI window.
DISPLAY=:9 xdotool mousemove 750 136 click 1; sleep 1
shot widgets
pkill -x kvantumpreview || true; sleep 2

QT_QUICK_BACKEND=software kcmshell6 kcm_lookandfeel >/tmp/kcmshell.log 2>&1 &
sleep 10
arrange kcmshell
shot settings

if [ -n "${KDE_SHOOT_LOGS:-}" ]; then
  mkdir -p /tmp/shots/logs-$V && cp /tmp/*.log /tmp/*.js /tmp/shots/logs-$V/ && cp -r $cfg /tmp/shots/logs-$V/config
fi
'"'"'
cp -r /tmp/shots/. /out/ && chown -R $HOST_ID /out
'
  for s in desktop kate widgets settings; do echo "$out/plasma-$s-$variant.png"; done
  if [ -n "${KDE_SHOOT_PREVIEWS:-}" ]; then
    previews=$repo/kde/look-and-feel/io.github.mishan.neon-doll-$variant/contents/previews
    mkdir -p "$previews"
    # 16:9, as Plasma lays them out: the top of the desktop, down to the panel.
    magick "$out/plasma-desktop-$variant.png" -gravity south -crop 1280x720+0+0 +repage \
      -strip -quality 90 "$previews/fullscreenpreview.jpg"
    magick "$out/plasma-desktop-$variant.png" -gravity south -crop 1280x720+0+0 +repage \
      -resize 600x337 -strip "$previews/preview.png"
    echo "$previews/"
  fi
done
