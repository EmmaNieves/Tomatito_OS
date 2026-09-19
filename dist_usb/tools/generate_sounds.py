"""
generate_sounds.py — Genera el banco de sonidos de Tomatito usando solo
la librería estándar de Python (wave + math). Sin dependencias externas.

Produce sonidos al estilo Windows XP:
- startup.wav      → acorde orquestal de bienvenida (estilo XP)
- click.wav        → clic suave de UI
- window_open.wav  → apertura de ventana (tono ascendente)
- window_close.wav → cierre de ventana (tono descendente)
- error.wav        → error del sistema (dos tonos)
- notification.wav → notificación (campana corta)
- minimize.wav     → minimizar ventana (swoosh descendente)

Ejecutar:
    py tools/generate_sounds.py
"""

import wave
import struct
import math
import os

SAMPLE_RATE = 44100
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR  = os.path.join(BASE_DIR, "assets", "sounds")


# ── Primitivas de síntesis ────────────────────────────────────────────────

def sine_wave(freq: float, duration: float, amplitude: float = 0.5,
              phase: float = 0.0, sample_rate: int = SAMPLE_RATE) -> list[float]:
    n = int(sample_rate * duration)
    return [amplitude * math.sin(2 * math.pi * freq * i / sample_rate + phase)
            for i in range(n)]


def envelope(samples: list[float], attack: float = 0.01, decay: float = 0.05,
             sustain: float = 0.7, release: float = 0.1,
             sample_rate: int = SAMPLE_RATE) -> list[float]:
    """Aplica envolvente ADSR a una lista de muestras."""
    n = len(samples)
    a = int(attack  * sample_rate)
    d = int(decay   * sample_rate)
    r = int(release * sample_rate)
    result = []
    for i, s in enumerate(samples):
        if i < a:
            gain = i / a
        elif i < a + d:
            gain = 1.0 - (1.0 - sustain) * (i - a) / d
        elif i >= n - r:
            gain = sustain * (n - i) / r
        else:
            gain = sustain
        result.append(s * gain)
    return result


def mix(*tracks: list[float]) -> list[float]:
    """Mezcla varias pistas al mismo tiempo."""
    length = max(len(t) for t in tracks)
    result = [0.0] * length
    for track in tracks:
        for i, s in enumerate(track):
            result[i] += s
    # Normalizar para evitar clipping
    peak = max(abs(x) for x in result) or 1.0
    return [x / peak * 0.9 for x in result]


def concatenate(*tracks: list[float]) -> list[float]:
    result = []
    for t in tracks:
        result.extend(t)
    return result


def fade_in(samples: list[float], duration: float,
            sample_rate: int = SAMPLE_RATE) -> list[float]:
    n = int(duration * sample_rate)
    result = list(samples)
    for i in range(min(n, len(result))):
        result[i] *= i / n
    return result


def fade_out(samples: list[float], duration: float,
             sample_rate: int = SAMPLE_RATE) -> list[float]:
    n = int(duration * sample_rate)
    result = list(samples)
    start = max(0, len(result) - n)
    for i in range(start, len(result)):
        result[i] *= (len(result) - i) / n
    return result


def silence(duration: float, sample_rate: int = SAMPLE_RATE) -> list[float]:
    return [0.0] * int(duration * sample_rate)


def save_wav(samples: list[float], filename: str,
             sample_rate: int = SAMPLE_RATE) -> None:
    path = os.path.join(OUT_DIR, filename)
    with wave.open(path, 'w') as wf:
        wf.setnchannels(1)       # mono
        wf.setsampwidth(2)       # 16-bit
        wf.setframerate(sample_rate)
        for s in samples:
            # Clampar entre -1 y 1
            s = max(-1.0, min(1.0, s))
            wf.writeframes(struct.pack('<h', int(s * 32767)))
    print(f"  Generado: {filename}")


# ── Definiciones de cada sonido ───────────────────────────────────────────

def make_startup():
    """
    Acorde orquestal de arranque estilo XP.
    Notas: La mayor (A4=440), Do#5=554, Mi5=659, La5=880 + armónicos.
    Inspirado en el estilo de Brian Eno para Windows 95/98.
    """
    # Nota base + acorde mayor
    freqs_chord = [
        (220.0, 0.18),  # A3 (bajo)
        (330.0, 0.12),  # E4
        (440.0, 0.20),  # A4
        (554.4, 0.16),  # C#5
        (659.3, 0.15),  # E5
        (880.0, 0.12),  # A5
        (1046.5, 0.07), # C6
    ]

    dur = 3.2
    tracks = []
    for freq, amp in freqs_chord:
        wave_samples = sine_wave(freq, dur, amplitude=amp)
        # Añadir 2º y 3º armónico para textura
        wave_samples = mix(
            wave_samples,
            sine_wave(freq * 2, dur, amplitude=amp * 0.15),
            sine_wave(freq * 3, dur, amplitude=amp * 0.07),
        )
        tracks.append(wave_samples)

    chord = mix(*tracks)
    chord = envelope(chord, attack=0.12, decay=0.3, sustain=0.6, release=0.8)
    chord = fade_in(chord, 0.12)
    chord = fade_out(chord, 1.0)
    save_wav(chord, "startup.wav")


