"""Draenei classic border: the Exodar / Azuremyst look.

A slim band of smooth pearl-silver naaru metal: a fine outer lip, a rounded main rail and a
thin inner bead, with a narrow amethyst crystal inlay set in the channel between rail and bead.
Along each edge the rail carries swept silver vesica mounts holding a faceted violet crystal.
The corners are a curved silver crescent (the Exodar's swept hull) cradling a ring mount with a
faceted amethyst, and a tapered silver fin sweeping from the ring along each rail.
Light from the top left; materials shaded from height maps, crystals by planar facets.
"""
import numpy as np
from PIL import Image

THEME = dict(
    Name="RacesDraenei", Background="SOLID", BackgroundInset=8,
    Color=(0.05, 0.04, 0.12, 0.78), Slice=40, Outset=22, TitleY=40, Close={"X": 22, "Y": 22},
    Search=("TOPRIGHT", -22, -2), Menu={"X": -27, "Y": 27},
    TabEdge=(0.72, 0.72, 0.8, 1), TabAccent=(0.62, 0.42, 0.95, 1),
)

N = 256          # texture size
S = 40           # slice
P = 88           # edge pattern period (176 = 2 x 88)
K = 4            # supersampling
CC = 17.0        # corner medallion centre, from the outer edges

LIGHT = np.array([-0.5, -0.62, 0.6])
LIGHT = LIGHT / np.linalg.norm(LIGHT)
HALF = LIGHT + np.array([0, 0, 1.0])
HALF = HALF / np.linalg.norm(HALF)

PEARL = np.array([206, 205, 218], np.float32)
PEARL_LAV = np.array([196, 184, 232], np.float32)
PEARL_ICE = np.array([214, 224, 236], np.float32)
VIO_D = np.array([58, 22, 112], np.float32)
VIO = np.array([132, 70, 214], np.float32)
VIO_L = np.array([214, 180, 255], np.float32)

g = (np.arange(N * K) + 0.5) / K
X, Y = np.meshgrid(g, g)


# ------------------------------------------------------------------ helpers
def sstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def blur(a, sigma):
    r = int(sigma * 3) + 1
    x = np.arange(-r, r + 1)
    k = np.exp(-x * x / (2 * sigma * sigma))
    k /= k.sum()
    p = np.pad(a, r, mode="constant")
    out = np.zeros_like(p)
    for i in range(2 * r + 1):
        out[:, r:-r] += k[i] * p[:, i:i + a.shape[1]]
    out2 = np.zeros_like(out)
    for i in range(2 * r + 1):
        out2[r:-r, :] += k[i] * out[i:i + a.shape[0], :]
    return out2[r:-r, r:-r]


def normals(h):
    gy, gx = np.gradient(h * K)
    n = np.stack([-gx, -gy, np.ones_like(h)], -1)
    return n / np.linalg.norm(n, axis=-1, keepdims=True)


def pearl(h):
    """Smooth pale-silver naaru metal with a faint pearlescent shift."""
    n = normals(h)
    ndl = np.clip((n * LIGHT).sum(-1), 0, 1)
    ndh = np.clip((n * HALF).sum(-1), 0, 1)
    # pearl shift: faces toward the light go icy, faces away go lavender
    tilt = np.clip((n[..., 0] * LIGHT[0] + n[..., 1] * LIGHT[1]) * 2.2, -1, 1)
    alb = PEARL + (PEARL_ICE - PEARL) * np.clip(tilt, 0, 1)[..., None] \
        + (PEARL_LAV - PEARL) * np.clip(-tilt, 0, 1)[..., None]
    rgb = alb * (0.36 + 0.66 * ndl)[..., None] + 255 * (0.55 * ndh ** 40 + 0.12 * ndh ** 6)[..., None]
    return np.clip(rgb, 0, 255)


def crystal(h, glow):
    """Faceted amethyst: planar facets from a polygon height, inner glow toward the table."""
    n = normals(h)
    ndl = np.clip((n * LIGHT).sum(-1), 0, 1)
    ndh = np.clip((n * HALF).sum(-1), 0, 1)
    base = VIO_D * 0.7 + (VIO_L - VIO_D * 0.7) * (0.05 + 0.75 * ndl ** 1.6)[..., None]
    base = base + (VIO - base) * (0.35 * glow)[..., None]
    rgb = base + 255 * (0.7 * ndh ** 60)[..., None] + np.array([90, 60, 140]) * (0.25 * ndh ** 8)[..., None]
    return np.clip(rgb, 0, 255)


