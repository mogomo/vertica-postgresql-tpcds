"""
kit.py - shared pieces of the chapters: colours of the two products, titles, bars,
counters, the measured numbers (read from ../results, never typed in twice).
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

from style import *

REPO = Path(__file__).resolve().parent.parent
RUNS = {
    ("vertica", 10): "20261031-0132_sf10_vertica_tuned",
    ("postgresql", 10): "20261031-0145_sf10_postgresql_tuned",
    ("vertica", 100): "20261031-0335_sf100_vertica_tuned",
    ("postgresql", 100): "20261031-0506_sf100_postgresql_tuned",
    ("vertica", 1): "20261031-0054_sf1_vertica_smoke",
    ("postgresql", 1): "20261031-0106_sf1_postgresql_smoke",
}
# single queries run again with a longer limit
RERUNS = {
    ("postgresql", 10): "20261031-0212_sf10_postgresql_rerun-600s",
    ("postgresql", 100): "20261031-1010_sf100_postgresql_q30-1800s",
}

# Vertica carries the brand; PostgreSQL is drawn in a neutral grey, never a competitor
# colour.
V_FILL, V_TEXT = BRAND_PRIMARY, BRAND_SECONDARY
P_FILL, P_TEXT = "#6E6E7C", GRAY_TEXT


# --------------------------------------------------------------------------
# measured numbers
# --------------------------------------------------------------------------
def metrics(product: str, sf: int) -> dict:
    path = REPO / "results" / RUNS[(product, sf)] / "metrics.csv"
    return {r["metric"]: r["value"] for r in csv.DictReader(open(path))}


def best_times(product: str, sf: int, runs: dict = RUNS) -> dict:
    best = {}
    for r in csv.DictReader(open(REPO / "results" / runs[(product, sf)] / "timings.csv")):
        if r["status"] == "ok":
            best[r["query"]] = min(best.get(r["query"], 1e9), float(r["seconds"]))
    return best


def stopped_at(product: str, sf: int, query: str, runs: dict = RUNS) -> float | None:
    """The limit a query was stopped at (None when it finished)."""
    for r in csv.DictReader(open(REPO / "results" / runs[(product, sf)] / "timings.csv")):
        if r["query"] == query and r["status"] == "timeout":
            return float(r["seconds"])
    return None


def ratios(sf: int) -> list[float]:
    """PostgreSQL / Vertica best time, for the queries both finished."""
    v, p = best_times("vertica", sf), best_times("postgresql", sf)
    return sorted(p[q] / v[q] for q in p if q in v)


# --------------------------------------------------------------------------
# layout atoms
# --------------------------------------------------------------------------
def chapter_title(text: str) -> VGroup:
    t = body(text, size=FS_TITLE, color=WHITE_SOFT)
    t.move_to(TITLE_ANCHOR, aligned_edge=UL)
    rule = Line(ORIGIN, RIGHT * 0.9).set_stroke(BRAND_PRIMARY, 3)
    rule.next_to(t, DOWN, buff=0.14, aligned_edge=LEFT)
    return VGroup(t, rule)


def product_label(product: str, size: int = FS_BODY) -> Text:
    return body("Vertica" if product == "vertica" else "PostgreSQL", size=size,
                color=V_TEXT if product == "vertica" else P_TEXT)


def hbar(value: float, vmax: float, width: float, color: str, height: float = 0.42,
         dashed: bool = False) -> VMobject:
    """A horizontal bar growing to the right from its left edge; dashed = lower bound."""
    w = max(0.02, width * value / vmax)
    r = Rectangle(width=w, height=height).set_stroke(width=0).set_fill(color, 1.0)
    if dashed:
        r.set_fill(color, 0.35)
        outline = DashedVMobject(Rectangle(width=w, height=height), num_dashes=40)
        outline.set_stroke(GRAY_TEXT, 1.2)
        outline.move_to(r)
        return VGroup(r, outline)
    return r


def vbar(value: float, vmax: float, height: float, color: str, width: float = 0.9,
         dashed: bool = False) -> VMobject:
    h = max(0.02, height * value / vmax)
    r = Rectangle(width=width, height=h).set_stroke(width=0).set_fill(color, 1.0)
    if dashed:
        r.set_fill(color, 0.35)
        outline = DashedVMobject(Rectangle(width=width, height=h), num_dashes=40)
        outline.set_stroke(GRAY_TEXT, 1.2)
        outline.move_to(r)
        return VGroup(r, outline)
    return r


def counter(value: float, decimals: int = 0, size: int = FS_BIG, color: str = WHITE_SOFT,
            prefix: str = "", suffix: str = "") -> VGroup:
    """A number that counts up from 0 (animate its .tracker to .target)."""
    tracker = ValueTracker(0.0)

    def make():
        v = tracker.get_value()
        txt = f"{prefix}{v:,.{decimals}f}{suffix}"
        return body(txt, size=size, color=color)

    num = always_redraw(make)
    g = VGroup(num)
    g.tracker, g.target = tracker, value
    return g


def count_to(g: VGroup, run_time: float = 1.2) -> Animation:
    return g.tracker.animate(run_time=run_time, rate_func=EASE_OUT).set_value(g.target)


def pill(text: str, color: str = BRAND_PRIMARY, size: int = FS_CAPTION) -> VGroup:
    t = body(text, size=size, color=WHITE_SOFT)
    box = RoundedRectangle(corner_radius=0.18, width=t.width + 0.45, height=t.height + 0.3)
    box.set_stroke(color, 1.5).set_fill(color, 0.18)
    t.move_to(box)
    return VGroup(box, t)


def db_icon(h: float = 1.0, w: float = 0.8, color: str = V_TEXT) -> VGroup:
    """A database cylinder, stroke only."""
    ry = w / 5.0
    body_h = h - 2 * ry
    top = Ellipse(width=w, height=2 * ry).set_stroke(color, 2).move_to(UP * body_h / 2)
    left = Line([-w / 2, body_h / 2, 0], [-w / 2, -body_h / 2, 0]).set_stroke(color, 2)
    right = Line([w / 2, body_h / 2, 0], [w / 2, -body_h / 2, 0]).set_stroke(color, 2)
    bottom = Arc(radius=1, start_angle=PI, angle=PI).set_stroke(color, 2)
    bottom.stretch_to_fit_width(w).stretch_to_fit_height(ry).move_to([0, -body_h / 2 - ry / 2, 0])
    return VGroup(top, left, right, bottom)


def log_x(v: float, lo: float, hi: float, width: float) -> float:
    """Position of v on a logarithmic axis from lo to hi, centred on 0."""
    return (math.log10(v) - math.log10(lo)) / (math.log10(hi) - math.log10(lo)) * width - width / 2
