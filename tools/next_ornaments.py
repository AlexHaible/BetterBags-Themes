#!/usr/bin/env python3
# Makes the art of this addon's BetterBags Next themes (themes/next/*.lua): the ornaments BetterBags draws on a Next
# bag's body (BetterBags' Panel.Ornaments, .claude/rules/next-themes.md §12 in BetterBags), high-resolution pieces
# drawn as signed-distance shapes (tapered tubes along curves, leaves, gems, metal), shaded under a light from the
# top left, with periodic noise for grain. Strips that repeat down a bag's side are periodic in y. Sizes are powers
# of two, several times what they are drawn at; BetterBags draws them smooth (TRILINEAR). Needs numpy. Run from the
# repository root:
#   python3 tools/next_ornaments.py                  (writes textures/next/<Race>/*.png for every theme)
#   python3 tools/next_ornaments.py NightElf         (one theme)
#   python3 tools/next_ornaments.py --preview DIR    (also writes a mock bag with each theme's ornaments to DIR)
import math
import os
import struct
import sys
import zlib

import numpy as np

OUT = "textures/next"


# --- Files ----------------------------------------------------------------------------------------------------------

def write_png(path, rgb, a):
    # rgb: H x W x 3 in [0, 1], a: H x W in [0, 1], straight (not premultiplied) alpha.
    h, w = a.shape
    data = np.dstack([np.clip(rgb, 0, 1), np.clip(a, 0, 1)])
    raw = np.round(data * 255).astype(np.uint8)
    rows = b"".join(b"\x00" + raw[y].tobytes() for y in range(h))

    def chunk(kind, body):
        return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF)

    header = struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(rows, 9))
                + chunk(b"IEND", b""))


# --- A canvas -------------------------------------------------------------------------------------------------------

class Canvas:
    def __init__(self, w, h, y0=0.0):
        # y0: the y of the canvas's top row, for a strip drawn with margins (Strip).
        self.w, self.h = w, h
        self.rgb = np.zeros((h, w, 3))
        self.a = np.zeros((h, w))
        self.X, self.Y = np.meshgrid(np.arange(w) + 0.5, np.arange(h) + 0.5 + y0)

    def view(self, x0, y0, x1, y1):
        # The part of the canvas between two corners (in its coordinates, so a strip's margins count), as a canvas
        # whose pixels are this one's: painting it paints this. For drawing a small shape without touching the rest.
        ox, oy = self.X[0, 0] - 0.5, self.Y[0, 0] - 0.5
        c0, c1 = max(0, int(math.floor(x0 - ox))), min(self.w, int(math.ceil(x1 - ox)))
        r0, r1 = max(0, int(math.floor(y0 - oy))), min(self.h, int(math.ceil(y1 - oy)))
        if c1 <= c0 or r1 <= r0:
            return None
        v = Canvas.__new__(Canvas)
        v.w, v.h = c1 - c0, r1 - r0
        v.rgb, v.a = self.rgb[r0:r1, c0:c1], self.a[r0:r1, c0:c1]
        v.X, v.Y = self.X[r0:r1, c0:c1], self.Y[r0:r1, c0:c1]
        return v

    def over(self, rgb, alpha):
        # Paints rgb (a color, or H x W x 3) with coverage alpha over the canvas, in place (a view paints its canvas).
        alpha = np.clip(alpha, 0, 1)
        rgb = np.broadcast_to(np.asarray(rgb, dtype=float), self.rgb.shape)
        out = alpha + self.a * (1 - alpha)
        safe = np.where(out > 1e-6, out, 1)
        self.rgb[...] = (rgb * alpha[..., None] + self.rgb * (self.a * (1 - alpha))[..., None]) / safe[..., None]
        self.a[...] = out

    def edge_window(self, margin):
        # 1 inside, falling to 0 at the canvas's edges: a glow never shows the texture's square.
        e = np.minimum(np.minimum(self.X, self.w - self.X), np.minimum(self.Y, self.h - self.Y))
        return smoothstep(0, margin, e)

    def add_glow(self, rgb, alpha, window=True):
        # A light under what is there: painted below the canvas, faded out before the canvas's edges (window; never
        # on a strip that repeats, whose edges meet the next tile's).
        alpha = np.clip(alpha, 0, 1)
        if window:
            alpha = alpha * self.edge_window(min(self.w, self.h) * 0.22)
        rgb = np.broadcast_to(np.asarray(rgb, dtype=float), self.rgb.shape)
        out = self.a + alpha * (1 - self.a)
        safe = np.where(out > 1e-6, out, 1)
        self.rgb[...] = (self.rgb * self.a[..., None] + rgb * (alpha * (1 - self.a))[..., None]) / safe[..., None]
        self.a[...] = out

    def save(self, path):
        write_png(path, self.rgb, self.a)


def coverage(d, soft=1.0):
    # A shape's coverage from its signed distance in pixels: one pixel of edge.
    return np.clip(0.5 - d / soft, 0, 1)


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def shift(a, dy, dx):
    # a moved dy rows down and dx columns right, what moves in from the edges empty: a drop shadow's offset. Never
    # np.roll, which wraps round: a strip draws partial copies at its ends so it repeats, and a copy at the bottom
    # wrapped its shadow onto the top rows, a seam where the strip meets its next tile.
    out = np.zeros_like(a)
    h, w = a.shape
    ys, yd = (slice(0, h - dy), slice(dy, h)) if dy >= 0 else (slice(-dy, h), slice(0, h + dy))
    xs, xd = (slice(0, w - dx), slice(dx, w)) if dx >= 0 else (slice(-dx, w), slice(0, w + dx))
    out[yd, xd] = a[ys, xs]
    return out


def blur(a, radius):
    # A separable box blur, three passes (close to a gaussian).
    r = max(1, int(radius))
    out = a.copy()
    for _ in range(3):
        for axis in (0, 1):
            pad = [(0, 0), (0, 0)]
            pad[axis] = (r, r)
            p = np.pad(out, pad, mode="edge")
            c = np.cumsum(p, axis=axis)
            c = np.concatenate([np.zeros_like(np.take(c, [0], axis=axis)), c], axis=axis)
            n = out.shape[axis]
            hi = np.take(c, np.arange(2 * r + 1, 2 * r + 1 + n), axis=axis)
            lo = np.take(c, np.arange(0, n), axis=axis)
            out = (hi - lo) / (2 * r + 1)
    return out


STRIP_MARGIN = 96


def Strip(w, h):
    # A canvas for a strip that repeats down a side, h tall, drawn with STRIP_MARGIN rows above and below: the strip's
    # periodic content runs on into them (drawn again a tile up and a tile down), so a shadow or a blur at either end
    # sees what is really beyond it. crop gives the tile.
    return Canvas(w, h + 2 * STRIP_MARGIN, -STRIP_MARGIN)


def crop(cv):
    m = STRIP_MARGIN
    out = Canvas(cv.w, cv.h - 2 * m)
    out.rgb, out.a = cv.rgb[m:-m].copy(), cv.a[m:-m].copy()
    return out


# --- Noise ----------------------------------------------------------------------------------------------------------

def vnoise(X, Y, cell, seed, period=None):
    # Value noise, about cell pixels per lattice step; periodic in y every period pixels when given.
    rng = np.random.RandomState(seed)
    nx = int(X.max() / cell) + 3
    ny = max(1, int(round(period / cell))) if period else int(Y.max() / cell) + 3
    table = rng.rand(ny, nx)
    # Periodic: the lattice fits the period exactly, so it repeats every period pixels whatever the cell.
    fx = X / cell
    fy = Y * ny / period if period else Y / cell
    ix, iy = np.floor(fx).astype(int), np.floor(fy).astype(int)
    tx, ty = fx - ix, fy - iy
    tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
    ix0, ix1 = np.clip(ix, 0, nx - 1), np.clip(ix + 1, 0, nx - 1)
    iy0, iy1 = iy % ny, (iy + 1) % ny
    a = table[iy0, ix0] * (1 - tx) + table[iy0, ix1] * tx
    b = table[iy1, ix0] * (1 - tx) + table[iy1, ix1] * tx
    return a * (1 - ty) + b * ty


