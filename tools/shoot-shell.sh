#!/bin/sh
# Screenshot the GNOME Shell theme in a throwaway headless shell, so it can be
# checked without installing it or touching the running session.
#
#   tools/shoot-shell.sh OUTDIR [dark|light] [hearts]
#
# "hearts" runs the Shell on the -Hearts theme (Locate Pointer as a heart);
# the apps keep the regular one.
#
# Everything runs under a scratch HOME, a private session bus and a stand-in
# system bus, so nothing reaches the real dconf, GDM or logind. A small
# extension drives the shell through each surface and saves a PNG per scene,
# plus computed-style probes in OUTDIR/probe.txt.
set -eu

out=$(realpath -m "$1")
variant=${2:-dark}
here=$(cd "$(dirname "$0")" && pwd)
repo=$(dirname "$here")

case $variant in
  dark)  scheme=prefer-dark;  name=Neon-Doll-Dark ;;
  light) scheme=prefer-light; name=Neon-Doll-Light ;;
  *) echo "variant must be dark or light" >&2; exit 2 ;;
esac
shell_name=$name
[ "${3:-}" = hearts ] && shell_name=$name-Hearts

mkdir -p "$out"
tmp=$(mktemp -d /tmp/shoot-shell.XXXXXX)
trap 'kill $(cat "$tmp/sysbus.pid" 2>/dev/null) 2>/dev/null || true; rm -rf "$tmp" 2>/dev/null' EXIT

mkdir -p "$tmp/home/.themes" "$tmp/run"
chmod 700 "$tmp/run"
# Theme the apps in the scenes too, so the shots show the whole desktop: the
# theme dir (Shell and GTK 3, whole, so url()s find their assets), the GTK 4
# stylesheet, and the Text Editor scheme.
# All of them: a -Hearts theme imports its sibling by relative path.
for t in "$repo"/themes/*/; do t=${t%/}; ln -s "$t" "$tmp/home/.themes/${t##*/}"; done
mkdir -p "$tmp/home/.config/gtk-4.0" "$tmp/home/.local/share/gtksourceview-5/styles"
ln -s "$repo/gtk-4.0/gtk.css" "$tmp/home/.config/gtk-4.0/gtk.css"
ln -s "$repo"/gtksourceview/neon-doll-*.xml "$tmp/home/.local/share/gtksourceview-5/styles/"

# Graph paper instead of the stock wallpaper: the page color and its 24px grid.
case $variant in
  dark)  page='#0f0d14'; grid='rgba(180,140,255,0.09)' ;;
  light) page='#f7f4fa'; grid='rgba(106,63,208,0.07)' ;;
esac
# Rendered at screen size: the shell stretches a small tile rather than
# repeating it.
convert -size 24x24 "xc:$page" -fill "$grid" \
  -draw 'rectangle 0,0 23,0' -draw 'rectangle 0,0 0,23' "$tmp/tile.png"
convert -size 1280x800 "tile:$tmp/tile.png" "$tmp/home/paper.png"

# Something to read in Text Editor: a short file from this repo.
cp "$here/check-tokens.py" "$tmp/home/check-tokens.py"

ext="$tmp/home/.local/share/gnome-shell/extensions/shoot@neon-doll"
mkdir -p "$ext"
cat > "$ext/metadata.json" <<'EOF'
{"uuid": "shoot@neon-doll", "name": "shoot", "description": "screenshots", "shell-version": ["51"]}
EOF
cat > "$ext/extension.js" <<'EOF'
import GLib from 'gi://GLib';
import Gio from 'gi://Gio';
import Shell from 'gi://Shell';
import St from 'gi://St';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import * as PopupMenu from 'resource:///org/gnome/shell/ui/popupMenu.js';
import * as ModalDialog from 'resource:///org/gnome/shell/ui/modalDialog.js';
import * as Dialog from 'resource:///org/gnome/shell/ui/dialog.js';
import * as AltTab from 'resource:///org/gnome/shell/ui/altTab.js';
import * as RunDialog from 'resource:///org/gnome/shell/ui/runDialog.js';
import * as Ripples from 'resource:///org/gnome/shell/ui/ripples.js';
import {UnlockDialog} from 'resource:///org/gnome/shell/ui/unlockDialog.js';

