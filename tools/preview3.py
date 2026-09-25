#!/usr/bin/env python3
"""A widget sampler for the GTK 3 theme in gtk-3.0/.

Unlike tools/preview.py it loads nothing itself: GTK 3 reads a theme by
name, so run it with GTK_THEME=Neon-Doll-Light (or Neon-Doll-Light:dark,
or Neon-Doll-Dark) and the theme somewhere GTK looks for one. tools/shoot3.sh
does that on a throwaway X server.

    tools/preview3.py [--menu] [--context] [--dialog] [--states]

--states pins hover on a few widgets and puts keyboard focus on a button,
since a headless X server has no pointer to rest anywhere.
"""

import sys

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, Gio, GLib, Gtk  # noqa: E402


def sidebar():
    lb = Gtk.ListBox()
    for icon, name in [
        ("user-home-symbolic", "home"),
        ("folder-documents-symbolic", "log"),
        ("folder-pictures-symbolic", "photos"),
        ("folder-music-symbolic", "projects"),
        ("user-trash-symbolic", "trash"),
    ]:
        box = Gtk.Box(spacing=10, margin=8)
        box.pack_start(Gtk.Image(icon_name=icon), False, False, 0)
        box.pack_start(Gtk.Label(label=name, xalign=0), True, True, 0)
        lb.add(box)
    lb.select_row(lb.get_row_at_index(2))
    hover(lb.get_row_at_index(3))
    sw = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.NEVER, width_request=220)
    sw.add(lb)
    sw.get_style_context().add_class("sidebar")
    return sw


HOVER = []


def hover(w):
    HOVER.append(w)
    return w


def buttons():
    box = Gtk.Box(spacing=8)
    box.pack_start(hover(Gtk.Button(label="Cancel")), False, False, 0)
    b = hover(Gtk.Button(label="Save contact"))
    b.get_style_context().add_class("suggested-action")
    box.pack_start(b, False, False, 0)
    b = Gtk.Button(label="Delete")
    b.get_style_context().add_class("destructive-action")
    box.pack_start(b, False, False, 0)
    b = hover(Gtk.Button(label="Flat"))
    b.get_style_context().add_class("flat")
    box.pack_start(b, False, False, 0)
    t = Gtk.ToggleButton(label="Toggled", active=True)
    box.pack_start(t, False, False, 0)
    box.pack_start(hover(Gtk.LinkButton(uri="https://example.org", label="example.org")), False, False, 0)
    box.focus_button = t
    return box


def toggles():
    box = Gtk.Box(spacing=12)
    box.pack_start(Gtk.CheckButton(label="check", active=True), False, False, 0)
    box.pack_start(hover(Gtk.CheckButton(label="unchecked")), False, False, 0)
    r1 = Gtk.RadioButton(label="radio")
    r2 = Gtk.RadioButton(label="other", group=r1)
    box.pack_start(r1, False, False, 0)
    box.pack_start(r2, False, False, 0)
    # off, on, off hovered, on hovered, off disabled, on disabled
    for active, hovered, sensitive in [(False, False, True), (True, False, True),
                                       (False, True, True), (True, True, True),
                                       (False, False, False), (True, False, False)]:
        sw = Gtk.Switch(active=active, sensitive=sensitive, valign=Gtk.Align.CENTER)
        box.pack_start(hover(sw) if hovered else sw, False, False, 0)
    box.pack_start(Gtk.CheckButton(label="disabled", sensitive=False), False, False, 0)
    return box


def ranges():
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    box.pack_start(Gtk.Scale(adjustment=Gtk.Adjustment(value=40, upper=100), draw_value=False), False, False, 0)
    box.pack_start(Gtk.ProgressBar(fraction=0.62), False, False, 0)
    row = Gtk.Box(spacing=8)
    row.pack_start(Gtk.Entry(placeholder_text="grep -i"), True, True, 0)
    e = Gtk.Entry(text="focused field")
    row.pack_start(e, True, True, 0)
    row.pack_start(Gtk.SpinButton(adjustment=Gtk.Adjustment(value=24, upper=100, step_increment=1)), False, False, 0)
    combo = Gtk.ComboBoxText()
    for t in ("Neon Doll", "Adwaita"):
        combo.append_text(t)
    combo.set_active(0)
    row.pack_start(combo, False, False, 0)
    box.pack_start(row, False, False, 0)
    return box, e


