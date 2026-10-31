"""SVG bar charts for the product comparison (used by compare.py; standard library).

Every chart is a self-contained SVG with light and dark colors (prefers-color-scheme),
one series color per product (fixed order), thin bars with a rounded data end, values
on the caps, a legend, and a <title> per bar as tooltip. Rendered by GitHub in Markdown.
"""
from pathlib import Path

SERIES = [  # fixed order: slot 1 blue, 2 orange, 3 aqua, 4 yellow (validated in both modes)
    {"light": "#2a78d6", "dark": "#3987e5"},
    {"light": "#eb6834", "dark": "#d95926"},
    {"light": "#1baf7a", "dark": "#199e70"},
    {"light": "#eda100", "dark": "#c98500"},
]
STYLE = """<style>
  text { font-family: system-ui, -apple-system, "Segoe UI", sans-serif; font-size: 12px; fill: #52514e; }
  .ink { fill: #0b0b0b; } .muted { fill: #898781; } .title { font-size: 14px; font-weight: 600; fill: #0b0b0b; }
  .grid { stroke: #e1e0d9; stroke-width: 1; } .axis { stroke: #c3c2b7; stroke-width: 1; }
  .bg { fill: #fcfcfb; } .val { font-variant-numeric: tabular-nums; }
  %s
  @media (prefers-color-scheme: dark) {
    text { fill: #c3c2b7; } .ink, .title { fill: #ffffff; } .muted { fill: #898781; }
    .grid { stroke: #2c2c2a; } .axis { stroke: #383835; } .bg { fill: #1a1a19; }
    %s
  }
</style>"""


# a lower bound is drawn lighter with a dashed outline, so it reads as "at least this"
HATCH = ' fill-opacity="0.45" stroke="#898781" stroke-dasharray="3 2" stroke-width="1"'


def style(n):
    light = " ".join(f".s{i} {{ fill: {SERIES[i]['light']}; }}" for i in range(n))
    dark = " ".join(f".s{i} {{ fill: {SERIES[i]['dark']}; }}" for i in range(n))
    return STYLE % (light, dark)


def nice_max(v):
    """Axis top: a round number just above v."""
    if v <= 0:
        return 1
    mag = 10 ** len(str(int(v)))
    for f in (0.1, 0.12, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0):
        if v <= f * mag:
            return f * mag
    return mag


def fmt(v, unit):
    if unit == "s" and v >= 100:
        return f"{v:,.0f} s"
    if unit == "s" and v >= 10:
        return f"{v:.1f} s"
    return f"{v:,.2f} {unit}" if v < 10 else f"{v:,.1f} {unit}"


def bar_path(x, y, w, h, r=4):
    """Column with a rounded top (data end) and a square base on the baseline."""
    r = min(r, w / 2, h)
    return (f"M{x:.1f},{y + h:.1f} V{y + r:.1f} Q{x:.1f},{y:.1f} {x + r:.1f},{y:.1f} "
            f"H{x + w - r:.1f} Q{x + w:.1f},{y:.1f} {x + w:.1f},{y + r:.1f} V{y + h:.1f} Z")


