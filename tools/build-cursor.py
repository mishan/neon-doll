#!/usr/bin/env python3
"""Build the Neon Doll cursor theme into icons/Neon-Doll-Cursors/.

The sources are the SVGs in cursor/src/, drawn on a 24-unit grid. Each is
rendered at 24, 32, 48, 64 and 96 px and packed into an Xcursor file, and the
legacy X11 and toolkit names are added as relative symlinks. The output is
committed, so installing needs no tools.

    tools/build-cursor.py                write icons/Neon-Doll-Cursors/
    tools/build-cursor.py --check        fail if the output is stale
    tools/build-cursor.py --sheet OUT    draw a contact sheet of the built
                                         cursors (needs Pillow)

Rendering takes rsvg-convert, inkscape or ImageMagick, whichever is found
first; ImageMagick only if it renders SVG through librsvg. xcursorgen isn't
needed: the Xcursor files are written here, so a renderer is the only tool.
--check allows a few levels of antialiasing difference per channel, so a
different librsvg version doesn't make the output look stale.

Design. One cursor theme serves both variants (GNOME has one cursor
setting, not a light and a dark one), and it has to stay findable on a large
screen over anything: dark, light, mid grey, a photo. A solid fuchsia cursor
did that but was too loud, so the body is black, #0f0d14, the dark variant's
page, and fuchsia is kept for what it means in Neon Doll: position.

  - The everyday pointers, default, pointer and text (and the names linked
    to them), are where you are, so they get the fuchsia: a crisp 1-unit
    #ff2d95 edge on the outline and a faint, short halo past it, the outline
    stroked 3 units wide, blurred by 0.75 and drawn at 60%. It fades out
    about 1.5 px past the edge at 24 px: light around the edge rather than a
    band, so the pointer stays slim and precise. On light and mid backgrounds
    the black body carries it; on dark ones the edge and halo do.
  - Every other cursor is drawn plainly: the black body with a crisp 1-unit
    light edge, #f7f4fa, the light variant's page. On light backgrounds the
    body carries it; on dark ones the edge does. No halo, so resize arrows,
    hands and the rest stay quiet next to the pointer.

Everything scales with the cursor: at 24 px each edge is 1 px. The edges are
strokes centered on the outline, 2 units wide, under a fill of the same
shape, so only their outer half shows and overlapping parts merge into one
silhouette. Corners are mitered, keeping them square, but the miter limit of
1.5 bevels any tip sharper than about 83 degrees; otherwise the arrow's edge
would run past its tip, and the eye would aim with a point that isn't the
hotspot. Details inside a body (sand, the plus on the magnifier) are
fuchsia. The halo is the one soft thing in a theme without shadows: it is
there to find the pointer by, and it fits inside the 24-unit canvas, so the
images stay at their nominal size.

No motion: the theme has none, so wait is a still hourglass with its sand
half run through, and progress is the arrow with a small one. Both read as
busy without animating.

The shapes are square, flat and built on the 24-unit grid, so the 24, 48 and
96 px sizes land on whole pixels. The rounded exceptions are the no-entry
sign and the magnifier's lens, whose meaning is their roundness.

Hotspots are the nd:hotspot attribute on each SVG's root, in grid units. At
size N a hotspot (x, y) lands on pixel (floor(x*N/24), floor(y*N/24)), so a
point on the grid maps to the pixel whose top-left corner it is.

The Xcursor format (see Xcursor(3)). Every number is a little-endian 32-bit
unsigned integer.

    file header   "Xcur"  header size (16)  version (0x10000)  ntoc
    ntoc entries  type  subtype  position   (position: byte offset of chunk)
    image chunk   header size (36)  type (0xfffd0002)  subtype (nominal size)
                  version (1)  width  height  xhot  yhot  delay (ms)
                  width*height pixels, ARGB with premultiplied alpha, rows
                  top to bottom

A file holds one image per nominal size (more, for an animation, with delay
set; there are none here). The loader picks the nominal size closest to the
one asked for. Images here are square and as wide as their nominal size.
"""

import os
import shutil
import struct
import subprocess
import sys
import tempfile
import zlib
from math import floor
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "cursor" / "src"
OUT = ROOT / "icons" / "Neon-Doll-Cursors"
SIZES = (24, 32, 48, 64, 96)
GRID = 24
ND = "{https://github.com/mishan/neon-doll}"

INDEX_THEME = """\
[Icon Theme]
Name=Neon Doll Cursors
Comment=Black cursors; the everyday pointers edged in fuchsia, with a faint halo
Inherits=Adwaita
"""

