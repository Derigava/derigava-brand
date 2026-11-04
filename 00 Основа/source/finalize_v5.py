"""Derigava v5: logos, signatures, avatars, overview and documentation.
Run after build_v5.py (it reuses the same engine, palettes and manifests)."""
from pathlib import Path
import importlib.util, json
spec=importlib.util.spec_from_file_location('v5',Path(__file__).with_name('build_v5.py'))
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
    for lang,name in [('ru','Дмитрий Горлов'),('en','Dmitriy Gorlov')]:
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
    readme=f'''# Derigava / {name}

{d['subtitle']}.

Темы: {d['topics']}.

## Визуальная система

Акцент {d['accent']}; тёмная основа {d['bg']}; светлая бумага {d['paper']}; читаемый цвет на светлом {d['deep']}.

{d['voice']}

{d['principle']}

## Комплект

- 24 SVG-иконки и цветные PNG-превью на прозрачном фоне. SVG используют currentColor.
- 3 редактируемых SVG-модуля и PNG.
- Иллюстрация illustrations/key-visual.png.
- Жанровые макеты в templates: SVG и PNG.
- Подписи и аватар направления в signatures.
- Визуальный гид PDF.
- manifest.json с названиями и применением.

## Редактирование

SVG содержат редактируемый текст и относительные ссылки на иллюстрацию и общие шрифты. Сохраняйте структуру папок. Для работы в редакторе установите шрифты из «00 Основа/assets/fonts» и при необходимости переподключите изображение. PNG готовы к использованию как образцы.

Квадратные скобки обозначают поля шаблона. Они не являются готовыми фактами, результатами или публикацией. Цитаты, снабжённые датой, взяты из предоставленных постов без смыслового редактирования.

Иллюстрация сгенерирована ИИ (ChatGPT, gpt-image) по заданию автора. Это художественная метафора, а не научный снимок, фотография автора или документальное свидетельство. Промпты: «00 Основа/source/image-prompts.json».

© 2026 Дмитрий Горлов (Dmitriy Gorlov). Все права защищены. Условия: LICENSE.md и NOTICE.md в корне пакета.
'''
    if d['key']=='biology':
        readme+='''
## Научные жанры

article: собственная статья; journal: научный манускрипт; journal-review: разбор чужой журнальной публикации с авторами оригинала, журналом, годом, DOI, методом, результатами и ограничениями.

В карточке факта оставляйте максимум три строки главного текста. Источник набран 29 px и не должен исчезать после уменьшения.
'''
    if d['key']=='management':
        readme+='''
## Две части WORK

- **Публичное** — посты, статьи и серии об управлении и продажах: макеты в templates.
- **Внутреннее** — материалы для своей команды: объявления в чат, итоги и рейтинги, обучение, таблицы. Папка «Командный кит»: книга brandbook.html, компоненты (source), PNG-образцы (previews), Excel-навык (excel).

Палитра у обеих частей одна: терминальный чёрный и кислотный акцент.
'''
    (d['path']/'README.md').write_text(readme,encoding='utf-8',newline='\n')
    (d['path']/'manifest.json').write_text(json.dumps({k:v for k,v in d.items() if k not in ['path','art']},ensure_ascii=False,indent=2,default=str),encoding='utf-8',newline='\n')

# ---------- overview ----------
s=M.S('Derigava / обзор пяти направлений',light=True,w=1800,h=1320)
s.rect(0,0,1800,245,'#0A0B0A');s.logo(56,40,860,c='#ECF2E8',accent='#B8FF2C')
s.text(1744,80,'V5',24,'Mono500','#9CA697',align='right')
s.text(56,194,'Пять направлений одного автора',29,'Onest400','#9CA697')
for i,d in enumerate(M.CONFIG):
    x=56+i*342;M.paste(s,M.template(d,'cover'),x,300,320,400)
    s.para(x,740,d['name'],320,24,'Literata400' if d['key']=='writing' else 'Onest600',d['deep'],leading=33)
    for j,it in enumerate(d['icons'][:3]):s.vector(d['path']/it['file'],x+j*94,855,62,62,d['deep'])
    s.rect(x,969,320,16,d['accent'])
    s.para(x,1020,d['topics'],316,21,'Onest400','muted',leading=31)
s.label(56,1230,'120 ИКОНОК / 15 МОДУЛЕЙ / 5 ИЛЛЮСТРАЦИЙ / 52 МАКЕТА / КОМАНДНЫЙ КИТ',size=18)
M.raster(s,M.ROOT/'previews/Обзор пяти направлений.png')
print('logos, signatures, overview, READMEs: ok')
