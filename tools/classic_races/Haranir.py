"""Haranir classic border: the crest's vocabulary, in a slim band.

A recessed channel of deep cobalt stone with darker veining and faint glowing blue veins, after
the crest's shield field. Two olive-green living vines twist loosely along the channel, over and
under each other. Fine dark root beads edge the channel inside and out. Along each edge, at a
calm period, sits a grey rune stone: a rounded square with a glowing pale-blue root rune cut into it.
Each corner is a larger grey rune stone set as a diamond and gripped by a ring of twisted vine.
Behind it, three small flame-orange leaves fan out toward the outer corner, the crest's fiery crown.
Orange appears only there.
Light from the top left; materials are shaded from height maps, and the runes are emissive with a soft halo.
"""
import numpy as np
from PIL import Image

THEME = dict(
    Name="RacesHaranir", Background="SOLID", BackgroundInset=8,
    Color=(0.02, 0.03, 0.09, 0.82), Slice=40, Outset=22, TitleY=40, Close={"X": 22, "Y": 22},
    Search=("TOPRIGHT", -22, -2), Menu={"X": -27, "Y": 27},
    TabEdge=(0.4, 0.46, 0.22, 1), TabAccent=(0.4, 0.66, 1.0, 1),
)
CREST = None  # textures/HaranirCrest.png (the default)

N = 256          # texture size
S = 40           # slice
P = 88           # edge pattern period (176 = 2 x 88)
K = 4            # supersampling
CC = 18.0        # corner stone centre, from the outer edges
TAU = 2 * np.pi

LIGHT = np.array([-0.5, -0.62, 0.6])
LIGHT = LIGHT / np.linalg.norm(LIGHT)
HALF = LIGHT + np.array([0, 0, 1.0])
HALF = HALF / np.linalg.norm(HALF)

ROOT_D = np.array([20, 14, 10], np.float32)
ROOT = np.array([70, 50, 34], np.float32)
ROOT_L = np.array([132, 104, 74], np.float32)
VINE_D = np.array([20, 28, 12], np.float32)
VINE = np.array([60, 78, 34], np.float32)
VINE_L = np.array([126, 138, 72], np.float32)
COB_D = np.array([6, 10, 48], np.float32)
COB = np.array([22, 44, 150], np.float32)
COB_GLOW = np.array([70, 130, 255], np.float32)
STONE_D = np.array([34, 36, 44], np.float32)
STONE = np.array([96, 98, 108], np.float32)
STONE_L = np.array([170, 172, 180], np.float32)
RUNE = np.array([90, 170, 255], np.float32)
RUNE_CORE = np.array([214, 238, 255], np.float32)
FLAME_D = np.array([110, 34, 16], np.float32)
FLAME = np.array([226, 98, 26], np.float32)
FLAME_L = np.array([255, 196, 84], np.float32)

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


def shade(h, dark, mid, light, spec=0.14, sp=24, tone=None):
    n = normals(h)
    ndl = np.clip((n * LIGHT).sum(-1), 0, 1)
    ndh = np.clip((n * HALF).sum(-1), 0, 1)
    lum = np.clip(0.1 + 0.95 * ndl ** 1.3, 0, 1.2)
    if tone is not None:
        lum = lum * tone
    lo = np.clip(lum * 2, 0, 1)[..., None]
    hi = np.clip(lum * 2 - 1, 0, 1)[..., None]
    alb = dark + (mid - dark) * lo + (light - mid) * hi
    return np.clip(alb + 255 * (spec * ndh ** sp)[..., None], 0, 255)


class Canvas:
    def __init__(self):
        self.rgb = np.zeros((N * K, N * K, 3), np.float32)
        self.a = np.zeros((N * K, N * K), np.float32)

    def over(self, rgb, a):
        da = self.a
        oa = a + da * (1 - a)
        self.rgb = (rgb * a[..., None] + self.rgb * (da * (1 - a))[..., None]) / np.maximum(oa, 1e-6)[..., None]
        self.a = oa

    def add(self, rgb, a):
        """Additive light on existing pixels only (a halo that never adds coverage)."""
        self.rgb = np.clip(self.rgb + rgb * (a * self.a)[..., None], 0, 255)

    def shadow(self, a, dx=1.2, dy=1.6, sig=1.4, op=0.6, clip=None):
        sx, sy = int(dx * K), int(dy * K)
        sh = np.zeros_like(a)
        sh[sy:, sx:] = a[:a.shape[0] - sy, :a.shape[1] - sx]
        sh = np.clip(blur(sh, sig * K), 0, 1) * op
        if clip is not None:
            sh = sh * clip
        self.over(np.zeros(a.shape + (3,), np.float32), sh)

    def image(self):
        pm = np.concatenate([self.rgb * self.a[..., None], self.a[..., None]], -1)
        pm = pm.reshape(N, K, N, K, 4).mean((1, 3))
        a = pm[..., 3:4]
        rgb = np.where(a > 0, pm[..., :3] / np.maximum(a, 1e-6), 0)
        return Image.fromarray(np.clip(np.concatenate([rgb, a * 255], -1) + 0.5, 0, 255).astype(np.uint8), "RGBA")