def group():
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    h = Gtk.Label(label="Contact", xalign=0)
    h.get_style_context().add_class("heading")
    box.pack_start(h, False, False, 0)
    lb = Gtk.ListBox(selection_mode=Gtk.SelectionMode.NONE)
    lb.get_style_context().add_class("frame")
    for title, sub, widget in [
        ("Email", "doll@example.org", Gtk.Image(icon_name="go-next-symbolic")),
        ("Show QR code", "On the contact page", Gtk.Switch(active=True, valign=Gtk.Align.CENTER)),
        ("Level", "levelbar", Gtk.LevelBar(value=0.7, width_request=160, valign=Gtk.Align.CENTER)),
    ]:
        row = Gtk.Box(spacing=12, margin=10)
        text = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        text.pack_start(Gtk.Label(label=title, xalign=0), False, False, 0)
        s = Gtk.Label(label=sub, xalign=0)
        s.get_style_context().add_class("dim-label")
        text.pack_start(s, False, False, 0)
        row.pack_start(text, True, True, 0)
        row.pack_start(widget, False, False, 0)
        lb.add(row)
    hover(lb.get_row_at_index(0))
    box.pack_start(lb, False, False, 0)
    return box


def tree():
    store = Gtk.ListStore(str, str, str)
    for row in [
        ("drwxr-xr-x", "photos/", "4.0K"),
        ("-rw-r--r--", "log.md", "12K"),
        ("-rw-r--r--", "card.php", "3.1K"),
        ("-rw-r--r--", "index.md", "880"),
        ("-rw-r--r--", "robots.txt", "64"),
        ("-rw-r--r--", "sitemap.xml", "2.2K"),
        ("drwxr-xr-x", "tools/", "4.0K"),
    ]:
        store.append(row)
    tv = Gtk.TreeView(model=store)
    for i, title in enumerate(("mode", "name", "size")):
        tv.append_column(Gtk.TreeViewColumn(title, Gtk.CellRendererText(), text=i))
    tv.get_selection().select_path(Gtk.TreePath(1))
    sw = Gtk.ScrolledWindow(height_request=150, overlay_scrolling=False)
    sw.get_style_context().add_class("frame")
    sw.add(tv)
    return sw


def text():
    buf = Gtk.TextBuffer()
    buf.set_text(
        "A man page rendered in a terminal that never existed.\n"
        "Mono carries the chrome; sans carries what you read.\n"
    )
    buf.select_range(buf.get_iter_at_offset(2), buf.get_iter_at_offset(22))
    tv = Gtk.TextView(buffer=buf, top_margin=8, bottom_margin=8, left_margin=10, right_margin=10)
    frame = Gtk.Frame()
    frame.add(tv)
    return frame


def header(win):
    hb = Gtk.HeaderBar(title="photos", subtitle="~/photos/2026", show_close_button=True)
    hb.pack_start(Gtk.Button.new_from_icon_name("go-previous-symbolic", Gtk.IconSize.BUTTON))
    menu = Gio.Menu()
    menu.append("New window", "app.new")
    menu.append("Preferences", "app.prefs")
    sec = Gio.Menu()
    sec.append("Keyboard shortcuts", "app.keys")
    sec.append("About", "app.about")
    menu.append_section(None, sec)
    mb = Gtk.MenuButton(menu_model=menu, image=Gtk.Image(icon_name="open-menu-symbolic"))
    win.menu_button = mb
    hb.pack_end(mb)
    hb.pack_end(Gtk.Button.new_from_icon_name("system-search-symbolic", Gtk.IconSize.BUTTON))
    return hb


def menubar(win):
    mb = Gtk.MenuBar()
    for name in ("File", "Edit", "View", "Help"):
        item = Gtk.MenuItem(label=name)
        sub = Gtk.Menu()
        for label in ("Open…", "Save", "Save as…"):
            sub.append(Gtk.MenuItem(label=label))
        sub.append(Gtk.SeparatorMenuItem())
        sub.append(Gtk.CheckMenuItem(label="Show hidden", active=True))
        dis = Gtk.MenuItem(label="Revert", sensitive=False)
        sub.append(dis)
        sub.append(Gtk.MenuItem(label="Quit"))
        sub.show_all()
        item.set_submenu(sub)
        mb.append(item)
        if name == "File":
            win.file_item = item
    return mb


