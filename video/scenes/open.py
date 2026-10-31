"""Cold open, music only: the 99 queries of the 102 GB power run as a race, then the title.

When Vertica has finished all 99 queries, PostgreSQL is still at an early query - both
runs drawn from their timings, in run order, on one compressed clock. The words stay in
the left half, the race in the right half: two columns of cells, one per product."""
from kit import *

COLS, ROWS, CELL, GAP = 9, 11, 0.2, 0.06
TEXT_X = LEFT_X + 0.3          # left edge of the words
RACE_X = 3.35                  # centre of the race


def grid(color) -> VGroup:
    cells = VGroup(*[Square(CELL).set_stroke(GRAY_TEXT, 1, 0.35).set_fill(color, 0)
                     for _ in range(COLS * ROWS)])
    cells.arrange_in_grid(ROWS, COLS, buff=GAP)
    return cells


def left_block(*rows, buff=0.2) -> VGroup:
    g = VGroup(*rows).arrange(DOWN, buff=buff, aligned_edge=LEFT)
    return g.move_to([TEXT_X, 0.35, 0], aligned_edge=LEFT)


def build(f, t_title: float, t_end: float):
    v_run, p_run = power_run("vertica", 100), power_run("postgresql", 100)
    v_total = sum(s for _, s, _ in v_run)
    ends = lambda run: [sum(s for _, s, _ in run[:i + 1]) for i in range(len(run))]
    v_ends, p_ends = ends(v_run), ends(p_run)
    p_done = sum(e <= v_total for e in p_ends)

    head = left_block(body("99 analytic queries,", size=34, weight=BOLD),
                      body("one after the other", size=34, weight=BOLD),
                      VGroup(*[body(t, size=20, color=LILAC) for t in
                               ("102 GB of raw data", "one machine", "the same queries")]
                             ).arrange(DOWN, buff=0.12, aligned_edge=LEFT))
    head[2].shift(DOWN * 0.2)
    gv, gp = grid(V_FILL), grid(P_FILL)
    VGroup(gv, gp).arrange(RIGHT, buff=0.75).move_to([RACE_X, 0.25, 0])
    lv = body("Vertica", size=22, weight=BOLD, color=V_TEXT).next_to(gv, UP, buff=0.3)
    lp = body("PostgreSQL", size=22, weight=BOLD, color=P_TEXT).next_to(gp, UP, buff=0.3)
    lp.align_to(lv, UP)                       # one cap line for both names
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

    def count(ends_, color, g):
        return always_redraw(lambda: body(f"{sum(e <= clock.get_value() for e in ends_)} / 99", size=24,
                                          weight=BOLD, color=color).next_to(g, DOWN, buff=0.28))
    cv, cp = count(v_ends, V_TEXT, gv), count(p_ends, P_TEXT, gp)
    timer = always_redraw(lambda: body(f"{clock.get_value():,.0f} s", size=26, weight=BOLD)
                          .move_to([RACE_X, gv.get_bottom()[1] - 1.05, 0]))
    tl = caption("elapsed", size=17).move_to([RACE_X, gv.get_bottom()[1] - 1.42, 0])

    f.play(FadeIn(head, shift=RIGHT * 0.15), run_time=0.6)
    f.play(FadeIn(VGroup(gv, gp, lv, lp)), FadeIn(cv), FadeIn(cp), FadeIn(timer), FadeIn(tl), run_time=0.6)
    f.play(clock.animate(rate_func=linear).set_value(v_total), run_time=5.0)
    for m in (gv, gp, cv, cp, timer):
        m.clear_updaters()
    note = VGroup(body("Vertica: all 99 done.", size=22, color=V_TEXT),
                  body(f"PostgreSQL: {p_done} done, query {p_done + 1} running.", size=22, color=WHITE_SOFT)
                  ).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
    note.next_to(head, DOWN, buff=0.6, aligned_edge=LEFT)
    f.play(FadeIn(note, shift=UP * 0.1), run_time=0.5)

    # the title takes the left half; the finished race stays where it is
    f.hold_until(t_title)
    f.play(FadeOut(head, shift=LEFT * 0.2), FadeOut(note, shift=LEFT * 0.2), run_time=0.6)
    title = body("Vertica and PostgreSQL", size=44, weight=BOLD)
    title2 = VGroup(body("on the same", size=44, weight=BOLD), body("analytic workload", size=44, weight=BOLD)
                    ).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
    title2.set_color_by_gradient(LILAC, PINK)
    subt = VGroup(body("99 queries derived from TPC-DS,", size=21, color=WHITE_SOFT),
                  body("on one machine, measured", size=21, color=WHITE_SOFT)).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
    rule = Line(ORIGIN, RIGHT * title.width).set_stroke(color=[ELECTRIC, PINK], width=3)
    tags = VGroup(*[body(t, size=17, color=LILAC) for t in
                    ("12 GB and 102 GB of raw data  ·  best of 3 runs",
                     "query times  ·  load  ·  storage and compression")]).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
    block = left_block(title, title2, subt, rule, tags, buff=0.22)
    subt.shift(DOWN * 0.08)
    rule.shift(DOWN * 0.1)
    tags.shift(DOWN * 0.2)
    f.play(FadeIn(title, shift=RIGHT * 0.25), run_time=0.55)
    f.play(FadeIn(title2, shift=RIGHT * 0.25), run_time=0.45)
    f.play(FadeIn(subt, shift=RIGHT * 0.15), Create(rule), run_time=0.45)
    f.play(FadeIn(tags), run_time=0.5)
    f.hold_until(t_end - 0.5)
    race = VGroup(gv, gp, lv, lp, cv, cp, timer, tl)
    f.play(FadeOut(block, shift=LEFT * 0.2), FadeOut(race), run_time=0.5)
