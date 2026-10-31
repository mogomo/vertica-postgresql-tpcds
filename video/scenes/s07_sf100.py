"""S07 - ten times the data: memory decides."""
from kit import *


def build(f, ch):
    title = chapter_title("A hundred gigabytes")
    f.play(FadeIn(title), run_time=0.6)
    v10 = float(metrics("vertica", 10)["power_best_iteration_seconds"])
    v100 = float(metrics("vertica", 100)["power_best_iteration_seconds"])
    ok = 99 - int(metrics("postgresql", 100)["queries_not_finished"])
    f.hold_until(f.cue(ch, "Vertica's time grew seven times"))
    a = body(f"Vertica: {v10:.0f} s → {v100:.0f} s  (×{v100 / v10:.1f})", size=FS_BODY, color=V_TEXT)
    a.to_edge(UP, buff=1.5).to_edge(LEFT, buff=0.9)
    f.play(FadeIn(a, shift=RIGHT * 0.2), run_time=0.7)
    f.hold_until(f.cue(ch, "PostgreSQL finished only"))
    b = body(f"PostgreSQL: {ok} of 99 queries finished within their limits", size=FS_BODY, color=P_TEXT)
    b.next_to(a, DOWN, buff=0.3, aligned_edge=LEFT)
    f.play(FadeIn(b, shift=RIGHT * 0.2), run_time=0.7)

    # memory: 61 GiB usable RAM vs the data in each product
    f.hold_until(f.cue(ch, "The reason is memory"))
    scale = 0.075   # units per GB
    ram = Rectangle(width=61 * 1.074 * scale, height=0.7).set_stroke(WHITE_SOFT, 1.5)
    ram.move_to([-6.0, -0.4, 0], aligned_edge=LEFT)
    rl = caption("laptop memory: 61 GiB usable").next_to(ram, UP, buff=0.15, aligned_edge=LEFT)
    vs = int(metrics("vertica", 100)["stored_bytes"]) / 1e9
    ps = int(metrics("postgresql", 100)["stored_bytes"]) / 1e9
    dv = Rectangle(width=vs * scale, height=0.5).set_stroke(width=0).set_fill(V_FILL, 0.95)
    dv.move_to([-6.0, -1.5, 0], aligned_edge=LEFT)
    dp = Rectangle(width=ps * scale, height=0.5).set_stroke(width=0).set_fill(P_FILL, 0.95)
    dp.move_to([-6.0, -2.55, 0], aligned_edge=LEFT)
    edge = DashedLine(ram.get_right() + UP * 0.6, ram.get_right() + DOWN * 2.6).set_stroke(WHITE_SOFT, 1.2)
    f.play(Create(ram), FadeIn(rl), Create(edge), run_time=0.8)
    f.hold_until(f.cue(ch, "Vertica's thirty-nine gigabytes"))
    lv = caption(f"Vertica {vs:.1f} GB", color=V_TEXT).next_to(dv, UP, buff=0.1, aligned_edge=LEFT)
    f.play(GrowFromEdge(dv, LEFT), FadeIn(lv), run_time=0.8)
    f.hold_until(f.cue(ch, "PostgreSQL's hundred and forty-seven do not"))
    lp = caption(f"PostgreSQL {ps:.1f} GB", color=P_TEXT).next_to(dp, RIGHT, buff=0.2)
    f.play(GrowFromEdge(dp, LEFT), run_time=1.2)
    lp.next_to(dp, UP, buff=0.1, aligned_edge=LEFT)
    f.play(FadeIn(lp), run_time=0.4)
    f.hold_until(f.cue(ch, "its joins spill"))
    sp = float(metrics("postgresql", 100)["spill_bytes_per_iteration"]) / 1e9
    sl = caption(f"{sp:.0f} GB of temporary files per run", color=P_TEXT).to_edge(DOWN, buff=0.6).to_edge(RIGHT, buff=0.9)
    f.play(FadeIn(sl), run_time=0.6)
    f.hold_until(f.cue(ch, "The typical gap grows"))
    m10, m100 = ratios(10), ratios(100)
    g = body(f"typical query: {m10[len(m10) // 2]:.0f}× → {m100[len(m100) // 2]:.0f}× slower on PostgreSQL",
             size=FS_BODY).next_to(b, DOWN, buff=0.3, aligned_edge=LEFT)
    f.play(FadeIn(g, shift=RIGHT * 0.2), run_time=0.7)
