# Video (manim)

The animated video of the comparison, about 6 minutes, 1920x1080. The narration is in
[../VIDEO.md](../VIDEO.md); every number on screen is read from `../results/` at render
time (`kit.py`), so the video always shows the measured values.

## Setup

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install "manim>=0.19" faster-whisper      # ffmpeg must be on PATH
```

Fonts: Calibri / Consolas when installed, otherwise the metric-compatible Carlito and
Inconsolata from `assets/fonts/` (registered by `style.py`).

## Render

```bash
python timeline.py                           # chapter times (estimate or from the recording)
manim -ql film.py Film                       # draft, 480p15
manim -qh --fps 60 --disable_caching film.py Film   # final, 1080p60
```

The result is written to `media/videos/film/<quality>/Film.mp4` (git-ignored).

Without a recording the chapters are timed from their word count (140 words per minute)
and the draft is silent. To make the final video: record the narration of VIDEO.md,
save it as `assets/narration.mp3`, and render again. `timeline.py` then transcribes the
recording (faster-whisper, word timestamps), finds the `ANCHOR:` sentence of every
chapter in it, and the animations of each chapter follow the spoken words; the
recording becomes the soundtrack.

## Files

```
film.py        the whole video on one timeline (opening mark, chapters, progress line)
timeline.py    chapter times from VIDEO.md and the recording
kit.py         product colours, titles, bars, counters, the measured numbers
scenes/        one build(film, chapter) function per chapter (s00 ... s09)
style.py       palette (Rocket Software brand), fonts, type scale
logo.py        the Rocket Software / Vertica lockup as vector, and its reveal
assets/        logos, fonts (and narration.mp3 once recorded)
```
