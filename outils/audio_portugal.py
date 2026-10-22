#!/usr/bin/env python3
"""Original 'Portuguese' track for Welcome to Portugal v7 (120 BPM, 19 s, E minor i-VI-iv-V7).
Everything is synthesized with numpy/scipy: no samples, no existing melody (no fado standard quoted).
- Intro 0-3 s : soft string pad, sparse Portuguese-guitar arpeggio, intro hits.
- Build 3-8 s : fado feel -> Portuguese guitar (bright Karplus-Strong, doubled metal courses +/-6 cents)
                16th-note arpeggios + original melody (tremolo on long notes), nylon bass on the beats,
                almost no percussion, snare roll + riser, gap before the drop.
- Drop 8 s    : boom + same melody doubled an octave up over kick / clap / hats / shaker / bass.
- Whoosh on every cut, ending hit at 16.5 s, fade at 19 s.
Usage: audio_portugal.py out.wav
"""
import sys, wave
import numpy as np
from scipy.signal import butter, lfilter

SR = 44100
DUR = 19.0
N = int(SR * DUR)
BEAT = 0.5
BAR = 2.0
DROP = 8.0
CUTS = [3.0, 5.0, 6.5, 8.0, 9.5, 10.5, 11.5, 12.5, 13.5, 14.5, 15.5]
END_HIT = 16.5
rng = np.random.default_rng(23)
L = np.zeros(N); R = np.zeros(N)
tt = np.arange(N) / SR


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def _f(kind, f, order=2):
    return butter(order, np.array(f) / (SR / 2), btype=kind)


def lp(x, fc, o=2): return lfilter(*_f('low', fc, o), x)
def hp(x, fc, o=2): return lfilter(*_f('high', fc, o), x)
def bp(x, lo, hi, o=2): return lfilter(*_f('band', [lo, hi], o), x)
def tvec(d): return np.arange(int(d * SR)) / SR


def add(sig, t0, gain=1.0, pan=0.0):
    i0 = int(round(t0 * SR))
    if i0 >= N:
        return
    if i0 < 0:
        sig = sig[-i0:]; i0 = 0
    n = min(len(sig), N - i0)
    L[i0:i0 + n] += sig[:n] * gain * np.sqrt(1 - pan)
    R[i0:i0 + n] += sig[:n] * gain * np.sqrt(1 + pan)


# E minor: i - VI - iv - V7 (Em - C - Am - B7), one chord per bar (2 s). t=8.0 (drop) lands on Em.
CHORDS = [[52, 59, 64, 67, 71], [48, 55, 64, 67, 72], [45, 52, 60, 64, 69], [47, 54, 63, 69, 71]]
ROOTS = [40, 36, 45, 35]  # E2, C2, A2, B1


