#!/usr/bin/env python3
"""Original 'Italian' track for Welcome to Italie (120 BPM, 20 s, A minor i-iv-V7-i).
Everything is synthesized with numpy/scipy: no samples, no existing melody.
- Intro 0-3 s : accordion-like pad (detuned saws, musette beating), sparse mandolin plucks, intro hits.
- Build 3-8 s : tarantella feel -> mandolin tremolo melody (Karplus-Strong), accordion oom-pah,
                tambourine in triplets (6/8 over the beat), snare roll + riser, gap before the drop.
- Drop 8 s    : boom + same mandolin melody (octave doubled) over kick / clap / hats / afro-house bass.
- Whoosh on every cut, ending hit at 17.5 s, fade at 20 s.
Usage: audio_italie.py out.wav
"""
import sys, wave
import numpy as np
from scipy.signal import butter, lfilter

SR = 44100
DUR = 20.0
N = int(SR * DUR)
BEAT = 0.5
BAR = 2.0
DROP = 8.0
CUTS = [3.0, 5.0, 6.5, 8.0, 9.5, 10.5, 11.5, 12.5, 13.5, 14.5, 15.5, 16.5]
END_HIT = 17.5
rng = np.random.default_rng(11)
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


# A minor: i - iv - V7 - i, one chord per bar (2 s). t=8.0 (drop) lands on Am.
CHORDS = [[57, 60, 64], [57, 62, 65], [56, 59, 62, 64], [57, 60, 64]]
ROOTS = [45, 50, 40, 45]  # A2, D3, E2, A2


