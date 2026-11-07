"""Zandalari Troll classic border: Dazar'alor temple gold.

A slim band of polished gold: a rounded outer and inner rail framing a recessed turquoise
enamel frieze, with jade lozenges set in stepped gold mounts and small stepped ziggurat
blocks between them, joined by two thin gold bars. The corners are stepped gold ziggurat
blocks (three tiers, notched like temple terraces) holding a domed jade cabochon.
Light from the top left via a height map.
"""
import numpy as np
from PIL import Image

THEME = dict(
    Name="RacesZandalariTroll", Background="SOLID", BackgroundInset=8,
    Color=(0.02, 0.09, 0.08, 0.75), Slice=32, Outset=25, TitleY=42, Close={"X": 24, "Y": 24},
    Search=("TOPRIGHT", -22, -2), Menu={"X": -30, "Y": 30},
    TabEdge=(0.72, 0.55, 0.2, 1), TabAccent=(0.25, 0.75, 0.62, 1),
)

N = 256          # texture size
S = 32           # slice
P = 48           # edge pattern period (192 = 4 x 48)
K = 4            # supersampling
B0, B1 = 4.0, 27.0   # band from / to (distance from the texture's outer edge)

GOLD, JADE, ENAMEL, DARK = 1, 2, 3, 4


def _blur(a, sigma):
    r = int(sigma * 3) + 1
    x = np.arange(-r, r + 1)
    k = np.exp(-x * x / (2 * sigma * sigma))
    k /= k.sum()
    p = np.pad(a, r, mode="edge")
    out = np.zeros_like(p)
    for i in range(2 * r + 1):
        out[:, r:-r] += k[i] * p[:, i:i + a.shape[1]]
    out2 = np.zeros_like(out)
    for i in range(2 * r + 1):
        out2[r:-r, :] += k[i] * out[i:i + a.shape[0], :]
    return out2[r:-r, r:-r]


def _noise(h, w, seed, scale):
    rng = np.random.default_rng(seed)
    acc = np.zeros((h, w))
    for s, amp in ((scale, 1.0), (scale / 2, 0.5), (scale / 4, 0.25)):
        g = rng.standard_normal((max(2, int(h / s)), max(2, int(w / s))))
        im = Image.fromarray(g.astype(np.float32)).resize((w, h), Image.BICUBIC)
        acc += amp * np.asarray(im)
    return acc / 1.75


def _rail(d, a, b):
    m, hw = (a + b) / 2, (b - a) / 2
    q = np.clip(1 - ((d - m) / hw) ** 2, 0, 1)
    return np.where((d >= a) & (d < b), 0.6 + 0.9 * np.sqrt(q), -1)


def _band(t, d):
    """Height and material of the edge band, t along the edge, d from the outer edge."""
    h = np.full(t.shape, -1.0)
    m = np.zeros(t.shape, np.int8)
    inb = (d >= B0) & (d < B1)
    # outline groove / base
    h[inb] = 0.0
    m[inb] = DARK
    for a, b in ((B0 + 0.5, B0 + 4.5), (B1 - 4.5, B1 - 0.5)):
        r = _rail(d, a, b)
        sel = r > 0
        h[sel] = r[sel]
        m[sel] = GOLD
    # frieze
    f0, f1 = B0 + 5.5, B1 - 5.5
    fr = (d >= f0) & (d < f1)
    h[fr] = 0.25
    m[fr] = ENAMEL
    v = d - (f0 + f1) / 2
    hv = (f1 - f0) / 2
    p = np.mod(t - S, P)
    u = p - P / 2                       # gem mount at the centre of the period
    w = np.where(u < 0, u + P / 2, u - P / 2)  # small block at the period boundary
    # two thin bars
    for c in (-hv + 1.6, hv - 1.6):
        bar = fr & (np.abs(v - c) < 0.9)
        h[bar] = np.maximum(h[bar], 0.8 + 0.3 * np.sqrt(np.clip(1 - ((v[bar] - c) / 0.9) ** 2, 0, 1)))
        m[bar] = GOLD
    # stepped lozenge mount + jade gem
    lz = np.abs(u) / 1.5 + np.abs(v)
    for lim, ht in ((hv + 0.6, 0.9), (hv - 1.6, 1.25)):
        sel = fr & (lz <= lim)
        h[sel] = np.maximum(h[sel], ht)
        m[sel] = GOLD
    g = fr & (lz <= hv - 3.2)
    gr = np.clip(1 - (lz / (hv - 3.2)) ** 2, 0, 1)
    h[g] = 1.3 + 0.9 * np.sqrt(gr[g])
    m[g] = JADE
    # small stepped diamond (three terraces) between mounts
    for hw_, hh_, ht in ((3.8, 1.2, 0.55), (2.5, 2.4, 0.7), (1.2, 3.6, 0.85)):
        sel = fr & (np.abs(w) <= hw_) & (np.abs(v) <= hh_)
        h[sel] = np.maximum(h[sel], ht)
        m[sel] = GOLD
    return h, m


