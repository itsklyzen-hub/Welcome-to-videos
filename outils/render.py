#!/usr/bin/env python3
"""Welcome to Italie - frame renderer. Usage: render.py OUT_RAW_PIPE_CMD
Writes raw RGB24 frames to stdout (1080x1920, 30 fps)."""
import sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

PH = '/tmp/claude-0/-home-claude/d203c4f7-bb80-582c-b7e8-064d5a4b8978/scratchpad/photos_italie'
FONT = '/usr/share/fonts/opentype/inter/Inter-Black.otf'
W, H, FPS, DUR = 1080, 1920, 30, 20.0
NF = int(DUR * FPS)
K = 1.25  # base supersampling (cover image is 1350x2400)
BEAT = 0.5
DROP = 8.0
END_POP = 17.5
HALF = 0.2  # transitions span cut +/- 0.2 s (0.4 s)

# ---------------- timeline ----------------
# (image, start, end, move)
CUTS = [3.0, 5.0, 6.5, 8.0, 9.5, 10.5, 11.5, 12.5, 13.5, 14.5, 15.5, 16.5]
TRANS = ['dots', 'vbars', 'hbars', 'drop', 'dots', 'vbars', 'hbars', 'dots', 'vbars', 'hbars', 'dots', 'vbars']
ORDER = list(range(1, 14))
NCLIP = len(ORDER)
bounds = [0.0] + CUTS + [DUR]
MOVES = [
    dict(name='push in', z=(1.04, 1.30)),                                  # 01 Colosseum intro
    dict(name='tilt up', z=(1.30, 1.30), dy=(185, -185)),                  # 02
    dict(name='pan right', z=(1.30, 1.30), dx=(105, -105)),                # 03
    dict(name='orbit CW', z=(1.20, 1.30), r=(-3, 3)),                      # 04
    dict(name='drop fast push-in (ease-out)', z=(1.10, 1.45), ease='out'),  # 05 drop
    dict(name='slow orbit CCW', z=(1.22, 1.28), r=(3, -3)),                # 06 pizza
    dict(name='tilt down', z=(1.30, 1.30), dy=(-185, 185)),                # 07
    dict(name='pan left + roll', z=(1.34, 1.34), dx=(-100, 100), r=(-1.5, 1.5)),  # 08
    dict(name='pull back', z=(1.45, 1.05)),                                # 09
    dict(name='pan right (landscape, modest zoom)', z=(1.25, 1.25), dx=(95, -95)),  # 10
    dict(name='push in', z=(1.00, 1.35)),                                  # 11 pizza
    dict(name='tilt up', z=(1.30, 1.30), dy=(185, -185)),                  # 12
    dict(name='pull back (landscape, modest zoom)', z=(1.30, 1.04)),       # 13 ending
]


def clip_window(i):
    """visible interval of clip i (including transition overlap)."""
    s = bounds[i] - (HALF if i > 0 else 0)
    if i > 0 and TRANS[i - 1] == 'drop':
        s = bounds[i]  # move starts at the drop; arrival phase frozen at p=0
    e = bounds[i + 1] + (HALF if i < NCLIP - 1 else 0)
    return s, e


# ---------------- images ----------------
def load_cover(path):
    im = Image.open(path).convert('RGB')
    w, h = im.size
    tw, th = int(W * K), int(H * K)
    sc = max(tw / w, th / h)
    nw, nh = round(w * sc), round(h * sc)
    im = im.resize((nw, nh), Image.LANCZOS)
    l, t = (nw - tw) // 2, (nh - th) // 2
    return im.crop((l, t, l + tw, t + th))


IMGS = [load_cover(f'{PH}/{i:02d}.jpg') for i in ORDER]


def lerp(a, b, p):
    return a + (b - a) * p


def cam_params(i, t):
    mv = MOVES[i]
    s, e = clip_window(i)
    p = min(1.0, max(0.0, (t - s) / (e - s)))
    if mv.get('ease') == 'out':
        p = 1 - (1 - p) ** 3
    z = lerp(*mv['z'], p)
    dx = lerp(*mv.get('dx', (0, 0)), p)
    dy = lerp(*mv.get('dy', (0, 0)), p)
    r = lerp(*mv.get('r', (0, 0)), p)
    return z, dx, dy, r


def beat_punch(t):
    if t < DROP + BEAT - 1e-6:
        return 1.0
    b = math.floor((t + 1e-6) / BEAT) * BEAT
    if b < DROP + BEAT - 1e-6:
        return 1.0
    dt = t - b
    return 1.0 + 0.035 * math.exp(-dt / 0.09)


def shake(t):
    if DROP <= t < DROP + 0.4:
        a = 16 * (1 - (t - DROP) / 0.4) ** 2
        return a * math.sin(t * 97.0), a * math.cos(t * 83.0)
    return 0.0, 0.0