def bar_idx(t):
    return int(t // BAR) % 4



# ---------------- Portuguese guitar (Karplus-Strong) ----------------
def ks(freq, dur, bright=0.6, decay=0.996):
    n = int(dur * SR)
    P = max(2, int(round(SR / freq - 0.5)))
    y = np.zeros(n + P + 1)
    exc = rng.uniform(-1, 1, P + 1)
    exc = bright * exc + (1 - bright) * lp(exc, 2500)  # pick brightness
    y[:P + 1] = exc
    s = P + 1
    while s < len(y):
        e = min(s + P, len(y))
        y[s:e] = decay * 0.5 * (y[s - P:e - P] + y[s - P - 1:e - P - 1])
        s = e
    out = y[:n]
    return out * np.minimum(1, np.arange(n) / 30)



def pg_pluck(m, ring=0.9, gain=1.0, bright=0.85):
    """Portuguese guitar: doubled metal courses (+/-6 cents), bright, long ring."""
    s = 0
    for det in (-6, 6):
        p = ks(mtof(m) * 2 ** (det / 1200), ring, bright=bright, decay=0.997)
        s = s + p * 0.5
    s = s * np.exp(-np.arange(len(s)) / SR / (ring * 0.55))
    return hp(s, 150) * gain


def pg_note(m, dur, gain=1.0):
    """melody note: single pluck if short, fado-style tremolo (16/s) if >= 1 beat."""
    sig = np.zeros(int((dur + 0.6) * SR))
    if dur < BEAT - 1e-6:
        p = pg_pluck(m, dur + 0.5, 1.0)
        sig[:len(p)] += p[:len(sig)]
    else:
        t, k = 0.0, 0
        while t < dur - 1e-6:
            p = pg_pluck(m, 0.3, 1.0 if k % 2 == 0 else 0.7)
            i0 = int(t * SR); sig[i0:i0 + len(p)] += p[:len(sig) - i0]
            t += BEAT / 8; k += 1
    return sig * gain


def nylon(m, dur, gain):
    p = ks(mtof(m), dur, bright=0.25, decay=0.998)
    return lp(p * np.exp(-np.arange(len(p)) / SR / 0.6), 1500) * gain


def bar_idx(t):
    return int(t // BAR) % 4


# original melody, E harmonic minor (D#), (midi, beats) per bar, follows Em - C - Am - B7
PHRASE = [
    [(83, 1), (81, .5), (79, .5), (78, .5), (79, .5), (76, 1)],       # Em
    [(79, 1), (84, .5), (83, .5), (81, .5), (79, .5), (76, 1)],           # C
    [(81, .5), (84, .5), (88, 1), (86, .5), (84, .5), (81, 1)],           # Am
    [(83, .5), (87, .5), (90, 1), (88, .5), (87, .5), (83, 1)],           # B7
]
mel = np.zeros(N)
for bar in range(int(DUR / BAR) + 1):
    t = bar * BAR
    for m, beats in PHRASE[bar % 4]:
        d = beats * BEAT
        if 3.0 <= t < 7.875:
            s = pg_note(m, min(d, 7.875 - t), 0.75 + 0.35 * (t - 3.0) / 5.0)
        elif DROP <= t < DUR - 0.6:
            s = pg_note(m, d, 0.95) + pg_note(m + 12, d, 0.30)
        else:
            s = None
        if s is not None:
            i0 = int(t * SR); n = min(len(s), N - i0)
            mel[i0:i0 + n] += s[:n]
        t += d
mL = mel.copy(); mR = mel.copy()
d1, d2 = int(0.027 * SR), int(0.044 * SR)
mL[d1:] += 0.35 * mel[:-d1]; mR[d2:] += 0.35 * mel[:-d2]
L += mL * 0.95; R += mR * 0.95

# 16th-note arpeggio (accompanying Portuguese guitar), sparse in the intro
ARP = [0, 2, 3, 4, 3, 2, 1, 2]
arp = np.zeros(N)
t, k = 0.0, 0
while t < DUR - 0.6:
    if 7.875 <= t < DROP:
        t += BEAT / 4; k += 1; continue
    ch = CHORDS[bar_idx(t)]
    if t < 3.0:
        play = k % 2 == 0          # 8ths in the intro
        g = 0.30 + 0.15 * t / 3.0
    elif t < DROP:
        play = True
        g = 0.48 + 0.12 * (t - 3.0) / 5.0
    else:
        play = True
        g = 0.30
    if play:
        s = pg_pluck(ch[ARP[k % 8]] + 12, 0.45, g * (1.0 if k % 4 == 0 else 0.75), bright=0.7)
        i0 = int(t * SR); n = min(len(s), N - i0)
        arp[i0:i0 + n] += s[:n]
    t += BEAT / 4; k += 1
add(arp, 0, 1.0, 0.3)
add(np.roll(arp, int(0.18 * SR)) * 0.18, 0, 1.0, -0.4)   # small echo

# nylon bass on the beats during the build (fado 'baixo')
t = 3.0
while t < 7.875:
    b = bar_idx(t)
    m = ROOTS[b] + (12 if int(t / BEAT) % 2 == 0 else 19)  # root / fifth alternation
    add(nylon(m, 0.5, 0.55), t, 1.0, -0.1)
    t += BEAT


# ---------------- soft string pad ----------------
def strings(freqs, dur):
    t = tvec(dur)
    s = np.zeros_like(t)
    for f in freqs:
        for det in (-7, 0, 7):
            ff = f * 2 ** (det / 1200)
            s += 2 * ((ff * t + rng.random()) % 1) - 1
    return lp(s, 900, 2)


pad = np.zeros(N)
for bar in range(int(DUR / BAR) + 1):
    t0 = bar * BAR
    d = 2.3
    t = tvec(d)
    env = np.minimum(1, t / 0.4) * np.clip((d - t) / 0.4, 0, 1)
    s = strings([mtof(m) for m in CHORDS[bar % 4][1:4]], d) * env
    i0 = int(t0 * SR); n = min(len(s), N - i0)
    pad[i0:i0 + n] += s[:n]
padg = np.where(tt < DROP, 0.045, 0.022)
add(pad * padg, 0, 1.0, -0.25)
add(np.roll(pad * padg, int(0.013 * SR)), 0, 1.0, 0.25)


# ---------------- intro / ending hits ----------------
def impact(strength=1.0, dur=0.9):
    d = tvec(dur)
    f = 90 * np.exp(-d * 6) + 40
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-d / 0.35)
    nz = lp(rng.standard_normal(len(d)), 2500) * np.exp(-d / 0.06)
    cr = hp(rng.standard_normal(len(d)), 5000) * np.exp(-d / 0.4) * 0.25
    return strength * (0.8 * body + 0.35 * nz + cr)


add(impact(0.45), 0.5)
add(impact(0.65), 1.5)
add(impact(0.6), END_HIT)


# ---------------- snare roll + riser into the drop ----------------
def snare(g):
    d = tvec(0.15)
    return g * (bp(rng.standard_normal(len(d)), 1200, 7000) * np.exp(-d / 0.05)
                + 0.5 * np.sin(2 * np.pi * 190 * d) * np.exp(-d / 0.04))


t = 6.0
while t < 7.875:
    step = 0.25 if t < 7.0 else (0.125 if t < 7.5 else 0.0625)
    add(snare(0.12 + 0.3 * (t - 6.0) / 1.875), t)
    t += step
d = tvec(2.875)  # 5.0 -> 7.875
x = d / d[-1]
f = 220 * (6 ** x)
add(np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.05 * x ** 2
    + hp(rng.standard_normal(len(d)), 1800) * 0.12 * x ** 2.2, 5.0)

# ---------------- drop boom ----------------
d = tvec(1.8)
f = 65 * np.exp(-d * 3) + 32
boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-d / 0.7)
boom += 0.5 * lp(rng.standard_normal(len(d)), 500) * np.exp(-d / 0.12)
add(np.tanh(1.6 * boom) * 0.95 + hp(rng.standard_normal(len(d)), 4500) * np.exp(-d / 0.6) * 0.3, DROP)


