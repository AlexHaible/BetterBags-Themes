"""Windshaper Skyborne classic border: elemental air of Skywall and the Zephras banner.

A slim band of cerulean steel-blue enamel (the Skyborne banner's field) between a thin silver-grey
outer rail and a thin silver-grey inner rail. Inlaid along each edge is the banner's wind sigil,
in raised silver: a spiral curl that flows into an S-shaped sweep with a second, shorter tail
beside it, a stylised gust. The sigils blow outward from the middle of each edge, where a small
silver mount holds a round pale-cyan windstone flanked by two fletched silver hippogryph feathers.
Each corner is a cloud-white stone plate with the banner's quarter-circle arc on its inner side,
edged in silver, carrying a silver ring around a cerulean disc in which a silver wind curl
swirls about a windstone. A soft pale-cyan air glow lies around the sigils and windstones.
Light from the top left; metal, stone and enamel shaded from height maps.
"""
import numpy as np
from PIL import Image

THEME = dict(
    Name="RacesWindshaperSkyborne", Background="SOLID", BackgroundInset=8,
    Color=(0.05, 0.08, 0.13, 0.8), Slice=44, Outset=22, TitleY=40, Close={"X": 22, "Y": 22},
    Search=("TOPRIGHT", -22, -2), Menu={"X": -26, "Y": 26},
    TabEdge=(0.72, 0.76, 0.82, 1), TabAccent=(0.3, 0.62, 0.86, 1),
)
CREST = None  # textures/WindshaperSkyborneCrest.png (the default; drawn by CREST_ART)

N = 256
S = 44
SEG = N - 2 * S  # 168
K = 3
CC = 18.5        # corner rosette centre, from the outer edges

LIGHT = np.array([-0.5, -0.62, 0.6])
LIGHT = LIGHT / np.linalg.norm(LIGHT)
HALF = LIGHT + np.array([0, 0, 1.0])
HALF = HALF / np.linalg.norm(HALF)

SILVER = np.array([150, 160, 174], np.float32)
SILVER_L = np.array([246, 250, 255], np.float32)
CLOUD = np.array([232, 238, 245], np.float32)
CLOUD_D = np.array([196, 208, 222], np.float32)
CERU = np.array([56, 128, 178], np.float32)
CERU_D = np.array([34, 88, 136], np.float32)
GLOW = np.array([175, 238, 255], np.float32)
WIND = (np.array([20, 80, 112]), np.array([90, 200, 232]), np.array([225, 252, 255]))

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


def periodic_noise(seed, sig_u, sig_t, period=SEG):
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


def shade(h, alb, amb=0.36, dif=0.68, spec=0.14, sp=24):
    n = normals(h)
    ndl = np.clip((n * LIGHT).sum(-1), 0, 1)
    ndh = np.clip((n * HALF).sum(-1), 0, 1)
    return np.clip(alb * (amb + dif * ndl)[..., None] + 255 * (spec * ndh ** sp)[..., None], 0, 255)


def silver(h):
    n = normals(h)
    ndl = np.clip((n * LIGHT).sum(-1), 0, 1)
    ndh = np.clip((n * HALF).sum(-1), 0, 1)
    alb = SILVER * 0.6 + (SILVER_L - SILVER * 0.6) * (ndl ** 2.0)[..., None]
    rgb = alb * (0.38 + 0.58 * ndl)[..., None] + 255 * (0.42 * ndh ** 30)[..., None]
    return np.clip(rgb, 0, 255)


def windstone(h, glow):
    d, m, l = (np.asarray(c, np.float32) for c in WIND)
    n = normals(h)
    ndl = np.clip((n * LIGHT).sum(-1), 0, 1)
    ndh = np.clip((n * HALF).sum(-1), 0, 1)
    base = d + (l - d) * (0.08 + 0.7 * ndl ** 1.6)[..., None]
    base = base + (m - base) * (0.5 * glow)[..., None]
    rgb = base + 255 * (0.8 * ndh ** 60)[..., None] + m * (0.25 * ndh ** 6)[..., None]
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
    t = [Y, X, N - Y, N - X]
    m = np.argmin(np.stack(t), 0)
    return m == i


# ------------------------------------------------------------------ strokes
def bezier(p0, p1, p2, p3, n=40):
    s = np.linspace(0, 1, n)[:, None]
    return ((1 - s) ** 3) * p0 + 3 * ((1 - s) ** 2) * s * p1 + 3 * (1 - s) * s * s * p2 + s ** 3 * p3


def spiral(c, r0, r1, a0, turns, n=60):
    """Points from angle a0 at radius r0 winding by `turns` (signed) to radius r1."""
    s = np.linspace(0, 1, n)
    a = a0 + 2 * np.pi * turns * s
    r = r0 + (r1 - r0) * s
    return np.stack([c[0] + r * np.cos(a), c[1] + r * np.sin(a)], -1)


def stroke_sdf(px, py, pts, w):
    """Signed distance to a polyline whose half-width varies per vertex."""
    d = np.full(px.shape, 1e9, np.float32)
    for i in range(len(pts) - 1):
        ax, ay = pts[i]
        bx, by = pts[i + 1]
        vx, vy = bx - ax, by - ay
        ll = vx * vx + vy * vy + 1e-9
        s = np.clip(((px - ax) * vx + (py - ay) * vy) / ll, 0, 1)
        dist = np.hypot(px - ax - s * vx, py - ay - s * vy)
        d = np.minimum(d, dist - (w[i] + (w[i + 1] - w[i]) * s))
    return d