def fbm(X, Y, cell, seed, octaves=4, period=None):
    total, amp, norm = 0.0, 1.0, 0.0
    for o in range(octaves):
        c = cell / (2 ** o)
        if c < 1:
            break
        total = total + amp * vnoise(X, Y, c, seed + o * 17, period)
        norm += amp
        amp *= 0.5
    return total / norm


# --- Light ----------------------------------------------------------------------------------------------------------

LIGHT = np.array([-0.45, -0.55, 0.70])
LIGHT = LIGHT / np.linalg.norm(LIGHT)


def lit(nx, ny, nz):
    return np.clip(nx * LIGHT[0] + ny * LIGHT[1] + nz * LIGHT[2], 0, 1)


def ramp(t, stops):
    # A color ramp: stops are (position, (r, g, b)).
    t = np.clip(t, 0, 1)
    out = np.zeros(t.shape + (3,))
    for i in range(len(stops) - 1):
        p0, c0 = stops[i]
        p1, c1 = stops[i + 1]
        w = np.clip((t - p0) / max(p1 - p0, 1e-9), 0, 1)
        inside = (t >= p0) & (t <= p1) if i < len(stops) - 2 else (t >= p0)
        mix = np.array(c0)[None, None, :] * (1 - w[..., None]) + np.array(c1)[None, None, :] * w[..., None]
        out = np.where(inside[..., None], mix, out)
    out = np.where((t < stops[0][0])[..., None], np.array(stops[0][1])[None, None, :], out)
    return out


# --- Shapes ---------------------------------------------------------------------------------------------------------

def tube(X, Y, pts, radii):
    # A tube along a polyline, its radius varying point to point. Returns (signed distance, across in [-1, 1],
    # the perpendicular's x and y at the nearest point, how far along in [0, 1]).
    pts = np.asarray(pts, dtype=float)
    radii = np.asarray(radii, dtype=float)
    lengths = np.hypot(np.diff(pts[:, 0]), np.diff(pts[:, 1]))
    total = max(lengths.sum(), 1e-9)
    starts = np.concatenate([[0], np.cumsum(lengths)])
    best = np.full(X.shape, np.inf)
    across = np.zeros(X.shape)
    px = np.zeros(X.shape)
    py = np.zeros(X.shape)
    along = np.zeros(X.shape)
    pad = radii.max() + 2
    # Pixel rows and columns from coordinates: a strip's canvas starts above y 0 (Strip).
    ox, oy = X[0, 0] - 0.5, Y[0, 0] - 0.5
    for i in range(len(pts) - 1):
        ax, ay = pts[i]
        bx, by = pts[i + 1]
        x0, x1 = min(ax, bx) - pad - ox, max(ax, bx) + pad - ox
        y0, y1 = min(ay, by) - pad - oy, max(ay, by) + pad - oy
        if x1 < 0 or y1 < 0 or x0 > X.shape[1] or y0 > X.shape[0]:
            continue
        sx = slice(max(0, int(x0)), min(X.shape[1], int(x1) + 1))
        sy = slice(max(0, int(y0)), min(X.shape[0], int(y1) + 1))
        x, y = X[sy, sx], Y[sy, sx]
        dx, dy = bx - ax, by - ay
        l2 = dx * dx + dy * dy
        if l2 == 0:
            continue
        t = np.clip(((x - ax) * dx + (y - ay) * dy) / l2, 0, 1)
        qx, qy = ax + t * dx - x, ay + t * dy - y
        dist = np.hypot(qx, qy)
        r = radii[i] + (radii[i + 1] - radii[i]) * t
        d = dist - r
        l = math.sqrt(l2)
        nxp, nyp = -dy / l, dx / l
        side = np.sign((x - ax) * nxp + (y - ay) * nyp)
        u = np.clip(side * dist / np.maximum(r, 1e-6), -1, 1)
        better = d < best[sy, sx]
        best[sy, sx] = np.where(better, d, best[sy, sx])
        across[sy, sx] = np.where(better, u, across[sy, sx])
        px[sy, sx] = np.where(better, nxp, px[sy, sx])
        py[sy, sx] = np.where(better, nyp, py[sy, sx])
        along[sy, sx] = np.where(better, (starts[i] + t * l) / total, along[sy, sx])
    return best, across, px, py, along


def tube_shade(across, px, py):
    # A tube's light: its normal across it, under the light from the top left.
    nz = np.sqrt(np.clip(1 - across ** 2, 0, 1))
    return lit(px * across, py * across, nz), nz


def leaf(X, Y, base, tip, width, bend=0.0):
    # A leaf from base to tip, width its widest half-width, bend curving its midrib. Returns (signed distance
    # (approximate), across in [-1, 1], how far along in [0, 1]).
    bx, by = base
    tx, ty = tip
    dx, dy = tx - bx, ty - by
    length = math.hypot(dx, dy)
    ux, uy = dx / length, dy / length
    vx, vy = -uy, ux
    rx, ry = X - bx, Y - by
    u = (rx * ux + ry * uy) / length
    v = rx * vx + ry * vy
    v = v - bend * length * np.sin(np.clip(u, 0, 1) * math.pi) * 0.25
    profile = width * np.power(np.clip(np.sin(np.clip(u, 0, 1) * math.pi), 0, 1), 0.75) * (1 - 0.35 * np.clip(u, 0, 1))
    d = np.abs(v) - profile
    d = np.where(u < 0, np.hypot(np.maximum(-u * length, 0), np.maximum(np.abs(v), 0)), d)
    d = np.where(u > 1, np.hypot((u - 1) * length, v), d)
    return d, np.clip(v / np.maximum(profile, 1e-6), -1, 1), u


# --- Leaves -----------------------------------------------------------------------------------------------------------
# Leaves (signed-distance shapes, shaded, two-toned when asked), and the plain bark and leaf colors a piece uses when it
# gives none.

BARK = [(0.0, (0.07, 0.05, 0.04)), (0.35, (0.18, 0.13, 0.10)), (0.7, (0.33, 0.26, 0.20)), (1.0, (0.56, 0.55, 0.58))]
# Leaves by night: deep greens, a moonlit rim on the lit edge.
LEAF_DARK, LEAF_MID, LEAF_LIGHT = (0.025, 0.10, 0.05), (0.08, 0.26, 0.12), (0.30, 0.55, 0.28)
MOONLIT = (0.62, 0.80, 0.92)


def draw_leaf(cv, base, tip, width, seed=1, bend=0.0, colors=(LEAF_DARK, LEAF_MID, LEAF_LIGHT), shadow=0.5,
              rim=MOONLIT, tip_colors=None, rim_amount=0.5, mottle=0.0):
    # tip_colors: a second set of tones the leaf turns to toward its tip (a two-toned leaf).
    # Drawn in a box round the leaf, its shadow's reach and its bend included.
    length = math.hypot(tip[0] - base[0], tip[1] - base[1])
    pad = width + abs(bend) * length * 0.3 + 16
    box = cv.view(min(base[0], tip[0]) - pad, min(base[1], tip[1]) - pad,
                  max(base[0], tip[0]) + pad, max(base[1], tip[1]) + pad)
    if box is None:
        return
    cv = box
    d, v, u = leaf(cv.X, cv.Y, base, tip, width, bend)
    mask = coverage(d)
    if mask.max() <= 0:
        return
    sh = blur(coverage(d - 1), 2)
    sh = shift(sh, 2, 1)
    cv.over((0, 0, 0), sh * shadow * (1 - mask))
    # Lit on the half facing the light, darker on the other; lighter toward the tip.
    dx, dy = tip[0] - base[0], tip[1] - base[1]
    length = math.hypot(dx, dy) or 1
    facing = -(-dy / length * LIGHT[0] + dx / length * LIGHT[1])
    half = smoothstep(-1, 1, v * np.sign(facing + 1e-9))
    rng = np.random.RandomState(seed)
    t = 0.3 + 0.36 * half + 0.22 * np.clip(u, 0, 1) + rng.uniform(-0.06, 0.06)
    dark, mid, light = colors
    color = ramp(t, [(0.0, dark), (0.55, mid), (1.0, light)])
    if tip_colors is not None:
        tdark, tmid, tlight = tip_colors
        toward = smoothstep(0.30, 0.92, np.clip(u, 0, 1) + 0.12 * (half - 0.5))[..., None]
        color = color * (1 - toward) + ramp(t, [(0.0, tdark), (0.55, tmid), (1.0, tlight)]) * toward
    # The midrib, lighter, and veins.
    rib = smoothstep(0.14, 0.0, np.abs(v)) * 0.55
    veins = smoothstep(0.86, 0.98, np.abs(np.sin((u * 6 - np.abs(v) * 1.3) * math.pi))) * 0.22 * (np.abs(v) > 0.12)
    color = color * (1 + rib[..., None] * 0.8 + veins[..., None])
    # Moonlight catching the lit edge, the other edge in shade.
    edge = smoothstep(0.62, 1.0, np.abs(v))
    lit_edge = edge * half
    color = color * (1 - 0.4 * (edge * (1 - half))[..., None])
    color = color * (1 - lit_edge[..., None] * rim_amount) + np.array(rim) * (lit_edge[..., None] * rim_amount)
    if mottle > 0:
        m = fbm(cv.X, cv.Y, 5, seed + 7, 3)
        color = color * (1 + mottle * (m[..., None] - 0.5) * 2)
    cv.over(color, mask)


