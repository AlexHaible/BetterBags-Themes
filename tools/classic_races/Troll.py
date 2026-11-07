"""Troll (Darkspear) classic border: lashed driftwood poles, teal-dyed leather bindings with
small bone tusks, worn red-ochre paint, and a carved tiki/loa mask with tusks at each corner.
Echo Isles / Sen'jin: weathered wood, bone, turquoise and ochre, no gold, no stone."""
import os

import numpy as np
from PIL import Image

_T = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "textures")
CREST = os.path.join(_T, "TrollCrest.png")

THEME = dict(
    Name="RacesTroll", Background="SOLID", BackgroundInset=8,
    Color=(0.02, 0.12, 0.12, 0.72), Slice=48, Outset=24, TitleY=24, Close={"X": 22, "Y": 22},
    Search=("TOPRIGHT", -22, -2), Menu={"X": -24, "Y": 24},
    TabEdge=(0.33, 0.26, 0.19, 1), TabAccent=(0.2, 0.6, 0.56, 1),
)

N = 256          # texture size
S = 48           # slice margin
SS = 4           # supersampling
P = N - 2 * S    # edge repeat (160)
C = 22.0         # pole centre line, from the outer edge
R = 6.3          # pole radius
LIGHT = np.array([-0.55, -0.62, 0.58])
LIGHT = LIGHT / np.linalg.norm(LIGHT)

WOOD_D = np.array([78, 58, 42], np.float32)
WOOD_L = np.array([150, 128, 102], np.float32)
TEAL = np.array([40, 128, 122], np.float32)
TEAL_D = np.array([18, 62, 64], np.float32)
OCHRE = np.array([158, 58, 36], np.float32)
BONE = np.array([226, 214, 184], np.float32)
BONE_D = np.array([150, 132, 100], np.float32)
MASKW = np.array([104, 70, 44], np.float32)
TURQ = np.array([64, 200, 190], np.float32)


# ------------------------------------------------------------------ helpers
def sstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def cover(d):
    """Signed distance (1x px, negative inside) -> anti-aliased coverage at SS."""
    return np.clip(0.5 - d * SS, 0, 1)


def pblur(a, sy, sx):
    """Periodic gaussian blur via FFT (sigmas in array pixels)."""
    fy = np.fft.fftfreq(a.shape[0])[:, None]
    fx = np.fft.fftfreq(a.shape[1])[None, :]
    g = np.exp(-2 * (np.pi ** 2) * ((fy * sy) ** 2 + (fx * sx) ** 2))
    return np.real(np.fft.ifft2(np.fft.fft2(a) * g))


def norm01(a):
    a = a - a.mean()
    return a / (np.abs(a).max() + 1e-6)