def cov(d):
    return (d < 0).astype(np.float32)


def dome(d, r, hmax):
    t = np.clip(-d / r, 0, 1)
    return hmax * np.sqrt(1 - (1 - t) ** 2)


def seg(px, py, ax, ay, bx, by):
    """Distance to segment a-b."""
    vx, vy = bx - ax, by - ay
    t = np.clip(((px - ax) * vx + (py - ay) * vy) / (vx * vx + vy * vy), 0, 1)
    return np.hypot(px - ax - t * vx, py - ay - t * vy)


def rune_d(lx, ly, s):
    """A root rune (an upright stem that forks up and roots down), size s, as a distance field."""
    d = seg(lx, ly, 0, -0.75 * s, 0, 0.8 * s)
    d = np.minimum(d, seg(lx, ly, 0, 0.0, -0.55 * s, -0.7 * s))
    d = np.minimum(d, seg(lx, ly, 0, 0.0, 0.55 * s, -0.7 * s))
    d = np.minimum(d, seg(lx, ly, 0, 0.45 * s, -0.42 * s, 0.85 * s))
    d = np.minimum(d, seg(lx, ly, 0, 0.45 * s, 0.42 * s, 0.85 * s))
    return d


def rbox(lx, ly, hx, hy, r):
    qx, qy = np.abs(lx) - hx + r, np.abs(ly) - hy + r
    return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - r


# ------------------------------------------------------------------ band (all four sides)
T = np.minimum(np.minimum(X, Y), np.minimum(N - X, N - Y))   # distance from the nearest outer side
U = np.where(np.minimum(X, N - X) <= np.minimum(Y, N - Y), Y, X)  # position along the nearest side

LIP = (7.0, 9.6)
CHAN = (9.6, 22.4)
BEAD = (22.4, 25.0)
TC = (CHAN[0] + CHAN[1]) / 2


def veins(u, t):
    """Cobalt stone veining, periodic in u over P."""
    f = TAU / P
    v = (np.sin(u * f * 2 + 1.7 * np.sin(t * 0.45 + u * f) + t * 0.3)
         + 0.6 * np.sin(u * f * 5 - t * 0.9 + 2.0))
    return v


def band(cv):
    m = cov(np.maximum(LIP[0] - T, T - BEAD[1]))
    cv.shadow(m, 1.0, 1.4, 1.2, 0.55)
    # cobalt channel, recessed, veined
    d = np.abs(T - TC) - (CHAN[1] - CHAN[0]) / 2
    v = veins(U, T)
    h = 0.6 * np.cos(np.clip((T - TC) / 6.4, -1, 1) * np.pi / 2) + 0.12 * v
    rgb = shade(h, COB_D, COB, COB * 1.5, spec=0.08)
    dark = sstep(0.55, 1.0, np.abs(np.sin(v * 1.3)))  # dark veins
    rgb = rgb * (1 - 0.45 * dark[..., None])
    glow = np.exp(-((v - 1.15) / 0.12) ** 2)        # thin glowing veins
    rgb = rgb + (COB_GLOW - rgb) * (0.55 * glow)[..., None]
    rgb = rgb * (1 - 0.35 * sstep(3.5, 6.4, np.abs(T - TC)))[..., None]   # depth toward the beads
    cv.over(rgb, cov(d))
    for (a, b), hmax in ((LIP, 1.6), (BEAD, 1.6)):
        c, r = (a + b) / 2, (b - a) / 2
        dd = np.abs(T - c) - r
        hh = dome(dd, r, hmax) - 0.2 * np.sin(U * TAU / P * 6 + T * 2)
        cv.over(shade(hh, ROOT_D, ROOT, ROOT_L), cov(dd))


def vines(cv):
    """Two strands twisting loosely along the channel; the front strand alternates at each crossing."""
    lam = P
    A, R = 3.4, 2.0
    ph = (U - S) * TAU / lam
    inband = ((T > LIP[0]) & (T < BEAD[1])).astype(np.float32)
    best_h = np.full(T.shape, -1e9, np.float32)
    best_m = np.zeros(T.shape, np.float32)
    shadow_m = np.zeros(T.shape, np.float32)
    for k in range(2):
        p = ph + k * np.pi
        c = TC + A * np.sin(p)
        slope = A * TAU / lam * np.cos(p)
        d = np.abs(T - c) / np.sqrt(1 + slope ** 2) - R
        z = 1.8 * np.cos(p)              # the strand nearer the viewer is higher
        h = 4.0 + z + dome(d, R, 2.0)
        # a slow spiral grain on each strand
        h = h - 0.25 * np.sin((U - S) * TAU / (lam / 4) + (T - c) * 1.6) * sstep(0, 0.8, -d)
        m = cov(d)
        take = (m > 0) & (h > best_h)
        best_h = np.where(take, h, best_h)
        best_m = np.maximum(best_m, m)
        shadow_m = np.maximum(shadow_m, m)
    best_m *= inband
    cv.shadow(shadow_m * inband, 0.8, 1.1, 0.9, 0.6, clip=inband)
    # a dark crease where the rear strand passes under
    rgb = shade(best_h, VINE_D, VINE, VINE_L, spec=0.12, sp=18)
    cv.over(rgb, best_m)


