"""Preview renderer and generator harness for the CLASSIC (ns.Framed) themes.

Usage:  python -B tools/classic_borders.py <Race> [--preview DIR] [--no-write]

<Race> names tools/classic_races/<Race>.py with the module contract:
  THEME       dict of ns.Framed options (Name, Background, BackgroundInset, BackgroundTileSize,
              Color, Slice, Outset, TitleY, Close{X,Y}, Search=(point,x,y), Menu{X,Y}, CrestScale,
              TabEdge, TabAccent, TabEdgeSize, ArtBelow, TabsX).  Background = "SOLID" or a file
              name in textures/.
  BORDER()    -> PIL RGBA image (the nine-slice source texture)
  BACKGROUND()  optional -> PIL image for the tiled/stretched fill
  CREST       optional path; default textures/<Race>Crest.png

Engine facts this mirrors (BetterBags sonata/apply.lua + decoration.lua):
  * border: SetTextureSliceMargins(S,S,S,S) + Enum.UITextureSliceMode.Tiled, region = window
    expanded by Outset on every side (Inset = -Outset)  [apply.lua:141-144, Shared.lua:160-168]
  * corners S x S fixed, edges + centre tile at NATIVE scale (1 texel = 1 unit), from the start
    (left / top) of each segment, the last partial tile cropped.
  * backdrop: SetBackdrop insets = -BackgroundInset (fill reaches that far outside)
    [decoration.lua:436-446]; Tile+TileSize tiles the file at TileSize from the top left.
"""
import importlib.util
import os
import sys
import argparse
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEX = os.path.join(ROOT, "textures")