# ---------------- post-drop groove (modern house / afro-house) ----------------
def kick():
    d = tvec(0.4)
    f = 140 * np.exp(-d * 30) + 45
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-d / 0.18)
    return np.tanh(1.4 * s) + hp(rng.standard_normal(len(d)), 3000) * np.exp(-d / 0.004) * 0.3


def hat(g):
    d = tvec(0.06)
    return g * hp(rng.standard_normal(len(d)), 7000) * np.exp(-d / 0.018)


def clap():
    d = tvec(0.25)
    env = sum(np.where(d >= o, np.exp(-(d - o) / 0.012), 0) for o in (0.0, 0.01, 0.022))
    env = env + 0.5 * np.exp(-d / 0.09)
    return bp(rng.standard_normal(len(d)), 900, 5000) * env * 0.3


def shaker(g):
    d = tvec(0.09)
    env = np.minimum(1, d / 0.02) * np.exp(-d / 0.03)
    return g * bp(rng.standard_normal(len(d)), 4000, 11000) * env


END = DUR - 0.4
b = DROP + BEAT
while b < END:
    add(kick() * 0.75, b); b += BEAT
b, i = DROP, 0
while b < END:
    add(hat(0.12), b + BEAT / 2, 1.0, 0.25)
    if i % 2 == 1:
        add(clap(), b)
    # shaker 16ths (accent on the 'e' and 'a')
    for q in (0.25, 0.75):
        add(shaker(0.10), b + BEAT * q, 1.0, -0.4)
    b += BEAT; i += 1
# bass: syncopated afro-house line (1, 'and-a' of 2, 'and' of 3, 4) per bar
BASS_PAT = [(0.0, 0, 0.30), (0.75, 0, 0.18), (1.25, 12, 0.18), (1.5, 0, 0.22), (2.5, 7, 0.22), (3.0, 0, 0.30), (3.5, 10, 0.2)]
bar = int(DROP // BAR)
while bar * BAR < END:
    root = ROOTS[bar % 4]
    for pos, iv, dur in BASS_PAT:
        t = bar * BAR + pos * BEAT
        if t >= END:
            break
        f = mtof(root + iv)
        d = tvec(dur)
        env = np.minimum(1, d / 0.004) * np.exp(-d / 0.14)
        add(np.tanh(2.0 * (np.sin(2 * np.pi * f * d) + 0.3 * np.sin(4 * np.pi * f * d))) * env * 0.27, t)
    bar += 1

# ---------------- whooshes ----------------
for c in CUTS:
    d = tvec(0.6)
    x = d / d[-1]
    env = np.where(d < 0.35, (d / 0.35) ** 2, np.exp(-(d - 0.35) / 0.08))
    nz = rng.standard_normal(len(d))
    mix = bp(nz, 300, 1500) * (1 - x) + bp(nz, 1500, 7000) * x
    i0 = int((c - 0.35) * SR)
    L[i0:i0 + len(d)] += mix * env * 0.29 * np.cos(x * np.pi / 2)
    R[i0:i0 + len(d)] += mix * env * 0.29 * np.sin(x * np.pi / 2)

# gap before the drop, loop fade at the end, tiny fade-in
gap = (tt >= 7.875) & (tt < DROP)
L[gap] *= 0.35; R[gap] *= 0.35
fade = np.clip((DUR - tt) / 0.45, 0, 1) * np.clip(tt / 0.01, 0, 1)
L *= fade; R *= fade

st = np.stack([L, R], 1)
st = np.tanh(st / (np.abs(st).max() + 1e-9) * 1.2) * 0.85
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype(np.int16).tobytes())
print('wrote', sys.argv[1])
