"""Derigava: logos, signatures, avatars, overview, README images and folder READMEs.
Run after build.py (it reuses the same engine, palettes and manifests)."""
from pathlib import Path
from urllib.parse import quote
import importlib.util, json
spec=importlib.util.spec_from_file_location('brand_build',Path(__file__).with_name('build.py'))
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
E=M.E
M.prepare()

# ---------- logos: derigava_█ ----------
LOGOS=M.BASE/'logos';LOGOS.mkdir(exist_ok=True)
for old in LOGOS.iterdir():old.unlink()
INK={'dark':'#ECF2E8','light':'#101310'};ACC={'dark':'#B8FF2C','light':'#3D6E00'};MUTED={'dark':'#9CA697','light':'#566052'}

def save(name,s,transparent=True):
    if transparent:s.items=s.items[1:]
    p=LOGOS/f'{name}.svg';p.write_text(E.Scene.svg(s),encoding='utf-8',newline='\n');M.raster(s,p.with_suffix('.png'),transparent=transparent)

def outline(s,x,y,text,size,color):
    f=E.Font(M.E.FONTS['Onest400'][2]);gs=f.getGlyphSet();upem=f['head'].unitsPerEm;cur=0
    for ch in text:
        gn=f.getBestCmap()[ord(ch)];pen=E.GlyphPen(gs,size/upem,-size/upem,x+cur,y+size*.82)
        gs[gn].draw(pen);s.path(pen.commands,fill=color);cur+=f['hmtx'][gn][0]*size/upem

for theme in ['dark','light']:
    for mode in ['color','mono']:
        acc=ACC[theme] if mode=='color' else INK[theme]
        s=E.Scene('Логотип Derigava',theme=theme,width=1280,height=390,furniture=False);s.logo(110,110,1060,INK[theme],acc)
        save(f'wordmark-{theme}-{mode}',s)
        s=E.Scene('Компактный знак Derigava',theme=theme,width=512,height=512,furniture=False);s.iconmark(0,0,512,INK[theme],acc)
        save(f'mark-{theme}-{mode}',s)
    s=E.Scene('Аватар Derigava',theme=theme,width=1024,height=1024,furniture=False);s.iconmark(0,0,1024,INK[theme],ACC[theme])
    save(f'avatar-{theme}',s,transparent=False)
    for lang,name in [('ru','Derigava'),('en','Derigava')]:
        s=E.Scene(f'Derigava / {name}',theme=theme,width=1280,height=500,furniture=False)
        s.logo(110,100,1060,INK[theme],ACC[theme]);outline(s,114,345,name,48,MUTED[theme])
        save(f'lockup-{lang}-{theme}',s)

# ---------- per direction: signatures, avatar, README, manifest ----------
for d in M.CONFIG:
    folder=d['path']/'signatures';folder.mkdir(exist_ok=True)
    for old in folder.iterdir():old.unlink()
    for light in [False,True]:
        s=M.S('Derigava / '+d['code'],d,light,w=1280,h=420)
        s.items=[];s.logo(100,110,800);s.text(940,178,d['code'],42,'Mono500','acid')
        p=folder/('signature-paper.svg' if light else 'signature-terminal.svg')
        p.write_text(s.svg(p),encoding='utf-8',newline='\n');M.raster(s,p.with_suffix('.png'),transparent=True)
    s=M.S('Аватар / '+d['code'],d,w=1024,h=1024);s.iconmark(0,0,1024)
    p=folder/'avatar.svg';p.write_text(s.svg(p),encoding='utf-8',newline='\n');M.raster(s,p.with_suffix('.png'))
    name=d['name'].replace('\n',' ')
    code=d['code']
    shelf=''.join(f'<a href="templates/{k}.svg"><img src="templates/{k}.png" width="32%" alt="{k}"></a>\n' for k in ['cover','post','quote'])
    readme=f'''<img src="illustrations/key-visual.png" alt="{name}" width="100%">

# {name}

{d['subtitle']}. {d['topics']}.

{d['voice']} {d['principle']}

![Палитра](../previews/palette-{code.lower()}.png)

{shelf}
## В папке

- [templates](templates): макеты в SVG и PNG
- [icons](icons): 24 иконки, цвет задаётся через currentColor
- [graphics](graphics): 3 графических модуля
- [signatures](signatures): подписи и аватар
- [{code} — визуальный гид.pdf]({quote(code+' — визуальный гид.pdf')})

SVG редактируются, если установить шрифты из [00 Основа/assets/fonts](../00%20Основа/assets/fonts).
'''
    if d['key']=='biology':
        readme+='''
## Научные жанры

- `article`: своя статья
- `journal`: пустой научный манускрипт
- `journal-review`: разбор чужой публикации

В карточке факта не больше трёх строк главного текста. Источник набран 29 px, чтобы читался после уменьшения. Пустые версии макетов лежат в [templates/blank](templates/blank).
'''
    if d['key']=='management':
        readme+='''
## Две части

- **Публичная**: посты, статьи и серии об управлении и продажах. Макеты в [templates](templates), пустые версии в [templates/blank](templates/blank).
- **Внутренняя**: объявления в чат, итоги и рейтинги, обучение, таблицы. Это [Командный кит](Командный%20кит).

Палитра у обеих частей одна: терминальный чёрный и кислотный акцент.
'''
    (d['path']/'README.md').write_text(readme,encoding='utf-8',newline='\n')
    (d['path']/'manifest.json').write_text(json.dumps({k:v for k,v in d.items() if k not in ['path','art']},ensure_ascii=False,indent=2,default=str),encoding='utf-8',newline='\n')

