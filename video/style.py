"""
style.py — the single source of visual truth.

Palette, fonts, typographic scale and the two persistent chrome elements
(chapter marker, progress line).  Import this before anything else: it
registers the fonts and configures Manim.
"""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path

import manimpango
from manim import *

ROOT = Path(__file__).parent
FONT_DIR = ROOT / "assets" / "fonts"

# --------------------------------------------------------------------------
# canvas
# --------------------------------------------------------------------------
config.background_color = "#000000"
# Resolution and frame rate come from the CLI quality flag: `-ql` for drafts,
# `-qh` (1920x1080 @ 60 fps) for the final.  Hard-coding them here would make
# every draft render at full size.

FRAME_W = config.frame_width          # 14.222…
FRAME_H = config.frame_height         # 8.0
SAFE = 0.6
LEFT_X = -FRAME_W / 2 + SAFE          # −6.51
RIGHT_X = FRAME_W / 2 - SAFE
TOP_Y = FRAME_H / 2 - SAFE
BOT_Y = -FRAME_H / 2 + SAFE

TITLE_ANCHOR = np.array([-6.2, TOP_Y, 0.0])

# --------------------------------------------------------------------------
# palette — the Rocket brand, defined once
#
# The brand sheet gives six values: black, a primary and a secondary, and
# three supporting tones.  Everything purple or lavender on screen — title
# rules, chart bars, icon strokes, pills, highlights — resolves to one of
# these.  There is no other purple in the film.
#
#   BRAND_PRIMARY    #990099   the accent: rules, fills, strokes, chart bars
#   BRAND_SECONDARY  #D257FC   type and anything thin on black
#
# The rule that decides which: **#990099 is never used for type on black.**
# It measures 2.8:1 against the ground, which is below legibility for text at
# any size the film uses.  #D257FC measures 6.6:1 and is what carries words.
# Primary is for shapes, where mass does the work that contrast cannot.
# --------------------------------------------------------------------------
BRAND_PRIMARY = "#990099"
BRAND_SECONDARY = "#D257FC"

# The rest of the same sheet. Dark fills and gradient stops only — never type.
BRAND_DEEP = "#4500A4"
BRAND_VIOLET = "#751ECA"
BRAND_BLUE = "#503EFF"

# Secondary, lightened, for a fill that has to sit *behind* white type.
BRAND_SECONDARY_LIGHT = "#E9A8FF"

# Short aliases of the brand values.
PURPLE_DEEP = BRAND_DEEP
PURPLE = BRAND_PRIMARY
MAGENTA = BRAND_PRIMARY
VIOLET_BLUE = BRAND_SECONDARY
ELECTRIC = BRAND_BLUE
PINK = BRAND_SECONDARY
LILAC = BRAND_SECONDARY

GRAY_TEXT = "#B8B8C4"
WHITE_SOFT = "#F2F2F5"
GREEN_OK = "#19B27A"
AMBER_WARN = "#E5A21B"
RED_STOP = "#C0392B"

DIM = 0.22          # opacity used for "not the subject right now"
HAIRLINE = 1.2      # stroke width for structural rules

# --------------------------------------------------------------------------
# fonts
# --------------------------------------------------------------------------
_PREFERRED_SANS = "Calibri"
_PREFERRED_MONO = "Consolas"
_FALLBACK_SANS = "Carlito"        # metric-compatible with Calibri
_FALLBACK_MONO = "Inconsolata"    # open substitute for Consolas


def _register_bundled_fonts() -> None:
    if not FONT_DIR.exists():
        return
    for ttf in sorted(FONT_DIR.glob("*.ttf")):
        manimpango.register_font(str(ttf))


_register_bundled_fonts()
_AVAILABLE = set(manimpango.list_fonts())

SANS = _PREFERRED_SANS if _PREFERRED_SANS in _AVAILABLE else _FALLBACK_SANS
MONO = _PREFERRED_MONO if _PREFERRED_MONO in _AVAILABLE else _FALLBACK_MONO

FONT_SUBSTITUTED = (SANS != _PREFERRED_SANS) or (MONO != _PREFERRED_MONO)

assert SANS in _AVAILABLE, (
    f"Neither {_PREFERRED_SANS} nor {_FALLBACK_SANS} is installed. "
    f"Put calibri.ttf (or Carlito) in {FONT_DIR}."
)
assert MONO in _AVAILABLE, (
    f"Neither {_PREFERRED_MONO} nor {_FALLBACK_MONO} is installed. "
    f"Put consola.ttf (or Inconsolata) in {FONT_DIR}."
)