# Link name -> cursor. The first block mirrors Adwaita's cursors/ directory,
# so every name GNOME resolves through Adwaita resolves here too; move and
# dnd-move point at the plain arrow there as well. The second block is names
# Adwaita lacks: those GDK's X11 backend falls back to, and Qt's.
ALIASES = {
    "arrow": "default",
    "bd_double_arrow": "nwse-resize",
    "bottom_left_corner": "sw-resize",
    "bottom_right_corner": "se-resize",
    "bottom_side": "s-resize",
    "cross": "crosshair",
    "cross_reverse": "crosshair",
    "diamond_cross": "crosshair",
    "dnd-ask": "context-menu",
    "dnd-move": "default",
    "fd_double_arrow": "nesw-resize",
    "fleur": "all-resize",
    "hand1": "grab",
    "hand2": "pointer",
    "left_ptr": "default",
    "left_side": "w-resize",
    "move": "default",
    "question_arrow": "help",
    "right_side": "e-resize",
    "sb_h_double_arrow": "ew-resize",
    "sb_v_double_arrow": "ns-resize",
    "tcross": "crosshair",
    "top_left_arrow": "default",
    "top_left_corner": "nw-resize",
    "top_right_corner": "ne-resize",
    "top_side": "n-resize",
    "watch": "wait",
    "xterm": "text",

    "crossed_circle": "not-allowed",
    "dnd-copy": "copy",
    "dnd-link": "alias",
    "dnd-none": "no-drop",
    "h_double_arrow": "ew-resize",
    "hand": "pointer",
    "left_ptr_watch": "progress",
    "plus": "cell",
    "v_double_arrow": "ns-resize",
    "closedhand": "grabbing",
    "forbidden": "not-allowed",
    "ibeam": "text",
    "openhand": "grab",
    "pointing_hand": "pointer",
    "size_all": "all-resize",
    "size_bdiag": "nesw-resize",
    "size_fdiag": "nwse-resize",
    "size_hor": "ew-resize",
    "size_ver": "ns-resize",
    "split_h": "col-resize",
    "split_v": "row-resize",
    "whats_this": "help",
}


# --- rendering ---------------------------------------------------------------