def sigil_strokes():
    """The banner's wind sigil laid along the band, in (a along, b across) with the curl at a=0.
    A spiral curl whose outer arm leaves at the bottom and sweeps on in a gentle S that tapers to a
    point, and a second shorter tail sweeping beside it."""
    c = np.array([4.6, -0.6])
    # the curl, from its centre outward: ~1.15 turns, ending at the bottom heading +a
    cur = spiral(c, 1.0, 4.4, np.pi / 2 + 2 * np.pi * 1.15, -1.15, 50)
    wc = np.linspace(0.7, 1.45, len(cur))
    p0 = cur[-1]
    sweep = bezier(p0, p0 + np.array([9.0, 0.0]), np.array([20.0, -4.6]), np.array([40.0, -2.6]), 50)
    ws = 1.45 * (1 - np.linspace(0, 1, len(sweep))) ** 0.8 + 0.05
    main = np.concatenate([cur, sweep[1:]])
    wm = np.concatenate([wc, ws[1:]])
    tail = bezier(np.array([12.5, 4.6]), np.array([18.0, 4.0]), np.array([22.0, 1.6]), np.array([31.0, 2.4]), 40)
    wt = 1.05 * np.sin(np.linspace(0.25, 1.0, len(tail)) * np.pi * 0.5) ** 0.3 * (1 - np.linspace(0, 1, len(tail))) ** 0.8 + 0.05
    sc = np.array([1.3, 1.22])
    return [(main * sc, wm * 1.7), (tail * sc, wt * 1.6)]


def sigil_field(a, b):
    d = np.full(a.shape, 1e9, np.float32)
    for pts, w in sigil_strokes():
        d = np.minimum(d, stroke_sdf(a, b, pts, w))
    return d


# ------------------------------------------------------------------ the band
T = np.minimum(np.minimum(X, Y), np.minimum(N - X, N - Y))
OUT = (6.0, 9.0)      # outer silver rail
FLD = (9.0, 27.0)     # cerulean enamel field
INN = (27.0, 30.0)    # inner silver rail
TC = (FLD[0] + FLD[1]) / 2
MID = S + SEG / 2     # segment centre: the windstone mount
SIG0 = 21.5           # sigil curl offset from the mount


def edge_sigils():
    """Signed distance of the sigils on each side: per side, mirrored about the segment centre."""
    out = np.full(X.shape, 1e9, np.float32)
    for i, (u, t) in enumerate(side_coords()):
        m = side_mask(i)
        du = u - MID
        a = np.abs(du) - SIG0
        b = t - TC
        sel = m & (a > -8) & (a < 58) & (np.abs(b) < 9)
        if sel.any():
            out[sel] = sigil_field(a[sel], b[sel])
    return out


def band(cv):
    full = cov(np.maximum(OUT[0] - T, T - INN[1]))
    cv.shadow(full, 1.2, 1.6, 1.4, 0.6)
    mot = periodic_noise(3, 10.0, 5.0)
    fine = periodic_noise(5, 1.0, 1.0)
    var = np.zeros(X.shape, np.float32)
    for i, (u, t) in enumerate(side_coords()):
        m = side_mask(i)
        var = np.where(m, 0.7 * mot(u + 31 * i, t) + 0.2 * fine(u + 17 * i, t), var)
    a, b = FLD
    # enamel: sunk a little below the rails, with a soft lip at each side
    h = 2.0 + 0.6 * sstep(0, 1.6, np.minimum(T - a, b - T)) + 0.05 * var
    alb = CERU + (CERU_D - CERU) * np.clip(0.4 - 0.18 * var + 0.35 * np.abs(T - TC) / 9, 0, 1)[..., None]
    rgb = shade(h, alb, amb=0.5, dif=0.55, spec=0.1)
    sd = edge_sigils()
    sm = cov(sd)
    # restrained pale-cyan air glow around the sigils
    halo = np.clip(blur(sm, 2.2 * K) * 1.4, 0, 1) * (1 - sm)
    rgb = rgb + (GLOW - rgb) * (0.32 * halo)[..., None]
    cv.over(rgb, cov(np.maximum(a - T, T - b)))
    # sigils: raised silver applique with a rounded profile
    cv.shadow(sm, 0.7, 0.9, 0.8, 0.55)
    hs = 4.0 + 1.6 * np.sqrt(np.clip(-sd / 1.2, 0, 1))
    cv.over(silver(hs), sm)
    # silver-grey rails, rounded
    for lo, hi in (OUT, INN):
        c, r = (lo + hi) / 2, (hi - lo) / 2
        hh = 4.0 + 2.2 * np.sqrt(np.clip(1 - ((T - c) / r) ** 2, 0, 1))
        cv.over(silver(hh), cov(np.abs(T - c) - r))


# ------------------------------------------------------------------ edge mounts
def feather(lx, ly, L, W):
    """A feather lying along +lx from its quill base at lx=0. Returns (sdf, height)."""
    s = np.clip(lx / L, 0, 1)
    hw = W * np.sin(np.pi * np.clip(s, 0, 1) ** 0.8) ** 0.7 + 0.15
    d = np.maximum(np.abs(ly) - hw, np.maximum(-lx, lx - L))
    # quill ridge and barb grooves angled back from the shaft toward the tip
    barb = np.abs(((lx + 1.4 * np.abs(ly)) / 2.1) % 1.0 - 0.5)
    h = 1.2 * np.sqrt(np.clip(1 - (ly / (hw + 1e-6)) ** 2, 0, 1)) + 0.9 * sstep(0.7, 0.1, np.abs(ly))
    h = h - 0.45 * sstep(0.18, 0.05, barb) * (np.abs(ly) > 0.6)
    return d, h