# ---------- overview ----------
s=M.S('Derigava / обзор пяти направлений',light=True,w=1800,h=1320)
s.rect(0,0,1800,245,'#0A0B0A');s.logo(56,40,860,c='#ECF2E8',accent='#B8FF2C')
s.text(56,194,M.TAGLINE,29,'Onest400','#9CA697')
for i,d in enumerate(M.CONFIG):
    x=56+i*342;M.paste(s,M.template(d,'cover'),x,300,320,400)
    s.para(x,740,d['name'],320,24,'Literata400' if d['key']=='writing' else 'Onest600',d['deep'],leading=33)
    for j,it in enumerate(d['icons'][:3]):s.vector(d['path']/it['file'],x+j*94,855,62,62,d['deep'])
    s.rect(x,969,320,16,d['accent'])
    s.para(x,1020,d['topics'],316,21,'Onest400','muted',leading=31)
s.label(56,1230,'120 ИКОНОК / 15 МОДУЛЕЙ / 5 ИЛЛЮСТРАЦИЙ / 52 МАКЕТА / КОМАНДНЫЙ КИТ',size=18)
M.raster(s,M.ROOT/'previews/Обзор пяти направлений.png')

# ---------- README images: palettes, type specimen, link preview ----------
PREVIEWS=M.ROOT/'previews'
CELLS=[('ОСНОВА','bg'),('АКЦЕНТ','accent'),('БУМАГА','paper'),('ТЕКСТ НА БУМАГЕ','deep')]
for d in M.CONFIG:
    s=M.S('Палитра / '+d['code'],d,True,w=1280,h=200)
    for i,(label,k) in enumerate(CELLS):
        x=i*320;s.rect(x,0,320,120,d[k],'line' if k=='paper' else None)
        s.label(x+24,136,label,size=12,c='muted');s.text(x+24,158,d[k],20,'Mono500')
    M.raster(s,PREVIEWS/f'palette-{d["code"].lower()}.png')

s=M.S('Палитры',light=True,w=1280,h=760)
for i,(label,k) in enumerate(CELLS):s.label(296+i*240,40,label,size=12,c='muted')
for row,d in enumerate(M.CONFIG):
    y=72+row*136
    s.para(40,y+8,d['name'],260,24,'Literata400' if d['key']=='writing' else 'Onest600',d['deep'],leading=31)
    s.label(40,y+86,d['code'],size=13,c='muted')
    for i,(label,k) in enumerate(CELLS):
        x=296+i*240;s.rect(x,y,224,120,d[k],'line' if k=='paper' else None)
        ink='#ECF2E8' if E.contrast('#ECF2E8',d[k])>E.contrast('#101310',d[k]) else '#101310'
        s.text(x+18,y+86,d[k],18,'Mono500',ink)
M.raster(s,PREVIEWS/'palette.png')

s=M.S('Шрифты',light=True,w=1280,h=660)
for row,(label,sample,font,size) in enumerate([('UNBOUNDED / ЗАГОЛОВКИ','Устройство живой системы','Unbounded600',44),('ONEST / ТЕКСТ','Гораздо полезнее мыслить поколениями.','Onest400',40),('JETBRAINS MONO / ЗНАК, МЕТКИ, ЦИФРЫ','> ИТОГИ / 05.08.2026 / [OK]','Mono500',38),('LITERATA / ПИСАТЕЛЬСТВО','Интонация была своя, родная, годами отшлифованная.','Literata400',38)]):
    y=44+row*150;s.label(56,y,label,size=14,c='muted');s.text(56,y+40,sample,size,font)
M.raster(s,PREVIEWS/'type.png')

s=M.S('Derigava',w=1280,h=640)
for i,d in enumerate(M.CONFIG):s.image(d['art'],i*256,0,256,350)
s.rect(0,350,1280,290,'#0A0B0A');s.logo(56,390,700,c='#ECF2E8',accent='#B8FF2C')
s.text(56,556,M.TAGLINE,26,'Onest400','#9CA697')
M.raster(s,PREVIEWS/'social.png')
print('logos, signatures, overview, README images, folder READMEs: ok')
