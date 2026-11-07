"""Mechagnome classic border: Mechagon salvage plating, Titan-refined.

The band is an exoskeleton of dark teal-patinated bronze lames: overlapping segmented plates with
chevron seams, each plate stepping up slightly toward its trailing edge. A fine groove runs down the
middle of the plates carrying a thin, restrained cyan energy line that dims toward every seam, and
small hex-bolt heads sit on alternate seams. An aged-bronze bead rims the outside and a rounded
aged-bronze rail runs along the window side (the crest's gilded trim on teal).
Each corner is a chamfered teal plate rimmed in bronze, carrying a quarter-turned bronze gear ring
(the crest's gear) around a dark hex cap with a glowing cyan core and three broken cyan arcs.

Drawn as a height map + material maps at 2x, lit from the top left, then downsampled to 256.
Everything along an edge repeats every 160 texels (the edge segment between the slice margins).
"""
import numpy as np
from PIL import Image, ImageFilter

SIZE = 256
SS = 2
SLICE = 48
SEG = SIZE - 2 * SLICE    # 160
LAME = 40.0               # plate length (4 per segment)

THEME = dict(
    Name="RacesMechagnome", Background="SOLID", BackgroundInset=8,
    Color=(0.02, 0.06, 0.07, 0.8), Slice=SLICE, Outset=20, TitleY=27, Close={"X": 16, "Y": 16},
    Search=("TOPRIGHT", -22, -2), Menu={"X": -28, "Y": 28},
    TabEdge=(0.16, 0.30, 0.29, 1), TabAccent=(0.35, 0.88, 0.95, 1),
)

TEAL = np.array([0.055, 0.125, 0.125])
PATINA = np.array([0.10, 0.20, 0.18])
BRONZE = np.array([0.47, 0.37, 0.19])
DARKBR = np.array([0.30, 0.24, 0.14])
CAP = np.array([0.09, 0.15, 0.15])
GLOW = np.array([0.30, 0.92, 1.00])


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


def _hex_sdf(u, v, cx, cy, R, rot=0.0):
    x, y = u - cx, v - cy
    c, s = np.cos(rot), np.sin(rot)
    x, y = np.abs(c * x - s * y), np.abs(s * x + c * y)
    a = R * np.sqrt(3) / 2
    return np.maximum(y - a, (x * np.sqrt(3) / 2 + y * 0.5) - a)


