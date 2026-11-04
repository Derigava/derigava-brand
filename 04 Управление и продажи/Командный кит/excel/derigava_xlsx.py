"""Derigava Terminal styling for .xlsx tables (openpyxl)."""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field

from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

# --- tokens (from the Derigava Terminal design system, tokens.json v2) -------
# dark = Terminal (default), light = Paper (print, projector in a bright room).
# acid = accent as text/line/bar; acid_fill = accent as a fill under on_acid text.

THEMES = {
    "dark": {
        "bg": "0A0B0A",
        "surface": "131613",
        "surface_raised": "1C201C",
        "line": "2C332B",
        "ink": "ECF2E8",
        "ink_muted": "8F998C",
        "acid": "B8FF2C",
        "acid_fill": "B8FF2C",
        "acid_deep": "1E3A00",
        "on_acid": "0A0B0A",
        "alert": "FF7A33",
    },
    "light": {
        "bg": "F3F5EF",
        "surface": "FFFFFF",
        "surface_raised": "E9EDE4",
        "line": "D3DACD",
        "ink": "101310",
        "ink_muted": "566052",
        "acid": "3D6E00",
        "acid_fill": "B8FF2C",
        "acid_deep": "E3F5C2",
        "on_acid": "0A0B0A",
        "alert": "B3460C",
    },
}
PALETTE = THEMES["dark"]  # backward-compatible alias

BRAND_FONTS = {"display": "Unbounded", "sans": "Onest", "mono": "JetBrains Mono"}
SAFE_FONTS = {"display": "Arial Black", "sans": "Segoe UI", "mono": "Consolas"}

# Excel points, scaled down from the 1080px-poster sizes for on-screen sheets.
SIZES = {"title": 18, "label": 9, "header": 9, "body": 11, "metric_sm": 11, "total": 12}

NUMBER_FORMATS = {
    "int": "#,##0",
    "num": "#,##0.0",
    "money": '#,##0 "₽"',
    "pct": "0%",
    "pct1": "0.0%",
    # ▲ / ▼ / ● glyphs instead of +/- ; colour comes from conditional formatting
    "delta": '"▲ "#,##0;"▼ "#,##0;"● "0',
    "delta_pct": '"▲ "0.0%;"▼ "0.0%;"● "0.0%',
    "date": "DD.MM",
    "datetime": "DD.MM HH:MM",
    "time": "HH:MM",
    "text": "@",
}


def _font_installed(name: str) -> bool:
    if sys.platform != "win32":
        return False
    key = name.replace(" ", "").lower()
    dirs = [os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Windows", "Fonts")]
    for d in dirs:
        try:
            if any(f.replace(" ", "").replace("-", "").lower().startswith(key) for f in os.listdir(d)):
                return True
        except OSError:
            pass
    return False


def pick_fonts(mode: str = "brand") -> dict:
    """'brand' = always brand fonts, 'safe' = always fallbacks,
    'auto' = brand font per role if installed here, else its fallback."""
    if mode == "brand":
        return dict(BRAND_FONTS)
    if mode == "safe":
        return dict(SAFE_FONTS)
    return {k: (v if _font_installed(v) else SAFE_FONTS[k]) for k, v in BRAND_FONTS.items()}


@dataclass
class DT:
    """Ready-made styles. Build once per workbook: DT.make(fonts='brand', theme='dark')."""
    fonts: dict
    theme: str = "dark"
    pal: dict = field(default_factory=lambda: dict(THEMES["dark"]))

    @classmethod
    def make(cls, fonts: str = "brand", theme: str = "dark") -> "DT":
        if theme not in THEMES:
            raise ValueError(f"theme must be one of {list(THEMES)}")
        return cls(pick_fonts(fonts), theme, dict(THEMES[theme]))

    def c(self, token: str) -> str:
        return self.pal[token]

    def fill(self, token: str) -> PatternFill:
        c = self.pal[token]
        return PatternFill("solid", start_color=c, end_color=c)

    def font(self, family: str, token: str = "ink", size: str = "body", bold: bool = False) -> Font:
        return Font(name=self.fonts[family], color=self.pal[token], size=SIZES[size], bold=bold)

    def side(self, token: str = "line", style: str = "thin") -> Side:
        return Side(style=style, color=self.pal[token])


def paint_background(ws, dt: DT, max_row: int, max_col: int, pad_rows: int = 2, pad_cols: int = 1):
    """Excel has no sheet background colour: fill the used area plus a margin with bg
    and hide gridlines so the sheet reads as one screen (dark) or one page (light)."""
    ws.sheet_view.showGridLines = False
    bg = dt.fill("bg")
    for r in range(1, max_row + pad_rows + 1):
        for c in range(1, max_col + pad_cols + 1):
            cell = ws.cell(r, c)
            if cell.fill is None or cell.fill.fgColor.rgb in (None, "00000000"):
                cell.fill = bg


def _is_numeric_col(rows, idx) -> bool:
    vals = [r[idx] for r in rows if idx < len(r) and r[idx] not in (None, "")]
    return bool(vals) and all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in vals)


