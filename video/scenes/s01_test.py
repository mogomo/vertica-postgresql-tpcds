"""S01 - one machine, two databases, the same data."""
from kit import *

SHEET = [("Machine", "Dell Precision 3591 workstation"),
         ("CPU", "Intel Core Ultra 7 165H · 16 cores · 22 threads"),
         ("Memory / disk", "64 GB · 1 TB NVMe SSD"),
         ("OS", "Ubuntu 26.04 LTS"),
         ("Vertica", "26.3.0 · 1 node"),
         ("PostgreSQL", "18.6")]


def build(f, ch):
    title = chapter_title("The test")
    f.play(FadeIn(title), run_time=0.6)

    box = RoundedRectangle(corner_radius=0.15, width=4.0, height=2.5).set_stroke(GRAY_TEXT, 1.5)
    dv, dp = db_icon(0.85, 0.68, color=V_TEXT), db_icon(0.85, 0.68, color=P_TEXT)
    dv.move_to(box.get_center() + LEFT * 0.95 + UP * 0.15)
    dp.move_to(box.get_center() + RIGHT * 0.95 + UP * 0.15)
    lv = body("Vertica 26.3", size=FS_CAPTION, color=V_TEXT).next_to(dv, DOWN, buff=0.18)
    lp = body("PostgreSQL 18.6", size=FS_CAPTION, color=P_TEXT).next_to(dp, DOWN, buff=0.18)
    machine = VGroup(box, dv, dp, lv, lp).move_to(LEFT * 3.2 + DOWN * 0.2)
    f.play(Create(box), run_time=0.9)
    f.play(LaggedStart(FadeIn(dv), FadeIn(lv), lag_ratio=0.3), run_time=0.7)
    f.hold_until(f.cue(ch, "and PostgreSQL eighteen point six"))
    f.play(LaggedStart(FadeIn(dp), FadeIn(lp), lag_ratio=0.3), run_time=0.7)

    # the hardware in small type: it is the setting, not the subject
    rows = VGroup()
    for k, v in SHEET:
        r = VGroup(tiny(k, size=13), body(v, size=13, color=GRAY_TEXT))
        r[1].move_to(r[0].get_left() + RIGHT * 1.25, aligned_edge=LEFT)
        rows.add(r)
    rows.arrange(DOWN, aligned_edge=LEFT, buff=0.13).move_to([0.6, 1.5, 0], aligned_edge=LEFT)
    f.play(LaggedStart(*[FadeIn(r, shift=LEFT * 0.15) for r in rows], lag_ratio=0.12), run_time=1.6)

    f.hold_until(f.cue(ch, "twenty-four tables"))
    pills = VGroup(pill("24 tables"), pill("99 queries")).arrange(RIGHT, buff=0.3)
    pills.next_to(rows, DOWN, buff=0.55, aligned_edge=LEFT)
    f.play(LaggedStart(*[FadeIn(p) for p in pills], lag_ratio=0.4), run_time=0.9)
    f.hold_until(f.cue(ch, "at twelve gigabytes"))
    rows100 = int(metrics("vertica", 100)["total_rows"])
    sizes = VGroup(pill("12 GB raw data", BRAND_VIOLET),
                   pill(f"102 GB raw data · {rows100 / 1e6:,.0f} million rows", BRAND_VIOLET)).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
    sizes.next_to(pills, DOWN, buff=0.22, aligned_edge=LEFT)
    f.play(FadeIn(sizes[0]), run_time=0.6)
    f.hold_until(f.cue(ch, "a hundred and two gigabytes"))
    f.play(FadeIn(sizes[1]), run_time=0.6)
    f.hold_until(f.cue(ch, "three times"))
    best = pill("3 runs · the best counts", BRAND_DEEP).next_to(sizes, DOWN, buff=0.22, aligned_edge=LEFT)
    f.play(FadeIn(best), run_time=0.6)