Gio._promisify(Shell.Screenshot.prototype, 'screenshot');
const OUT = GLib.getenv('SHOOT_OUT');
const wait = ms => new Promise(r => GLib.timeout_add(GLib.PRIORITY_DEFAULT, ms, () => {
    r();
    return GLib.SOURCE_REMOVE;
}));
const probes = [];

async function shot(name) {
    const file = Gio.File.new_for_path(`${OUT}/${name}.png`);
    const stream = file.replace(null, false, Gio.FileCreateFlags.NONE, null);
    await new Shell.Screenshot().screenshot(false, stream);
    stream.close(null);
}

function probe(label, actor) {
    try {
        const n = actor.get_theme_node();
        const c = x => x.to_string().slice(0, 9);
        const font = n.get_font();
        probes.push(`${label}: bg=${c(n.get_background_color())} fg=${c(n.get_foreground_color())} ` +
            `radius=${n.get_border_radius(St.Corner.TOPLEFT)} ` +
            `border=${n.get_border_width(St.Side.BOTTOM)}/${c(n.get_border_color(St.Side.BOTTOM))} ` +
            `font=${font.get_family()} ${font.get_weight()} ` +
            `transition=${n.get_transition_duration()}`);
    } catch (e) {
        probes.push(`${label}: ${e}`);
    }
}

// Apps started for the switcher can raise a keyring prompt; it isn't a scene.
function dismissDialogs() {
    for (const d of Main.layoutManager.modalDialogGroup.get_children())
        d.close?.();
}

async function scene(name, fn) {
    dismissDialogs();
    try {
        await fn();
    } catch (e) {
        probes.push(`scene ${name} failed: ${e}\n${e.stack}`);
    }
}

