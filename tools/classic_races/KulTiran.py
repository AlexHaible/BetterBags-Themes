"""Kul Tiran classic border: Boralus ship's timber, a laid rope trim and brass compass-rose corners.

The band, outside in: a round brass capping rod; two strakes of polished dark teak planking
(grain running along the band, a caulked seam between them, staggered butt joints with brass
nail heads); a rounded moulding painted Proudmoore teal-green; then a thick three-strand rope
laid flat along the inner edge, held by a brass clamp once per segment.
Each corner is a sea-chest brass corner cap (bevelled, engraved, three rivets) carrying a brass
compass medallion: a teal enamel field with a gold eight-point compass star (the crest's green
shield and gold anchor in naval-instrument form).

Drawn as a height map + material maps at 3x, lit from the top left, then downsampled to 256.
Everything along an edge repeats every 80 texels (half the 160-texel edge segment), except the
rope clamp, which sits once per segment.
"""
import numpy as np
from PIL import Image, ImageFilter

SIZE = 256
SS = 3                    # supersampling
SLICE = 48
SEG = SIZE - 2 * SLICE    # 160: the edge segment
PER = 80                  # edge motif period (divides SEG)

THEME = dict(
    Name="RacesKulTiran", Background="SOLID", BackgroundInset=8,
    Color=(0.02, 0.06, 0.065, 0.82), Slice=SLICE, Outset=22, TitleY=28, Close={"X": 18, "Y": 18},
    Search=("TOPRIGHT", -22, -2), Menu={"X": -28, "Y": 28},
    TabEdge=(0.28, 0.16, 0.08, 1), TabAccent=(0.82, 0.62, 0.24, 1),
)

# albedo (0..1)
TEAK = np.array([0.215, 0.115, 0.058])
TEAK_D = np.array([0.10, 0.050, 0.025])
BRASS = np.array([0.66, 0.49, 0.20])
BRASS_OLD = np.array([0.40, 0.28, 0.12])   # darker, aged bronze for the corner cap
GOLD = np.array([0.88, 0.68, 0.26])
TEAL = np.array([0.06, 0.33, 0.29])
TEAL_D = np.array([0.03, 0.18, 0.16])
ROPE = np.array([0.58, 0.45, 0.27])

# band layout (distance from the texture's outer edge)
ROD, RODR = 2.0, 1.75        # brass capping rod centre / radius
PL0, PLM, PL1 = 3.4, 9.6, 15.6  # planking: outer edge, caulked seam, inner edge
MOUL, MOULR = 17.0, 1.6      # teal moulding
ROPEC, ROPER = 22.4, 4.4     # rope centre / radius
LAY = PER / 10               # rope strand pitch along the band (divides PER)
SLANT = 0.85                 # strand slant (times the rope radius, through the cylinder)


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
        if maxh:
            m = m & (h > self.h)
        self.h = np.where(m, h, self.h)
        alb = np.broadcast_to(alb, self.alb.shape) if np.ndim(alb) == 1 else alb
        self.alb = np.where(m[..., None], alb, self.alb)
        self.spec = np.where(m, spec, self.spec)
        self.shin = np.where(m, shin, self.shin)
        c = m.astype(float) if cov is None else cov
        self.alpha = np.maximum(self.alpha, c)


def _rod(d, c, r):
    """height profile of a round rod of radius r centred at depth c (nan-free, 0 outside)"""
    q = np.clip(1 - ((d - c) / r) ** 2, 0, 1)
    return np.sqrt(q)


