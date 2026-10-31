"""S10 - limits of the test, how to repeat it, the closing lockup on the last hit of the music."""
from kit import *
from logo import lockup_vector, reveal_lockup


def build(f, ch):
    a = caption("one machine · one workload · one query stream", size=FS_BODY)
    n = caption("Vertica on a single node: a cluster or stronger hardware would likely do better still", size=FS_CAPTION)
    b = caption("not part of this test: transactions, many concurrent users", size=FS_CAPTION)
    c = caption("Workload derived from TPC-DS. Not an official TPC-DS result.", size=FS_CAPTION)
    g = VGroup(a, n, b, c).arrange(DOWN, buff=0.35).move_to(UP * 0.6)
    f.play(FadeIn(a), run_time=0.6)
    f.hold_until(f.cue(ch, "Vertica ran as a single node"))
    f.play(FadeIn(n), run_time=0.5)
    f.hold_until(f.cue(ch, "Transactions and many concurrent users"))
    f.play(FadeIn(b), run_time=0.5)
    f.hold_until(f.cue(ch, "This is not an official"))
    f.play(FadeIn(c), run_time=0.5)

    f.hold_until(f.cue(ch, "Every script"))
    f.play(FadeOut(g, shift=UP * 0.2), run_time=0.4)
    note = body("Every script, setting and timing is published, as is.", size=30, color=LILAC)
    url = mono(ADDRESS, size=32, color=WHITE_SOFT)
    VGroup(note, url).arrange(DOWN, buff=0.4).move_to(ORIGIN)
    rule = Line(LEFT, RIGHT).set_stroke(color=[ELECTRIC, PINK], width=3.5)
    rule.set(width=url.width + 0.5).next_to(url, DOWN, buff=0.18)
    f.play(FadeIn(note, shift=UP * 0.1), run_time=0.4)
    f.play(FadeIn(url, shift=UP * 0.1), Create(rule), run_time=0.6)

    # the lockup: drawn from "Vertica, from Rocket Software", its bloom on the last hit
    start = f.timing["lockup"]
    f.hold_until(start - 0.5)
    f.play(FadeOut(VGroup(note, url, rule)), run_time=0.5)
    lockup = lockup_vector(height=3.3)
    if lockup.width > 10.8:
        lockup.set(width=10.8)
    lockup.scale(0.5 / 0.8).move_to(ORIGIN)
    f.hold_until(start)
    reveal_lockup(f, lockup, draw=1.7, text=1.3, glow=0.55)
