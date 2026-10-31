"""S08 - what a time limit hides: the worst query that finished, its growth, 30 minutes."""
from kit import *


def build(f, ch):
    title = chapter_title("What a time limit hides")
    f.play(FadeIn(title), run_time=0.6)
    f.hold_until(f.cue(ch, "A query that was stopped"))
    a = body("“> 10 min”  =  at least 10 minutes.  How much more: unknown.", size=FS_BODY)
    a.to_edge(UP, buff=1.55).to_edge(LEFT, buff=0.9)
    f.play(FadeIn(a, shift=RIGHT * 0.2), run_time=0.7)

    # the worst ratio among the queries that finished: query 30 at SF10, 10-minute limit
    v10 = best_times("vertica", 10)["30"]
    p10 = best_times("postgresql", 10, RERUNS)["30"]
    f.hold_until(f.cue(ch, "Take the worst query that did finish"))
    q = caption("query 30, 12 GB: customers whose web returns are 20% above their state's average")
    q.next_to(a, DOWN, buff=0.55, aligned_edge=LEFT)
    f.play(FadeIn(q), run_time=0.5)
    lv = product_label("vertica")
    lp = product_label("postgresql")
    tv = body(f"{v10:.2f} s", size=FS_HEAD, color=V_TEXT)
    tp = body(f"{p10:,.0f} s", size=FS_HEAD, color=P_TEXT)
    grid = VGroup(lv, tv, lp, tp).arrange_in_grid(rows=2, cols=2, col_alignments="lr", buff=(0.6, 0.2))
    grid.next_to(q, DOWN, buff=0.35, aligned_edge=LEFT).shift(RIGHT * 0.3)
    f.play(FadeIn(lv), FadeIn(tv), run_time=0.5)
    f.hold_until(f.cue(ch, "Five hundred and eighty seconds"))
    f.play(FadeIn(lp), FadeIn(tp), run_time=0.5)
    f.hold_until(f.cue(ch, "Three thousand seven hundred times"))
    x = body(f"× {p10 / v10:,.0f}", size=FS_BIG, color=WHITE_SOFT).next_to(grid, RIGHT, buff=1.2)
    f.play(FadeIn(x, scale=0.9), run_time=0.6)

    # measured growth from SF1 to SF10, the estimate for SF100, and the 30-minute run
    p1, v1 = best_times("postgresql", 1)["30"], best_times("vertica", 1)["30"]
    f.hold_until(f.cue(ch, "From one gigabyte to twelve"))
    g = body(f"1 GB → 12 GB:  {p1:.1f} s → {p10:,.0f} s,  × {p10 / p1:.0f} for 10× the data"
             f"   (Vertica × {v10 / v1:.1f})", size=FS_BODY, color=P_TEXT)
    g.next_to(grid, DOWN, buff=0.55, aligned_edge=LEFT).shift(LEFT * 0.3)
    f.play(FadeIn(g, shift=RIGHT * 0.2), run_time=0.7)
    f.hold_until(f.cue(ch, "that points to about fifteen hours"))
    est = p10 * p10 / p1
    e = body(f"102 GB, the same growth:  ≈ {est / 3600:.0f} hours", size=FS_BODY, color=P_TEXT)
    e.next_to(g, DOWN, buff=0.3, aligned_edge=LEFT)
    f.play(FadeIn(e, shift=RIGHT * 0.2), run_time=0.7)

    f.hold_until(f.cue(ch, "So we gave it thirty minutes"))
    limit = stopped_at("postgresql", 100, "30", RERUNS)
    W = 6.0
    frame = Rectangle(width=W, height=0.36).set_stroke(GRAY_TEXT, 1.2)
    frame.next_to(e, DOWN, buff=0.55, aligned_edge=LEFT)
    fill = Rectangle(width=W, height=0.36).set_stroke(width=0).set_fill(P_FILL, 0.9).move_to(frame)
    ends = VGroup(tiny("0").next_to(frame, DOWN, buff=0.1, aligned_edge=LEFT),
                  tiny("30 min").next_to(frame, DOWN, buff=0.1, aligned_edge=RIGHT))
    f.play(Create(frame), FadeIn(ends), run_time=0.5)
    f.play(GrowFromEdge(fill, LEFT), run_time=1.4, rate_func=linear)
    f.hold_until(f.cue(ch, "It did not finish"))
    verdict = ("stopped at 30 min: not finished" if limit else "finished")
    s = body(verdict, size=FS_BODY, color=WHITE_SOFT).next_to(frame, RIGHT, buff=0.35)
    f.play(FadeIn(s), run_time=0.5)
    f.hold_until(f.cue(ch, "Every PostgreSQL total"))
    fl = caption("totals marked ≥ are floors, not estimates", color=WHITE_SOFT).to_edge(DOWN, buff=0.9)
    f.play(FadeIn(fl), run_time=0.6)
