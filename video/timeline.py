"""
timeline.py - the one clock of the film.

The narration is the master clock: one recording per chapter (s00.mp3 ... s10.mp3, the
blocks of ../VIDEO.md), played one after the other with a short pause between them. Every
picture event is addressed by what is *said* (chapter + phrase), never by a typed second.

    0             cold open, music only: the race of the 99 queries, the title
    OPEN_LEN      s00 ... s10, the voice; the caption band from s01 on
    MUSIC_LEN     the music ends; its last hit lands on the bloom of the lockup
    + LOGO_HOLD   the lockup stays in silence
    + DISCLAIMER  the disclaimer, no music

The music bed is the track lengthened by one long inner repeat (audio.py music); the
length of the repeat decides OPEN_LEN to the frame, so the last hit of the music lands on
the lockup whatever the voice.

    python timeline.py     # print the clock
"""

from __future__ import annotations

import json
import re
import subprocess
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
SCRIPT = REPO / "VIDEO.md"
OUT = ROOT / "output"
AUDIO = OUT / "audio"
WORDS = OUT / "words.json"            # word times of the recordings (audio.py words)
MUSIC_INFO = AUDIO / "music.json"     # the repeat chosen by audio.py music

OPEN_NOM = 15.0          # cold open before the first word (adjusted by the music fit)
PAUSE = 1.1              # between two chapters
REVEAL = 3.0             # lockup: mark drawn (1.7 s) + words (1.3 s), then the bloom
LOGO_HOLD = 2.5          # the lockup stays after the music ends
DISCLAIMER_LEN = 6.0     # after the end, no music

# the music track: used from 0 to SRC_END (its own fade-out); the last hit before it
SRC_END = 207.0


def _config() -> dict:
    """NARRATION_DIR and MUSIC_SRC from ../config.env (git-ignored)."""
    cfg = {"NARRATION_DIR": str(REPO / "work" / "narration"), "MUSIC_SRC": ""}
    path = REPO / "config.env"
    if path.exists():
        for line in path.read_text().splitlines():
            m = re.match(r'^\s*(NARRATION_DIR|MUSIC_SRC)=["\']?(.*?)["\']?\s*$', line)
            if m:
                cfg[m.group(1)] = m.group(2)
    return cfg


CONFIG = _config()
NARRATION_DIR = Path(CONFIG["NARRATION_DIR"])


def _dur(p: Path) -> float:
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                 "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout)


_SCENE = re.compile(r"^\[SCENE (\d+)\s*[—-]\s*(.*?)\]")


def parse_script(path: Path = SCRIPT) -> list[dict]:
    """The chapters of the narration block in VIDEO.md: id, title, text."""
    block = path.read_text().split("## Narration", 1)[1].split("```", 2)[1]
    scenes: list[dict] = []
    for line in block.splitlines():
        m = _SCENE.match(line.strip())
        if m:
            scenes.append({"id": f"s{int(m.group(1)):02d}", "title": m.group(2).strip(), "text": ""})
        elif scenes and line.strip() and not line.strip().upper().startswith("ANCHOR:"):
            scenes[-1]["text"] += " " + line.strip()
    return scenes


def _words(s: str) -> list[str]:
    s = s.lower().replace("postgresk", "postgresql")
    return re.findall(r"[a-z0-9']+", s)


def _word_times(script_text: str, heard: list) -> list[float]:
    """Start time of every word of the script: script words matched to the words the
    transcription heard; words it spelled differently (numbers in digits) interpolated."""
    sw = _words(script_text)
    hw, ht = [], []
    for w, t0, _ in heard:
        for tok in _words(w):
            hw.append(tok)
            ht.append(t0)
    times: list[float | None] = [None] * len(sw)
    for a, b, n in SequenceMatcher(None, sw, hw, autojunk=False).get_matching_blocks():
        for k in range(n):
            times[a + k] = ht[b + k]
    known = [(i, t) for i, t in enumerate(times) if t is not None]
    for i in range(len(times)):
        if times[i] is None:
            before = [(j, t) for j, t in known if j < i]
            after = [(j, t) for j, t in known if j > i]
            if before and after:
                (j0, t0), (j1, t1) = before[-1], after[0]
                times[i] = t0 + (t1 - t0) * (i - j0) / (j1 - j0)
            else:
                times[i] = (before[-1][1] if before else after[0][1] if after else 0.0)
    return times


def build() -> dict:
    scenes = parse_script()
    heard = json.loads(WORDS.read_text())
    for sc in scenes:
        src = AUDIO / f"{sc['id']}.wav"
        sc["len"] = _dur(src) if src.exists() else heard[sc["id"]]["duration"]
        sc["tokens"] = _words(sc["text"])
        sc["times"] = _word_times(sc["text"], heard[sc["id"]]["words"])

    def layout(open_len: float) -> None:
        t = open_len
        for sc in scenes:
            sc["start"] = round(t * 60) / 60
            sc["end"] = sc["start"] + sc["len"]
            t = sc["end"] + PAUSE

    def lockup_at() -> float:
        return cue_in(scenes[-1], "Vertica, from Rocket Software") - 0.1

    layout(OPEN_NOM)
    music = json.loads(MUSIC_INFO.read_text()) if MUSIC_INFO.exists() else None
    hit_tail = (SRC_END - music["hit"]) if music else 3.7
    music_nom = lockup_at() + REVEAL + 0.15 + hit_tail
    repeat_nom = music_nom - SRC_END
    open_len = OPEN_NOM
    if music:
        open_len = OPEN_NOM + (music["repeat"] - repeat_nom)
        layout(open_len)
    music_len = lockup_at() + REVEAL + 0.15 + hit_tail
    return {"open": open_len, "scenes": scenes, "lockup": lockup_at(),
            "music_len": music_len, "repeat_nom": repeat_nom,
            "total": music_len + LOGO_HOLD + DISCLAIMER_LEN}


def cue_in(sc: dict, phrase: str, end: bool = False) -> float:
    """Film second at which `phrase` is spoken in chapter sc (its first word; end=True:
    the start of its last word)."""
    target = _words(phrase)
    toks = sc["tokens"]
    for i in range(len(toks) - len(target) + 1):
        if toks[i:i + len(target)] == target:
            return sc["start"] + sc["times"][i + (len(target) - 1 if end else 0)]
    raise ValueError(f"'{phrase}' is not in the narration of {sc['id']}")


_CACHE: dict | None = None


def load() -> dict:
    global _CACHE
    if _CACHE is None:
        _CACHE = build()
    return _CACHE


def chapter(cid: str) -> dict:
    return next(sc for sc in load()["scenes"] if sc["id"] == cid)


def at(cid: str, phrase: str, end: bool = False) -> float:
    return cue_in(chapter(cid), phrase, end)


if __name__ == "__main__":
    t = load()
    print(f"cold open   0.0 - {t['open']:6.1f}")
    for sc in t["scenes"]:
        print(f"{sc['id']}  {sc['start']:7.1f} - {sc['end']:7.1f}  {sc['title']}")
    print(f"lockup {t['lockup']:.1f}  music ends {t['music_len']:.1f} (repeat {t['repeat_nom']:.1f} s nominal)"
          f"  film {t['total']:.1f} s")
