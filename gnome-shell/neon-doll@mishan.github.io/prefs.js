import Adw from 'gi://Adw';
import Gio from 'gi://Gio';

import {ExtensionPreferences} from 'resource:///org/gnome/Shell/Extensions/js/extensions/prefs.js';

export default class NeonDollPreferences extends ExtensionPreferences {
    fillPreferencesWindow(window) {
        const row = new Adw.SwitchRow({
            title: 'A heart for Locate Pointer',
            subtitle: 'Instead of a ring',
        });
        this.getSettings().bind('hearts', row, 'active', Gio.SettingsBindFlags.DEFAULT);
        const group = new Adw.PreferencesGroup();
        group.add(row);
        const page = new Adw.PreferencesPage();
        page.add(group);
        window.add(page);
    }
}
