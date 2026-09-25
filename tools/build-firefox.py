#!/usr/bin/env python3
"""Build the Firefox theme into firefox/.

A Firefox static theme is colors and images, like Chrome's, but it names many
more parts: popups, the sidebar, the address bar and its focus state, the
selected tab's outline, toolbar buttons. It can also carry a `dark_theme`,
which Firefox uses while the system is dark, so one theme holds both
variants: `theme` is light and `dark_theme` is dark. Output is committed, so
installing needs no Python.

    tools/build-firefox.py            write the theme
    tools/build-firefox.py --check    fail if the output is stale

Mapping, as in the Chrome themes. The window frame is the page and the
toolbar is the panel on it, so the current tab, which takes the toolbar
color, reads as the one panel lifted off the page. Its title is fuchsia, and
so is its 1px outline (`tab_line`): it is where you are. Background tabs are
muted. The address bar is a slot, page-colored with a line edge; focused, the
edge turns fuchsia, as a focus ring does. Popups and the sidebar are panels
with a line edge; the highlighted address-bar result and the current sidebar
row get a fuchsia wash, and the sidebar row fuchsia text. Toolbar hover is a
fuchsia wash too, since hover is a position; pressed is one step stronger.
Loading and attention (a finished download, a starred page) are fuchsia.
The New Tab page is the page, with panel-colored cards.

The graph paper tiles the frame, so it shows in the tab strip, where the
window shows through, and nowhere else: tabs and toolbar are opaque on top.
Firefox, unlike Chrome, doesn't restyle anything when a theme has an image,
so light gets the paper too. The New Tab page can't take an image.
"""

import json
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "firefox"
VERSION = "0.1.0"
ADDON_ID = "neon-doll@mishan.github.io"

PALETTES = {
    "dark": {
        "bg": "#0f0d14", "panel": "#16131d", "line": "#2a2438",
        "ink": "#ebe6f0", "muted": "#9c93ab", "dimmest": "#6f6880",
        "pink": "#ff2d95", "purple": "#b48cff",
        "grid": ("#b48cff", 0.09),
    },
    "light": {
        "bg": "#f7f4fa", "panel": "#ede7f3", "line": "#d6cce2",
        "ink": "#1a1522", "muted": "#5f5670", "dimmest": "#8d84a0",
        "pink": "#c8006a", "purple": "#6a3fd0",
        "grid": ("#6a3fd0", 0.07),
    },
}


def rgb(h):
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def rgba(h, alpha):
    r, g, b = rgb(h)
    return f"rgba({r}, {g}, {b}, {alpha})"


def over(base, color, alpha):
    b, c = rgb(base), rgb(color)
    return [round(b[i] + (c[i] - b[i]) * alpha) for i in range(3)]


def png(width, height, pixel):
    """A minimal RGB PNG; pixel(x, y) returns [r, g, b]."""
    raw = b"".join(b"\0" + bytes(v for x in range(width) for v in pixel(x, y))
                   for y in range(height))

    def chunk(kind, data):
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body))

    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9))
            + chunk(b"IEND", b""))


def paper(p):
    """One 24px cell of the graph paper, lines on the top and left edge."""
    page, line = rgb(p["bg"]), over(p["bg"], *p["grid"])
    return png(24, 24, lambda x, y: line if x == 0 or y == 0 else page)


def theme(variant, p):
    return {
        "colors": {
            "frame": p["bg"],
            "frame_inactive": p["bg"],
            "tab_background_text": p["muted"],
            "tab_background_separator": p["line"],
            "tab_selected": p["panel"],
            "tab_text": p["pink"],
            "tab_line": p["pink"],
            "tab_loading": p["pink"],
            "toolbar": p["panel"],
            "toolbar_text": p["ink"],
            "bookmark_text": p["ink"],
            "icons": p["ink"],
            "icons_attention": p["pink"],
            "button_background_hover": rgba(p["pink"], 0.10),
            "button_background_active": rgba(p["pink"], 0.18),
            "toolbar_top_separator": p["line"],
            "toolbar_bottom_separator": p["line"],
            "toolbar_vertical_separator": p["line"],
            "toolbar_field": p["bg"],
            "toolbar_field_text": p["ink"],
            "toolbar_field_border": p["line"],
            "toolbar_field_focus": p["bg"],
            "toolbar_field_text_focus": p["ink"],
            "toolbar_field_border_focus": p["pink"],
            "toolbar_field_highlight": rgba(p["pink"], 0.30),
            "toolbar_field_highlight_text": p["ink"],
            "popup": p["panel"],
            "popup_text": p["ink"],
            "popup_border": p["line"],
            "popup_highlight": rgba(p["pink"], 0.14),
            "popup_highlight_text": p["ink"],
            "sidebar": p["panel"],
            "sidebar_text": p["ink"],
            "sidebar_border": p["line"],
            "sidebar_highlight": rgba(p["pink"], 0.14),
            "sidebar_highlight_text": p["pink"],
            "ntp_background": p["bg"],
            "ntp_card_background": p["panel"],
            "ntp_text": p["ink"],
        },
        "images": {
            "additional_backgrounds": [f"images/paper-{variant}.png"],
        },
        "properties": {
            "additional_backgrounds_alignment": ["left top"],
            "additional_backgrounds_tiling": ["repeat"],
            # The toolbar and field colors say which; saying it outright keeps
            # Firefox's own icons and menus from guessing.
            "color_scheme": variant,
            # Web pages follow the system, not the theme.
            "content_color_scheme": "system",
        },
    }


def manifest():
    return {
        "manifest_version": 2,
        "name": "Neon Doll",
        "version": VERSION,
        "description": "A man page in a terminal that never existed: plum, fuchsia for where you are, purple for links. Follows the system's light or dark mode.",
        "homepage_url": "https://github.com/mishan/neon-doll",
        "browser_specific_settings": {
            "gecko": {"id": ADDON_ID},
        },
        "theme": theme("light", PALETTES["light"]),
        "dark_theme": theme("dark", PALETTES["dark"]),
    }


def outputs():
    yield OUT / "manifest.json", (json.dumps(manifest(), indent=2) + "\n").encode()
    for variant, p in PALETTES.items():
        yield OUT / "images" / f"paper-{variant}.png", paper(p)


def main():
    check = "--check" in sys.argv
    stale = []
    for path, data in outputs():
        if check:
            if not path.exists() or path.read_bytes() != data:
                stale.append(path.relative_to(ROOT))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            print(path.relative_to(ROOT))
    if stale:
        sys.exit("stale: " + ", ".join(map(str, stale)) + " (run tools/build-firefox.py)")


main()
