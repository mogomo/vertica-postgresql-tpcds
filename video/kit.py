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
    rule = Line(ORIGIN, RIGHT * t.width).set_stroke(color=[BRAND_PRIMARY, PINK], width=3)
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
            prefix: str = "", suffix: str = "", place=None) -> VGroup:
    """A number that counts up from 0 (animate its .tracker to .target). place(m) puts
    the text where it belongs; it runs inside the redraw, every frame."""
    tracker = ValueTracker(0.0)

    def make():
        v = tracker.get_value()
        txt = f"{prefix}{v:,.{decimals}f}{suffix}"
        m = body(txt, size=size, color=color)
        return place(m) if place else m

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


# --------------------------------------------------------------------------
# a Vertica node, its depot, communal storage: the cluster drawing of the companion
# roadmap film, one closed outline each so a node can grow into a cluster
# --------------------------------------------------------------------------
def _arc_pts(cx: float, cy: float, rx: float, ry: float, a0: float, a1: float, n: int = 44) -> list:
    return [np.array([cx + rx * np.cos(t), cy + ry * np.sin(t), 0.0]) for t in np.linspace(a0, a1, n)]


def _outline(points, color: str, stroke: float, fill: float) -> VMobject:
    m = VMobject()
    m.set_points_as_corners(points + [points[0]])
    return m.set_stroke(color, stroke).set_fill(color, fill)


def stroke_node(w: float = 1.15, h: float = 0.9, color: str = V_TEXT, stroke: float = 1.8) -> VMobject:
    return RoundedRectangle(corner_radius=0.10, width=w, height=h).set_stroke(color, stroke).set_fill(color, 0.07)


def node_detail(node, color: str = V_TEXT, stroke: float = 1.8) -> VGroup:
    """The bezel and two status lights that make a rectangle read as a machine."""
    w, h, c = node.width, node.height, node.get_center()
    bezel = Line([c[0] - w / 2 + 0.09, c[1] + h / 2 - 0.16, 0], [c[0] + w / 2 - 0.09, c[1] + h / 2 - 0.16, 0])
    bezel.set_stroke(color, stroke * 0.7, 0.7)
    leds = VGroup(*[Dot([c[0] - w / 2 + 0.17 + i * 0.11, c[1] + h / 2 - 0.08, 0], radius=0.024, color=color)
                    for i in range(2)])
    return VGroup(bezel, leds)


def stroke_cylinder(w: float = 0.8, h: float = 1.0, color: str = V_TEXT, stroke: float = 1.8) -> VGroup:
    """A disk or a depot: one outline plus the front lip."""
    rx, ry = w / 2, w / 5.0
    by = max(0.02, h / 2 - ry)
    pts = (_arc_pts(0, by, rx, ry, PI, 0) + [np.array([rx, -by, 0.0])]
           + _arc_pts(0, -by, rx, ry, 0, -PI) + [np.array([-rx, by, 0.0])])
    lip = VMobject().set_points_as_corners(_arc_pts(0, by, rx, ry, -PI, 0))
    lip.set_stroke(color, stroke * 0.75, 0.75)
    return VGroup(_outline(pts, color, stroke, 0.07), lip)


def stroke_bucket(w: float = 1.25, h: float = 1.05, color: str = V_TEXT, stroke: float = 1.8) -> VGroup:
    """Communal (object) storage: a bucket, one outline plus the near edge of the rim."""
    ry, bw = w / 5.0, w * 0.70
    top_y, bot_y = h / 2 - ry, -h / 2 + ry * 0.9
    pts = (_arc_pts(0, top_y, w / 2, ry, PI, 0) + [np.array([bw / 2, bot_y, 0.0])]
           + _arc_pts(0, bot_y, bw / 2, ry * 0.85, 0, -PI) + [np.array([-w / 2, top_y, 0.0])])
    lip = VMobject().set_points_as_corners(_arc_pts(0, top_y, w / 2, ry, -PI, 0))
    lip.set_stroke(color, stroke * 0.75, 0.75)
    return VGroup(_outline(pts, color, stroke, 0.09), lip)


def dashed_box(mobj, color: str = GRAY_TEXT, buff: float = 0.25, dashes: int = 40) -> DashedVMobject:
    r = RoundedRectangle(corner_radius=0.14, width=mobj.width + 2 * buff, height=mobj.height + 2 * buff)
    return DashedVMobject(r.move_to(mobj), num_dashes=dashes).set_stroke(color, 1.2, 0.85)


