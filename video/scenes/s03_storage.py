"""S03 - size on disk, and why: rows with headers vs sorted, encoded columns."""
from kit import *

K = 0.7          # the scale of the drawings in this chapter


def size_group(sf: int, label: str, vmax: float, height: float = 3.2 * K) -> VGroup:
    raw = int(metrics("vertica", sf)["raw_data_bytes"]) / 1e9
    v = int(metrics("vertica", sf)["stored_bytes"]) / 1e9
    p = int(metrics("postgresql", sf)["stored_bytes"]) / 1e9
    bars = VGroup(vbar(raw, vmax, height, BRAND_DEEP, 0.8 * K),
                  vbar(v, vmax, height, V_FILL, 0.8 * K),
                  vbar(p, vmax, height, P_FILL, 0.8 * K)).arrange(RIGHT, buff=0.25 * K, aligned_edge=DOWN)
    vals = VGroup(*[caption(f"{x:.1f} GB", size=15, color=c).next_to(b, UP, buff=0.08)
                    for x, b, c in zip((raw, v, p), bars, (GRAY_TEXT, V_TEXT, P_TEXT))])
    name = body(label, size=16).next_to(bars, DOWN, buff=0.2)
    g = VGroup(bars, vals, name)
    g.bars, g.vals = bars, vals
    return g


def build(f, ch):
    title = chapter_title("Storage")
    f.play(FadeIn(title), run_time=0.6)
    g10 = size_group(10, "12 GB raw", 25).move_to(LEFT * 2.4 + DOWN * 1.55, aligned_edge=DOWN)
    g100 = size_group(100, "102 GB raw", 150).move_to(RIGHT * 2.4 + DOWN * 1.55, aligned_edge=DOWN)
    legend = VGroup(*[VGroup(Square(0.13).set_stroke(width=0).set_fill(c, 1), caption(t, size=15, color=tc)).arrange(RIGHT, buff=0.12)
                      for c, t, tc in ((BRAND_DEEP, "raw text", GRAY_TEXT), (V_FILL, "Vertica", V_TEXT),
                                       (P_FILL, "PostgreSQL", P_TEXT))]).arrange(RIGHT, buff=0.4)
    legend.move_to(DOWN * 2.35)
    f.play(FadeIn(legend), run_time=0.5)
    for g, phrase in ((g10, "Twelve gigabytes of raw text"), (g100, "At a hundred and two gigabytes")):
        f.hold_until(f.cue(ch, phrase))
        f.play(FadeIn(g[2]), run_time=0.3)
        for bar, val in zip(g.bars, g.vals):
            f.play(GrowFromEdge(bar, DOWN), FadeIn(val), run_time=0.55)

    # one table: inventory
    f.hold_until(f.cue(ch, "Look at one table"))
    f.play(FadeOut(VGroup(legend, g10, g100)), run_time=0.5)
    head = body("inventory · 399 million rows · 4 integers each", size=21).move_to(UP * 1.75)
    f.play(FadeIn(head), run_time=0.6)

    # PostgreSQL: each row = a header bigger than its values
    f.hold_until(f.cue(ch, "PostgreSQL stores every row"))
    rows = VGroup()
    for i in range(6):
        hdr = Rectangle(width=1.3 * K, height=0.32 * K).set_stroke(width=0).set_fill(P_FILL, 0.9)
        vals = VGroup(*[Rectangle(width=0.22 * K, height=0.32 * K).set_stroke(BLACK, 1).set_fill(GRAY_TEXT, 0.9)
                        for _ in range(4)]).arrange(RIGHT, buff=0)
        rows.add(VGroup(hdr, vals).arrange(RIGHT, buff=0.04))
    rows.arrange(DOWN, buff=0.1 * K).move_to(LEFT * 2.7 + DOWN * 0.1)
    rl = VGroup(caption("row header ~24 bytes", size=15, color=P_TEXT), caption("4 values, 16 bytes", size=15)
                ).arrange(RIGHT, buff=0.3)
    rl.next_to(rows, UP, buff=0.22)
    f.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in rows], lag_ratio=0.1), FadeIn(rl), run_time=1.4)
    f.hold_until(f.cue(ch, "needs another index on top"))
    idx_t = caption("+ primary key index", size=15, color=P_TEXT)
    idx = Rectangle(width=idx_t.width + 0.3, height=0.4).set_stroke(P_TEXT, 1.2).set_fill(P_FILL, 0.3).next_to(rows, DOWN, buff=0.25)
    idx_t.move_to(idx)
    f.play(FadeIn(idx), FadeIn(idx_t), run_time=0.6)

    # Vertica: sorted columns, run-length encoded
    f.hold_until(f.cue(ch, "Vertica stores each column sorted"))
    cell, gap = 0.32 * K, 0.1 * K

    def column(n_runs, fill):
        return VGroup(*[Rectangle(width=0.5 * K, height=cell * n + gap * (n - 1)).set_stroke(BLACK, 1).set_fill(V_FILL, fill)
                        for n in n_runs]).arrange(DOWN, buff=gap)

    cols = VGroup(*[column(r, 0.9 if c < 2 else 0.55)
                    for c, r in enumerate([[3, 3], [2, 2, 2], [1] * 6, [1] * 6])])
    cols.arrange(RIGHT, buff=0.18 * K, aligned_edge=UP).move_to(RIGHT * 2.4 + DOWN * 0.1)
    names = VGroup(*[tiny(n, size=14, color=V_TEXT).next_to(c, UP, buff=0.12) for n, c in zip(("date", "item", "wh", "qty"), cols)])
    f.play(LaggedStart(*[GrowFromEdge(c, UP) for c in cols], lag_ratio=0.15), FadeIn(names), run_time=1.2)
    f.hold_until(f.cue(ch, "run-length encoding"))
    rle = column([1, 1], 0.9).move_to(cols[0], aligned_edge=UP)
    rle2 = column([1, 1, 1], 0.9).move_to(cols[1], aligned_edge=UP)
    f.play(Transform(cols[0], rle), Transform(cols[1], rle2), run_time=1.0)
    rlabel = caption("runs of one value → one entry", size=15, color=V_TEXT).next_to(cols, DOWN, buff=0.3)
    f.play(FadeIn(rlabel), run_time=0.5)

    f.hold_until(f.cue(ch, "Eight gigabytes of text"))
    res = VGroup(body("8.2 GB as text", size=20),
                 body("0.7 GB in Vertica", size=20, color=V_TEXT),
                 body("30.3 GB in PostgreSQL", size=20, color=P_TEXT)).arrange(RIGHT, buff=0.6)
    res.move_to(DOWN * 2.35)
    f.play(LaggedStart(*[FadeIn(r, shift=UP * 0.15) for r in res], lag_ratio=0.3), run_time=1.2)
