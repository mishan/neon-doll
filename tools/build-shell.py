#!/usr/bin/env python3
"""Build the GNOME Shell stylesheets from gnome-shell/gnome-shell.css.in.

St has no custom properties, so the palette is substituted here instead:
@name@ becomes the token's value. Both variants come from one template, so
they can't drift. The output is committed, so installing needs no Python.

    tools/build-shell.py            write themes/Neon-Doll-{Dark,Light}/gnome-shell/
    tools/build-shell.py --check    fail if the output is stale, or if a class
                                    or id in the template isn't one the shell uses
    tools/build-shell.py --coverage list stock selectors that paint with the
                                    system accent and aren't matched here; after a
                                    GNOME upgrade this is the list to read. Some are
                                    Sass artifacts that match no real widget.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "gnome-shell" / "gnome-shell.css.in"

# Names follow the GTK stylesheet's tokens, with _ for -. The core palette and
# its tints are the website's; on_fill, string_bg, tint_pink, osd_bg and the
# wall_* colors are the desktop's own, each taken from a palette color.
DARK = {
    "variant": "dark",
    "bg": "#0f0d14", "panel": "#16131d", "line": "#2a2438",
    "ink": "#ebe6f0", "muted": "#9c93ab", "dimmest": "#6f6880",
    "pink": "#ff2d95", "purple": "#b48cff",
    "string": "#e5c07b", "add": "#7ee787", "del": "#ff7b72",
    "wash": "rgba(180, 140, 255, 0.06)",
    "wash_strong": "rgba(180, 140, 255, 0.10)",
    "press": "rgba(180, 140, 255, 0.16)",
    "tint_purple": "rgba(180, 140, 255, 0.35)",
    "wash_pink": "rgba(255, 45, 149, 0.08)",
    "tint_pink": "rgba(255, 45, 149, 0.35)",
    "select_pink": "rgba(255, 45, 149, 0.30)",
    "string_bg": "rgba(229, 192, 123, 0.10)",
    "osd_bg": "rgba(22, 19, 29, 0.90)",
    "on_fill": "#0f0d14",
    "wall_ink": "#ebe6f0", "wall_muted": "#9c93ab", "wall_warning": "#e5c07b",
}

LIGHT = {
    "variant": "light",
    "bg": "#f7f4fa", "panel": "#ede7f3", "line": "#d6cce2",
    "ink": "#1a1522", "muted": "#5f5670", "dimmest": "#8d84a0",
    "pink": "#c8006a", "purple": "#6a3fd0",
    "string": "#8a6100", "add": "#1f7a33", "del": "#c4312a",
    "wash": "rgba(106, 63, 208, 0.05)",
    "wash_strong": "rgba(106, 63, 208, 0.09)",
    "press": "rgba(106, 63, 208, 0.14)",
    "tint_purple": "rgba(106, 63, 208, 0.40)",
    "wash_pink": "rgba(200, 0, 106, 0.08)",
    "tint_pink": "rgba(200, 0, 106, 0.35)",
    "select_pink": "rgba(200, 0, 106, 0.18)",
    "string_bg": "rgba(138, 97, 0, 0.10)",
    "osd_bg": "rgba(237, 231, 243, 0.92)",
    "on_fill": "#f7f4fa",
    # The lock screen's wallpaper is dimmed dark in both variants, so text
    # on it keeps light values: paper, and the dark palette's muted and string.
    "wall_ink": "#f7f4fa", "wall_muted": "#9c93ab", "wall_warning": "#e5c07b",
}

# Selector families for @family|:state :state@ in the template. Each state is
# appended to every selector; an empty state list gives the bare selectors.
_LOGIN = [f".login-dialog-button.{c}" for c in (
    "cancel-button", "switch-user-button", "a11y-button",
    "login-dialog-auth-menu-button", "login-dialog-session-list-button")]
_UNLOCK_FLAT = [
    ".message-notification-group .message-collapse-button",
    ".message .message-header .message-expand-button",
    ".message .message-header .message-close-button",
    ".calendar .calendar-month-header .pager-button",
    ".login-dialog-button.next-button",
]
FAMILIES = {
    "button": [
        ".button", ".icon-button",
        ".modal-dialog .modal-dialog-button-box .modal-dialog-button",
        ".notification-button", *_LOGIN,
        ".login-dialog .login-button", ".login-dialog .web-login-prompt-button",
        ".unlock-dialog .button", ".unlock-dialog .icon-button",
        ".unlock-dialog .login-button", ".unlock-dialog .web-login-prompt-button",
        *(f".unlock-dialog {s}" for s in _LOGIN),
        ".parental-controls-shield .parental-controls-shield-button",
        ".app-folder-dialog .icon-button", ".background-app-item .icon-button",
        ".screenshot-ui-type-button", ".screenshot-ui-show-pointer-button",
        ".word-suggestions StButton",
    ],
    "default": [
        ".button.default", ".icon-button.default",
        ".modal-dialog .modal-dialog-button-box .modal-dialog-button:default",
    ],
    "flat": [
        ".button.flat", ".icon-button.flat", *_UNLOCK_FLAT,
        *(f".unlock-dialog {s}" for s in _UNLOCK_FLAT),
        ".unlock-dialog-notifications-container .message StButton",
        ".unlock-dialog-notifications-container .unlock-dialog-notification-source StButton",
    ],
}

OUTPUTS = {
    "Neon-Doll-Dark": DARK,
    "Neon-Doll-Light": LIGHT,
}


def _rgb(hex_color):
    return [int(hex_color[i:i + 2], 16) for i in (1, 3, 5)]


def mix(a, b, weight):
    """color-mix(in srgb, a weight, b), as the GTK stylesheet writes it."""
    return "#" + "".join(f"{round(x * weight + y * (1 - weight)):02x}"
                         for x, y in zip(_rgb(a), _rgb(b)))


for _t in (DARK, LIGHT):
    _t["pink_hover"] = mix(_t["pink"], _t["ink"], 0.75)

# Hover and pressed fills for panels that float over windows, like a
# notification banner: the wash and press tints composited onto the panel
# ahead of time, so the fill stays opaque. The translucent tints on their own
# let the windows behind show through.
DARK["panel_hover"] = mix(DARK["purple"], DARK["panel"], 0.06)
DARK["panel_press"] = mix(DARK["purple"], DARK["panel"], 0.16)
LIGHT["panel_hover"] = mix(LIGHT["purple"], LIGHT["panel"], 0.05)
LIGHT["panel_press"] = mix(LIGHT["purple"], LIGHT["panel"], 0.14)


def switch_assets(t):
    """The switch's marks and grip, which GTK draws with gradients.

    Geometry follows gtk-4.0/gtk.css: a 42x24 slot, an 8px ring with a 2px
    wall in the open half when off, a 2x10 bar when on, and three 1px ribs
    across the middle 8px of the 18px cursor."""
    def svg(w, h, body):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
                f'viewBox="0 0 {w} {h}">{body}</svg>\n')

    def ring(c):
        return svg(42, 24, f'<rect x="27" y="9" width="6" height="6" fill="none" '
                           f'stroke="{c}" stroke-width="2"/>')

    def bar(c):
        return svg(42, 24, f'<rect x="11" y="7" width="2" height="10" fill="{c}"/>')

    def grip(c):
        return svg(18, 18, "".join(f'<rect x="{x}" y="5" width="1" height="8" fill="{c}"/>'
                                   for x in (5, 8, 11)))

    return {
        "switch-track-off.svg": ring(t["dimmest"]),
        "switch-track-on.svg": bar(t["pink"]),
        "switch-track-off-disabled.svg": ring(t["line"]),
        "switch-track-on-disabled.svg": bar(t["line"]),
        "switch-grip-off.svg": grip(t["panel"]),
        "switch-grip-on.svg": grip(t["bg"]),
    }


def hearts(theme, t):
    """A -Hearts theme: the regular one, with Locate Pointer's ring swapped for
    a heart. User Themes takes a theme name and nothing else, so an option has
    to be a theme of its own; this one imports its sibling rather than copying
    it, and holds only the difference. It has no gtk-3.0/, so it's offered for
    the Shell and nowhere else."""
    heart = (f'<svg xmlns="http://www.w3.org/2000/svg" width="50" height="50" viewBox="0 0 50 50">'
             f'<path d="M25 43C9 31 4 22 8.5 14.5C12.5 8 21 8.5 25 15'
             f'C29 8.5 37.5 8 41.5 14.5C46 22 41 31 25 43Z" '
             f'fill="{t["pink"]}" fill-opacity="0.12" '
             f'stroke="{t["pink"]}" stroke-width="2" stroke-linejoin="round"/></svg>\n')
    css = f'''/* {theme}, with a heart for Locate Pointer instead of a ring.
   Generated by tools/build-shell.py; edit that, not this. */

@import url("../../{theme}/gnome-shell/gnome-shell.css");

/* St can't draw a heart, so it's an image; the shell still grows the box
   outward from the pointer, and the image with it. The box itself stays
   empty. 64px against the ring's 50: a heart covers less of its box. */
.ripple-pointer-location {{
  width: 64px;
  height: 64px;
  background-color: transparent;
  border: none;
  background-image: url("locate-pointer-heart.svg");
  background-size: contain;
}}
'''
    return {"gnome-shell.css": css, "locate-pointer-heart.svg": heart}


def outputs():
    """Every generated file, as {path: text}."""
    files = {}
    for theme, tokens in OUTPUTS.items():
        base = ROOT / "themes" / theme / "gnome-shell"
        files[base / "gnome-shell.css"] = render(tokens)
        for name, text in switch_assets(tokens).items():
            files[base / name] = text
        for name, text in hearts(theme, tokens).items():
            files[ROOT / "themes" / f"{theme}-Hearts" / "gnome-shell" / name] = text
    return files

ROLES = {
    "bg": "the page", "panel": "anything that sits on the page",
    "line": "panel edges", "ink": "text", "muted": "labels, metadata",
    "dimmest": "disabled", "pink": "position: current, focused, checked",
    "purple": "links and the default action", "string": "warning",
    "add": "success", "del": "destructive, error, recording",
    "wash": "button field, hover", "wash_strong": "icon wells",
    "press": ":active", "tint_purple": "default action edge",
    "wash_pink": "checked and selected field", "tint_pink": "pink edge, soft",
    "select_pink": "text selection", "string_bg": "warning field",
    "osd_bg": "OSDs and switchers", "on_fill": "text on a pink fill",
    "wall_ink": "text on the lock screen wallpaper",
    "wall_muted": "secondary text there", "wall_warning": "warnings there",
    "pink_hover": "hovered switch cursor: pink 75%, ink 25%",
}


def header(tokens):
    width = max(len(k) for k in ROLES)
    lines = [
        f"/* Neon Doll, {tokens['variant']}. Generated from gnome-shell/gnome-shell.css.in",
        "   by tools/build-shell.py; edit the template, not this file.",
        "",
        "   The palette is a website design system's, carried onto the desktop.",
        "   St has no variables, so the values are written out below; this is",
        "   the key.",
        "",
    ]
    for k, role in ROLES.items():
        lines.append(f"   {k.replace('_', '-'):<{width}}  {tokens[k]:<26} {role}")
    lines.append("*/")
    return "\n".join(lines) + "\n\n"


def expand_families(template):
    def sub(m):
        family, states = m.group(1), m.group(2).split() or [""]
        if family not in FAMILIES:
            sys.exit(f"unknown selector family: {family}")
        return ",\n".join(f"{sel}{st}" for st in states for sel in FAMILIES[family])
    return re.sub(r"@([a-z]+)\|([^@]*)@", sub, template)


def render(tokens):
    template = expand_families(SRC.read_text())
    missing = set()

    def sub(m):
        if m.group(1) not in tokens:
            missing.add(m.group(1))
            return m.group(0)
        return tokens[m.group(1)]

    body = re.sub(r"@([a-z_]+)@", sub, template)
    if missing:
        sys.exit(f"unknown tokens in template: {', '.join(sorted(missing))}")
    return header(tokens) + body


def stock_css():
    return subprocess.run(
        ["gresource", "extract", "/usr/share/gnome-shell/gnome-shell-theme.gresource",
         "/org/gnome/shell/theme/gnome-shell-dark.css"],
        capture_output=True, text=True, check=True).stdout


def _norm(selector):
    """Whitespace collapsed, pseudo-classes on the last part sorted."""
    parts = selector.split()
    m = re.match(r"([^:]*)((?::[\w-]+)*)$", parts[-1])
    if m:
        parts[-1] = m.group(1) + "".join(sorted(re.findall(r":[\w-]+", m.group(2))))
    return " ".join(parts)


def _rules(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
        yield [s.strip() for s in m.group(1).split(",") if s.strip()], m.group(2)


def coverage():
    ours = {_norm(s) for sels, _ in _rules(expand_families(SRC.read_text())) for s in sels}
    for sels, body in _rules(stock_css()):
        if "-st-accent" in body:
            for s in sels:
                if "LookingGlass" not in s and _norm(s) not in ours:
                    print(_norm(s))


def shell_names():
    """Every class and id the stock theme or the shell's own JS mentions."""
    names = set()
    names |= set(re.findall(r"[.#]([A-Za-z][\w-]*)", stock_css()))
    lib = next(Path("/usr/lib/gnome-shell").glob("libshell-*.so"), None)
    if lib:
        listing = subprocess.run(["gresource", "list", str(lib)],
                                 capture_output=True, text=True).stdout.split()
        for path in listing:
            if path.endswith(".js"):
                js = subprocess.run(["gresource", "extract", str(lib), path],
                                    capture_output=True, text=True).stdout
                names |= set(re.findall(r"[\w-]+", js))
    return names


def check():
    ok = True
    for path, text in outputs().items():
        if not path.exists() or path.read_text() != text:
            print(f"stale: {path.relative_to(ROOT)} (run tools/build-shell.py)")
            ok = False

    css = re.sub(r"/\*.*?\*/", "", expand_families(SRC.read_text()), flags=re.S)
    selectors = " ".join(re.findall(r"([^{}]+)\{[^{}]*\}", css))
    used = set(re.findall(r"[.#]([A-Za-z][\w-]*)", selectors))
    known = shell_names()
    for n in sorted(used - known):
        print(f"unknown class or id: {n}")
        ok = False
    return ok


def main():
    if "--coverage" in sys.argv[1:]:
        coverage()
        return
    if "--check" in sys.argv[1:]:
        sys.exit(0 if check() else 1)
    for path, text in outputs().items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
