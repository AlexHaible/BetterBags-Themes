"""High Order Skyborne classic border: Highborne marble and gold of Zephras Isle, set with arcane violet.

A slim band of polished ivory marble with soft grey veining, between a rounded gold outer rail
and a rounded gold inner rail. Along each edge sits a winged arcane crystal: a slender upright
violet crystal (a pylon's crystal, pointed at both ends) in a gold setting, with a pair of
stylised gold wings, three curved feathers each, sweeping out along the marble. Between the
wings the marble blocks meet at a thin gold-lined joint. Each corner is a round gold medallion
of cerulean enamel (the Skyborne banner's field) bearing the race's wind sigil in raised gold, a
curl sweeping down into an S-shaped gust, traced from the official banner. A small gold wing
sweeps from it along each edge, and a slender gold pylon finial tipped with a violet crystal
points out at the corner. Curves and feathers, no angular plate; light from the top left.
"""
import numpy as np
from PIL import Image

THEME = dict(
    Name="RacesHighOrderSkyborne", Background="SOLID", BackgroundInset=8,
    Color=(0.065, 0.06, 0.095, 0.8), Slice=44, Outset=20, TitleY=40, Close={"X": 20, "Y": 20},
    Search=("TOPRIGHT", -22, -2), Menu={"X": -22, "Y": 22},
    TabEdge=(0.8, 0.76, 0.68, 1), TabAccent=(0.72, 0.5, 1.0, 1),
)
CREST = None  # textures/HighOrderSkyborneCrest.png (the default; drawn by CREST_ART)

N = 256
S = 44
SEG = N - 2 * S  # 168
P = SEG // 2     # 84: edge pattern period
K = 3
CC = 18.0        # corner medallion centre, from the outer edges

LIGHT = np.array([-0.5, -0.62, 0.6])
LIGHT = LIGHT / np.linalg.norm(LIGHT)
HALF = LIGHT + np.array([0, 0, 1.0])
HALF = HALF / np.linalg.norm(HALF)

MARBLE = np.array([236, 230, 216], np.float32)
MARBLE_D = np.array([196, 190, 182], np.float32)
VEIN = np.array([150, 146, 150], np.float32)
GOLD = np.array([206, 160, 72], np.float32)
GOLD_L = np.array([255, 230, 150], np.float32)
CERULEAN = np.array([44, 112, 170], np.float32)   # the Skyborne banner's field
CERULEAN_L = np.array([96, 170, 220], np.float32)
VIOLET = (np.array([34, 8, 72]), np.array([150, 70, 235]), np.array([236, 205, 255]))

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


def shade(h, alb, amb=0.42, dif=0.62, spec=0.2, sp=28):
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


def crystal(h, glow):
    d, m, l = (np.asarray(c, np.float32) for c in VIOLET)
    n = normals(h)
    ndl = np.clip((n * LIGHT).sum(-1), 0, 1)
    ndh = np.clip((n * HALF).sum(-1), 0, 1)
    base = d + (l - d) * (0.05 + 0.7 * ndl ** 1.8)[..., None]
    base = base + (m - base) * (0.5 * glow)[..., None]
    rgb = base + 255 * (0.7 * ndh ** 70)[..., None] + m * (0.2 * ndh ** 8)[..., None]
    return np.clip(rgb, 0, 255)


class Canvas:
    def __init__(self):
        self.rgb = np.zeros((N * K, N * K, 3), np.float32)
        self.a = np.zeros((N * K, N * K), np.float32)

    def over(self, rgb, a):
        da = self.a
        oa = a + da * (1 - a)
        self.rgb = (rgb * a[..., None] + self.rgb * (da * (1 - a))[..., None]) / np.maximum(oa, 1e-6)[..., None]
        self.a = oa

    def tint(self, col, a):
        self.rgb = self.rgb + (col - self.rgb) * a[..., None]

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
    """Anti-aliased coverage of a signed distance (negative inside), in texels."""
    return np.clip(0.5 - d * K, 0, 1).astype(np.float32)


def side_coords():
    """(u along, t across) for top, left, bottom, right."""
    return [(X, Y), (Y, X), (X, N - Y), (Y, N - X)]


# ------------------------------------------------------------------ feathers
def feather(lx, ly, root, ang, L, W):
    """A curved gold feather from `root`, at angle `ang` (radians, in the lx/ly frame), length L,
    half-width W. Returns (signed distance-ish, height)."""
    ca, sa = np.cos(ang), np.sin(ang)
    px, py = lx - root[0], ly - root[1]
    a = px * ca + py * sa
    b = -px * sa + py * ca
    s = np.clip(a / L, 0, 1)
    b = b + 0.08 * L * s * s            # the feather curls back toward the band's outer edge
    prof = W * np.sqrt(np.clip(s / 0.25, 0, 1)) * np.clip((1 - s) / 0.55, 0, 1) ** 0.9
    prof = np.maximum(prof, 1e-3)
    d = np.maximum(np.abs(b) - prof, np.maximum(-a, a - L))
    q = np.clip(np.abs(b) / prof, 0, 1)
    h = 1.6 * (1 - q * q) - 0.5 * np.exp(-(b / 0.35) ** 2) * (s > 0.08)   # rounded, with a quill groove
    # a few faint barb grooves, raking back from the quill
    h = h - 0.25 * (np.cos((a + 1.6 * np.abs(b)) * 2 * np.pi / 3.2) > 0.6) * (q > 0.25)
    return d, h


