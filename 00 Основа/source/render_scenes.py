"""Derigava: the brand in use. Composes previews/in-use/*.png from the finished layouts.

Run after build.py and finalize.py. Needs an installed Google Chrome, like render_kit.py.
"""
from pathlib import Path
import tempfile

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / '00 Основа'
OUT = ROOT / 'previews' / 'in-use'
BIO, TEXT, TECH, WORK, LIFE = (ROOT / n for n in ['01 Биология', '02 Писательство', '03 Техника и AI', '04 Управление и продажи', '05 Личное'])
KIT = WORK / 'Командный кит' / 'previews' / 'terminal'
W, H = 1600, 900


def src(path):
    return Path(path).as_uri()


FONTS = ''.join(
    f'@font-face{{font-family:"{family}";font-weight:{weight};src:url("{src(BASE / "assets/fonts" / name)}")}}'
    for family, name, weight in [
        ('Onest', 'Onest-Variable.ttf', '100 900'),
        ('Unbounded', 'Unbounded-Variable.ttf', '200 900'),
        ('JetBrains Mono', 'JetBrainsMono-Regular.ttf', '400'),
        ('JetBrains Mono', 'JetBrainsMono-Medium.ttf', '500'),
        ('Literata', 'Literata-Variable.ttf', '200 900'),
    ]
)
BASE_CSS = FONTS + f'''
*{{box-sizing:border-box;margin:0}}
html,body{{width:{W}px;height:{H}px;overflow:hidden;font-family:Onest,sans-serif}}
img{{display:block}}
.mono{{font-family:"JetBrains Mono",monospace}}
'''


def page(css, body):
    return f'<!doctype html><html lang="ru"><meta charset="utf-8"><style>{BASE_CSS}{css}</style><body>{body}</body></html>'


def profile():
    strip = ''.join(f'<img src="{src(d / "illustrations/key-visual.png")}" alt="">' for d in [BIO, TEXT, TECH, WORK, LIFE])
    covers = ''.join(f'<img src="{src(d / "templates/cover.png")}" alt="">' for d in [BIO, TEXT, TECH, WORK, LIFE])
    css = '''
body{background:#F3F5EF;display:flex;align-items:center;justify-content:center}
.card{width:1440px;padding-bottom:40px;background:#0A0B0A;color:#ECF2E8;overflow:hidden}
.banner{display:flex;height:250px}
.banner img{width:20%;height:100%;object-fit:cover}
.head{position:relative;padding:22px 40px 22px 228px;height:128px}
.avatar{position:absolute;left:40px;top:-74px;width:164px;height:164px;border:6px solid #0A0B0A}
h1{font-size:38px;font-weight:600}
.head p{color:#9CA697;font-size:20px;margin-top:8px}
.head .mono{color:#ECF2E8;font-size:18px;position:absolute;right:40px;top:30px}
.head .mono b{color:#B8FF2C;font-weight:500}
.grid{display:grid;grid-template-columns:repeat(5,1fr);gap:16px;padding:14px 40px 0}
.grid img{width:100%;aspect-ratio:1080/1350}
'''
    body = f'''<div class="card"><div class="banner">{strip}</div>
<div class="head"><img class="avatar" src="{src(BASE / "logos/avatar-dark.png")}" alt="">
<h1>Derigava</h1><p>Биология, писательство, техника, управление и личное</p><span class="mono">derigava_<b>█</b></span></div>
<div class="grid">{covers}</div></div>'''
    return page(css, body)


