"""S05 - where PostgreSQL wins: an index finds two weeks out of five years."""
from kit import *


def build(f, ch):
    title = chapter_title("Where PostgreSQL wins")
    f.play(FadeIn(title), run_time=0.6)
    years = Rectangle(width=11, height=0.6).set_stroke(GRAY_TEXT, 1).set_fill(GRAY_TEXT, 0.08).move_to(UP * 0.4)
    yl = VGroup(*[tiny(str(1998 + i)).move_to(years.get_left() + RIGHT * (1.1 + 2.2 * i) + DOWN * 0.55) for i in range(5)])
    cap = caption("store_sales: five years of sales").next_to(years, UP, buff=0.95)
    f.play(FadeIn(years), FadeIn(yl), FadeIn(cap), run_time=0.8)
    f.hold_until(f.cue(ch, "Query five reports two weeks"))
    win = Rectangle(width=0.085, height=0.6).set_stroke(width=0).set_fill(P_TEXT, 1).move_to(years.get_left() + RIGHT * 6.2 + UP * 0.4 + DOWN * 0.4)
    wl = caption("14 days", color=P_TEXT).next_to(win, UP, buff=0.15)
    f.play(FadeIn(win), FadeIn(wl), run_time=0.6)
    f.hold_until(f.cue(ch, "walks the index"))
    idx = mono("index on the date key", size=FS_CAPTION, color=P_TEXT).move_to(DOWN * 1.4 + RIGHT * 2.4)
    arr = Arrow(idx.get_top(), win.get_bottom(), buff=0.1, stroke_width=2, tip_length=0.15, color=P_TEXT)
    f.play(FadeIn(idx), GrowArrow(arr), run_time=0.8)
    v10, p10 = best_times("vertica", 10)["05"], best_times("postgresql", 10)["05"]
    v100, p100 = best_times("vertica", 100)["05"], best_times("postgresql", 100)["05"]
    tab = VGroup(
        VGroup(caption("query 5"), product_label("vertica", FS_CAPTION), product_label("postgresql", FS_CAPTION)),
        VGroup(caption("12 GB"), body(f"{v10:.1f} s", size=FS_BODY, color=V_TEXT), body(f"{p10:.1f} s", size=FS_BODY, color=P_TEXT)),
        VGroup(caption("102 GB"), body(f"{v100:.1f} s", size=FS_BODY, color=V_TEXT), body(f"{p100:.1f} s", size=FS_BODY, color=P_TEXT)))
    for row in tab:
        for i, c in enumerate(row):
            c.move_to([-5.4 + i * 1.9, 0, 0], aligned_edge=LEFT)
    tab.arrange(DOWN, buff=0.3, aligned_edge=LEFT).move_to(LEFT * 3.4 + DOWN * 1.9)
    f.play(LaggedStart(*[FadeIn(r) for r in tab], lag_ratio=0.3), run_time=1.0)
    f.hold_until(f.cue(ch, "a fair test has to show it"))
    f.play(Circumscribe(VGroup(tab[1][2], tab[2][2]), color=P_TEXT, buff=0.1), run_time=1.0)