def wing(cv, lx, ly, mask, root, sgn, scale=1.0, base=6.0):
    """Three stacked feathers sweeping along +lx (sgn=1) or -lx; ly grows toward the window."""
    specs = [  # (root dy, angle, length, half-width), back feather first
        (-1.7, -0.06, 20.0, 2.3),
        (0.5, 0.0, 15.0, 2.2),
        (2.6, 0.06, 10.5, 2.0),
    ]
    for i, (dy, ang, L, Wd) in enumerate(specs):
        r = (root[0], root[1] + dy * scale)
        d, h = feather(sgn * (lx - r[0]) + r[0], ly, r, ang, L * scale, Wd * scale)
        m = cov(d) * mask
        cv.shadow(m, 0.6, 0.9, 0.8, 0.5)
        cv.over(gold(base + i * 0.8 + h), m)


# ------------------------------------------------------------------ the band
T = np.minimum(np.minimum(X, Y), np.minimum(N - X, N - Y))
OUT = (5.0, 7.6)       # outer gold rail
MAR = (7.6, 21.0)      # marble face
INN = (21.0, 23.6)     # inner gold rail
TC = (MAR[0] + MAR[1]) / 2


def band(cv):
    full = cov(np.maximum(OUT[0] - T, T - INN[1]))
    cv.shadow(full, 1.2, 1.6, 1.4, 0.55)
    mot = periodic_noise(3, 10.0, 5.0)
    vein_n = periodic_noise(8, 7.0, 3.0)
    vein_f = periodic_noise(12, 3.0, 1.5)
    a, b = MAR
    h = 2.6 + np.minimum(np.minimum(T - a, b - T), 2.2) * 0.8     # flat polished face, soft bevels
    var = np.zeros(X.shape, np.float32)
    vein = np.zeros(X.shape, np.float32)
    t_all = [Y, X, N - Y, N - X]
    owner = np.argmin(np.stack(t_all), 0)
    for i, (u, t) in enumerate(side_coords()):
        m = owner == i
        var = np.where(m, mot(u + 29 * i, t), var)
        vn = vein_n(u + 13 * i, t) + 0.45 * vein_f(u + 7 * i, t)
        vein = np.where(m, np.exp(-(vn / 0.09) ** 2) * 0.55 + np.exp(-((vn - 1.1) / 0.06) ** 2) * 0.3, vein)
    alb = MARBLE + (MARBLE_D - MARBLE) * np.clip(0.45 - 0.3 * var, 0, 1)[..., None]
    alb = alb + (VEIN - alb) * (0.55 * vein)[..., None]
    rgb = shade(h, alb)
    cv.over(rgb, cov(np.maximum(a - T, T - b)))
    for (lo, hi) in (OUT, INN):
        c, r = (lo + hi) / 2, (hi - lo) / 2
        d = np.abs(T - c) - r
        hh = 4.0 + 1.9 * np.sqrt(np.clip(1 - ((T - c) / r) ** 2, 0, 1))
        cv.over(gold(hh), cov(d))


# ------------------------------------------------------------------ edge ornament
def edge_ornament(cv):
    for u, t in side_coords():
        inseg = ((u > S - 3) & (u < N - S + 3) & (t < S)).astype(np.float32)
        # block joints at the period boundaries: a fine sunken seam lined with gold
        for uj in (S, S + P, S + 2 * P):
            dj = np.maximum(np.abs(u - uj) - 0.75, np.maximum(MAR[0] - t, t - MAR[1]))
            cv.over(np.zeros(X.shape + (3,), np.float32) + 40, cov(dj) * inseg * 0.6)
            dl = np.maximum(np.abs(u - uj) - 0.4, np.maximum(MAR[0] - t, t - MAR[1]))
            cv.over(gold(np.full(X.shape, 4.2, np.float32)), cov(dl) * inseg * 0.9)
        u0 = S + P / 2
        for k in range(2):
            uc = u0 + k * P
            lx, ly = u - uc, t - TC
            near = inseg * (np.abs(lx) < P / 2 - 1)
            # wings, sweeping out both ways from behind the crystal setting
            for sgn in (1, -1):
                wing(cv, lx, ly, near, (sgn * 4.0, 0.2), sgn, scale=1.0)
            # gold setting: a slender pointed oval, then the violet pylon crystal
            dset = np.abs(lx) / 4.6 + (np.abs(ly) / 9.6) ** 1.6 - 1.0
            dset = dset * 4.2
            ms = cov(dset) * near
            cv.shadow(ms, 0.8, 1.1, 1.0, 0.6)
            cv.over(gold(8.0 + np.clip(-dset, 0, 1.6) * 1.0), ms)
            # crystal: a long hexagonal prism, pointed at both ends, two flat facets with a ridge
            hx = 2.5
            dc = np.maximum(np.abs(lx) - hx, np.abs(lx) * 1.9 + np.abs(ly) - 7.6)
            mc = cov(dc) * near
            hc = 10.0 + 1.6 * (1 - np.abs(lx) / hx) + 0.7 * np.clip(-(np.abs(ly) - 5.0), 0, 1)
            cv.over(crystal(hc, sstep(-0.5, -2.0, dc)), mc)


# ------------------------------------------------------------------ corners
def corner_coords():
    """Local coords from each texture corner, and the sign of the x/y mirror."""
    return [(X, Y), (N - X, Y), (X, N - Y), (N - X, N - Y)]