def feed():
    posts = [
        (BIO, 'post', 'Биология', 'Семя финиковой пальмы пролежало около двух тысяч лет и проросло.', 'BIO'),
        (TEXT, 'post', 'Писательство', 'Фрагмент рассказа «Без продолжения».', '23.10.2026'),
        (TECH, 'post', 'Техника и AI', 'Гораздо полезнее мыслить поколениями.', '11.08.2026'),
        (LIFE, 'post', 'Личное', 'Увы, Дима — не команда разработчиков с шестью свободными годами.', '05.08.2026'),
    ]
    cards = ''.join(
        f'''<article><header><img src="{src(d / "signatures/avatar.png")}" alt=""><div><b>{name}</b><span class="mono">{meta}</span></div></header>
<img class="shot" src="{src(d / f"templates/{kind}.png")}" alt=""><p>{text}</p></article>'''
        for d, kind, name, text, meta in posts
    )
    css = '''
body{background:#E3E7DF;display:flex;align-items:center;justify-content:center;gap:20px}
article{width:370px;background:#FFFFFF;color:#171A17}
header{display:flex;align-items:center;gap:12px;padding:14px}
header img{width:46px;height:46px}
header b{display:block;font-size:17px;font-weight:600}
header span{font-size:13px;color:#575E55}
.shot{width:370px;height:462px}
article p{padding:14px;font-size:16px;line-height:1.4;height:84px}
'''
    return page(css, cards)


def slide():
    thumbs = ''.join(f'<img src="{src(p)}" alt="">' for p in [BIO / 'templates/slide.png', KIT / '21-format-FormatSlideTitle.png', LIFE / 'templates/slide.png'])
    css = '''
body{background:#0B151B;color:#ECF2E8;padding:96px 50px 0}
.row{display:flex;gap:24px}
.main{width:1136px;height:639px;border:1px solid #2B3A42}
.side{display:flex;flex-direction:column;gap:18px}
.side img{width:340px;height:191px;border:1px solid #2B3A42}
.foot{display:flex;align-items:center;justify-content:space-between;margin-top:30px}
.foot img{width:230px;margin-left:-20px}
.foot span{color:#A4B7C0;font-size:16px}
'''
    body = f'''<div class="row"><img class="main" src="{src(TECH / "templates/slide.png")}" alt=""><div class="side">{thumbs}</div></div>
<div class="foot"><img src="{src(BASE / "logos/wordmark-dark-color.png")}" alt=""><span class="mono">1920 × 1080</span></div>'''
    return page(css, body)


def team():
    css = '''
body{background:#0A0B0A;color:#ECF2E8;display:flex}
aside{width:300px;border-right:1px solid #394236;padding:36px 28px}
aside img{width:200px;margin:-14px 0 30px -16px}
aside p{font-size:17px;color:#9CA697;padding:10px 0}
aside p.on{color:#B8FF2C}
main{flex:1;padding:36px 48px}
.who{display:flex;align-items:center;gap:14px;margin-bottom:12px}
.who img{width:44px;height:44px}
.who b{font-size:17px;font-weight:600}
.msg{font-size:18px;margin:0 0 20px 58px;color:#ECF2E8}
.shots{display:flex;gap:18px;margin-left:58px;align-items:flex-start}
.shots img{height:650px;border:1px solid #394236}
.shots img.sq{height:520px}
'''
    channels = ''.join(f'<p class="mono{" on" if name == "# итоги" else ""}">{name}</p>' for name in ['# итоги', '# объявления', '# обучение', '# инструкции'])
    body = f'''<aside><img src="{src(BASE / "logos/wordmark-dark-color.png")}" alt="">{channels}</aside>
<main><div class="who"><img src="{src(WORK / "signatures/avatar.png")}" alt=""><b>Derigava</b></div>
<p class="msg">Закрываем неделю.</p>
<div class="shots"><img src="{src(KIT / "18-format-FormatResults.png")}" alt=""><img class="sq" src="{src(KIT / "17-format-FormatPost.png")}" alt=""></div></main>'''
    return page(css, body)


OUT.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory() as tmp, sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome')
    tab = browser.new_page(viewport={'width': W, 'height': H}, device_scale_factor=1)
    for name, build in [('profile', profile), ('feed', feed), ('slide', slide), ('team', team)]:
        html = Path(tmp) / f'{name}.html'
        html.write_text(build(), encoding='utf-8')
        tab.goto(html.as_uri())
        tab.wait_for_load_state('networkidle')
        tab.evaluate('document.fonts.ready')
        tab.screenshot(path=str(OUT / f'{name}.png'))
    browser.close()
print('in-use scenes: ok')
