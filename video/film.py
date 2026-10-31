"""
film.py - the whole video on one timeline.

    manim -ql film.py Film                     # draft, 480p15
    manim -qh --fps 60 film.py Film            # final, 1080p60

The picture only: audio.py mix adds the voice and the music afterwards. Every chapter is
a `build(film, chapter)` function in scenes/, started when its recording starts
(timeline.py), and its animations wait for the words they show.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import timeline as TL                    # noqa: E402
from captions import band_items          # noqa: E402
from kit import *                        # noqa: E402

CHAPTERS = ["s00_cold_open", "s01_test", "s02_fair", "s03_storage", "s04_sf10",
            "s05_wins", "s06_breaks", "s07_sf100", "s08_limits", "s09_meaning", "s10_close"]
TITLE_HOLD = 1.2         # the title stays this long into the first words


class Film(MovingCameraScene):
    def now(self) -> float:
        return self.renderer.time

    def hold_until(self, t: float) -> None:
        d = t - self.now()
        if d > 1 / config.frame_rate:
            self.wait(d)
        elif d < -0.15:
            print(f"  !! late by {-d:.2f} s at film {t:.2f}")

    def cue(self, chapter: dict, phrase: str) -> float:
        """A little before `phrase` is spoken in the chapter."""
        return TL.cue_in(chapter, phrase) - 0.15

    def clear_stage(self, run_time: float = 0.5) -> None:
        keep = set(getattr(self, "persistent", []))
        gone = [m for m in self.mobjects if m not in keep]
        if gone:
            self.play(*[FadeOut(m) for m in gone], run_time=run_time)

    def construct(self):
        self.camera.background_color = "#000000"
        t = TL.load()
        self.timing = t
        scenes = t["scenes"]

        importlib.import_module("scenes.open").build(
            self, t_title=7.0, t_end=scenes[0]["start"] + TITLE_HOLD)

        band = Band(self, band_items(), t_end=t["lockup"] - 0.5)
        self.add_foreground_mobject(band)
        self.persistent = [band]

        for chapter, module in zip(scenes, CHAPTERS):
            if chapter is not scenes[0]:                # s00 waits for the title itself
                self.hold_until(chapter["start"] - 0.3)
            importlib.import_module(f"scenes.{module}").build(self, chapter)
            if chapter is not scenes[-1]:
                self.hold_until(chapter["end"] + 0.05)
                self.clear_stage()

        self.hold_until(t["music_len"] + TL.LOGO_HOLD - 0.5)
        self.clear_stage()
        importlib.import_module("scenes.disclaimer").build(self, TL.DISCLAIMER_LEN)