def edge_mounts(cv):
    for u, t in side_coords():
        inseg = (u > S) & (u < N - S) & (t < S)
        lx, ly = u - MID, t - TC
        # two fletched feathers, quills under the mount, tips along the band
        for sgn in (-1, 1):
            df, hf = feather(sgn * lx - 4.5, ly, 14.0, 3.6)
            mf = cov(df) * inseg
            cv.shadow(mf, 0.8, 1.0, 0.9, 0.55)
            cv.over(silver(5.0 + hf), mf)
        # silver lozenge mount
        dl = np.abs(lx) / 0.95 + np.abs(ly) - 9.2
        ml = cov(dl) * inseg
        cv.shadow(ml, 1.0, 1.3, 1.2, 0.6)
        cv.over(silver(7.0 + np.minimum(-dl, 1.8) * 1.0), ml)
        # round windstone cabochon
        r = np.hypot(lx, ly)
        dg = r - 4.6
        mg = cov(dg) * inseg
        cv.over(np.zeros(X.shape + (3,), np.float32) + 25, cov(r - 5.3) * inseg * 0.6)
        hg = 10.0 + 3.0 * np.sqrt(np.clip(1 - (r / 4.6) ** 2, 0, 1))
        cv.over(windstone(hg, sstep(0, 3.5, -dg)), mg)


# ------------------------------------------------------------------ corners
def corner_coords():
    return [(X, Y), (N - X, Y), (X, N - Y), (N - X, N - Y)]


def corners(cv):
    mot = periodic_noise(11, 6.0, 6.0, period=64)
    for lx0, ly0 in corner_coords():
        region = (lx0 < S) & (ly0 < S)
        # cloud-white plate: square to the outside, the banner's quarter arc on the inside
        rq = np.hypot(lx0 - 2.0, ly0 - 2.0)
        dp = np.maximum(np.maximum(3.0 - lx0, 3.0 - ly0), rq - 37.0)
        mp = cov(dp) * region
        cv.shadow(mp, 1.5, 1.9, 1.7, 0.65)
        cv.over(silver(5.0 + np.minimum(-dp, 1.6) * 1.2), mp)
        var = mot(lx0 + 7, ly0)
        di = dp + 2.2
        h = 6.2 + np.minimum(-di, 1.8) * 0.8 + 0.08 * var
        alb = CLOUD + (CLOUD_D - CLOUD) * np.clip(0.4 - 0.3 * var, 0, 1)[..., None]
        # a recessed cerulean arc inlay echoing the banner's quarter arcs
        dq = np.abs(rq - 31.6) - 1.0
        h = h - 0.9 * sstep(0.4, -0.6, dq)
        rgb = shade(h, alb, amb=0.66, dif=0.42, spec=0.1)
        rgb = np.where((dq < 0)[..., None], shade(h, CERU, amb=0.55, dif=0.5, spec=0.1), rgb)
        cv.over(rgb, cov(di) * region)
        # silver ring rosette
        lx, ly = lx0 - CC, ly0 - CC
        r = np.hypot(lx, ly)
        dr = r - 14.4
        mr = cov(dr) * region
        cv.shadow(mr, 1.0, 1.3, 1.2, 0.6)
        ring = np.abs(r - 13.2) - 1.2
        hr = 8.0 + 1.6 * np.sqrt(np.clip(1 - ((r - 13.2) / 1.2) ** 2, 0, 1))
        disc = r < 12.0
        # cerulean enamel disc
        hd = 7.0 + 0.5 * sstep(12.0, 10.7, r)
        alb_d = CERU + (CERU_D - CERU) * np.clip(r / 12.0 * 0.7, 0, 1)[..., None]
        rgb = np.where(disc[..., None], shade(hd, alb_d, amb=0.5, dif=0.55, spec=0.1), silver(hr))
        cv.over(rgb, mr * ((ring < 0) | disc))
        # silver wind curl swirling around the windstone (the sigil's spiral, closed into a vortex)
        arms = []
        for k in range(3):
            th_k = 2 * np.pi * k / 3 + 0.4
            pts = spiral((0.0, 0.0), 6.0, 10.6, th_k, -0.42, 40)
            w = 1.25 * np.sin(np.linspace(0.08, 1.0, len(pts)) * np.pi) ** 0.6 + 0.1
            arms.append((pts, w))
        sel = region & (r < 12.0)
        dsw = np.full(X.shape, 1e9, np.float32)
        acc = np.full(sel.sum(), 1e9, np.float32)
        for pts, w in arms:
            acc = np.minimum(acc, stroke_sdf(lx[sel], ly[sel], pts, w))
        dsw[sel] = acc
        msw = cov(dsw) * region
        halo = np.clip(blur(msw, 1.6 * K) * 1.4, 0, 1) * (1 - msw) * disc
        cv.over(np.zeros(X.shape + (3,), np.float32) + GLOW, 0.28 * halo * region)
        cv.shadow(msw, 0.5, 0.7, 0.6, 0.5)
        cv.over(silver(9.0 + 1.4 * np.sqrt(np.clip(-dsw / 1.1, 0, 1))), msw)
        # windstone in a silver bezel
        dbz = r - 6.4
        mbz = cov(dbz) * region
        cv.shadow(mbz, 0.6, 0.8, 0.8, 0.55)
        cv.over(silver(11.0 + np.minimum(-dbz, 1.4) * 1.1), mbz)
        dg = r - 4.9
        hg = 13.0 + 3.2 * np.sqrt(np.clip(1 - (r / 4.9) ** 2, 0, 1))
        cv.over(windstone(hg, sstep(0, 3.8, -dg)), cov(dg) * region)


