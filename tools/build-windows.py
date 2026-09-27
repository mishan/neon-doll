#!/usr/bin/env python3
"""Build the Windows files: Terminal schemes and the contrast themes.

    tools/build-windows.py            write windows/terminal/ and windows/contrast/
    tools/build-windows.py --check    fail if the output is stale

windows/terminal/neon-doll.json is a Windows Terminal *fragment*: dropped in
%LOCALAPPDATA%\\Microsoft\\Windows Terminal\\Fragments\\Neon Doll\\, it adds
both color schemes without anyone editing settings.json. The colors are the
Tilix schemes', entry for entry, so a terminal on either OS looks the same.

windows/terminal/themes.json holds the window themes (tab row and tab colors),
which fragments can't carry; they go into settings.json by hand. Same mapping
as Chrome's: the tab row is the page, the current tab is the panel lifted off
it.

windows/contrast/neon-doll-{dark,light}.theme are Windows *contrast themes*
(high contrast, as it was), the one way to recolor the whole desktop without
patching Windows: Win32 dialogs, WinUI apps, Settings, Explorer, and web pages
in Edge and Chrome. They take a fixed set of system colors and nothing else, so
they're flat by nature: no tints, no graph paper. The files take the stock
ones' shape (C:\\Windows\\Resources\\Ease of Access Themes\\): the AeroLite
visual style with HighContrast=3 for dark and 4 for light, as hcblack and
hcwhite have it (the taskbar's weather text goes by it, not by the colors), no
wallpaper so the desktop is bg, and no sounds or cursors, so yours are left
alone.
"""

import json
import sys
from pathlib import Path

import tokens

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "windows" / "terminal"
CONTRAST_OUT = ROOT / "windows" / "contrast"

ANSI = ["black", "red", "green", "yellow", "blue", "purple", "cyan", "white",
        "brightBlack", "brightRed", "brightGreen", "brightYellow",
        "brightBlue", "brightPurple", "brightCyan", "brightWhite"]

PANEL = {v: tokens.palette(v)["panel"] for v in tokens.VARIANTS}


def scheme(variant):
    t = json.loads((ROOT / "tilix" / f"neon-doll-{variant}.json").read_text())
    s = {
        "name": t["name"],
        "background": t["background-color"],
        "foreground": t["foreground-color"],
        "cursorColor": t["cursor-background-color"],
        "selectionBackground": t["highlight-background-color"],
    }
    s.update(zip(ANSI, t["palette"]))
    return s


def theme(variant):
    bg = scheme(variant)["background"]
    return {
        "name": f"Neon Doll {variant.title()}",
        "window": {"applicationTheme": variant},
        "tabRow": {"background": bg + "ff", "unfocusedBackground": bg + "ff"},
        "tab": {
            "background": PANEL[variant] + "ff",
            "unfocusedBackground": bg + "ff",
            "showCloseButton": "hover",
        },
    }


# System colors, by the .theme file's names, to tokens. Settings' contrast
# theme editor shows eight of them (in its words: Background, Text, Hyperlink,
# Inactive text, Selected text and Button text, each of the last two a pair);
# the rest are Win32's and still paint classic dialogs, menus and title bars.
#
# The roles hold: fuchsia is where you are (the selection, the current menu
# item, the focused window's title bar and border), purple is what you can
# touch (links, button labels and button edges). Buttons are drawn flat: a 3D
# edge is two pairs of colors, outer (hilight, dark shadow) and inner (light,
# shadow), so the outer pair is purple and the inner pair is the face, which
# leaves a hard 1px edge.
# Every text pair clears 4.5:1 in both variants.
CONTRAST = [
    ("Window", "bg"),                   # Background
    ("WindowText", "ink"),              # Text
    ("HotTrackingColor", "purple"),     # Hyperlink
    ("GrayText", "muted"),              # Inactive text
    ("Hilight", "pink"),                # Selected text, background
    ("HilightText", "bg"),              # Selected text, text
    ("ButtonFace", "bg"),               # Button text, background; also dialogs
    ("ButtonText", "purple"),           # Button text, text
    ("ButtonHilight", "purple"),
    ("ButtonDkShadow", "purple"),
    ("ButtonLight", "bg"),
    ("ButtonShadow", "bg"),
    ("ButtonAlternateFace", "panel"),
    ("WindowFrame", "muted"),
    ("ActiveBorder", "line"),
    ("InactiveBorder", "line"),
    # The focused window. Windows 11 fills a Win32 caption, and the resize
    # border of every window, WinUI too, with ActiveTitle, so that is the
    # fuchsia light on the window you're in. The title on it is TitleText
    # under the light theme but *Window* under the dark one, so both are bg.
    ("ActiveTitle", "pink"),
    ("GradientActiveTitle", "pink"),
    ("TitleText", "bg"),
    ("InactiveTitle", "bg"),
    ("GradientInactiveTitle", "bg"),
    ("InactiveTitleText", "muted"),
    ("Menu", "panel"),
    ("MenuBar", "panel"),
    ("MenuText", "ink"),
    ("MenuHilight", "pink"),            # flat menus; its text is HilightText
    ("InfoWindow", "panel"),            # tooltips
    ("InfoText", "ink"),
    ("Scrollbar", "panel"),
    ("AppWorkspace", "bg"),
    ("Background", "bg"),               # the desktop
]


def contrast_theme(variant):
    p = tokens.palette(variant)
    colors = "\n".join(f"{k}={' '.join(map(str, tokens.rgb(p[t])))}" for k, t in CONTRAST)
    hc = 4 if variant == "light" else 3
    text = f"""; Neon Doll {variant.title()}, a Windows contrast theme. Built by
; tools/build-windows.py from tokens.toml; edit those, not this.

[Theme]
DisplayName=Neon Doll {variant.title()}
SetLogonBackground=0

[Control Panel\\Colors]
{colors}

[Control Panel\\Desktop]
Wallpaper=
TileWallpaper=0
WallpaperStyle=10
Pattern=

[VisualStyles]
Path=%SystemRoot%\\Resources\\Themes\\Aero\\AeroLite.msstyles
ColorStyle=NormalColor
Size=NormalSize
HighContrast={hc}
Transparency=0

[MasterThemeSelector]
MTSM=RJSPBS
"""
    # CRLF, as Windows writes them.
    return text.replace("\n", "\r\n").encode("ascii")


def outputs():
    variants = ("dark", "light")
    dump = lambda o: (json.dumps(o, indent=2) + "\n").encode()
    yield OUT / "neon-doll.json", dump({"schemes": [scheme(v) for v in variants]})
    yield OUT / "themes.json", dump({"themes": [theme(v) for v in variants]})
    for v in variants:
        yield CONTRAST_OUT / f"neon-doll-{v}.theme", contrast_theme(v)


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
        sys.exit("stale: " + ", ".join(map(str, stale)) + " (run tools/build-windows.py)")


main()
