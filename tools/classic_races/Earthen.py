"""Earthen classic border: titan-forged living stone of Dornogal / Khaz Algar, set with gems.

A slim band of smooth, dressed grey-blue titan stone with a flat face and crisp chamfered bevels,
between a thin gold outer rail and a thin gold inner rail. A fine recessed channel along the stone
carries a faint pale-blue titan rune line. Along each edge the stone holds angular gold bezels set
with faceted sapphires (the Earthen's gem encrustations). Each corner is a raised chamfered block of
the same stone, framed in gold, with a large octagon-cut gem in its natural colour: sapphire, ruby,
emerald and amber, the Khaz Algar gems.
Light from the top left; stone and gold shaded from height maps, gems by planar facets.
"""
import numpy as np
from PIL import Image

THEME = dict(
    Name="RacesEarthen", Background="SOLID", BackgroundInset=8,
    Color=(0.06, 0.07, 0.09, 0.8), Slice=44, Outset=22, TitleY=40, Close={"X": 22, "Y": 22},
    Search=("TOPRIGHT", -22, -2), Menu={"X": -26, "Y": 26},
    TabEdge=(0.5, 0.55, 0.62, 1), TabAccent=(0.85, 0.66, 0.28, 1),
)
CREST = None  # textures/EarthenCrest.png (the default)

N = 256
S = 44
SEG = N - 2 * S  # 168
P = SEG // 2     # 84: edge pattern period
K = 3
CC = 21.0        # corner block centre, from the outer edges

LIGHT = np.array([-0.5, -0.62, 0.6])
LIGHT = LIGHT / np.linalg.norm(LIGHT)
HALF = LIGHT + np.array([0, 0, 1.0])
HALF = HALF / np.linalg.norm(HALF)

STONE = np.array([128, 138, 152], np.float32)
STONE_D = np.array([96, 106, 122], np.float32)
GOLD = np.array([206, 160, 72], np.float32)
GOLD_L = np.array([255, 228, 150], np.float32)
RUNE = np.array([150, 215, 255], np.float32)

GEMS = {
    "sapphire": (np.array([14, 30, 96]), np.array([50, 110, 230]), np.array([170, 210, 255])),
    "ruby": (np.array([80, 6, 18]), np.array([200, 30, 50]), np.array([255, 170, 175])),
    "emerald": (np.array([6, 60, 30]), np.array([30, 170, 90]), np.array([170, 255, 200])),
    "amber": (np.array([96, 44, 4]), np.array([235, 140, 30]), np.array([255, 225, 150])),
}

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


def periodic_noise(seed, sig_u, sig_t, period=P):
    """Smooth noise over (u, t) that repeats every `period` along u. Returns a lookup f(u, t)."""
    rng = np.random.default_rng(seed)
    w, h = period * K, N * K // 2
    a = rng.standard_normal((h, w))
    fu = np.fft.fftfreq(w)[None, :]
    ft = np.fft.fftfreq(h)[:, None]
    filt = np.exp(-2 * (np.pi ** 2) * ((fu * sig_u * K) ** 2 + (ft * sig_t * K) ** 2))
    a = np.real(np.fft.ifft2(np.fft.fft2(a) * filt))
    a = (a - a.mean()) / (a.std() + 1e-9)

    def f(u, t):
        iu = (np.floor(u * K).astype(int)) % w
        it = np.clip(np.floor(t * K).astype(int), 0, h - 1)
        return a[it, iu]
    return f


def normals(h):
    gy, gx = np.gradient(h * K)
    n = np.stack([-gx, -gy, np.ones_like(h)], -1)
    return n / np.linalg.norm(n, axis=-1, keepdims=True)


def shade(h, alb, amb=0.34, dif=0.7, spec=0.18, sp=24):
    n = normals(h)
    ndl = np.clip((n * LIGHT).sum(-1), 0, 1)
    ndh = np.clip((n * HALF).sum(-1), 0, 1)
    return np.clip(alb * (amb + dif * ndl)[..., None] + 255 * (spec * ndh ** sp)[..., None], 0, 255)


def gold(h):
    n = normals(h)
    ndl = np.clip((n * LIGHT).sum(-1), 0, 1)
    ndh = np.clip((n * HALF).sum(-1), 0, 1)
    alb = GOLD * 0.55 + (GOLD_L - GOLD * 0.55) * (ndl ** 2.2)[..., None]
    rgb = alb * (0.35 + 0.6 * ndl)[..., None] + 255 * (0.45 * ndh ** 30)[..., None]
    return np.clip(rgb, 0, 255)