# ------------------------------------------------------------------ assembly
def BORDER():
    cv = Canvas()
    band(cv)
    edge_mounts(cv)
    corners(cv)
    arr = np.array(cv.image())
    arr[S:N - S, S:N - S] = 0
    return Image.fromarray(arr, "RGBA")


# ------------------------------------------------------------------ crest
# The racial crest (Blizzard made none): a cerulean-enamel elven shield rimmed in silver, bearing the
# banner's wind sigil, whose curl winds as a vortex around a glowing windstone; a crown of two wind
# volutes and a feather spire above, and fanned silver hippogryph feathers spread as wings behind.
# Drawn at 550x700 (2x the 275:350 crest frame) with 2x supersampling; light from the top left.
CW, CH, CK = 550, 700, 2
CX = CW / 2


def _cblur(a, sigma):
    """Gaussian blur (sigma in grid px) via FFT."""
    pad = int(3 * sigma) + 2
    p = np.pad(a, pad)
    fy = np.fft.fftfreq(p.shape[0])[:, None]
    fx = np.fft.rfftfreq(p.shape[1])[None, :]
    f = np.exp(-2 * np.pi ** 2 * sigma ** 2 * (fx ** 2 + fy ** 2))
    return np.fft.irfft2(np.fft.rfft2(p) * f, s=p.shape)[pad:-pad, pad:-pad].astype(np.float32)


def _cnoise(seed, sigma):
    """Smooth unit-variance noise over the crest grid (sigma in canvas px)."""
    a = _cblur(np.random.default_rng(seed).standard_normal((CH * CK, CW * CK)).astype(np.float32), sigma * CK)
    return (a - a.mean()) / (a.std() + 1e-9)


def _clight(h):
    gy, gx = np.gradient(h * CK)
    n = np.stack([-gx, -gy, np.ones_like(h)], -1)
    n = n / np.linalg.norm(n, axis=-1, keepdims=True)
    return n, np.clip((n * LIGHT).sum(-1), 0, 1), np.clip((n * HALF).sum(-1), 0, 1)


def _cblur2(a, sx, sy):
    """Anisotropic Gaussian blur (sigmas in grid px) via FFT."""
    pad = int(3 * max(sx, sy)) + 2
    p = np.pad(a, pad)
    fy = np.fft.fftfreq(p.shape[0])[:, None]
    fx = np.fft.rfftfreq(p.shape[1])[None, :]
    f = np.exp(-2 * np.pi ** 2 * ((sx * fx) ** 2 + (sy * fy) ** 2))
    return np.fft.irfft2(np.fft.rfft2(p) * f, s=p.shape)[pad:-pad, pad:-pad].astype(np.float32)


_TX = {}


def _textures():
    """Shared surface textures: hammer dents, brushing, mottling, nicks."""
    if not _TX:
        rng = np.random.default_rng(29)
        b = _cblur2(rng.standard_normal((CH * CK, CW * CK)).astype(np.float32), 9 * CK, 0.5 * CK)
        _TX["brush"] = (b - b.mean()) / (b.std() + 1e-9)
        _TX["hammer"] = _cnoise(31, 2.6)
        _TX["mott"] = _cnoise(37, 9.0)
        fine = _cnoise(41, 0.7)
        _TX["nick"] = sstep(2.9, 3.4, fine)
    return _TX


_SV_LO = np.array([18, 21, 30], np.float32)
_SV_MID = np.array([100, 110, 128], np.float32)
_SV_HI = np.array([228, 236, 246], np.float32)


def _csilver(h, var=None, dim=1.0):
    """Hand-painted worn silver: a dark-to-light ramp, brushed and hammered, grime in the crevices,
    small nicks, and crisp glints only where a surface turns toward the top-left light."""
    tx = _textures()
    n, ndl, ndh = _clight(h + 0.11 * tx["hammer"])
    streak = np.exp(-(((n[..., 0] * 0.55 + n[..., 1] * 0.83) - 0.25) / 0.14) ** 2)
    v = 0.04 + 1.0 * ndl ** 1.7 - 0.18 * streak + 0.035 * tx["brush"] + 0.03 * tx["mott"]
    cav = np.clip((_cblur(h, 2.2 * CK) - h) / 1.2, 0, 1)
    v = v * (1 - 0.6 * cav) * (1 - 0.55 * tx["nick"])
    v = np.clip(v * dim, 0, 1)
    alb = np.where((v < 0.5)[..., None], _SV_LO + (_SV_MID - _SV_LO) * (v / 0.5)[..., None],
                   _SV_MID + (_SV_HI - _SV_MID) * ((v - 0.5) / 0.5)[..., None])
    facing = np.clip((-0.6 * n[..., 0] - 0.8 * n[..., 1]) * 4.0, 0, 1)
    spec = 0.75 * ndh ** 70 * facing * (1 - tx["nick"])
    return np.clip(alb + 255 * spec[..., None] * dim, 0, 255)


