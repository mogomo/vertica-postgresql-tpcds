"""Cold open, music only: the 99 queries of the 102 GB power run as a race, then the title.

When Vertica has finished all 99 queries, PostgreSQL is still at an early query - both
runs drawn from their timings, in run order, on one compressed clock."""
from kit import *

COLS, ROWS, CELL, GAP = 33, 3, 0.2, 0.06


def grid(color) -> VGroup:
    cells = VGroup(*[Square(CELL).set_stroke(GRAY_TEXT, 1, 0.35).set_fill(color, 0)
                     for _ in range(COLS * ROWS)])
    cells.arrange_in_grid(ROWS, COLS, buff=GAP)
    return cells


def build(f, t_title: float, t_end: float):
    v_run, p_run = power_run("vertica", 100), power_run("postgresql", 100)
    v_total = sum(s for _, s, _ in v_run)
    ends = lambda run: [sum(s for _, s, _ in run[:i + 1]) for i in range(len(run))]
    v_ends, p_ends = ends(v_run), ends(p_run)
    p_done = sum(e <= v_total for e in p_ends)

    head = VGroup(body("99 analytic queries, one after the other", size=40, weight=BOLD),
                  body("102 GB of raw data   ·   one machine   ·   the same queries", size=24, color=LILAC)
                  ).arrange(DOWN, buff=0.18).move_to(UP * 3.0)
    gv, gp = grid(V_FILL), grid(P_FILL)
    lv = body("Vertica", size=28, weight=BOLD, color=V_TEXT)
    lp = body("PostgreSQL", size=28, weight=BOLD, color=P_TEXT)
    gv.move_to(UP * 0.95 + RIGHT * 0.6)
    gp.move_to(DOWN * 0.95 + RIGHT * 0.6)
    lv.next_to(gv, LEFT, buff=0.4)
    lp.next_to(gp, LEFT, buff=0.4)
    clock = ValueTracker(0.0)

    def paint(cells, ends_, run, color):
        now = clock.get_value()
        for i, c in enumerate(cells):
            start = ends_[i - 1] if i else 0.0
            if now >= ends_[i]:
                stopped = run[i][2] != "ok"
                c.set_fill(RED_STOP if stopped else color, 0.9)
                c.set_stroke(GRAY_TEXT, 1, 0.35)
            elif now >= start:
                c.set_fill(color, 0.15).set_stroke(WHITE_SOFT, 2, 1)
            else:
                c.set_fill(color, 0).set_stroke(GRAY_TEXT, 1, 0.35)

    gv.add_updater(lambda m: paint(m, v_ends, v_run, V_FILL))
    gp.add_updater(lambda m: paint(m, p_ends, p_run, P_FILL))

    def count(ends_, color):
        return always_redraw(lambda: body(f"{sum(e <= clock.get_value() for e in ends_)} / 99", size=30,
                                          weight=BOLD, color=color))
    cv, cp = count(v_ends, V_TEXT), count(p_ends, P_TEXT)
    cv.add_updater(lambda m: m.next_to(gv, RIGHT, buff=0.4))
    cp.add_updater(lambda m: m.next_to(gp, RIGHT, buff=0.4))
    timer = always_redraw(lambda: body(f"{clock.get_value():,.0f} s", size=30, weight=BOLD)
                          .move_to(DOWN * 2.45 + RIGHT * 0.6))
    tl = caption("elapsed", size=20).move_to(DOWN * 2.85 + RIGHT * 0.6)

    f.play(FadeIn(head, shift=DOWN * 0.1), run_time=0.6)
    f.play(FadeIn(VGroup(gv, gp, lv, lp)), FadeIn(cv), FadeIn(cp), FadeIn(timer), FadeIn(tl), run_time=0.6)
    f.play(clock.animate(rate_func=linear).set_value(v_total), run_time=5.0)
    for m in (gv, gp, cv, cp, timer):
        m.clear_updaters()
    note = body(f"Vertica: all 99 done.   PostgreSQL: {p_done} done, query {p_done + 1} running.",
                size=26, color=WHITE_SOFT).move_to(DOWN * 3.35)
    f.play(FadeIn(note, shift=UP * 0.1), run_time=0.5)

    f.hold_until(t_title)
    race = VGroup(gv, gp, lv, lp, cv, cp, timer, tl)
    f.play(FadeOut(head), FadeOut(note), race.animate.scale(0.55).move_to(RIGHT * 2.2 + DOWN * 2.35),
           run_time=0.8)
    title = body("Vertica and PostgreSQL", size=64, weight=BOLD)
    title2 = body("on the same analytic workload", size=64, weight=BOLD)
    title2.set_color_by_gradient(LILAC, PINK)
    subt = body("99 queries derived from TPC-DS, on one machine, measured", size=26, color=WHITE_SOFT)
    rule = Line(ORIGIN, RIGHT * 5.6).set_stroke(color=[ELECTRIC, PINK], width=3.5)
    tag1 = body("12 GB and 102 GB of raw data  ·  best of 3 runs", size=21, color=LILAC)
    tag2 = body("query times  ·  load  ·  storage and compression", size=21, color=LILAC)
    block = VGroup(title, title2, subt, rule, tag1, tag2).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
    rule.shift(DOWN * 0.05)
    VGroup(tag1, tag2).shift(DOWN * 0.12)
    block.move_to(LEFT * 6.4 + UP * 1.55, aligned_edge=LEFT)
    f.play(FadeIn(title, shift=RIGHT * 0.25), run_time=0.55)
    f.play(FadeIn(title2, shift=RIGHT * 0.25), run_time=0.45)
    f.play(FadeIn(subt, shift=RIGHT * 0.15), Create(rule), run_time=0.45)
    f.play(FadeIn(tag1), FadeIn(tag2), run_time=0.5)
    f.hold_until(t_end - 0.5)
    f.play(FadeOut(block, shift=LEFT * 0.2), FadeOut(race), run_time=0.5)
