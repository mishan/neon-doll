import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import St from 'gi://St';

import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';

// Where User Themes looks for a theme, in its order.
const THEME_DIRS = [
    GLib.build_filenamev([GLib.get_home_dir(), '.themes']),
    GLib.build_filenamev([GLib.get_user_data_dir(), 'themes']),
    ...GLib.get_system_data_dirs().map(dir => GLib.build_filenamev([dir, 'themes'])),
];

// Neon Doll's Shell stylesheet laid over the Shell's own, swapped when the
// Shell swaps its own: with the style it picks for the system's light or
// dark preference, and for High Contrast, none, leaving the Shell's
// high-contrast theme.
export default class NeonDoll extends Extension {
    enable() {
        this._settings = this.getSettings();
        this._settings.connectObject('changed::hearts', () => this._load(), this);
        St.Settings.get().connectObject(
            'notify::color-scheme', () => this._load(),
            'notify::high-contrast', () => this._load(), this);
        this._load();
    }

    disable() {
        St.Settings.get().disconnectObject(this);
        this._settings.disconnectObject(this);
        this._settings = null;
        Main.setThemeStylesheet(null);
        Main.loadTheme();
    }

    _stylesheet() {
        if (St.Settings.get().high_contrast)
            return null;
        const name = `Neon-Doll${Main.getStyleVariant() === 'light' ? '' : '-dark'}` +
            `${this._settings.get_boolean('hearts') ? '-Hearts' : ''}`;
        return THEME_DIRS
            .map(dir => GLib.build_filenamev([dir, name, 'gnome-shell', 'gnome-shell.css']))
            .find(path => Gio.File.new_for_path(path).query_exists(null)) ?? null;
    }

    _load() {
        Main.setThemeStylesheet(this._stylesheet());
        Main.loadTheme();
    }
}
