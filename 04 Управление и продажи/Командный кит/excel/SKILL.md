---
name: derigava-tables
description: "Оформление таблиц Excel (.xlsx) в стиле Derigava Terminal: тёмный «терминал» (по умолчанию) или светлая тема Paper для печати, один акцент, моноширинные цифры. Для таблиц, рейтингов, итогов, отчётов и выгрузок «в моём стиле»."
---

# Derigava Terminal — таблицы .xlsx

Источник правды по стилю — дизайн-система Derigava Terminal
(папка `source` рядом с навыком: `source/README.md`, `source/02-data.md` и `source/tokens.json`).
Если там что-то поменялось, сначала обнови `THEMES` в хелпере ниже.

Прочитай также xlsx-скилл (формулы, recalc) — этот навык отвечает только за оформление.

## Подготовка (один раз за сессию)

Скрипты к навыку не прикладываются, поэтому хелпер лежит целиком в конце этого файла
(раздел «Хелпер derigava_xlsx.py»). Запиши его как есть в рабочую папку, например
`<scratchpad>/derigava/derigava_xlsx.py`, и импортируй оттуда. Не переписывай и не
«улучшай» его по памяти.

## Темы

| Тема | `theme=` | Когда |
|---|---|---|
| Terminal | `"dark"` (по умолчанию) | Всё на экран: файлы в чат, выгрузки, отчёты |
| Paper | `"light"` | Печать; проектор в светлой комнате; пользователь попросил светлую |

- Правила одинаковые, меняются только значения токенов.
- В Paper `acid` — тёмно-зелёный `#3D6E00` (текст, линии, столбец лидера): кислотный на светлом не читается.
  Кислотный `#B8FF2C` остаётся только как `acid_fill` — заливка под тёмный текст `on_acid`.
- Если пользователь говорит «распечатать», «на печать», «для принтера» — сразу `theme="light"`, без вопроса.

## Как делать

1. Данные собери в `headers` + `rows` (список списков). Порядок колонок для рейтинга:
   место → имя → результат → % плана → динамика.
2. Вызови `write_table()` из хелпера (openpyxl). Не крась ячейки вручную —
   хелпер уже знает палитру обеих тем, шрифты, рамки, форматы и печать.
3. Сохрани и **проверь рендер** (см. ниже). Не отдавай файл, который не видел глазами.

```python
import sys; sys.path.insert(0, "<scratchpad>/derigava")
from openpyxl import Workbook
from derigava_xlsx import DT, write_table, style_bar_chart, paint_background

wb = Workbook(); ws = wb.active; ws.title = "Рейтинг"
dt = DT.make("brand", theme="dark")  # шрифты: "brand" | "safe" | "auto"; тема: "dark" | "light"
info = write_table(ws,
    headers=["#", "Менеджер", "Оплаты", "% плана", "Δ к прошлой"],
    rows=rows,
    label="> ИТОГИ · НЕДЕЛЯ 42",            # mono-label, верхний регистр, префикс > // [OK] [!]
    title="Рейтинг недели",                 # без точки в конце
    formats={"% плана": "pct", "Δ к прошлой": "delta_pct"},
    leader_row=1,                           # строка лидера: acid-deep, место в acid
    total={"Менеджер": "ИТОГО", "Оплаты": "sum", "% плана": "avg"},
    dt=dt)
wb.save(out_path)
```

Один `dt` на всю книгу: все листы одной книги — в одной теме.

Пример с графиком — раздел «График» ниже.

## Сложные таблицы (многоуровневая шапка, несколько блоков)

`write_table()` умеет только одну строку шапки. Если нужна шапка «блок → группа → метрика»
(например, направления × «мест / ₽/год», или СПО и ВО рядом), собирай лист вручную, но
**только через `DT` (`dt.fill`, `dt.font`, `dt.side`, `dt.c`), `NUMBER_FORMATS`, `paint_background`, `setup_print`** —
никаких своих цветов и шрифтов, и никогда `PALETTE[...]` напрямую: это всегда тёмная тема.
- Шапка на `bg`: все уровни — моно, ВЕРХНИМ РЕГИСТРОМ, `ink_muted`, bold; группы — объединённые
  ячейки с переносом; нижняя строка шапки — `acid` medium снизу. Метка блока (`// СПО · …`) — моно `ink`.
- Данные на `surface`, разделители строк `line`; тонкая `line` слева у первой колонки каждой группы.
- Строка общего итога (РФ, вся команда) — как строка лидера: `acid_deep`, метка в `acid`, цифры bold `ink`.
  Промежуточные итоги (округ, отдел) — `surface_raised`, bold.
- Пустые значения — текст `н/д` моно `ink_muted` мелким размером, вправо. Ноль — это значение, не `н/д`. Прочерк не используем.
- Между блоками — узкая пустая колонка на `bg`. Закрепление: шапка + колонки-метки.
- Внизу — короткое «// КАК ЧИТАТЬ» (`ink_muted`) и подпись `derigava_█`.

## Правила стиля (что хелпер делает и чего не ломать)

