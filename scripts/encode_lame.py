#!/usr/bin/env python3
"""Alternativa a encode_audio.sh senza ffmpeg (macOS): WAV PCM 16 bit → MP3 CBR.

  afconvert -f WAVE -d LEI16@44100 -c 2 "originale.mp3" /tmp/src.wav
  python3 scripts/encode_lame.py /tmp/src.wav assets/traccia.mp3 96
Richiede: pip install lameenc
"""
import sys, wave
import lameenc

src, dst = sys.argv[1], sys.argv[2]
kbps = int(sys.argv[3]) if len(sys.argv) > 3 else 96
with wave.open(src, "rb") as w:
    assert w.getsampwidth() == 2, "serve PCM 16 bit"
    enc = lameenc.Encoder()
    enc.set_bit_rate(kbps)
    enc.set_in_sample_rate(w.getframerate())
    enc.set_out_sample_rate(44100)
    enc.set_channels(w.getnchannels())
    enc.set_quality(2)  # 2 = alta qualità
    with open(dst, "wb") as out:
        while True:
            frames = w.readframes(44100 * 10)
            if not frames:
                break
            out.write(enc.encode(frames))
        out.write(enc.flush())
print("ok", dst)