def corners(cv):
    mot = periodic_noise(17, 5.0, 5.0, period=64)
    for lx0, ly0 in corner_coords():
        region = ((lx0 < S - 0.5) & (ly0 < S - 0.5)).astype(np.float32)
        lx, ly = lx0 - CC, ly0 - CC
        r = np.hypot(lx, ly)
        # wings along both edges, behind the medallion
        wing(cv, lx0, ly0 - TC, region, (CC + 8.0, 0.0), 1, scale=0.8, base=7.0)
        wing(cv, ly0, lx0 - TC, region, (CC + 8.0, 0.0), 1, scale=0.8, base=7.0)
        # pylon finial: a slender gold spire on the diagonal, pointing out at the corner
        dd = (lx + ly) / np.sqrt(2)          # along the diagonal (negative toward the corner)
        dp = (lx - ly) / np.sqrt(2)
        tip, base = -24.6, -9.0
        s = np.clip((dd - tip) / (base - tip), 0, 1)
        wsp = 0.5 + 3.6 * s ** 0.8
        dsp = np.maximum(np.abs(dp) - wsp, np.maximum(tip - dd, dd - base))
        msp = cov(dsp) * region
        cv.shadow(msp, 0.8, 1.0, 0.9, 0.55)
        hsp = 9.0 + 1.4 * np.clip(1 - np.abs(dp) / np.maximum(wsp, 0.3), 0, 1)
        cv.over(gold(hsp), msp)
        # a tiny violet crystal near the spire's tip
        dtc = np.abs(dp) * 1.2 + np.abs(dd + 18.2) - 3.2
        cv.over(crystal(11.0 + np.clip(-dtc, 0, 1.4), sstep(-0.3, -1.5, dtc)), cov(dtc) * region)
        # medallion: a gold ring round a cerulean enamel field bearing the Skyborne wind sigil in gold
        R0, R1 = 13.4, 11.0
        mo = cov(r - R0) * region
        cv.shadow(mo, 1.4, 1.8, 1.6, 0.7)
        c, rw = (R0 + R1) / 2, (R0 - R1) / 2
        hr = 10.0 + 1.9 * np.sqrt(np.clip(1 - ((r - c) / rw) ** 2, 0, 1))
        cv.over(gold(hr), mo)
        # enamel: slightly dished, darker toward the rim, a soft sheen at the top left
        he = 10.4 + 0.5 * np.clip((R1 - r) / 2.0, 0, 1) - 0.02 * r
        sheen = np.clip(1 - np.hypot(lx + 4, ly + 4) / 9, 0, 1)
        alb = CERULEAN + (CERULEAN_L - CERULEAN) * (0.6 * sheen)[..., None]
        alb = alb * (1 - 0.35 * sstep(R1 - 3.0, R1, r))[..., None]
        cv.over(shade(he, alb, amb=0.55, dif=0.5, spec=0.25), cov(r - R1) * region)
        # the sigil, upright in every corner (an emblem is not mirrored)


def sigil(cv):
    """The Skyborne wind sigil: a curl that sweeps down into an S-shaped gust, plus a second gust stroke."""
    for cx, cy in ((CC, CC), (N - CC, CC), (CC, N - CC), (N - CC, N - CC)):
        lx, ly = X - cx, Y - cy
        region = ((np.abs(lx) < 12) & (np.abs(ly) < 12)).astype(np.float32)
        d = np.full(X.shape, 99.0, np.float32)
        hh = np.zeros(X.shape, np.float32)
        for pts, w0, w1 in SIGIL:
            dd, s = polyline(lx, ly, pts)
            hw = w0 + (w1 - w0) * s
            hw = hw * np.clip(np.minimum(s, 1 - s) / 0.12 + 0.35, 0, 1)
            ds = dd - hw
            hs = 1.4 * np.sqrt(np.clip(1 - (dd / np.maximum(hw, 0.2)) ** 2, 0, 1))
            sel = ds < d
            d = np.where(sel, ds, d)
            hh = np.where(sel, hs, hh)
        m = cov(d) * region
        cv.shadow(m, 0.5, 0.7, 0.6, 0.55)
        cv.over(gold(12.0 + hh), m)


def polyline(px, py, pts):
    """Distance to a polyline and the normalised arc length of the nearest point."""
    pts = np.asarray(pts, np.float32)
    seg = np.diff(pts, axis=0)
    ln = np.hypot(seg[:, 0], seg[:, 1])
    cum = np.concatenate([[0], np.cumsum(ln)])
    best = np.full(px.shape, 1e9, np.float32)
    sb = np.zeros(px.shape, np.float32)
    for i in range(len(seg)):
        ax, ay = pts[i]
        dx, dy = seg[i]
        t = np.clip(((px - ax) * dx + (py - ay) * dy) / (ln[i] ** 2), 0, 1)
        dist = np.hypot(px - ax - t * dx, py - ay - t * dy)
        sel = dist < best
        best = np.where(sel, dist, best)
        sb = np.where(sel, (cum[i] + t * ln[i]) / cum[-1], sb)
    return best, sb


def _sig(pts):
    """Banner pixels (official Skyborne banner) -> medallion texels, centred, about 19 texels tall."""
    k = 19.0 / 357.0
    return [((x - 345) * k, (y - 422) * k) for x, y in pts]


# (points, half-width at start, half-width at end): the curl runs from its eye outward and down
SIGIL = [
    (_sig([(348, 300), (362, 303), (372, 288), (370, 266), (354, 250), (328, 243), (300, 251), (279, 273),
           (272, 302), (282, 336), (310, 370), (358, 404), (398, 440), (423, 490), (431, 545), (428, 600)]),
     0.7, 1.15),
    (_sig([(256, 430), (298, 466), (342, 515), (370, 565), (382, 600)]), 0.95, 0.75),
]


# ------------------------------------------------------------------ assembly
def BORDER():
    cv = Canvas()
    band(cv)
    edge_ornament(cv)
    corners(cv)
    sigil(cv)
    arr = np.array(cv.image())
    arr[S:N - S, S:N - S] = 0
    return Image.fromarray(arr, "RGBA")