def _cseg(px, py, pts, w):
    d = np.full(px.shape, 1e9, np.float32)
    for i in range(len(pts) - 1):
        ax, ay = pts[i]
        bx, by = pts[i + 1]
        vx, vy = bx - ax, by - ay
        ll = vx * vx + vy * vy + 1e-9
        s = np.clip(((px - ax) * vx + (py - ay) * vy) / ll, 0, 1)
        dist = np.hypot(px - ax - s * vx, py - ay - s * vy)
        d = np.minimum(d, dist - (w[i] + (w[i + 1] - w[i]) * s))
    return d


def _ccov(d):
    """Anti-aliased coverage of d < 0 (d in canvas px)."""
    return np.clip(0.5 - d * CK, 0, 1).astype(np.float32)


class _CCanvas:
    def __init__(self):
        g = lambda n: (np.arange(n * CK, dtype=np.float32) + 0.5) / CK
        self.X, self.Y = np.meshgrid(g(CW), g(CH))
        self.rgb = np.zeros(self.X.shape + (3,), np.float32)
        self.a = np.zeros(self.X.shape, np.float32)

    def window(self, box):
        x0, y0, x1, y1 = (int(min(max(0, v * CK), lim)) for v, lim in
                          zip(box, (CW * CK, CH * CK, CW * CK, CH * CK)))
        return slice(y0, y1), slice(x0, x1)

    def field(self, f, box):
        """Evaluate a distance function only inside box=(x0, y0, x1, y1) (canvas px); 1e9 elsewhere."""
        sl = self.window(box)
        d = np.full(self.X.shape, 1e9, np.float32)
        d[sl] = f(self.X[sl], self.Y[sl])
        return d

    def over(self, rgb, a):
        da = self.a
        oa = a + da * (1 - a)
        self.rgb = (rgb * a[..., None] + self.rgb * (da * (1 - a))[..., None]) / np.maximum(oa, 1e-6)[..., None]
        self.a = oa

    def shadow(self, m, dx, dy, sig, op, onto=True, clip=None):
        """A soft cast shadow of mask m, offset down-right; by default it only falls on what is drawn."""
        sx, sy = int(dx * CK), int(dy * CK)
        sh = np.zeros_like(m)
        sh[sy:, sx:] = m[:m.shape[0] - sy, :m.shape[1] - sx]
        sh = np.clip(_cblur(sh, sig * CK), 0, 1) * op
        if onto:
            sh = sh * self.a
        if clip is not None:
            sh = sh * clip
        self.over(np.zeros(m.shape + (3,), np.float32) + 8, sh)

    def outline(self, d, w=2.4, col=(9, 12, 22)):
        self.over(np.zeros(d.shape + (3,), np.float32) + np.asarray(col, np.float32), _ccov(d - w))

    def glow(self, a, col=GLOW):
        """Additive-looking light: lighten toward col by a, without adding coverage."""
        self.rgb = self.rgb + (np.asarray(col, np.float32) - self.rgb) * np.clip(a, 0, 1)[..., None]

    def image(self):
        pm = np.concatenate([self.rgb * self.a[..., None], self.a[..., None]], -1)
        pm = pm.reshape(CH, CK, CW, CK, 4).mean((1, 3))
        a = pm[..., 3:4]
        rgb = np.where(a > 0, pm[..., :3] / np.maximum(a, 1e-6), 0)
        return Image.fromarray(np.clip(np.concatenate([rgb, a * 255], -1) + 0.5, 0, 255).astype(np.uint8), "RGBA")


# shield outline: a pointed elven arch on top, flared shoulders, sides sweeping to a point
SH_TOP, SH_SHOULDER, SH_TIP, SH_W = 168.0, 222.0, 640.0, 136.0
SH_RIM = 18.0
GEM_C = np.array([CX, 340.0])


def _shield_side(t):
    return SH_W * (1 - t ** 1.9) ** 0.7


def _shield_poly():
    side = []
    for t in np.linspace(0, 1, 44):                          # right side, shoulder to tip
        side.append((CX + _shield_side(t), SH_SHOULDER + (SH_TIP - SH_SHOULDER) * t))
    left = [(2 * CX - x, y) for x, y in side[::-1]]
    top = []
    for t in np.linspace(0, 1, 24):                          # top arch, left shoulder to right
        x = -SH_W + 2 * SH_W * t
        top.append((CX + x, SH_SHOULDER - (SH_SHOULDER - SH_TOP) * (1 - abs(x) / SH_W) ** 1.7))
    return np.array(left[:-1] + top[:-1] + side, np.float32)


def _poly_sdf(cv, poly):
    from PIL import ImageDraw
    x0, y0 = poly.min(0) - 8
    x1, y1 = poly.max(0) + 8
    seg = np.concatenate([poly, poly[:1]])
    d = cv.field(lambda px, py: _cseg(px, py, seg, np.zeros(len(seg))), (x0, y0, x1, y1))
    m = Image.new("L", (CW * CK, CH * CK))
    ImageDraw.Draw(m).polygon([(x * CK, y * CK) for x, y in poly], fill=255)
    return np.where(np.array(m) > 127, -d, d)


