"""Worgen classic border: Gilneas wrought-iron railing on slate, brass and a crimson rose.

The band is a Gilneas City railing seen face-on: a round black-iron top rail with spear-point
pickets rising through it (their points make the outer silhouette), a recessed slate panel
between the top rail and a lower iron rail, an iron ring hung between each pair of pickets,
and a thin tarnished-brass bead along the inner edge. The pickets come in pairs with a ring
between them, then a gap: a calm, Victorian rhythm (period 40, four per edge segment).
Each corner is an iron gate-post cap: a bevelled charcoal plate with an engraved line and four
small brass rivets, holding a brass-ringed slate dish with a crimson rose (the crest's roses).

Drawn as a height map + material maps at 3x, lit from the top left, then downsampled to 256.
"""
import numpy as np
from PIL import Image, ImageFilter

SIZE = 256
SS = 3                    # supersampling
SLICE = 48
SEG = SIZE - 2 * SLICE    # 160: the edge segment
PER = 40                  # edge motif period (divides SEG)

THEME = dict(
    Name="RacesWorgen", Background="SOLID", BackgroundInset=8,
    Color=(0.05, 0.055, 0.065, 0.8), Slice=SLICE, Outset=22, TitleY=24, Close={"X": 18, "Y": 18},
    Search=("TOPRIGHT", -22, -2), Menu={"X": -28, "Y": 28},
    TabEdge=(0.24, 0.25, 0.28, 1), TabAccent=(0.55, 0.1, 0.12, 1),
)

# albedo (0..1)
IRON = np.array([0.125, 0.130, 0.145])
SLATE = np.array([0.300, 0.320, 0.350])
BRASS = np.array([0.44, 0.35, 0.19])
CRIMSON = np.array([0.50, 0.055, 0.075])
CRIMSON_D = np.array([0.22, 0.02, 0.035])

# band layout (distance from the texture's outer edge)
TIP = 0.9          # spear tips
RAIL_T = 10.0      # top rail centre
RAIL_TR = 1.7
PANEL0, PANEL1 = 10.0, 21.0
RAIL_B = 19.6      # lower rail centre
RAIL_BR = 1.15
RING_D = (RAIL_T + RAIL_TR + RAIL_B - RAIL_BR) / 2
RING_R = (RAIL_B - RAIL_BR - RAIL_T - RAIL_TR) / 2 + 0.2
BEAD = 22.4        # brass bead centre
BEADR = 1.45
SHAFT = 0.95       # picket half width


def _smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def _noise(n, seed, sx, sy):
    rng = np.random.default_rng(seed)
    f = np.fft.fft2(rng.standard_normal((n, n)))
    ky = np.fft.fftfreq(n)[:, None]
    kx = np.fft.fftfreq(n)[None, :]
    f *= np.exp(-((kx * sx) ** 2 + (ky * sy) ** 2) * 20)
    r = np.real(np.fft.ifft2(f))
    return (r - r.mean()) / (r.std() + 1e-9)


def _cov(sd):
    """signed distance (1x px, negative inside) -> coverage"""
    return np.clip(0.5 - sd * SS, 0, 1)


class Maps:
    def __init__(self, n):
        self.h = np.zeros((n, n))
        self.alb = np.zeros((n, n, 3))
        self.spec = np.zeros((n, n))
        self.shin = np.full((n, n), 24.0)
        self.alpha = np.zeros((n, n))

    def put(self, m, h, alb, spec, shin, cov=None, maxh=False):
        """write material where mask m; h may be array; cov for alpha (defaults to m)."""
        if maxh:
            m = m & (h > self.h)
        self.h = np.where(m, h, self.h)
        alb = np.broadcast_to(alb, self.alb.shape) if np.ndim(alb) == 1 else alb
        self.alb = np.where(m[..., None], alb, self.alb)
        self.spec = np.where(m, spec, self.spec)
        self.shin = np.where(m, shin, self.shin)
        c = m.astype(float) if cov is None else cov
        self.alpha = np.maximum(self.alpha, c)


def _spear(x, d, tip, s=1.0):
    """Signed distance + midrib height for a spear point at along-offset x, tip at depth `tip`."""
    k = (d - tip) / s
    x = x / s
    w_head = 2.5 * np.clip(k / 4.8, 0, 1) ** 0.85
    w_neck = 2.5 + (0.8 - 2.5) * _smooth(4.8, 5.9, k)
    w = np.where(k < 4.8, w_head, w_neck)
    sd = np.maximum(np.abs(x) - w, -k)
    rib = 1 - np.abs(x) / np.maximum(w, 0.3)
    return sd * s, w * s, rib


