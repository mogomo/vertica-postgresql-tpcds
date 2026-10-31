"""
logo.py — the Rocket Software / Vertica lockup, as pure vector, and its reveal.

Nothing here is a bitmap. The lockup is loaded from the official vector
artwork (`assets/logos/rocket_vertica.svg`) and every element on screen —
the seven strokes of the Rocket mark, every glyph of "Rocket software" and
"Vertica", both ® marks — is a native VMobject that is *drawn into its final
position and left there*. The animation adds to the emblem; it never swaps it
for a picture at the end.

Run the reveal on its own:

    manim -pqh --disable_caching logo.py RocketVerticaReveal
"""

from __future__ import annotations

from pathlib import Path

from manim import *

LOGO_SVG = Path(__file__).parent / "assets" / "logos" / "rocket_vertica.svg"

# The brand gradient along the mark, bottom-left to top-right. These are the
# stops declared in the official artwork itself, not an eyeballed match.
SWOOSH_STOPS = ((0.00, "#4B00E0"), (0.24, "#533dff"), (0.61, "#980baf"),
                (0.69, "#a8009e"), (0.86, "#c728d1"), (1.00, "#e34cff"))

TEXT_WHITE = "#F2F2F5"

# how finely each stroke resamples the five-stop brand ramp
GRADIENT_SAMPLES = 24


def gradient_at(t: float) -> ManimColor:
    """Sample the brand gradient at 0 (bottom-left) … 1 (top-right)."""
    t = float(np.clip(t, 0.0, 1.0))
    if t <= SWOOSH_STOPS[0][0]:
        return ManimColor(SWOOSH_STOPS[0][1])
    for (t0, c0), (t1, c1) in zip(SWOOSH_STOPS, SWOOSH_STOPS[1:]):
        if t <= t1:
            f = (t - t0) / max(1e-6, t1 - t0)
            return interpolate_color(ManimColor(c0), ManimColor(c1), f)
    return ManimColor(SWOOSH_STOPS[-1][1])


def lockup_vector(height: float = 2.0, text_color: str = TEXT_WHITE) -> VGroup:
    """The whole lockup as vectors.

    Returns a VGroup carrying two handles:
      `.swoosh` — the seven strokes of the Rocket mark, ordered bottom-left to
                  top-right so they can be drawn in launch direction;
      `.words`  — every glyph of the wordmark, in reading order.
    """
    svg = SVGMobject(str(LOGO_SVG))
    svg.set(height=height)

    # the mark is the single largest element in the lockup
    mark = max(svg.submobjects, key=lambda m: m.width * m.height)
    svg.remove(mark)

    # The brand gradient is a linear one running bottom-left to top-right, so
    # project each point onto that axis and normalise over the mark's own
    # extent. Using bounding-box fractions instead compresses the sweep and
    # leaves nearly every stroke the same colour.
    # The artwork declares
    #   <linearGradient x1="21.17" y1="142.25" x2="138.18" y2="25.23">
    # i.e. a 45° axis running from the mark's bottom-left corner to its
    # top-right corner (dx = 117.01, dy = -117.02 in SVG's inverted y). So the
    # gradient's 0 and 1 are the projections of those two bbox corners, and t
    # is a point's projection normalised between them.
    axis = np.array([1.0, 1.0, 0.0]) / np.sqrt(2.0)
    dl, ur = mark.get_corner(DL), mark.get_corner(UR)
    p_lo, p_hi = float(dl @ axis), float(ur @ axis)

    def axis_t(p) -> float:
        v = float(np.asarray(p)[:3] @ axis)
        return float(np.clip((v - p_lo) / max(1e-6, p_hi - p_lo), 0.0, 1.0))

    swoosh = VGroup()
    for sub in mark.get_subpaths():
        m = VMobject()
        m.set_points(sub)
        # Manim lays a sheen gradient across the mobject's *bounding box*
        # along the sheen direction, so the slice of the ramp this stroke
        # gets must be sampled at that box's corners — not at the extremes of
        # its own points, which for a bent stroke sit elsewhere.
        t0 = axis_t(m.get_corner(DL))
        t1 = axis_t(m.get_corner(UR))
        # The brand gradient has five stops, so two colours per stroke would
        # cut the corners between them. Sample the real curve across the slice
        # this stroke spans and hand the whole ramp over.
        stops = [gradient_at(t0 + (t1 - t0) * k / (GRADIENT_SAMPLES - 1))
                 for k in range(GRADIENT_SAMPLES)]
        m.set_stroke(width=0)
        # `set_fill` with a list plus a sheen direction is what actually
        # renders a gradient across a single path. `set_color_by_gradient`
        # looks like the right call and is not: on a leaf VMobject it
        # collapses to a flat colour and silently throws the sweep away.
        m.set_fill(color=stops, opacity=1.0)
        m.set_sheen_direction(UR)
        m.axis_t = 0.5 * (t0 + t1)
        swoosh.add(m)
    swoosh.submobjects.sort(key=lambda m: m.axis_t)      # launch order

    words = VGroup(*svg.submobjects)
    words.set_stroke(width=0).set_fill(text_color, 1.0)
    words.submobjects.sort(key=lambda m: (-round(m.get_center()[1], 1),
                                          m.get_center()[0]))

    # split the wordmark into its two lines, so a caller can hand the
    # "Vertica" line an existing piece of type to transform into
    ys = sorted(m.get_center()[1] for m in words)
    gaps = [(ys[i + 1] - ys[i], i) for i in range(len(ys) - 1)]
    _, cut = max(gaps)
    split_y = (ys[cut] + ys[cut + 1]) / 2
    line_vertica = VGroup(*[m for m in words if m.get_center()[1] <= split_y])
    line_rocket = VGroup(*[m for m in words if m.get_center()[1] > split_y])

    g = VGroup(swoosh, words)
    g.swoosh, g.words = swoosh, words
    g.line_rocket, g.line_vertica = line_rocket, line_vertica
    return g