def renderer():
    if shutil.which("rsvg-convert"):
        return lambda svg, n, out: ["rsvg-convert", "-w", str(n), "-h", str(n),
                                    "-o", out, svg]
    if shutil.which("inkscape"):
        return lambda svg, n, out: ["inkscape", "-w", str(n), "-h", str(n),
                                    "--export-png-color-mode=RGBA_8",
                                    f"--export-filename={out}", svg]
    # ImageMagick only when it hands SVG to librsvg: its own renderer, MSVG,
    # skips the stroked edges and the transformed shapes.
    for magick in ("magick", "convert"):
        if shutil.which(magick):
            formats = subprocess.run([magick, "-list", "format"], text=True,
                                     capture_output=True).stdout
            if any(line.split()[:1] == ["SVG"] and "RSVG" in line
                   for line in formats.splitlines()):
                return lambda svg, n, out, m=magick: [
                    m, "-background", "none", "-density", str(72 * n // GRID),
                    svg, "-resize", f"{n}x{n}", f"PNG32:{out}"]
    sys.exit("need rsvg-convert (librsvg), inkscape, or ImageMagick built "
             "with librsvg to render the SVGs")


def read_png(data):
    """Decode an 8-bit, non-interlaced RGB or RGBA PNG into RGBA rows."""
    pos, chunks = 8, {}
    while pos < len(data):
        length, kind = struct.unpack(">I4s", data[pos:pos + 8])
        chunks.setdefault(kind, []).append(data[pos + 8:pos + 8 + length])
        pos += 12 + length
    width, height, depth, ctype, _, _, interlace = struct.unpack(
        ">IIBBBBB", chunks[b"IHDR"][0])
    if depth != 8 or ctype not in (2, 6) or interlace:
        raise ValueError(f"unsupported PNG: depth {depth}, type {ctype}")
    bpp = 4 if ctype == 6 else 3
    raw = zlib.decompress(b"".join(chunks[b"IDAT"]))
    stride, rows, prev = width * bpp, [], bytearray(width * bpp)
    for y in range(height):
        f = raw[y * (stride + 1)]
        line = bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        for i in range(stride):
            a = line[i - bpp] if i >= bpp else 0
            b = prev[i]
            c = prev[i - bpp] if i >= bpp else 0
            if f == 1:
                line[i] = (line[i] + a) & 255
            elif f == 2:
                line[i] = (line[i] + b) & 255
            elif f == 3:
                line[i] = (line[i] + (a + b) // 2) & 255
            elif f == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pred = a if pa <= pb and pa <= pc else b if pb <= pc else c
                line[i] = (line[i] + pred) & 255
        prev = line
        if bpp == 3:
            line = bytearray(b for i in range(0, stride, 3)
                             for b in (*line[i:i + 3], 255))
        rows.append(bytes(line))
    return width, height, rows


# --- Xcursor -----------------------------------------------------------------

IMAGE = 0xFFFD0002


def xcursor(images):
    """images: [(nominal, width, height, xhot, yhot, rgba_rows)], one per size."""
    toc_end = 16 + 12 * len(images)
    header = struct.pack("<4sIII", b"Xcur", 16, 0x10000, len(images))
    toc, body = b"", b""
    for nominal, w, h, xhot, yhot, rows in images:
        toc += struct.pack("<III", IMAGE, nominal, toc_end + len(body))
        pixels = bytearray()
        for row in rows:
            for i in range(0, len(row), 4):
                r, g, b, a = row[i:i + 4]
                pm = lambda c: (c * a + 127) // 255  # noqa: E731
                pixels += struct.pack("<I", a << 24 | pm(r) << 16 | pm(g) << 8 | pm(b))
        body += struct.pack("<9I", 36, IMAGE, nominal, 1, w, h, xhot, yhot, 0)
        body += pixels
    return header + toc + body


def read_xcursor(data):
    """Parse an Xcursor file back: [(nominal, w, h, xhot, yhot, delay, argb)]."""
    magic, hsize, _, ntoc = struct.unpack("<4sIII", data[:16])
    if magic != b"Xcur":
        raise ValueError("not an Xcursor file")
    out = []
    for i in range(ntoc):
        kind, subtype, pos = struct.unpack("<III", data[hsize + 12 * i:hsize + 12 * i + 12])
        if kind != IMAGE:
            continue
        hdr = struct.unpack("<9I", data[pos:pos + 36])
        if hdr[1] != IMAGE or hdr[2] != subtype:
            raise ValueError("chunk header doesn't match its table entry")
        w, h = hdr[4], hdr[5]
        argb = struct.unpack(f"<{w * h}I", data[pos + 36:pos + 36 + 4 * w * h])
        out.append((subtype, w, h, hdr[6], hdr[7], hdr[8], argb))
    return out


# --- build -------------------------------------------------------------------

def hotspot(svg):
    root = ElementTree.parse(svg).getroot()
    x, y = (float(v) for v in root.get(ND + "hotspot").split())
    return x, y


def build(out):
    render = renderer()
    cursors = out / "cursors"
    if out.exists():
        shutil.rmtree(out)
    cursors.mkdir(parents=True)
    (out / "index.theme").write_text(INDEX_THEME)
    names = sorted(p.stem for p in SRC.glob("*.svg"))
    with tempfile.TemporaryDirectory() as tmp:
        for name in names:
            svg = SRC / f"{name}.svg"
            hx, hy = hotspot(svg)
            images = []
            for n in SIZES:
                png = Path(tmp) / f"{name}-{n}.png"
                subprocess.run(render(str(svg), n, str(png)), check=True,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                w, h, rows = read_png(png.read_bytes())
                xhot = min(w - 1, floor(hx * n / GRID))
                yhot = min(h - 1, floor(hy * n / GRID))
                images.append((n, w, h, xhot, yhot, rows))
            (cursors / name).write_bytes(xcursor(images))
    for link, target in sorted(ALIASES.items()):
        if target not in names:
            sys.exit(f"alias {link} points at {target}, which has no SVG")
        if link in names:
            sys.exit(f"{link} is both a cursor and an alias")
        os.symlink(target, cursors / link)
    return names


def snapshot(out):
    """Everything under out: files by content, links by target."""
    got = {}
    for p in sorted(out.rglob("*")):
        rel = str(p.relative_to(out))
        if p.is_symlink():
            got[rel] = ("link", os.readlink(p))
        elif p.is_file():
            got[rel] = ("file", p.read_bytes())
    return got


def same_cursor(a, b, tolerance=8):
    """Equal up to renderer antialiasing: same sizes and hotspots, and no
    channel more than `tolerance` apart."""
    ia, ib = read_xcursor(a), read_xcursor(b)
    if [i[:6] for i in ia] != [i[:6] for i in ib]:
        return False
    for x, y in zip(ia, ib):
        for p, q in zip(x[6], y[6]):
            if p != q and any(abs((p >> s & 255) - (q >> s & 255)) > tolerance
                              for s in (0, 8, 16, 24)):
                return False
    return True


def check():
    with tempfile.TemporaryDirectory() as tmp:
        fresh = Path(tmp) / OUT.name
        build(fresh)
        want, have = snapshot(fresh), snapshot(OUT) if OUT.exists() else {}
    stale = sorted(set(want) ^ set(have))
    for rel in sorted(set(want) & set(have)):
        (kw, vw), (kh, vh) = want[rel], have[rel]
        if kw != kh or (vw != vh and not (kw == "file" and rel.startswith("cursors/")
                                          and same_cursor(vw, vh))):
            stale.append(rel)
    if stale:
        print(f"{OUT.relative_to(ROOT)} is stale; run tools/build-cursor.py:",
              *stale, sep="\n  ", file=sys.stderr)
        return 1
    print(f"{OUT.relative_to(ROOT)} is up to date")
    return 0


# --- contact sheets ----------------------------------------------------------

def photo(w, h):
    """A busy, photo-like field: smooth color, hard-edged patches of black,
    white and fuchsia, and grain. Seeded, so the sheet is reproducible."""
    import random
    from PIL import Image, ImageDraw, ImageFilter
    rnd = random.Random(7)
    img = Image.new("RGB", (16, 6))
    img.putdata([tuple(rnd.randrange(256) for _ in range(3)) for _ in range(96)])
    img = img.resize((w, h), Image.BICUBIC)
    d = ImageDraw.Draw(img)
    for _ in range(60 * w * h // (1272 * 342)):
        x, y = rnd.randrange(w), rnd.randrange(h)
        c = rnd.choice([(255, 255, 255), (0, 0, 0), (255, 45, 149),
                        (200, 0, 106), (247, 244, 250), (15, 13, 20)])
        d.rectangle((x, y, x + rnd.randrange(8, 90), y + rnd.randrange(4, 40)), fill=c)
    img = img.filter(ImageFilter.GaussianBlur(1.2))
    noise = Image.frombytes("L", (w, h), rnd.randbytes(w * h)).convert("RGB")
    return Image.blend(img, noise, 0.25)


def image(theme, name, n):
    """One size of a built cursor as a PIL image, and its hotspot."""
    from PIL import Image
    for nominal, w, h, _, _, _, argb in read_xcursor((theme / "cursors" / name).read_bytes()):
        if nominal == n:
            data = bytearray()
            for p in argb:
                a = p >> 24
                un = lambda c: min(255, (c * 255 + a // 2) // a) if a else 0  # noqa: E731
                data += bytes((un(p >> 16 & 255), un(p >> 8 & 255), un(p & 255), a))
            return Image.frombytes("RGBA", (w, h), bytes(data))
    raise KeyError(f"{name} has no {n}px image")


def sheet(path):
    """Every cursor at 64 and 32 px on dark, light, mid grey and a busy,
    photo-like field with fuchsia in it, drawn from the built files."""
    from PIL import Image, ImageDraw, ImageFont

    names = sorted(p.stem for p in SRC.glob("*.svg"))
    cols, cell_w, cell_h, label_h, pad = 12, 104, 92, 14, 12
    rows = -(-len(names) // cols)
    band_w, band_h = cols * cell_w + 2 * pad, rows * (cell_h + label_h) + 2 * pad
    head = 26
    try:
        font = ImageFont.truetype("DejaVuSansMono.ttf", 11)
        hfont = ImageFont.truetype("DejaVuSansMono.ttf", 13)
    except OSError:
        font = hfont = ImageFont.load_default()

    bands = [("dark #0f0d14", Image.new("RGB", (band_w, band_h), "#0f0d14")),
             ("light #f7f4fa", Image.new("RGB", (band_w, band_h), "#f7f4fa")),
             ("mid grey #808080", Image.new("RGB", (band_w, band_h), "#808080")),
             ("busy photo-like noise, fuchsia included", photo(band_w, band_h))]
    out = Image.new("RGB", (band_w, len(bands) * (band_h + head)), "#16131d")
    draw = ImageDraw.Draw(out)

    tiles = {(name, n): image(OUT, name, n) for name in names for n in (64, 32)}
    for b, (title, bg) in enumerate(bands):
        top = b * (band_h + head)
        draw.text((pad, top + 6), title, fill="#ebe6f0", font=hfont)
        band = bg.copy()
        bd = ImageDraw.Draw(band)
        for i, name in enumerate(names):
            x = pad + (i % cols) * cell_w
            y = pad + (i // cols) * (cell_h + label_h)
            band.paste(tiles[name, 64], (x + 2, y + 6), tiles[name, 64])
            band.paste(tiles[name, 32], (x + 68, y + 38), tiles[name, 32])
            bd.rectangle((x, y + cell_h - 4, x + cell_w - 6, y + cell_h + label_h - 4),
                         fill="#16131d")
            bd.text((x + 3, y + cell_h - 3), name, fill="#ebe6f0", font=font)
        out.paste(band, (0, top + head))
    out.save(path, optimize=True)
    print(path)


def main():
    args = sys.argv[1:]
    if args[:1] == ["--check"]:
        return check()
    if args[:1] == ["--sheet"] and len(args) == 2:
        sheet(args[1])
        return 0
    if args:
        print(__doc__.split("\n\n")[1], file=sys.stderr)
        return 2
    names = build(OUT)
    print(f"{OUT.relative_to(ROOT)}: {len(names)} cursors, {len(ALIASES)} links, "
          f"sizes {', '.join(map(str, SIZES))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