def grouped_columns(title, unit, groups, series, values, path, note="", lower=None):
    """groups: x labels; series: legend names; values[s][g]: number or None;
    lower[s][g]: True when the value is a lower bound (labelled "≥", drawn hatched)."""
    n_s, n_g = len(series), len(groups)
    band = max(120, n_s * 60 + 40)   # room for each column's value label
    bar = min(28, (band - 40) // n_s - 4)
    gap = (band - 40) // n_s - bar
    left, top, right, bottom = 60, 56, 20, 52
    plot_h = 220
    width = max(left + n_g * band + right, left + 8 * len(title) + right, left + 6 * len(note) + right)
    height = top + plot_h + bottom + (18 if note else 0)
    vmax = nice_max(max(v for row in values for v in row if v is not None) * 1.15)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
           f'viewBox="0 0 {width} {height}" role="img" aria-label="{title}">', style(n_s),
           f'<rect class="bg" width="{width}" height="{height}"/>',
           f'<text class="title" x="{left}" y="22">{title}</text>']
    lx = left
    for i, s in enumerate(series):   # legend
        out.append(f'<rect class="s{i}" x="{lx}" y="32" width="10" height="10" rx="2"/>'
                   f'<text x="{lx + 14}" y="41">{s}</text>')
        lx += 14 + 7 * len(s) + 18
    for k in range(5):               # gridlines and ticks
        v = vmax * k / 4
        y = top + plot_h - plot_h * k / 4
        out.append(f'<line class="grid" x1="{left}" x2="{width - right}" y1="{y:.1f}" y2="{y:.1f}"/>'
                   f'<text class="muted val" x="{left - 8}" y="{y + 4:.1f}" text-anchor="end">{v:g}</text>')
    out.append(f'<line class="axis" x1="{left}" x2="{width - right}" y1="{top + plot_h}" y2="{top + plot_h}"/>')
    for g, name in enumerate(groups):
        x0 = left + g * band + (band - n_s * (bar + gap)) / 2
        out.append(f'<text class="ink" x="{left + g * band + band / 2}" y="{top + plot_h + 20}" text-anchor="middle">{name}</text>')
        for i, s in enumerate(series):
            v = values[i][g]
            if v is None:
                continue
            h = plot_h * v / vmax
            x = x0 + i * (bar + gap)
            y = top + plot_h - h
            lb = "≥ " if lower and lower[i][g] else ""
            out.append(f'<path class="s{i}" d="{bar_path(x, y, bar, h)}"{HATCH if lb else ""}><title>{s}, {name}: {lb}{fmt(v, unit)}</title></path>'
                       f'<text class="ink val" x="{x + bar / 2:.1f}" y="{y - 6:.1f}" text-anchor="middle" font-size="11">{lb}{fmt(v, unit)}</text>')
    if note:
        out.append(f'<text class="muted" x="{left}" y="{height - 8}" font-size="11">{note}</text>')
    out.append("</svg>")
    Path(path).write_text("\n".join(out))


def grouped_bars_h(title, unit, items, series, values, path, note="", lower=None):
    """Horizontal grouped bars: items = row labels, values[s][row]; lower[s][row]: True
    when the value is a lower bound (a query stopped at its time limit: "> x", hatched)."""
    n_s, n_r = len(series), len(items)
    bar, gap, row_h = 12, 2, n_s * 14 + 10
    left, top, right, bottom = 56, 56, 90, 16 + (18 if note else 0)
    plot_w = 520
    width = left + plot_w + right
    height = top + n_r * row_h + bottom
    vmax = nice_max(max(v for row in values for v in row if v is not None) * 1.02)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
           f'viewBox="0 0 {width} {height}" role="img" aria-label="{title}">', style(n_s),
           f'<rect class="bg" width="{width}" height="{height}"/>',
           f'<text class="title" x="{left}" y="22">{title}</text>']
    lx = left
    for i, s in enumerate(series):
        out.append(f'<rect class="s{i}" x="{lx}" y="32" width="10" height="10" rx="2"/>'
                   f'<text x="{lx + 14}" y="41">{s}</text>')
        lx += 14 + 7 * len(s) + 18
    for k in range(5):
        v = vmax * k / 4
        x = left + plot_w * k / 4
        out.append(f'<line class="grid" x1="{x:.1f}" x2="{x:.1f}" y1="{top}" y2="{top + n_r * row_h}"/>'
                   f'<text class="muted val" x="{x:.1f}" y="{top + n_r * row_h + 14}" text-anchor="middle">{v:g}</text>')
    out.append(f'<line class="axis" x1="{left}" x2="{left}" y1="{top}" y2="{top + n_r * row_h}"/>')
    for r, name in enumerate(items):
        y0 = top + r * row_h + 5
        out.append(f'<text class="ink" x="{left - 8}" y="{y0 + n_s * 7 + 4}" text-anchor="end">{name}</text>')
        for i, s in enumerate(series):
            v = values[i][r]
            if v is None:
                continue
            w = plot_w * v / vmax
            y = y0 + i * (bar + gap)
            rr = min(4, w / 2)
            d = (f"M{left},{y} H{left + w - rr:.1f} Q{left + w:.1f},{y} {left + w:.1f},{y + rr:.1f} "
                 f"V{y + bar - rr:.1f} Q{left + w:.1f},{y + bar} {left + w - rr:.1f},{y + bar} H{left} Z")
            lb = "> " if lower and lower[i][r] else ""
            out.append(f'<path class="s{i}" d="{d}"{HATCH if lb else ""}><title>{s}, query {name}: {lb}{fmt(v, unit)}'
                       f'{" (stopped at its time limit)" if lb else ""}</title></path>'
                       f'<text class="ink val" x="{left + w + 5:.1f}" y="{y + bar - 2}" font-size="11">{lb}{fmt(v, unit)}</text>')
    if note:
        out.append(f'<text class="muted" x="{left}" y="{height - 6}" font-size="11">{note}</text>')
    out.append("</svg>")
    Path(path).write_text("\n".join(out))