# --- Night Elf: roots that reach out from the bag, with gaps between them ---------------------------------------------
# Drawn at 4 pixels to a unit. On a full bag the strips run from the top of the screen to the bottom (they are the
# bag's inner border); on a small bag they are drawn at two thirds of that, their ends hidden in roots gripping the
# corners.

NE_EDGE = 384           # The bag's inner edge across the strips: 96 of their 128 units out from the body, 32 in.
NE_SHADOW_TINT = (0.06, 0.05, 0.09)
FUNGUS_GLOW = (0.35, 0.95, 0.90)


def cv_left(cv):
    return cv.X[0, 0] - 0.5


def cv_right(cv):
    return cv.X[0, -1] + 0.5


def bump(y, h, center, width):
    # A bump at center (a share of h) width pixels wide, repeating every h.
    return np.exp(-((((y / h - center + 0.5) % 1.0) - 0.5) * h / width) ** 2)


def ne_sink(cv, edge):
    # What reaches into the bag sinks into its backdrop: darker, then gone, over 30 units past its edge.
    f = 1.0 - smoothstep(edge + 8, edge + 118, cv.X)
    cv.rgb[...] = cv.rgb * (0.35 + 0.65 * f)[..., None]
    cv.a[...] = cv.a * f


def ne_bark(cv, d, u, px, py, seed, period=None, depth=1.0, stops=None, rim_color=None):
    # Bark that follows the root: furrows running along it (noise across the root's width and down the strip, which
    # repeats with the strip), sharp ridges between them, cracks across now and then, moonlight on the lit edge.
    shade, nz = tube_shade(u, px, py)
    across = (u + 1.0) * 90.0 + seed * 7.0
    n = fbm(across, cv.Y * 0.22, 18, seed, 4, period=period * 0.22 if period else None)
    ridge = 1.0 - np.abs(2.0 * n - 1.0)
    furrow = smoothstep(0.50, 0.92, ridge)
    crack = smoothstep(0.80, 0.95, fbm(across * 0.5, cv.Y * 1.6, 14, seed + 5, 2, period=period * 1.6 if period else None))
    tone = (0.16 + 0.66 * shade * (0.78 + 0.30 * n) + 0.10 * shade * (1 - furrow)
            - 0.42 * depth * furrow - 0.14 * depth * crack * (1 - furrow))
    color = ramp(tone, stops or BARK)
    rim = smoothstep(0.50, 0.95, -u) * shade * 0.30
    color = color * (1 - rim[..., None]) + np.array(rim_color or MOONLIT) * rim[..., None]
    color = color * (0.50 + 0.50 * nz[..., None]) + np.array(NE_SHADOW_TINT) * (1 - nz[..., None]) * 0.5
    return color


def ne_roots_weave(cv, strands, period, bark=None):
    # Roots woven by depth: at each pixel the nearest root (its z) is in front; one behind another is shaded where
    # the front one passes over it. strands: (pts, radii, z per point, seed).
    covs, colors, zs = [], [], []
    for pts, radii, z, seed in strands:
        d, u, px, py, al = tube(cv.X, cv.Y, pts, radii)
        covs.append(coverage(d))
        colors.append((bark or ne_bark)(cv, d, u, px, py, seed, period=period))
        zs.append(np.interp(al, np.linspace(0, 1, len(z)), z))
    covs, colors, zs = np.array(covs), np.array(colors), np.array(zs)
    zs = np.where(covs > 0, zs, -1e9)
    order = np.argsort(zs, axis=0)
    for k in range(len(strands)):
        idx = order[k]
        cov = np.take_along_axis(covs, idx[None], axis=0)[0]
        col = np.take_along_axis(colors, idx[None, ..., None].repeat(3, axis=-1), axis=0)[0]
        cv.over(col, cov)
    for k in range(len(strands)):
        front = np.zeros(cv.a.shape)
        for j in range(len(strands)):
            if j != k:
                front = np.maximum(front, covs[j] * (zs[j] > zs[k]))
        cv.over((0.02, 0.015, 0.02), blur(front, 10) * covs[k] * (1 - front) * 0.7)
    return covs


MUSHROOM_CAP = ((0.05, 0.05, 0.14), (0.16, 0.20, 0.42), (0.55, 0.95, 1.0))
MUSHROOM_STEM = [(0.0, (0.16, 0.16, 0.24)), (0.6, (0.48, 0.50, 0.62)), (1.0, (0.78, 0.80, 0.90))]


def glow_mushrooms(cv, x, y, side, size, count, seed):
    # A cluster of Teldrassil's glowing mushrooms growing from a root at (x, y), out toward side (-1: over the
    # feather): each stem leaves the root sideways and curves up; each cap sits level on top, wide and low, dark blue
    # with a glowing rim and gills; the largest drawn first, so smaller ones stand in front.
    rng = np.random.RandomState(seed)
    dark, mid, light = MUSHROOM_CAP
    shrooms = []
    for k in range(count):
        s_ = size * (1.0 - 0.22 * k) * rng.uniform(0.9, 1.1)
        # Spread down the root, alternating above and below the first, each reaching its own way out.
        dy = (0 if k == 0 else (0.42 + 0.18 * k) * size * (1 if k % 2 else -1)) + rng.uniform(-0.08, 0.08) * size
        shrooms.append(dict(size=s_, dy=dy, reach=rng.uniform(0.35, 0.75) * s_,
                            rise=rng.uniform(0.55, 0.85) * s_, lean=rng.uniform(-0.12, 0.12)))
    for m in shrooms:
        s_ = m["size"]
        bx, by = x, y + m["dy"]
        tx, ty = bx + side * m["reach"], by - m["rise"]
        box = cv.view(min(bx, tx) - s_, ty - s_ * 0.8, max(bx, tx) + s_, by + s_ * 0.5)
        if box is None:
            continue
        # The stem: a smooth curve, leaving the root sideways and rising to the cap, emerging from the bark (its first
        # stretch fades in), slimmer toward the cap.
        tt = np.linspace(0, 1, 40)
        cx_, cy_ = bx + side * m["reach"], by
        sx = (1 - tt) ** 2 * (bx - side * s_ * 0.08) + 2 * (1 - tt) * tt * cx_ + tt ** 2 * tx
        sy = (1 - tt) ** 2 * by + 2 * (1 - tt) * tt * cy_ + tt ** 2 * ty
        d, u, px, py, al = tube(box.X, box.Y, list(zip(sx, sy)), s_ * (0.075 - 0.025 * tt))
        emerge = smoothstep(0.0, 0.25, al)
        box.over((0, 0, 0), shift(blur(coverage(d - 1), 2), 2, 1) * 0.3 * (1 - coverage(d)) * emerge)
        shade, nz = tube_shade(u, px, py)
        box.over(ramp(0.25 + 0.6 * shade, MUSHROOM_STEM) * (0.65 + 0.35 * nz[..., None]), coverage(d) * emerge)
        # The cap: a low dome, level, its underside a flat shallow curve.
        rx, ry = s_ * 0.55, s_ * 0.30
        lx = (box.X - tx) / rx - m["lean"] * (box.Y - ty) / ry
        ly = (box.Y - ty) / ry
        upper = np.hypot(lx, np.minimum(ly, 0)) - 1
        lower = ly - 0.28 * (1 - lx ** 2)
        dome = np.maximum(upper, lower) * ry
        mask = coverage(dome)
        box.add_glow(FUNGUS_GLOW, blur(mask * smoothstep(-0.3, 0.3, ly), max(3, s_ * 0.25)) * 0.7, window=False)
        box.over((0, 0, 0), shift(blur(coverage(dome - 1), 2), 3, 1) * 0.3 * (1 - mask))
        nzc = np.sqrt(np.clip(1 - lx ** 2 - np.minimum(ly, 0) ** 2, 0, 1))
        top = lit(lx * 0.8, np.minimum(ly, 0) * 0.8, nzc)
        rim = smoothstep(0.7, 1.0, np.hypot(lx, np.minimum(ly, 0)))
        gills = smoothstep(-0.05, 0.2, ly)
        lines = 0.75 + 0.25 * np.abs(np.sin(lx * 18))
        t = 0.10 + 0.40 * top * (1 - gills) + 0.30 * rim + 0.80 * gills * lines
        color = ramp(np.clip(t, 0, 1), [(0.0, dark), (0.5, mid), (1.0, light)])
        box.over(color, mask)