async function run() {
    await wait(4000);
    Main.overview.hide();
    await wait(1500);

    await scene('panel', async () => {
        probe('#panel', Main.panel);
        probe('clock', Main.panel.statusArea.dateMenu);
        probe('activities', Main.panel.statusArea.activities);
        await shot('01-desktop');
    });

    await scene('notification', async () => {
        Main.notify('Build finished', 'neon-doll: 3 files changed, 42 insertions(+), 7 deletions(-). The body of a notification is prose, so it stays sans.');
        await wait(1500);
        await shot('02-notification-banner');
        Main.messageTray.bannerBlocked = true;
    });

    await scene('calendar', async () => {
        Main.panel.statusArea.dateMenu.menu.open();
        await wait(800);
        await shot('03-calendar');
        Main.panel.statusArea.dateMenu.menu.close();
        // Clear the banners so they don't cover the scenes that follow.
        for (const source of Main.messageTray.getSources())
            source.destroy();
        await wait(400);
    });

    await scene('quick-settings', async () => {
        const qs = Main.panel.statusArea.quickSettings;
        qs.menu.open();
        await wait(800);
        probe('quick-settings', qs.menu.box);
        await shot('04-quick-settings');
        // Open the first toggle that has a menu, to show the submenu.
        const grid = qs.menu._grid;
        const withMenu = grid?.get_children().find(c => c.menu && c.visible);
        if (withMenu) {
            withMenu.checked = true;
            qs.menu._setActiveMenu?.(withMenu.menu);
            withMenu.menu.open();
            await wait(800);
            await shot('05-quick-settings-menu');
        }
        qs.menu.close();
        await wait(400);
    });

    await scene('popup-menu', async () => {
        const source = Main.panel.statusArea.activities;
        const menu = new PopupMenu.PopupMenu(source, 0.0, St.Side.TOP);
        Main.uiGroup.add_child(menu.actor);
        menu.addMenuItem(new PopupMenu.PopupMenuItem('Open'));
        const hovered = new PopupMenu.PopupMenuItem('Hovered item');
        menu.addMenuItem(hovered);
        const checked = new PopupMenu.PopupMenuItem('Checked item');
        checked.setOrnament(PopupMenu.Ornament.CHECK);
        menu.addMenuItem(checked);
        menu.addMenuItem(new PopupMenu.PopupSwitchMenuItem('A switch, on', true));
        menu.addMenuItem(new PopupMenu.PopupSwitchMenuItem('A switch, off', false));
        menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());
        const sub = new PopupMenu.PopupSubMenuMenuItem('Submenu', true);
        sub.icon.icon_name = 'folder-symbolic';
        sub.menu.addMenuItem(new PopupMenu.PopupMenuItem('Inside'));
        sub.menu.addMenuItem(new PopupMenu.PopupMenuItem('Also inside'));
        menu.addMenuItem(sub);
        const off = new PopupMenu.PopupMenuItem('Insensitive');
        off.setSensitive(false);
        menu.addMenuItem(off);
        menu.open();
        sub.setSubmenuShown(true);
        hovered.add_style_pseudo_class('hover');
        await wait(800);
        probe('popup-menu-content', menu.box.get_parent());
        probe('popup-menu-item:hover', hovered);
        await shot('06-popup-menu');
        menu.close();
        await wait(300);
        menu.destroy();
    });

    // Every switch state at once, pinned with pseudo-classes.
    await scene('switches', async () => {
        const source = Main.panel.statusArea.activities;
        const menu = new PopupMenu.PopupMenu(source, 0.0, St.Side.TOP);
        Main.uiGroup.add_child(menu.actor);
        const states = [
            ['off', false, null], ['on', true, null],
            ['off, hover', false, 'hover'], ['on, hover', true, 'hover'],
            ['off, disabled', false, 'off'], ['on, disabled', true, 'off'],
        ];
        for (const [label, on, how] of states) {
            const item = new PopupMenu.PopupSwitchMenuItem(label, on);
            menu.addMenuItem(item);
            if (how === 'hover')
                item._switch.add_style_pseudo_class('hover');
            else if (how === 'off')
                item.setSensitive(false);
        }
        menu.open();
        await wait(800);
        await shot('06b-switches');
        menu.close();
        await wait(300);
        menu.destroy();
    });

    // Locate Pointer's ripple, caught while it grows. The headless pointer
    // sits nowhere useful, so play the same ripples at the screen's center.
    await scene('locate-pointer', async () => {
        const ripples = new Ripples.Ripples(0.5, 0.5, 'ripple-pointer-location');
        ripples.addTo(Main.uiGroup);
        ripples.playAnimation(global.screen_width / 2, global.screen_height / 2);
        await wait(250);
        await shot('07b-locate-pointer');
        await wait(1200);
    });

    await scene('osd', async () => {
        Main.osdWindowManager.showAll(Gio.ThemedIcon.new('audio-volume-medium-symbolic'), 'Speakers', 0.6, 1);
        await wait(700);
        await shot('07-osd');
        Main.osdWindowManager.hideAll();
        await wait(400);
    });

    await scene('overview', async () => {
        // A window on a second workspace makes the shell show the thumbnails.
        global.get_window_actors()[0]?.meta_window.change_workspace_by_index(1, true);
        Main.overview.show();
        await wait(1500);
        probe('dash', Main.overview.dash._background);
        await shot('08-overview');
        Main.overview.dash.showAppsButton.checked = true;
        await wait(1500);
        await shot('09-app-grid');
        Main.overview.dash.showAppsButton.checked = false;
        await wait(800);
        Main.overview.searchEntry.grab_key_focus();
        Main.overview.searchEntry.set_text('calc');
        await wait(2000);
        dismissDialogs();
        await wait(500);
        probe('search-entry', Main.overview.searchEntry);
        await shot('10-search');
        Main.overview.searchEntry.set_text('');
        Main.overview.hide();
        await wait(1500);
    });

    await scene('app-switcher', async () => {
        const popup = new AltTab.AppSwitcherPopup();
        if (popup.show(false, 'switch-applications', 0)) {
            await wait(600);
            await shot('11-app-switcher');
            popup.destroy();
        } else {
            probes.push('app switcher: no windows');
        }
        await wait(400);
    });

    await scene('modal', async () => {
        const dialog = new ModalDialog.ModalDialog();
        dialog.contentLayout.add_child(new Dialog.MessageDialogContent({
            title: 'Log Out',
            description: 'You will be logged out in 60 seconds. Unsaved work in open apps may be lost.',
        }));
        dialog.addButton({label: 'Cancel', action: () => dialog.close(), key: 0xff1b});
        dialog.addButton({label: 'Log Out', action: () => dialog.close(), default: true});
        dialog.open();
        await wait(1000);
        await shot('12-modal-dialog');
        dialog.close();
        await wait(600);
    });

    await scene('run-dialog', async () => {
        const rd = new RunDialog.RunDialog();
        rd.open();
        await wait(1000);
        probe('run-dialog entry', rd.contentLayout.get_children().find(c => c instanceof St.Entry) ?? rd);
        await shot('13-run-dialog');
        rd.close();
        await wait(600);
    });

    // The GDM client inside only ever reaches the stand-in system bus.
    await scene('lock', async () => {
        const dialog = new UnlockDialog(Main.layoutManager.uiGroup);
        dialog.open();
        await wait(1500);
        await shot('14-lock-clock');
        dialog.activate();
        await wait(2000);
        await shot('15-lock-prompt');
        dialog.popModal();
        dialog.destroy();
    });

    Gio.File.new_for_path(`${OUT}/probe.txt`).replace_contents(
        new TextEncoder().encode(`${probes.join('\n')}\n`), null, false, Gio.FileCreateFlags.NONE, null);
    Gio.File.new_for_path(`${OUT}/.done`).replace_contents(new Uint8Array(), null, false, Gio.FileCreateFlags.NONE, null);
}

