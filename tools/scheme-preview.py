#!/usr/bin/env python3
"""Show a Neon Doll GtkSourceView scheme on a code sample and a diff, loaded
straight from gtksourceview/ in this repo, without installing anything.

    tools/scheme-preview.py [dark|light]
    tools/scheme-shoot.sh out.png gsv [dark|light]    # the same, screenshotted

In the code view the search hit inside foreach (...) is selected, as the
match under the cursor is after a search; the other hits are highlighted, the
cursor's line is the current line, and the cursor sits against the closing
bracket, so the bracket pair is matched.
"""
import os
import sys

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
gi.require_version("GtkSource", "5")
from gi.repository import Gdk, GLib, Gtk, GtkSource  # noqa: E402

SCHEMES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "gtksourceview")

CODE = """<?php
// four token colors, three already in the palette
namespace Site\\Block;

final class Listing implements Block
{
    private const MODE = 'drwxr-xr-x';

    /** @param list<Row> $rows the entries, already sorted */
    public function render(array $rows, int $width = 80): string
    {
        $out = [];
        foreach ($rows as $row) {
            $out[] = sprintf("%s %4d %s\\n", self::MODE, $row->size, $row->name);
        }
        return '<ul class="ls">' . implode('', $out) . '</ul>'; // TODO: escape
    }
}
"""

DIFF = """diff --git a/src/Site/Block/Listing.php b/src/Site/Block/Listing.php
--- a/src/Site/Block/Listing.php
+++ b/src/Site/Block/Listing.php
@@ -18,7 +18,7 @@ final class Listing implements Block
     public function render(): string
     {
-        return '<ul>' . $rows . '</ul>';
+        return '<ul class="ls">' . $rows . '</ul>';
     }
 }
"""


def make_view(text, lang_id, scheme):
    lang = GtkSource.LanguageManager.get_default().get_language(lang_id)
    buf = GtkSource.Buffer(language=lang, style_scheme=scheme)
    buf.set_text(text)
    buf.set_highlight_matching_brackets(True)
    view = GtkSource.View(buffer=buf, monospace=True, show_line_numbers=True,
                          highlight_current_line=True, show_right_margin=True,
                          right_margin_position=80, top_margin=6, bottom_margin=6,
                          vexpand=True)
    return buf, view


def main():
    variant = sys.argv[1] if len(sys.argv) > 1 else "dark"
    mgr = GtkSource.StyleSchemeManager()
    mgr.set_search_path([SCHEMES])
    scheme = mgr.get_scheme("neon-doll-%s" % variant)
    if scheme is None:
        sys.exit("no scheme neon-doll-%s in %s" % (variant, SCHEMES))

    Gtk.init()
    Gtk.Settings.get_default().props.gtk_application_prefer_dark_theme = variant == "dark"
    css = Gtk.CssProvider()
    css.load_from_string("textview { font: 14px monospace; }")
    Gtk.StyleContext.add_provider_for_display(
        Gdk.Display.get_default(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    win = Gtk.Window(title="Neon Doll %s" % variant.title(),
                     default_width=1000, default_height=720)
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    win.set_child(box)
    code_buf, code_view = make_view(CODE, "php", scheme)
    diff_buf, diff_view = make_view(DIFF, "diff", scheme)
    box.append(code_view)
    box.append(diff_view)

    settings = GtkSource.SearchSettings(search_text="$row", case_sensitive=True)
    search = GtkSource.SearchContext(buffer=code_buf, settings=settings)
    search.set_highlight(True)

    def select_hit():
        start = CODE.index("as $row") + len("as ")
        # The insert mark (the cursor) at the end of the hit, against the ")",
        # so the bracket pair lights up.
        code_buf.select_range(code_buf.get_iter_at_offset(start + len("$row")),
                              code_buf.get_iter_at_offset(start))
        diff_buf.place_cursor(diff_buf.get_iter_at_line(9)[1])
        code_view.grab_focus()
        return False

    GLib.timeout_add(300, select_hit)
    win.present()
    loop = GLib.MainLoop()
    win.connect("close-request", lambda *_: loop.quit())
    loop.run()


if __name__ == "__main__":
    main()