def write_table(ws, headers, rows, *, title=None, label=None, formats=None, leader_row=None,
                total=None, start_row=1, start_col=1, fonts="brand", theme="dark", freeze=True,
                autofilter=False, col_widths=None, signature=True, alert_negative=False,
                paint_to_col=None, dt: DT | None = None):
    """Write a Derigava Terminal table. Returns dict with header_row, first_row, last_row, total_row.

    formats: {header: key from NUMBER_FORMATS or a raw Excel format string}
    leader_row: 1-based index into `rows` to highlight (acid-deep fill, acid first cell)
    total: {header: "sum" | "avg" | literal}; adds a total row with an acid top rule
    alert_negative: colour ▼ deltas in alert. Keep False for per-person tables (rating):
        people are not publicly flagged in alert; True for team risks (overdue, plan miss).
    paint_to_col: extend the background to this column (e.g. to sit under a chart)
    theme: "dark" (Terminal, default) | "light" (Paper); ignored when dt is passed.
    """
    dt = dt or DT.make(fonts, theme)
    formats = formats or {}
    ncol = len(headers)
    r = start_row
    c0 = start_col

    if label:
        ws.cell(r, c0, label.upper()).font = dt.font("mono", "ink_muted", "label")
        r += 1
    if title:
        cell = ws.cell(r, c0, title.rstrip("."))
        cell.font = dt.font("display", "ink", "title", bold=True)
        ws.row_dimensions[r].height = 30
        r += 2

    numeric = [_is_numeric_col(rows, i) for i in range(ncol)]
    fmt_for = []
    for i, h in enumerate(headers):
        f = formats.get(h)
        fmt_for.append(NUMBER_FORMATS.get(f, f) if f else ("#,##0" if numeric[i] else None))

    # header: mono label, muted, on bg, acid rule below
    header_row = r
    for i, h in enumerate(headers):
        cell = ws.cell(r, c0 + i, str(h).upper())
        cell.font = dt.font("mono", "ink_muted", "header", bold=True)
        cell.fill = dt.fill("bg")
        cell.border = Border(bottom=dt.side("acid", "medium"))
        cell.alignment = Alignment(horizontal="right" if numeric[i] else "left", vertical="center",
                                   indent=0 if numeric[i] else 1)
    ws.row_dimensions[r].height = 22
    r += 1

    first_row = r
    for k, row in enumerate(rows, start=1):
        is_leader = leader_row == k
        fill = dt.fill("acid_deep" if is_leader else "surface")
        for i in range(ncol):
            v = row[i] if i < len(row) else None
            cell = ws.cell(r, c0 + i, v)
            cell.fill = fill
            cell.border = Border(bottom=dt.side("line"))
            if numeric[i]:
                token = "acid" if (is_leader and i == 0) else "ink"
                cell.font = dt.font("mono", token, "metric_sm", bold=is_leader)
                cell.alignment = Alignment(horizontal="right", vertical="center")
            else:
                cell.font = dt.font("sans", "ink", "body", bold=is_leader)
                cell.alignment = Alignment(horizontal="left", vertical="center", indent=1)
            if fmt_for[i]:
                cell.number_format = fmt_for[i]
        ws.row_dimensions[r].height = 20
        r += 1
    last_row = r - 1

    # ▲ acid / ▼ alert for delta columns; colour is never the only signal (glyph is in the format)
    for i, h in enumerate(headers):
        if formats.get(h) in ("delta", "delta_pct") and last_row >= first_row:
            col = get_column_letter(c0 + i)
            rng = f"{col}{first_row}:{col}{last_row}"
            ws.conditional_formatting.add(rng, CellIsRule(operator="greaterThan", formula=["0"],
                                          font=Font(color=dt.c("acid"))))
            neg = dt.c("alert") if alert_negative else dt.c("ink_muted")
            ws.conditional_formatting.add(rng, CellIsRule(operator="lessThan", formula=["0"],
                                          font=Font(color=neg)))
            ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=["0"],
                                          font=Font(color=dt.c("ink_muted"))))

    total_row = None
    if total and last_row >= first_row:
        total_row = r
        for i, h in enumerate(headers):
            spec = total.get(h)
            col = get_column_letter(c0 + i)
            if spec == "sum":
                v = f"=SUM({col}{first_row}:{col}{last_row})"
            elif spec == "avg":
                v = f"=AVERAGE({col}{first_row}:{col}{last_row})"
            else:
                v = spec
            cell = ws.cell(r, c0 + i, v)
            cell.fill = dt.fill("bg")
            cell.border = Border(top=dt.side("acid", "medium"))
            if numeric[i] or (isinstance(v, str) and v.startswith("=")):
                cell.font = dt.font("mono", "acid", "total", bold=True)
                cell.alignment = Alignment(horizontal="right", vertical="center")
                if fmt_for[i]:
                    cell.number_format = fmt_for[i]
            else:
                cell.font = dt.font("mono", "ink", "total", bold=True)
                cell.alignment = Alignment(horizontal="left", vertical="center", indent=1)
        ws.row_dimensions[r].height = 24
        r += 1

    end_row = r - 1
    if signature:
        r += 1
        sig = ws.cell(r, c0, "derigava_█")
        sig.font = dt.font("mono", "ink_muted", "label")
        end_row = r

    # column widths: from content unless given
    for i, h in enumerate(headers):
        letter = get_column_letter(c0 + i)
        if col_widths and h in col_widths:
            ws.column_dimensions[letter].width = col_widths[h]
            continue
        longest = max([len(str(h))] + [len(str(row[i])) for row in rows if i < len(row) and row[i] is not None])
        ws.column_dimensions[letter].width = min(max(longest + 4, 8), 48)

    if freeze:
        ws.freeze_panes = ws.cell(first_row, c0)
    if autofilter:
        ws.auto_filter.ref = f"{get_column_letter(c0)}{header_row}:{get_column_letter(c0 + ncol - 1)}{last_row}"

    paint_background(ws, dt, end_row, max(c0 + ncol - 1, paint_to_col or 0))
    setup_print(ws, landscape=ncol > 6)
    return {"header_row": header_row, "first_row": first_row, "last_row": last_row, "total_row": total_row}


