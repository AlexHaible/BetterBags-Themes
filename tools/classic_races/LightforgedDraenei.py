"""Lightforged Draenei classic border: Vindicaar holy plate, polished gold over white enamel.

A slim band of plate armour: a faceted (ridged, two-plane) gold rail outside and inside, and
between them a strip of ivory-white enamel. Along the enamel run gold blade inlays that taper
from a small gold mount holding a pale-yellow light crystal (a faceted lozenge with a warm
glow), and between the crystals sits a gold chevron pointing at the window, like the
chevrons on the crest's helm. Each corner is a faceted gold shield-plate: a square back plate
under a four-facet gold diamond, an inset ivory enamel ring and a larger glowing light
crystal in the middle. Everything angular, no curves; light from the top left.
"""
import numpy as np
from PIL import Image

THEME = dict(
    Name="RacesLightforgedDraenei", Background="SOLID", BackgroundInset=8,
    Color=(0.07, 0.06, 0.045, 0.8), Slice=40, Outset=21, TitleY=42, Close={"X": 20, "Y": 20},
    Search=("TOPRIGHT", -22, -2), Menu={"X": -27, "Y": 27},
    TabEdge=(0.78, 0.6, 0.26, 1), TabAccent=(1.0, 0.93, 0.6, 1),
)

N = 256          # texture size
S = 40           # slice
SEG = N - 2 * S  # 176, the edge segment
P = 88           # edge pattern period (176 = 2 x 88)
K = 4            # supersampling
B0, B1 = 4.0, 25.0   # band from / to (distance from the texture's outer edge)

GOLD, IVORY, CRYSTAL, DARK, DGOLD = 1, 2, 3, 4, 5


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


def _ridge(d, a, b, base, peak):
    """A faceted rail: two flat planes meeting in a sharp ridge (a chamfered bar)."""
    m, hw = (a + b) / 2, (b - a) / 2
    return np.where((d >= a) & (d < b), base + (peak - base) * (1 - np.abs(d - m) / hw), -1)


def _band(t, d):
    """Height, material and glow of the edge band; t along the edge, d from the outer edge."""
    h = np.full(t.shape, -1.0)
    m = np.zeros(t.shape, np.int8)
    g = np.zeros(t.shape)
    inb = (d >= B0) & (d < B1)
    h[inb] = 0.0
    m[inb] = DARK
    for a, b, pk in ((B0 + 0.3, B0 + 5.0, 1.9), (B1 - 4.3, B1 - 0.3, 1.7)):
        r = _ridge(d, a, b, 0.5, pk)
        sel = r > 0
        h[sel] = r[sel]
        m[sel] = GOLD
    # ivory enamel strip, its long edges bevelled
    f0, f1 = B0 + 6.0, B1 - 5.3
    fr = (d >= f0) & (d < f1)
    bev = np.minimum(d - f0, f1 - d)
    h[fr] = 0.55 + 0.35 * np.clip(bev / 1.2, 0, 1)[fr]
    m[fr] = IVORY
    c = (f0 + f1) / 2
    v = d - c
    hv = (f1 - f0) / 2
    p = np.mod(t - 22, P)            # the slice lines fall mid-blade, between motifs
    u = p - P / 2                      # crystal at the middle of the period
    w = np.where(u < 0, u + P / 2, u - P / 2)   # chevron at the period boundary
    au = np.abs(u)
    # gold blade inlays: long thin wedges tapering from the crystal mount toward the chevrons
    blade_w = 1.7 * np.clip(1 - (au - 9) / 26, 0, 1)
    bl = fr & (au > 8) & (np.abs(v) < blade_w)
    h[bl] = (0.95 + 0.35 * (1 - np.abs(v) / np.maximum(blade_w, 1e-6)))[bl]
    m[bl] = GOLD
    # crystal mount: a stepped gold lozenge, faceted (pyramid)
    lz = au / 2.0 + np.abs(v)
    mount = fr & (lz <= hv + 0.4)
    h[mount] = (1.0 + 0.5 * np.clip(1 - lz / (hv + 0.4), 0, 1))[mount] + 0.0
    m[mount] = GOLD
    cr_r = hv - 1.6
    lzc = au / 2.2 + np.abs(v)
    seat = fr & (lzc <= cr_r + 0.6)
    h[seat] = 1.0
    m[seat] = DARK
    cry = fr & (lzc <= cr_r)
    h[cry] = (1.6 + 1.4 * (1 - lzc / cr_r))[cry]
    m[cry] = CRYSTAL
    g[cry] = (0.55 + 0.45 * (1 - lzc / cr_r))[cry]
    # soft holy light in the enamel around each crystal
    halo = fr & ~mount & ~bl
    g[halo] = np.maximum(g[halo], 0.5 * np.exp(-((au / 16.0) ** 2 + (v / 6.0) ** 2))[halo])
    # chevron pointing at the window (inner edge): a V of two blade strokes
    aw = np.abs(w)
    for off in (3.3, 0.0):             # a double chevron, apex toward the window
        vv = off + 1.2 - v
        k = np.abs(vv - aw * 1.0)
        chev = fr & (k < 1.0) & (aw < 4.6)
        h[chev] = (1.2 + 0.3 * (1 - k / 1.0))[chev]
        m[chev] = GOLD
    m[chev] = GOLD
    return h, m, g