def _paint():
    N = SIZE * SS
    idx = (np.arange(N) + 0.5) / SS
    X, Y = np.meshgrid(idx, idx)
    S = SLICE
    mp = Maps(N)

    stack = np.stack([Y, SIZE - Y, X, SIZE - X])
    side = np.argmin(stack, axis=0)
    d = np.min(stack, axis=0)
    t = np.where(side < 2, X - S, Y - S)
    tm = np.mod(t, PER)
    in_seg = (t >= 0) & (t < SEG)

    nP = SEG * SS
    ti = np.mod(np.floor(t * SS), nP).astype(int)
    di = np.mod(np.floor(d * SS), nP).astype(int)
    brushed = _noise(nP, 1, 6.0, 0.35)[di, ti]
    grain = _noise(nP, 2, 4.0, 0.7)[di, ti]
    blotch = _noise(nP, 3, 8.0, 8.0)[di, ti]

    iron = IRON * (1 + 0.05 * brushed + 0.06 * blotch)[..., None]

    # ---- slate panel (recessed)
    pan = (d > PANEL0 - 0.5) & (d < PANEL1 + 0.5)
    hpan = 0.8 + 0.06 * grain
    slate = SLATE * (1 + 0.05 * grain + 0.06 * blotch)[..., None] * (1 - 0.25 * _smooth(13.0, 11.0, d)
                                                                    - 0.2 * _smooth(17.5, 19.0, d))[..., None]
    mp.put(pan, hpan, slate, 0.08, 10.0, cov=np.clip(np.minimum(d - PANEL0 + 0.5, PANEL1 + 0.5 - d) * SS, 0, 1))

    # ---- iron rings between paired pickets (centre tm = 20)
    rr = np.sqrt((tm - 20) ** 2 + (d - RING_D) ** 2)
    ringd = np.abs(rr - (RING_R - 0.7)) - 0.75
    m = in_seg & (ringd < 0.5 / SS)
    hring = 1.6 + 1.0 * np.sqrt(np.clip(1 - (ringd / 0.75 + 1) ** 2, 0, 1))
    mp.put(m, hring, iron, 0.8, 30.0)

    # ---- lower iron rail
    pd = np.abs(d - RAIL_B)
    m = pd < RAIL_BR
    mp.put(m, 1.6 + np.sqrt(np.clip(RAIL_BR ** 2 - pd ** 2, 0, None)) * 1.2, iron, 0.55, 30.0, maxh=True)

    # ---- pickets: shafts + spear points, at tm 10 and 30 (in the segment), plus one in each corner
    def picket(x, dd, ok):
        sd, w, rib = _spear(x, dd, TIP)
        head = ok & (sd < 0.5 / SS) & (dd < TIP + 6.8)
        hh = 2.2 + 1.6 * rib + 0.6 * _smooth(TIP, TIP + 3, dd)
        mp.put(head, hh, iron, 0.75, 34.0, cov=np.where(ok & (dd < TIP + 6.8), _cov(sd), 0))
        sh = ok & (np.abs(x) < SHAFT) & (dd >= TIP + 6.8) & (dd < RAIL_B)
        hs = 2.2 + 1.0 * np.sqrt(np.clip(1 - (x / SHAFT) ** 2, 0, 1))
        mp.put(sh, hs, iron, 0.6, 30.0, maxh=True)
        # small collar knob just under the point
        kd = np.sqrt((x / 1.45) ** 2 + ((dd - (TIP + 6.9)) / 0.9) ** 2)
        kn = ok & (kd < 1)
        mp.put(kn, 3.0 + 0.8 * np.sqrt(np.clip(1 - kd ** 2, 0, 1)), iron, 0.8, 36.0,
               cov=np.where(ok, np.clip((1 - kd) * 1.2 * SS, 0, 1), 0), maxh=True)

    for pc in (10.0, 30.0):
        picket(tm - pc, d, in_seg & (np.abs(tm - pc) < 4))

    # corner pickets (mirrored coordinates, along each edge out of the post)
    cu = np.where(X < SIZE / 2, X, SIZE - X)
    cv = np.where(Y < SIZE / 2, Y, SIZE - Y)
    corner = (cu < S) & (cv < S)
    CP = 39.0
    for along, across in ((cu, cv), (cv, cu)):
        picket(along - CP, across, corner & (np.abs(along - CP) < 4) & (across < 26))

    # ---- top rail (over the shafts)
    pd = np.abs(d - RAIL_T)
    m = pd < RAIL_TR
    mp.put(m, 2.6 + 1.3 * np.sqrt(np.clip(RAIL_TR ** 2 - pd ** 2, 0, None)), iron, 0.6, 30.0,
           cov=np.clip((RAIL_TR - pd) * SS + 0.5, 0, 1))

    # ---- brass bead along the inner edge
    pd = np.abs(d - BEAD)
    m = pd < BEADR
    brass = BRASS * (1 + 0.06 * brushed + 0.10 * blotch)[..., None]
    mp.put(m, 1.4 + 1.1 * np.sqrt(np.clip(BEADR ** 2 - pd ** 2, 0, None)), brass, 0.7, 34.0,
           cov=np.clip((BEADR - pd) * SS + 0.5, 0, 1))

    # ---- corner: iron gate-post cap
    bn = _noise(nP, 4, 4.0, 4.0)[np.floor(cv * SS).astype(int) % nP, np.floor(cu * SS).astype(int) % nP]
    # spear finial on the post, pointing diagonally out of the corner
    xr = (cu - cv) / np.sqrt(2)
    dr = (cu + cv) / np.sqrt(2)
    sd_f, w_f, rib_f = _spear(xr, dr, 0.6, 1.6)
    fin = corner & (dr < 12) & (sd_f < 0.5 / SS)
    mp.put(fin, 4.0 + 1.6 * rib_f + 0.6 * _smooth(0.6, 5.0, dr), iron, 0.8, 34.0,
           cov=np.where(corner & (dr < 12), _cov(sd_f), 0))
    P0, P1 = 5.5, 31.0
    pc_ = (P0 + P1) / 2
    hw = (P1 - P0) / 2
    sd = np.maximum(np.abs(cu - pc_), np.abs(cv - pc_)) - hw
    # chamfer the four corners a little
    sd = np.maximum(sd, (np.abs(cu - pc_) + np.abs(cv - pc_) - 2 * hw + 3.2) / np.sqrt(2))
    cp = corner & (sd < 0.5 / SS)
    hpl = 4.6 + 1.8 * _smooth(0, 2.4, -sd)
    engr = np.abs(sd + 2.3) < 0.4
    hpl = np.where(engr, hpl - 0.55, hpl)
    plate = IRON * 1.12 * ((1 + 0.05 * bn + 0.04 * brushed) * (1 - 0.25 * _smooth(-4, 0, sd))
                           * np.where(engr, 0.55, 1))[..., None]
    mp.h = np.where(cp, hpl, mp.h)
    mp.alb = np.where(cp[..., None], plate, mp.alb)
    mp.spec = np.where(cp, 0.6, mp.spec)
    mp.shin = np.where(cp, 30.0, mp.shin)
    mp.alpha = np.where(corner, np.maximum(mp.alpha, _cov(sd)), mp.alpha)

    # brass rivets in the plate corners
    for ru, rv in ((10.2, 10.2), (26.3, 10.2), (10.2, 26.3), (26.3, 26.3)):
        r2 = ((cu - ru) ** 2 + (cv - rv) ** 2) / 1.35 ** 2
        m = corner & (r2 < 1)
        ring = corner & (r2 >= 1) & (r2 < 1.9)
        mp.alb = np.where(ring[..., None], mp.alb * 0.6, mp.alb)
        mp.put(m, 6.4 + 1.1 * np.sqrt(np.clip(1 - r2, 0, 1)), BRASS * 1.05, 0.9, 44.0, cov=np.zeros_like(cu))

    # brass ring + slate dish
    r = np.sqrt((cu - pc_) ** 2 + (cv - pc_) ** 2)
    shadow_ring = corner & (r >= 9.3) & (r < 10.2)
    mp.alb = np.where(shadow_ring[..., None], mp.alb * 0.6, mp.alb)
    br = corner & (r < 9.3)
    mp.put(br, 6.6 + 1.0 * np.sqrt(np.clip(1 - ((r - 8.4) / 0.95) ** 2, 0, 1)),
           BRASS * (1 + 0.08 * bn)[..., None], 0.85, 40.0, cov=np.zeros_like(cu))
    dish = corner & (r < 7.45)
    mp.put(dish, 5.6 + 0.3 * (r / 7.45) ** 2, SLATE * 0.55, 0.1, 10.0, cov=np.zeros_like(cu))

    # crimson rose: four layers of five cupped petals, each turned, then a bud
    th = np.arctan2(cv - pc_, cu - pc_)
    rose_h = np.full(cu.shape, -1.0)
    rose_t = np.zeros_like(cu)       # 0 = outer petal edge .. 1 = heart, for colour
    for i, (R, rot, base) in enumerate(((6.9, 0.0, 6.0), (5.1, 0.63, 7.0), (3.4, 0.2, 7.9), (1.9, 0.9, 8.6))):
        lobe = R * (0.80 + 0.20 * np.abs(np.cos(2.5 * (th - rot))))
        inside = corner & (r < lobe)
        k = np.clip(r / lobe, 0, 1)
        hh = base + 1.1 * k ** 2.2                 # cupped: the petal rim stands up
        mm = inside & (hh > rose_h)
        rose_h = np.where(mm, hh, rose_h)
        rose_t = np.where(mm, 0.25 * i / 3.0 + 0.75 * (1 - k) ** 1.5, rose_t)
    bud = corner & (r < 0.95)
    rose_h = np.where(bud, 9.4 + 0.5 * np.sqrt(np.clip(1 - (r / 0.95) ** 2, 0, 1)), rose_h)
    rose_t = np.where(bud, 1.0, rose_t)
    m = rose_h > 0
    col = CRIMSON * 1.15 + (CRIMSON_D - CRIMSON * 1.15) * rose_t[..., None]
    col = col * (1 + 0.05 * bn)[..., None]
    mp.put(m, rose_h, col, 0.35, 18.0, cov=np.zeros_like(cu))

    return mp