# ================================================================== racial crest
# Blizzard drew no Skyborne crest, so this one is painted to sit beside theirs: 275:350, drawn at 2x.
# A pointed ivory-and-gold shield with the gold wind sigil on cerulean enamel, flanked by swept gold
# feathered wings, crowned by a slender pylon spire holding a glowing arcane-violet crystal.
CW, CH = 275, 350      # crest design units (the game's 275x350 crest box)
CS = 4                 # grid samples per design unit; output is 2x, so 2x2 supersampling
CGW, CGH = CW * CS, CH * CS
_cx = ((np.arange(CGW) + 0.5) / CS).astype(np.float32)
_cy = ((np.arange(CGH) + 0.5) / CS).astype(np.float32)
CMID = CW / 2

C_DARK = np.array([38, 22, 14], np.float32)          # painted outline
C_GOLD = (np.array([40, 26, 12]), np.array([158, 116, 54]), np.array([230, 202, 138]))   # aged gold
C_GRIME = np.array([30, 20, 12], np.float32)
C_FIELD_D = np.array([12, 28, 48], np.float32)       # the banner's muted steel blue
C_FIELD_L = np.array([66, 106, 140], np.float32)
C_GLOW = np.array([176, 104, 255], np.float32)


def _bez(p0, p1, p2, p3, n=24):
    t = np.linspace(0, 1, n)[:, None]
    p0, p1, p2, p3 = (np.asarray(p, np.float32) for p in (p0, p1, p2, p3))
    return ((1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t * t * p2 + t ** 3 * p3).tolist()


def _catmull(pts, n=8):
    p = np.asarray(pts, np.float32)
    p = np.vstack([2 * p[0] - p[1], p, 2 * p[-1] - p[-2]])
    out = []
    for i in range(1, len(p) - 2):
        a, b, c, d = p[i - 1], p[i], p[i + 1], p[i + 2]
        for t in np.linspace(0, 1, n, endpoint=False):
            out.append(0.5 * (2 * b + (c - a) * t + (2 * a - 5 * b + 4 * c - d) * t * t
                              + (3 * b - a - 3 * c + d) * t ** 3))
    out.append(p[-2])
    return np.asarray(out).tolist()


def _box(pts, margin):
    p = np.asarray(pts, np.float32)
    x0, y0 = p.min(0) - margin
    x1, y1 = p.max(0) + margin
    j0, j1 = max(int(x0 * CS), 0), min(int(x1 * CS) + 1, CGW)
    i0, i1 = max(int(y0 * CS), 0), min(int(y1 * CS) + 1, CGH)
    return i0, i1, j0, j1


def _pdist(pts, margin=30):
    """Distance (design units) to a polyline and the normalised arc length of the nearest point."""
    pts = np.asarray(pts, np.float32)
    i0, i1, j0, j1 = _box(pts, margin)
    px, py = _cx[None, j0:j1], _cy[i0:i1, None]
    seg = np.diff(pts, axis=0)
    ln = np.maximum(np.hypot(seg[:, 0], seg[:, 1]), 1e-6)
    cum = np.concatenate([[0], np.cumsum(ln)])
    best = np.full((i1 - i0, j1 - j0), 1e3, np.float32)
    sb = np.zeros_like(best)
    for k in range(len(seg)):
        ax, ay = pts[k]
        dx, dy = seg[k]
        t = np.clip(((px - ax) * dx + (py - ay) * dy) / (ln[k] ** 2), 0, 1)
        dist = np.hypot(px - ax - t * dx, py - ay - t * dy)
        sel = dist < best
        best = np.where(sel, dist, best)
        sb = np.where(sel, (cum[k] + t * ln[k]) / cum[-1], sb)
    D = np.full((CGH, CGW), 1e3, np.float32)
    Sx = np.zeros((CGH, CGW), np.float32)
    D[i0:i1, j0:j1] = best
    Sx[i0:i1, j0:j1] = sb
    return D, Sx


def _polysdf(pts):
    """Signed distance to a closed polygon (negative inside)."""
    from PIL import ImageDraw
    pts = [tuple(p) for p in pts]
    m = Image.new("L", (CGW, CGH), 0)
    ImageDraw.Draw(m).polygon([(x * CS, y * CS) for x, y in pts], fill=255)
    inside = np.asarray(m) > 127
    D, _ = _pdist(pts + [pts[0]], margin=60)
    return np.where(inside, -D, D)


def _stroke(pts, prof):
    """A tapered stroke: prof(s) gives the half-width along it. Returns (sdf, s, |dist|/halfwidth)."""
    D, s = _pdist(pts)
    hw = np.maximum(prof(s), 1e-3)
    return D - hw, s, np.clip(D / hw, 0, 1)


def _ccov(d):
    return np.clip(0.5 - d * CS, 0, 1).astype(np.float32)


def _cblur(a, sigma):
    """Gaussian blur, sigma in design units; done at a quarter of the grid for speed."""
    small = Image.fromarray(a.astype(np.float32), "F").resize((CGW // 4, CGH // 4), Image.BILINEAR)
    s = blur(np.asarray(small, np.float32), sigma * CS / 4)
    return np.asarray(Image.fromarray(s.astype(np.float32), "F").resize((CGW, CGH), Image.BILINEAR), np.float32)


def _cnormals(h):
    gy, gx = np.gradient(h * CS)
    n = np.stack([-gx, -gy, np.ones_like(h)], -1)
    return n / np.linalg.norm(n, axis=-1, keepdims=True)


def _light(h):
    n = _cnormals(h)
    return np.clip((n * LIGHT).sum(-1), 0, 1), np.clip((n * HALF).sum(-1), 0, 1)


def _vgrad():
    """A painter's top-down falloff: things read lighter at the top of the crest."""
    return (1.1 - 0.28 * (_cy / CH))[:, None] * np.ones((1, CGW), np.float32)


def _paint_gold(h, warm=1.0):
    d, m, l = (np.asarray(c, np.float32) for c in C_GOLD)
    ndl, ndh = _light(h)
    t = np.clip(ndl * _vgrad(), 0, 1)
    lo = d + (m - d) * np.clip(t / 0.55, 0, 1)[..., None]
    hi = m + (l - m) * (np.clip((t - 0.55) / 0.45, 0, 1) ** 1.3)[..., None]
    rgb = np.where((t < 0.55)[..., None], lo, hi)
    crisp = sstep(0.955, 0.985, ndh)               # only faces turned to the top-left light
    rgb = rgb * warm + (np.array([255, 240, 196], np.float32) - rgb * warm) * (0.6 * crisp)[..., None]
    return np.clip(rgb, 0, 255)


class _CCanvas:
    def __init__(self):
        self.rgb = np.zeros((CGH, CGW, 3), np.float32)
        self.a = np.zeros((CGH, CGW), np.float32)

    def over(self, rgb, a):
        da = self.a
        oa = a + da * (1 - a)
        rgb = np.broadcast_to(np.asarray(rgb, np.float32), self.rgb.shape)
        self.rgb = (rgb * a[..., None] + self.rgb * (da * (1 - a))[..., None]) / np.maximum(oa, 1e-6)[..., None]
        self.a = oa

    def tint(self, col, a):
        self.rgb = self.rgb + (np.asarray(col, np.float32) - self.rgb) * a[..., None]

    def shadow(self, a, dx, dy, sig, op):
        sx, sy = int(round(dx * CS)), int(round(dy * CS))
        sh = np.zeros_like(a)
        sh[sy:, sx:] = a[:CGH - sy, :CGW - sx]
        self.over(np.zeros(3, np.float32), np.clip(_cblur(sh, sig), 0, 1) * op)

    def piece(self, d, rgb, outline=1.3, shadow=(1.0, 1.6, 1.4, 0.55)):
        """Lay a shape with a soft cast shadow, a dark painted outline and its fill."""
        if shadow:
            self.shadow(_ccov(d - outline), *shadow)
        if outline:
            self.over(C_DARK, _ccov(d - outline))
        self.over(rgb, _ccov(d))

    def image(self):
        pm = np.concatenate([self.rgb * self.a[..., None], self.a[..., None]], -1)
        pm = pm.reshape(CGH // 2, 2, CGW // 2, 2, 4).mean((1, 3))
        a = pm[..., 3:4]
        rgb = np.where(a > 0, pm[..., :3] / np.maximum(a, 1e-6), 0)
        return Image.fromarray(np.clip(np.concatenate([rgb, a * 255], -1) + 0.5, 0, 255).astype(np.uint8), "RGBA")


def _mirror(pts):
    return [(2 * CMID - x, y) for x, y in pts]


def _lownoise(seed, cell, sigma):
    """Smooth unit noise over the crest grid: `cell` design units per random sample."""
    rng = np.random.default_rng(seed)
    nz = rng.standard_normal((CH // cell + 2, CW // cell + 2)).astype(np.float32)
    nz = np.asarray(Image.fromarray(nz, "F").resize((CGW, CGH), Image.BICUBIC), np.float32)
    nz = _cblur(nz, sigma)
    return (nz - nz.mean()) / (nz.std() + 1e-6)


def _noise2(seed, cx, cy, sigma=0.0):
    """Unit noise with separate cell sizes along x and y (cy >> cx gives brushed streaks)."""
    rng = np.random.default_rng(seed)
    nz = rng.standard_normal((int(CH / cy) + 2, int(CW / cx) + 2)).astype(np.float32)
    nz = np.asarray(Image.fromarray(nz, "F").resize((CGW, CGH), Image.BICUBIC), np.float32)
    if sigma:
        nz = _cblur(nz, sigma)
    return (nz - nz.mean()) / (nz.std() + 1e-6)


# ------------------------------------------------------------------ crest parts
SH_TOP, SH_SHOULDER, SH_POINT = 96.0, (200.0, 106.0), 334.0


def _shield_outline():
    sx, sy = SH_SHOULDER
    right = (_bez((CMID, SH_TOP), (152, 106), (178, 112), (sx, sy), 20)
             + _bez((sx, sy), (197, 146), (196, 186), (189, 220), 20)[1:]
             + _bez((189, 220), (180, 268), (158, 306), (CMID, SH_POINT), 24)[1:])
    left = _mirror(right[::-1])
    return right + left[1:-1]


# left wing (mirrored for the right): primaries, top/leading first; (root, angle deg, length, half-width)
# Every tip sweeps outward and up; each lower feather is shorter, turned ~11 degrees further down.
PRIMARIES = [
    ((106, 126), 147, 124, 15.5),
    ((104, 140), 158, 108, 15.5),
    ((103, 154), 169, 94, 15.0),
    ((103, 168), 180, 80, 14.0),
    ((104, 182), 191, 66, 13.0),
]
COVERTS = [   # a short row of ivory coverts over the primaries' roots
    ((96, 128), 150, 46, 10.5),
    ((93, 143), 161, 42, 10.5),
    ((92, 158), 172, 38, 10.0),
    ((93, 173), 183, 32, 9.0),
]


def _feather(root, ang, L, W, bow=0.3):
    r = np.asarray(root, np.float32)
    a = np.radians(ang)
    v = np.array([np.cos(a), -np.sin(a)], np.float32) * L
    nrm = np.array([v[1], -v[0]], np.float32) / L
    if nrm[1] > 0:
        nrm = -nrm                      # bow toward the top, so the tips sweep upward
    pts = _bez(r, r + 0.4 * v, r + 0.78 * v + 0.15 * bow * L * nrm, r + v + bow * L * nrm, 30)

    def prof(s):     # full almost from the root, rounded shoulder, then a point
        return W * np.clip(s / 0.1, 0.55, 1) ** 0.5 * np.clip((1 - s) / 0.62, 0, 1) ** 0.85
    d, s, q = _stroke(pts, prof)
    h = 3.2 * np.sqrt(1 - q * q) + 1.2 * np.exp(-(q / 0.14) ** 2) * (s > 0.04) * (s < 0.88)  # quill ridge
    # barbs: fine grooves raking back from the quill
    h = h - 0.16 * (0.5 + 0.5 * np.cos(s * L / 2.4 * 2 * np.pi + q * 3.2)) * sstep(0.18, 0.4, q)
    return d, h, pts


def _sigil_strokes(k=0.37, ox=132.0, oy=204.0):
    """The Skyborne wind sigil traced from the official banner (banner pixels -> design units)."""
    def bmap(pts):
        return [(ox + (x - 343.5) * k, oy + (y - 421.5) * k) for x, y in pts]
    return [
        (bmap(_catmull([(348, 300), (362, 303), (372, 288), (370, 266), (354, 250), (328, 243), (300, 251),
                        (279, 273), (272, 302), (282, 336), (310, 370), (358, 404), (398, 440), (423, 490),
                        (431, 545), (428, 600)])), 3.8, 7.4),
        (bmap(_catmull([(256, 430), (298, 466), (342, 515), (370, 565), (382, 600)])), 6.6, 5.0),
    ]


CZOOM = 0.92  # the painted emblem's share of the crest box
OLS = 3.2  # outline round the whole silhouette
OL = 2.2   # silhouette outline width (design units) - it must survive the 0.25x game scale


def CREST_ART():
    cv = _CCanvas()
    xx = _cx[None, :] - CMID
    yy = _cy[:, None]
    tarnish = _lownoise(11, 6, 1.5)
    hammer = _noise2(31, 2.2, 2.2, 0.6)
    brushed = _noise2(32, 0.6, 9.0)
    nicks = sstep(2.5, 2.8, _noise2(33, 1.4, 1.4))

    def gold(h, warm=1.0):
        """Aged gold: hammered dents, brushed streaks, small nicks, grime in the crevices."""
        hh = h + 0.05 * hammer - 0.5 * nicks
        rgb = _paint_gold(hh, warm) * (1 + 0.07 * tarnish + 0.035 * brushed)[..., None]
        cav = np.clip(_cblur(hh, 1.2) - hh, 0, None)
        g = np.clip(cav * 0.9 + 0.12 * np.clip(-tarnish, 0, None), 0, 0.75)
        return np.clip(rgb + (C_GRIME - rgb) * g[..., None], 0, 255)

    feathers = []      # (layer, sdf, height)
    for side in (0, 1):
        for row, spec in ((0, PRIMARIES), (1, COVERTS)):
            for i, (root, ang, L, W) in enumerate(spec):
                if side:
                    root = _mirror([root])[0]
                    ang = 180 - ang
                d, h, _ = _feather(root, ang, L, W)
                feathers.append((row, i, d, h))
        for i, (root, ang, L, W) in enumerate(PRIMARIES[:-1]):   # a darker layer showing between them
            root, ang, L = (root[0] - 2, root[1] + 7), ang + 5.5, L * 0.97
            if side:
                root = _mirror([root])[0]
                ang = 180 - ang
            d, h, _ = _feather(root, ang, L, W * 0.9)
            feathers.append((-1, i, d, h))
    shield = _polysdf(_shield_outline())
    crys_hw, crys_top, crys_bot = 19.0, 8.0, 104.0
    cyc, half_len = (crys_top + crys_bot) / 2, (crys_bot - crys_top) / 2
    crys = np.maximum(np.abs(xx) - crys_hw, np.abs(xx) * 1.45 + np.abs(yy - cyc) - half_len)
    # mount: two upright gold prongs rising from the shield's crown to hold the crystal, a pylon's crystal setting
    cradle = np.full((CGH, CGW), 1e3, np.float32)
    hcr = np.zeros_like(cradle)
    for sg in (-1, 1):
        claw = _bez((CMID + sg * 6, 110), (CMID + sg * 24, 106), (CMID + sg * 25, 86), (CMID + sg * 23, 56), 24)
        dcl, scl, qcl = _stroke(claw, lambda s: 5.4 * (1 - 0.88 * s ** 1.3))
        sel = dcl < cradle
        cradle = np.where(sel, dcl, cradle)
        hcr = np.where(sel, 13.0 + 2.4 * np.sqrt(1 - qcl * qcl), hcr)

    # soft drop shadow from the whole silhouette
    sil = _ccov(np.minimum(np.minimum(shield, cradle), crys) - OL)
    for _, _, d, _ in feathers:
        sil = np.maximum(sil, _ccov(d - OL))
    sh = _cblur(sil, 6.0)
    shoff = np.zeros_like(sh)
    oy, ox = int(5 * CS), int(2 * CS)
    shoff[oy:, ox:] = sh[:-oy, :-ox]
    cv.over(np.zeros(3, np.float32), np.clip(np.maximum(shoff * 1.1, _cblur(sil, 9) * 0.85), 0, 1))
    silo = _ccov(np.minimum(np.minimum(shield, cradle), crys) - OLS)
    for _, _, d, _ in feathers:
        silo = np.maximum(silo, _ccov(d - OLS))
    cv.over(C_DARK * 0.6, silo)

    # ---- wings, behind the shield: primaries bottom-up, then the coverts over their roots
    for row in (-1, 0, 1):
        layer = [f for f in feathers if f[0] == row]
        for _, i, d, h in sorted(layer, key=lambda f: -f[1]):
            if row == -1:
                rgb = gold(4.0 + h, warm=0.5)
            elif row == 0:
                rgb = gold(5.0 + h, warm=0.78 + 0.05 * (4 - i))
            else:
                ndl, ndh = _light(7.0 + h)
                rgb = np.clip(MARBLE * (0.5 + 0.58 * ndl * _vgrad())[..., None] * np.array([1.0, 0.98, 0.93])
                              + 255 * (0.25 * ndh ** 30)[..., None], 0, 255)
            cv.piece(d, rgb, outline=OL if row == 0 else 1.6, shadow=(0.8, 1.8, 1.8, 0.6))
    # occlusion where the wings tuck in behind the shield
    cv.over(np.zeros(3, np.float32), np.clip(_cblur(_ccov(shield), 6.0) * 0.75, 0, 1) * (1 - _ccov(shield)))

    # ---- shield: gold rim, ivory marble band, gold inner line, cerulean enamel field
    ds = shield
    cv.shadow(_ccov(ds - OL), 1.4, 2.4, 2.2, 0.7)
    cv.over(C_DARK, _ccov(ds - OL))
    nz = _lownoise(5, 4, 2.0)
    nz2 = _lownoise(6, 2, 0.6)
    patch = _lownoise(7, 10, 3.0)
    vein = np.maximum(np.exp(-(nz / 0.08) ** 2), 0.6 * np.exp(-((nz2 + 0.3 * nz) / 0.07) ** 2))
    alb = (MARBLE * np.array([1.0, 0.97, 0.9], np.float32)
           + (MARBLE_D - MARBLE) * np.clip(0.5 - 0.35 * patch, 0, 1)[..., None])
    alb = alb + (VEIN - alb) * (0.5 * vein)[..., None]
    RO, RM, RI = 5.5, 15.0, 19.0
    hm = 8.0 + np.minimum(np.minimum(-ds - RO, RM + ds), 2.0) * 0.8
    ndl, ndh = _light(hm)
    marble = np.clip(alb * (0.46 + 0.6 * ndl * _vgrad())[..., None] + 255 * (0.2 * ndh ** 26)[..., None], 0, 255)
    cv.over(marble, _ccov(np.maximum(ds, -ds - RM)))
    so = _shield_outline()
    _, sarc = _pdist(so + [so[0]], margin=8)
    rim_notch = np.exp(-((((sarc * 760.0) % 9.0) - 4.5) / 0.5) ** 2)    # engraved cross-notches
    # occlusion on the marble under the raised outer rim
    rim = _ccov(np.abs(-ds - RO / 2) - RO / 2)
    cv.shadow(rim, 1.0, 1.6, 1.4, 0.55)
    for lo, hi in ((0.0, RO), (RM, RI)):
        c, r = (lo + hi) / 2, (hi - lo) / 2
        dd = np.abs(-ds - c) - r
        hh = 9.0 + 2.4 * np.sqrt(np.clip(1 - ((-ds - c) / r) ** 2, 0, 1))
        if lo == 0.0:   # engrave the outer rim: a centre groove broken by cross-notches
            hh = hh - 0.9 * np.exp(-((-ds - c) / 0.45) ** 2) * (1 - rim_notch)
            hh = hh - 0.8 * rim_notch * (np.abs(-ds - c) < r - 0.8)
        cv.over(C_DARK, _ccov(dd - 0.8) * 0.8)
        cv.over(gold(hh), _ccov(dd))
    # gold rivets studding the marble band
    outline = _shield_outline()
    pts = np.asarray(outline + [outline[0]], np.float32)
    seg = np.hypot(*np.diff(pts, axis=0).T)
    cum = np.concatenate([[0], np.cumsum(seg)])
    for k in range(1, 16):
        u = cum[-1] * k / 16 + cum[-1] / 32
        j = np.searchsorted(cum, u) - 1
        p = pts[j] + (pts[j + 1] - pts[j]) * (u - cum[j]) / max(seg[j], 1e-6)
        # step inward to the band's middle
        tng = (pts[j + 1] - pts[j]) / max(seg[j], 1e-6)
        inward = np.array([-tng[1], tng[0]])
        q = p + inward * (RO + RM) / 2
        if np.hypot(q[0] - CMID, q[1] - SH_TOP) < 30:     # keep clear of the crystal mount
            continue
        rr = np.hypot(_cx[None, :] - q[0], _cy[:, None] - q[1])
        cv.shadow(_ccov(rr - 2.6), 0.6, 0.9, 0.7, 0.6)
        cv.over(C_DARK, _ccov(rr - 2.9))
        cv.over(gold(10 + 2.2 * np.sqrt(np.clip(1 - (rr / 2.3) ** 2, 0, 1))), _ccov(rr - 2.3))
    df = ds + RI
    fm = _ccov(df)
    hf = 9.0 - 0.6 * np.clip(-df / 6, 0, 1)
    sheen = np.clip(1 - np.hypot(_cx[None, :] - 112, _cy[:, None] - 150) / 125, 0, 1)
    brush = _lownoise(21, 9, 2.5)
    mottle = _noise2(22, 2.5, 2.5, 0.5)
    alb = C_FIELD_D + (C_FIELD_L - C_FIELD_D) * (sheen ** 1.3)[..., None]
    alb = alb * (1 + 0.07 * brush + 0.06 * mottle)[..., None] * (1.12 - 0.3 * (_cy[:, None] - 110) / 220)[..., None]
    lat = np.minimum(np.abs(((_cx[None, :] + _cy[:, None]) % 10.0) - 5.0),
                     np.abs(((_cx[None, :] - _cy[:, None]) % 10.0) - 5.0))
    lattice = np.exp(-(lat / 0.45) ** 2)     # faint engraved diamond lattice
    ndl, ndh = _light(hf)
    enamel = np.clip(alb * (0.8 + 0.25 * ndl)[..., None], 0, 255)
    # worn edge: chips where the enamel meets the rim show the dull metal beneath
    chip = sstep(0.3, 0.6, _noise2(23, 1.8, 1.8, 0.3)) * sstep(-4.5, -1.0, df)
    enamel = enamel + (np.array([92, 74, 50], np.float32) - enamel) * (0.75 * chip)[..., None]
    cv.over(enamel, fm)
    inner = np.zeros_like(fm)
    o1, o2 = int(1.5 * CS), int(2.5 * CS)
    inner[o2:, o1:] = (1 - fm)[:-o2, :-o1]
    cv.over(np.array([2, 10, 30], np.float32), np.clip(_cblur(inner, 3.0), 0, 1) * fm * 0.85)

    # fine gold inner line inset from the field's edge
    dl = np.abs(df + 6.0) - 0.75
    cv.over(C_DARK, _ccov(dl - 0.5) * fm * 0.8)
    cv.over(gold(10.5 + 0.8 * np.clip(-dl / 0.75, 0, 1)), _ccov(dl) * fm)

    # ---- the wind sigil, raised gold on the enamel
    dsig = np.full((CGH, CGW), 1e3, np.float32)
    hsig = np.zeros_like(dsig)
    for pts_, w0, w1 in _sigil_strokes():
        def prof(s, w0=w0, w1=w1):
            return (w0 + (w1 - w0) * s) * np.clip(np.minimum(s / 0.06, (1 - s) / 0.22), 0.25, 1) ** 0.7
        d, s, q = _stroke(pts_, prof)
        sel = d < dsig
        dsig = np.where(sel, d, dsig)
        hsig = np.where(sel, 2.6 * np.sqrt(1 - q * q), hsig)
    clip = _ccov(df + 1.0)
    keep = (1 - np.clip(_cblur(_ccov(dsig - 5.0), 1.5) * 1.5, 0, 1)) * _ccov(df + 9.0)
    cv.over(np.array([6, 16, 30], np.float32), lattice * keep * 0.28)
    cv.shadow(_ccov(dsig - 1.4) * clip, 1.4, 2.2, 1.8, 0.8)
    cv.over(C_DARK, _ccov(dsig - 1.4) * clip)
    cv.over(gold(12.0 + hsig), _ccov(dsig) * clip)

    # ---- gold clasps binding the wings to the shield's flanks
    for sg in (-1, 1):
        qx, qy = CMID + sg * 62.5, 146.0
        lx, ly = _cx[None, :] - qx, _cy[:, None] - qy
        dcl = (np.abs(lx) / 7.5 + np.abs(ly) / 11.0 - 1.0) * 6.5
        rr = np.hypot(lx, ly)
        hcl = 12.0 + np.clip(-dcl, 0, 2.2) * 0.9 - 0.8 * np.exp(-((rr - 3.6) / 0.45) ** 2)
        hcl = hcl + 1.4 * np.sqrt(np.clip(1 - (rr / 2.2) ** 2, 0, 1))
        cv.piece(dcl, gold(hcl), outline=1.6, shadow=(1.0, 1.8, 1.6, 0.65))

    # ---- the pylon crystal on the shield's crown: glow, gold cradle, faceted arcane violet, glint
    glow = _cblur(_ccov(crys), 10.0)
    cv.over(C_GLOW, np.clip(glow * 0.9, 0, 1) * (1 - _ccov(crys)) * 0.8)
    cv.shadow(_ccov(crys - OL), 1.0, 1.8, 1.6, 0.55)
    cv.over(np.array([26, 4, 52], np.float32), _ccov(crys - OL))
    hc = np.minimum(crys_hw - np.abs(xx), (half_len - np.abs(yy - cyc)) / 1.45) * 0.9
    ndl, ndh = _light(hc)
    vd, vm, vl = (np.asarray(c, np.float32) for c in VIOLET)
    lo = vd + (vm - vd) * np.clip(ndl / 0.5, 0, 1)[..., None]
    hi = vm + (vl - vm) * np.clip((ndl - 0.5) / 0.5, 0, 1)[..., None]
    base = np.where((ndl < 0.5)[..., None], lo, hi)
    core = np.clip(1 - np.hypot(xx / 9, (yy - cyc - 8) / 28), 0, 1)
    base = base + (np.array([255, 220, 255], np.float32) - base) * (0.5 * core ** 1.4)[..., None]
    cv.over(np.clip(base + 255 * (0.6 * ndh ** 60)[..., None], 0, 255), _ccov(crys))
    cv.piece(cradle, gold(hcr), outline=1.6, shadow=(1.0, 1.6, 1.4, 0.6))
    gx, gy = xx + 7, yy - 36
    star = np.maximum(np.exp(-(gx / 0.8) ** 2 - (gy / 9) ** 2), np.exp(-(gx / 6) ** 2 - (gy / 0.8) ** 2))
    cv.tint((255, 255, 255), np.clip(star * 0.95, 0, 1) * _ccov(crys))

    # settle the emblem into the box with a little padding, as Blizzard's crests sit
    img = cv.image()
    w, h = img.size
    small = img.resize((round(w * CZOOM), round(h * CZOOM)), Image.LANCZOS)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.alpha_composite(small, ((w - small.width) // 2, (h - small.height) // 2 + 4))
    return out
