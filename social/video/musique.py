#!/usr/bin/env python3
"""Compose la bande-son des Reels — ecrite de toutes pieces, donc libre de droits.

Parti pris : **upbeat**. Quatre au sol a 128 BPM, clap sur 2 et 4, charleston
ouvert sur les contretemps — c'est lui qui donne l'elan —, basse syncopee et
arpege clair par-dessus. Structure intro / montee / corps / sortie, pour que le
morceau aille quelque part au lieu de tourner en boucle.

Le montage est coupe sur cette meme grille : un plan change toujours sur un temps.
"""
import numpy as np
from scipy.io import wavfile

SR = 48000
BPM = 128
TEMPS = 60 / BPM            # 0,46875 s
MESURE = 4 * TEMPS

# la mineur : le mode qui sonne energique sans devenir joyeux-publicitaire
LA, DO, MI, SOL, LA2 = 220.0, 261.63, 329.63, 392.0, 440.0
BASSE = 55.0


def _env(n, attaque, courbe=2.5):
    a = max(int(attaque * SR), 1)
    e = np.ones(n)
    e[:a] = np.linspace(0, 1, a)
    e[a:] = np.linspace(1, 0, max(n - a, 1))[: n - a] ** courbe
    return e


def _passe_bas(x, coupe):
    """Un pole, coupe donnee en coefficient (0-1). Suffisant pour arrondir."""
    y, acc = np.empty_like(x), 0.0
    c = coupe if np.ndim(coupe) else np.full(len(x), coupe)
    for i in range(len(x)):
        acc += c[i] * (x[i] - acc)
        y[i] = acc
    return y


def kick(dur=0.34):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 120 * np.exp(-t * 38) + 44
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(n, 0.001, 3.4)
    clic = np.sin(2 * np.pi * 1800 * t) * _env(n, 0.0004, 6) * 0.22
    return np.tanh((x + clic) * 1.7) * 0.92


def clap(dur=0.20):
    n = int(dur * SR)
    rng = np.random.default_rng(3)
    x = np.zeros(n)
    for d in (0, 0.010, 0.019):                 # trois rebonds : ca fait le clap
        i = int(d * SR)
        b = rng.standard_normal(n - i) * _env(n - i, 0.0006, 5.5)
        x[i:] += b * (1.0 if d == 0 else 0.65)
    x = x - _passe_bas(x, 0.06)                 # on vide le grave
    return x * 0.33


def hat(dur=0.05, ouvert=False):
    d = dur * (4.5 if ouvert else 1)
    n = int(d * SR)
    rng = np.random.default_rng(19 if ouvert else 5)
    x = rng.standard_normal(n)
    x = x - _passe_bas(x, 0.035)
    return x * _env(n, 0.0004, 3.0 if ouvert else 5.0) * (0.34 if ouvert else 0.20)


def basse(freq, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    ph = 2 * np.pi * freq * t
    dent = 2 * ((ph / (2 * np.pi)) % 1) - 1
    x = 0.75 * np.sin(ph) + 0.35 * dent
    x = _passe_bas(x, np.linspace(0.045, 0.020, n))
    return x * _env(n, 0.004, 1.9) * 0.50


def pluck(freq, dur=0.30):
    """Arpege : dent de scie courte, filtre qui se referme. C'est la melodie."""
    n = int(dur * SR); t = np.arange(n) / SR
    ph = 2 * np.pi * freq * t
    x = 2 * ((ph / (2 * np.pi)) % 1) - 1
    x += 0.5 * (2 * (((ph * 1.005) / (2 * np.pi)) % 1) - 1)
    x = _passe_bas(x, np.linspace(0.42, 0.06, n))
    return x * _env(n, 0.002, 3.6) * 0.22


def montee(dur):
    n = int(dur * SR)
    rng = np.random.default_rng(23)
    x = _passe_bas(rng.standard_normal(n), np.linspace(0.006, 0.30, n))
    return x * (np.linspace(0, 1, n) ** 2.4) * 0.34


def composer(duree, sortie):
    n = int(duree * SR)
    p = np.zeros(n)

    def pose(son, t, gain=1.0):
        i = int(t * SR); j = min(i + len(son), n)
        if i < n:
            p[i:j] += son[: j - i] * gain

    intro = 2 * MESURE                 # 2 mesures d'installation
    fin = duree - 2.2                  # la carte de fin respire

    # --- batterie ---
    t = intro
    while t < fin:
        pose(kick(), t)
        t += TEMPS
    t = intro + TEMPS
    while t < fin:                     # clap sur 2 et 4
        pose(clap(), t)
        t += 2 * TEMPS
    t = TEMPS / 2                      # charleston des le debut : c'est l'elan
    while t < fin:
        pose(hat(ouvert=True), t, 0.6 if t < intro else 1.0)
        t += TEMPS
    t = intro
    while t < fin:
        pose(hat(), t)
        t += TEMPS / 2

    # --- basse syncopee : fondamentale, puis contretemps ---
    motif = [(0.0, LA/4), (1.5*TEMPS, LA/4), (2.0*TEMPS, SOL/4),
             (3.0*TEMPS, LA/4), (3.5*TEMPS, DO/4)]
    t = intro
    while t < fin:
        for dt, f in motif:
            if t + dt < fin:
                pose(basse(f, TEMPS * 0.75), t + dt)
        t += MESURE

    # --- arpege : entre a la 4e mesure, c'est lui qui donne envie ---
    arp = [LA, DO, MI, LA2, MI, DO]
    depart = intro + 2 * MESURE
    t, k = depart, 0
    while t < fin - MESURE:
        pose(pluck(arp[k % len(arp)]), t)
        k += 1
        t += TEMPS / 2

    # --- montee avant la carte de fin, puis coup d'arret ---
    pose(montee(2 * MESURE), fin - 2 * MESURE)
    pose(kick(0.7), fin)
    for f in (LA, DO, MI):
        pose(pluck(f, 1.8), fin, 0.8)

    p = np.tanh(p * 1.15)
    p *= 10 ** (-1.0 / 20) / max(np.abs(p).max(), 1e-9)
    f = int(1.0 * SR)
    p[-f:] *= np.linspace(1, 0, f)
    wavfile.write(sortie, SR, (np.stack([p, p], 1) * 32767).astype(np.int16))
    return sortie


if __name__ == "__main__":
    import sys
    composer(float(sys.argv[2]) if len(sys.argv) > 2 else 22.0, sys.argv[1])
    print(sys.argv[1])