export default class Shoot extends Extension {
    enable() {
        run().catch(e => logError(e));
    }

    disable() {}
}
EOF

cat > "$tmp/sysbus.conf" <<EOF
<!DOCTYPE busconfig PUBLIC "-//freedesktop//DTD D-Bus Bus Configuration 1.0//EN" "http://www.freedesktop.org/standards/dbus/1.0/busconfig.dtd">
<busconfig>
  <type>system</type>
  <listen>unix:path=$tmp/run/system_bus_socket</listen>
  <auth>EXTERNAL</auth>
  <policy context="default"><allow user="*"/><allow send_destination="*" eavesdrop="true"/><allow eavesdrop="true"/><allow own="*"/></policy>
</busconfig>
EOF
dbus-daemon --config-file="$tmp/sysbus.conf" --fork --print-pid > "$tmp/sysbus.pid"

rm -f "$out/.done"
env -i PATH=/usr/bin:/bin LANG=C.UTF-8 \
  HOME="$tmp/home" XDG_CONFIG_HOME="$tmp/home/.config" \
  XDG_DATA_HOME="$tmp/home/.local/share" XDG_CACHE_HOME="$tmp/home/.cache" \
  XDG_RUNTIME_DIR="$tmp/run" SHOOT_OUT="$out" \
  DBUS_SYSTEM_BUS_ADDRESS="unix:path=$tmp/run/system_bus_socket" \
  dbus-run-session -- sh -c "
    gsettings set org.gnome.shell enabled-extensions \"['user-theme@gnome-shell-extensions.gcampax.github.com', 'shoot@neon-doll']\"
    gsettings set org.gnome.shell welcome-dialog-last-shown-version '999'
    gsettings set org.gnome.shell.extensions.user-theme name '$shell_name'
    gsettings set org.gnome.desktop.interface color-scheme '$scheme'
    gsettings set org.gnome.desktop.interface gtk-theme '$name'
    gsettings set org.gnome.desktop.background picture-uri 'file://$tmp/home/paper.png'
    gsettings set org.gnome.desktop.background picture-uri-dark 'file://$tmp/home/paper.png'
    gsettings set org.gnome.desktop.background picture-options 'zoom'
    gsettings set org.gnome.TextEditor style-scheme 'neon-doll-$variant'
    gsettings set org.gnome.TextEditor restore-session false
    gnome-shell --headless --virtual-monitor 1280x800 --wayland --no-x11 --wayland-display=shoot-0 &
    shell=\$!
    sleep 3
    WAYLAND_DISPLAY=shoot-0 gnome-calculator >/dev/null 2>&1 &
    WAYLAND_DISPLAY=shoot-0 gnome-text-editor --standalone '$tmp/home/check-tokens.py' >/dev/null 2>&1 &
    for i in \$(seq 90); do [ -e '$out/.done' ] && break; sleep 1; done
    kill \$shell
  " > "$out/shell.log" 2>&1 || true

rm -f "$out/.done"
grep -iE 'JS ERROR|theme|stylesheet|St-WARNING|css' "$out/shell.log" | grep -v dbus-daemon || true
ls "$out"