def rocket_software_mark(height: float = 0.30,
                         text_color: str = TEXT_WHITE) -> VGroup:
    """The Rocket Software mark on its own — the swoosh and its wordmark.

    Cut from the same official artwork as the full lockup (the "Vertica" line
    is simply left off), so it is the approved mark rather than a second logo.
    """
    lk = lockup_vector(height=2.0, text_color=text_color)
    swoosh, words = lk.swoosh, lk.line_rocket
    # on its own the wordmark centres against the mark instead of sitting on
    # the upper of two lines
    words.move_to([words.get_center()[0], swoosh.get_center()[1], 0])
    g = VGroup(swoosh, words)
    g.set(height=height)
    g.swoosh, g.words = swoosh, words
    return g


def reveal_lockup(scene, lockup: VGroup, draw: float = 2.0,
                  text: float = 1.5, glow: float = 0.55):
    """Draw the mark, then add the words to it. Nothing is replaced.

    Every mobject animated here is the one that stays on screen: the strokes
    are drawn *at* their final positions, so the emblem never jumps and the
    wordmark joins the same object rather than a new one.
    """
    scene.play(
        LaggedStart(*[Create(m) for m in lockup.swoosh], lag_ratio=0.13),
        run_time=draw, rate_func=rate_functions.ease_in_out_sine,
    )
    scene.play(
        LaggedStart(*[FadeIn(g, shift=RIGHT * 0.3) for g in lockup.words],
                    lag_ratio=0.025),
        run_time=text, rate_func=rate_functions.ease_out_cubic,
    )

    # a brief bloom over the finished emblem — an overlay that fades away and
    # leaves the lockup exactly as drawn
    halo = lockup.copy()
    halo.set_stroke(WHITE, 2.5, 1.0).set_fill(WHITE, 1.0).set_opacity(0.0)
    scene.add(halo)
    scene.play(halo.animate.set_opacity(0.5), run_time=glow * 0.4,
               rate_func=rate_functions.ease_out_quad)
    scene.play(halo.animate.set_opacity(0.0), run_time=glow * 0.6,
               rate_func=rate_functions.ease_in_quad)
    scene.remove(halo)
    return lockup


class RocketVerticaReveal(Scene):
    """Standalone reveal: draw the mark, write the words, bloom, hold."""

    def construct(self):
        self.camera.background_color = "#000000"
        lockup = lockup_vector(height=2.2).move_to(ORIGIN)
        reveal_lockup(self, lockup, draw=2.0, text=1.5, glow=0.55)
        self.wait(2.0)
