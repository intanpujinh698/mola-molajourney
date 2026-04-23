#!/usr/bin/env python3
# ============================================================
#  generate_sounds.py
#  Generate semua sound effect secara prosedural (tanpa file audio eksternal)
#  Jalankan SEKALI:
#    pip install numpy
#    python generate_sounds.py
#  Output: assets/sounds/
# ============================================================
import os
import struct
import math
import wave

OUT = 'assets/sounds'
os.makedirs(OUT, exist_ok=True)

SAMPLE_RATE = 44100

def write_wav(filename, samples, rate=SAMPLE_RATE):
    """Tulis list float [-1,1] ke file WAV 16-bit mono."""
    path = os.path.join(OUT, filename)
    clamped = [max(-1.0, min(1.0, s)) for s in samples]
    raw     = [int(s * 32767) for s in clamped]
    with wave.open(path, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes(struct.pack(f'<{len(raw)}h', *raw))
    print(f'  saved: {path}  ({len(samples)/rate:.2f}s)')

def silence(dur):
    return [0.0] * int(SAMPLE_RATE * dur)

def sine(freq, dur, amp=1.0, phase=0.0):
    n = int(SAMPLE_RATE * dur)
    return [amp * math.sin(2*math.pi*freq*i/SAMPLE_RATE + phase) for i in range(n)]

def sawtooth(freq, dur, amp=1.0):
    n   = int(SAMPLE_RATE * dur)
    per = SAMPLE_RATE / freq
    return [amp * (2*(i%per)/per - 1) for i in range(n)]

def noise(dur, amp=0.5):
    import random
    n = int(SAMPLE_RATE * dur)
    return [amp * (random.random()*2-1) for _ in range(n)]

def envelope(samples, attack=0.01, decay=0.05, sustain=0.7, release=0.1):
    """ADSR envelope."""
    n  = len(samples)
    sr = SAMPLE_RATE
    a  = int(attack  * sr)
    d  = int(decay   * sr)
    r  = int(release * sr)
    s_len = max(0, n - a - d - r)
    out   = []
    for i, smp in enumerate(samples):
        if i < a:
            g = i / a
        elif i < a + d:
            g = 1.0 - (1.0-sustain) * (i-a)/d
        elif i < a + d + s_len:
            g = sustain
        else:
            pos = i - (a+d+s_len)
            g   = sustain * max(0, 1 - pos/r) if r > 0 else 0
        out.append(smp * g)
    return out

def mix(*tracks):
    """Mix beberapa track (sum lalu normalize)."""
    length = max(len(t) for t in tracks)
    result = [0.0] * length
    for t in tracks:
        for i, v in enumerate(t):
            result[i] += v
    peak = max(abs(v) for v in result) or 1.0
    return [v/peak for v in result]

def fade_out(samples, dur_s):
    n     = len(samples)
    fade  = int(dur_s * SAMPLE_RATE)
    start = max(0, n - fade)
    result = list(samples)
    for i in range(start, n):
        t = (i - start) / fade
        result[i] *= (1 - t)
    return result

# ─────────────────────────────────────────────────────────
#  1. EAT — gelembung melesat (pop lembut)
# ─────────────────────────────────────────────────────────
def make_eat():
    # tone pendek naik lalu mati
    dur   = 0.18
    chirp = []
    n     = int(SAMPLE_RATE * dur)
    for i in range(n):
        t    = i / SAMPLE_RATE
        freq = 400 + 800 * (t/dur)**0.5       # sweep up
        chirp.append(math.sin(2*math.pi*freq*t))
    chirp  = envelope(chirp, 0.005, 0.04, 0.3, 0.13)
    # tambah sedikit noise untuk tekstur "basah"
    wet   = noise(dur, 0.15)
    result= mix(chirp, wet)
    write_wav('eat.wav', result)

# ─────────────────────────────────────────────────────────
#  2. TANGLE — "thud" berat + getaran
# ─────────────────────────────────────────────────────────
def make_tangle():
    dur   = 0.5
    thud  = sine(60, dur, 0.9)
    thud  = envelope(thud, 0.003, 0.08, 0.1, 0.4)
    buzz  = sawtooth(120, dur, 0.3)
    buzz  = envelope(buzz, 0.005, 0.05, 0.2, 0.3)
    n_lay = noise(0.12, 0.4)
    n_lay = envelope(n_lay, 0.001, 0.03, 0.0, 0.09)
    # pad ke dur penuh
    n_lay += silence(dur - 0.12)
    result= mix(thud, buzz, n_lay)
    write_wav('tangle.wav', result)

# ─────────────────────────────────────────────────────────
#  3. DAMAGE (hiu menyerang) — "crunch" keras
# ─────────────────────────────────────────────────────────
def make_damage():
    dur   = 0.35
    body  = noise(dur, 1.0)
    body  = envelope(body, 0.001, 0.05, 0.3, 0.25)
    low   = sine(80, dur, 0.7)
    low   = envelope(low, 0.002, 0.06, 0.2, 0.28)
    result= mix(body, low)
    write_wav('damage.wav', result)

# ─────────────────────────────────────────────────────────
#  4. SURFACE BASK — "whoosh" lembut naik ke permukaan
# ─────────────────────────────────────────────────────────
def make_surface():
    dur   = 0.6
    sweep = []
    n     = int(SAMPLE_RATE * dur)
    for i in range(n):
        t    = i / SAMPLE_RATE
        freq = 200 + 600*(t/dur)
        sweep.append(0.5*math.sin(2*math.pi*freq*t))
    sweep  = envelope(sweep, 0.05, 0.1, 0.4, 0.35)
    breath = noise(dur, 0.2)
    breath = envelope(breath, 0.05, 0.15, 0.3, 0.3)
    result = mix(sweep, breath)
    result = fade_out(result, 0.2)
    write_wav('surface.wav', result)

# ─────────────────────────────────────────────────────────
#  5. GAME OVER — chord minor turun (tragis tapi tidak berlebihan)
# ─────────────────────────────────────────────────────────
def make_gameover():
    dur = 2.2
    notes = [220, 261.6, 311.1, 220, 196]  # A3-C4-Eb4-A3-G3
    times = [0.0, 0.25, 0.5, 1.0, 1.5]
    result= [0.0] * int(SAMPLE_RATE * dur)
    for freq, t_start in zip(notes, times):
        note_dur = 0.8
        s_note   = sine(freq, note_dur, 0.5)
        s_note  += sine(freq*2, note_dur, 0.15)   # harmonik
        s_note   = envelope(s_note, 0.02, 0.1, 0.5, 0.5)
        start_i  = int(t_start * SAMPLE_RATE)
        for j, v in enumerate(s_note):
            if start_i + j < len(result):
                result[start_i+j] += v
    peak   = max(abs(v) for v in result) or 1
    result = [v/peak for v in result]
    result = fade_out(result, 0.4)
    write_wav('gameover.wav', result)

# ─────────────────────────────────────────────────────────
#  6. AMBIENT OCEAN — loop background (white noise + low rumble)
# ─────────────────────────────────────────────────────────
def make_ambient():
    import random
    dur    = 4.0   # loop pendek, akan di-loop oleh pygame
    n      = int(SAMPLE_RATE * dur)
    result = []
    # low-pass filter sederhana pada noise
    prev   = 0.0
    alpha  = 0.004   # makin kecil = makin low-pass (ombak berat)
    for i in range(n):
        raw   = random.random()*2-1
        prev  = prev + alpha*(raw - prev)
        t     = i/SAMPLE_RATE
        # modulasi perlahan seperti ombak
        mod   = 0.5 + 0.5*math.sin(2*math.pi*0.18*t + 0.8)
        result.append(prev * mod * 0.6)
    # tambah rumble sangat pelan
    for i in range(n):
        t = i/SAMPLE_RATE
        result[i] += 0.08*math.sin(2*math.pi*38*t)
    # normalize + cross-fade loop edges
    peak = max(abs(v) for v in result) or 1
    result = [v/peak for v in result]
    cf = int(0.15 * SAMPLE_RATE)
    for i in range(cf):
        t = i/cf
        result[i]        = result[i]*t        + result[n-cf+i]*(1-t)
        result[n-cf+i]   = result[n-cf+i]*t   + result[i]*(1-t)
    write_wav('ambient_ocean.wav', result)

# ─────────────────────────────────────────────────────────
#  7. WARNING — pip pendek berulang (untuk energi kritis)
# ─────────────────────────────────────────────────────────
def make_warning():
    dur   = 0.12
    beep  = sine(880, dur, 0.6)
    beep  = envelope(beep, 0.005, 0.02, 0.5, 0.08)
    result= beep + silence(0.18)  # gap antara beep
    write_wav('warning_beep.wav', result)

# ─────────────────────────────────────────────────────────
print('Generating sounds...')
make_eat()
make_tangle()
make_damage()
make_surface()
make_gameover()
make_ambient()
make_warning()
print('\n✅ Semua sound selesai!')
print(f'   Lokasi: {os.path.abspath(OUT)}')