def ne_leaf_cluster(cv, x, y, out, seed, count=6, size=1.0, spread=(0, 70), leaves=(-40, 95), margin=18, dusk=False,
                    blossoms=0):
    # dusk: the Darnassus look (violet twig, two-toned leaves, lavender rim); blossoms: that many magenta flowers.
    # A twig from a root with leaves on it, reaching out (out -1: over the feather) and drooping, some smaller; made
    # smaller when the art has less room than that on its side (a twig and its leaves reach about 200 pixels at
    # size 1), so nothing is cut off where the art ends.
    room = (x - cv_left(cv) - margin) if out < 0 else (cv_right(cv) - margin - x)
    size = max(0.3, min(size, room / 200.0))
    rng = np.random.RandomState(seed)
    ang0 = math.radians(rng.uniform(*spread))
    tx = x + out * 60 * size * math.cos(ang0)
    ty = y + 60 * size * math.sin(ang0)
    twig = [(x, y), ((x + tx) / 2 + out * 6, (y + ty) / 2 - 10 * size), (tx, ty)]
    box = cv.view(min(x, tx) - 30, min(y, ty) - 30, max(x, tx) + 30, max(y, ty) + 30)
    if box is not None:
        d, u, px, py, al = tube(box.X, box.Y, twig, [7 * size, 5 * size, 2.5 * size])
        box.over((0, 0, 0), shift(blur(coverage(d - 1), 3), 4, 2) * 0.5 * (1 - coverage(d)))
        if dusk:
            box.over(ne_bark(box, d, u, px, py, seed, stops=BARK_DUSK, rim_color=LAVENDER_RIM), coverage(d))
        else:
            box.over(ne_bark(box, d, u, px, py, seed), coverage(d))
    hue = rng.uniform(-0.02, 0.04)
    colors = tuple(tuple(np.clip(np.array(c) + [hue * 0.5, 0, hue], 0, 1)) for c in (LEAF_DARK, LEAF_MID, LEAF_LIGHT))
    tips = None
    rim = MOONLIT
    if dusk:
        colors = tuple(tuple(np.clip(np.array(c) + [0, hue, hue * 0.5], 0, 1)) for c in LEAF_BASE)
        tips = LEAF_TIP
        rim = LAVENDER_RIM
    for k in range(count):
        t = rng.uniform(0.25, 1.0)
        bx = x + (tx - x) * t
        by = y + (ty - y) * t
        ang = math.radians(rng.uniform(*leaves))
        length = rng.uniform(80, 135) * size * (0.6 + 0.4 * t)
        tip = (bx + out * length * math.cos(ang), by + length * math.sin(ang))
        draw_leaf(cv, (bx, by), tip, length * rng.uniform(0.24, 0.32), seed=seed * 10 + k, bend=rng.uniform(0.1, 0.4) * out,
                  colors=colors, rim=rim, tip_colors=tips if (not dusk or rng.rand() < 0.75) else None,
                  rim_amount=0.28 if dusk else 0.5, mottle=0.18 if dusk else 0.0)
    for k in range(blossoms):
        t = rng.uniform(0.5, 1.0)
        draw_blossom(cv, x + (tx - x) * t + rng.uniform(-18, 18) * size, y + (ty - y) * t + rng.uniform(-14, 14) * size,
                     rng.uniform(9, 14) * size, seed * 20 + k)


# --- Night Elf at dusk: Darnassus' look -------------------------------------------------------------------------------
# Asked, with a screenshot just outside Darnassus: "this is what i think of when i think nightelf"; "most leaves in
# nightelf tend to be two toned". Violet light everywhere (violet-plum bark, lavender rim light), teal-emerald moss and
# two-toned leaves, magenta blossoms, cyan-blue wisps; roots that fuse where they meet and are painted (soft forms, grain
# following them, strong rim light), not textured with fine noise; an occasional carved spiral.

BARK_DUSK = [(0.0, (0.05, 0.03, 0.06)), (0.32, (0.18, 0.12, 0.18)), (0.62, (0.33, 0.25, 0.32)),
             (0.85, (0.52, 0.45, 0.53)), (1.0, (0.78, 0.71, 0.82))]
# Old bark's warmer patches, mixed into the violet.
BARK_WARM = (0.34, 0.24, 0.23)
LAVENDER_RIM = (0.80, 0.70, 1.0)
LEAF_BASE = ((0.035, 0.11, 0.09), (0.11, 0.32, 0.25), (0.36, 0.62, 0.46))
LEAF_TIP = ((0.09, 0.06, 0.15), (0.29, 0.20, 0.42), (0.58, 0.47, 0.74))
BLOSSOM = ((0.34, 0.03, 0.24), (0.88, 0.24, 0.62), (1.0, 0.72, 0.90))
MOSS_DUSK = [(0.0, (0.05, 0.18, 0.14)), (1.0, (0.30, 0.70, 0.46))]


def smin(a, b, k):
    # A smooth union of two distance fields: shapes closer than k fuse with a fillet, as roots grow together.
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1)
    return b * (1 - h) + a * h - k * h * (1 - h)


def draw_blossom(cv, x, y, r, seed):
    # A small five-petalled magenta flower, its centre pale.
    rng = np.random.RandomState(seed)
    box = cv.view(x - r * 2, y - r * 2, x + r * 2, y + r * 2)
    if box is None:
        return
    rot = rng.uniform(0, math.pi * 2)
    ang = np.arctan2(box.Y - y, box.X - x) - rot
    rr = np.hypot(box.X - x, box.Y - y)
    petal = r * (0.62 + 0.38 * np.abs(np.cos(ang * 2.5)))
    d = rr - petal
    mask = coverage(d)
    box.over((0, 0, 0), shift(blur(coverage(d - 1), 2), 2, 1) * 0.4 * (1 - mask))
    t = 0.35 + 0.45 * (rr / np.maximum(petal, 1e-6)) + 0.2 * np.cos(ang * 5) * 0.3
    dark, mid, light = BLOSSOM
    color = ramp(np.clip(1.15 - t, 0, 1), [(0.0, dark), (0.5, mid), (1.0, light)])
    box.over(color, mask)
    box.over((1.0, 0.92, 0.75), coverage(rr - r * 0.22))


