#!/usr/bin/env python3
"""Fail if the GTK 3 colors have drifted from their sources.

A maintainer tool: it needs the source website's system.css, which is not
part of this repo.

gtk-3.0/_colors-dark.css is checked against the site's system.css and the
desktop-only tokens in gtk-4.0/gtk.css; gtk-3.0/_colors-light.css against
the light block in gtk-4.0/gtk.css, which is where the light palette is
defined. GTK 3 has no custom properties, so there each token is an
@define-color of the same name, less the leading --. Tokens only one side
has are fine.

    tools/check-tokens3.py path/to/system.css
"""

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
GTK4 = HERE / "gtk-4.0" / "gtk.css"
if len(sys.argv) != 2:
    sys.exit(__doc__.strip())
SITE = Path(sys.argv[1])

PROP = re.compile(r"--([a-z0-9-]+)\s*:\s*([^;]+);")
DEFINE = re.compile(r"@define-color\s+([a-z0-9-]+)\s+([^;]+);")


def clean(text):
    return re.sub(r"/\*.*?\*/", "", text, flags=re.S)


def norm(pairs):
    return {name: " ".join(value.split()).lower() for name, value in pairs}


def light_block(text):
    start = text.index("@media (prefers-color-scheme: light)")
    root = text.index(":root", start)
    return text[root:text.index("}", root)]


gtk4 = clean(GTK4.read_text())
light = light_block(gtk4)
dark = {**norm(PROP.findall(gtk4.replace(light, ""))), **norm(PROP.findall(clean(SITE.read_text())))}
checks = [
    ("dark", dark, f"{SITE.name} + gtk-4.0/gtk.css"),
    ("light", norm(PROP.findall(light)), "gtk-4.0/gtk.css"),
]
failed = False
for variant, source, source_name in checks:
    ours = norm(DEFINE.findall(clean((HERE / "gtk-3.0" / f"_colors-{variant}.css").read_text())))
    shared = sorted(source.keys() & ours.keys())
    for name in shared:
        if source[name] != ours[name]:
            failed = True
            print(f"{variant} {name}: {source_name} has {source[name]}, _colors-{variant}.css has {ours[name]}")
    print(f"{variant}: {len(shared)} shared tokens checked against {source_name}")
sys.exit(1 if failed else 0)
