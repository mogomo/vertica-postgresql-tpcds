"""S09 - what it means."""
from kit import *


def build(f, ch):
    title = chapter_title("What it means")
    f.play(FadeIn(title), run_time=0.6)
    lines = [("For tens of gigabytes", "Tens of gigabytes, simple selective queries:", "PostgreSQL can be good enough", P_TEXT),
             ("For analytic SQL as it is really written", "Analytic SQL as it is really written:", "Vertica, faster by orders of magnitude", V_TEXT),
             ("the gap grows with your data", "More data:", "the gap grows - compression keeps Vertica in memory", V_TEXT)]
    rows = VGroup()
    for _, a, b, c in lines:
        rows.add(VGroup(body(a, size=FS_BODY, color=GRAY_TEXT), body(b, size=FS_BODY, color=c)).arrange(DOWN, aligned_edge=LEFT, buff=0.12))
    rows.arrange(DOWN, aligned_edge=LEFT, buff=0.6).move_to(DOWN * 0.2).to_edge(LEFT, buff=1.0)
    for (phrase, *_), row in zip(lines, rows):
        f.hold_until(f.cue(ch, phrase))
        f.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.8)
