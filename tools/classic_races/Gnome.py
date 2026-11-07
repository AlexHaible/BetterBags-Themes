"""Gnome classic border: Gnomeregan / Tinker Town polished copper, brass and pale enamel.

The band is a slim, rounded frame: a polished copper bead on the outside, a glossy pale blue-white
enamel panel in the middle and a fine brass bead on the inside. Along each edge, once per segment,
sits a cyan light crystal (the crest's blue gem) in a round brass bezel and a small copper strap
fixed with one round brass rivet. Each corner is a round brass gear housing: rounded gear teeth, a
polished copper cap with four rivets, and a faceted cyan crystal in the middle.

Drawn as a height map + material maps at 2x, lit from the top left, then downsampled to 256.
Everything along an edge repeats every 160 texels (the edge segment between the slice margins).
"""
import numpy as np
from PIL import Image, ImageFilter

SIZE = 256
SS = 2                    # supersampling
SLICE = 48
SEG = SIZE - 2 * SLICE    # 160: the edge segment; edge art repeats with this period

THEME = dict(
    Name="RacesGnome", Background="SOLID", BackgroundInset=8,
    Color=(0.04, 0.06, 0.10, 0.8), Slice=SLICE, Outset=20, TitleY=40, Close={"X": 16, "Y": 16},
    Search=("TOPRIGHT", -22, -2), Menu={"X": -28, "Y": 28},
    TabEdge=(0.78, 0.58, 0.26, 1), TabAccent=(0.45, 0.88, 1.0, 1),
)

# albedo (0..1)
COPPER = np.array([0.74, 0.38, 0.20])
BRASS = np.array([0.80, 0.62, 0.27])
ENAMEL = np.array([0.72, 0.78, 0.84])
CRYSTAL = np.array([0.30, 0.74, 0.92])
GLOW = np.array([0.55, 0.95, 1.00])


def _smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def _noise(n, seed, sx, sy):
    """Periodic noise n x n (FFT filtered): sx/sy are blur scales along columns/rows."""
    rng = np.random.default_rng(seed)
    f = np.fft.fft2(rng.standard_normal((n, n)))
    ky = np.fft.fftfreq(n)[:, None]
    kx = np.fft.fftfreq(n)[None, :]
    f *= np.exp(-((kx * sx) ** 2 + (ky * sy) ** 2) * 20)
    r = np.real(np.fft.ifft2(f))
    return (r - r.mean()) / (r.std() + 1e-9)


def _dome(cx, cy, R, u, v):
    r2 = ((u - cx) ** 2 + (v - cy) ** 2) / (R * R)
    return np.where(r2 < 1, np.sqrt(np.clip(1 - r2, 0, 1)), -1.0)


def _hex_sdf(u, v, cx, cy, R):
    """Signed distance to a pointy-topped hexagon of circumradius R (approx, negative inside)."""
    x, y = np.abs(u - cx), np.abs(v - cy)
    a = R * np.sqrt(3) / 2
    return np.maximum(x - a, (y * np.sqrt(3) / 2 + x * 0.5) - a)


