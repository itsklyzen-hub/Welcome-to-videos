#!/usr/bin/env python3
"""Original 120 BPM beat for 'Welcome to Italie' (numpy/scipy only)."""
import sys
import numpy as np
from scipy.signal import butter, lfilter
import wave

SR = 44100
DUR = 20.0
N = int(SR * DUR)
rng = np.random.default_rng(7)
L = np.zeros(N); R = np.zeros(N)
BEAT = 0.5
CUTS = [3.0, 5.0, 6.5, 8.0, 9.5, 10.5, 11.5, 12.5, 13.5, 14.5, 15.5, 16.5]
DROP = 8.0


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def bp(x, lo, hi, order=2):
    b, a = butter(order, [lo / (SR / 2), hi / (SR / 2)], btype='band')
    return lfilter(b, a, x)


def lp(x, fc, order=2):
    b, a = butter(order, fc / (SR / 2), btype='low')
    return lfilter(b, a, x)


def hp(x, fc, order=2):
    b, a = butter(order, fc / (SR / 2), btype='high')
    return lfilter(b, a, x)


def add(sig, t0, gain=1.0, pan=0.0):
    i0 = int(round(t0 * SR))
    if i0 >= N:
        return
    if i0 < 0:
        sig = sig[-i0:]; i0 = 0
    n = min(len(sig), N - i0)
    gl = gain * np.sqrt((1 - pan) / 2) * np.sqrt(2)
    gr = gain * np.sqrt((1 + pan) / 2) * np.sqrt(2)
    L[i0:i0 + n] += sig[:n] * gl
    R[i0:i0 + n] += sig[:n] * gr


def tvec(d):
    return np.arange(int(d * SR)) / SR


# chord progression, one chord per bar (2 s)
CHORDS = [[57, 60, 64], [57, 60, 65], [55, 60, 64], [55, 59, 62]]
ROOTS = [45, 41, 48, 43]


def chord_at(t):
    return int(t // 2.0) % 4

# ---------------- pad ----------------
pad = np.zeros(N)
for bar in range(int(DUR // 2) + 1):
    t0 = bar * 2.0
    t = tvec(2.3)
    env = np.minimum(1, t / 0.25) * np.minimum(1, np.maximum(0, (2.3 - t) / 0.4))
    s = np.zeros_like(t)
    for m in CHORDS[bar % 4]:
        for det in (-0.12, 0.0, 0.12):
            f = mtof(m) * 2 ** (det / 12)
            ph = rng.random()
            s += 2 * ((f * t + ph) % 1.0) - 1
    s = lp(s, 1400) * env
    i0 = int(t0 * SR)
    n = min(len(s), N - i0)
    pad[i0:i0 + n] += s[:n]
pad *= 0.035
padenv = np.ones(N)
tt = np.arange(N) / SR
padenv *= np.where(tt < DROP, 0.7 + 0.3 * (tt / DROP), 0.8)
add(pad * padenv, 0, 1.0, -0.15)
add(np.roll(pad * padenv, int(0.011 * SR)), 0, 1.0, 0.15)

# ---------------- arpeggio (16ths) ----------------
pattern = [0, 1, 2, 3, 2, 1, 0, 2]
arp_sig = np.zeros(N)
step = BEAT / 4
k = 0
t = 0.5
while t < DUR - 0.25:
    if 7.875 <= t < DROP:  # drop gap
        t += step; k += 1; continue
    ch = CHORDS[chord_at(t)]
    notes = ch + [ch[0] + 12]
    m = notes[pattern[k % 8]] + 12
    f = mtof(m)
    d = tvec(0.22)
    env = np.exp(-d / 0.07)
    s = (np.sin(2 * np.pi * f * d) + 0.35 * np.sin(4 * np.pi * f * d) + 0.15 * np.sin(6 * np.pi * f * d)) * env
    g = 0.07 + 0.08 * min(1, t / DROP) if t < DROP else 0.11
    i0 = int(t * SR); n = min(len(s), N - i0)
    arp_sig[i0:i0 + n] += s[:n] * g
    t += step; k += 1
# ping-pong delay
dl = int(0.1875 * SR)
arpL = arp_sig.copy(); arpR = np.zeros(N)
arpR[dl:] += arp_sig[:-dl] * 0.45
arpL[2 * dl:] += arp_sig[:-2 * dl] * 0.25
L += arpL; R += arpR + arp_sig * 0.6

# ---------------- intro / ending hits ----------------
def impact(strength=1.0, dur=0.9):
    d = tvec(dur)
    f = 90 * np.exp(-d * 6) + 40
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-d / 0.35)
    nz = lp(rng.standard_normal(len(d)), 2500) * np.exp(-d / 0.06)
    cr = hp(rng.standard_normal(len(d)), 5000) * np.exp(-d / 0.4) * 0.25
    return strength * (0.8 * body + 0.35 * nz + cr)

add(impact(0.45), 0.5)
add(impact(0.65), 1.5)
add(impact(0.6), 17.5)

# ---------------- build: snare roll + riser ----------------
def snare(g):
    d = tvec(0.15)
    nz = bp(rng.standard_normal(len(d)), 1200, 7000) * np.exp(-d / 0.05)
    tone = np.sin(2 * np.pi * 190 * d) * np.exp(-d / 0.04)
    return g * (nz + 0.5 * tone)

t = 6.0
while t < 7.875:
    step = 0.25 if t < 7.0 else (0.125 if t < 7.5 else 0.0625)
    g = 0.12 + 0.3 * (t - 6.0) / 1.875
    add(snare(g), t, 1.0, 0.0)
    t += step

rd = 3.0
d = tvec(rd - 0.125)  # 5.0 -> 7.875
f = 220 * (6 ** (d / d[-1]))
riser = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.05 * (d / d[-1]) ** 2
nz = hp(rng.standard_normal(len(d)), 1800)
nz *= 0.12 * (d / d[-1]) ** 2.2
add(riser + nz, 5.0)

# ---------------- drop boom ----------------
d = tvec(1.8)
f = 65 * np.exp(-d * 3) + 32
boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-d / 0.7)
boom += 0.5 * lp(rng.standard_normal(len(d)), 500) * np.exp(-d / 0.12)
crash = hp(rng.standard_normal(len(d)), 4500) * np.exp(-d / 0.6) * 0.3
add(np.tanh(1.6 * boom) * 0.95 + crash, DROP)

# ---------------- post-drop groove ----------------
def kick():
    d = tvec(0.4)
    f = 140 * np.exp(-d * 30) + 45
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-d / 0.18)
    click = hp(rng.standard_normal(len(d)), 3000) * np.exp(-d / 0.004) * 0.3
    return np.tanh(1.4 * s) + click