def _light(mp):
    h, alb, spec, shin = mp.h, mp.alb, mp.spec, mp.shin
    gy, gx = np.gradient(h * SS)
    nx, ny, nz = -gx, -gy, np.ones_like(h)
    n = np.sqrt(nx * nx + ny * ny + nz * nz)
    nx, ny, nz = nx / n, ny / n, nz / n
    L = np.array([-1.0, -1.0, 1.2])
    L /= np.linalg.norm(L)
    ndl = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1)
    Hv = L + np.array([0, 0, 1.0])
    Hv /= np.linalg.norm(Hv)
    ndh = np.clip(nx * Hv[0] + ny * Hv[1] + nz * Hv[2], 0, 1)

    N = h.shape[0]
    pad = 12
    hp = np.pad(h, pad, mode="edge")
    shadow = np.zeros_like(h)
    for s in range(1, 3 * SS):
        sh = hp[pad - s:pad - s + N, pad - s:pad - s + N]
        shadow = np.maximum(shadow, np.clip((sh - h - 0.3 * s / SS * 2) / 1.2, 0, 1))
    shade = 0.30 + 0.85 * ndl / L[2]
    shade *= 1 - 0.5 * shadow
    moon = np.array([0.86, 0.90, 1.0])        # cool moonlight on the highlights
    col = alb * shade[..., None] + (spec * ndh ** shin)[..., None] * 0.85 * moon
    return np.clip(col, 0, 1)