- **Фон** `bg` на всей используемой области (Terminal #0A0B0A, Paper #F3F5EF), сетка Excel скрыта.
  Строки данных — `surface`, разделители — `line`. Градиентов, синего и фиолетового нет.
- **Один акцент.** `acid` — только линия под шапкой и над итогом, номер места лидера,
  итоговые цифры, рост `▲`, столбец лидера на графике. Не заливай `acid` целые колонки;
  заливка кислотным — только `acid_fill` с текстом `on_acid`.
- **Цифры** — моноширинный шрифт, выравнивание вправо, форматы из `NUMBER_FORMATS`
  (`int`, `money`, `pct`, `pct1`, `delta`, `delta_pct`, `date` = `DD.MM`, `time` = `HH:MM`).
  Текст — гротеск, влево с отступом. Единицы — в шапке (`₽ ТЫС`, `ШТ`), не в ячейках.
- **Динамика** — глифами `▲` / `▼` / `●` в числовом формате, цвет добавляется условным форматированием.
  Цвет никогда не единственный носитель смысла.
- **`alert` не подсвечивает конкретных людей.** В рейтингах `alert_negative=False`
  (по умолчанию) — падение у человека рисуется `ink-muted`. `alert_negative=True` — только для
  командных рисков: просрочки, срыв плана, долги.
- **Шапка** — метки ВЕРХНИМ РЕГИСТРОМ, моно, `ink-muted`. Заголовок листа — display-шрифт, `ink`.
- Углы прямые (`radius-0`), эмодзи нет, подпись внизу `derigava_█`.
- Одна таблица — одна мысль. Больше ~7 колонок или нужна вторая тема — второй лист.
  Исключение: пользователь прямо попросил всё на одном листе — тогда один лист.

## Шрифты

Excel не умеет цепочку запасных шрифтов: в ячейке одно имя.
- **По умолчанию `"brand"`** — Unbounded / Onest / JetBrains Mono. У пользователя они установлены,
  и Unbounded ему нравится; не подменяй их запасными без его просьбы.
- `"safe"` — всегда запасные (Arial Black / Segoe UI / Consolas): только если пользователь сказал,
  что файл уйдёт людям без этих шрифтов.
- `"auto"` — бренд-шрифт, если установлен на машине, где запускается скрипт, иначе запасной.
  В облачной песочнице (Linux) шрифты Windows не видны, и `auto` всегда даёт запасные — здесь
  его не используй.
В ответе про шрифты ничего не пиши, если стоят бренд-шрифты; если `"safe"` — скажи одной строкой.

## График

`openpyxl.chart.BarChart` + `style_bar_chart(chart, dt, highlight_first=True)`: область цвета `bg`,
оси моно `ink-muted`, лидер в `acid`, остальные `ink-muted`. Горизонтальный бар с
`x_axis.scaling.orientation = "maxMin"` — лидер сверху. После `add_chart` вызови
`paint_background(ws, dt, max_row, max_col)`, чтобы фон был и под графиком. Передавай тот же `dt`,
что и в `write_table`, — иначе график окажется в другой теме.

```python
from openpyxl.chart import BarChart, Reference
chart = BarChart(); chart.type = "bar"; chart.height, chart.width = 7, 12
data = Reference(ws, min_col=3, min_row=info["header_row"], max_row=info["last_row"])
cats = Reference(ws, min_col=2, min_row=info["first_row"], max_row=info["last_row"])
chart.add_data(data, titles_from_data=True); chart.set_categories(cats)
chart.y_axis.scaling.min = 0
chart.x_axis.scaling.orientation = "maxMin"
style_bar_chart(chart, dt, highlight_first=True)
ws.add_chart(chart, "G3")
paint_background(ws, dt, max_row=18, max_col=14)
```

## Проверка

В облачной песочнице Excel нет — рендер через LibreOffice (во временной папке):

```bash
mkdir -p <scratchpad>/chk && cd <scratchpad>/chk
soffice --headless --convert-to pdf /path/file.xlsx
pdftoppm -r 170 -png -f 1 -l 1 file.pdf p    # потом кропы PIL и Read
```

LibreOffice подменяет Segoe UI / Consolas / бренд-шрифты — по рендеру проверяй раскладку,
а не гарнитуру. Если формулы есть — сначала recalc из xlsx-скилла.

На Windows-машине пользователя с Excel (если доступна оболочка на его компьютере) можно
рендерить через Excel COM: `Workbooks.Open` → `CalculateFull()` → `ExportAsFixedFormat(0, pdf)`.

Открой PNG и проверь: нет `####` (узкая колонка), формулы посчитались, фон сплошной, акцент один,
текст не обрезан, лидер подсвечен, весь лист в одной теме. Промежуточные PDF/PNG держи во временной папке и не отдавай,
если не просили.

## Чего не делать

- Не используй pandas `to_excel` со стилями и не крась через `Styler` — только хелпер.
- Не ставь значения жёстко там, где есть формула: итоги — `=SUM()`/`=AVERAGE()` (хелпер так и делает).
  Если данные — снимок из другого файла без исходных листов, значения допустимы; укажи источник
  в примечании под таблицей.
- Не отправляй на печать тёмную тему: она съедает тонер. Для печати — `theme="light"`.
- Не смешивай темы в одной книге и не бери цвета из `PALETTE` напрямую — только через `dt`.

## Хелпер derigava_xlsx.py

Записать в файл дословно:

```python
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
```