def _paint():
    N = SIZE * SS
    idx = (np.arange(N) + 0.5) / SS
    X, Y = np.meshgrid(idx, idx)
    S = SLICE

    # ---- per-side band coordinates: d = depth into the band, t = position along the segment
    stack = np.stack([Y, SIZE - Y, X, SIZE - X])
    side = np.argmin(stack, axis=0)
    d = np.min(stack, axis=0)
    t = np.where(side < 2, X - S, Y - S)
    tm = np.mod(t, SEG)
    in_seg = (t >= 0) & (t < SEG)

    nP = SEG * SS
    ti = np.mod(np.floor(t * SS), nP).astype(int)
    di = np.mod(np.floor(d * SS), nP).astype(int)
    brushed = _noise(nP, 1, 6.0, 0.4)[di, ti]      # fine polish streaks along the band
    blotch = _noise(nP, 2, 9.0, 9.0)[di, ti]

    h = np.zeros((N, N))
    alb = np.zeros((N, N, 3))
    spec = np.zeros((N, N))
    shin = np.full((N, N), 30.0)
    emit = np.zeros((N, N, 3))
    alpha = np.zeros((N, N))

    def put(mask, hv, col, sp, sh):
        nonlocal h, alb, spec, shin
        h = np.where(mask, hv, h)
        alb = np.where(mask[..., None], col, alb)
        spec = np.where(mask, sp, spec)
        shin = np.where(mask, sh, shin)

    # ---- enamel panel (lowest layer of the band)
    en = (d > 5.4) & (d < 20.0)
    gloss = 1 + 0.025 * blotch - 0.10 * _smooth(9.0, 5.8, d) - 0.08 * _smooth(15.5, 19.5, d)
    put(en, np.full_like(h, 1.3), ENAMEL * gloss[..., None], 0.40, 60.0)
    # a fine engraved line down the middle of the enamel
    eng = en & (np.abs(d - 12.6) < 0.35)
    h = np.where(eng, h - 0.35, h)
    alb = np.where(eng[..., None], alb * 0.86, alb)

    # ---- outer copper bead
    pd = np.abs(d - 3.5)
    ob = pd < 2.9
    hb = 0.6 + 2.5 * np.sqrt(np.clip(1 - (pd / 2.9) ** 2, 0, 1))
    put(ob & (hb > h), hb, COPPER * (1 + 0.05 * brushed + 0.05 * blotch)[..., None], 0.9, 34.0)

    # ---- inner brass bead
    pd = np.abs(d - 20.6)
    ib = pd < 2.1
    hb = 0.6 + 1.9 * np.sqrt(np.clip(1 - (pd / 2.1) ** 2, 0, 1))
    put(ib & (hb > h), hb, BRASS * (1 + 0.05 * brushed)[..., None], 0.95, 40.0)

    alpha = np.clip((d - 0.6) * SS + 0.5, 0, 1) * np.clip((22.7 - d) * SS + 0.5, 0, 1)

    # ---- per segment: a copper strap with a rivet (t = 120) and a cyan crystal (t = 40)
    sd = np.abs(tm - 120)
    st = in_seg & (sd < 3.6) & (d > 5.0) & (d < 20.4)
    hs = 2.4 + 0.6 * _smooth(3.6, 2.4, sd)
    put(st, hs, COPPER * 1.04 * (1 + 0.05 * blotch)[..., None], 0.85, 36.0)
    dm = np.where(in_seg, _dome(120.0, 12.6, 2.1, tm, d), -1)
    ring = in_seg & (dm < 0) & (_dome(120.0, 12.6, 2.9, tm, d) >= 0)
    alb = np.where(ring[..., None], alb * 0.7, alb)
    m = dm >= 0
    put(m, 3.0 + 1.4 * dm, BRASS * 1.05, 1.0, 46.0)

    lr = np.sqrt((tm - 40) ** 2 + (d - 12.6) ** 2)
    halo = in_seg & en & (lr < 10)
    emit = np.where(halo[..., None], GLOW * 0.10 * np.exp(-((lr - 6.4) / 2.0) ** 2)[..., None], emit)
    bez = in_seg & (lr < 6.4)
    put(bez, 3.0 + 0.9 * _smooth(6.4, 5.4, lr), BRASS * (1 + 0.04 * blotch)[..., None], 0.95, 44.0)
    hx = np.where(in_seg, _hex_sdf(tm, d, 40.0, 12.6, 4.9), 1)
    gem = hx < 0
    put(gem, 3.6 + np.minimum(-hx, 1.6) * 1.2, CRYSTAL, 1.4, 70.0)
    gr2 = (tm - 39.0) ** 2 + (d - 11.6) ** 2
    emit = np.where(gem[..., None], GLOW * (0.55 * np.exp(-gr2 / 7.0) + 0.10)[..., None], emit)

    # ---- corners: round brass gear housing (top-left design, mirrored; lit afterwards)
    cu = np.where(X < SIZE / 2, X, SIZE - X)
    cv = np.where(Y < SIZE / 2, Y, SIZE - Y)
    corner = (cu < S) & (cv < S)
    bn = _noise(nP, 3, 5.0, 5.0)[np.floor(cv * SS).astype(int) % nP, np.floor(cu * SS).astype(int) % nP]
    c0 = 20.0
    du, dv = cu - c0, cv - c0
    r = np.sqrt(du * du + dv * dv)
    th = np.arctan2(dv, du)
    tooth = _smooth(-0.35, 0.35, np.cos(12 * th))
    rout = 16.2 + 3.3 * tooth
    gear = corner & (r < rout)
    # contact shadow of the gear on the band
    gsh = corner & ~gear & (r < rout + 1.3)
    alb = np.where(gsh[..., None], alb * 0.65, alb)
    hg = 4.0 + 1.1 * _smooth(0, 1.4, rout - r)
    put(gear, hg, BRASS * (1 + 0.06 * bn + 0.03 * brushed)[..., None], 0.95, 40.0)
    alpha = np.where(corner, np.maximum(alpha, np.clip((rout - r) * SS + 0.5, 0, 1)), alpha)
    groove = gear & (np.abs(r - 15.0) < 0.55)
    h = np.where(groove, h - 0.7, h)
    alb = np.where(groove[..., None], alb * 0.55, alb)

    # polished copper cap
    cap = corner & (r < 14.3)
    put(cap, 5.4 + 0.9 * (1 - (r / 14.3) ** 2) + 0.6 * _smooth(14.3, 13.3, r),
        COPPER * (1 + 0.05 * bn)[..., None], 0.95, 36.0)
    for a in (np.pi / 4, 3 * np.pi / 4, 5 * np.pi / 4, 7 * np.pi / 4):
        ru, rv = c0 + 10.9 * np.cos(a), c0 + 10.9 * np.sin(a)
        dm = np.where(corner, _dome(ru, rv, 1.7, cu, cv), -1)
        ring = corner & (dm < 0) & (_dome(ru, rv, 2.4, cu, cv) >= 0)
        alb = np.where(ring[..., None], alb * 0.72, alb)
        m = dm >= 0
        put(m, 6.4 + 1.2 * dm, BRASS * 1.05, 1.0, 46.0)

    # brass bezel and faceted cyan crystal
    bez = corner & (r < 8.0)
    put(bez, 6.8 + 0.8 * _smooth(8.0, 7.0, r), BRASS * (1 + 0.04 * bn)[..., None], 0.95, 44.0)
    halo = corner & cap & ~bez & (r < 11)
    emit = np.where(halo[..., None], GLOW * 0.08 * np.exp(-((r - 8.0) / 1.6) ** 2)[..., None], emit)
    hx = np.where(corner, _hex_sdf(cu, cv, c0, c0, 6.5), 1)
    gem = hx < 0
    put(gem, 7.2 + np.minimum(-hx, 2.2) * 1.3, CRYSTAL, 1.5, 80.0)
    gr2 = (cu - c0 + 1.2) ** 2 + (cv - c0 + 1.4) ** 2
    emit = np.where(gem[..., None], GLOW * (0.60 * np.exp(-gr2 / 10.0) + 0.12)[..., None], emit)

    return h, alb, spec, shin, emit, alpha