def ne_paint_roots(cv, strands, seed, period=None, k=16.0, shade=1.0):
    # Roots painted as one mass: every strand fused with the others (a smooth union), lit as a soft form (normals from
    # a blurred silhouette), grain running along the shape (bands of the distance inside it), a strong lavender rim
    # where it faces the moon, a darker violet in its shade. strands: (pts, radii). Returns the mass's distance field.
    d = None
    for pts, radii in strands:
        di, _, _, _, _ = tube(cv.X, cv.Y, pts, radii)
        # tube is infinite where no strand is near: fusing two infinities would make nothing a number.
        di = np.minimum(di, 1e5)
        d = di if d is None else smin(d, di, k)
    mask = coverage(d)
    cv.over((0, 0, 0), shift(blur(coverage(d - 3), 14), 10, 6) * 0.55)
    inside = np.clip(-d, 0, None)
    # A soft dome over the whole width (the distance inside, saturating), and bevels at the edges.
    hgt = 0.55 * (1 - np.exp(-inside / 22.0)) + 0.45 * blur(mask, 6)
    gy, gx = np.gradient(hgt)
    nx, ny = -gx * 10.0, -gy * 10.0
    norm = np.sqrt(nx * nx + ny * ny + 1.0)
    nx, ny, nz = nx / norm, ny / norm, 1.0 / norm
    light = lit(nx, ny, nz)
    toward = np.clip((nx * LIGHT[0] + ny * LIGHT[1]) / np.maximum(np.hypot(nx, ny), 1e-6), 0, 1)
    edge = smoothstep(0.88, 0.35, blur(mask, 5)) * mask
    rim = smoothstep(0.15, 0.65, toward) * edge
    # Shadow in the creases where roots meet (less of the mass around them than its own width).
    crease = smoothstep(0.92, 0.55, blur(mask, 16)) * mask * (1 - edge)
    noise = fbm(cv.X, cv.Y, 60, seed, 3, period=period)
    fine = fbm(cv.X, cv.Y, 9, seed + 4, 3, period=period)
    warm = smoothstep(0.52, 0.70, fbm(cv.X, cv.Y, 110, seed + 9, 3, period=period))
    # Bark: ridged furrows running along the roots (noise across their width, by the distance inside, and down the
    # strip), cracks across them now and then, and grain following the shape, broken into strokes.
    across = inside * 1.7 + noise * 30.0 + seed * 5.0
    n = fbm(across, cv.Y * 0.22, 16, seed + 2, 4, period=period * 0.22 if period else None)
    ridge = 1.0 - np.abs(2.0 * n - 1.0)
    furrow = smoothstep(0.52, 0.93, ridge)
    crack = smoothstep(0.82, 0.96, fbm(across * 0.5, cv.Y * 1.5, 13, seed + 6, 2,
                                       period=period * 1.5 if period else None)) * (1 - furrow)
    grain = 0.5 + 0.5 * np.sin(inside * 0.22 * (0.8 + 0.5 * noise) + noise * 9.0)
    groove = smoothstep(0.86, 0.98, grain) * smoothstep(0.35, 0.6, fine)
    tone = (0.10 + 0.70 * light * (0.82 + 0.25 * n) + 0.08 * light * (1 - furrow) - 0.34 * furrow - 0.14 * crack
            - 0.10 * groove + 0.12 * (fine - 0.5) - 0.18 * crease)
    color = ramp(np.clip(tone, 0, 1), BARK_DUSK) * shade
    color = color * (1 - 0.35 * warm[..., None]) + np.array(BARK_WARM) * (0.35 * warm * np.clip(tone, 0, 1))[..., None]
    color = color * (1 - 0.70 * rim[..., None] * (1 - 0.5 * furrow[..., None])) \
        + np.array(LAVENDER_RIM) * (0.70 * rim * (1 - 0.5 * furrow))[..., None]
    # Pale lichen on the bark, in small patches.
    lichen = smoothstep(0.62, 0.72, fbm(cv.X, cv.Y, 6, seed + 11, 3, period=period)) \
        * smoothstep(0.55, 0.7, fbm(cv.X, cv.Y, 50, seed + 12, 2, period=period)) * (1 - furrow)
    color = color * (1 - 0.5 * lichen[..., None]) + np.array((0.62, 0.66, 0.66)) * (0.5 * lichen * light)[..., None]
    cv.over(color, mask)
    return d


def carved_spiral(cv, d, cx, cy, r, turns, seed):
    # A spiral carved into the bark: a groove (dark) with the light catching its lower lip, only where the mass is.
    t = np.linspace(0, 1, 160)
    a = t * turns * 2 * math.pi + seed
    pts = list(zip(cx + r * t * np.cos(a), cy + r * t * np.sin(a)))
    box = cv.view(cx - r - 10, cy - r - 10, cx + r + 10, cy + r + 10)
    if box is None:
        return
    dg, _, _, _, _ = tube(box.X, box.Y, pts, [2.6] * len(pts))
    lip, _, _, _, _ = tube(box.X, box.Y, [(x + 1.5, y + 2.0) for x, y in pts], [2.0] * len(pts))
    ox, oy = box.X[0, 0] - cv.X[0, 0], box.Y[0, 0] - cv.Y[0, 0]
    r0, c0 = int(round(oy)), int(round(ox))
    inside = coverage(d[r0:r0 + box.h, c0:c0 + box.w] + 6)
    box.over(LAVENDER_RIM, coverage(lip) * (1 - coverage(dg)) * inside * 0.45)
    box.over((0.04, 0.02, 0.06), coverage(dg) * inside * 0.85)


def nightelf_roots(w=512, h=2048):
    # The front roots, drawn over the bag's edge: two great roots (one hugging the edge and dipping into the bag, one
    # wandering out and crossing it), a tendril looping out, another ending in leaves, fused where they meet and
    # painted; leaves (some behind), blossoms, mushrooms, carved spirals. Where they reach into the bag they sink into
    # its backdrop.
    cv = Strip(w, h)
    E = NE_EDGE
    ya = np.arange(-h * 0.12, h * 1.12, 3.0)
    t = np.linspace(0, 1, 160)
    ty0, ty1 = h * 0.10, h * 0.52
    tyy = ty0 + (ty1 - ty0) * t
    txx = (1 - t) * ne_xa(np.array([ty0]), h)[0] + t * ne_xb(np.array([ty1]), h)[0] - 190 * np.sin(math.pi * t) ** 1.3 \
        - 24 * np.sin(math.pi * 3 * t)
    tr = 13 * (1 - 0.45 * np.sin(math.pi * t)) + 2
    t2 = np.linspace(0, 1, 140)
    s0y = h * 0.60
    sx0 = ne_xb(np.array([s0y]), h)[0]
    sxx = sx0 - 150 * t2 + 30 * np.sin(t2 * 5) * t2
    syy = s0y + 240 * t2 + 50 * t2 ** 2
    sr = 11 * (1 - 0.85 * t2) + 1.8
    strands = []
    for off in (-h, 0, h):
        strands.append((list(zip(ne_xa(ya, h), ya + off)), ne_ra(ya, h)))
        strands.append((list(zip(ne_xb(ya, h), ya + off)), ne_rb(ya, h)))
        strands.append((list(zip(txx, tyy + off)), tr))
        strands.append((list(zip(sxx, syy + off)), sr))
    # Leaves behind the roots, for depth: darker, partly covered.
    for off in (-h, 0, h):
        for k, (y, which) in enumerate(((h * 0.13, "a"), (h * 0.70, "b"))):
            fn = ne_xa if which == "a" else ne_xb
            ne_leaf_cluster(cv, fn(np.array([y]), h)[0] + 10, y + off, -1, 630 + k, count=5, size=1.0, spread=(10, 50),
                            dusk=True)
    behind = cv.a.copy()
    cv.over((0.02, 0.0, 0.04), behind * 0.40)
    d = ne_paint_roots(cv, strands, 11, period=h)
    # Moss: teal-emerald, on the lit tops, in patches.
    speck = fbm(cv.X, cv.Y, 7, 91, 3, period=h)
    patch = fbm(cv.X, cv.Y, 70, 93, 3, period=h)
    moss = np.clip((speck - 0.5) * 5, 0, 1) * np.clip((patch - 0.58) * 5, 0, 1) * coverage(d + 6)
    cv.over(ramp(speck, MOSS_DUSK), moss * 0.85)
    # Spirals carved where the roots fuse, widest.
    ys = np.linspace(0, h, 4096, endpoint=False)
    diff = ne_xa(ys, h) - ne_xb(ys, h)
    crossings = [ys[i] for i in range(len(ys)) if (diff[i] > 0) != (diff[(i + 1) % len(ys)] > 0)]
    for k, yc in enumerate(crossings[:2]):
        xc = float(ne_xa(np.array([yc]), h)[0])
        for off in (-h, 0, h):
            carved_spiral(cv, d, xc - 4, yc + off, 22, 2.4, 1.3 + k)
    for off in (-h, 0, h):
        for y, which, n, size in ((h * 0.30, "a", 3, 58), (h * 0.76, "b", 2, 50), (h * 0.47, "a", 2, 42)):
            fn, rf = (ne_xa, ne_ra) if which == "a" else (ne_xb, ne_rb)
            x = fn(np.array([y]), h)[0] - rf(np.array([y]), h)[0] * 0.8
            glow_mushrooms(cv, x, y + off, -1, size, n, 500 + int(y))
        for k, (y, which, out, count, size, bloom) in enumerate(((h * 0.04, "b", -1, 7, 1.15, 4),
                                                                 (h * 0.21, "a", -1, 6, 1.0, 0),
                                                                 (h * 0.40, "b", -1, 5, 0.9, 3),
                                                                 (h * 0.66, "a", -1, 7, 1.1, 0),
                                                                 (h * 0.88, "b", -1, 6, 1.0, 5),
                                                                 (h * 0.55, "a", 1, 3, 0.7, 0))):
            fn, rf = (ne_xa, ne_ra) if which == "a" else (ne_xb, ne_rb)
            x = fn(np.array([y]), h)[0] + out * rf(np.array([y]), h)[0] * 0.5
            ne_leaf_cluster(cv, x, y + off, out, 600 + k, count=count, size=size, dusk=True, blossoms=bloom)
        ne_leaf_cluster(cv, sxx[-1], syy[-1] + off, -1, 650, count=5, size=0.8, spread=(40, 80), leaves=(40, 120),
                        dusk=True, blossoms=3)
    ne_sink(cv, E)
    return crop(cv)


