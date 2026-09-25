#!/usr/bin/env python3
"""A widget sampler for gtk-4.0/gtk.css.

Loads the stylesheet at user priority — where ~/.config/gtk-4.0/gtk.css would
sit — so it can be looked at without installing it. Run it directly on the
desktop, or under Broadway with tools/shoot.sh to get screenshots.

    tools/preview.py [--menu] [--dialog] [--light]
"""

import sys
from pathlib import Path

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gdk, Gio, GLib, Gtk  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CSS = [ROOT / "gtk-4.0" / "gtk.css"]


def load_css():
    for i, path in enumerate(CSS):
        provider = Gtk.CssProvider()
        provider.connect(
            "parsing-error",
            lambda _p, section, err: print(f"{section.to_string()}: {err.message}", file=sys.stderr),
        )
        # A provider added by hand does not follow the app's color scheme the
        # way the installed ~/.config/gtk-4.0/gtk.css does, so pin it.
        provider.props.prefers_color_scheme = (
            Gtk.InterfaceColorScheme.LIGHT if "--light" in sys.argv else Gtk.InterfaceColorScheme.DARK)
        provider.load_from_path(str(path))
        # Later files sit one step higher, so the spike wins over the theme.
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_USER + i,
        )


def sidebar():
    lb = Gtk.ListBox(css_classes=["navigation-sidebar"])
    for icon, name in [
        ("user-home-symbolic", "home"),
        ("folder-documents-symbolic", "log"),
        ("folder-pictures-symbolic", "photos"),
        ("folder-music-symbolic", "projects"),
        ("user-trash-symbolic", "trash"),
    ]:
        box = Gtk.Box(spacing=10, margin_start=6, margin_end=6, margin_top=6, margin_bottom=6)
        box.append(Gtk.Image(icon_name=icon))
        box.append(Gtk.Label(label=name, xalign=0))
        lb.append(box)
    lb.select_row(lb.get_row_at_index(2))

    header = Adw.HeaderBar()
    header.set_title_widget(Adw.WindowTitle(title="neon-doll(7)"))
    tv = Adw.ToolbarView()
    tv.add_top_bar(header)
    tv.set_content(lb)
    return Adw.NavigationPage(title="sidebar", child=tv)


def buttons():
    box = Gtk.Box(spacing=8)
    box.append(Gtk.Button(label="Cancel"))
    box.append(Gtk.Button(label="Save contact", css_classes=["suggested-action"]))
    box.append(Gtk.Button(label="Delete", css_classes=["destructive-action"]))
    box.append(Gtk.Button(label="Flat", css_classes=["flat"]))
    box.append(Gtk.ToggleButton(label="Toggled", active=True))
    box.append(Gtk.LinkButton(uri="https://example.org", label="example.org"))
    return box


def toggles():
    box = Gtk.Box(spacing=16)
    box.append(Gtk.CheckButton(label="check", active=True))
    box.append(Gtk.CheckButton(label="unchecked"))
    r1 = Gtk.CheckButton(label="radio", active=True)
    r2 = Gtk.CheckButton(label="other", group=r1)
    box.append(r1)
    box.append(r2)
    box.append(Gtk.Switch(active=True, valign=Gtk.Align.CENTER))
    box.append(Gtk.Switch(active=False, valign=Gtk.Align.CENTER))
    box.append(Gtk.CheckButton(label="disabled", sensitive=False))
    return box


def ranges():
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    box.append(Gtk.Scale(adjustment=Gtk.Adjustment(value=40, upper=100), hexpand=True))
    pb = Gtk.ProgressBar(fraction=0.62)
    box.append(pb)
    row = Gtk.Box(spacing=8)
    row.append(Gtk.Entry(placeholder_text="grep -i", hexpand=True))
    e = Gtk.Entry(text="focused field", hexpand=True)
    row.append(e)
    row.append(Gtk.SpinButton(adjustment=Gtk.Adjustment(value=24, upper=100, step_increment=1)))
    box.append(row)
    return box, e


def group():
    g = Adw.PreferencesGroup(title="Contact", description="How the card reaches people")
    r = Adw.ActionRow(title="Email", subtitle="doll@example.org", activatable=True)
    r.add_suffix(Gtk.Image(icon_name="go-next-symbolic"))
    g.add(r)
    g.add(Adw.SwitchRow(title="Show QR code", subtitle="On the contact page", active=True))
    g.add(Adw.EntryRow(title="Display name", text="Neon Doll"))
    g.add(Adw.ComboRow(title="Theme", model=Gtk.StringList.new(["Neon Doll", "Adwaita"])))
    exp = Adw.ExpanderRow(title="Advanced", subtitle="Things you rarely touch")
    exp.add_row(Adw.ActionRow(title="Nested row"))
    g.add(exp)
    return g


