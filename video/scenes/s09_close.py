"""S09 - limits of the test, how to repeat it, the closing lockup."""
from kit import *
from logo import lockup_vector, reveal_lockup


def build(f, ch):
    a = caption("one machine · one workload · one query stream", size=FS_BODY)
    b = caption("not part of this test: transactions, many concurrent users", size=FS_CAPTION)
    c = caption("Workload derived from TPC-DS. Not an official TPC-DS result.", size=FS_CAPTION)
    d = body("Every script, setting and timing is published.", size=FS_BODY, color=BRAND_SECONDARY)
    g = VGroup(a, b, c, d).arrange(DOWN, buff=0.35).move_to(UP * 0.3)
    f.play(FadeIn(a), run_time=0.6)
    f.hold_until(f.cue(ch, "Transactions and many concurrent users"))
    f.play(FadeIn(b), run_time=0.5)
    f.hold_until(f.cue(ch, "This is not an official"))
    f.play(FadeIn(c), run_time=0.5)
    f.hold_until(f.cue(ch, "Every script"))
    f.play(FadeIn(d), run_time=0.6)
    f.hold_until(f.cue(ch, "Vertica, from Rocket Software"))
    f.play(FadeOut(g), run_time=0.5)
    lk = lockup_vector(height=2.4).move_to(UP * 0.2)
    reveal_lockup(f, lk)