def _corner(x, y):
    """Stepped gold ziggurat block with a jade cabochon; x, y from the texture corner."""
    h = np.full(x.shape, -1.0)
    m = np.zeros(x.shape, np.int8)
    cx = cy = 15.5
    ax, ay = np.abs(x - cx), np.abs(y - cy)
    cheb = np.maximum(ax, ay)

    def notched(r, n):  # square of half-size r, its corners cut in two terrace steps of n
        cut = ((ax > r - n) & (ay > r - 2 * n)) | ((ax > r - 2 * n) & (ay > r - n))
        return (cheb <= r) & ~cut

    tiers = ((15.4, 2.6, 0.5, DARK), (14.6, 2.6, 1.0, GOLD), (11.6, 2.0, 1.15, DARK),
             (11.0, 2.0, 1.7, GOLD), (8.0, 1.5, 1.85, DARK), (7.4, 1.5, 2.35, GOLD))
    for r, n, ht, mat in tiers:
        sel = notched(r, n)
        h[sel] = ht
        m[sel] = mat
    rr = np.hypot(x - cx, y - cy)
    gem = rr <= 4.6
    h[gem] = 2.4 + 1.5 * np.sqrt(np.clip(1 - (rr[gem] / 4.6) ** 2, 0, 1))
    m[gem] = JADE
    return h, m


def _ramp(stops, v):
    xs = np.array([s[0] for s in stops])
    out = np.zeros(v.shape + (3,))
    for c in range(3):
        out[..., c] = np.interp(v, xs, [s[1][c] for s in stops])
    return out


def _render():
    n = N * K
    c = (np.arange(n) + 0.5) / K
    X, Y = np.meshgrid(c, c)
    H = np.full((n, n), -1.0)
    M = np.zeros((n, n), np.int8)
    # four edges: distance from each outer edge, position along it
    for d, t in ((Y, X), (N - Y, X), (X, Y), (N - X, Y)):
        h, m = _band(t, d)
        upd = h > H
        H[upd] = h[upd]
        M[upd] = m[upd]
    # corners
    for fx in (False, True):
        for fy in (False, True):
            xs = slice(n - S * K, n) if fx else slice(0, S * K)
            ys = slice(n - S * K, n) if fy else slice(0, S * K)
            lx = (N - X[ys, xs]) if fx else X[ys, xs]
            ly = (N - Y[ys, xs]) if fy else Y[ys, xs]
            h, m = _corner(lx, ly)
            sub_h, sub_m = H[ys, xs], M[ys, xs]
            sel = h > -1
            sub_h[sel] = h[sel]
            sub_m[sel] = m[sel]
    alpha = (H > -1).astype(float)
    Hs = _blur(np.where(H < 0, 0, H), 0.9 * K)
    gy, gx = np.gradient(Hs * K * 1.6)
    nz = np.ones_like(gx)
    nrm = np.sqrt(gx * gx + gy * gy + nz * nz)
    L = np.array([-0.55, -0.6, 0.58])
    L = L / np.linalg.norm(L)
    # gradient points uphill; a surface facing the light (top left) rises toward the light
    lam = (-gx * L[0] - gy * L[1] + nz * L[2]) / nrm
    hvec = L + np.array([0, 0, 1.0])
    hvec /= np.linalg.norm(hvec)
    spec = np.clip((-gx * hvec[0] - gy * hvec[1] + nz * hvec[2]) / nrm, 0, 1) ** 24

    grain = _noise(n, n, 5, 6 * K)
    fine = _noise(n, n, 9, 1.5 * K)
    shade = np.clip(lam + 0.03 * grain + 0.03 * fine, 0, 1.2)
    rgb = np.zeros((n, n, 3))
    gold = _ramp([(0.0, (60, 32, 8)), (0.35, (140, 92, 26)), (0.6, (205, 152, 52)),
                  (0.8, (240, 200, 96)), (1.0, (255, 236, 160))], shade)
    gold += 255 * 0.35 * spec[..., None]
    jade = _ramp([(0.0, (6, 40, 34)), (0.4, (22, 110, 88)), (0.7, (52, 175, 140)),
                  (1.0, (150, 240, 205))], shade)
    jade += 255 * 0.8 * spec[..., None]
    enam = _ramp([(0.0, (6, 30, 30)), (0.5, (16, 78, 74)), (1.0, (40, 125, 115))], shade * 0.9)
    enam *= (0.92 + 0.08 * grain[..., None])
    dark = _ramp([(0.0, (14, 8, 3)), (1.0, (52, 34, 14))], shade)
    for mat, col in ((GOLD, gold), (JADE, jade), (ENAMEL, enam), (DARK, dark)):
        sel = M == mat
        rgb[sel] = col[sel]
    # contact shadow where a lower surface meets a higher one (recesses darken)
    occ = np.clip(_blur(np.where(H < 0, 0, H), 1.6 * K) - np.where(H < 0, 0, H), 0, 1)
    rgb *= (1 - 0.55 * occ)[..., None]
    rgba = np.dstack([np.clip(rgb, 0, 255), alpha * 255])
    img = rgba.reshape(N, K, N, K, 4)
    # premultiplied downsample
    a = img[..., 3:4] / 255.0
    col = (img[..., :3] * a).sum(axis=(1, 3))
    asum = a.sum(axis=(1, 3))
    out = np.zeros((N, N, 4))
    out[..., :3] = np.where(asum > 0, col / np.maximum(asum, 1e-6), 0)
    out[..., 3] = asum[..., 0] / (K * K) * 255
    return out


def BORDER():
    a = _render()
    # make every edge segment an exact repeat of one period taken from its middle
    src = slice(S + P, S + 2 * P)
    for k in range(S, N - S, P):
        a[:S, k:k + P] = a[:S, src]
        a[N - S:, k:k + P] = a[N - S:, src]
        a[k:k + P, :S] = a[src, :S]
        a[k:k + P, N - S:] = a[src, N - S:]
    a[S:N - S, S:N - S] = 0
    return Image.fromarray(np.clip(a + 0.5, 0, 255).astype(np.uint8), "RGBA")
