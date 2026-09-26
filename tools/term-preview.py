#!/usr/bin/env python3
"""Render a command in a VTE terminal (Tilix's engine) with a Tilix scheme.

    tools/term-preview.py tilix/neon-doll-dark.json 'ls -l --color=always' [TYPE]

TYPE, if given, is typed into the terminal three seconds in, as if at the
keyboard: to show an interactive shell's highlighting as you type.

Run under tools/term-shoot.sh to get a screenshot. The command runs in
bash with the caller's environment, so set LS_COLORS and cwd before.
"""

import json
import sys

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("Vte", "2.91")
from gi.repository import Gdk, GLib, Gtk, Pango, Vte  # noqa: E402


def rgba(hex_):
    c = Gdk.RGBA()
    c.parse(hex_)
    return c


scheme = json.load(open(sys.argv[1]))
command = sys.argv[2]

term = Vte.Terminal()
term.set_font(Pango.FontDescription("Monospace 11"))
term.set_colors(rgba(scheme["foreground-color"]), rgba(scheme["background-color"]),
                [rgba(c) for c in scheme["palette"]])
term.set_color_cursor(rgba(scheme["cursor-background-color"]))
term.set_color_bold(rgba(scheme["bold-color"]))
term.set_size(72, 24)
term.spawn_async(Vte.PtyFlags.DEFAULT, None, ["/bin/bash", "--norc", "-c", command + "; sleep 60"],
                 None, GLib.SpawnFlags.DEFAULT, None, None, -1, None, None)

if len(sys.argv) > 3:
    typed = sys.argv[3].encode()
    GLib.timeout_add(3000, lambda: term.feed_child(typed) and False)

win = Gtk.Window(title=scheme["name"])
win.add(term)
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
