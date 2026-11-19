#!/usr/bin/env python3
"""Sépare la voix de la musique d'origine (la voix fournie contenait encore l'ancienne musique).

Modèle UVR MDX-Net « Kim_Vocal_2 » (ONNX, sortie = voix), exécuté avec onnxruntime ; STFT et ISTFT en numpy,
mêmes réglages que UVR : n_fft 7680, hop 1024, 3072 bandes, 256 trames par morceau.

Usage : python3 tools/separer-voix.py <modele.onnx> <entree.wav> <sortie-voix.wav>
"""
import subprocess
import sys

import numpy as np
import onnxruntime as ort

MODELE, ENTREE, SORTIE = sys.argv[1:4]
SR, N_FFT, HOP, DIM_F, DIM_T = 44100, 7680, 1024, 3072, 256
N_BINS = N_FFT // 2 + 1
CHUNK = HOP * (DIM_T - 1)
TRIM = N_FFT // 2
GEN = CHUNK - 2 * TRIM
FEN = np.hanning(N_FFT + 1)[:-1].astype(np.float32)  # Hann périodique (comme torch.hann_window)


def lire(f):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).T.copy()


def stft(x):
    """x : [n, L] → [n, N_BINS, trames] (centré, bords en miroir)."""
    x = np.pad(x, ((0, 0), (N_FFT // 2, N_FFT // 2)), mode="reflect")
    n_tr = 1 + (x.shape[1] - N_FFT) // HOP
    idx = np.arange(N_FFT)[None, :] + HOP * np.arange(n_tr)[:, None]
    return np.fft.rfft(x[:, idx] * FEN, axis=-1).transpose(0, 2, 1)


def istft(S, longueur):
    """S : [n, N_BINS, trames] → [n, longueur]."""
    n, _, n_tr = S.shape
    fr = np.fft.irfft(S.transpose(0, 2, 1), n=N_FFT, axis=-1) * FEN
    total = N_FFT + HOP * (n_tr - 1)
    y = np.zeros((n, total), dtype=np.float64)
    w = np.zeros(total, dtype=np.float64)
    for t in range(n_tr):
        y[:, t * HOP:t * HOP + N_FFT] += fr[:, t]
        w[t * HOP:t * HOP + N_FFT] += FEN ** 2
    y /= np.maximum(w, 1e-8)
    return y[:, N_FFT // 2:N_FFT // 2 + longueur]


mix = lire(ENTREE)
n = mix.shape[1]
pad = GEN - n % GEN
mixp = np.concatenate([np.zeros((2, TRIM), np.float32), mix, np.zeros((2, pad + TRIM), np.float32)], axis=1)
sess = ort.InferenceSession(MODELE, providers=["CPUExecutionProvider"])
sorties = []
for i in range(0, n + pad, GEN):
    morceau = mixp[:, i:i + CHUNK]
    S = stft(morceau)  # [2, N_BINS, 256]
    entree = np.stack([S[0].real, S[0].imag, S[1].real, S[1].imag])[None, :, :DIM_F, :].astype(np.float32)
    sortie = sess.run(None, {"input": entree})[0][0]  # [4, DIM_F, 256]
    spec = np.zeros((2, N_BINS, DIM_T), dtype=np.complex64)
    spec[0, :DIM_F] = sortie[0] + 1j * sortie[1]
    spec[1, :DIM_F] = sortie[2] + 1j * sortie[3]
    sorties.append(istft(spec, CHUNK)[:, TRIM:-TRIM])
voix = np.concatenate(sorties, axis=1)[:, :n].mean(0).astype(np.float32)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", SORTIE], input=voix.tobytes(), check=True)
print(f"voix séparée : {n / SR:.1f} s → {SORTIE}")
