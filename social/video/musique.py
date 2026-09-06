#!/usr/bin/env python3
"""Compose un lit musical libre de droits pour les Reels.

Ecrit de toutes pieces : aucune licence a verifier, et le tempo est celui sur
lequel le montage est coupe, donc les plans tombent sur les temps.

Palette sonore : quatre au sol sourd, sub, charleston sur les contretemps,
nappe mineure filtree. Rien de melodique — le Reel montre un chantier, la
musique porte le rythme, elle ne raconte pas.
"""
import numpy as np

SR = 48000
BPM = 120
TEMPS = 60 / BPM          # 0,5 s
MESURE = 4 * TEMPS        # 2 s


def _env(n, attaque, chute, courbe=2.5):
    a = max(int(attaque * SR), 1)
    e = np.ones(n)
    e[:a] = np.linspace(0, 1, a)
    d = np.linspace(1, 0, max(n - a, 1)) ** courbe
    e[a:] = d[: n - a]
    return e


def kick(dur=0.42):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 105 * np.exp(-t * 34) + 42
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(n, 0.001, dur, 3.2)
    clic = np.sin(2 * np.pi * 1400 * t) * _env(n, 0.0005, 0.012, 5) * 0.16
    return np.tanh((x + clic) * 1.5) * 0.78


def charley(dur=0.06, ouvert=False):
    n = int((dur * (3 if ouvert else 1)) * SR)
    rng = np.random.default_rng(7)
    x = rng.standard_normal(n)
    # passe-haut grossier : la difference successive coupe le grave
    x = np.diff(np.concatenate([[0], x]))
    return x * _env(n, 0.0004, dur, 4.5) * (0.40 if ouvert else 0.28)


def sub(freq, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * freq * t) + 0.28 * np.sin(2 * np.pi * freq * 2 * t)
    return x * _env(n, 0.006, dur, 1.6) * 0.42


def nappe(freqs, dur, niveau=0.14):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for f in freqs:
        for det in (-0.4, 0.0, 0.4):          # trois voix legerement desaccordees
            ph = 2 * np.pi * (f + det) * t
            x += (2 * (ph / (2 * np.pi) % 1) - 1)   # dent de scie
    x /= len(freqs) * 3
    # passe-bas a un pole, balaye lentement vers le haut
    c = np.linspace(0.010, 0.055, n)
    y = np.zeros(n)
    acc = 0.0
    for i in range(n):
        acc += c[i] * (x[i] - acc)
        y[i] = acc
    env = np.minimum(np.linspace(0, 1, n) * 3, 1) * np.linspace(1, 0.55, n)
    return y * env * niveau


def montee(dur=1.6):
    n = int(dur * SR)
    rng = np.random.default_rng(11)
    x = rng.standard_normal(n)
    c = np.linspace(0.004, 0.20, n)
    y, acc = np.zeros(n), 0.0
    for i in range(n):
        acc += c[i] * (x[i] - acc)
        y[i] = acc
    return y * (np.linspace(0, 1, n) ** 2.2) * 0.30


def pose(piste, son, depart):
    i = int(depart * SR)
    j = min(i + len(son), len(piste))
    if i < len(piste):
        piste[i:j] += son[: j - i]


def composer(duree, sortie):
    n = int(duree * SR)
    p = np.zeros(n)

    LA, DO, MI = 55.0, 65.41, 82.41       # la mineur, registre grave

    # nappe continue, par blocs de deux mesures
    b = 0.0
    while b < duree:
        pose(p, nappe([LA, DO, MI] if int(b / (2 * MESURE)) % 2 == 0 else [LA, MI, 73.42],
                      min(2 * MESURE, duree - b)), b)
        b += 2 * MESURE

    # le kick entre a la 2e mesure, s'arrete sur la carte de fin
    fin_kick = duree - 3.4
    t = MESURE
    while t < fin_kick:
        pose(p, kick(), t)
        t += TEMPS

    # sub sur les temps 1 et 3
    t = MESURE
    while t < fin_kick:
        pose(p, sub(LA, TEMPS * 0.9), t)
        t += 2 * TEMPS

    # charleston sur les contretemps, ouvert en fin de mesure
    t = MESURE + TEMPS / 2
    while t < fin_kick:
        ouv = abs((t % MESURE) - (3.5 * TEMPS)) < 1e-6
        pose(p, charley(ouvert=ouv), t)
        t += TEMPS

    # montee avant la carte de fin
    pose(p, montee(), fin_kick - 1.6)
    pose(p, kick(0.8), fin_kick)

    # limiteur doux puis normalisation a -14 dBFS crete
    p = np.tanh(p * 1.25)
    p *= 10 ** (-1.0 / 20) / max(np.abs(p).max(), 1e-9)

    # fondu de sortie sur la derniere seconde
    f = int(1.2 * SR)
    p[-f:] *= np.linspace(1, 0, f)

    st = np.stack([p, p], axis=1)
    from scipy.io import wavfile
    wavfile.write(sortie, SR, (st * 32767).astype(np.int16))
    return sortie


if __name__ == "__main__":
    import sys
    composer(float(sys.argv[2]) if len(sys.argv) > 2 else 23.0, sys.argv[1])
    print(sys.argv[1])
