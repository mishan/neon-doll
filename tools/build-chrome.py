#!/usr/bin/env python3
"""Build the Chrome themes into chrome/neon-doll-{dark,light}/.

A Chrome theme is colors and images and nothing else: no fonts, corners,
shadows or hover states, and no light/dark switching, so each variant is its
own theme. Output is committed, so installing needs no Python.

    tools/build-chrome.py            write both themes
    tools/build-chrome.py --check    fail if the output is stale

Mapping. The window frame is the page and the toolbar is the panel on it,
so the current tab, which Chrome paints in the toolbar color, reads as the
one panel lifted off the page. Its title is fuchsia: it is where you are.
Background tabs are muted. The address bar is a slot in the toolbar, like a
text field. The New Tab page is the page itself, with links in purple.

The graph paper goes on the dark New Tab page only. Chrome treats any New Tab
image as a photo: it turns the logo and shortcut labels white and shades the
top with a gradient. On the dark page that's invisible; on paper it makes the
logo vanish, so light gets the page color alone.
"""

import json
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "chrome"
VERSION = "0.1.0"

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


def manifest(variant, p):
    c = {k: rgb(v) for k, v in p.items() if k != "grid"}
    theme = {
        "manifest_version": 3,
        "name": f"Neon Doll {variant.title()}",
        "version": VERSION,
        "description": "A man page in a terminal that never existed: plum, fuchsia for where you are, purple for links.",
        "theme": {
            "colors": {
                "frame": c["bg"],
                "frame_inactive": c["bg"],
                "frame_incognito": c["bg"],
                "frame_incognito_inactive": c["bg"],
                "background_tab": c["bg"],
                "background_tab_inactive": c["bg"],
                "toolbar": c["panel"],
                "toolbar_text": c["ink"],
                "toolbar_button_icon": c["ink"],
                "tab_text": c["pink"],
                "tab_background_text": c["muted"],
                "tab_background_text_inactive": c["dimmest"],
                "tab_background_text_incognito": c["muted"],
                "tab_background_text_incognito_inactive": c["dimmest"],
                "bookmark_text": c["ink"],
                "omnibox_background": c["bg"],
                "omnibox_text": c["ink"],
                "ntp_background": c["bg"],
                "ntp_text": c["ink"],
                "ntp_link": c["purple"],
                "ntp_header": c["line"],
            },
        },
    }
    if variant == "dark":
        theme["theme"]["images"] = {"theme_ntp_background": "images/paper.png"}
        theme["theme"]["properties"] = {
            "ntp_background_alignment": "top left",
            "ntp_background_repeat": "repeat",
        }
    return theme


def outputs():
    for variant, p in PALETTES.items():
        d = OUT / f"neon-doll-{variant}"
        yield d / "manifest.json", (json.dumps(manifest(variant, p), indent=2) + "\n").encode()
        if variant == "dark":
            yield d / "images" / "paper.png", paper(p)


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
        sys.exit("stale: " + ", ".join(map(str, stale)) + " (run tools/build-chrome.py)")


main()