def poly_sdf(lx, ly, verts):
    """Convex polygon SDF via half-planes (negative inside). Returns d."""
    v = np.asarray(verts, np.float32)
    d = np.full(lx.shape, -1e9, np.float32)
    for i in range(len(v)):
        a, b = v[i], v[(i + 1) % len(v)]
        e = b - a
        nx, ny = e[1], -e[0]
        l = np.hypot(nx, ny)
        nx, ny = nx / l, ny / l
        # outward normal for counter-clockwise (y down) ordering handled by sign check below
        d = np.maximum(d, (lx - a[0]) * nx + (ly - a[1]) * ny)
    return d


def ccw(verts):
    v = np.asarray(verts, np.float32)
    area = 0.5 * np.sum(v[:, 0] * np.roll(v[:, 1], -1) - np.roll(v[:, 0], -1) * v[:, 1])
    return v[::-1] if area < 0 else v


class Canvas:
    def __init__(self):
        self.rgb = np.zeros((N * K, N * K, 3), np.float32)
        self.a = np.zeros((N * K, N * K), np.float32)

    def over(self, rgb, a):
        da = self.a
        oa = a + da * (1 - a)
        self.rgb = (rgb * a[..., None] + self.rgb * (da * (1 - a))[..., None]) / np.maximum(oa, 1e-6)[..., None]
        self.a = oa

    def shadow(self, a, dx=1.2, dy=1.6, sig=1.4, op=0.6):
        sx, sy = int(dx * K), int(dy * K)
        sh = np.zeros_like(a)
        sh[sy:, sx:] = a[:a.shape[0] - sy, :a.shape[1] - sx]
        sh = np.clip(blur(sh, sig * K), 0, 1) * op
        self.over(np.zeros(a.shape + (3,), np.float32), sh)

    def image(self):
        pm = np.concatenate([self.rgb * self.a[..., None], self.a[..., None]], -1)
        pm = pm.reshape(N, K, N, K, 4).mean((1, 3))
        a = pm[..., 3:4]
        rgb = np.where(a > 0, pm[..., :3] / np.maximum(a, 1e-6), 0)
        return Image.fromarray(np.clip(np.concatenate([rgb, a * 255], -1) + 0.5, 0, 255).astype(np.uint8), "RGBA")


def cov(d):
    """Signed distance (1x px) -> coverage at the supersampled grid (hard edge; box-averaged later)."""
    return (d < 0).astype(np.float32)


def dome(d, r, hmax):
    """Rounded profile from a signed distance: 0 at the rim, hmax at depth r."""
    t = np.clip(-d / r, 0, 1)
    return hmax * np.sqrt(1 - (1 - t) ** 2)


# ------------------------------------------------------------------ the rail (all four sides)
T = np.minimum(np.minimum(X, Y), np.minimum(N - X, N - Y))   # distance from the nearest outer side

LIP = (7.5, 10.5)
TUBE = (10.5, 20.5)
INLAY = (20.5, 22.5)
BEAD = (22.5, 25.5)


def rail(cv):
    out = cv
    band = cov(np.maximum(LIP[0] - T, T - BEAD[1]))
    out.shadow(band, 1.0, 1.4, 1.2, 0.55)
    # violet inlay channel (under everything, a recessed crystal line)
    m = cov(np.maximum(INLAY[0] - 0.3 - T, T - INLAY[1] - 0.3))
    hc = 0.6 * np.sin(np.clip((T - INLAY[0]) / (INLAY[1] - INLAY[0]), 0, 1) * np.pi)
    glow = 0.0 + 0.1 * np.sin(np.clip((T - INLAY[0]) / (INLAY[1] - INLAY[0]), 0, 1) * np.pi)
    out.over(crystal(hc, glow), m)
    for (a, b), hmax in ((LIP, 1.6), (TUBE, 4.2), (BEAD, 1.5)):
        c, r = (a + b) / 2, (b - a) / 2
        d = np.abs(T - c) - r
        m = cov(d)
        h = dome(d, r, hmax)
        # a fine engraved line along the crown of the main rail
        if hmax > 4:
            h = h - 0.2 * np.exp(-((T - (c - 1.2)) / 0.45) ** 2)
        out.over(pearl(h), m)


# ------------------------------------------------------------------ edge mounts
def side_coords():
    """(u along, t across) for top, left, bottom, right."""
    return [(X, Y), (Y, X), (X, N - Y), (Y, N - X)]