def BORDER():
    mp = _paint()
    col = _light(mp)
    alpha = np.clip(mp.alpha, 0, 1)
    ai = Image.fromarray((alpha * 255).astype(np.uint8))
    ring = np.asarray(ai.filter(ImageFilter.MaxFilter(3)), dtype=np.float64) / 255
    a = np.maximum(alpha, ring)
    col = col * (alpha / np.maximum(a, 1e-6))[..., None] + np.array([0.02, 0.02, 0.025]) * ((a - alpha) / np.maximum(a, 1e-6))[..., None]
    sh = np.zeros_like(a)
    o = 2 * SS
    sh[o:, o:] = a[:-o, :-o]
    sha = np.asarray(Image.fromarray((sh * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2 * SS)),
                     dtype=np.float64) / 255 * 0.5
    out_a = a + sha * (1 - a)
    out_rgb = col * (a / np.maximum(out_a, 1e-6))[..., None]
    rgba = np.dstack([out_rgb * out_a[..., None], out_a])
    rgba = rgba.reshape(SIZE, SS, SIZE, SS, 4).mean(axis=(1, 3))
    A = rgba[..., 3:4]
    rgb = np.where(A > 1e-6, rgba[..., :3] / np.maximum(A, 1e-6), 0)
    img = np.clip(np.dstack([rgb, A]) * 255 + 0.5, 0, 255)
    img[SLICE:SIZE - SLICE, SLICE:SIZE - SLICE] = 0          # the centre must be fully transparent
    return Image.fromarray(img.astype(np.uint8), "RGBA")