def text():
    buf = Gtk.TextBuffer()
    buf.set_text(
        "A man page rendered in a terminal that never existed.\n"
        "Mono carries the chrome; sans carries what you read.\n"
    )
    buf.select_range(buf.get_iter_at_offset(2), buf.get_iter_at_offset(22))
    tv = Gtk.TextView(buffer=buf, top_margin=8, bottom_margin=8, left_margin=10, right_margin=10)
    frame = Gtk.Frame(child=tv)
    return frame, tv


def content(win):
    header = Adw.HeaderBar()
    header.set_title_widget(Adw.WindowTitle(title="photos", subtitle="~/photos/2026"))
    header.pack_start(Gtk.Button(icon_name="go-previous-symbolic"))
    menu = Gio.Menu()
    menu.append("New window", "app.new")
    menu.append("Preferences", "app.prefs")
    sec = Gio.Menu()
    sec.append("Keyboard shortcuts", "app.keys")
    sec.append("About", "app.about")
    menu.append_section(None, sec)
    mb = Gtk.MenuButton(icon_name="open-menu-symbolic", menu_model=menu)
    win.menu_button = mb
    header.pack_end(mb)
    header.pack_end(Gtk.Button(icon_name="system-search-symbolic"))

    tabs = Adw.TabView()
    for t in ("index.md", "log.md", "card.php"):
        tabs.append(Gtk.Label(label=t)).set_title(t)
    tabbar = Adw.TabBar(view=tabs, autohide=False)
    tabs.set_selected_page(tabs.get_nth_page(1))

    col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18,
                  margin_top=18, margin_bottom=18, margin_start=24, margin_end=24)
    title = Gtk.Label(label="NEON-DOLL(7)", xalign=0, css_classes=["title-1"])
    col.append(title)
    col.append(Gtk.Label(label="SYNOPSIS", xalign=0, css_classes=["heading", "dim-label"]))
    col.append(buttons())
    col.append(toggles())
    r, entry = ranges()
    col.append(r)
    col.append(group())
    tframe, tv = text()
    col.append(tframe)
    win.focus_target = entry

    scroller = Gtk.ScrolledWindow(child=Adw.Clamp(maximum_size=760, child=col), vexpand=True)
    tv_ = Adw.ToolbarView()
    tv_.add_top_bar(header)
    tv_.add_top_bar(tabbar)
    tv_.set_content(scroller)
    overlay = Adw.ToastOverlay(child=tv_)
    overlay.add_toast(Adw.Toast(title="Copied to clipboard", timeout=0))
    return Adw.NavigationPage(title="content", child=overlay)


def on_activate(app):
    load_css()
    for name in ("new", "prefs", "keys", "about"):
        app.add_action(Gio.SimpleAction(name=name))
    win = Adw.ApplicationWindow(application=app, default_width=1180, default_height=980)
    split = Adw.NavigationSplitView(sidebar=sidebar(), content=content(win), min_sidebar_width=220)
    win.set_content(split)
    win.present()

    def later():
        win.focus_target.grab_focus()
        if "--menu" in sys.argv:
            win.menu_button.popup()
        if "--dialog" in sys.argv:
            d = Adw.AlertDialog(heading="Discard changes?",
                                body="The draft of log/2026-09-25.md has not been saved.")
            d.add_response("cancel", "Cancel")
            d.add_response("discard", "Discard")
            d.add_response("save", "Save")
            d.set_response_appearance("discard", Adw.ResponseAppearance.DESTRUCTIVE)
            d.set_response_appearance("save", Adw.ResponseAppearance.SUGGESTED)
            d.present(win)
        return False

    GLib.timeout_add(300, later)


app = Adw.Application(application_id="io.github.mishan.NeonDoll.Preview",
                      flags=Gio.ApplicationFlags.NON_UNIQUE)
Adw.StyleManager.get_default().set_color_scheme(
    Adw.ColorScheme.FORCE_LIGHT if "--light" in sys.argv else Adw.ColorScheme.FORCE_DARK)
app.connect("activate", on_activate)
app.run([sys.argv[0]])