def gem(h, glow, kind):
    d, m, l = (np.asarray(c, np.float32) for c in GEMS[kind])
    n = normals(h)
    ndl = np.clip((n * LIGHT).sum(-1), 0, 1)
    ndh = np.clip((n * HALF).sum(-1), 0, 1)
    base = d + (l - d) * (0.05 + 0.7 * ndl ** 1.8)[..., None]
    base = base + (m - base) * (0.45 * glow)[..., None]
    rgb = base + 255 * (0.75 * ndh ** 70)[..., None] + m * (0.2 * ndh ** 8)[..., None]
    return np.clip(rgb, 0, 255)


def octagon(lx, ly, r, c):
    """Square of half-size r with corners chamfered by c (L-inf / L1 octagon). Negative inside."""
    return np.maximum(np.maximum(np.abs(lx), np.abs(ly)) - r, (np.abs(lx) + np.abs(ly)) - (2 * r - c))


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
    return (d < 0).astype(np.float32)


def side_coords():
    """(u along, t across) for top, left, bottom, right."""
    return [(X, Y), (Y, X), (X, N - Y), (Y, N - X)]


def side_mask(i):
    """Which side owns each pixel (split along the corner diagonals)."""
    t = [Y, X, N - Y, N - X]
    m = np.argmin(np.stack(t), 0)
    return m == i


# ------------------------------------------------------------------ the band
T = np.minimum(np.minimum(X, Y), np.minimum(N - X, N - Y))
OUT = (6.0, 8.5)      # outer gold rail
STN = (8.5, 27.5)     # stone face
INN = (27.5, 30.0)    # inner gold rail
CH = 18.0             # rune channel centre


def band(cv):
    full = cov(np.maximum(OUT[0] - T, T - INN[1]))
    cv.shadow(full, 1.2, 1.6, 1.4, 0.6)
    # stone: flat face with 45-degree chamfers, slight mottle and grain (periodic along each edge)
    mot = periodic_noise(3, 9.0, 4.0)
    grain = periodic_noise(5, 0.8, 0.8)
    a, b = STN
    chamf = 2.6
    h = 3.2 + np.minimum(np.minimum(T - a, b - T), chamf) * 0.9
    # recessed rune channel
    h = h - 1.1 * sstep(1.4, 0.6, np.abs(T - CH))
    alb = np.zeros(X.shape + (3,), np.float32)
    var = np.zeros(X.shape, np.float32)
    for i, (u, t) in enumerate(side_coords()):
        m = side_mask(i)
        var = np.where(m, 0.6 * mot(u + 31 * i, t) + 0.25 * grain(u + 17 * i, t), var)
    h = h + 0.12 * var
    alb = STONE + (STONE_D - STONE) * np.clip(0.5 - 0.35 * var, 0, 1)[..., None]
    rgb = shade(h, alb)
    # rune line: faint pale-blue glow at the channel floor
    glow = np.exp(-((T - CH) / 0.7) ** 2)
    rgb = rgb + (RUNE - rgb) * (0.75 * glow)[..., None]
    cv.over(rgb, cov(np.maximum(a - T, T - b)))
    # gold rails, rounded
    for (lo, hi), hm in ((OUT, 2.0), (INN, 2.0)):
        c, r = (lo + hi) / 2, (hi - lo) / 2
        d = np.abs(T - c) - r
        hh = 4.0 + hm * np.sqrt(np.clip(1 - ((T - c) / r) ** 2, 0, 1))
        cv.over(gold(hh), cov(d))