def _feather(cv, base, ang, L, W, bend, sg):
    """A hippogryph feather from its quill at base, pointing at ang (deg, 0 = up, clockwise), its tip
    curving upward. Returns (sdf, height, position along the feather)."""
    t = np.radians(ang)
    ux, uy = np.sin(t), -np.cos(t)
    span = L + W + 12
    sl = cv.window((base[0] - span, base[1] - span, base[0] + span, base[1] + span))
    px, py = cv.X[sl] - base[0], cv.Y[sl] - base[1]
    lx = px * ux + py * uy
    ly = (px * uy - py * ux) * sg                            # + on the leading (upper) side
    s = np.clip(lx / L, 0, 1)
    ly = ly - bend * L * s ** 2
    hw = W * 1.78 * s ** 0.35 * (1 - s) ** 0.5
    hw = np.where(ly > 0, hw * 0.62, hw)                     # narrow leading vane
    # soft ragged barb edges: the vane frays a little along each barb, and wavers
    saw = ((lx * 0.85 + 1.2 * np.abs(ly)) / 6.5) % 1.0
    hw = hw * (1 - 0.11 * saw * sstep(0.08, 0.3, s)) * (1 + 0.05 * np.sin(lx * 0.21 + 1.3 * sg))
    dv = np.maximum(np.abs(ly) - hw, np.maximum(-lx, lx - L))
    dq = np.maximum(np.abs(ly) - 2.6, np.maximum(-lx - 0.1 * L, lx - L))
    # two splits in the trailing vane, the way a real flight feather parts
    for k, at in ((0, 0.52), (1, 0.74)):
        nd = np.abs((lx - at * L) + 0.75 * ly) - 1.1
        dv = np.maximum(dv, -np.where(ly < -0.35 * hw, nd, 1e3))
    d = np.full(cv.X.shape, 1e9, np.float32)
    d[sl] = np.minimum(dv, dq)
    vane = 3.2 * np.sqrt(np.clip(1 - (ly / (hw + 1e-6)) ** 2, 0, 1))
    ridge = 2.6 * sstep(3.2, 0.5, np.abs(ly))
    barb = np.abs(((lx * 0.85 + 1.2 * np.abs(ly)) / 3.2) % 1.0 - 0.5)
    groove = 0.3 * sstep(0.2, 0.05, barb) * (np.abs(ly) > 3.4)
    groove = groove + 0.5 * np.abs(((lx * 0.85 + 1.2 * np.abs(ly)) / 6.5) % 1.0 - 0.5) * (np.abs(ly) > 3.4)
    h = np.zeros(cv.X.shape, np.float32)
    h[sl] = vane + ridge - groove
    pos = np.zeros(cv.X.shape, np.float32)
    pos[sl] = s
    return d, h, pos


def _crown(cv):
    """Two wind volutes rising from the shield's peak and curling outward, and a feather spire."""
    c = np.array([CX + 70.0, 116.0])
    lead = bezier(np.array([CX + 6.0, 196.0]), np.array([CX + 10.0, 130.0]),
                  np.array([CX + 32.0, 84.0]), c + np.array([0.0, -34.0]), 30)
    sp = spiral(c, 34.0, 12.0, -np.pi / 2, 0.92, 50)
    right = np.concatenate([lead, sp[1:]])
    w = np.concatenate([np.linspace(14.0, 11.0, len(lead)), np.linspace(11.0, 5.0, len(sp) - 1)])
    left = right * np.array([-1, 1]) + np.array([2 * CX, 0])
    dv = cv.field(lambda px, py: np.minimum(_cseg(px, py, right, w), _cseg(px, py, left, w)),
                  (CX - 130, 40, CX + 130, 220))

    def spire(px, py):
        s = np.clip((200 - py) / 152.0, 0, 1)
        hw = 23.0 * (1 - s) ** 0.9 * (0.5 + 0.5 * np.sin(np.pi * np.clip(s * 1.6, 0, 1)))
        return np.maximum(np.abs(px - CX) - hw, np.maximum(48 - py, py - 204))
    ds = cv.field(spire, (CX - 30, 40, CX + 30, 220))
    return dv, ds


def _tails(cv):
    """Two wind curls blowing out from behind the shield's lower sides, answering the crown."""
    c = np.array([CX + 106.0, 560.0])
    lead = bezier(np.array([CX + 60.0, 484.0]), np.array([CX + 96.0, 488.0]),
                  np.array([CX + 132.0, 520.0]), c + np.array([26.0, 0.0]), 30)
    sp = spiral(c, 26.0, 9.0, 0.0, 0.85, 40)
    right = np.concatenate([lead, sp[1:]])
    w = np.concatenate([np.linspace(12.0, 9.0, len(lead)), np.linspace(9.0, 4.0, len(sp) - 1)])
    left = right * np.array([-1, 1]) + np.array([2 * CX, 0])
    return cv.field(lambda px, py: np.minimum(_cseg(px, py, right, w), _cseg(px, py, left, w)),
                    (CX - 150, 460, CX + 150, 600))