def nightelf_under_roots(w=512, h=2048):
    # The back roots: drawn under the bag's body and its feathered edge (BetterBags draws them on the background
    # layer, below the body), so they reach out from under the bag, darkening as they near it; sinuous, interlacing
    # like the knotwork of roots on the ground at Darnassus, each passing over one and under the next.
    cv = Strip(w, h)
    E = NE_EDGE
    rng = np.random.RandomState(19)
    roots = []
    for k in range(6):
        roots.append(dict(y0=(k + 0.5) * h / 6 + rng.uniform(-40, 40), amp=rng.uniform(60, 110),
                          waves=rng.uniform(1.2, 2.0), phase=rng.uniform(0, 6.28), slope=rng.uniform(-0.25, 0.25),
                          length=rng.uniform(360, 400), r0=rng.uniform(22, 30), zp=rng.uniform(0, 6.28), seed=320 + k))
    strands = []
    for off in (-h, 0, h):
        for r in roots:
            t = np.linspace(0, 1, 160)
            xs = E + 40 - r["length"] * t
            ys = r["y0"] + off + r["slope"] * r["length"] * t + r["amp"] * np.sin(t * r["waves"] * math.pi + r["phase"]) * t
            radii = r["r0"] * (1 - 0.80 * t) + 3
            z = np.cos(t * 9.0 + r["zp"])
            strands.append((list(zip(xs, ys)), radii, z, r["seed"]))
    shadow = np.zeros(cv.a.shape)
    for pts, radii, z, seed in strands:
        dd, _, _, _, _ = tube(cv.X, cv.Y, pts, radii)
        shadow = np.maximum(shadow, coverage(dd - 2))
    cv.over((0, 0, 0), shift(blur(shadow, 10), 8, 4) * 0.5)

    def bark(c, d, u, px, py, seed, period=None):
        return ne_bark(c, d, u, px, py, seed, period=period, stops=BARK_DUSK, rim_color=LAVENDER_RIM, depth=0.5) * 0.9

    ne_roots_weave(cv, strands, period=h, bark=bark)
    return crop(cv)


# The two main roots across a strip h tall (and the small bag's corner pieces, which meet them): one hugging the bag's
# edge and dipping into the bag once a tile, one wandering out over the feather and crossing it twice; both gnarled
# (kinks, knots).
TAU = 2 * math.pi


def ne_xa(y, h):
    E = NE_EDGE
    return (E - 58 - 38 * np.sin(TAU * y / h + 0.4) - 14 * np.sin(TAU * 3 * y / h + 1.7) - 9 * np.sin(TAU * 7 * y / h + 0.3)
            - 5 * np.sin(TAU * 13 * y / h + 2.1) + 70 * bump(y, h, 0.42, 90))


def ne_xb(y, h):
    E = NE_EDGE
    return (E - 170 + 124 * np.sin(TAU * y / h + 3.3) + 18 * np.sin(TAU * 2 * y / h + 0.5)
            + 10 * np.sin(TAU * 6 * y / h + 1.1) + 5 * np.sin(TAU * 11 * y / h + 0.7))


def ne_ra(y, h):
    return 38 * (1 + 0.18 * np.sin(TAU * 2 * y / h + 0.9) + 0.08 * np.sin(TAU * 7 * y / h)
                 + 0.35 * (bump(y, h, 0.18, 26) + bump(y, h, 0.61, 26)))


def ne_rb(y, h):
    return 25 * (1 + 0.20 * np.sin(TAU * 3 * y / h + 2.2) + 0.08 * np.sin(TAU * 9 * y / h + 1)
                 + 0.40 * (bump(y, h, 0.37, 26) + bump(y, h, 0.83, 26)))


def nightelf_corner(w=512, h=256, top=True):
    # A small bag's roots at its top or bottom corner, gripping it: a thick root along the border, from far out over
    # the feather into the bag (where it sinks into the backdrop), its outer end curling, a thinner one fused along it,
    # all painted as one mass. The theme moves this piece out so the border root lies along the bag's edge and hangs
    # past it (asked: the corners reach the bag's edges, past rather than short of them); the strips on a small bag start
    # and end inside these border roots, so the roots always hide where they are cut. At the top the strip begins (the top of its tile) at the border root, and
    # its two roots rise from it on the strip's own lines, fading out toward this piece's bottom, where the strip
    # carries on beneath.
    cv = Canvas(w, h)
    E = NE_EDGE
    band = 48 if top else h - 66
    rng = np.random.RandomState(29 if top else 31)
    tile = 2048
    strands = []
    if top:
        ys = np.arange(band, h + 12, 3.0)
        for fx, fr in ((ne_xa, ne_ra), (ne_xb, ne_rb)):
            strands.append((list(zip(fx(ys - band, tile), ys)), fr(ys - band, tile)))
    t = np.linspace(0, 1, 160)
    xs = E + 100 - (E + 100 - 64) * t
    ys = band + 7 * np.sin(t * 9 + (0 if top else 2)) + 4 * np.sin(t * 23)
    radii = (30 if top else 34) * (1 - 0.35 * t) + 2
    curl = t > 0.86
    cu = (t[curl] - 0.86) / 0.14
    turn = 1 if top else -1
    xs[curl] = xs[curl][0] - 30 * np.sin(cu * 3.6)
    ys[curl] = ys[curl][0] + turn * 30 * (1 - np.cos(cu * 3.6))
    radii[curl] = radii[curl][0] * (1 - 0.7 * cu) + 1
    strands.append((list(zip(xs, ys)), radii))
    xs2 = E + 60 - (E + 60 - 110) * t
    ys2 = band + (1 if top else -1) * (16 * np.sin(t * 6 + 1) + 8)
    strands.append((list(zip(xs2, ys2)), 12 * (1 - 0.5 * t) + 2))
    d = ne_paint_roots(cv, strands, 95 if top else 97)
    if top:
        # Out toward the bottom, where the strip carries on beneath with the same roots.
        fade = 1 - smoothstep(h - 60, h - 6, cv.Y)
    else:
        # The border root's shadow, cast down, fades before the bag's bottom edge.
        fade = 1 - smoothstep(h - 18, h - 3, cv.Y)
    cv.a[...] = cv.a * fade
    carved_spiral(cv, d, E - 150, band, 16, 2.2, 0.7 if top else 2.1)
    glow_mushrooms(cv, E - 210, band + (24 if top else -30), -1, 44, 2, 105 if top else 107)
    for k in range(2):
        x = E - 60 - k * 150 + rng.uniform(-20, 20)
        y = band + (18 if top else -18)
        ne_leaf_cluster(cv, x, y, -1, 810 + k + (0 if top else 10), count=5, size=0.8,
                        spread=(30, 70) if top else (-70, -30), leaves=(0, 110) if top else (-110, 0),
                        dusk=True, blossoms=2 if k == 1 else 0)
    ne_sink(cv, E)
    return cv