# ------------------------------------------------------------------ rune stones
def side_coords():
    return [(X, Y), (Y, X), (X, N - Y), (Y, N - X)]


def rune_glow(cv, lx, ly, s, region, w=0.75):
    d = rune_d(lx, ly, s) - w
    m = cov(d) * region
    cv.add(RUNE * 0.6, np.clip(blur(m, 1.3 * K) * 1.6, 0, 1) * region * 0.6)
    core = sstep(0, w * 0.9, -d)
    cv.over(RUNE + (RUNE_CORE - RUNE) * core[..., None], m)


def stone(cv, lx, ly, hx, hy, region, rs):
    db = rbox(lx, ly, hx, hy, 2.6)
    m = cov(db) * region
    cv.shadow(m, 1.2, 1.6, 1.3, 0.65, clip=region)
    h = 4.6 + dome(db, 2.4, 2.2)
    # chipped, hand-cut face: a few low facets, fixed so every stone matches
    h = h + 0.25 * np.sin(lx * 0.9 + ly * 0.5) + 0.18 * np.sin(ly * 1.3 - lx * 0.4)
    # the rune is cut in
    dr = rune_d(lx, ly, rs)
    h = h - 0.9 * sstep(1.4, 0.4, dr)
    cv.over(shade(h, STONE_D, STONE, STONE_L, spec=0.1, sp=20), m)
    rune_glow(cv, lx, ly, rs, region)


def edge_stones(cv):
    centres = [S + P / 2 + k * P for k in range(int((N - 2 * S) / P))]
    for u, t in side_coords():
        inseg = ((u > S) & (u < N - S) & (t < S)).astype(np.float32)
        for u0 in centres:
            stone(cv, u - u0, t - TC, 7.4, 7.4, inseg, 4.0)


# ------------------------------------------------------------------ corners
def corner_coords():
    return [(X, Y), (N - X, Y), (X, N - Y), (N - X, N - Y)]


def leaf_d(a, b, L, W):
    """A pointed leaf from the origin along +a, length L, half-width W (a vesica)."""
    t = np.clip(a / L, 0, 1)
    half = W * np.sin(np.pi * t) ** 0.8
    return np.maximum(np.abs(b) - half, np.maximum(-a, a - L))


def corners(cv):
    q = np.sqrt(0.5)
    for lx0, ly0 in corner_coords():
        region = ((lx0 < S) & (ly0 < S)).astype(np.float32)
        lx, ly = lx0 - CC, ly0 - CC
        a = (lx + ly) * q            # inward along the diagonal
        b = (lx - ly) * q
        # flame leaves fanning out toward the outer corner, behind the stone
        fl = np.zeros(lx.shape, np.float32)
        fh = np.full(lx.shape, -1e9, np.float32)
        ft = np.zeros(lx.shape, np.float32)
        for ang, L in ((0.0, 16.0), (0.52, 11.5), (-0.52, 11.5)):
            ca, sa = np.cos(np.pi + ang), np.sin(np.pi + ang)
            la, lb = a * ca + b * sa, -a * sa + b * ca
            d = leaf_d(la - 5.0, lb, L, 4.4)
            m = cov(d)
            h = 3.0 + dome(d, 2.0, 1.4) - 0.5 * np.exp(-(lb / 0.45) ** 2) * (la > 5)
            take = (m > 0) & (h > fh)
            fh = np.where(take, h, fh)
            ft = np.where(take, np.clip((la - 5.0) / L, 0, 1), ft)
            fl = np.maximum(fl, m)
        fl *= region
        cv.shadow(fl, 1.0, 1.3, 1.1, 0.5, clip=region)
        rgb = shade(fh, FLAME_D, FLAME, FLAME_L, spec=0.1)
        tip = sstep(0.45, 1.0, ft)
        rgb = rgb + (FLAME_L - rgb) * (0.45 * tip)[..., None]
        cv.over(rgb, fl)
        # a ring of vine gripping the stone
        r = np.hypot(lx, ly)
        ang = np.arctan2(ly, lx)
        dr = np.abs(r - 10.4) - 1.8
        mr = cov(dr) * region
        cv.shadow(mr, 1.0, 1.4, 1.2, 0.6, clip=region)
        # two strands twisted into the ring: a spiral crease around it
        hr = 4.2 + dome(dr, 1.8, 2.0) - 0.7 * sstep(0.55, 0.95, np.sin(ang * 9 + (r - 10.4) * 1.4) ** 2)
        cv.over(shade(hr, VINE_D, VINE, VINE_L, spec=0.12, sp=18), mr)
        # the corner rune stone, set as a diamond
        stone(cv, a, b, 7.6, 7.6, region, 4.3)


# ------------------------------------------------------------------ assembly
def BORDER():
    cv = Canvas()
    band(cv)
    vines(cv)
    edge_stones(cv)
    corners(cv)
    img = cv.image()
    arr = np.array(img)
    arr[S:N - S, S:N - S] = 0
    return Image.fromarray(arr, "RGBA")
