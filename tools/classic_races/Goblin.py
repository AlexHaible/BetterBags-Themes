"""Goblin classic border: Bilgewater/Undermine riveted gunmetal with a copper pipe and brass corner plates.

The band is a dark gunmetal plate (riveted seams, a small green-lit lamp) with a copper steam pipe
along its inner edge (brass couplings). Each corner is a worn brass plate clipped toward the window,
with a hazard-striped lip on the clip, three rivets, and a gunmetal hex nut holding a green glass
lens (the crest's green bulb).

Drawn as a height map + material maps at 2x, lit from the top left, then downsampled to 256.
Everything along an edge repeats every 160 texels (the edge segment between the slice margins).
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SIZE = 256
SS = 2                    # supersampling
SLICE = 48
SEG = SIZE - 2 * SLICE    # 160: the edge segment; edge art repeats with this period

THEME = dict(
    Name="RacesGoblin", Background="SOLID", BackgroundInset=8,
    Color=(0.05, 0.08, 0.05, 0.8), Slice=SLICE, Outset=24, TitleY=29, Close={"X": 18, "Y": 18},
    Search=("TOPRIGHT", -22, -2), Menu={"X": -28, "Y": 28},
    TabEdge=(0.25, 0.27, 0.27, 1), TabAccent=(0.55, 0.85, 0.2, 1),
)

# albedo (0..1)
IRON = np.array([0.205, 0.225, 0.235])
STEEL = np.array([0.42, 0.44, 0.44])
COPPER = np.array([0.58, 0.30, 0.15])
VERDIGRIS = np.array([0.24, 0.42, 0.33])
BRASS = np.array([0.64, 0.49, 0.21])
NUT = np.array([0.27, 0.29, 0.29])
HAZ_Y = np.array([0.80, 0.60, 0.10])
HAZ_K = np.array([0.07, 0.07, 0.065])
GLASS = np.array([0.12, 0.36, 0.06])
GLOW = np.array([0.50, 1.00, 0.22])


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
    """Signed distance to a flat-topped hexagon of circumradius R (approx, negative inside)."""
    x, y = np.abs(u - cx), np.abs(v - cy)
    a = R * np.sqrt(3) / 2
    return np.maximum(y - a, (x * np.sqrt(3) / 2 + y * 0.5) - a)


def _scratches(nP, seed):
    """Sparse wear scratches on the plate, in (d, t) space, wrapping in t."""
    rng = np.random.default_rng(seed)
    img = Image.new("L", (nP, 20 * SS), 0)
    dr = ImageDraw.Draw(img)
    for _ in range(9):
        t0 = rng.uniform(0, nP)
        d0 = rng.uniform(3, 17) * SS
        ln = rng.uniform(4, 11) * SS
        ang = rng.uniform(-0.5, 0.5)
        dt, dd = ln * np.cos(ang), ln * np.sin(ang)
        for off in (-nP, 0, nP):
            dr.line((t0 + off, d0, t0 + off + dt, d0 + dd), fill=int(rng.uniform(120, 220)), width=1)
    a = np.asarray(img, dtype=np.float64) / 255
    return a


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
    brushed = _noise(nP, 1, 6.0, 0.4)[di, ti]      # streaks run along the band
    soot = _noise(nP, 4, 0.5, 4.0)[di, ti]          # faint streaks across it
    blotch = _noise(nP, 2, 9.0, 9.0)[di, ti]
    wob = _noise(nP, 5, 6.0, 6.0)[0, ti]            # outline wobble, periodic in t
    scr = _scratches(nP, 6)
    scratch = np.where(d < 20, scr[np.clip(np.floor(d * SS).astype(int), 0, 20 * SS - 1), ti], 0)

    h = np.zeros((N, N))
    alb = np.zeros((N, N, 3))
    spec = np.zeros((N, N))
    shin = np.full((N, N), 24.0)
    emit = np.zeros((N, N, 3))
    alpha = np.zeros((N, N))

    # ---- gunmetal plate
    d0 = 0.35 * wob
    plate = d < 19.4
    hp = 3.0 * _smooth(d0, d0 + 2.0, d) * (1 - _smooth(17.6, 19.4, d))
    seam = in_seg & (d > 1.2) & (d < 18.2) & ((np.abs(tm - 60) < 0.75) | (np.abs(tm - 140) < 0.75))
    hp = np.where(seam, hp - 1.2, hp)
    h = np.where(plate, hp, h)
    panel = np.where(np.mod(t - 60, SEG) < 80, 1.045, 0.955)
    seamdist = np.minimum(np.abs(tm - 60), np.abs(tm - 140))
    grime = (1 - 0.22 * _smooth(3.5, 0.5, d) - 0.30 * _smooth(13.5, 19, d)
             - 0.18 * np.where(in_seg, _smooth(4, 0.8, seamdist), 0) + 0.05 * soot)
    iron = IRON * (panel * (1 + 0.04 * brushed + 0.08 * blotch) * grime)[..., None]
    iron = iron * (1 + 0.55 * scratch)[..., None]
    alb = np.where(plate[..., None], iron, alb)
    spec = np.where(plate, 0.22 + 0.25 * scratch, spec)
    shin = np.where(plate, 18.0, shin)
    alpha = np.where(plate, np.clip((d - d0) * SS + 0.5, 0, 1), alpha)

    # seam rivets, each slightly different
    rng = np.random.default_rng(11)
    for sx in (60.0, 140.0):
        for cx in (sx - 5.5, sx + 5.5):
            for cy in (6.0, 13.5):
                R = rng.uniform(1.85, 2.25)
                jx, jy = rng.uniform(-0.3, 0.3, 2)
                dm = np.where(in_seg, _dome(cx + jx, cy + jy, R, tm, d), -1)
                m = dm >= 0
                ring = in_seg & ~m & (_dome(cx + jx, cy + jy, R + 1.0, tm, d) >= 0)
                alb = np.where(ring[..., None], alb * 0.7, alb)
                h = np.where(m, np.maximum(h, 3.0 + 1.3 * dm), h)
                alb = np.where(m[..., None], STEEL * rng.uniform(0.85, 1.1), alb)
                spec = np.where(m, rng.uniform(0.4, 0.75), spec)
                shin = np.where(m, 30.0, shin)

    # the goblin tell: a small green-lit lamp in a brass bezel, once per segment
    lr = np.sqrt((tm - 100) ** 2 + (d - 10.0) ** 2)
    bez = in_seg & (lr < 3.9)
    h = np.where(bez, 3.0 + 1.6 * _smooth(3.9, 2.9, lr), h)
    alb = np.where(bez[..., None], BRASS * 0.95, alb)
    spec = np.where(bez, 0.8, spec)
    shin = np.where(bez, 40.0, shin)
    halo = in_seg & plate & ~bez & (lr < 7)
    emit = np.where(halo[..., None], GLOW * 0.10 * np.exp(-((lr - 3.9) / 1.6) ** 2)[..., None], emit)
    lamp = in_seg & (lr < 2.5)
    h = np.where(lamp, 4.1 + 1.0 * np.sqrt(np.clip(1 - (lr / 2.5) ** 2, 0, 1)), h)
    alb = np.where(lamp[..., None], GLASS, alb)
    spec = np.where(lamp, 1.3, spec)
    shin = np.where(lamp, 60.0, shin)
    emit = np.where(lamp[..., None], GLOW * (0.75 * np.exp(-(((tm - 100.4) ** 2 + (d - 10.4) ** 2) / 2.2)))[..., None], emit)

    # ---- copper pipe
    pr = 4.2
    pd = np.abs(d - 24.0)
    pipe = pd < pr
    hpipe = 1.5 + np.sqrt(np.clip(pr * pr - pd * pd, 0, None))
    copper = COPPER * (1 + 0.05 * brushed + 0.10 * blotch)[..., None]
    cdist = np.abs(tm - 20)
    verd = np.where(in_seg, _smooth(9.0, 3.6, cdist), 0) * _smooth(0.5, 3.6, pd) * (0.75 + 0.3 * blotch).clip(0, 1)
    copper = copper * (1 - verd[..., None]) + VERDIGRIS * verd[..., None]
    m = pipe & (hpipe > h)
    h = np.where(m, hpipe, h)
    alb = np.where(m[..., None], copper, alb)
    spec = np.where(m, 0.6 * (1 - verd), spec)
    shin = np.where(m, 26.0, shin)
    alpha = np.where(pipe, np.maximum(alpha, np.clip((pr - pd) * SS + 0.5, 0, 1)), alpha)

    def collar(mask_t, R, mat, sp=0.75):
        nonlocal h, alb, spec, alpha, shin
        hc = 1.5 + np.sqrt(np.clip(R * R - pd * pd, 0, None))
        m = mask_t & (pd < R)
        h = np.where(m, np.maximum(h, hc), h)
        alb = np.where(m[..., None], mat * (1 + 0.06 * blotch)[..., None], alb)
        spec = np.where(m, sp, spec)
        shin = np.where(m, 36.0, shin)
        alpha = np.where(m, np.maximum(alpha, np.clip((R - pd) * SS + 0.5, 0, 1)), alpha)

    collar(in_seg & (cdist < 3.4), 5.0, BRASS)
    collar(in_seg & (np.abs(cdist - 2.5) < 0.85), 5.5, BRASS * 1.05)

    # ---- corners (top-left design, mirrored; lighting is applied afterwards so it stays top-left)
    cu = np.where(X < SIZE / 2, X, SIZE - X)
    cv = np.where(Y < SIZE / 2, Y, SIZE - Y)
    corner = (cu < S) & (cv < S)
    bn = _noise(nP, 3, 5.0, 5.0)[np.floor(cv * SS).astype(int) % nP, np.floor(cu * SS).astype(int) % nP]

    # brass flange where the pipe leaves the plate
    for along, across in ((cu, cv), (cv, cu)):
        fl = corner & (np.abs(along - 45.0) < 1.7) & (np.abs(across - 24) < 5.7)
        hc = 1.5 + np.sqrt(np.clip(5.7 ** 2 - (across - 24) ** 2, 0, None))
        h = np.where(fl, np.maximum(h, hc), h)
        alb = np.where(fl[..., None], BRASS * 0.9, alb)
        spec = np.where(fl, 0.75, spec)
        shin = np.where(fl, 36.0, shin)
        alpha = np.where(fl, 1.0, alpha)

    sd = np.maximum.reduce([0.8 - cu, 0.8 - cv, cu - 43.5, cv - 43.5, (cu + cv - 69) / np.sqrt(2)])
    cp = corner & (sd < 0.5)
    hpl = 5.0 + 1.9 * _smooth(0, 2.2, -sd)
    engr = np.abs(sd + 4.2) < 0.45                       # engraved line inside the rim
    hpl = np.where(engr, hpl - 0.6, hpl)
    edge_dark = _smooth(-4.5, 0, sd)
    brass = BRASS * ((1 + 0.07 * bn + 0.05 * brushed) * (1 - 0.30 * edge_dark) * np.where(engr, 0.6, 1))[..., None]
    h = np.where(cp, hpl, h)
    alb = np.where(cp[..., None], brass, alb)
    spec = np.where(cp, 0.85, spec)
    shin = np.where(cp, 40.0, shin)
    alpha = np.where(cp, np.maximum(alpha, np.clip((0.5 - sd) * SS, 0, 1)), alpha)

    # hazard stripes along the clipped lip
    dd = -(cu + cv - 69) / np.sqrt(2)
    haz = cp & (dd > 2.6) & (dd < 7.2) & (cu > 4.5) & (cv > 4.5)
    stripes = np.mod(cu - cv + 0.5 * bn, 6.0) < 3.0
    hz = np.where(stripes[..., None], HAZ_Y, HAZ_K) * (1 + 0.10 * bn - 0.05 * np.abs(brushed))[..., None]
    h = np.where(haz, 5.5 + 0.5 * _smooth(2.6, 3.3, dd) * _smooth(7.2, 6.5, dd), h)
    alb = np.where(haz[..., None], hz, alb)
    spec = np.where(haz, 0.18, spec)
    shin = np.where(haz, 14.0, shin)

    # plate rivets
    for (ru, rv, R) in ((5.4, 5.4, 2.4), (38.6, 5.4, 2.2), (5.4, 38.6, 2.2)):
        dm = np.where(corner, _dome(ru, rv, R, cu, cv), -1)
        m = dm >= 0
        ring = corner & ~m & (_dome(ru, rv, R + 0.9, cu, cv) >= 0)
        alb = np.where(ring[..., None], alb * 0.6, alb)
        h = np.where(m, 6.8 + 1.4 * dm, h)
        alb = np.where(m[..., None], BRASS * 1.05, alb)
        spec = np.where(m, 0.9, spec)
        shin = np.where(m, 44.0, shin)

    # hex nut, brass bezel, green glass lens
    nc = 19.0
    hs = _hex_sdf(cu, cv, nc, nc, 11.0)
    nutshadow = corner & (hs > 0) & (hs < 1.4) & cp
    alb = np.where(nutshadow[..., None], alb * 0.65, alb)
    nut = corner & (hs < 0)
    h = np.where(nut, 6.9 + 1.7 * _smooth(0, 1.8, -hs), h)
    alb = np.where(nut[..., None], NUT * (1 + 0.06 * bn + 0.04 * brushed)[..., None], alb)
    spec = np.where(nut, 0.5, spec)
    shin = np.where(nut, 26.0, shin)
    rr = np.sqrt((cu - nc) ** 2 + (cv - nc) ** 2)
    bez = corner & (rr < 7.7)
    h = np.where(bez, 8.6 + 0.5 * _smooth(7.7, 6.9, rr), h)
    alb = np.where(bez[..., None], BRASS * 0.85, alb)
    spec = np.where(bez, 0.9, spec)
    shin = np.where(bez, 44.0, shin)
    lens = corner & (rr < 6.3)
    dm = np.sqrt(np.clip(1 - (rr / 6.3) ** 2, 0, 1))
    h = np.where(lens, 8.6 + 2.4 * dm, h)
    alb = np.where(lens[..., None], GLASS, alb)
    spec = np.where(lens, 1.5, spec)
    shin = np.where(lens, 70.0, shin)
    gr2 = (cu - nc - 1.3) ** 2 + (cv - nc - 1.3) ** 2
    emit = np.where(lens[..., None], GLOW * (0.85 * np.exp(-gr2 / 11.0) + 0.06)[..., None], emit)

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
    shade = 0.30 + 0.85 * ndl / L[2]
    shade *= 1 - 0.5 * shadow
    col = alb * shade[..., None] + (spec * ndh ** shin)[..., None] * 0.85 + emit
    return np.clip(col, 0, 1)


def BORDER():
    h, alb, spec, shin, emit, alpha = _paint()
    col = _light(h, alb, spec, shin, emit)
    # thin dark outline on the outside of the art, then a soft drop shadow down/right onto the bag
    ai = Image.fromarray((alpha * 255).astype(np.uint8))
    ring = np.asarray(ai.filter(ImageFilter.MaxFilter(3)), dtype=np.float64) / 255
    a = np.maximum(alpha, ring)
    col = col * (alpha / np.maximum(a, 1e-6))[..., None] + np.array([0.03, 0.03, 0.025]) * ((a - alpha) / np.maximum(a, 1e-6))[..., None]
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