def nightelf_bough(w=512, h=512):
    # A great bough growing out from behind the roots: its base at the middle of the art's right side, arching up and
    # out over the feather and drooping, twigs leaving it along its way (fused into it, painted as one mass), leaves
    # along it and heavy at its tips, blossoms among them, mushrooms by its base.
    cv = Canvas(w, h)
    rng = np.random.RandomState(71)
    t = np.linspace(0, 1, 140)
    bx = w - t * 420
    by = h / 2 - 140 * np.sin(t * math.pi * 0.85) + 130 * t ** 2
    br = 30 * (1 - 0.8 * t) + 4
    strands = [(list(zip(bx, by)), br)]
    tips = []
    for k, tt in enumerate((0.30, 0.48, 0.64, 0.80)):
        i0 = int(tt * 139)
        x0, y0 = bx[i0], by[i0]
        dx, dy = bx[min(i0 + 6, 139)] - x0, by[min(i0 + 6, 139)] - y0
        heading = math.atan2(dy, dx) + math.radians(rng.uniform(25, 45) * (1 if k % 2 else -1))
        length = rng.uniform(70, 110)
        tw = np.linspace(0, 1, 30)
        txs = x0 + np.cos(heading) * length * tw
        tys = y0 + np.sin(heading) * length * tw + 18 * tw ** 2
        strands.append((list(zip(txs, tys)), br[i0] * 0.45 * (1 - 0.8 * tw) + 1.5))
        tips.append((txs[-1], tys[-1]))
    d = ne_paint_roots(cv, strands, 73, k=10.0)
    carved_spiral(cv, d, bx[18], by[18], 13, 2.0, 1.9)
    glow_mushrooms(cv, bx[14], by[14] - br[14] * 0.6, -1, 46, 2, 77)
    for k, (x, y) in enumerate(tips + [(bx[-1], by[-1])]):
        ne_leaf_cluster(cv, x, y, -1, 700 + k, count=6, size=0.8, spread=(-20, 60), leaves=(-60, 100), dusk=True,
                        blossoms=3 if k in (1, 4) else 0)
    for k, tt in enumerate((0.40, 0.58, 0.72, 0.90)):
        i0 = int(tt * 139)
        ne_leaf_cluster(cv, bx[i0], by[i0], -1, 720 + k, count=3, size=0.7, spread=(30, 80), leaves=(20, 110), dusk=True)
    return cv


def nightelf_frond(w=256, h=256):
    # A frond of leaves on a short twig, its base at the bottom right: it sways about there.
    cv = Canvas(w, h)
    ne_leaf_cluster(cv, w - 28, h - 28, -1, 760, count=9, size=0.72, spread=(-58, -40), leaves=(-100, 15), dusk=True,
                    blossoms=2)
    return cv


THEMES = {}


def nightelf():
    return {
        "roots": nightelf_roots(),
        "under": nightelf_under_roots(),
        "bough": nightelf_bough(),
        "frond": nightelf_frond(),
        "corner_top": nightelf_corner(top=True),
        "corner_bottom": nightelf_corner(top=False),
    }


THEMES["NightElf"] = nightelf


# --- Previews -------------------------------------------------------------------------------------------------------

