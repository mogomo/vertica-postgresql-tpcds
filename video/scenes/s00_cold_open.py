"""S00 - the question, and the answer: measure it."""
from kit import *


def build(f, ch):
    q = body("“Couldn't we just run our reports on PostgreSQL?”", size=FS_HEAD)
    f.play(Write(q), run_time=1.6)
    f.hold_until(f.cue(ch, "PostgreSQL is an excellent database"))
    f.play(q.animate.shift(UP * 1.4).set_opacity(0.55), run_time=0.8)
    facts = VGroup(*[caption(t, size=FS_BODY) for t in ("excellent", "everywhere", "free to start")])
    facts.arrange(RIGHT, buff=1.0).next_to(q, DOWN, buff=1.0)
    f.play(LaggedStart(*[enter(x) for x in facts], lag_ratio=0.35), run_time=1.6)
    f.hold_until(f.cue(ch, "we measured it"))
    m = body("So we measured it.", size=FS_BIG, color=BRAND_SECONDARY)
    m.next_to(facts, DOWN, buff=1.0)
    f.play(FadeIn(m, shift=UP * 0.2), run_time=0.9)
