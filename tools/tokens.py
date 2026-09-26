"""Neon Doll's colors, read from tokens.toml, for the builders in tools/.

    import tokens
    p = tokens.palette("dark")     # solid colors, by name: p["pink"]
    tokens.css("dark", "wash")     # a tint as CSS: "rgba(180, 140, 255, 0.06)"
    f = tokens.flat("dark")        # everything flattened onto bg, as the
                                   # editor and terminal schemes take it

Names are tokens.toml's (the design system's), plus the short ones the
editor schemes grew up with: string, add and del for code-string, diff-add
and diff-del.
"""

import colorsys
import tomllib
from functools import cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VARIANTS = ("dark", "light")
SHORT = {"string": "code-string", "add": "diff-add", "del": "diff-del"}


@cache
def _load():
    with open(ROOT / "tokens.toml", "rb") as f:
        return tomllib.load(f)


def palette(variant):
    """The solid colors, under their own names and the short ones."""
    v = _load()[variant]
    p = {k: c for k, c in v.items() if isinstance(c, str)}
    for short, name in SHORT.items():
        p[short] = p[name]
    return p


def tint(variant, name, flat=False):
    """A tint as (hex color, alpha); flat=True takes the [flat] override."""
    v = _load()[variant]
    color, alpha = v.get("flat", {}).get(name) if flat and name in v.get("flat", {}) else v["tints"][name]
    return palette(variant).get(color, color), alpha


def tints(variant):
    return list(_load()[variant]["tints"])


def css(variant, name):
    """A tint as CSS rgba(), alpha to two places, as the stylesheets write it."""
    color, alpha = tint(variant, name)
    r, g, b = rgb(color)
    return f"rgba({r}, {g}, {b}, {alpha:.2f})"


# --- color math ---------------------------------------------------------------

def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def hexs(c):
    return "#%02x%02x%02x" % tuple(max(0, min(255, round(v))) for v in c)


def over(base, color, alpha):
    """`color` at `alpha` composited over `base`, as a browser would."""
    b, c = rgb(base), rgb(color)
    return hexs([b[i] + (c[i] - b[i]) * alpha for i in range(3)])


def hsl(h, s, l):
    r, g, b = colorsys.hls_to_rgb(h / 360, l, s)
    return hexs((r * 255, g * 255, b * 255))


def hsl_of(c):
    h, l, s = colorsys.rgb_to_hls(*[v / 255 for v in rgb(c)])
    return h * 360, s, l


def luminance(c):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = map(ch, rgb(c))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


# --- flattened, for themes that take only solid colors -------------------------

# The editor schemes' names for the tints they use.
FLAT_NAMES = {
    "wash": "wash", "wash-strong": "wash-strong", "grid": "grid",
    "press": "press", "edge-purple": "edge-purple", "ul-purple": "ul-purple",
    "select": "select-pink", "wash-pink": "wash-pink",
    "add-bg": "diff-add-bg", "del-bg": "diff-del-bg",
    "add-refine": "diff-add-refine", "del-refine": "diff-del-refine",
    "change-bg": "change-bg",
}


@cache
def flat(variant):
    """Every color the editor and terminal schemes use, as solid hex.

    The GtkSourceView, Tilix and Emacs schemes all take solid colors, because
    none of them composites alpha the way a browser does. So every tint is
    flattened onto bg, and every ANSI color the palette has no token for is
    derived by a stated rule. Both variants go through the same rules.
    """
    p = palette(variant)
    for name, token in FLAT_NAMES.items():
        color, alpha = tint(variant, token, flat=True)
        p[name] = over(p["bg"], color, alpha)
    # Diff rows under the current-line tint (magit's highlighted hunk): 1.6x
    # the row tint over the wash. Text on these rows takes the bright ANSI
    # variant of its color, which is what keeps it above 4.5:1. Word-level
    # refine tints carry ink.
    for row, token in (("add-bg-hl", "diff-add-bg"), ("del-bg-hl", "diff-del-bg")):
        color, alpha = tint(variant, token)
        p[row] = over(p["wash"], color, alpha * 1.6)

    # ANSI. Normal colors reuse palette tokens where one exists. The two hues
    # the site has no token for keep a sibling's saturation and lightness and
    # rotate only the hue, so they sit at the same weight as the rest:
    #   blue = purple's S and L at hue 228 (a violet-leaning periwinkle)
    #   cyan = diff-add's S and L at hue 188 (a mint-cyan)
    # Bright variants are the normal color mixed 40% toward ink: lighter on
    # dark, deeper on light, and plum-tinted either way. Black and white are
    # assigned by role, not by lightness: 0 is line and 15 is ink in both
    # variants, so "white" text is always the foreground and never vanishes.
    # Fuchsia is kept out of the sixteen so no program can use it as
    # decoration; it is the cursor.
    _, ps, pl = hsl_of(p["purple"])
    _, as_, al = hsl_of(p["add"])
    blue = hsl(228, ps, pl)
    cyan = hsl(188, as_, al)
    gray = over(p["muted"], p["ink"], 0.5)

    def bright(c):
        return over(c, p["ink"], 0.4)

    p["ansi"] = [
        ("0 black", p["line"], "--line"),
        ("1 red", p["del"], "--diff-del"),
        ("2 green", p["add"], "--diff-add"),
        ("3 yellow", p["string"], "--code-string"),
        ("4 blue", blue, "hsl(228, S and L of --purple)"),
        ("5 magenta", p["purple"], "--purple"),
        ("6 cyan", cyan, "hsl(188, S and L of --diff-add)"),
        ("7 white", gray, "--muted + 50% --ink"),
        ("8 bright black", p["muted"], "--muted"),
        ("9 bright red", bright(p["del"]), "red + 40% --ink"),
        ("10 bright green", bright(p["add"]), "green + 40% --ink"),
        ("11 bright yellow", bright(p["string"]), "yellow + 40% --ink"),
        ("12 bright blue", bright(blue), "blue + 40% --ink"),
        ("13 bright magenta", bright(p["purple"]), "magenta + 40% --ink"),
        ("14 bright cyan", bright(cyan), "cyan + 40% --ink"),
        ("15 bright white", p["ink"], "--ink"),
    ]
    p["bright-red"] = bright(p["del"])
    p["bright-green"] = bright(p["add"])
    return p
