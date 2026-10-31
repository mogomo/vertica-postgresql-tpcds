"""S06 - where it breaks: a correlated subquery, per row vs once."""
from kit import *


def build(f, ch):
    title = chapter_title("Where it breaks")
    f.play(FadeIn(title), run_time=0.6)
    sql = VGroup(mono("-- customers whose returns are 20% above their store's average", size=FS_CAPTION, color=GRAY_TEXT),
                 mono("ctr1.ctr_total_return > (select avg(ctr_total_return) * 1.2", size=FS_CAPTION, color=WHITE_SOFT),
                 mono("    from customer_total_return ctr2", size=FS_CAPTION, color=WHITE_SOFT),
                 mono("    where ctr1.ctr_store_sk = ctr2.ctr_store_sk)", size=FS_CAPTION, color=WHITE_SOFT))
    sql.arrange(DOWN, aligned_edge=LEFT, buff=0.12).to_edge(UP, buff=1.5).shift(LEFT * 1.0)
    f.hold_until(f.cue(ch, "Query one asks"))
    f.play(FadeIn(sql[0]), FadeIn(sql[1]), run_time=0.8)
    f.hold_until(f.cue(ch, "That average is a correlated subquery"))
    f.play(FadeIn(sql[2:]), run_time=0.6)
    f.play(Circumscribe(sql[3], color=BRAND_SECONDARY, buff=0.06), run_time=0.9)

    # PostgreSQL: for every outer row, scan the whole intermediate result again
    f.hold_until(f.cue(ch, "PostgreSQL computes it again for every single row"))
    outer = VGroup(*[Rectangle(width=1.4, height=0.18).set_stroke(width=0).set_fill(P_FILL, 0.9) for _ in range(9)]).arrange(DOWN, buff=0.07)
    inner = VGroup(*[Rectangle(width=1.4, height=0.18).set_stroke(width=0).set_fill(P_FILL, 0.45) for _ in range(9)]).arrange(DOWN, buff=0.07)
    VGroup(outer, inner).arrange(RIGHT, buff=1.2).move_to(LEFT * 3.5 + DOWN * 1.2)
    pl = product_label("postgresql", FS_CAPTION).next_to(VGroup(outer, inner), UP, buff=0.25)
    f.play(FadeIn(outer), FadeIn(inner), FadeIn(pl), run_time=0.6)
    for i in range(4):
        hl = SurroundingRectangle(outer[i], color=WHITE_SOFT, buff=0.03, stroke_width=1.5)
        sweep = Rectangle(width=1.5, height=inner.height + 0.1).set_stroke(P_TEXT, 1.5).move_to(inner)
        f.play(Create(hl), ShowPassingFlash(sweep.copy().set_stroke(WHITE_SOFT, 2), time_width=0.6), run_time=0.45)
        f.remove(hl)
    sq = caption("work grows with the square of the rows", color=P_TEXT).next_to(VGroup(outer, inner), DOWN, buff=0.3)
    f.hold_until(f.cue(ch, "The work grows with the square"))
    f.play(FadeIn(sq), run_time=0.5)

    # Vertica: one average per store, computed once, then a join
    f.hold_until(f.cue(ch, "Vertica turns the same subquery into a join"))
    rows_v = VGroup(*[Rectangle(width=1.4, height=0.18).set_stroke(width=0).set_fill(V_FILL, 0.9) for _ in range(9)]).arrange(DOWN, buff=0.07)
    avg = VGroup(*[Rectangle(width=1.0, height=0.18).set_stroke(width=0).set_fill(V_FILL, 0.5) for _ in range(3)]).arrange(DOWN, buff=0.07)
    VGroup(rows_v, avg).arrange(RIGHT, buff=1.2).move_to(RIGHT * 3.3 + DOWN * 1.2)
    vl = product_label("vertica", FS_CAPTION).next_to(VGroup(rows_v, avg), UP, buff=0.25)
    al = tiny("avg per store", color=V_TEXT).next_to(avg, DOWN, buff=0.12)
    join = Line(rows_v.get_right(), avg.get_left(), buff=0.1).set_stroke(V_TEXT, 2)
    f.play(FadeIn(rows_v), FadeIn(vl), run_time=0.5)
    f.play(FadeIn(avg), FadeIn(al), Create(join), run_time=0.8)
    f.hold_until(f.cue(ch, "A quarter of a second"))
    tv = body(f"{best_times('vertica', 10)['01']:.2f} s", size=FS_HEAD, color=V_TEXT).next_to(al, DOWN, buff=0.3)
    tp = body("> 10 min", size=FS_HEAD, color=P_TEXT).next_to(sq, DOWN, buff=0.25)
    f.play(FadeIn(tv), run_time=0.5)
    f.hold_until(f.cue(ch, "more than ten minutes"))
    f.play(FadeIn(tp), run_time=0.5)

    # query 41: the text alone
    f.hold_until(f.cue(ch, "In one of them"))
    f.play(FadeOut(VGroup(sql, outer, inner, pl, sq, rows_v, avg, vl, al, join, tv, tp)), run_time=0.5)
    a = mono("(select count(*) ... where i_manufact = i1.i_manufact) > 0", size=FS_CAPTION, color=WHITE_SOFT)
    b = mono("exists (select * ... where i_manufact = i1.i_manufact)", size=FS_CAPTION, color=WHITE_SOFT)
    q41 = body("query 41: the same meaning, two texts", size=FS_BODY).to_edge(UP, buff=1.5)
    a.move_to(UP * 0.6)
    ta = caption("PostgreSQL with the original text: 18.8 s", color=P_TEXT).next_to(a, DOWN, buff=0.25)
    f.play(FadeIn(q41), FadeIn(a), FadeIn(ta), run_time=0.8)
    f.hold_until(f.cue(ch, "given the equivalent text Vertica runs"))
    b.move_to(DOWN * 1.0)
    tb = caption("PostgreSQL with Vertica's text: 0.03 s  ·  Vertica: 0.05 s", color=WHITE_SOFT).next_to(b, DOWN, buff=0.25)
    f.play(TransformFromCopy(a, b), run_time=1.0)
    f.play(FadeIn(tb), run_time=0.6)
