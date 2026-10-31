# Video (manim)

The animated video of the comparison, 6 minutes 32 seconds, 1920x1080 at 60 fps. The
narration is in [../VIDEO.md](../VIDEO.md); every number on screen is read from
`../results/` at render time (`kit.py`, `captions.py`), so the video always shows the
measured values.

## Setup

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install "manim>=0.19" faster-whisper numpy     # ffmpeg must be on PATH
```

Fonts: Calibri / Consolas when installed (also from Microsoft Office on macOS), otherwise
the metric-compatible Carlito and Inconsolata from `assets/fonts/` (registered by `style.py`).

Inputs, set in `../config.env` (not part of the repository):

- `NARRATION_DIR`: the recordings, one per chapter of VIDEO.md: `s00.mp3` ... `s10.mp3`
- `MUSIC_SRC`: the music track (WAV)

## Build

```bash
python audio.py words        # word times of the recordings (only when a recording changed)
python audio.py voice        # the recordings at one loudness
python audio.py music        # the music bed, lengthened to the film
python timeline.py           # print the clock
manim -ql film.py Film                               # draft, 480p15 (2 minutes)
python audio.py mix --draft                          # -> output/draft_<film>.mp4
manim -qh --fps 60 --disable_caching film.py Film    # final, 1080p60
python audio.py mix                                  # -> output/<film>.mp4
```

## How the clock works

- The recordings play one after the other with a pause of 1.1 s; the animations of a
  chapter wait for the words they show (`film.cue(chapter, "phrase")`: the script words of
  VIDEO.md matched to the word times of the transcription).
- The music is used from its start to 3:27 (its own fade-out). It is lengthened by one long
  repeat, `x[:b] + x[a:]`, with `a` a few seconds after the start and `b` before the final
  hits, chosen where both points sound alike (spectrogram similarity, sample-accurate
  alignment, equal-power cross-fade). The length of the chosen repeat sets the cold open
  (11.5 to 17.5 s), so the last hit of the music lands on the bloom of the lockup.
- Mix: voice at -16 LUFS, music alone at -20 LUFS, under the voice about 11 dB lower.
- After the music: the lockup stays 2.5 s in silence, then the disclaimer (6 s, no music).

## Files

```
film.py        the whole picture on one timeline: cold open, chapters, band, lockup, disclaimer
timeline.py    the clock: chapter times from the recordings, cue times of phrases, music fit
audio.py       word times, voice levels, music bed, final mix
captions.py    the caption band: chapter chips and captions at spoken phrases
kit.py         product colours, titles, bars, counters, the band, the measured numbers
scenes/        open.py, s00 ... s10 (one build(film, chapter) per chapter), disclaimer.py
style.py       palette (Rocket Software brand), fonts, type scale
logo.py        the Rocket Software / Vertica lockup as vector, and its reveal
assets/        logos, fonts
output/        word times, prepared audio, the film (git-ignored)
```