def edge_mounts(cv):
    centres = [S + P / 2 + k * P for k in range(int((N - 2 * S) / P))]
    tc = (TUBE[0] + TUBE[1]) / 2
    for u, t in side_coords():
        inseg = (u > S) & (u < N - S) & (t < S)
        for u0 in centres:
            lx, ly = u - u0, t - tc
            # vesica (lens) mount: intersection of two circles
            R, w = 34.0, 6.6      # circle radius, half-height of the lens
            off = R - w
            d1 = np.hypot(lx, ly - off) - R
            d2 = np.hypot(lx, ly + off) - R
            dv = np.maximum(d1, d2)
            m = cov(dv) * inseg
            cv.shadow(m, 1.0, 1.4, 1.3, 0.6)
            h = 4.2 + dome(dv, 3.0, 2.2)
            # swept grooves following the lens curve
            dgr = np.maximum(np.hypot(lx, ly - off) - R, np.hypot(lx, ly + off) - R) + 2.6
            h = h - 0.45 * np.exp(-(dgr / 0.5) ** 2)
            cv.over(pearl(h), m)
            # faceted crystal: elongated hexagon
            hx, hy = 10.5, 4.2
            verts = ccw([(-hx, 0), (-hx + 4.6, -hy), (hx - 4.6, -hy), (hx, 0), (hx - 4.6, hy), (-hx + 4.6, hy)])
            dg = poly_sdf(lx, ly, verts)
            mg = cov(dg) * inseg
            hg = 6.0 + np.minimum(-dg * 1.15, 2.6)
            glow = sstep(-1.0, -3.6, dg)
            cv.shadow(mg, 0.5, 0.7, 0.6, 0.5)
            cv.over(crystal(hg, glow), mg)


# ------------------------------------------------------------------ corners
def corner_coords():
    """Local (x, y) per corner, positive pointing inward from the outer corner."""
    return [(X, Y), (N - X, Y), (X, N - Y), (N - X, N - Y)]


def corners(cv):
    q = np.sqrt(0.5)
    for lx0, ly0 in corner_coords():
        region = (lx0 < S) & (ly0 < S)
        lx, ly = lx0 - CC, ly0 - CC
        # diagonal frame: a runs from the outer corner inward, b across
        a = (lx + ly) * q
        b = (lx - ly) * q
        r = np.hypot(lx, ly)
        # cradle: a swept crescent cupping the inner side, its two arms curling out past the crystal
        dA = np.hypot(a - 3.0, b) - 16.2
        dB = np.hypot(a + 5.2, b) - 15.0
        dcr = np.maximum(dA, -dB)
        mc = cov(dcr) * region
        # backing dish: a pearl bezel with a dark recessed field the crystal sits in
        dd = r - 12.6
        md = cov(dd) * region
        cv.shadow(np.maximum(md, mc), 1.3, 1.7, 1.6, 0.65)
        h_d = 4.4 + dome(dd, 2.6, 1.8) - 2.0 * sstep(-2.4, -3.4, dd)
        rgb_d = pearl(h_d)
        field = sstep(-2.6, -3.6, dd)
        deep = np.array([150, 140, 178], np.float32) - np.array([70, 70, 80], np.float32) * sstep(-3.0, -11.0, dd)[..., None]
        rgb_d = rgb_d * (1 - field[..., None]) + deep * field[..., None]
        cv.over(rgb_d, md)
        h_c = 6.2 + dome(dcr, 2.6, 2.2)
        cv.over(pearl(h_c), mc)
        # faceted amethyst: an elongated hexagon along the diagonal, pointing at the outer corner
        L, W, F = 11.5, 6.4, 6.0
        verts = ccw([(-L, 0), (-L + F, -W), (L - F, -W), (L, 0), (L - F, W), (-L + F, W)])
        dg = poly_sdf(a + 1.0, b, verts)
        mg = cov(dg) * region
        hg = 8.0 + np.minimum(-dg * 1.0, 3.2)
        glow = sstep(-1.5, -4.5, dg)
        cv.shadow(mg, 0.7, 0.9, 0.8, 0.6)
        cv.over(crystal(hg, glow), mg)


# ------------------------------------------------------------------ assembly
def BORDER():
    cv = Canvas()
    rail(cv)
    edge_mounts(cv)
    corners(cv)
    img = cv.image()
    arr = np.array(img)
    arr[S:N - S, S:N - S] = 0
    return Image.fromarray(arr, "RGBA")