def _light(h, alb, spec, shin, emit):
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

    # cast shadows toward the bottom right; short reach so nothing crosses a slice line
    N = h.shape[0]
    pad = 8
    hp = np.pad(h, pad, mode="edge")
    shadow = np.zeros_like(h)
    for s in range(1, 6):
        sh = hp[pad - s:pad - s + N, pad - s:pad - s + N]
        shadow = np.maximum(shadow, np.clip((sh - h - 0.3 * s) / 1.2, 0, 1))
    shade = 0.32 + 0.80 * ndl / L[2]
    shade *= 1 - 0.45 * shadow
    col = alb * shade[..., None] + (spec * ndh ** shin)[..., None] * 0.8 + emit
    return np.clip(col, 0, 1)


def BORDER():
    h, alb, spec, shin, emit, alpha = _paint()
    col = _light(h, alb, spec, shin, emit)
    # thin dark outline on the outside of the art, then a soft drop shadow down/right onto the bag
    ai = Image.fromarray((alpha * 255).astype(np.uint8))
    ring = np.asarray(ai.filter(ImageFilter.MaxFilter(3)), dtype=np.float64) / 255
    a = np.maximum(alpha, ring)
    col = col * (alpha / np.maximum(a, 1e-6))[..., None] + np.array([0.12, 0.06, 0.03]) * ((a - alpha) / np.maximum(a, 1e-6))[..., None]
    sh = np.zeros_like(a)
    sh[3:, 3:] = a[:-3, :-3]
    sha = np.asarray(Image.fromarray((sh * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3)),
                     dtype=np.float64) / 255 * 0.5
    out_a = a + sha * (1 - a)
    out_rgb = col * (a / np.maximum(out_a, 1e-6))[..., None]
    rgba = np.dstack([out_rgb * out_a[..., None], out_a])     # premultiplied for the downsample
    rgba = rgba.reshape(SIZE, SS, SIZE, SS, 4).mean(axis=(1, 3))
    A = rgba[..., 3:4]
    rgb = np.where(A > 1e-6, rgba[..., :3] / np.maximum(A, 1e-6), 0)
    img = np.clip(np.dstack([rgb, A]) * 255 + 0.5, 0, 255)
    c = img[SLICE:SIZE - SLICE, SLICE:SIZE - SLICE]
    c[..., 3] = np.where(c[..., 3] < 3, 0, c[..., 3])          # the centre must be fully transparent
    return Image.fromarray(img.astype(np.uint8), "RGBA")