# ------------------------------------------------------------------ edge mounts
def edge_mounts(cv):
    """One stepped gold plate with a diamond-cut gem per segment; gold-lined block joints between."""
    tc = (STN[0] + STN[1]) / 2
    for u, t in side_coords():
        inseg = (u > S) & (u < N - S) & (t < S)
        # block joints: a sunken seam lined with gold, at the quarter points (period P, offset from the plates)
        for uj in (S + P / 2, S + P / 2 + P):
            dj = np.abs(u - uj) - 0.9
            mj = cov(np.maximum(dj, np.maximum(STN[0] - t, t - STN[1]))) * inseg
            cv.over(np.zeros(X.shape + (3,), np.float32) + 30, mj * 0.55)
            dl = np.abs(u - uj - 0.3) - 0.45
            ml = cov(np.maximum(dl, np.maximum(STN[0] - t, t - STN[1]))) * inseg
            cv.over(gold(4.0 + 0.0 * u), ml * 0.9)
        for u0 in (S + SEG / 2,):
            lx, ly = u - u0, t - tc
            # stepped gold plate: two tiers, wide and low, then narrow and raised (titan ziggurat)
            d1 = np.maximum(np.abs(lx) - 15.0, np.abs(ly) - 7.2)
            d1 = np.maximum(d1, np.abs(lx) + np.abs(ly) - 19.5)
            d2 = np.maximum(np.abs(lx) - 9.5, np.abs(ly) - 10.2)
            d2 = np.maximum(d2, np.abs(lx) + np.abs(ly) - 16.0)
            dp = np.minimum(d1, d2)
            mp = cov(dp) * inseg
            cv.shadow(mp, 1.0, 1.3, 1.2, 0.6)
            hp = 5.0 + np.minimum(-d1, 1.6) * 1.0
            hp = np.where(d2 < 0, 6.6 + np.minimum(-d2, 1.6) * 1.0, hp)
            cv.over(gold(hp), mp)
            # diamond-cut gem: a rhombus with a small flat table
            dg = np.abs(lx) / 1.15 + np.abs(ly) - 7.4
            mg = cov(dg) * inseg
            hg = 9.0 + np.clip(-dg, 0, 3.2) * 1.0
            cv.shadow(mg, 0.5, 0.6, 0.6, 0.55)
            cv.over(gem(hg, sstep(-1.0, -3.6, dg), "sapphire"), mg)


# ------------------------------------------------------------------ corners
def corner_coords():
    return [(X, Y), (N - X, Y), (X, N - Y), (N - X, N - Y)]


CORNER_GEMS = ["sapphire", "ruby", "emerald", "amber"]   # TL, TR, BL, BR


def corners(cv):
    mot = periodic_noise(11, 6.0, 6.0, period=64)
    for (lx0, ly0), kind in zip(corner_coords(), CORNER_GEMS):
        region = (lx0 < S) & (ly0 < S)
        lx, ly = lx0 - CC, ly0 - CC
        var = mot(lx0 + 7, ly0)
        alb = STONE + (STONE_D - STONE) * np.clip(0.5 - 0.35 * var, 0, 1)[..., None]
        # gold frame
        dout = octagon(lx, ly, 19.5, 8.0)
        mo = cov(dout) * region
        cv.shadow(mo, 1.5, 1.9, 1.7, 0.7)
        cv.over(gold(6.0 + np.minimum(-dout, 1.8) * 1.0), mo)
        # lower stone tier with a rune groove, then a raised chamfered upper tier
        d1 = octagon(lx, ly, 17.6, 7.2)
        d2 = octagon(lx, ly, 13.4, 5.4)
        h = 7.6 + np.minimum(-d1, 1.6) * 0.9
        h = np.where(d2 < 0, 9.8 + np.minimum(-d2, 2.4) * 1.0, h)
        dgr = np.abs(d2 - 1.9)
        h = h - 0.8 * sstep(0.9, 0.3, dgr) + 0.1 * var
        rgb = shade(h, alb)
        rgb = rgb + (RUNE - rgb) * (0.7 * np.exp(-(dgr / 0.55) ** 2) * (d2 > 0))[..., None]
        cv.over(rgb, cov(d1) * region)
        # gold bezel and octagon step-cut gem
        dbz = octagon(lx, ly, 9.6, 4.0)
        mbz = cov(dbz) * region
        cv.shadow(mbz, 0.8, 1.0, 0.9, 0.55)
        cv.over(gold(13.0 + np.minimum(-dbz, 1.6) * 1.1), mbz)
        dg = octagon(lx, ly, 7.8, 3.3)
        mg = cov(dg) * region
        table = octagon(lx, ly, 3.6, 1.5)
        hg = 15.0 + np.clip(4.2 - np.clip(table, 0, None) * 1.0, 0, 4.2)
        cv.over(gem(hg, sstep(-1.0, -4.5, dg), kind), mg)


# ------------------------------------------------------------------ assembly
def BORDER():
    cv = Canvas()
    band(cv)
    edge_mounts(cv)
    corners(cv)
    arr = np.array(cv.image())
    arr[S:N - S, S:N - S] = 0
    return Image.fromarray(arr, "RGBA")