def log_x(v: float, lo: float, hi: float, width: float) -> float:
    """Position of v on a logarithmic axis from lo to hi, centred on 0."""
    return (math.log10(v) - math.log10(lo)) / (math.log10(hi) - math.log10(lo)) * width - width / 2


# --------------------------------------------------------------------------
# the caption band (chapter chip, caption, address) - the format of the
# companion films
# --------------------------------------------------------------------------
PX = config.frame_width / 1920.0          # one output pixel (1080p) in scene units
BAND_H = 64                               # band height, output pixels
BAND_TOP = -FRAME_H / 2 + BAND_H * PX     # keep content above this line
ADDRESS = "github.com/mogomo/vertica-postgresql-tpcds"


def chip(text: str, size: int = 15) -> VGroup:
    t = body(text, size=size, weight=BOLD)
    box = RoundedRectangle(corner_radius=0.12, width=t.width + 0.36, height=t.height + 0.22)
    box.set_fill(PURPLE, 1).set_stroke(PINK, 1.4, 0.85)
    t.move_to(box)
    return VGroup(box, t)


class Band(VGroup):
    """The bottom band. Chips and captions are built once; an updater shows the one
    that belongs to the current film second (cross-fades of FADE seconds), so the
    band runs beside the chapters without taking part in their animations.

    items: [(t, chapter_label, caption)], sorted by t; shown from items[0] to t_end."""

    FADE = 0.35

    def __init__(self, scene, items, t_end):
        super().__init__()
        self.scene, self.t_end = scene, t_end
        y = -FRAME_H / 2 + BAND_H * PX / 2
        bar = Rectangle(width=FRAME_W, height=BAND_H * PX).set_fill("#07070D", 0.92).set_stroke(width=0)
        bar.move_to([0, y, 0])
        edge = Line([-FRAME_W / 2, BAND_TOP, 0], [FRAME_W / 2, BAND_TOP, 0])
        edge.set_stroke(color=[ELECTRIC, MAGENTA, PINK], width=2.5)
        addr = body(ADDRESS, size=11, color=GRAY_TEXT).move_to([FRAME_W / 2 - 24 * PX, y, 0], aligned_edge=RIGHT)
        self.chrome = VGroup(bar, edge, addr)
        self.add(self.chrome)
        self.t0 = items[0][0]
        self.chips, self.caps = [], []
        chips = {}
        for i, (t, label, text) in enumerate(items):
            if label not in chips:
                c = chip(label, size=11).move_to([-FRAME_W / 2 + 24 * PX, y, 0], aligned_edge=LEFT)
                chips[label] = [c, t, None]
                self.chips.append(chips[label])
                self.add(c)
            t1 = items[i + 1][0] if i + 1 < len(items) else t_end
            chips[label][2] = t1
            cap = body(text, size=18).move_to(chips[label][0].get_right() + RIGHT * 0.24, aligned_edge=LEFT)
            cap.set_y(y)
            self.caps.append((cap, t, t1))
            self.add(cap)
        self.add_updater(lambda m: m._show(m.scene.renderer.time))
        self._show(0.0)

    def _alpha(self, now, t0, t1):
        if now < t0 or now > t1 + self.FADE:
            return 0.0
        return min(1.0, (now - t0) / self.FADE, max(0.0, (t1 + self.FADE - now) / self.FADE))

    def _show(self, now):
        a = self._alpha(now, self.t0, self.t_end)
        bar, edge, addr = self.chrome
        bar.set_fill(opacity=0.92 * a)
        edge.set_stroke(opacity=a)
        addr.set_opacity(a)
        for c, t0, t1 in self.chips:
            c[0].set_fill(opacity=self._alpha(now, t0, t1)).set_stroke(opacity=0.85 * self._alpha(now, t0, t1))
            c[1].set_opacity(self._alpha(now, t0, t1))
        for cap, t0, t1 in self.caps:
            cap.set_opacity(self._alpha(now, t0, t1))


def power_run(product: str, sf: int) -> list[tuple[str, float, str]]:
    """The best iteration of a power run, in run order: (query, seconds, status)."""
    rows = list(csv.DictReader(open(REPO / "results" / RUNS[(product, sf)] / "timings.csv")))
    total = {}
    for r in rows:
        total[r["iteration"]] = total.get(r["iteration"], 0.0) + float(r["seconds"])
    best = min(total, key=total.get)
    return [(r["query"], float(r["seconds"]), r["status"]) for r in rows if r["iteration"] == best]
