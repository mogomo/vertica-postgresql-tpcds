"""
timeline.py - when each chapter starts and ends.

The narration in ../VIDEO.md is the script: one `[SCENE NN — Title]` block per chapter,
each with an `ANCHOR:` line (its first sentence). Two sources of timing:

  * assets/narration.mp3 present: the recording is transcribed with faster-whisper
    (word timestamps) and every anchor sentence is located in it; a chapter starts
    where its anchor is spoken.
  * no recording yet: every chapter lasts as long as its words take at WPM words per
    minute plus a short pause, so the film can be drafted before the voice exists.

    python timeline.py     # print the chapters and write output/timing.json
"""

from __future__ import annotations

import json
import re
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCRIPT = ROOT.parent / "VIDEO.md"
NARRATION = ROOT / "assets" / "narration.mp3"
TIMING = ROOT / "output" / "timing.json"

WPM = 140            # reading pace of the estimate
PAUSE = 1.2          # seconds between chapters in the estimate
LEAD_IN = 3.5        # opening logo before the voice starts
TAIL = 5.0           # closing logo after the voice ends

_SCENE = re.compile(r"^\[SCENE (\d+)\s*[—-]\s*(.*?)\]")


def parse_script(path: Path = SCRIPT) -> list[dict]:
    """The chapters of the narration block in VIDEO.md: id, title, anchor, text."""
    text = path.read_text()
    block = text.split("## Narration", 1)[1].split("```", 2)[1]
    scenes: list[dict] = []
    for line in block.splitlines():
        m = _SCENE.match(line.strip())
        if m:
            scenes.append({"id": f"s{int(m.group(1)):02d}", "title": m.group(2).strip(),
                           "anchor": "", "text": ""})
        elif scenes and line.strip().upper().startswith("ANCHOR:"):
            scenes[-1]["anchor"] = line.split(":", 1)[1].strip()
        elif scenes and line.strip():
            scenes[-1]["text"] += " " + line.strip()
    return scenes


def _words(s: str) -> list[str]:
    return re.findall(r"[a-z0-9']+", s.lower())


def estimate(scenes: list[dict]) -> dict:
    t = LEAD_IN
    for sc in scenes:
        sc["start"] = t
        t += len(_words(sc["text"])) / WPM * 60 + PAUSE
        sc["end"] = t
    return {"source": "estimate", "total": t + TAIL, "scenes": scenes}


def measure(scenes: list[dict], model: str = "medium") -> dict:
    from faster_whisper import WhisperModel
    segments, info = WhisperModel(model, compute_type="int8").transcribe(
        str(NARRATION), word_timestamps=True, language="en")
    words = [(w.start, w.word) for seg in segments for w in seg.words]
    spoken = [_words(w)[0] if _words(w) else "" for _, w in words]
    pos = 0
    for sc in scenes:
        target = _words(sc["anchor"])
        best, best_i = 0.0, None
        for i in range(pos, len(spoken) - len(target) + 1):
            r = SequenceMatcher(None, spoken[i:i + len(target)], target).ratio()
            if r > best:
                best, best_i = r, i
        if best_i is None or best < 0.75:
            raise SystemExit(f"anchor of {sc['id']} not found in the recording "
                             f"(best match {best:.2f}): {sc['anchor']}")
        sc["start"] = LEAD_IN + words[best_i][0]
        pos = best_i + len(target)
    for a, b in zip(scenes, scenes[1:]):
        a["end"] = b["start"]
    scenes[-1]["end"] = LEAD_IN + info.duration
    return {"source": "narration.mp3", "total": LEAD_IN + info.duration + TAIL, "scenes": scenes}


def build() -> dict:
    scenes = parse_script()
    timing = measure(scenes) if NARRATION.exists() else estimate(scenes)
    timing["lead_in"], timing["tail"] = LEAD_IN, TAIL
    TIMING.parent.mkdir(exist_ok=True)
    TIMING.write_text(json.dumps(timing, indent=2))
    return timing


def load() -> dict:
    """Timing for the render: output/timing.json when it is newer than its sources."""
    srcs = [SCRIPT] + ([NARRATION] if NARRATION.exists() else [])
    if TIMING.exists() and all(TIMING.stat().st_mtime > s.stat().st_mtime for s in srcs):
        return json.loads(TIMING.read_text())
    return build()


if __name__ == "__main__":
    t = build()
    for sc in t["scenes"]:
        print(f"{sc['id']}  {sc['start']:7.1f} - {sc['end']:7.1f}  {sc['title']}")
    print(f"total {t['total']:.1f} s ({t['source']})")