def bar_idx(t):
    return int(t // BAR) % 4


# ---------------- Karplus-Strong mandolin ----------------
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


def mandolin_note(m, dur, trem=True, gain=1.0):
    """double course (two slightly detuned strings), tremolo picking at 32nds (16/s)."""
    sig = np.zeros(int((dur + 0.3) * SR))
    step = BEAT / 8 if trem else dur
    k = 0
    t = 0.0
    while t < dur - 1e-6:
        a = 1.0 if k % 2 == 0 else 0.75          # down / up strokes
        ring = 0.16 if trem else 0.6
        for det in (-4, 4):                       # cents
            p = ks(mtof(m) * 2 ** (det / 1200), ring + 0.15, bright=0.75, decay=0.995)
            p *= np.exp(-np.arange(len(p)) / SR / 0.35)
            i0 = int(t * SR)
            sig[i0:i0 + len(p)] += p[:len(sig) - i0] * a * 0.5
        t += step; k += 1
    return hp(sig, 180) * gain


# original melody, A harmonic minor, (midi, beats) per bar, follows i-iv-V7-i
PHRASE = [
    [(76, 1), (74, .5), (72, .5), (71, .5), (72, .5), (69, 1)],          # Am
    [(74, 1), (77, .5), (76, .5), (74, .5), (72, .5), (74, 1)],          # Dm
    [(71, .5), (74, .5), (80, 1), (76, .5), (74, .5), (71, 1)],          # E7 (G#)
    [(72, .5), (71, .5), (69, 1), (76, 1), (69, 1)],                     # Am
]
mand = np.zeros(N)
for bar in range(int(DUR / BAR) + 1):
    t = bar * BAR
    for m, beats in PHRASE[bar % 4]:
        d = beats * BEAT
        in_build = 3.0 <= t < 7.875
        in_drop = DROP <= t < DUR - 0.6
        if in_build or in_drop:
            if in_build:
                g = 0.9 + 0.5 * (t - 3.0) / 5.0
                s = mandolin_note(m, min(d, 7.875 - t), True, g)
            else:
                s = mandolin_note(m, d, True, 1.1) + mandolin_note(m + 12, d, True, 0.45)
            i0 = int(t * SR); n = min(len(s), N - i0)
            mand[i0:i0 + n] += s[:n]
        t += d
# intro: sparse single plucks of the Am arpeggio on beats
for i, m in enumerate([69, 72, 76, 72, 69, 76]):
    add(mandolin_note(m, 0.5, False, 0.9), 0.0 + i * BEAT, 1.0, 0.2)
# light room: two short reflections
mL = mand.copy(); mR = mand.copy()
d1, d2 = int(0.023 * SR), int(0.041 * SR)
mL[d1:] += 0.35 * mand[:-d1]; mR[d2:] += 0.35 * mand[:-d2]
L += mL * 0.9; R += mR * 1.0


# ---------------- accordion ----------------
def reed(freqs, dur):
    t = tvec(dur)
    s = np.zeros_like(t)
    for f in freqs:
        for det in (-9, 0, 9):                     # musette beating
            ff = f * 2 ** (det / 1200)
            ph = rng.random()
            saw = 2 * ((ff * t + ph) % 1) - 1
            sq = np.sign(np.sin(2 * np.pi * ff * t + ph * 6.28))
            s += 0.7 * saw + 0.3 * sq
    s = lp(s, 1800, 2)
    return s


acc = np.zeros(N)
for bar in range(int(DUR / BAR) + 1):
    t0 = bar * BAR
    ch = [mtof(m) for m in CHORDS[bar % 4]]
    d = 2.3
    t = tvec(d)
    env = np.minimum(1, t / 0.18) * np.clip((d - t) / 0.35, 0, 1)
    bellows = 1 + 0.08 * np.sin(2 * np.pi * 0.5 * t)
    s = reed(ch, d) * env * bellows
    i0 = int(t0 * SR); n = min(len(s), N - i0)
    acc[i0:i0 + n] += s[:n]
accg = np.where(tt < 3.0, 0.070, np.where(tt < DROP, 0.050, 0.030))
add(acc * accg, 0, 1.0, -0.2)
# oom-pah in tarantella triplets during the build: bass on beat, chord stab on 3rd triplet
t = 3.0
while t < 7.875:
    b = bar_idx(t)
    d = tvec(0.14)
    env = np.exp(-d / 0.06)
    bass = reed([mtof(ROOTS[b])], 0.14) * env
    stab = reed([mtof(m) for m in CHORDS[b]], 0.12)[:len(d)] * np.exp(-d[:int(0.12 * SR)] / 0.04)
    add(bass * 0.12, t, 1.0, 0.0)
    add(stab * 0.06, t + BEAT * 2 / 3, 1.0, 0.25)
    t += BEAT


# ---------------- tambourine (triplets over the beat = 6/8 feel) ----------------
def tamb(g):
    d = tvec(0.12)
    jing = np.zeros_like(d)
    for o in rng.uniform(0, 0.012, 5):            # several jingles
        jing += np.where(d >= o, np.exp(-(d - o) / 0.03), 0)
    nz = bp(rng.standard_normal(len(d)), 5500, 12000)
    ring = np.sin(2 * np.pi * 7200 * d) * 0.15
    return g * (nz + ring) * jing / 5


t = 3.0
k = 0
while t < DUR - 0.6:
    if 7.875 <= t < DROP:
        t += BEAT / 3; k += 1; continue
    acc_g = 0.20 if k % 3 == 0 else (0.08 if k % 3 == 1 else 0.13)
    if t >= DROP:
        acc_g *= 0.75
    add(tamb(acc_g), t, 1.0, 0.35)
    t += BEAT / 3; k += 1


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


# ---------------- post-drop groove (Italo-dance / afro-house) ----------------
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


def conga(f0, g):
    d = tvec(0.18)
    f = f0 * (1 + 0.4 * np.exp(-d * 60))
    return g * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-d / 0.07)


END = DUR - 0.4
b = DROP + BEAT
while b < END:
    add(kick() * 0.75, b); b += BEAT
b, i = DROP, 0
while b < END:
    add(hat(0.12), b + BEAT / 2, 1.0, 0.25)
    if i % 2 == 1:
        add(clap(), b)
    # afro-house percussion: conga on the 'a' of each beat
    add(conga(330 if i % 2 else 250, 0.10), b + BEAT * 3 / 4, 1.0, -0.4)
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
