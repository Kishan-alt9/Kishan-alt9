#!/usr/bin/env python3

"""
Render data/contributions.json as a GitHub-style contribution heatmap SVG.

The heatmap uses:
- 53-week x 7-day calendar
- rounded contribution boxes
- animated one-shot reveal
- Less → More legend
- contribution statistics footer
"""

import datetime
import json
import os


HERE = os.path.dirname(__file__)

IN_PATH = os.path.join(
    HERE,
    "..",
    "data",
    "contributions.json"
)

OUT_PATH = os.path.join(
    HERE,
    "..",
    "contrib-heatmap.svg"
)


# -------------------------------------------------------------------
# GitHub-style contribution colors
# -------------------------------------------------------------------

PALETTE = [
    "#161b22",
    "#0e4429",
    "#006d32",
    "#26a641",
    "#39d353",
    "#69f0a0"
]


# -------------------------------------------------------------------
# Layout
# -------------------------------------------------------------------

CELL = 12
GAP = 3
STEP = CELL + GAP

PAD = 22

LEFT_LABEL_W = 30
TOP_LABEL_H = 20

TITLEBAR_H = 30


# -------------------------------------------------------------------
# Colors
# -------------------------------------------------------------------

BG = "#0a0e14"
BG2 = "#0d1420"

FRAME = "#1f6feb"

MUTED = "#7d8590"
TEXT = "#e6edf3"

ACCENT = "#22d3ee"
GREEN = "#39d353"
GOLD = "#f2cc60"


# -------------------------------------------------------------------
# Animation timing
# -------------------------------------------------------------------

COL_T = 0.018
ROW_T = 0.045

CELL_DUR = 0.42


def level_for(count):

    if count == 0:
        return 0

    if count <= 5:
        return 1

    if count <= 15:
        return 2

    if count <= 30:
        return 3

    if count <= 50:
        return 4

    return 5


def build_grid(days):

    first = datetime.date.fromisoformat(
        days[0]["date"]
    )

    # Sunday = 0
    lead_pad = (
        first.weekday() + 1
    ) % 7

    grid = []

    col = [None] * lead_pad


    for d in days:

        date = datetime.date.fromisoformat(
            d["date"]
        )

        weekday = (
            date.weekday() + 1
        ) % 7


        while len(col) < weekday:
            col.append(None)


        col.append(
            (
                d["date"],
                d["count"],
                level_for(d["count"])
            )
        )


        if len(col) == 7:

            grid.append(col)

            col = []


    if col:

        while len(col) < 7:
            col.append(None)

        grid.append(col)


    return grid


