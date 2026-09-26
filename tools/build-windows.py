#!/usr/bin/env python3
"""Build the Windows Terminal files from the Tilix schemes.

    tools/build-windows.py            write windows/terminal/
    tools/build-windows.py --check    fail if the output is stale

windows/terminal/neon-doll.json is a Windows Terminal *fragment*: dropped in
%LOCALAPPDATA%\\Microsoft\\Windows Terminal\\Fragments\\Neon Doll\\, it adds
both color schemes without anyone editing settings.json. The colors are the
Tilix schemes', entry for entry, so a terminal on either OS looks the same.

windows/terminal/themes.json holds the window themes (tab row and tab colors),
which fragments can't carry; they go into settings.json by hand. Same mapping
as Chrome's: the tab row is the page, the current tab is the panel lifted off
it.
"""

import json
import sys
from pathlib import Path

import tokens

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "windows" / "terminal"

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


def outputs():
    variants = ("dark", "light")
    dump = lambda o: (json.dumps(o, indent=2) + "\n").encode()
    yield OUT / "neon-doll.json", dump({"schemes": [scheme(v) for v in variants]})
    yield OUT / "themes.json", dump({"themes": [theme(v) for v in variants]})


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