def render_cam(img, z, dx, dy, rdeg):
    th = math.radians(rdeg)
    c, s = math.cos(th), abs(math.sin(th))
    # keep edges hidden
    zmin = max((540 * c + 960 * s) / 540, (960 * c + 540 * s) / 960) * 1.003
    z = max(z, zmin)
    hx = (540 * c + 960 * s) / z
    hy = (960 * c + 540 * s) / z
    mx, my = 540 - hx, 960 - hy
    dx = max(-mx, min(mx, dx))
    dy = max(-my, min(my, dy))
    cs, sn = math.cos(th), math.sin(th)
    a, b = K * cs / z, K * sn / z
    d, e = -K * sn / z, K * cs / z
    cx, cy = img.size[0] / 2, img.size[1] / 2
    cc = cx + K * dx - a * 540 - b * 960
    ff = cy + K * dy - d * 540 - e * 960
    return img.transform((W, H), Image.AFFINE, (a, b, cc, d, e, ff), resample=Image.BICUBIC)


def clip_frame(i, t):
    z, dx, dy, r = cam_params(i, t)
    z *= beat_punch(t)
    sx, sy = shake(t)
    return render_cam(IMGS[i], z, dx + sx, dy + sy, r)


# ---------------- text ----------------
FLAG = [(0x00, 0x8C, 0x45), (0xF4, 0xF5, 0xF0), (0xCD, 0x21, 0x2A)]  # Italian flag, equal thirds


def text_sprite(txt, size, stroke, flag):
    f = ImageFont.truetype(FONT, size)
    pad = stroke + 20
    bb = f.getbbox(txt)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    sw, sh = tw + 2 * pad, th + 2 * pad
    org = (pad - bb[0], pad - bb[1])
    outline = Image.new('L', (sw, sh), 0)
    ImageDraw.Draw(outline).text(org, txt, font=f, fill=255, stroke_width=stroke, stroke_fill=255)
    fillm = Image.new('L', (sw, sh), 0)
    ImageDraw.Draw(fillm).text(org, txt, font=f, fill=255)
    # soft drop shadow
    rgba = np.zeros((sh, sw, 4), np.float32)
    col = np.zeros((sh, sw, 3), np.float32)
    if flag:
        a1, a2 = pad + round(tw / 3), pad + round(2 * tw / 3)
        col[:, :a1] = FLAG[0]
        col[:, a1:a2] = FLAG[1]
        col[:, a2:] = FLAG[2]
    else:
        col[:] = 255
    fm = np.asarray(fillm, np.float32)[..., None] / 255
    om = np.asarray(outline, np.float32)[..., None] / 255
    rgb = col * fm  # black stroke elsewhere
    rgba[..., :3] = rgb
    rgba[..., 3] = np.maximum(om[..., 0], fm[..., 0]) * 255
    return Image.fromarray(rgba.astype(np.uint8), 'RGBA')


def fit_size(txt, maxw, stroke):
    for size in range(220, 40, -2):
        f = ImageFont.truetype(FONT, size)
        bb = f.getbbox(txt)
        if bb[2] - bb[0] + 2 * stroke <= maxw:
            return size
    return 40


S_REF = fit_size('PORTUGAL', 820, 14)  # keep WELCOME TO identical to the Portugal template
S_PT = min(fit_size('ITALIE', 820, 14), int(S_REF * 1.25))
SPR_PT = text_sprite('ITALIE', S_PT, 14, True)
S_WT = int(S_REF * 0.62)
SPR_WT = text_sprite('WELCOME TO', S_WT, 12, False)
TEXT_CX = 500  # centre of usable width (0..940 safe)


def ease_out_back(p, k=2.2):
    p = min(1, max(0, p))
    return 1 + (k + 1) * (p - 1) ** 3 + k * (p - 1) ** 2


def pop_scale(t, t0, d=0.32):
    if t < t0:
        return 0.0
    return max(0.0, ease_out_back((t - t0) / d))


def paste_sprite(frame, spr, scale, cx, cy):
    if scale <= 0.02:
        return
    w, h = spr.size
    nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
    s = spr.resize((nw, nh), Image.BICUBIC)
    frame.paste(s, (int(cx - nw / 2), int(cy - nh / 2)), s)


def flash(arr, alpha):
    if alpha > 0.003:
        arr[:] = arr * (1 - alpha) + 255 * alpha