def render(data):

    days = data["days"]

    grid = build_grid(days)

    n_cols = len(grid)

    art_w = n_cols * STEP
    art_h = 7 * STEP


    # ---------------------------------------------------------------
    # Month labels
    # ---------------------------------------------------------------

    month_labels = []

    seen_months = set()


    for ci, column in enumerate(grid):

        for cell in column:

            if cell is None:
                continue


            date = datetime.date.fromisoformat(
                cell[0]
            )

            key = (
                date.year,
                date.month
            )


            if (
                key not in seen_months
                and date.day <= 7
            ):

                seen_months.add(key)

                month_labels.append(
                    (
                        ci,
                        date.strftime("%b")
                    )
                )

            break


    # ---------------------------------------------------------------
    # Canvas
    # ---------------------------------------------------------------

    canvas_w = (
        PAD
        + LEFT_LABEL_W
        + art_w
        + PAD
    )

    stats_h = 88

    canvas_h = (
        TITLEBAR_H
        + TOP_LABEL_H
        + art_h
        + stats_h
        + PAD
    )


    # ---------------------------------------------------------------
    # Animation CSS
    # ---------------------------------------------------------------

    css = f"""
@keyframes cell {{
  0% {{
    opacity: 0;
    transform: translateY(-6px);
  }}

  100% {{
    opacity: 1;
    transform: translateY(0);
  }}
}}

.c {{
  opacity: 0;
  animation:
    cell {CELL_DUR:.2f}s
    cubic-bezier(.2,.8,.2,1)
    both;
}}
""".strip()


    # ---------------------------------------------------------------
    # SVG start
    # ---------------------------------------------------------------

    parts = [

        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{canvas_w}" '
        f'height="{canvas_h}" '
        f'viewBox="0 0 {canvas_w} {canvas_h}" '
        f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',


        f'<style>{css}</style>',


        '<defs>'

        f'<linearGradient id="hbg" '
        f'x1="0" y1="0" x2="0" y2="1">'

        f'<stop offset="0" '
        f'stop-color="{BG2}"/>'

        f'<stop offset="1" '
        f'stop-color="{BG}"/>'

        '</linearGradient>'

        '</defs>',


        f'<rect '
        f'width="{canvas_w}" '
        f'height="{canvas_h}" '
        f'rx="12" '
        f'fill="url(#hbg)"/>',


        f'<rect '
        f'x="0.5" '
        f'y="0.5" '
        f'width="{canvas_w - 1}" '
        f'height="{canvas_h - 1}" '
        f'rx="12" '
        f'fill="none" '
        f'stroke="{FRAME}" '
        f'stroke-width="1" '
        f'stroke-opacity="0.55"/>',


        f'<line '
        f'x1="0" '
        f'y1="{TITLEBAR_H}" '
        f'x2="{canvas_w}" '
        f'y2="{TITLEBAR_H}" '
        f'stroke="{FRAME}" '
        f'stroke-opacity="0.35"/>'

    ]


    # ---------------------------------------------------------------
    # Terminal dots
    # ---------------------------------------------------------------

    for i, dotcol in enumerate(
        [
            "#ff5f56",
            "#ffbd2e",
            "#27c93f"
        ]
    ):

        parts.append(
            f'<circle '
            f'cx="{PAD + i * 16}" '
            f'cy="{TITLEBAR_H / 2}" '
            f'r="5" '
            f'fill="{dotcol}"/>'
        )


    # Personalized terminal title

    parts.append(
        f'<text '
        f'x="{canvas_w / 2}" '
        f'y="{TITLEBAR_H / 2 + 4}" '
        f'fill="{MUTED}" '
        f'font-size="12" '
        f'text-anchor="middle">'
        f'Kishan-alt9@github: ~/contributions --graph'
        f'</text>'
    )


    # ---------------------------------------------------------------
    # Grid positioning
    # ---------------------------------------------------------------

    grid_top = (
        TITLEBAR_H
        + TOP_LABEL_H
    )

    grid_left = (
        PAD
        + LEFT_LABEL_W
    )


    # ---------------------------------------------------------------
    # Month labels
    # ---------------------------------------------------------------

    for ci, label in month_labels:

        x = (
            grid_left
            + ci * STEP
        )

        parts.append(
            f'<text '
            f'x="{x}" '
            f'y="{TITLEBAR_H + 14}" '
            f'fill="{MUTED}" '
            f'font-size="10">'
            f'{label}'
            f'</text>'
        )


    # ---------------------------------------------------------------
    # Weekday labels
    # ---------------------------------------------------------------

    for wi, wname in [
        (1, "Mon"),
        (3, "Wed"),
        (5, "Fri")
    ]:

        y = (
            grid_top
            + wi * STEP
            + CELL * 0.78
        )

        parts.append(
            f'<text '
            f'x="{PAD}" '
            f'y="{y:.1f}" '
            f'fill="{MUTED}" '
            f'font-size="9">'
            f'{wname}'
            f'</text>'
        )


    # ---------------------------------------------------------------
    # Contribution boxes
    # ---------------------------------------------------------------

    for ci, column in enumerate(grid):

        gx = (
            grid_left
            + ci * STEP
        )


        for ri, cell in enumerate(column):

            if cell is None:
                continue


            date_s, count, lvl = cell


            gy = (
                grid_top
                + ri * STEP
            )


            delay = (
                ci * COL_T
                + ri * ROW_T
            )


            plural = (
                "s"
                if count != 1
                else ""
            )


            parts.append(
                f'<rect '
                f'class="c" '
                f'x="{gx}" '
                f'y="{gy}" '
                f'width="{CELL}" '
                f'height="{CELL}" '
                f'rx="2.5" '
                f'fill="{PALETTE[lvl]}" '
                f'style="animation-delay:{delay:.3f}s">'

                f'<title>'
                f'{date_s}: '
                f'{count} contribution{plural}'
                f'</title>'

                f'</rect>'
            )


    # ---------------------------------------------------------------
    # Legend
    # ---------------------------------------------------------------

    leg_y = (
        grid_top
        + art_h
        + 6
    )


    leg_x = (
        canvas_w
        - PAD
        - (
            len(PALETTE)
            * (CELL - 1)
            + 70
        )
    )


    parts.append(
        f'<text '
        f'x="{leg_x}" '
        f'y="{leg_y + CELL * 0.8:.1f}" '
        f'fill="{MUTED}" '
        f'font-size="10" '
        f'text-anchor="end">'
        f'Less'
        f'</text>'
    )


    lx = leg_x + 8


    for lvl, color in enumerate(PALETTE):

        parts.append(
            f'<rect '
            f'x="{lx}" '
            f'y="{leg_y}" '
            f'width="{CELL - 1}" '
            f'height="{CELL - 1}" '
            f'rx="2.2" '
            f'fill="{color}"/>'
        )

        lx += CELL


    parts.append(
        f'<text '
        f'x="{lx + 4}" '
        f'y="{leg_y + CELL * 0.8:.1f}" '
        f'fill="{MUTED}" '
        f'font-size="10">'
        f'More'
        f'</text>'
    )


    # ---------------------------------------------------------------
    # Statistics section
    # ---------------------------------------------------------------

    sep_y = (
        leg_y
        + CELL
        + 14
    )


    parts.append(
        f'<line '
        f'x1="0" '
        f'y1="{sep_y}" '
        f'x2="{canvas_w}" '
        f'y2="{sep_y}" '
        f'stroke="{FRAME}" '
        f'stroke-opacity="0.25"/>'
    )


    # Get stats

    cs = data["current_streak"]["length"]

    ls = data["longest_streak"]["length"]

    total = data["total_contributions"]

    best = data["best_day"]

    rng = data["range"]


    ly = sep_y + 24


    # Total contributions

    parts.append(
        f'<text '
        f'x="{PAD}" '
        f'y="{ly}" '
        f'font-size="13" '
        f'fill="{GREEN}">'

        f'<tspan font-weight="700">'
        f'{total:,}'
        f'</tspan>'

        f'<tspan fill="{MUTED}">'
        f' contributions in the last year'
        f'</tspan>'

        f'</text>'
    )


    # Date range

    parts.append(
        f'<text '
        f'x="{canvas_w - PAD}" '
        f'y="{ly}" '
        f'font-size="12" '
        f'fill="{MUTED}" '
        f'text-anchor="end">'

        f'{rng["start"]} &#8594; '
        f'{rng["end"]}'

        f'</text>'
    )


    ly += 24


    # Streaks

    parts.append(
        f'<text '
        f'x="{PAD}" '
        f'y="{ly}" '
        f'font-size="13" '
        f'fill="{MUTED}">'

        f'current streak '

        f'<tspan '
        f'fill="{ACCENT}" '
        f'font-weight="700">'
        f'{cs} days'
        f'</tspan>'

        f'<tspan fill="{MUTED}">'
        f'   &#183;   longest '
        f'</tspan>'

        f'<tspan '
        f'fill="{ACCENT}" '
        f'font-weight="700">'
        f'{ls} days'
        f'</tspan>'

        f'</text>'
    )


    # Best day

    parts.append(
        f'<text '
        f'x="{canvas_w - PAD}" '
        f'y="{ly}" '
        f'font-size="12" '
        f'fill="{MUTED}" '
        f'text-anchor="end">'

        f'best day '

        f'<tspan '
        f'fill="{GOLD}" '
        f'font-weight="700">'
        f'{best["count"]}'
        f'</tspan>'

        f' on {best["date"]}'

        f'</text>'
    )


    parts.append("</svg>")


    return "".join(parts)


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------

if __name__ == "__main__":

    with open(
        IN_PATH,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)


    svg = render(data)


    with open(
        OUT_PATH,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(svg)


    print(
        f"wrote {OUT_PATH} "
        f"({len(svg)} bytes)"
    )
    