# ---------------------------------------------------------------- helpers
def _font(size, bold=True):
    for name in ("arialbd.ttf" if bold else "arial.ttf", "DejaVuSans-Bold.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def tint(img, color):
    """Multiply an RGBA image by an RGBA colour (floats 0..1), as SetVertexColor does."""
    a = np.asarray(img.convert("RGBA"), dtype=np.float32)
    c = np.array(color if len(color) == 4 else list(color) + [1], dtype=np.float32)
    return Image.fromarray(np.clip(a * c, 0, 255).astype(np.uint8), "RGBA")


def tile_fill(src, w, h, tw=None, th=None):
    """Tile src over w x h from the top left, at tw x th (default native), crop the remainder."""
    if tw is not None and (tw, th or tw) != src.size:
        src = src.resize((tw, th or tw), Image.BILINEAR)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sw, sh = src.size
    for y in range(0, h, sh):
        for x in range(0, w, sw):
            out.paste(src, (x, y))
    return out


def sliced_border(tex, w, h, S, draw_center=True):
    """Nine-slice `tex` into w x h like SliceMode Tiled with margins S on all sides."""
    tex = tex.convert("RGBA")
    tw, th = tex.size
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if w < 2 * S or h < 2 * S:
        return out  # degenerate, corners would overlap
    def part(box):
        return tex.crop(box)
    ex, ey = tw - 2 * S, th - 2 * S  # edge tile length along x / y
    out.alpha_composite(part((0, 0, S, S)), (0, 0))
    out.alpha_composite(part((tw - S, 0, tw, S)), (w - S, 0))
    out.alpha_composite(part((0, th - S, S, th)), (0, h - S))
    out.alpha_composite(part((tw - S, th - S, tw, th)), (w - S, h - S))
    segw, segh = w - 2 * S, h - 2 * S
    if ex > 0:
        out.alpha_composite(tile_fill(part((S, 0, tw - S, S)), segw, S), (S, 0))
        out.alpha_composite(tile_fill(part((S, th - S, tw - S, th)), segw, S), (S, h - S))
    if ey > 0:
        out.alpha_composite(tile_fill(part((0, S, S, th - S)), S, segh), (0, S))
        out.alpha_composite(tile_fill(part((tw - S, S, tw, th - S)), S, segh), (w - S, S))
    if draw_center and ex > 0 and ey > 0:
        out.alpha_composite(tile_fill(part((S, S, tw - S, th - S)), segw, segh), (S, S))
    return out


# ---------------------------------------------------------------- seam checker
def check_border(tex, S):
    """Return (lines, ok): max difference across each tiled edge's wrap, and centre alpha."""
    a = np.asarray(tex.convert("RGBA"), dtype=np.float32)
    th, tw = a.shape[:2]
    lines, ok = [], True
    lines.append(f"texture {tw}x{th}, slice {S}")
    if 2 * S >= tw or 2 * S >= th:
        return lines + ["FAIL: 2*Slice >= texture size, no edge/centre left to tile"], False

    def pm(x):  # premultiplied, so invisible RGB under alpha 0 does not matter
        return np.concatenate([x[..., :3] * (x[..., 3:4] / 255.0), x[..., 3:4]], axis=-1)

    def wrap(name, strip, axis):
        """strip: the edge region; axis 1 = tiles along x, 0 = along y. Compares the wrap pair
        (last -> first line) with the p95 step between neighbouring lines inside the strip."""
        nonlocal ok
        s = pm(strip)
        first, last = (s[:, 0], s[:, -1]) if axis == 1 else (s[0], s[-1])
        d = float(np.abs(first - last).max())
        other = 0 if axis == 1 else 1
        inner = float(np.percentile(np.abs(np.diff(s, axis=axis)).max(axis=(other, 2)), 95))
        bad = d > max(24, 1.25 * inner)
        if bad:
            ok = False
        lines.append(f"  {name:<12} wrap step {d:6.1f} vs p95 inner step {inner:6.1f}  {'SEAM' if bad else 'ok'}")

    wrap("top (x)", a[0:S, S:tw - S], 1)
    wrap("bottom (x)", a[th - S:th, S:tw - S], 1)
    wrap("left (y)", a[S:th - S, 0:S], 0)
    wrap("right (y)", a[S:th - S, tw - S:tw], 0)
    cm = float(a[S:th - S, S:tw - S, 3].max())
    lines.append(f"  centre alpha max {cm:.0f} {'ok' if cm == 0 else 'NOT TRANSPARENT'}")
    if cm != 0:
        ok = False
    return lines, ok


# ---------------------------------------------------------------- renderer
def _world(w, h, seed=7):
    rng = random.Random(seed)
    img = Image.new("RGB", (w, h), (34, 44, 30))
    d = ImageDraw.Draw(img)
    for _ in range(90):
        x, y = rng.randrange(w), rng.randrange(h)
        r = rng.randrange(20, 110)
        c = rng.choice([(70, 90, 50), (50, 70, 90), (110, 90, 60), (24, 30, 24), (90, 60, 60), (160, 150, 120)])
        d.ellipse((x - r, y - r, x + r, y + r), fill=c)
    return img.filter(ImageFilter.GaussianBlur(18)).convert("RGBA")


def _close_button(img, right, top, X, Y):
    # Blizzard UIPanelCloseButton: 32x32 with its TOPRIGHT at the offset (X right, Y up)
    x0, y0 = right + X - 32, top - Y
    d = ImageDraw.Draw(img)
    d.ellipse((x0 + 3, y0 + 3, x0 + 29, y0 + 29), fill=(120, 20, 18, 255), outline=(220, 170, 40, 255), width=2)
    d.line((x0 + 10, y0 + 10, x0 + 22, y0 + 22), fill=(255, 220, 120, 255), width=3)
    d.line((x0 + 22, y0 + 10, x0 + 10, y0 + 22), fill=(255, 220, 120, 255), width=3)


def render_bag(theme, border_img, crest_img, width, height, out_path=None,
               background_img=None, zoom_corner=None):
    """Mock a classic bag. `width` x `height` is the WINDOW; 1 texel = 1 UI unit."""
    S = theme["Slice"]
    outset = theme["Outset"]
    bginset = theme.get("BackgroundInset", 0)
    reach = max(outset, bginset)
    below = max(theme.get("ArtBelow", outset), bginset)
    title_y = theme["TitleY"]
    close = theme["Close"]
    menu = theme["Menu"]
    scale = theme.get("CrestScale", 0.25)
    pad = 50
    left = pad + max(reach, -menu["X"], 0)
    top = pad + max(reach, title_y + 30, close["Y"] + 32, menu["Y"])
    W = left + width + pad + max(reach, close["X"])
    H = top + height + pad + below + 30
    canvas = _world(W, H)
    wl, wt, wr, wb = left, top, left + width, top + height

    color = theme.get("Color", (1, 1, 1, 1))
    bgname = theme.get("Background", "SOLID")
    tilesize = theme.get("BackgroundTileSize")

    def fill_img(w, h):
        if bgname in ("SOLID", None) and background_img is None:
            base = Image.new("RGBA", (w, h), (255, 255, 255, 255))
        else:
            src = background_img
            if src is None:
                src = Image.open(os.path.join(TEX, bgname))
            src = src.convert("RGBA")
            if tilesize:
                base = tile_fill(src, w, h, tilesize, tilesize)
            else:
                base = src.resize((w, h), Image.BILINEAR)
        return tint(base, color)

    canvas.alpha_composite(fill_img(width + 2 * bginset, height + 2 * bginset), (wl - bginset, wt - bginset))

    # item slots: 37x37, 4 gap, 10 side padding, 30 header band
    d = ImageDraw.Draw(canvas)
    rng = random.Random(3)
    cols = max(1, (width - 20 + 4) // 41)
    rows = max(1, (height - 40 + 4) // 41)
    for r in range(rows):
        for c in range(cols):
            x, y = wl + 10 + c * 41, wt + 30 + r * 41
            if x + 37 > wr - 8 or y + 37 > wb - 8:
                continue
            d.rectangle((x, y, x + 36, y + 36), fill=(12, 12, 14, 200), outline=(70, 70, 74, 255))
            if rng.random() < 0.55:
                col = (rng.randrange(60, 230), rng.randrange(60, 230), rng.randrange(60, 230), 255)
                d.rectangle((x + 4, y + 4, x + 32, y + 32), fill=col, outline=(0, 0, 0, 255))

    canvas.alpha_composite(
        sliced_border(border_img, width + 2 * outset, height + 2 * outset, S), (wl - outset, wt - outset))

    d = ImageDraw.Draw(canvas)
    d.text(((wl + wr) / 2, wt - title_y + 15), "Backpack", font=_font(14), fill=(255, 210, 0, 255), anchor="mm")

    pt, sx, sy = theme.get("Search", ("TOPRIGHT", -22, -2))
    if pt == "TOP":
        sl = (wl + wr) / 2 + sx - 75
    else:
        sl = wr + sx - 150
    d.rectangle((sl, wt - sy, sl + 150, wt - sy + 20), fill=(0, 0, 0, 170), outline=(120, 120, 120, 255))
    d.text((sl + 8, wt - sy + 10), "Search", font=_font(11, False), fill=(150, 150, 150, 255), anchor="lm")

    _close_button(canvas, wr, wt, close["X"], close["Y"])
    if crest_img is not None:
        # Sonata sizes the bag button 40x40 (elements.lua StyleBagButton), anchors it by its TOPLEFT at
        # Menu, and draws the crest centred on it (bagArt: SetPoint("CENTER", owner, "CENTER")).
        cw, ch = round(275 * scale), round(350 * scale)
        cx, cy = wl + menu["X"] + 20, wt - menu["Y"] + 20
        canvas.alpha_composite(crest_img.convert("RGBA").resize((cw, ch), Image.LANCZOS),
                               (round(cx - cw / 2), round(cy - ch / 2)))

    # tabs: their art starts `below` under the window
    tab_top, tab_h, tab_w, gap = wb + below, 24, 70, 4
    tabx = wl + theme.get("TabsX", 0)
    edge_sz = theme.get("TabEdgeSize", 2)
    for i, (label, selected) in enumerate((("Bags", True), ("Bank", False))):
        x0 = tabx + i * (tab_w + gap)
        canvas.alpha_composite(fill_img(tab_w, tab_h), (x0, tab_top))
        if selected:
            canvas.alpha_composite(Image.new("RGBA", (tab_w, tab_h), (255, 255, 255, 31)), (x0, tab_top))
        ec = tuple(int(v * 255) for v in (theme["TabAccent"] if selected else theme["TabEdge"]))
        ed = ImageDraw.Draw(canvas)
        for k in range(edge_sz):
            ed.rectangle((x0 + k, tab_top + k, x0 + tab_w - 1 - k, tab_top + tab_h - 1 - k), outline=ec)
        ed.text((x0 + tab_w / 2, tab_top + tab_h / 2 - 1), label, font=_font(12, False),
                fill=(255, 255, 255, 255) if selected else (204, 204, 204, 255), anchor="mm",
                stroke_width=1, stroke_fill=(0, 0, 0, 255))

    if out_path:
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        canvas.convert("RGB").save(out_path)
    if zoom_corner:
        x0, y0 = max(0, wl - reach - 20), max(0, wt - reach - 20)
        size = reach + 190
        crop = canvas.crop((x0, y0, x0 + size, y0 + size))
        crop = crop.resize((crop.width * 2, crop.height * 2), Image.NEAREST).convert("RGB")
        os.makedirs(os.path.dirname(zoom_corner) or ".", exist_ok=True)
        crop.save(zoom_corner)
    return canvas


# ---------------------------------------------------------------- CLI
def load_module(race):
    path = os.path.join(ROOT, "tools", "classic_races", race + ".py")
    spec = importlib.util.spec_from_file_location("classic_race_" + race, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("race")
    ap.add_argument("--preview", help="directory for preview PNGs")
    ap.add_argument("--no-write", action="store_true", help="do not write textures/")
    a = ap.parse_args(argv)

    mod = load_module(a.race)
    theme = mod.THEME
    border = mod.BORDER().convert("RGBA")
    bg = mod.BACKGROUND() if hasattr(mod, "BACKGROUND") else None
    crest_path = getattr(mod, "CREST", None) or os.path.join(TEX, a.race + "Crest.png")
    crest = Image.open(crest_path) if os.path.exists(crest_path) else None
    if crest is None:
        print("warning: no crest at", crest_path)

    lines, ok = check_border(border, theme["Slice"])
    print("\n".join(lines))
    print("SEAM CHECK:", "PASS" if ok else "FAIL")

    if not a.no_write:
        border.save(os.path.join(TEX, a.race + "Border.png"))
        print("wrote textures/%sBorder.png" % a.race)
        if bg is not None:
            bg.save(os.path.join(TEX, a.race + "Background.png"))
            print("wrote textures/%sBackground.png" % a.race)
    if a.preview:
        render_bag(theme, border, crest, 420, 520, os.path.join(a.preview, a.race + "_large.png"),
                   bg, zoom_corner=os.path.join(a.preview, a.race + "_corner2x.png"))
        render_bag(theme, border, crest, 220, 260, os.path.join(a.preview, a.race + "_small.png"), bg)
        print("previews ->", a.preview)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
