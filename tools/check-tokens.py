#!/usr/bin/env python3
"""Fail if gtk-4.0/gtk.css has drifted from the design system it came from.

A maintainer tool: it needs the source website's system.css, which is not
part of this repo.

Every custom property the two stylesheets both define must have the same
value. Tokens only one side has are fine: the desktop needs a few the site
does not (--select-pink, --press), and most of the site's type and layout
tokens mean nothing to GTK.

    tools/check-tokens.py path/to/system.css
"""

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
GTK = HERE / "gtk-4.0" / "gtk.css"
if len(sys.argv) != 2:
    sys.exit(__doc__.strip())
SITE = Path(sys.argv[1])

DECL = re.compile(r"(--[a-z0-9-]+)\s*:\s*([^;]+);")


def tokens(path):
    text = re.sub(r"/\*.*?\*/", "", path.read_text(), flags=re.S)
    # The site is dark only; compare against the base palette, not the
    # light overrides under @media.
    text = text.split("@media", 1)[0]
    return {name: " ".join(value.split()).lower() for name, value in DECL.findall(text)}


site, gtk = tokens(SITE), tokens(GTK)
shared = sorted(site.keys() & gtk.keys())
drift = [(n, site[n], gtk[n]) for n in shared if site[n] != gtk[n]]

for name, want, got in drift:
    print(f"{name}: site has {want}, gtk.css has {got}")
print(f"{len(shared)} shared tokens, {len(drift)} drifted")
sys.exit(1 if drift else 0)
