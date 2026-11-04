"""Derigava: renders Командный кит from its HTML sources.

Output: previews/{terminal,paper}/NN-*.png and brandbook-{terminal,paper}.pdf.
Run it before build.py: page 7 of the book reuses the terminal previews.
Needs an installed Google Chrome (playwright channel="chrome"), no browser download.
Fails if a brand font does not load, so a preview can't silently fall back to system fonts.
"""
from pathlib import Path
import re
import sys

from playwright.sync_api import sync_playwright
from pypdf import PdfReader, PdfWriter

ROOT = Path(__file__).resolve().parents[2]
KIT = ROOT / '04 Управление и продажи' / 'Командный кит'
SRC = KIT / 'source'
COPYRIGHT = '© 2026 Дмитрий Горлов (Dmitriy Gorlov). Все права защищены.'

ITEMS = [
    ('component', n) for n in ['Label', 'Badge', 'Signature', 'Callout', 'Cta', 'Metric', 'Delta', 'Progress', 'Leaderboard', 'DataTable', 'BarChart', 'Trend', 'Steps', 'Script', 'DoDont', 'Compare']
] + [
    ('format', n) for n in ['FormatPost', 'FormatResults', 'FormatStory', 'FormatCongrats', 'FormatSlideTitle', 'FormatSlideScript', 'FormatCompare']
] + [('cover', 'Cover')]
THEMES = {'terminal': 'dark', 'paper': 'light'}
PRINT_FRAME_HEIGHT = 600
PAGE_BG = {'terminal': '#0a0b0a', 'paper': '#f3f5ef'}

SETTLE_FONTS = """async () => {
  await document.fonts.ready;
  await Promise.all([...document.fonts].map(f => f.load().catch(() => null)));
  await document.fonts.ready;
  return [...document.fonts].filter(f => f.status === 'error').map(f => f.family + ' ' + f.weight);
}"""


def settle(frame, label):
    failed = frame.evaluate(SETTLE_FONTS)
    if failed:
        sys.exit(f'{label}: fonts failed to load: {failed}')


def card_size(html, kind):
    width = re.search(r'width=(\d+)', html.splitlines()[0])
    height = re.search(r'height=(\d+)', html.splitlines()[0])
    w = int(width.group(1)) if width else 960
    # Components take their natural height; formats and the cover are fixed frames.
    h = int(height.group(1)) if kind != 'component' else 200
    return w, h


def render_previews(browser):
    for folder, theme in THEMES.items():
        out = KIT / 'previews' / folder
        out.mkdir(parents=True, exist_ok=True)
        for old in out.glob('*.png'):
            old.unlink()
        for n, (kind, name) in enumerate(ITEMS, 1):
            source = SRC / 'components' / name / 'preview.html'
            w, h = card_size(source.read_text(encoding='utf-8'), kind)
            # Formats sit inside the preview page's padding, so they need a wider viewport.
            viewport = {'width': w + 256, 'height': h + 256} if kind == 'format' else {'width': w, 'height': h}
            page = browser.new_page(viewport=viewport, device_scale_factor=1)
            page.goto(source.as_uri())
            page.add_style_tag(url=(SRC / 'tokens.css').as_uri())
            page.add_style_tag(url=(SRC / 'components' / 'bundle.css').as_uri())
            page.evaluate('t => document.documentElement.setAttribute("data-theme", t)', theme)
            page.wait_for_load_state('networkidle')
            settle(page, name)
            target = out / f'{n:02d}-{kind}-{name}.png'
            if kind == 'format':
                # Formats are saved at their real size, without the preview page's padding.
                page.locator('.dt-frame').first.screenshot(path=str(target))
            else:
                page.screenshot(path=str(target), full_page=True)
            page.close()
        print(f'previews/{folder}: {len(ITEMS)}')


def render_book(browser):
    for folder, theme in THEMES.items():
        # The viewport is an A4 landscape sheet: frames must scale to the page, not to a screen.
        page = browser.new_page(viewport={'width': 1123, 'height': 794})
        page.emulate_media(media='print')
        page.goto((KIT / 'brandbook.html').as_uri() + f'?theme={theme}')
        page.wait_for_load_state('networkidle')
        settle(page, 'brandbook')
        for i, frame in enumerate(page.frames):
            settle(frame, f'brandbook frame {i}')
        # __printMode caps a frame's height, so a tall format fits one sheet instead of splitting.
        page.evaluate(f'window.__printMode = {PRINT_FRAME_HEIGHT}; window.__fitAll()')
        page.wait_for_timeout(800)
        page.evaluate('window.__fitAll()')
        # Page margins take the theme background; otherwise they print white on the dark theme.
        page.add_style_tag(content=f'@page {{ size: A4 landscape; margin: 10mm 0; background: {PAGE_BG[folder]}; }}')
        path = KIT / f'brandbook-{folder}.pdf'
        page.pdf(path=str(path), print_background=True, prefer_css_page_size=True)
        page.close()
        writer = PdfWriter(clone_from=str(path))
        writer.add_metadata({'/Title': f'Derigava Terminal — брендбук ({folder})', '/Author': 'Дмитрий Горлов (Dmitriy Gorlov)', '/Subject': COPYRIGHT})
        writer.write(str(path))
        print(f'brandbook-{folder}.pdf: {len(PdfReader(str(path)).pages)} pages')


with sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome')
    render_previews(browser)
    render_book(browser)
    browser.close()
print('kit: ok')
