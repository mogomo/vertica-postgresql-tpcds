"""S10 - limits of the test (one node here, a cluster is what Vertica is built for), how to
repeat it, the closing lockup on the last hit of the music."""
from kit import *
from logo import lockup_vector, reveal_lockup

ROW_Y = 0.95                   # the node row
SINGLE_X, CLUSTER_X = -4.45, 2.45


def build(f, ch):
    a = caption("one machine · one workload · one query stream", size=FS_BODY).move_to(UP * 2.9)
    f.play(FadeIn(a), run_time=0.6)

    # this test: one node, its data on the machine's own disk
    f.hold_until(f.cue(ch, "Vertica ran as a single node"))
    one = stroke_node(1.5, 0.95).move_to([SINGLE_X, ROW_Y, 0])
    one_d = node_detail(one)
    disk = stroke_cylinder(0.62, 0.55).next_to(one, DOWN, buff=0.2)
    one_l = VGroup(body("This test", size=FS_CAPTION, color=V_TEXT),
                   tiny("one node · local disk")).arrange(DOWN, buff=0.1).next_to(disk, DOWN, buff=0.3)
    f.play(Create(one), run_time=0.6)
    f.play(FadeIn(one_d), FadeIn(disk, shift=DOWN * 0.1), FadeIn(one_l), run_time=0.5)

    # a cluster in Eon Mode: two subclusters, a depot under each node, one communal storage
    f.hold_until(f.cue(ch, "built to scale out"))
    nodes = VGroup(*[stroke_node(0.8, 0.6) for _ in range(6)]).arrange(RIGHT, buff=0.32)
    for n in nodes[3:]:
        n.shift(RIGHT * 0.5)
    nodes.move_to([CLUSTER_X, ROW_Y, 0])
    arrow = Arrow([SINGLE_X + 1.05, ROW_Y, 0], [nodes.get_left()[0] - 0.25, ROW_Y, 0], buff=0,
                  stroke_width=2, tip_length=0.16, color=GRAY_TEXT)
    out_l = tiny("scale out").next_to(arrow, UP, buff=0.12)
    f.play(GrowArrow(arrow), FadeIn(out_l), run_time=0.5)
    f.play(LaggedStart(*[TransformFromCopy(one, n) for n in nodes], lag_ratio=0.1), run_time=1.0)
    depots = VGroup(*[stroke_cylinder(0.36, 0.32, stroke=1.5).next_to(n, DOWN, buff=0.16) for n in nodes])
    f.play(FadeIn(VGroup(*[node_detail(n, stroke=1.5) for n in nodes])),
           LaggedStart(*[GrowFromEdge(d, UP) for d in depots], lag_ratio=0.08), run_time=0.6)
    store = stroke_bucket(1.6, 1.0).move_to([CLUSTER_X, -1.45, 0])
    store_l = tiny("communal storage").next_to(store, DOWN, buff=0.18)
    flow = depots.copy().set_stroke(opacity=0.55)
    f.add(flow)
    f.play(ReplacementTransform(flow, store, rate_func=EASE), FadeIn(store_l), run_time=0.8)
    links = VGroup(*[DashedLine(d.get_bottom() + DOWN * 0.05, store.get_top() + DOWN * 0.04, dash_length=0.08)
                     .set_stroke(GRAY_TEXT, 1.0, 0.5) for d in depots])
    subs = VGroup(dashed_box(VGroup(*nodes[:3], *depots[:3]), V_TEXT, 0.16),
                  dashed_box(VGroup(*nodes[3:], *depots[3:]), V_TEXT, 0.16))
    sub_l = VGroup(*[tiny(t, size=14, color=V_TEXT).next_to(b, UP, buff=0.1)
                     for t, b in (("Subcluster A", subs[0]), ("Subcluster B", subs[1]))])
    cl = body("A Vertica cluster · Eon Mode", size=FS_CAPTION, color=V_TEXT).next_to(sub_l, UP, buff=0.18)
    cl.set_x(CLUSTER_X)
    f.play(LaggedStart(*[Create(l) for l in links], lag_ratio=0.08), Create(subs), FadeIn(sub_l), FadeIn(cl),
           run_time=0.8)

    f.hold_until(f.cue(ch, "it would likely do better"))
    n = caption("on more nodes or stronger hardware, Vertica would likely do better still", size=FS_CAPTION,
                color=WHITE_SOFT).move_to(DOWN * 2.85)
    f.play(FadeIn(n, shift=UP * 0.1), run_time=0.5)

    f.hold_until(f.cue(ch, "Every script"))
    f.clear_stage(0.4)
    note = body("Every script, setting and timing is published, as is.", size=26, color=LILAC)
    url = mono(ADDRESS, size=28, color=WHITE_SOFT)
    VGroup(note, url).arrange(DOWN, buff=0.4).move_to(UP * 0.2)
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
