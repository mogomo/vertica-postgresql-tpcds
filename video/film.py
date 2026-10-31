"""
film.py - the whole video on one timeline.

    manim -ql film.py Film                     # draft, 480p15
    manim -qh --fps 60 film.py Film            # final, 1080p60

Every chapter is a `build(film, chapter)` function in scenes/, played at the time
timeline.py gives it, so picture and narration share one clock. With
assets/narration.mp3 present the recording is added as the soundtrack.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import timeline                          # noqa: E402
from logo import lockup_vector, reveal_lockup, rocket_software_mark   # noqa: E402
from style import *                      # noqa: E402

CHAPTERS = ["s00_cold_open", "s01_test", "s02_fair", "s03_storage", "s04_sf10",
            "s05_wins", "s06_breaks", "s07_sf100", "s08_meaning", "s09_close"]


class Film(MovingCameraScene):
    def now(self) -> float:
        return self.renderer.time

    def hold_until(self, t: float) -> None:
        d = t - self.now()
        if d > 1 / config.frame_rate:
            self.wait(d)

    def cue(self, chapter: dict, phrase: str) -> float:
        """When `phrase` is spoken in the chapter: its share of the chapter's words,
        placed between the chapter's start and end (minus the pause at the end)."""
        words = timeline._words(chapter["text"])
        target = timeline._words(phrase)
        n = len(target)
        for i in range(len(words) - n + 1):
            if words[i:i + n] == target:
                span = chapter["end"] - chapter["start"] - timeline.PAUSE * 0.8
                return chapter["start"] + span * i / max(1, len(words)) - 0.2
        raise ValueError(f"'{phrase}' is not in the narration of {chapter['id']}")

    def clear_stage(self, run_time: float = 0.5) -> None:
        keep = set(getattr(self, "persistent", []))
        gone = [m for m in self.mobjects if m not in keep]
        if gone:
            self.play(*[FadeOut(m) for m in gone], run_time=run_time)

    def construct(self):
        timing = timeline.load()
        if timeline.NARRATION.exists():
            self.add_sound(str(timeline.NARRATION), time_offset=timing["lead_in"])
        self.timing = timing

        # opening: the Rocket Software mark, then the voice starts
        mark = rocket_software_mark(height=1.4)
        self.play(FadeIn(mark, scale=0.96), run_time=1.0)
        self.hold_until(timing["lead_in"] - 0.8)
        self.play(FadeOut(mark), run_time=0.6)

        # progress line along the bottom edge
        total = timing["total"]
        progress = always_redraw(lambda: Line(
            [-FRAME_W / 2, -FRAME_H / 2 + 0.04, 0],
            [-FRAME_W / 2 + FRAME_W * min(1.0, self.now() / total), -FRAME_H / 2 + 0.04, 0],
        ).set_stroke(GRAY_TEXT, 1.5, 0.3))
        self.add(progress)
        self.persistent = [progress]

        for chapter, module in zip(timing["scenes"], CHAPTERS):
            self.hold_until(chapter["start"] - 0.3)
            importlib.import_module(f"scenes.{module}").build(self, chapter)
            if chapter is not timing["scenes"][-1]:
                self.hold_until(chapter["end"] - 0.6)
                self.clear_stage()
        self.hold_until(total)