def _paint():
    N = SIZE * SS
    idx = (np.arange(N) + 0.5) / SS
    X, Y = np.meshgrid(idx, idx)
    S = SLICE
    mp = Maps(N)

    stack = np.stack([Y, SIZE - Y, X, SIZE - X])
    side = np.argmin(stack, axis=0)
    d = np.min(stack, axis=0)
    horiz = side < 2
    t = np.where(horiz, X - S, Y - S)
    tm = np.mod(t, PER)
    in_seg = (t >= 0) & (t < SEG)

    nP = SEG * SS
    ti = np.mod(np.floor(t * SS), nP).astype(int)
    di = np.mod(np.floor(d * SS), nP).astype(int)
    grain = _noise(nP, 1, 9.0, 0.30)[di, ti]      # long streaks along the band
    warp = _noise(nP, 2, 7.0, 3.0)[di, ti]        # bends the grain lines
    blotch = _noise(nP, 3, 8.0, 8.0)[di, ti]
    fib = _noise(nP, 4, 0.35, 0.35)[di, ti]       # fine fibre noise
    brushed = _noise(nP, 5, 5.0, 0.4)[di, ti]

    # ---- teak planking: two strakes, caulked seam, staggered butt joints
    pl = (d > PL0 - 0.6) & (d < PL1 + 0.6)
    upper = d < PLM
    lines = 0.5 + 0.5 * np.sin((d + 2.6 * warp + 0.8 * blotch) * 1.45 + np.where(upper, 0.0, 1.7))
    wood = TEAK * (1 + 0.12 * grain + 0.08 * blotch)[..., None]
    wood = wood * (1 - 0.18 * lines ** 3)[..., None]
    # each plank is a slightly different board: shift tone by which board we are on
    jt_u = np.mod(t - 60, PER)                     # upper joints at tm = 60
    jt_l = np.mod(t - 20, PER)                     # lower joints at tm = 20
    jt = np.where(upper, jt_u, jt_l)
    board = np.mod(np.where(upper, np.floor((t - 60) / PER), np.floor((t - 20) / PER) + 1), 2)
    tone = 1 + 0.06 * (board - 0.5)            # two boards per strake per segment
    wood = wood * tone[..., None]
    # edges of each strake bevelled and darkened
    lo = np.where(upper, PL0, PLM)
    hi = np.where(upper, PLM, PL1)
    edge_in = np.minimum(d - lo, hi - d)
    jd = np.minimum(jt, PER - jt)                  # distance to the nearest butt joint
    bev = np.minimum(edge_in, jd)
    hpl = 2.0 + 0.9 * _smooth(-0.2, 1.3, bev) + 0.05 * grain
    wood = wood * (0.72 + 0.28 * _smooth(-0.2, 1.1, bev))[..., None]
    seamline = (np.abs(d - PLM) < 0.45) | (jd < 0.4)
    wood = np.where(seamline[..., None], TEAK_D * 0.45, wood)
    hpl = np.where(seamline, 1.4, hpl)
    mp.put(pl, hpl, wood, 0.42, 55.0, cov=_cov(np.maximum(PL0 - 0.6 - d, d - PL1 - 0.6)))

    # brass nail heads either side of each butt joint
    for jc, dc in ((60.0, (PL0 + PLM) / 2), (20.0, (PLM + PL1) / 2)):
        for off in (-2.4, 2.4):
            rr = np.sqrt((np.mod(t - jc - off + PER / 2, PER) - PER / 2) ** 2 + (d - dc) ** 2)
            m = rr < 1.05
            mp.put(m, 3.1 + 0.6 * np.sqrt(np.clip(1 - (rr / 1.05) ** 2, 0, 1)), BRASS * 1.05, 0.9, 40.0)

    # ---- brass capping rod on the outside
    m = np.abs(d - ROD) < RODR
    hb = 2.2 + 1.6 * _rod(d, ROD, RODR)
    brass = BRASS * (1 + 0.06 * brushed + 0.05 * blotch)[..., None]
    mp.put(m, hb, brass, 0.85, 38.0, cov=_cov(np.abs(d - ROD) - RODR), maxh=False)

    # ---- teal-painted moulding
    m = np.abs(d - MOUL) < MOULR
    hm = 2.3 + 1.1 * _rod(d, MOUL, MOULR)
    teal = TEAL * (1 + 0.08 * blotch + 0.04 * grain)[..., None]
    mp.put(m, hm, teal, 0.45, 30.0, cov=_cov(np.abs(d - MOUL) - MOULR))

    # ---- the rope: three-strand, laid along the band
    rd = d - ROPEC
    m = np.abs(rd) < ROPER
    cyl = _rod(d, ROPEC, ROPER)
    # across-rope coordinate in screen terms, so the lay keeps one direction around the frame;
    # arcsin projects the helix onto the cylinder, curving the strands near the rope's sides
    g = rd * np.where((side == 0) | (side == 2), 1.0, -1.0)
    geo = ROPER * np.arcsin(np.clip(g / ROPER, -1, 1)) * 1.25
    sgn = np.where(horiz, 1.0, -1.0)
    s = np.mod((t + sgn * SLANT * geo) / LAY, 1.0)
    strand = np.sqrt(np.clip(1 - (2 * s - 1) ** 2, 0, 1))       # each strand a rounded ridge
    groove = 1 - strand
    hr = 1.8 + 2.0 * cyl + 2.2 * strand * np.sqrt(cyl)
    twist = np.mod((t + sgn * SLANT * geo) * 3 / LAY, 1.0)  # fibre twist inside each strand
    fibre = 0.5 + 0.5 * np.sin(twist * 2 * np.pi)
    rope = ROPE * (1 + 0.07 * fib + 0.06 * blotch - 0.025 * fibre)[..., None]
    rope = rope * (1 - 0.6 * groove ** 1.3)[..., None]
    rope = rope * (0.75 + 0.25 * cyl)[..., None]
    mp.put(m, hr, rope, 0.06, 10.0, cov=_cov(np.abs(rd) - ROPER), maxh=False)

    # brass clamp over the rope, once per segment
    cd = np.abs(np.mod(t - 80 + PER / 2, SEG) - PER / 2)
    m = in_seg & (cd < 2.3) & (np.abs(rd) < ROPER + 0.9)
    hcl = 2.4 + 3.6 * _rod(d, ROPEC, ROPER + 0.9) + 0.5 * _smooth(2.3, 1.3, cd)
    mp.put(m, hcl, BRASS * (1 + 0.05 * brushed)[..., None], 0.9, 40.0,
           cov=_cov(np.maximum(cd - 2.3, np.abs(rd) - ROPER - 0.9)))
    m = in_seg & (cd < 2.3) & (np.abs(rd) < ROPER + 0.9) & (np.abs(cd) < 0.35)
    mp.alb = np.where(m[..., None], mp.alb * 0.7, mp.alb)

    # ---- corners (top-left design, mirrored; lighting afterwards stays top-left)
    cu = np.where(X < SIZE / 2, X, SIZE - X)
    cv = np.where(Y < SIZE / 2, Y, SIZE - Y)
    corner = (cu < S) & (cv < S)
    bn = _noise(nP, 6, 5.0, 5.0)[np.floor(cv * SS).astype(int) % nP, np.floor(cu * SS).astype(int) % nP]

    # sea-chest brass corner cap: rounded square
    CAP, CR = 34.0, 5.0
    qx, qy = cu - CAP / 2, cv - CAP / 2
    ax, ay = np.abs(qx) - (CAP / 2 - CR - 0.6), np.abs(qy) - (CAP / 2 - CR - 0.6)
    sd = np.sqrt(np.maximum(ax, 0) ** 2 + np.maximum(ay, 0) ** 2) + np.minimum(np.maximum(ax, ay), 0) - CR
    cap = corner & (sd < 0.5 / SS)
    hc = 5.0 + 1.6 * _smooth(0, 2.0, -sd)
    engr = np.abs(sd + 3.4) < 0.4
    hc = np.where(engr, hc - 0.5, hc)
    capc = BRASS_OLD * ((1 + 0.07 * bn + 0.05 * brushed) * (1 - 0.25 * _smooth(-4, 0, sd))
                        * np.where(engr, 0.6, 1))[..., None]
    mp.put(cap, hc, capc, 0.8, 36.0, cov=np.where(corner, _cov(sd), 0))

    for (ru, rv, R) in ((4.6, 4.6, 1.9), (30.4, 4.4, 1.7), (4.4, 30.4, 1.7)):
        rr = np.sqrt((cu - ru) ** 2 + (cv - rv) ** 2)
        ring = corner & (rr >= R) & (rr < R + 0.8)
        mp.alb = np.where(ring[..., None], mp.alb * 0.6, mp.alb)
        m = corner & (rr < R)
        mp.put(m, 6.8 + 1.2 * np.sqrt(np.clip(1 - (rr / R) ** 2, 0, 1)), BRASS * 1.1, 0.95, 44.0)

    # compass medallion
    MC, MR, ER = 20.0, 15.6, 12.0
    du, dv = cu - MC, cv - MC
    rr = np.sqrt(du * du + dv * dv)
    shadow_ring = corner & (rr >= MR) & (rr < MR + 1.2) & cap
    mp.alb = np.where(shadow_ring[..., None], mp.alb * 0.6, mp.alb)
    ringm = corner & (rr < MR) & (rr >= ER)
    prof = np.sin(np.clip((rr - ER) / (MR - ER), 0, 1) * np.pi)
    hring = 7.4 + 1.6 * prof
    ang = np.arctan2(dv, du)
    ticks = (np.abs(np.mod(ang * 16 / (2 * np.pi) + 0.5, 1.0) - 0.5) < 0.09) & (np.abs(rr - (ER + 1.7)) < 1.0)
    hring = np.where(ticks, hring - 0.5, hring)
    ringc = BRASS * ((1 + 0.06 * bn + 0.04 * brushed) * np.where(ticks, 0.55, 1))[..., None]
    mp.put(ringm, hring, ringc, 0.95, 44.0, cov=np.where(corner, _cov(rr - MR), 0))

    field = corner & (rr < ER)
    tealf = TEAL * (1 + 0.06 * bn)[..., None] * (0.85 + 0.15 * _smooth(ER, ER - 3, rr))[..., None]
    tealf = tealf + (TEAL_D - TEAL) * _smooth(ER - 1.5, ER, rr)[..., None]
    mp.put(field, 6.6 + 0.0 * rr, tealf, 0.55, 50.0)

    # gold eight-point compass star: each point a ridged triangle
    starh = np.full(cu.shape, -1.0)
    for k in range(8):
        th = k * np.pi / 4
        major = k % 2 == 0
        L, w0, top = (10.6, 2.9, 1.5) if major else (6.6, 2.2, 1.0)
        ex, ey = np.cos(th), np.sin(th)
        along = du * ex + dv * ey
        perp = np.abs(-du * ey + dv * ex)
        hw = w0 * np.clip(1 - along / L, 0, 1)
        inside = corner & (along > -0.5) & (along < L) & (perp < hw)
        ridge = 1 - perp / np.maximum(hw, 1e-3)
        hh = 6.9 + top * ridge * (0.6 + 0.4 * np.clip(1 - along / L, 0, 1)) + (0.6 if major else 0)
        starh = np.where(inside & (hh > starh), hh, starh)
    m = starh > 0
    mp.put(m, starh, GOLD * (1 + 0.05 * bn)[..., None], 1.0, 50.0)
    boss = corner & (rr < 2.0)
    mp.put(boss, 8.8 + 0.8 * np.sqrt(np.clip(1 - (rr / 2.0) ** 2, 0, 1)), BRASS * 1.1, 1.0, 50.0)

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
    warm = np.array([1.0, 0.95, 0.85])
    col = alb * shade[..., None] + (spec * ndh ** shin)[..., None] * 0.85 * warm
    return np.clip(col, 0, 1)


def BORDER():
    mp = _paint()
    col = _light(mp)
    alpha = np.clip(mp.alpha, 0, 1)
    ai = Image.fromarray((alpha * 255).astype(np.uint8))
    ring = np.asarray(ai.filter(ImageFilter.MaxFilter(3)), dtype=np.float64) / 255
    a = np.maximum(alpha, ring)
    col = col * (alpha / np.maximum(a, 1e-6))[..., None] + np.array([0.025, 0.02, 0.015]) * ((a - alpha) / np.maximum(a, 1e-6))[..., None]
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