def shade(h, albedo, spec=0.15, amb=0.42, gain=0.8):
    gy, gx = np.gradient(h * SS)  # h in 1x px, grid at SS -> slope per 1x px
    n = np.stack([-gx, -gy, np.ones_like(h)], -1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    ndl = np.clip((n * LIGHT).sum(-1), 0, 1)
    hv = LIGHT + np.array([0, 0, 1.0])
    hv /= np.linalg.norm(hv)
    sp = np.clip((n * hv).sum(-1), 0, 1) ** 24 * spec
    rgb = albedo * (amb + gain * ndl)[..., None] + 255 * sp[..., None]
    return np.clip(rgb, 0, 255)


class Canvas:
    def __init__(self):
        self.rgb = np.zeros((N * SS, N * SS, 3), np.float32)
        self.a = np.zeros((N * SS, N * SS), np.float32)
        g = (np.arange(N * SS) + 0.5) / SS
        self.X, self.Y = np.meshgrid(g, g)

    def over(self, rgb, a, y0=0, x0=0):
        h, w = a.shape
        sl = (slice(y0, y0 + h), slice(x0, x0 + w))
        da = self.a[sl]
        oa = a + da * (1 - a)
        self.rgb[sl] = (rgb * a[..., None] + self.rgb[sl] * (da * (1 - a))[..., None]) / np.maximum(oa, 1e-6)[..., None]
        self.a[sl] = oa

    def shadow(self, a, dx=1.6, dy=2.0, blur=1.6, op=0.55, y0=0, x0=0):
        full = np.zeros_like(self.a)
        h, w = a.shape
        full[y0:y0 + h, x0:x0 + w] = a
        sy, sx = int(dy * SS), int(dx * SS)
        sh = np.zeros_like(full)
        sh[sy:, sx:] = full[:full.shape[0] - sy, :full.shape[1] - sx]
        full = sh
        full = pblur(full, blur * SS, blur * SS)
        self.over(np.zeros(full.shape + (3,), np.float32), np.clip(full, 0, 1) * op)

    def image(self):
        pm = np.concatenate([self.rgb * self.a[..., None], self.a[..., None]], -1)
        pm = pm.reshape(N, SS, N, SS, 4).mean((1, 3))
        a = pm[..., 3:4]
        rgb = np.where(a > 0, pm[..., :3] / np.maximum(a, 1e-6), 0)
        return Image.fromarray(np.clip(np.concatenate([rgb, a * 255], -1) + 0.5, 0, 255).astype(np.uint8), "RGBA")


# ------------------------------------------------------------------ edge pole
def pole_strip(seed, length=N):
    """Horizontal driftwood pole, `length` long, H tall at SS, periodic in P along x with phase
    0 at x = S. Returns rgb, alpha, height (for shadows)."""
    rng = np.random.default_rng(seed)
    H = 2 * int(C)
    Hs, Ls, Ps = H * SS, length * SS, P * SS
    u = (np.arange(Ls) + 0.5) / SS              # x in texture px
    v = (np.arange(Hs) + 0.5) / SS - C          # across, 0 = centre
    U, V = np.meshgrid(u, v)
    ph = (U - S) % P                             # phase along the repeat
    pidx = ((np.arange(Ls) - S * SS) % Ps)

    def pnoise(sy, sx, rows=Hs):
        n = pblur(rng.standard_normal((rows, Ps)), sy, sx)
        return norm01(n)[:, pidx]

    # silhouette wobble (driftwood is never round)
    wob = pnoise(0.1, 18 * SS, rows=1)[0]
    rad = R + 0.55 * wob[None, :]
    # lashing band in the middle of the repeat
    lc = P / 2
    du = ph - lc
    band = sstep(6.4, 5.4, np.abs(du))
    rad_l = rad + 1.3 * band
    d = np.abs(V) - rad_l
    alpha = cover(d)
    vv = np.clip(V / rad_l, -1, 1)
    h = rad_l * np.sqrt(1 - vv ** 2)

    # wood grain: long streaks, worn grey on top
    g1 = pnoise(0.7 * SS, 22 * SS)
    g2 = pnoise(0.35 * SS, 5 * SS)
    crack = sstep(0.62, 0.8, pnoise(0.25 * SS, 30 * SS))
    t = np.clip(0.5 + 0.45 * g1 + 0.3 * g2 - 0.2 * vv, 0, 1)
    wood = WOOD_D + (WOOD_L - WOOD_D) * t[..., None]
    wood *= (1 - 0.45 * crack)[..., None]
    h = h - 0.6 * crack + 0.25 * g2

    # worn red-ochre rings painted either side of the lashing
    ring = sstep(1.5, 0.8, np.abs(np.abs(du) - 21.5))
    wear = sstep(-0.45, 0.1, pnoise(0.8 * SS, 2 * SS))
    pa = (ring * wear * 0.9)[..., None]
    wood = wood * (1 - pa) + OCHRE * pa

    # teal leather lashing, diagonal wraps
    tt = (du + 0.55 * V) / 2.6
    fr = tt - np.floor(tt)
    bump = np.sin(np.pi * fr)
    leather = TEAL_D + (TEAL - TEAL_D) * (0.35 + 0.65 * bump)[..., None]
    bm = band[..., None]
    alb = wood * (1 - bm) + leather * bm
    h = h + band * (0.9 * bump)

    rgb = shade(h, alb, spec=0.12)
    return rgb, alpha, h, U, V, ph


def tusk_field(X, Y, pts, r0, r1):
    """Distance to a tapered stroke through pts (list of (x, y)), radius r0 -> r1."""
    pts = np.asarray(pts, np.float32)
    # densify
    seg = []
    for i in range(len(pts) - 1):
        for t in np.linspace(0, 1, 12, endpoint=False):
            seg.append(pts[i] * (1 - t) + pts[i + 1] * t)
    seg.append(pts[-1])
    seg = np.array(seg)
    k = np.linspace(0, 1, len(seg))
    rads = r0 + (r1 - r0) * k ** 1.3
    d = np.full(X.shape, 1e9, np.float32)
    s = np.zeros(X.shape, np.float32)
    for (cx, cy), rr, kk in zip(seg, rads, k):
        di = np.hypot(X - cx, Y - cy) - rr
        m = di < d
        d = np.where(m, di, d)
        s = np.where(m, kk, s)
    return d, s


def bezier(p0, p1, p2, n=10):
    t = np.linspace(0, 1, n)[:, None]
    return ((1 - t) ** 2 * np.array(p0) + 2 * (1 - t) * t * np.array(p1) + t * t * np.array(p2)).tolist()


def add_edge_tusks(rgb, alpha, U, V, ph):
    """Two small bone tusks tied under the lashing, pointing away along the pole."""
    lc = P / 2
    out_rgb, out_a = rgb.copy(), alpha.copy()
    base = None
    for sgn in (-1, 1):
        # local coordinates: x along from lashing centre
        x = (ph - lc) * sgn
        pts = bezier((3.5, 1.0), (11, 1.2), (16.5, -3.6), 8)
        d, s = tusk_field(x, V, pts, 2.3, 0.35)
        a = cover(d)
        hh = np.sqrt(np.clip(1 - (np.clip(d, -3, 0) / -2.3 + 1) ** 2, 0, 1)) * 1.6 + (-d).clip(0, 2.3)
        tone = np.clip(0.75 + 0.25 * (1 - s), 0, 1)
        alb = BONE_D + (BONE - BONE_D) * tone[..., None]
        trgb = shade(hh, alb, spec=0.35, amb=0.5, gain=0.65)
        out_rgb = trgb * a[..., None] + out_rgb * (1 - a[..., None])
        out_a = a + out_a * (1 - a)
        base = a if base is None else np.maximum(base, a)
    # lashing over the tusk roots
    du = ph - lc
    band = sstep(6.4, 5.4, np.abs(du)) * alpha
    keep = band[..., None]
    out_rgb = rgb * keep + out_rgb * (1 - keep)
    out_a = np.maximum(out_a, band)
    return out_rgb, out_a


def end_cap(rgb, alpha, U, V, end_x, side):
    """Cut the pole at end_x (side -1 = keep x > end_x); show end grain on the cut."""
    keep = cover(end_x - U) if side == -1 else cover(U - end_x)
    a = alpha * keep
    # end grain band
    eg = sstep(1.6, 0.4, np.abs(U - end_x)) * a
    rings = 0.5 + 0.5 * np.cos(np.hypot(U - end_x, V) * 2.4)
    endc = np.array([168, 140, 104], np.float32) * (0.75 + 0.25 * rings)[..., None]
    rgb = rgb * (1 - eg[..., None]) + endc * eg[..., None]
    return rgb, a


# ------------------------------------------------------------------ corner mask
def mask_layer(cv, cx, cy):
    X, Y = cv.X, cv.Y
    x, y = X - cx, Y - cy
    a_w, b_h = 12.5, 16.0
    # shield-shaped face: wider brow, tapered chin
    wscale = 1 + 0.12 * np.clip(-y / b_h, -1, 1)
    e = np.hypot(x / (a_w * wscale), (y + 0.5) / b_h)
    d_face = (e - 1) * a_w
    dome = np.sqrt(np.clip(1 - np.clip(e, 0, 1) ** 2, 0, 1)) * 5.0
    # carved headdress: three rounded spikes rising from a headband
    spike_d = np.full(x.shape, 1e9, np.float32)
    spike_h = np.zeros_like(x)
    for xi, tip in ((-6.6, -17.4), (0.0, -19.2), (6.6, -17.4)):
        base = -10.5
        k = np.clip((y - tip) / (base - tip), 0, 1)
        w = 0.4 + 2.5 * np.sqrt(k)
        di = np.maximum(np.maximum(np.abs(x - xi) - w, tip - y), y + 6.0)
        spike_d = np.minimum(spike_d, di)
        spike_h = np.maximum(spike_h, np.clip(1 - np.abs(x - xi) / np.maximum(w, 0.3), 0, 1) * 2.2 * (y > tip) * (y < -6.0))
    spikes = cover(spike_d)
    face = np.maximum(cover(d_face), spikes)
    dome = np.maximum(dome, spike_h * spikes + 2.6 * spikes * (y < -10))

    # headband ridge across the top of the face, set with turquoise beads
    brow = np.exp(-((y + 5.2) / 1.5) ** 2) * sstep(1.0, 0.8, np.abs(x) / (a_w * 1.05))
    band = sstep(1.2, 0.6, np.abs(y + 9.6)) * cover(d_face + 0.3)
    bead_d = np.min([np.hypot(x - bx, y + 9.6) - 1.25 for bx in (-6.4, 0.0, 6.4)], axis=0)
    bead = cover(bead_d)
    crown = band
    # eyes
    eye_d = np.hypot((np.abs(x) - 5.0) / 3.4, (y + 1.2) / 2.0) - 1
    eye = cover(eye_d * 2.0)
    stone_d = np.hypot((np.abs(x) - 5.0) / 2.1, (y + 1.3) / 1.3) - 1
    stone = cover(stone_d * 1.3)
    # nose
    nose = np.exp(-(x / 1.8) ** 2) * sstep(-4.5, -3.0, y) * sstep(4.8, 3.2, y)
    # mouth
    mouth_d = np.maximum(np.abs(x) - 7.2 + 0.08 * (y - 8) ** 2, np.abs(y - 8.3) - 2.6)
    mouth = cover(mouth_d)
    teeth = mouth * (sstep(0.4, 0.1, np.abs(((x + 0.9) / 1.8) % 1 - 0.5))) * sstep(7.2, 6.6, y)
    # carved grooves on cheeks
    groove = np.exp(-((np.abs(x) - 8.3 + 0.25 * y) / 0.7) ** 2) * sstep(1.5, 3.0, y) * sstep(10, 7.5, y)

    h = dome + 1.3 * brow + 1.6 * nose - 2.2 * eye - 2.0 * mouth - 0.8 * groove + 0.9 * crown
    h = h + 1.2 * stone + 1.0 * teeth + 1.0 * bead

    grain = norm01(pblur(np.random.default_rng(5).standard_normal(X.shape), 0.4 * SS, 4 * SS))
    alb = MASKW * (0.85 + 0.25 * grain)[..., None]
    # ochre paint: crown band, cheek stripes under the eyes
    paint = spikes * sstep(-10.6, -11.6, y) * 0.9
    cheek = sstep(0.7, 0.3, np.abs((np.abs(x) - 5.0) % 2.2 - 1.1)) * sstep(1.8, 2.6, y) * sstep(5.6, 4.6, y) \
        * sstep(8.4, 7.4, np.abs(x)) * sstep(2.2, 3.0, np.abs(x))
    paint = np.clip(paint + 0.85 * cheek, 0, 1)
    alb = alb * (1 - paint[..., None]) + OCHRE * paint[..., None]
    alb = alb * (1 - 0.65 * eye[..., None])
    alb = alb * (1 - 0.8 * mouth[..., None])
    alb = alb * (1 - 0.35 * band[..., None])
    alb = alb * (1 - stone[..., None]) + TURQ * stone[..., None]
    alb = alb * (1 - bead[..., None]) + TURQ * 0.85 * bead[..., None]
    alb = alb * (1 - teeth[..., None]) + BONE * teeth[..., None]
    rgb = shade(h, alb, spec=0.18)
    # glossy stone
    rgb = rgb + stone[..., None] * 60 * sstep(0.6, 0.0, np.hypot(np.abs(x) - 5.8, y + 2.0))[..., None]

    # tusks from the mouth corners, sweeping up and out past the cheeks
    tusk_rgb = np.zeros_like(rgb)
    tusk_a = np.zeros_like(face)
    for sgn in (-1, 1):
        xl = x * sgn
        pts = bezier((6.0, 8.6), (13.5, 9.5), (14.8, -1.5), 10)
        d, s = tusk_field(xl, y, pts, 2.2, 0.35)
        a = cover(d)
        hh = (-d).clip(0, 2.2) * 1.2
        alb_t = BONE_D + (BONE - BONE_D) * np.clip(0.7 + 0.3 * (1 - s), 0, 1)[..., None]
        trgb = shade(hh, alb_t, spec=0.4, amb=0.5, gain=0.65)
        tusk_rgb = trgb * a[..., None] + tusk_rgb * (1 - a[..., None])
        tusk_a = a + tusk_a * (1 - a)

    # composite: shadow, face, tusks
    allm = np.maximum(face, tusk_a)
    cv.shadow(allm, 1.8, 2.2, 1.8, 0.6)
    cv.over(rgb, face)
    cv.shadow(tusk_a * (1 - 0.0), 0.8, 1.0, 0.8, 0.35)
    cv.over(tusk_rgb, tusk_a)


# ------------------------------------------------------------------ assembly
def BORDER():
    cv = Canvas()
    Hs = 2 * int(C) * SS
    strips = []
    for k, seed in enumerate((11, 23, 37, 41)):
        rgb, a, h, U, V, ph = pole_strip(seed)
        rgb, a = add_edge_tusks(rgb, a, U, V, ph)
        # cut ends a little beyond the crossing
        rgb, a = end_cap(rgb, a, U, V, 3.0, -1)
        rgb, a = end_cap(rgb, a, U, V, N - 3.0, 1)
        strips.append((rgb, a))

    def full(rgb, a, transpose, offset):
        R3 = np.zeros((N * SS, N * SS, 3), np.float32)
        A = np.zeros((N * SS, N * SS), np.float32)
        if transpose:
            rgb, a = rgb.transpose(1, 0, 2), a.T
            R3[:, offset:offset + Hs] = rgb
            A[:, offset:offset + Hs] = a
        else:
            R3[offset:offset + Hs] = rgb
            A[offset:offset + Hs] = a
        return R3, A

    lo = 0
    hi = (N - 2 * int(C)) * SS
    layers = [full(*strips[0], True, lo), full(*strips[1], True, hi),
              full(*strips[2], False, lo), full(*strips[3], False, hi)]
    # vertical poles first, horizontal over them
    for R3, A in layers[:2]:
        cv.shadow(A, 1.4, 1.8, 1.4, 0.5)
        cv.over(R3, A)
    for R3, A in layers[2:]:
        cv.shadow(A, 1.4, 1.8, 1.4, 0.5)
        cv.over(R3, A)

    for cx, cy in ((C + 1, C + 0.5), (N - C - 1, C + 0.5), (C + 1, N - C + 0.5), (N - C - 1, N - C + 0.5)):
        mask_layer(cv, cx, cy)

    img = cv.image()
    # centre must be transparent
    arr = np.array(img)
    arr[S:N - S, S:N - S] = 0
    return Image.fromarray(arr, "RGBA")