def _sigil(cv, c):
    """The banner's wind sigil: a curl wound about the windstone that sweeps down in an S, and a tail."""
    cur = spiral(c, 39.0, 68.0, np.radians(150 + 300), -300 / 360, 60)
    p0 = cur[-1]
    s1 = bezier(p0, p0 + np.array([0.0, 62.0]), np.array([CX + 40.0, 400.0]), np.array([CX + 50.0, 470.0]), 30)
    s2 = bezier(s1[-1], np.array([CX + 58.0, 524.0]), np.array([CX + 26.0, 552.0]), np.array([CX - 2.0, 578.0]), 30)
    main = np.concatenate([cur, s1[1:], s2[1:]])
    n1, n2 = len(cur), len(s1) + len(s2) - 2
    wm = np.concatenate([np.linspace(7.0, 15.0, n1), 15.0 * (1 - np.linspace(0, 1, n2)) ** 0.8 + 0.6])
    tail = bezier(np.array([CX - 86.0, 446.0]), np.array([CX - 40.0, 456.0]),
                  np.array([CX + 2.0, 482.0]), np.array([CX - 12.0, 544.0]), 40)
    tt = np.linspace(0, 1, len(tail))
    wt = 11.0 * np.sin(np.clip(tt, 0.04, 1) * np.pi * 0.5) ** 0.35 * (1 - tt) ** 0.9 + 0.6
    return cv.field(lambda px, py: np.minimum(_cseg(px, py, main, wm), _cseg(px, py, tail, wt)),
                    (CX - 120, 250, CX + 120, 630))


def _dome(cv, cx, cy, r, hbase):
    rr = np.hypot(cv.X - cx, cv.Y - cy)
    return rr - r, hbase + r * 0.8 * np.sqrt(np.clip(1 - (rr / r) ** 2, 0, 1))


def _clasp(cv, cx, cy):
    """A small silver lozenge mount holding the wing to the shield, with a dark cerulean enamel boss."""
    dx, dy = cv.X - cx, cv.Y - cy
    d = np.abs(dx) / 0.62 + np.abs(dy) - 24.0
    h = 9.0 + np.minimum(-d, 6.0) * 0.55
    rr = np.hypot(dx, dy)
    h = h - 1.6 * sstep(1.2, 0.2, np.abs(rr - 8.5))          # engraved ring about the boss
    return d, h, rr