def place(dst, src, x, y, w, h, tint=None, add=False, alpha=1.0):
    # Draws a canvas resized (area average) to w x h at (x, y) on dst, tinted (its colors times tint) and faded
    # (alpha), over what is there or added to it (as BetterBags draws an ornament with BlendMode "ADD").
    sh, sw = src.a.shape
    ys = (np.arange(h) + 0.5) * sh / h
    xs = (np.arange(w) + 0.5) * sw / w
    # Box-filter down by averaging a few samples.
    acc_rgb = np.zeros((h, w, 3))
    acc_a = np.zeros((h, w))
    n = 0
    for oy in (-0.25, 0.25):
        for ox in (-0.25, 0.25):
            yy = np.clip(((np.arange(h) + 0.5 + oy) * sh / h).astype(int), 0, sh - 1)
            xx = np.clip(((np.arange(w) + 0.5 + ox) * sw / w).astype(int), 0, sw - 1)
            a = src.a[yy][:, xx]
            acc_rgb += src.rgb[yy][:, xx] * a[..., None]
            acc_a += a
            n += 1
    a = acc_a / n
    rgb = acc_rgb / np.maximum(acc_a, 1e-6)[..., None]
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(dst.w, x + w), min(dst.h, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    sub = (slice(y0 - y, y1 - y), slice(x0 - x, x1 - x))
    region = (slice(y0, y1), slice(x0, x1))
    if tint is not None:
        rgb = rgb * np.array(tint)[None, None, :]
    if add:
        dst.rgb[region] = np.clip(dst.rgb[region] + rgb[sub] * (a[sub] * alpha)[..., None], 0, 1)
        return
    alpha = a[sub] * alpha
    out = alpha + dst.a[region] * (1 - alpha)
    safe = np.where(out > 1e-6, out, 1)
    dst.rgb[region] = (rgb[sub] * alpha[..., None] + dst.rgb[region] * (dst.a[region] * (1 - alpha))[..., None]) / safe[..., None]
    dst.a[region] = out


# The Night Elf theme's ornaments (themes/next/NightElf.lua), for its previews, and where wisps (its sparkles) might be.
NIGHTELF_ORNAMENTS = [
    ("under", dict(Point="INNER", Width=128, Tile=512, X=-96, Sizes="Full", Layer="BACKGROUND")),
    ("bough", dict(Point="TOPINNER", Anchor="TOPOUTER", X=-14, Y=220, Width=128, Height=128, Sizes="Full")),
    ("roots", dict(Point="INNER", Width=128, Tile=512, X=-96, Sizes="Full")),
    ("frond", dict(Point="TOPINNER", Anchor="BOTTOMOUTER", X=-30, Y=120, Width=56, Height=56, Sizes="Full")),
    ("frond", dict(Point="BOTTOMINNER", Anchor="BOTTOMOUTER", X=-40, Y=-140, Width=50, Height=50, Sizes="Full")),
    ("under", dict(Point="INNER", Width=84, Tile=336, X=-63, Start=2, End=2, Sizes="Small", Layer="BACKGROUND")),
    ("roots", dict(Point="INNER", Width=84, Tile=336, X=-63, Start=2, End=2, Sizes="Small")),
    ("corner_top", dict(Point="TOPINNER", X=-63, Y=-6, Width=84, Height=42, Sizes="Small")),
    ("corner_bottom", dict(Point="BOTTOMINNER", X=-63, Y=9, Width=84, Height=42, Sizes="Small")),
    ("frond", dict(Point="TOPINNER", Anchor="BOTTOMOUTER", X=-20, Y=170, Width=44, Height=44, Sizes="Small")),
]
NIGHTELF_BODY = (0.05, 0.035, 0.09, 0.94)
NIGHTELF_WISPS = [(150, 180, 9), (60, 330, 12), (120, 520, 8), (30, 640, 10), (175, 770, 7), (95, 860, 11)]


def preview_nightelf(pieces, path):
    preview_ornaments(pieces, NIGHTELF_ORNAMENTS, NIGHTELF_BODY, (0.86, 0.80, 1.0), path, wisps=NIGHTELF_WISPS)
    preview_ornaments(pieces, NIGHTELF_ORNAMENTS, NIGHTELF_BODY, (0.86, 0.80, 1.0), path.replace(".png", "-small.png"),
                      small=True, wisps=[(x + 40, y * 0.7 + 110, r * 0.8) for x, y, r in NIGHTELF_WISPS])


def crop_rows(src, fraction):
    # The top fraction of a canvas, as a new canvas.
    rows = max(1, int(round(src.h * fraction)))
    out = Canvas(src.w, rows)
    out.rgb, out.a = src.rgb[:rows].copy(), src.a[:rows].copy()
    return out


def preview_ornaments(pieces, ornaments, body, accent, path, unit=1.15, small=False, wisps=()):
    # A mock backpack (its inner side on the left) with a theme's ornaments placed as BetterBags places them
    # (Panel.Ornaments): ornaments is the theme's list, as (piece, spec) pairs whose specs use the theme's keys
    # (Point, Anchor, X, Y, Width, Height, Tile, Start, End, Sizes, Layer). A full bag fills the height with its
    # feathered edge on the left; a small one is a window. Drawn in the game's order: ornaments on the background
    # layer, then the bag's body (and feather), its items, then the other ornaments. Pieces are drawn at rest.
    W, H = 720, 900
    box = (220, 110, 560, 760) if small else (220, 0, W, H)
    left, top, right, bottom = box
    corners = {"TOPINNER": (left, top), "TOPOUTER": (right, top), "BOTTOMINNER": (left, bottom),
               "BOTTOMOUTER": (right, bottom)}
    back, front = [], []
    for piece, o in ornaments:
        if o.get("Sizes") is not None and (o["Sizes"] == "Small") != small:
            continue
        art = back if o.get("Layer") == "BACKGROUND" else front
        src = pieces[piece]
        style = dict(tint=o.get("Color"), add=o.get("BlendMode") == "ADD", alpha=o.get("Alpha", 1.0))
        x, y = o.get("X", 0) * unit, o.get("Y", 0) * unit
        if o["Point"] == "INNER":
            y0, y1 = top + o.get("Start", 0) * unit, bottom - o.get("End", 0) * unit
            w = o["Width"] * unit
            if "Tile" in o:
                th = o["Tile"] * unit
                yy = y0
                while yy < y1 - 0.5:
                    part = min(th, y1 - yy)
                    piece_src = src if part >= th - 0.5 else crop_rows(src, part / th)
                    art.append((piece_src, left + x, yy, w, part, style))
                    yy += th
            else:
                art.append((src, left + x, y0, w, y1 - y0, style))
            continue
        cx, cy = corners[o["Point"]]
        w, h = o["Width"] * unit, o["Height"] * unit
        dx = x if o["Point"].endswith("INNER") else -x
        px, py = cx + dx, cy + y
        anchor = o.get("Anchor", o["Point"])
        ox = 0 if anchor.endswith("INNER") else -w
        oy = 0 if anchor.startswith("TOP") else -h
        art.append((src, px + ox, py + oy, w, h, style))
    preview_scene(back, front, body, accent, path, box, feather=not small, wisps=wisps)


def preview_scene(back, front, body, accent, path, box, feather=True, wisps=()):
    W, H = 720, 900
    left, top, right, bottom = box
    cv = Canvas(W, H)
    cv.over((0.10, 0.11, 0.12), np.ones((H, W)))
    scene = fbm(cv.X, cv.Y, 120, 3, 4)
    cv.over((0.18, 0.2, 0.22), (scene - 0.3) * 0.6)
    # Light patches on the ground, so what is drawn under the bag's feather shows how it darkens.
    cv.over((0.45, 0.32, 0.20), np.clip((fbm(cv.X, cv.Y, 200, 9, 3) - 0.45) * 2.5, 0, 0.6))

    def draw(art):
        for src, x, y, w, h, style in art:
            place(cv, src, int(round(x)), int(round(y)), max(1, int(round(w))), max(1, int(round(h))), **style)

    draw(back)
    inside = (cv.X >= left) & (cv.X < right) & (cv.Y >= top) & (cv.Y < bottom)
    if feather:
        f = np.clip(1 - (left - cv.X) / 96, 0, 1) * (cv.X < left) * (cv.Y >= top) * (cv.Y < bottom)
        cv.over(body[:3], f * body[3])
    cv.over(body[:3], inside * body[3])
    if not feather:
        edge = inside & ((cv.X < left + 1) | (cv.X >= right - 1) | (cv.Y < top + 1) | (cv.Y >= bottom - 1))
        cv.over((0.70, 0.82, 0.90), edge * 0.35)
    rng = np.random.RandomState(4)
    quality = [(0.62, 0.62, 0.62), (0.12, 1.0, 0.0), (0.0, 0.44, 0.87), (0.64, 0.21, 0.93)]
    for row in range(14):
        for col in range(8):
            x0, y0 = left + 30 + col * 54, top + 130 + row * 52
            if x0 + 44 > right - 10 or y0 + 44 > bottom - 40:
                continue
            d = np.maximum(np.abs(cv.X - (x0 + 22)) - 22, np.abs(cv.Y - (y0 + 22)) - 22)
            q = quality[rng.randint(4)]
            cv.over((0.16, 0.15, 0.17), coverage(d))
            cv.over(q, coverage(np.abs(d + 1) - 1) * 0.8)
    cv.over(accent, coverage(np.maximum(np.abs(cv.X - (left + 90)) - 50, np.abs(cv.Y - (top + 40)) - 7)) * 0.9)
    draw(front)
    # Wisps (the theme's sparkles): soft cyan-blue lights with a bright heart.
    for wx, wy, wr in wisps:
        rr = np.hypot(cv.X - wx, cv.Y - wy)
        cv.over((0.45, 0.78, 1.0), np.exp(-(rr / (wr * 1.6)) ** 2) * 0.55)
        cv.over((0.85, 0.95, 1.0), np.exp(-(rr / (wr * 0.45)) ** 2) * 0.9)
    cv.save(path)


PREVIEWS = {"NightElf": preview_nightelf}

# The sides of each piece its art may reach (anything else touching its edge would be cut off where it is drawn): a
# strip's ends (it repeats), a corner piece's side the strip's roots go on from, the bough's base.
OPEN = {
    "NightElf": {"roots": ("top", "bottom"), "under": ("top", "bottom"), "bough": ("right",), "corner_top": ("bottom",)},
}


def check_edges(theme, name, cv):
    # Fails when a piece's art reaches an edge it should not.
    a = cv.a
    sides = {"left": a[:, :2], "right": a[:, -2:], "top": a[:2, :], "bottom": a[-2:, :]}
    open_sides = OPEN.get(theme, {}).get(name, ())
    # A soft shadow's last few percent cut at an edge cannot be seen; anything solid there (a leaf, a root) can.
    bad = [side for side, edge in sides.items() if side not in open_sides and edge.max() > 0.04]
    if bad:
        raise SystemExit("%s/%s: its art reaches its %s edge, where it would be cut off" % (theme, name, ", ".join(bad)))


if __name__ == "__main__":
    args = sys.argv[1:]
    previews = None
    if "--preview" in args:
        previews = args[args.index("--preview") + 1]
        args = args[:args.index("--preview")] + args[args.index("--preview") + 2:]
    only = args or list(THEMES)
    for theme in only:
        pieces = THEMES[theme]()
        for name, cv in pieces.items():
            check_edges(theme, name, cv)
            cv.save(os.path.join(OUT, theme, name + ".png"))
        if previews:
            os.makedirs(previews, exist_ok=True)
            PREVIEWS[theme](pieces, os.path.join(previews, theme + ".png"))
