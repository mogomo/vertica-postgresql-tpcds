"""S02 - the rules that make the comparison fair."""
from kit import *

RULES = [("same memory budget", "same memory budget: about 40 GB · all 22 CPU threads"),
         ("tuned the way its own documentation", "each tuned as its documentation recommends"),
         ("No materialized views", "no materialized views · no caches · no hints · no hand-tuned queries"),
         ("compared the answers", "answers compared row by row"),
         ("time limit", "time limit per PostgreSQL query")]


def build(f, ch):
    title = chapter_title("Making it fair")
    f.play(FadeIn(title), run_time=0.6)
    items = VGroup()
    for _, text in RULES:
        dot = Square(0.11).set_stroke(width=0).set_fill(BRAND_PRIMARY, 1)
        items.add(VGroup(dot, body(text, size=FS_BODY)).arrange(RIGHT, buff=0.3))
    items.arrange(DOWN, aligned_edge=LEFT, buff=0.42).move_to(LEFT * 1.6 + UP * 0.6)
    for (phrase, _), item in zip(RULES[:3], items[:3]):
        f.hold_until(f.cue(ch, phrase))
        f.play(FadeIn(item, shift=RIGHT * 0.2), run_time=0.7)

    # the designs of each product, under the second rule
    f.hold_until(f.cue(ch, "Vertica projections designed"))
    dv = caption("Vertica: Database Designer projections", color=V_TEXT)
    dp = caption("PostgreSQL: analytic settings, primary keys, indexes, VACUUM ANALYZE", color=P_TEXT)
    VGroup(dv, dp).arrange(DOWN, aligned_edge=LEFT, buff=0.12).next_to(items[1], DOWN, buff=0.1, aligned_edge=LEFT).shift(RIGHT * 0.41)
    items[2].shift(DOWN * 0.7)
    items[3:].shift(DOWN * 0.7)
    f.play(FadeIn(dv), run_time=0.5)
    f.hold_until(f.cue(ch, "PostgreSQL settings for analytics"))
    f.play(FadeIn(dp), run_time=0.5)

    f.hold_until(f.cue(ch, "compared the answers"))
    f.play(FadeIn(items[3], shift=RIGHT * 0.2), run_time=0.7)
    # integer division: same question, different answers
    f.hold_until(f.cue(ch, "five queries divide one integer"))
    stage = VGroup(*items, dv, dp)
    f.play(stage.animate.scale(0.7).to_edge(LEFT, buff=0.7).shift(UP * 0.3), run_time=0.8)
    expr = mono("hd_dep_count / hd_vehicle_count > 1.2", size=FS_CODE, color=WHITE_SOFT)
    ex = mono("7 / 2", size=FS_HEAD, color=WHITE_SOFT)
    rv = VGroup(product_label("vertica", FS_CAPTION), mono("= 3.5", size=FS_HEAD, color=V_TEXT)).arrange(RIGHT, buff=0.3)
    rp = VGroup(product_label("postgresql", FS_CAPTION), mono("= 3", size=FS_HEAD, color=P_TEXT)).arrange(RIGHT, buff=0.3)
    box = VGroup(expr, ex, rv, rp).arrange(DOWN, buff=0.35).move_to(RIGHT * 3.6 + UP * 0.6)
    f.play(FadeIn(expr), run_time=0.6)
    f.play(FadeIn(ex), run_time=0.5)
    f.hold_until(f.cue(ch, "Vertica returns a decimal"))
    f.play(FadeIn(rv, shift=UP * 0.1), run_time=0.5)
    f.hold_until(f.cue(ch, "PostgreSQL truncates"))
    f.play(FadeIn(rp, shift=UP * 0.1), run_time=0.5)
    fix = caption("fixed with a cast: same question, same answer", color=GREEN_OK).next_to(box, DOWN, buff=0.3)
    f.hold_until(f.cue(ch, "a different question"))
    f.play(FadeIn(fix), run_time=0.5)

    f.hold_until(f.cue(ch, "every PostgreSQL query got a time limit"))
    f.play(FadeOut(VGroup(box, fix)), run_time=0.4)
    f.play(FadeIn(items[4], shift=RIGHT * 0.2), run_time=0.6)
    formula = mono("limit = max(60 s, 5 × Vertica's time)", size=FS_HEAD, color=WHITE_SOFT)
    formula.next_to(stage, DOWN, buff=0.7).set_x(0)
    note = caption("a query over its limit counts with its limit: totals are lower bounds (≥)")
    note.next_to(formula, DOWN, buff=0.3)
    f.play(Write(formula), run_time=1.2)
    f.play(FadeIn(note), run_time=0.6)