def make_click():
    """Clic suave de interfaz (similar al clic de XP)."""
    dur = 0.08
    samples = mix(
        sine_wave(800,  dur, amplitude=0.4),
        sine_wave(1200, dur, amplitude=0.2),
        sine_wave(400,  dur, amplitude=0.15),
    )
    samples = envelope(samples, attack=0.002, decay=0.02, sustain=0.0, release=0.05)
    save_wav(samples, "click.wav")


def make_window_open():
    """Apertura de ventana: tono ascendente + shimmer."""
    t1 = envelope(sine_wave(400, 0.06, 0.3), attack=0.01, decay=0.01, sustain=0.4, release=0.04)
    t2 = envelope(sine_wave(600, 0.08, 0.3), attack=0.01, decay=0.02, sustain=0.4, release=0.05)
    t3 = envelope(sine_wave(900, 0.1,  0.25),attack=0.01, decay=0.02, sustain=0.3, release=0.06)

    s = concatenate(
        t1,
        silence(0.01),
        t2,
        silence(0.01),
        t3,
    )
    s = fade_out(s, 0.04)
    save_wav(s, "window_open.wav")


def make_window_close():
    """Cierre de ventana: tono descendente."""
    t1 = envelope(sine_wave(700, 0.06, 0.3), attack=0.005, decay=0.01, sustain=0.3, release=0.04)
    t2 = envelope(sine_wave(500, 0.07, 0.3), attack=0.005, decay=0.01, sustain=0.3, release=0.05)
    t3 = envelope(sine_wave(300, 0.08, 0.25),attack=0.005, decay=0.01, sustain=0.2, release=0.06)

    s = concatenate(t1, silence(0.008), t2, silence(0.008), t3)
    s = fade_out(s, 0.04)
    save_wav(s, "window_close.wav")


def make_error():
    """Error del sistema: dos tonos discordantes estilo XP."""
    tone1 = mix(
        sine_wave(392, 0.2, 0.4),   # Sol4
        sine_wave(370, 0.2, 0.15),  # Fa#4 (disonancia)
    )
    tone1 = envelope(tone1, attack=0.01, decay=0.05, sustain=0.5, release=0.08)

    gap = silence(0.05)

    tone2 = mix(
        sine_wave(349, 0.25, 0.4),  # Fa4
        sine_wave(330, 0.25, 0.15), # Mi4
    )
    tone2 = envelope(tone2, attack=0.01, decay=0.05, sustain=0.4, release=0.1)

    s = concatenate(tone1, gap, tone2)
    save_wav(s, "error.wav")


def make_notification():
    """Notificación: campana brillante (ding)."""
    dur = 0.6
    samples = mix(
        sine_wave(1047, dur, amplitude=0.35),  # Do6
        sine_wave(1319, dur, amplitude=0.20),  # Mi6
        sine_wave(2093, dur, amplitude=0.10),  # Do7
    )
    samples = envelope(samples, attack=0.005, decay=0.05, sustain=0.4, release=0.4)
    save_wav(samples, "notification.wav")


def make_minimize():
    """Minimizar: swoosh suave descendente."""
    # Barrido de frecuencia descendente (chirp)
    dur = 0.15
    n = int(SAMPLE_RATE * dur)
    f_start, f_end = 800, 200
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        freq = f_start + (f_end - f_start) * (i / n)
        samples.append(0.3 * math.sin(2 * math.pi * freq * t))
    samples = envelope(samples, attack=0.01, decay=0.02, sustain=0.3, release=0.08)
    save_wav(samples, "minimize.wav")


def make_balloon():
    """Globo de información: doble ding suave."""
    d1 = envelope(mix(
        sine_wave(880, 0.12, 0.3),
        sine_wave(1109, 0.12, 0.15),
    ), attack=0.005, decay=0.03, sustain=0.3, release=0.07)

    gap = silence(0.08)

    d2 = envelope(mix(
        sine_wave(1047, 0.14, 0.25),
        sine_wave(1319, 0.14, 0.12),
    ), attack=0.005, decay=0.03, sustain=0.28, release=0.09)

    s = concatenate(d1, gap, d2)
    save_wav(s, "balloon.wav")


# ── Main ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"Generando banco de sonidos en: {OUT_DIR}")
    make_startup()
    make_click()
    make_window_open()
    make_window_close()
    make_error()
    make_notification()
    make_minimize()
    make_balloon()
    print("\nBanco de sonidos completo: 8 archivos generados.")
