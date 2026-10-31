"""
audio.py - the sound of the film: the voice, the music bed, the final mix.

    python audio.py words      # word times of the recordings -> output/words.json (faster-whisper)
    python audio.py voice      # sNN.mp3 -> output/audio/sNN.wav, all at the same loudness
    python audio.py music      # the music bed, lengthened to the film -> output/audio/music.wav
    python audio.py mix [--draft]   # rendered picture + voice + music -> output/<film>.mp4

The recordings are in NARRATION_DIR, the music track is MUSIC_SRC (both in ../config.env).

The music is used from its start to SRC_END (its own fade-out). To fit the film it is
lengthened by ONE long repeat: x[:b] + x[a:], with a a few seconds after the start and b
well before the final hits, both chosen where the track sounds the same (spectrogram
similarity over 8 s, then sample-accurate alignment, equal-power cross-fade), so the seam
is not heard as a repeat. timeline.py then moves the first word by the few tenths the
chosen repeat differs from the ideal one, so the last hit lands on the lockup.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys

import numpy as np

import timeline as TL

SR = 48000
VOICE_LUFS = -16.0
MUSIC_LUFS = -20.0       # music alone (cold open, ending)
DUCK = 0.28              # music under the voice (about -11 dB)
FILM_NAME = "Vertica_and_PostgreSQL_on_the_same_analytic_workload.mp4"


def run(cmd, **kw):
    return subprocess.run([str(c) for c in cmd], check=True, **kw)


def loudness(path) -> float:
    """Integrated loudness (LUFS) of a file."""
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-af",
                          "loudnorm=print_format=json", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return float(re.search(r'"input_i"\s*:\s*"([-\d.]+)"', err).group(1))


# ------------------------------------------------------------------ words
def words() -> None:
    from faster_whisper import WhisperModel
    m = WhisperModel("small.en", compute_type="int8")
    out = {}
    for f in sorted(TL.NARRATION_DIR.glob("s??.mp3")):
        segs, info = m.transcribe(str(f), word_timestamps=True, language="en", beam_size=5)
        out[f.stem] = {"duration": info.duration,
                       "words": [[w.word.strip(), round(w.start, 3), round(w.end, 3)]
                                 for s in segs for w in s.words]}
        print(f.stem, len(out[f.stem]["words"]), "words")
    TL.OUT.mkdir(exist_ok=True)
    TL.WORDS.write_text(json.dumps(out, indent=0))


# ------------------------------------------------------------------ voice
def voice() -> None:
    TL.AUDIO.mkdir(parents=True, exist_ok=True)
    for f in sorted(TL.NARRATION_DIR.glob("s??.mp3")):
        gain = VOICE_LUFS - loudness(f)
        dst = TL.AUDIO / f"{f.stem}.wav"
        run(["ffmpeg", "-v", "error", "-y", "-i", f, "-af",
             f"volume={gain:.2f}dB,alimiter=limit=0.95:level=disabled,afade=t=in:d=0.02,"
             "aformat=channel_layouts=stereo", "-ar", SR, dst])
        print(f"{f.name}: {gain:+.1f} dB -> {dst.name}")


# ------------------------------------------------------------------ music
def _read(path) -> np.ndarray:
    raw = run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "2", "-ar", SR, "-"],
              capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def music() -> None:
    src = TL.CONFIG["MUSIC_SRC"]
    if not src:
        sys.exit("MUSIC_SRC is not set in config.env")
    TL.MUSIC_INFO.unlink(missing_ok=True)          # the nominal clock, without a chosen repeat
    want = TL.build()["repeat_nom"]
    x = _read(src)[: int(TL.SRC_END * SR)]
    mono = x.mean(axis=1)

    # the last hit before the fade-out: the largest rise of the short-time level
    seg = mono[int(201.5 * SR): int(204.5 * SR)]
    h = SR // 100
    rms = np.sqrt(np.convolve(seg ** 2, np.ones(2 * h) / (2 * h), mode="same"))[::h]
    hit = 201.5 + (int(np.argmax(np.diff(rms))) + 1) / 100

    HOP, WIN = 2400, 4096                          # 50 ms
    n = (len(mono) - WIN) // HOP
    idx = np.arange(WIN)[None, :] + HOP * np.arange(n)[:, None]
    spec = np.abs(np.fft.rfft(mono[idx] * np.hanning(WIN), axis=1))[:, :600]
    bands = np.add.reduceat(spec, np.unique(np.geomspace(2, 599, 48).astype(int)), axis=1)
    feat = np.log1p(40 * bands)
    feat -= feat.mean(axis=1, keepdims=True)
    feat /= np.linalg.norm(feat, axis=1, keepdims=True) + 1e-9

    W = 160                                         # 8 s, centred on the seam
    A_MIN, B_MAX = 4.0, 197.0                       # soon after the start; before the final hits
    best = (-1.0, 0, 0)
    for lag in range(int((want - 3.5) / 0.05), int((want + 2.5) / 0.05)):     # cold open 11.5 to 17.5 s
        sim = (feat[:-lag] * feat[lag:]).sum(axis=1)
        c = np.convolve(sim, np.ones(W) / W, mode="same")
        lo, hi = int(A_MIN / 0.05), min(len(c), int((B_MAX - lag * 0.05) / 0.05))
        if hi <= lo:
            continue
        k = lo + int(np.argmax(c[lo:hi]))
        if c[k] > best[0]:
            best = (float(c[k]), k, lag)
    score, k, lag = best
    if lag == 0:
        sys.exit(f"no repeat of about {want:.1f} s fits between {A_MIN} and {B_MAX} s")
    a, b = k * HOP, (k + lag) * HOP
    ref = mono[a:a + SR]
    r = np.array([np.dot(ref, mono[b + d:b + d + SR]) for d in range(-2400, 2400)])
    b += int(np.argmax(r)) - 2400

    XF = int(0.6 * SR)
    t = np.linspace(0, np.pi / 2, XF)[:, None]
    out = np.concatenate([x[:b - XF], x[b - XF:b] * np.cos(t) + x[a - XF:a] * np.sin(t), x[a:]])
    fade = int(0.3 * SR)
    out[-fade:] *= np.linspace(1, 0, fade)[:, None]
    TL.AUDIO.mkdir(parents=True, exist_ok=True)
    tmp = TL.AUDIO / "music_raw.wav"
    run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ac", 2, "-ar", SR, "-i", "-",
         "-c:a", "pcm_s16le", tmp], input=out.astype(np.float32).tobytes())
    gain = MUSIC_LUFS - loudness(tmp)
    run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", f"volume={gain:.2f}dB", "-c:a", "pcm_f32le",
         TL.AUDIO / "music.wav"])
    tmp.unlink()
    info = {"a": a / SR, "b": b / SR, "repeat": (b - a) / SR, "hit": hit, "similarity": score,
            "length": len(out) / SR, "gain_db": gain}
    TL.MUSIC_INFO.write_text(json.dumps(info, indent=2))
    print(f"repeat {a / SR:.2f} -> {b / SR:.2f} s ({(b - a) / SR:.2f} s, wanted {want:.2f}, "
          f"similarity {score:.3f}); last hit {hit:.2f} s; music {len(out) / SR:.1f} s")


# ------------------------------------------------------------------ mix
def mix(draft: bool) -> None:
    t = TL.load()
    q = "480p15" if draft else "1080p60"
    picture = TL.ROOT / "media" / "videos" / "film" / q / "Film.mp4"
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", picture]
    for sc in t["scenes"]:
        cmd += ["-i", TL.AUDIO / f"{sc['id']}.wav"]
    cmd += ["-i", TL.AUDIO / "music.wav"]
    g, labels = [], ""
    for i, sc in enumerate(t["scenes"], start=1):
        g.append(f"[{i}:a]adelay={round(sc['start'] * 1000)}:all=1[v{i}]")
        labels += f"[v{i}]"
    n = len(t["scenes"])
    g.append(f"{labels}amix=inputs={n}:normalize=0[voice]")
    first, last = t["scenes"][0]["start"], t["scenes"][-1]["end"]
    d0, d1 = first - 1.4, first - 0.1               # down before the first word
    u0, u1 = last + 0.1, last + 0.9                 # up again for the ending
    vol = (f"1-{1 - DUCK}*clip((t-{d0:.3f})/{d1 - d0:.3f},0,1)"
           f"+{1 - DUCK}*clip((t-{u0:.3f})/{u1 - u0:.3f},0,1)")
    g.append(f"[{n + 1}:a]volume='{vol}':eval=frame[music]")
    g.append(f"[voice][music]amix=inputs=2:normalize=0,alimiter=limit=0.95:level=disabled,"
             f"apad=whole_dur={t['total']:.3f}[a]")
    out = TL.OUT / (("draft_" if draft else "") + FILM_NAME)
    cmd += ["-filter_complex", ";".join(g), "-map", "0:v", "-map", "[a]", "-t", f"{t['total']:.3f}",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-ar", SR, "-movflags", "+faststart", out]
    run(cmd)
    print("->", out)


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else ""
    if what == "words":
        words()
    elif what == "voice":
        voice()
    elif what == "music":
        music()
    elif what == "mix":
        mix("--draft" in sys.argv)
    else:
        sys.exit(__doc__)