def content(win):
    nb = Gtk.Notebook()
    for t in ("index.md", "log.md", "card.php"):
        tab = Gtk.Box(spacing=6)
        tab.pack_start(Gtk.Label(label=t), True, True, 0)
        close = Gtk.Button.new_from_icon_name("window-close-symbolic", Gtk.IconSize.MENU)
        close.get_style_context().add_class("flat")
        tab.pack_start(close, False, False, 0)
        tab.show_all()
        nb.append_page(Gtk.Label(label=t), tab)

    col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16, margin=24)
    title = Gtk.Label(label="NEON-DOLL(7)", xalign=0)
    title.get_style_context().add_class("title-1")
    col.pack_start(title, False, False, 0)
    syn = Gtk.Label(label="SYNOPSIS", xalign=0)
    syn.get_style_context().add_class("heading")
    syn.get_style_context().add_class("dim-label")
    col.pack_start(syn, False, False, 0)
    bb = buttons()
    win.focus_button = bb.focus_button
    col.pack_start(bb, False, False, 0)
    col.pack_start(toggles(), False, False, 0)
    r, entry = ranges()
    col.pack_start(r, False, False, 0)
    col.pack_start(group(), False, False, 0)
    col.pack_start(tree(), False, False, 0)
    col.pack_start(text(), False, False, 0)
    win.focus_target = entry

    ib = Gtk.InfoBar(message_type=Gtk.MessageType.WARNING, show_close_button=True)
    ib.get_content_area().add(Gtk.Label(label="The draft has not been saved."))
    ib.add_button("Save", 1)

    scroller = Gtk.ScrolledWindow(vexpand=True)
    scroller.add(col)
    outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    outer.pack_start(nb, False, False, 0)
    outer.pack_start(ib, False, False, 0)
    outer.pack_start(scroller, True, True, 0)
    win.notebook = nb
    return outer


def on_activate(app):
    for name in ("new", "prefs", "keys", "about"):
        app.add_action(Gio.SimpleAction(name=name))
    win = Gtk.ApplicationWindow(application=app, default_width=1180, default_height=1000)
    win.set_titlebar(header(win))
    paned = Gtk.Paned()
    paned.pack1(sidebar(), False, False)
    right = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    right.pack_start(menubar(win), False, False, 0)
    right.pack_start(content(win), True, True, 0)
    paned.pack2(right, True, False)
    win.add(paned)
    win.show_all()

    def later():
        win.notebook.set_current_page(1)
        win.present()
        win.focus_target.grab_focus()
        win.focus_target.select_region(0, 7)
        if "--states" in sys.argv:
            for w in HOVER:
                w.set_state_flags(Gtk.StateFlags.PRELIGHT, False)
            win.focus_button.grab_focus()
            win.set_focus_visible(True)
        if "--menu" in sys.argv:
            win.menu_button.set_active(True)
        if "--context" in sys.argv:
            win.file_item.get_submenu().popup_at_widget(
                win.file_item, Gdk.Gravity.SOUTH_WEST, Gdk.Gravity.NORTH_WEST, None)
            win.file_item.get_submenu().select_first(False)
        if "--dialog" in sys.argv:
            d = Gtk.MessageDialog(transient_for=win, modal=True, message_type=Gtk.MessageType.QUESTION,
                                  text="Discard changes?",
                                  secondary_text="The draft of log/2026-09-25.md has not been saved.")
            d.add_button("Cancel", Gtk.ResponseType.CANCEL)
            d.add_button("Discard", Gtk.ResponseType.REJECT).get_style_context().add_class("destructive-action")
            d.add_button("Save", Gtk.ResponseType.ACCEPT).get_style_context().add_class("suggested-action")
            d.show_all()
        return False

    GLib.timeout_add(300, later)


app = Gtk.Application(flags=Gio.ApplicationFlags.NON_UNIQUE)
app.connect("activate", on_activate)
app.run([sys.argv[0]])