def setup_print(ws, landscape: bool = False):
    ws.page_setup.orientation = "landscape" if landscape else "portrait"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.print_options.horizontalCentered = False
    ws.page_margins.left = ws.page_margins.right = 0.4


def style_bar_chart(chart, dt: DT | None = None, highlight_first: bool = False):
    """Background plot area, acid bars, muted axes, no legend clutter.
    highlight_first: first point in acid, the rest in ink_muted (one accent per picture).
    In light theme acid is dark green: lime bars vanish on a light page."""
    from openpyxl.chart.marker import DataPoint
    from openpyxl.chart.shapes import GraphicalProperties
    from openpyxl.drawing.line import LineProperties
    from openpyxl.chart.text import RichText
    from openpyxl.drawing.text import CharacterProperties, Paragraph, ParagraphProperties, Font as DFont

    dt = dt or DT.make()
    chart.style = None
    chart.legend = None
    chart.roundedCorners = False  # radius-0: the terminal is rectangular
    chart.graphical_properties = GraphicalProperties(solidFill=dt.c("bg"), ln=LineProperties(noFill=True))
    chart.plot_area.graphicalProperties = GraphicalProperties(solidFill=dt.c("bg"),
                                                              ln=LineProperties(noFill=True))

    def axis_text(color):
        cp = CharacterProperties(latin=DFont(typeface=dt.fonts["mono"]), sz=900, solidFill=color)
        return RichText(p=[Paragraph(pPr=ParagraphProperties(defRPr=cp), endParaRPr=cp)])

    for ax in (chart.x_axis, chart.y_axis):
        ax.txPr = axis_text(dt.c("ink_muted"))
        ax.graphicalProperties = GraphicalProperties(ln=LineProperties(solidFill=dt.c("line")))
        ax.delete = False
    chart.y_axis.majorGridlines.spPr = GraphicalProperties(ln=LineProperties(solidFill=dt.c("line")))

    for s in chart.series:
        base = dt.c("ink_muted") if highlight_first else dt.c("acid")
        s.graphicalProperties = GraphicalProperties(solidFill=base, ln=LineProperties(noFill=True))
        if highlight_first:
            pt = DataPoint(idx=0)
            pt.graphicalProperties = GraphicalProperties(solidFill=dt.c("acid"), ln=LineProperties(noFill=True))
            s.dPt = [pt]
    return chart