def hat(g):
    d = tvec(0.06)
    return g * hp(rng.standard_normal(len(d)), 7000) * np.exp(-d / 0.018)

def clap():
    d = tvec(0.25)
    env = np.zeros_like(d)
    for o in (0.0, 0.01, 0.022):
        env += np.where(d >= o, np.exp(-(d - o) / 0.012), 0)
    env += 0.5 * np.exp(-d / 0.09)
    return bp(rng.standard_normal(len(d)), 900, 5000) * env * 0.3

b = DROP + BEAT
while b < DUR - 0.4:
    add(kick() * 0.75, b)
    b += BEAT
b = DROP
i = 0
while b < DUR - 0.4:
    add(hat(0.13), b + BEAT / 2, 1.0, 0.25)
    add(hat(0.06), b + BEAT / 4 * 3, 1.0, -0.25)
    if i % 2 == 1:
        add(clap(), b, 1.0, 0.0)
    b += BEAT; i += 1
# bass (8ths)
t = DROP
while t < DUR - 0.4:
    root = ROOTS[chord_at(t)]
    f = mtof(root)
    d = tvec(0.24)
    env = np.minimum(1, d / 0.005) * np.exp(-d / 0.16)
    s = np.tanh(2.0 * (np.sin(2 * np.pi * f * d) + 0.3 * np.sin(4 * np.pi * f * d))) * env
    add(s * 0.28, t)
    t += BEAT / 2

# ---------------- whooshes ----------------
for c in CUTS:
    d = tvec(0.6)  # c-0.35 .. c+0.25
    x = d / d[-1]
    env = np.where(d < 0.35, (d / 0.35) ** 2, np.exp(-(d - 0.35) / 0.08))
    nz = rng.standard_normal(len(d))
    low = bp(nz, 300, 1500); high = bp(nz, 1500, 7000)
    mix = low * (1 - x) + high * x
    g = 0.22
    i0 = int((c - 0.35) * SR); n = len(d)
    panL = np.cos(x * np.pi / 2); panR = np.sin(x * np.pi / 2)
    L[i0:i0 + n] += mix * env * g * panL * 1.3
    R[i0:i0 + n] += mix * env * g * panR * 1.3

# drop gap: duck music 7.875-8.0 (whoosh tail remains audible but low)
gap = (tt >= 7.875) & (tt < DROP)
L[gap] *= 0.35; R[gap] *= 0.35

# loop fade at the end
fade = np.clip((DUR - tt) / 0.45, 0, 1)
L *= fade; R *= fade
# tiny fade-in
fin = np.clip(tt / 0.01, 0, 1); L *= fin; R *= fin

st = np.stack([L, R], 1)
st = np.tanh(st / (np.abs(st).max() + 1e-9) * 1.2) * 0.85
pcm = (st * 32767).astype(np.int16)
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print('wrote', sys.argv[1])