# ---------------- transitions ----------------
DOT_CELL = 72
DOT_CENTERS = []
for row in range(-1, H // DOT_CELL + 2):
    off = (DOT_CELL / 2) if row % 2 else 0
    for col in range(-1, W // DOT_CELL + 2):
        DOT_CENTERS.append((col * DOT_CELL + off, row * DOT_CELL))
DMAX = max(0.45 * x + y for x, y in DOT_CENTERS)


def mask_dots(q):
    m = Image.new('L', (W, H), 0)
    dr = ImageDraw.Draw(m)
    for x, y in DOT_CENTERS:
        d = max(0, (0.45 * x + y) / DMAX)
        loc = min(1, max(0, (q - 0.55 * d) / 0.45))
        r = 50 * (1 - (1 - loc) ** 2)
        if r > 0.6:
            dr.ellipse((x - r, y - r, x + r, y + r), fill=255)
    return m


def mask_vbars(q, n=9):
    m = np.zeros((H, W), np.uint8)
    bw = W / n
    for i in range(n):
        loc = min(1, max(0, (q - 0.07 * i) / (1 - 0.07 * (n - 1))))
        loc = 1 - (1 - loc) ** 2
        hgt = int(round(loc * H))
        x0, x1 = int(round(i * bw)), int(round((i + 1) * bw))
        if i % 2 == 0:
            m[:hgt, x0:x1] = 255
        else:
            m[H - hgt:, x0:x1] = 255
    return Image.fromarray(m)


def mask_hbars(q, n=14):
    m = np.zeros((H, W), np.uint8)
    bh = H / n
    for i in range(n):
        loc = min(1, max(0, (q - 0.04 * i) / (1 - 0.04 * (n - 1))))
        loc = 1 - (1 - loc) ** 2
        wid = int(round(loc * W))
        y0, y1 = int(round(i * bh)), int(round((i + 1) * bh))
        if i % 2 == 0:
            m[y0:y1, :wid] = 255
        else:
            m[y0:y1, W - wid:] = 255
    return Image.fromarray(m)


def overlay_text(frame, t, i):
    """text belongs to the image layer (gets wiped by transitions)."""
    if i == 0:
        paste_sprite(frame, SPR_WT, pop_scale(t, 0.5), TEXT_CX, 560)
        paste_sprite(frame, SPR_PT, pop_scale(t, 1.5), TEXT_CX, 560 + SPR_WT.size[1] * 0.5 + SPR_PT.size[1] * 0.5 - 30)
    if i == NCLIP - 1:
        paste_sprite(frame, SPR_PT, pop_scale(t, END_POP), TEXT_CX, 640)


def layer(i, t):
    f = clip_frame(i, t)
    overlay_text(f, t, i)
    return f


def frame_at(t):
    # which cut are we near?
    for ci, c in enumerate(CUTS):
        kind = TRANS[ci]
        if kind == 'drop':
            if c - 0.35 <= t < c:
                a = layer(ci, t)
                arr = np.asarray(a, np.float32) * (1 - 0.35 * (t - (c - 0.35)) / 0.35)
                a = Image.fromarray(arr.astype(np.uint8))
                b = layer(ci + 1, t)
                p = (t - (c - 0.35)) / 0.35
                sc = 0.22 + 0.78 * p ** 2.2
                bw, bh = int(W * sc), int(H * sc)
                a.paste(b.resize((bw, bh), Image.BILINEAR), ((W - bw) // 2, (H - bh) // 2))
                return a
            continue
        if c - HALF <= t < c + HALF:
            q = (t - (c - HALF)) / (2 * HALF)
            a, b = layer(ci, t), layer(ci + 1, t)
            m = {'dots': mask_dots, 'vbars': mask_vbars, 'hbars': mask_hbars}[kind](q)
            return Image.composite(b, a, m)
    idx = max(i for i in range(NCLIP) if bounds[i] <= t + 1e-9)
    return layer(idx, t)


def post(img, t):
    arr = np.asarray(img, np.float32).copy()
    # flashes: PORTUGAL pops and drop
    for t0, amp, dec in ((1.5, 0.55, 0.12), (END_POP, 0.55, 0.12), (DROP, 0.9, 0.22)):
        if t0 <= t < t0 + 0.5:
            flash(arr, amp * math.exp(-(t - t0) / dec))
    # loop darkening
    if t > DUR - 0.6:
        k = (t - (DUR - 0.6)) / 0.6
        arr *= 1 - 0.55 * k
    return np.clip(arr, 0, 255).astype(np.uint8)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'still':
        for ts in sys.argv[2:]:
            t = float(ts)
            Image.fromarray(post(frame_at(t), t)).save(f'still_{t:05.2f}.png')
        sys.exit()
    out = sys.stdout.buffer
    for n in range(NF):
        t = n / FPS
        out.write(post(frame_at(t), t).tobytes())
        if n % 60 == 0:
            print(f'frame {n}/{NF}', file=sys.stderr)
