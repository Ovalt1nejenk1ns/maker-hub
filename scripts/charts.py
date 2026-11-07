"""Tiny dependency-free SVG chart helpers. Colors come from CSS variables so the theme controls them."""
from html import escape


def bar_chart(items, width=640, bar_h=26, gap=8, label_w=230):
    """items: list of (label, value). Horizontal bars, longest = full width."""
    if not items:
        return ""
    vmax = max(v for _, v in items) or 1
    h = len(items) * (bar_h + gap)
    plot_w = width - label_w - 70
    out = [f'<svg viewBox="0 0 {width} {h}" role="img" class="chart">']
    for i, (label, v) in enumerate(items):
        y = i * (bar_h + gap)
        w = max(2, plot_w * v / vmax)
        short = label if len(label) <= 32 else label[:31] + "…"
        out.append(
            f'<text x="0" y="{y + bar_h * 0.68}" class="lbl">{escape(short)}</text>'
            f'<rect x="{label_w}" y="{y}" width="{w:.1f}" height="{bar_h}" rx="3" class="bar"/>'
            f'<text x="{label_w + w + 6:.1f}" y="{y + bar_h * 0.68}" class="val">{v:,}</text>')
    out.append("</svg>")
    return "".join(out)


def line_chart(series, width=640, height=220):
    """series: {name: [(date_str, value), ...]}. Needs >=2 dates overall to draw."""
    dates = sorted({d for pts in series.values() for d, _ in pts})
    if len(dates) < 2:
        return ""
    pad_l, pad_r, pad_t, pad_b = 52, 12, 10, 28
    vals = [v for pts in series.values() for _, v in pts]
    lo, hi = min(vals), max(vals)
    if hi == lo:
        hi = lo + 1
    xi = {d: pad_l + (width - pad_l - pad_r) * i / (len(dates) - 1) for i, d in enumerate(dates)}
    y = lambda v: pad_t + (height - pad_t - pad_b) * (1 - (v - lo) / (hi - lo))
    out = [f'<svg viewBox="0 0 {width} {height}" role="img" class="chart">']
    for frac in (0, 0.5, 1):
        v = lo + (hi - lo) * frac
        out.append(f'<line x1="{pad_l}" x2="{width - pad_r}" y1="{y(v):.1f}" y2="{y(v):.1f}" class="grid"/>'
                   f'<text x="{pad_l - 6}" y="{y(v) + 4:.1f}" class="axis" text-anchor="end">{int(v):,}</text>')
    out.append(f'<text x="{pad_l}" y="{height - 6}" class="axis">{dates[0]}</text>'
               f'<text x="{width - pad_r}" y="{height - 6}" class="axis" text-anchor="end">{dates[-1]}</text>')
    for n, (name, pts) in enumerate(sorted(series.items())):
        path = " ".join(f"{xi[d]:.1f},{y(v):.1f}" for d, v in sorted(pts))
        out.append(f'<polyline points="{path}" class="line s{n % 6}"><title>{escape(name)}</title></polyline>')
    out.append("</svg>")
    return "".join(out)