def _paint():
    N = SIZE * SS
    idx = (np.arange(N) + 0.5) / SS
    X, Y = np.meshgrid(idx, idx)
    S = SLICE

    stack = np.stack([Y, SIZE - Y, X, SIZE - X])
    side = np.argmin(stack, axis=0)
    d = np.min(stack, axis=0)
    t = np.where(side < 2, X - S, Y - S)
    in_seg = (t >= 0) & (t < SEG)

    nP = SEG * SS
    ti = np.mod(np.floor(t * SS), nP).astype(int)
    di = np.mod(np.floor(d * SS), nP).astype(int)
    brushed = _noise(nP, 1, 6.0, 0.4)[di, ti]
    blotch = _noise(nP, 2, 7.0, 7.0)[di, ti]
    fine = _noise(nP, 3, 1.2, 1.2)[di, ti]
    wob = _noise(nP, 5, 6.0, 6.0)[0, ti]

    h = np.zeros((N, N))
    alb = np.zeros((N, N, 3))
    spec = np.zeros((N, N))
    shin = np.full((N, N), 24.0)
    emit = np.zeros((N, N, 3))
    alpha = np.zeros((N, N))

    patina = np.clip(0.45 + 0.35 * blotch + 0.12 * fine, 0, 1)
    teal = (TEAL * (1 - patina[..., None]) + PATINA * patina[..., None]) * (1 + 0.05 * brushed)[..., None]
    bronze = BRONZE * (1 + 0.06 * brushed + 0.08 * blotch)[..., None]
    pw = 0.18 * np.clip(0.3 + 0.5 * blotch, 0, 1)
    bronze = bronze * (1 - pw)[..., None] + PATINA * pw[..., None]

    # ---- outer bronze bead
    d0 = 0.3 * wob
    PL0, PL1 = 3.0, 16.6          # plate span
    RA0, RA1 = 16.2, 20.4         # inner rail span
    bead = d < PL0 + 0.2
    rb = (PL0 - d0) / 2
    pb = np.abs(d - (d0 + rb))
    hb = 2.4 + 1.2 * np.sqrt(np.clip(1 - (pb / rb) ** 2, 0, 1))
    h = np.where(bead, hb, h)
    alb = np.where(bead[..., None], bronze * 0.9, alb)
    spec = np.where(bead, 0.6, spec)
    shin = np.where(bead, 30.0, shin)
    alpha = np.where(bead, np.clip((d - d0) * SS + 0.5, 0, 1), alpha)

    # ---- segmented lames, chevron seams
    plate = (d >= PL0) & (d < RA0 + 0.4)
    mid = (PL0 + PL1) / 2
    chev = 0.45 * np.abs(d - mid)                  # seam leans back toward both band edges
    u = np.mod(t - 10.0 + chev, LAME)              # position within a lame; seams at u=0
    k = np.floor((t - 10.0 + chev) / LAME)
    seamd = np.minimum(u, LAME - u)
    hp = 2.0 + 0.9 * (u / LAME) + 0.5 * _smooth(PL0, PL0 + 1.6, d) * _smooth(PL1, PL1 - 1.6, d)
    hp = hp - 1.6 * _smooth(1.2, 0.0, seamd)       # dark gap between lames
    # central energy groove
    gd = np.abs(d - mid)
    groove = gd < 1.25
    hp = np.where(groove, hp - 0.9 * _smooth(1.25, 0.6, gd), hp)
    h = np.where(plate, hp, h)
    lame_tone = 1.0 + 0.05 * np.cos(k * 2.1)
    pal = teal * (lame_tone * (1 - 0.35 * _smooth(1.6, 0.2, seamd)) * (1 - 0.25 * _smooth(1.25, 0.4, gd)))[..., None]
    # bronze tip strip on each lame's trailing edge (a little wear-polished)
    tip = (LAME - u < 3.2) & (LAME - u > 1.1)
    pal = np.where(tip[..., None], bronze * 0.8, pal)
    alb = np.where(plate[..., None], pal, alb)
    spec = np.where(plate, np.where(tip, 0.6, 0.28), spec)
    shin = np.where(plate, np.where(tip, 30.0, 16.0), shin)
    alpha = np.where(plate, 1.0, alpha)

    # cyan energy line in the groove, dimming toward every seam
    gu = np.mod(t - 10.0, LAME)
    run = _smooth(2.5, 9.0, np.minimum(gu, LAME - gu))
    core = np.exp(-(gd / 0.45) ** 2) * run
    halo = np.exp(-(gd / 1.6) ** 2) * run
    emit = emit + GLOW * ((0.75 * core + 0.12 * halo) * plate)[..., None]

    # hex bolts on alternate seams, above and below the groove
    tm = np.mod(t, SEG)
    for sx in (10.0, 90.0):
        for cy in (6.2, 13.4):
            cx = sx - 0.45 * abs(cy - mid)
            hs = _hex_sdf(tm, d, cx, cy, 2.1, rot=0.2)
            ring = in_seg & (hs > 0) & (hs < 0.8)
            alb = np.where(ring[..., None], alb * 0.55, alb)
            m = in_seg & (hs < 0)
            h = np.where(m, 3.6 + 0.9 * _smooth(0, 0.9, -hs), h)
            alb = np.where(m[..., None], BRONZE * 0.95, alb)
            spec = np.where(m, 0.75, spec)
            shin = np.where(m, 36.0, shin)

    # ---- inner bronze rail
    rail = (d >= RA0) & (d < RA1)
    rr = (RA1 - RA0) / 2
    pr = np.abs(d - (RA0 + rr))
    hr = 2.2 + 1.8 * np.sqrt(np.clip(1 - (pr / rr) ** 2, 0, 1))
    m = rail & (hr > h)
    h = np.where(m, hr, h)
    alb = np.where(m[..., None], bronze, alb)
    spec = np.where(m, 0.7, spec)
    shin = np.where(m, 32.0, shin)
    alpha = np.where(rail, np.maximum(alpha, np.clip((RA1 - d) * SS + 0.5, 0, 1)), alpha)

    # ---- corners (top-left design, mirrored)
    cu = np.where(X < SIZE / 2, X, SIZE - X)
    cv = np.where(Y < SIZE / 2, Y, SIZE - Y)
    corner = (cu < S) & (cv < S)
    cn = _noise(nP, 4, 5.0, 5.0)[np.floor(cv * SS).astype(int) % nP, np.floor(cu * SS).astype(int) % nP]
    cpat = np.clip(0.45 + 0.35 * cn, 0, 1)
    cteal = TEAL * (1 - cpat[..., None]) + PATINA * cpat[..., None]
    cbron = BRONZE * (1 + 0.07 * cn)[..., None]

    # chamfered plate
    sd = np.maximum.reduce([0.6 - cu, 0.6 - cv, cu - 40.0, cv - 40.0, (cu + cv - 64) / np.sqrt(2)])
    cp = corner & (sd < 0.5)
    rim = sd > -2.6
    hpl = np.where(rim, 4.6 + 1.0 * _smooth(0, 1.3, -sd) * _smooth(-2.6, -1.4, sd), 3.9)
    h = np.where(cp, hpl, h)
    alb = np.where(cp[..., None], np.where(rim[..., None], cbron * 0.95, cteal * 0.9), alb)
    spec = np.where(cp, np.where(rim, 0.7, 0.3), spec)
    shin = np.where(cp, np.where(rim, 32.0, 16.0), shin)
    alpha = np.where(cp, np.maximum(alpha, np.clip((0.5 - sd) * SS, 0, 1)), alpha)
    emit = np.where(cp[..., None], 0.0, emit)

    # small hex bolts on the plate tips
    for (bu, bv) in ((36.0, 4.6), (4.6, 36.0), (31.5, 31.5)):
        hs = _hex_sdf(cu, cv, bu, bv, 1.9)
        if (bu, bv) == (31.5, 31.5):
            hs = _hex_sdf(cu, cv, bu, bv, 2.0, rot=np.pi / 6)
        ring = corner & (hs > 0) & (hs < 0.8)
        alb = np.where(ring[..., None], alb * 0.55, alb)
        m = corner & (hs < 0)
        h = np.where(m, 5.6 + 0.9 * _smooth(0, 0.9, -hs), h)
        alb = np.where(m[..., None], BRONZE * 1.0, alb)
        spec = np.where(m, 0.8, spec)
        shin = np.where(m, 38.0, shin)

    # gear ring
    gc = 19.0
    r = np.sqrt((cu - gc) ** 2 + (cv - gc) ** 2)
    ang = np.arctan2(cv - gc, cu - gc)
    teeth = 12
    tooth = 0.5 + 0.5 * np.tanh(4.0 * np.cos(teeth * (ang - np.pi / teeth / 2)))   # square-ish teeth
    Rout = 14.4 + 2.4 * tooth
    gear = corner & (r < Rout) & (r > 9.6)
    shade_g = corner & (r >= Rout) & (r < Rout + 1.2) & cp
    alb = np.where(shade_g[..., None], alb * 0.6, alb)
    hg = 6.4 + 1.0 * _smooth(9.6, 10.8, r) * _smooth(Rout, Rout - 1.2, r)
    groove_g = np.abs(r - 12.2) < 0.4
    hg = np.where(groove_g, hg - 0.5, hg)
    h = np.where(gear, hg, h)
    alb = np.where(gear[..., None], cbron * np.where(groove_g, 0.6, 1.0)[..., None], alb)
    spec = np.where(gear, 0.85, spec)
    shin = np.where(gear, 40.0, shin)
    alpha = np.where(gear, 1.0, alpha)

    # recessed well with three broken cyan arcs
    well = corner & (r <= 9.6)
    h = np.where(well, 4.8, h)
    alb = np.where(well[..., None], CAP * (1 + 0.08 * cn)[..., None], alb)
    spec = np.where(well, 0.2, spec)
    arcgap = np.cos(3 * (ang + 0.35))
    arc = well & (np.abs(r - 8.0) < 1.6)
    arcI = np.exp(-((r - 8.0) / 0.55) ** 2) * _smooth(0.55, 0.85, arcgap)
    emit = emit + GLOW * (0.75 * arcI * arc)[..., None]

    # hex cap with glowing core
    hs = _hex_sdf(cu, cv, gc, gc, 6.2, rot=np.pi / 12)
    capm = corner & (hs < 0)
    capsh = corner & well & (hs >= 0) & (hs < 1.0)
    alb = np.where(capsh[..., None], alb * 0.5, alb)
    h = np.where(capm, 5.8 + 1.4 * _smooth(0, 1.4, -hs), h)
    alb = np.where(capm[..., None], DARKBR * (1 + 0.06 * cn)[..., None], alb)
    spec = np.where(capm, 0.7, spec)
    shin = np.where(capm, 36.0, shin)
    cr = np.sqrt((cu - gc) ** 2 + (cv - gc) ** 2)
    lens = corner & (cr < 3.0)
    h = np.where(lens, 7.0 + 1.2 * np.sqrt(np.clip(1 - (cr / 3.0) ** 2, 0, 1)), h)
    alb = np.where(lens[..., None], np.array([0.05, 0.30, 0.34]), alb)
    spec = np.where(lens, 1.2, spec)
    shin = np.where(lens, 60.0, shin)
    gr2 = (cu - gc - 0.6) ** 2 + (cv - gc - 0.6) ** 2
    glow = 0.85 * np.exp(-gr2 / 3.2) * lens + 0.10 * np.exp(-(cr - 3.0) ** 2 / 2.0) * capm
    emit = emit + GLOW * glow[..., None]

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
    ai = Image.fromarray((alpha * 255).astype(np.uint8))
    ring = np.asarray(ai.filter(ImageFilter.MaxFilter(3)), dtype=np.float64) / 255
    a = np.maximum(alpha, ring)
    col = col * (alpha / np.maximum(a, 1e-6))[..., None] + np.array([0.02, 0.03, 0.03]) * ((a - alpha) / np.maximum(a, 1e-6))[..., None]
    sh = np.zeros_like(a)
    sh[3:, 3:] = a[:-3, :-3]
    sha = np.asarray(Image.fromarray((sh * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3)),
                     dtype=np.float64) / 255 * 0.5
    out_a = a + sha * (1 - a)
    out_rgb = col * (a / np.maximum(out_a, 1e-6))[..., None]
    rgba = np.dstack([out_rgb * out_a[..., None], out_a])
    rgba = rgba.reshape(SIZE, SS, SIZE, SS, 4).mean(axis=(1, 3))
    A = rgba[..., 3:4]
    rgb = np.where(A > 1e-6, rgba[..., :3] / np.maximum(A, 1e-6), 0)
    img = np.clip(np.dstack([rgb, A]) * 255 + 0.5, 0, 255)
    c = img[SLICE:SIZE - SLICE, SLICE:SIZE - SLICE]
    c[..., 3] = np.where(c[..., 3] < 3, 0, c[..., 3])
    return Image.fromarray(img.astype(np.uint8), "RGBA")