# --------------------------------------------------------------------------
# typographic scale
# --------------------------------------------------------------------------
FS_HERO = 72
FS_BIG = 48
FS_TITLE = 44
FS_HEAD = 36
FS_BODY = 28
FS_CODE = 24
FS_CAPTION = 22
FS_TINY = 18

MAX_TEXT_W = FRAME_W * 0.60


# --------------------------------------------------------------------------
# Text is always rendered at TEXT_BASE and scaled down to the size we want.
#
# Manim lays glyphs out from the SVG Pango produces, and Pango rounds glyph
# positions to whole units at the size it is asked for. At font_size 16-22
# that rounding is coarse enough to open visible gaps inside words
# ("Wor kload", "Databas e", "Quer y") and to swallow word spaces. Rendering
# at 96 and scaling gives the rounding six times the resolution, and the
# spacing comes out even at every size. The scale is exact, so a piece of text
# still ends up the same height as font_size would have made it, and every
# layout measurement downstream is unchanged.
# --------------------------------------------------------------------------
TEXT_BASE = 96


# Pango lays the text out inside a box of config.pixel_width x pixel_height,
# so at TEXT_BASE a long line would wrap — and it would wrap differently at
# 480p than at 1080p, while manim's text-SVG cache is not keyed on the render
# resolution. Widening the box for the duration of the build makes the result
# identical at every quality, and therefore safe to cache.
_LAYOUT_W, _LAYOUT_H = 60_000, 8_000


@contextmanager
def _unbounded_layout():
    pw, ph = config.pixel_width, config.pixel_height
    config.pixel_width, config.pixel_height = _LAYOUT_W, _LAYOUT_H
    try:
        yield
    finally:
        config.pixel_width, config.pixel_height = pw, ph


def styled_text(text: str, size: float, font: str, color: str, weight=NORMAL,
          **kw) -> Text:
    with _unbounded_layout():
        t = Text(text, font=font, font_size=TEXT_BASE, color=color,
                 weight=weight, **kw)
    t.scale(size / TEXT_BASE)
    return t


def body(text: str, size: int = FS_BODY, color: str = WHITE_SOFT,
         weight=NORMAL, **kw) -> Text:
    return styled_text(text, size, SANS, color, weight, **kw)


def head(text: str, size: int = FS_HEAD, color: str = WHITE_SOFT, **kw) -> Text:
    return body(text, size=size, color=color, weight=NORMAL, **kw)


def caption(text: str, size: int = FS_CAPTION, color: str = GRAY_TEXT,
            **kw) -> Text:
    return body(text, size=size, color=color, **kw)


def tiny(text: str, size: int = FS_TINY, color: str = GRAY_TEXT, **kw) -> Text:
    return body(text, size=size, color=color, **kw)


def mono(text: str, size: int = FS_CODE, color: str = LILAC, **kw) -> Text:
    """Consolas — for code, prompts, commands, identifiers. Never prose."""
    return styled_text(text, size, MONO, color, **kw)


def markup(text: str, size: int = FS_BODY, color: str = WHITE_SOFT,
           font: str | None = None, **kw) -> MarkupText:
    with _unbounded_layout():
        m = MarkupText(text, font=font or SANS, font_size=TEXT_BASE,
                       color=color, **kw)
    m.scale(size / TEXT_BASE)
    return m


def para(lines, size: int = FS_BODY, color: str = WHITE_SOFT,
         align="left", buff: float = 0.22, **kw) -> VGroup:
    """A paragraph built from individual Text lines so we control leading."""
    g = VGroup(*[body(l, size=size, color=color, **kw) for l in lines])
    g.arrange(DOWN, aligned_edge=LEFT if align == "left" else ORIGIN, buff=buff)
    return g


# --------------------------------------------------------------------------
# easing shorthands
# --------------------------------------------------------------------------
EASE_IN = rate_functions.ease_in_cubic
EASE_OUT = rate_functions.ease_out_cubic
EASE = rate_functions.ease_in_out_cubic
SMOOTH = smooth


def enter(m: Mobject, shift=UP * 0.25, **kw) -> Animation:
    return FadeIn(m, shift=shift, rate_func=EASE_OUT, **kw)


def leave(m: Mobject, shift=DOWN * 0.15, **kw) -> Animation:
    return FadeOut(m, shift=shift, rate_func=EASE_IN, **kw)