def _corner(x, y):
    """Faceted gold shield-plate with a light crystal; x, y from the texture corner."""
    h = np.full(x.shape, -1.0)
    m = np.zeros(x.shape, np.int8)
    g = np.zeros(x.shape)
    # the plate: a square clipped to a blade point toward the window and chamfered outside,
    # raised as a roof of flat facets (height grows with the distance from its outline)
    lo, hi = 0.8, 36.5
    e = np.minimum.reduce([x - lo, y - lo, hi - x, hi - y,
                           (60.0 - x - y) / np.sqrt(2), (x + y - 7.0) / np.sqrt(2)])
    plate = e >= 0
    h[plate] = (0.8 + 2.4 * np.clip(e / 3.4, 0, 1))[plate]
    m[plate] = GOLD
    # engraved line inside the bevel
    eng = plate & (np.abs(e - 5.2) < 0.45)
    h[eng] -= 0.6
    m[eng] = DARK
    # white enamel diamond on the plateau, set in a dark seat
    cx = cy = 19.0
    dx, dy = x - cx, y - cy
    r1 = np.abs(dx) + np.abs(dy)
    seat = plate & (r1 <= 13.2)
    h[seat] = 3.0
    m[seat] = DARK
    ena = r1 <= 12.4
    h[ena] = (3.1 + 0.6 * np.clip((12.4 - r1) / 1.5, 0, 1))[ena]
    m[ena] = IVORY
    # a gold mount, then the light crystal: eight flat facets, pale yellow and glowing
    mount = r1 <= 8.2
    h[mount] = (3.9 + 1.0 * np.clip((8.2 - r1) / 1.6, 0, 1))[mount]
    m[mount] = GOLD
    oc = np.maximum(np.abs(dx), np.abs(dy)) * 0.55 + r1 * 0.45
    rc = 5.0
    cry = oc <= rc
    q = 1 - oc / rc
    h[cry] = (4.6 + 2.4 * q)[cry]
    m[cry] = CRYSTAL
    g[cry] = (0.6 + 0.4 * q)[cry]
    halo = ena & ~mount
    g[halo] = np.maximum(g[halo], 0.55 * np.clip(1 - (r1[halo] - 8.2) / 4.2, 0, 1))
    # three rivets on the bevel: outside corner and the two ends along the edges
    for rx, ry in ((6.2, 6.2), (32.4, 4.6), (4.6, 32.4)):
        rr = np.hypot(x - rx, y - ry)
        ring = plate & (rr < 2.3)
        m[ring & (rr >= 1.6)] = DARK
        dm = plate & (rr < 1.6)
        h[dm] = (3.6 + 1.3 * np.sqrt(np.clip(1 - (rr / 1.6) ** 2, 0, 1)))[dm]
        m[dm] = GOLD
    return h, m, g


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
    G = np.zeros((n, n))
    for d, t in ((Y, X - S), (N - Y, X - S), (X, Y - S), (N - X, Y - S)):
        h, m, g = _band(t, d)
        upd = h > H
        H[upd] = h[upd]
        M[upd] = m[upd]
        G[upd] = g[upd]
    for fx in (False, True):
        for fy in (False, True):
            xs = slice(n - S * K, n) if fx else slice(0, S * K)
            ys = slice(n - S * K, n) if fy else slice(0, S * K)
            lx = (N - X[ys, xs]) if fx else X[ys, xs]
            ly = (N - Y[ys, xs]) if fy else Y[ys, xs]
            h, m, g = _corner(lx, ly)
            sub_h, sub_m, sub_g = H[ys, xs], M[ys, xs], G[ys, xs]
            sel = h > -1
            sub_h[sel] = h[sel]
            sub_m[sel] = m[sel]
            sub_g[sel] = g[sel]
    alpha = (H > -1).astype(float)
    Hz = np.where(H < 0, 0, H)
    Hs = _blur(Hz, 0.55 * K)
    gy, gx = np.gradient(Hs * K * 1.4)
    nz = np.ones_like(gx)
    nrm = np.sqrt(gx * gx + gy * gy + nz * nz)
    L = np.array([-0.55, -0.6, 0.58])
    L = L / np.linalg.norm(L)
    lam = (-gx * L[0] - gy * L[1] + nz * L[2]) / nrm
    hvec = L + np.array([0, 0, 1.0])
    hvec /= np.linalg.norm(hvec)
    spec = np.clip((-gx * hvec[0] - gy * hvec[1] + nz * hvec[2]) / nrm, 0, 1) ** 30

    grain = _noise(n, n, 5, 6 * K)
    fine = _noise(n, n, 9, 1.5 * K)
    shade = np.clip(lam + 0.025 * grain + 0.02 * fine, 0, 1.2)
    rgb = np.zeros((n, n, 3))
    gold = _ramp([(0.0, (62, 36, 10)), (0.35, (150, 102, 32)), (0.6, (214, 166, 64)),
                  (0.8, (246, 212, 112)), (1.0, (255, 244, 186))], shade)
    gold += 255 * 0.4 * spec[..., None]
    dgold = _ramp([(0.0, (40, 24, 8)), (0.4, (110, 72, 24)), (0.7, (170, 124, 46)),
                   (1.0, (226, 186, 98))], shade)
    dgold += 255 * 0.25 * spec[..., None]
    ivory = _ramp([(0.0, (110, 98, 78)), (0.4, (198, 188, 164)), (0.7, (238, 232, 214)),
                   (1.0, (255, 252, 242))], shade)
    ivory *= (0.97 + 0.03 * grain[..., None])
    ivory += 255 * 0.15 * spec[..., None]
    cryst = _ramp([(0.0, (178, 150, 56)), (0.35, (226, 204, 104)), (0.7, (252, 240, 160)),
                   (1.0, (255, 254, 232))], shade)
    cryst += 255 * 0.5 * spec[..., None]
    dark = _ramp([(0.0, (18, 12, 5)), (1.0, (60, 42, 18))], shade)
    for mat, col in ((GOLD, gold), (DGOLD, dgold), (IVORY, ivory), (CRYSTAL, cryst), (DARK, dark)):
        sel = M == mat
        rgb[sel] = col[sel]
    occ = np.clip(_blur(Hz, 1.4 * K) - Hz, 0, 1)
    rgb *= (1 - 0.5 * occ)[..., None]
    # warm gold-white light
    glow = np.array([255, 236, 170.0])
    Gs = np.maximum(G, _blur(G, 1.2 * K) * 0.8)
    gk = np.where(M == CRYSTAL, 0.12, 0.45)
    rgb += glow * gk[..., None] * Gs[..., None] * (M != DARK)[..., None]
    rgba = np.dstack([np.clip(rgb, 0, 255), alpha * 255])
    img = rgba.reshape(N, K, N, K, 4)
    a = img[..., 3:4] / 255.0
    col = (img[..., :3] * a).sum(axis=(1, 3))
    asum = a.sum(axis=(1, 3))
    out = np.zeros((N, N, 4))
    out[..., :3] = np.where(asum > 0, col / np.maximum(asum, 1e-6), 0)
    out[..., 3] = asum[..., 0] / (K * K) * 255
    return out


def BORDER():
    a = _render()
    # every edge segment is an exact repeat of one period taken from its middle
    src = slice(S, S + P)
    for k in range(S, N - S, P):
        a[:S, k:k + P] = a[:S, src]
        a[N - S:, k:k + P] = a[N - S:, src]
        a[k:k + P, :S] = a[src, :S]
        a[k:k + P, N - S:] = a[src, N - S:]
    a[S:N - S, S:N - S] = 0
    return Image.fromarray(np.clip(a + 0.5, 0, 255).astype(np.uint8), "RGBA")
