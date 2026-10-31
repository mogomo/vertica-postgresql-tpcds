"""S04 - the 99 queries at scale factor 10: totals, then the queries one by one."""
from kit import *


def build(f, ch):
    title = chapter_title("Twelve gigabytes")
    f.play(FadeIn(title), run_time=0.6)
    v = float(metrics("vertica", 10)["power_best_iteration_seconds"])
    p = float(metrics("postgresql", 10)["power_best_iteration_seconds"])
    nf = int(metrics("postgresql", 10)["queries_not_finished"])
    vmax = p * 1.05
    bv = hbar(v, vmax, 8.5, V_FILL, 0.55)
    bp = hbar(p, vmax, 8.5, P_FILL, 0.55, dashed=True)
    lv, lp = product_label("vertica"), product_label("postgresql")
    for bar, lab, y in ((bv, lv, 1.1), (bp, lp, 0.0)):
        bar.move_to([-4.6, y, 0], aligned_edge=LEFT)
        lab.next_to(bar, LEFT, buff=0.3).align_to([-4.75, 0, 0], RIGHT)
    cv = counter(v, 0, FS_HEAD, V_TEXT, suffix=" s", place=lambda m: m.next_to(bv, RIGHT, buff=0.25))
    cp = counter(p, 0, FS_HEAD, P_TEXT, prefix="≥ ", suffix=" s", place=lambda m: m.next_to(bp, RIGHT, buff=0.25))
    f.hold_until(f.cue(ch, "Vertica ran all ninety-nine"))
    f.play(FadeIn(lv), GrowFromEdge(bv, LEFT), run_time=0.8)
    f.add(cv)
    f.play(count_to(cv, 0.8))
    f.hold_until(f.cue(ch, "PostgreSQL needed at least"))
    f.play(FadeIn(lp), GrowFromEdge(bp, LEFT), run_time=1.4)
    f.add(cp)
    f.play(count_to(cp, 1.0))
    f.hold_until(f.cue(ch, "eight queries did not finish"))
    nfl = caption(f"{nf} queries stopped at their 60 s limit (counted with the limit)", color=P_TEXT)
    nfl.next_to(bp, DOWN, buff=0.3, aligned_edge=LEFT)
    f.play(FadeIn(nfl), run_time=0.6)

    # every query: PostgreSQL time / Vertica time, on a log axis
    f.hold_until(f.cue(ch, "look at the queries one by one"))
    cv.clear_updaters(); cp.clear_updaters()
    f.play(FadeOut(VGroup(bv, bp, lv, lp, cv, cp, nfl)), run_time=0.5)
    lo, hi, W = 0.05, 500.0, 11.0
    axis = Line([-W / 2, -1.2, 0], [W / 2, -1.2, 0]).set_stroke(GRAY_TEXT, 1.2)
    ticks = VGroup()
    for x, t in ((0.1, "10× faster"), (1, "same"), (2, "2×"), (10, "10×"), (100, "100× slower")):
        px = log_x(x, lo, hi, W)
        ticks.add(VGroup(Line([px, -1.28, 0], [px, -1.12, 0]).set_stroke(GRAY_TEXT, 1.2),
                         tiny(t).move_to([px, -1.55, 0])))
    axl = caption("PostgreSQL time ÷ Vertica time, per query (best of 3)").move_to([0, -2.1, 0])
    f.play(Create(axis), FadeIn(ticks), FadeIn(axl), run_time=0.6)
    rs = ratios(10)
    dots = VGroup()
    counts = {}
    for r in rs:
        px = log_x(max(lo, min(hi, r)), lo, hi, W)
        k = round(px / 0.13)
        counts[k] = counts.get(k, 0) + 1
        dots.add(Dot([px, -1.0 + 0.16 * counts[k], 0], radius=0.065,
                     color=V_TEXT if r <= 1 else P_TEXT))
    f.play(LaggedStart(*[FadeIn(d, shift=DOWN * 0.2) for d in dots], lag_ratio=0.02), run_time=1.3)
    f.hold_until(f.cue(ch, "On seven of them"))
    fast = VGroup(*[d for d, r in zip(dots, rs) if r <= 1])
    t7 = caption(f"{len(fast)} queries: PostgreSQL as fast or faster", color=V_TEXT)
    t7.move_to([-W / 2, -0.15, 0], aligned_edge=LEFT)
    f.play(Indicate(fast, color=WHITE_SOFT, scale_factor=1.6), FadeIn(t7), run_time=1.0)
    f.hold_until(f.cue(ch, "were within a factor of two"))
    n2 = sum(r < 2 for r in rs)
    x1, x2 = log_x(1, lo, hi, W), log_x(2, lo, hi, W)
    band = Rectangle(width=log_x(2, lo, hi, W) - log_x(lo, lo, hi, W), height=2.6).set_stroke(width=0).set_fill(WHITE_SOFT, 0.06)
    band.move_to([(-W / 2 + x2) / 2, 0.1, 0])
    t2 = caption(f"{n2} within 2×").move_to([-W / 2 + 0.1, 1.15, 0], aligned_edge=LEFT)
    f.play(FadeIn(band), FadeIn(t2), run_time=0.7)
    f.hold_until(f.cue(ch, "The typical query"))
    med = rs[len(rs) // 2]
    xm = log_x(med, lo, hi, W)
    ml = DashedLine([xm, -1.2, 0], [xm, 2.0, 0]).set_stroke(WHITE_SOFT, 1.5)
    mt = body(f"median {med:.1f}×", size=FS_BODY).next_to(ml, UP, buff=0.1)
    f.play(Create(ml), FadeIn(mt), run_time=0.8)