def CREST_ART():
    _TX.clear()
    tx = _textures()
    cv = _CCanvas()
    X_, Y_ = cv.X, cv.Y
    blank = np.zeros_like(cv.rgb)
    steel = np.array([0.5, 0.66, 0.86], np.float32)
    # --- a darker under-layer of feathers between and behind the silver ones, for depth
    under = [(132, 150, 27), (93, 182, 29), (56, 192, 29), (22, 170, 26)]
    for j, (ang, L, W) in enumerate(under):
        for sg in (-1, 1):
            d, h, pos = _feather(cv, (CX + sg * 46, 300), sg * ang, L, W, 0.12, sg)
            m = _ccov(d)
            cv.shadow(m, 3, 5, 4, 0.6)
            cv.outline(d, 2.0)
            rgb = _csilver(3.0 + h, dim=0.62) * steel
            cv.over(rgb, m)
    # --- silver feathers fanned as wings, lowest drawn first
    fan = [(112, 168, 31), (74, 186, 33), (38, 180, 31)]
    for j, (ang, L, W) in enumerate(fan):
        for sg in (-1, 1):
            d, h, pos = _feather(cv, (CX + sg * 52, 292), sg * ang, L, W, 0.12, sg)
            m = _ccov(d)
            cv.shadow(m, 3.5, 6, 5, 0.75)
            cv.outline(d, 1.8)
            rgb = _csilver(4.0 + h, dim=0.95 + 0.05 * j)
            tip = sstep(0.55, 0.95, pos)
            rgb = rgb + (rgb * steel - rgb) * (0.5 * tip)[..., None]
            rgb = rgb * (0.62 + 0.38 * sstep(0.0, 0.45, pos))[..., None]
            cv.over(rgb, m)
    # --- crown of wind volutes and the spire, and the lower wind curls
    for d in _crown(cv) + (_tails(cv),):
        m = _ccov(d)
        cv.shadow(m, 3.5, 6, 5, 0.75)
        cv.outline(d, 2.6)
        cv.over(_csilver(6.0 + 3.6 * np.sqrt(np.clip(-d / 6.5, 0, 1))), m)
    # --- the shield rim: engraved with two lines and a row of punched diamonds between them
    poly = _shield_poly()
    dsh = _poly_sdf(cv, poly)
    msh = _ccov(dsh)
    cv.shadow(msh, 4, 7, 7, 0.8)
    cv.outline(dsh, 3.2)
    inner = -dsh
    rim_h = 8.0 + 3.4 * np.sqrt(np.clip(np.minimum(inner, SH_RIM - inner) / (SH_RIM / 2), 0, 1))
    for at in (0.3, 0.74):
        rim_h = rim_h - 1.0 * sstep(1.0, 0.25, np.abs(inner - SH_RIM * at))
    th = np.arctan2(Y_ - 400.0, X_ - CX)
    ph = np.abs(((th / (2 * np.pi / 72)) % 1.0) - 0.5)
    rim_h = rim_h - 1.1 * sstep(0.22, 0.06, ph + 0.11 * np.abs(inner - SH_RIM * 0.52))
    cv.over(_csilver(rim_h), msh)
    # --- cerulean enamel: muted steel blue, mottled, crazed, worn where it meets the silver
    dfl = dsh + SH_RIM
    mfl = _ccov(dfl)
    cv.outline(dfl, 2.0, (10, 16, 26))
    nb, nm, nf = _cnoise(11, 16.0), _cnoise(13, 4.0), _cnoise(17, 1.1)
    gy = np.clip((Y_ - 200) / 440, 0, 1)
    gx = np.clip((X_ - (CX - 110)) / 220, 0, 1)
    k = 0.12 + 0.45 * gy + 0.22 * gx + 0.13 * nb + 0.08 * nm + 0.05 * nf
    k = k + 0.4 * sstep(26, 0, -dfl) * sstep(0.2, 0.8, gy * 0.6 + gx * 0.4)
    k = np.clip(k, 0, 1)[..., None]
    lite = np.array([58, 112, 150], np.float32)
    dark = np.array([9, 26, 46], np.float32)
    enamel = lite + (dark - lite) * k
    crack = sstep(0.07, 0.0, np.abs(_cnoise(21, 7.0))) + 0.7 * sstep(0.05, 0.0, np.abs(_cnoise(23, 3.5)))
    crack = np.clip(crack, 0, 1) * (0.3 + 0.7 * sstep(34, 2, -dfl))
    enamel = enamel * (1 - 0.45 * crack)[..., None]
    worn = sstep(7, 1.5, -dfl) * sstep(0.6, 1.4, _cnoise(25, 2.2))
    enamel = enamel + (np.array([70, 80, 96], np.float32) * (0.8 + 0.1 * nf)[..., None] - enamel) * worn[..., None]
    cv.over(enamel, mfl)
    cv.shadow(1 - mfl, 2.5, 3.5, 3, 0.7, clip=mfl)          # the rim's shadow on the enamel
    # inset silver line inside the rim
    dln = np.abs(-dfl - 9.0) - 1.7
    mln = _ccov(dln) * mfl
    cv.shadow(mln, 1.2, 1.8, 1.2, 0.6)
    cv.over(_csilver(5.0 + 1.6 * np.sqrt(np.clip(-dln / 1.7, 0, 1))), mln)
    # --- clasps where the wings meet the shield
    cl_d = np.full(X_.shape, 1e9, np.float32)
    cl_h = np.zeros(X_.shape, np.float32)
    cl_r = np.full(X_.shape, 1e9, np.float32)
    for sg in (-1, 1):
        d, h, rr = _clasp(cv, CX + sg * 133, 296)
        sel = d < cl_d
        cl_h, cl_r, cl_d = np.where(sel, h, cl_h), np.where(sel, rr, cl_r), np.minimum(cl_d, d)
    mcl = _ccov(cl_d)
    cv.shadow(mcl, 2.5, 4, 3, 0.75)
    cv.outline(cl_d, 2.2)
    cv.over(_csilver(cl_h), mcl)
    hb = 11.0 + 4.0 * np.sqrt(np.clip(1 - (cl_r / 6.0) ** 2, 0, 1))
    boss = shade(hb, np.zeros(X_.shape + (3,), np.float32) + np.array([40, 92, 132], np.float32),
                 amb=0.35, dif=0.7, spec=0.3)
    cv.over(np.clip(boss, 0, 255), _ccov(cl_r - 6.0) * mcl)
    # --- the sigil: raised silver
    c = GEM_C
    dsg = np.maximum(_sigil(cv, c), dfl + 4)
    msg = _ccov(dsg)
    cv.shadow(msg, 3, 4.5, 2.8, 0.8)
    cv.outline(dsg, 2.2, (8, 14, 26))
    cv.over(_csilver(6.0 + 3.0 * np.sqrt(np.clip(-dsg / 5.5, 0, 1))), msg)
    # --- the windstone in the curl's eye: the brightest point and the only glow
    r = np.hypot(X_ - c[0], Y_ - c[1])
    cv.glow(0.62 * np.clip(1 - (r - 27) / 44, 0, 1) ** 2.2 * (r > 27) * mfl)
    dbz = r - 32.0
    cv.shadow(_ccov(dbz), 2.5, 3.5, 2.5, 0.75)
    cv.outline(dbz, 2.2)
    cv.over(_csilver(10.0 + 2.4 * np.sqrt(np.clip(-dbz / 3.5, 0, 1))), _ccov(dbz))
    dg = r - 26.0
    cv.outline(dg, 1.6, (4, 20, 34))
    n, ndl, ndh = _clight(12.0 + 18.0 * np.sqrt(np.clip(1 - (r / 26.0) ** 2, 0, 1)))
    d_, m_, l_ = (np.asarray(v, np.float32) for v in WIND)
    inner_l = np.clip(1 - np.hypot(X_ - c[0] - 6, Y_ - c[1] - 7) / 23.0, 0, 1)
    base = d_ + (m_ - d_) * (0.3 + 0.5 * ndl + 0.06 * tx["mott"])[..., None]
    base = base + (l_ - base) * (0.88 * inner_l ** 1.3)[..., None]
    cv.over(np.clip(base + 255 * (0.95 * ndh ** 90)[..., None], 0, 255), _ccov(dg))
    # --- a heavy dark outline around the whole silhouette, a soft drop shadow and haze beneath
    out = _CCanvas()
    out.shadow(cv.a, 7, 12, 11, 0.85, onto=False)
    out.over(blank + 6, np.clip(_cblur(cv.a, 5 * CK) * 1.4, 0, 1) * 0.6)
    out.over(blank + np.array([6, 8, 14], np.float32), np.clip(_cblur(cv.a, 1.6 * CK) * 3.0, 0, 1))
    out.over(cv.rgb, cv.a)
    return out.image()
