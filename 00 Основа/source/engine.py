from __future__ import annotations

import base64
import hashlib
import html
import json
import math
import os
import re
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

from fontTools.ttLib import TTFont as Font
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.basePen import BasePen
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4, landscape

W, H = 1280, 905
COPYRIGHT = '© 2026 Дмитрий Горлов (Dmitriy Gorlov). Все права защищены.'
FONT_DIR = ROOT / 'assets' / 'fonts'
TMP = Path(tempfile.gettempdir()) / 'derigava-build'
TMP.mkdir(parents=True, exist_ok=True)

FONTS = {}
for family, weights in [('Onest', [400, 500, 600, 700]), ('Unbounded', [400, 600, 700, 800])]:
    for weight in weights:
        path = TMP / f'{family}-{weight}.ttf'
        if not path.exists():
            instance = instantiateVariableFont(Font(FONT_DIR / f'{family}-Variable.ttf'), {'wght': weight}, inplace=False)
            instance.save(path)
        # ReportLab keys embedded font subsets by the internal PostScript name.
        # Distinct instance names keep all weights distinct inside the PDF.
        fixed = Font(path)
        ps_name=f'{family}-W{weight}'
        if fixed['name'].getDebugName(6) != ps_name:
            for record in fixed['name'].names:
                if record.nameID == 6: record.string=ps_name.encode(record.getEncoding())
            fixed.save(path)
        key = f'{family}{weight}'
        pdfmetrics.registerFont(TTFont(key, str(path)))
        FONTS[key] = (family, weight, path)
for label, weight in [('Regular', 400), ('Medium', 500), ('Bold', 700)]:
    key = f'Mono{weight}'
    path = FONT_DIR / f'JetBrainsMono-{label}.ttf'
    pdfmetrics.registerFont(TTFont(key, str(path)))
    FONTS[key] = ('JetBrains Mono', weight, path)

DARK = dict(bg='#0A0B0A', surface='#131613', raised='#1C201C', line='#394236', ink='#ECF2E8', muted='#9CA697', acid='#B8FF2C', fill='#B8FF2C', deep='#1E3A00', onacid='#0A0B0A', alert='#FF964F')
LIGHT = dict(bg='#F3F5EF', surface='#FFFFFF', raised='#E9EDE4', line='#C9D2C3', ink='#101310', muted='#566052', acid='#3D6E00', fill='#B8FF2C', deep='#E3F5C2', onacid='#0A0B0A', alert='#A83E06')
PAGES = []
QA = {'out_of_bounds': [], 'missing_glyphs': [], 'overlong_lines': []}

def rgb(value):
    value = value.lstrip('#')
    return tuple(int(value[i:i+2], 16)/255 for i in [0, 2, 4])

def contrast(fg, bg):
    def lum(h):
        c = [(v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4) for v in rgb(h)]
        return .2126*c[0] + .7152*c[1] + .0722*c[2]
    a, b = sorted([lum(fg), lum(bg)], reverse=True)
    return (a+.05)/(b+.05)

def esc(value):
    return html.escape(str(value), quote=True)

class GlyphPen(BasePen):
    def __init__(self, glyphset, sx, sy, ox, oy):
        super().__init__(glyphset)
        self.commands = []
        self.sx, self.sy, self.ox, self.oy = sx, sy, ox, oy
    def point(self, p): return (p[0]*self.sx+self.ox, p[1]*self.sy+self.oy)
    def _moveTo(self,p): self.commands.append(('M', *self.point(p)))
    def _lineTo(self,p): self.commands.append(('L', *self.point(p)))
    def _curveToOne(self,a,b,c): self.commands.append(('C', *self.point(a), *self.point(b), *self.point(c)))
    def _closePath(self): self.commands.append(('Z',))
    def _endPath(self): pass

LOGO_FONT = Font(FONT_DIR / 'JetBrainsMono-Medium.ttf')
LOGO_GLYPHS = LOGO_FONT.getGlyphSet()

class Scene:
    def __init__(self, title, chapter='', number=0, theme='light', paper=False, width=W, height=H, furniture=True):
        self.title, self.chapter, self.number = title, chapter, number
        self.w, self.h = width, height
        self.c = LIGHT if theme == 'light' or paper else DARK
        self.items = []
        self.rect(0, 0, width, height, self.c['bg'])
        if furniture:
            self.text(64, 29, 'DERIGAVA / PERSONAL BRAND SYSTEM', 13, 'Mono500', 'muted')
            self.text(width-64, 29, chapter.upper(), 13, 'Mono500', 'muted', align='right')
            self.line(64, height-61, width-64, height-61, 'line', 1)
            self.text(64, height-43, 'DERIGAVA  ·  V3.0  ·  2026', 12, 'Mono400', 'muted')
            self.text(width-64, height-43, f'{number:02d} / 40', 12, 'Mono400', 'muted', align='right')
    def color(self, c): return self.c.get(c, c)
    def rect(self,x,y,w,h,fill=None,stroke=None,sw=1,rx=0):
        self.items.append(dict(kind='rect',x=x,y=y,w=w,h=h,fill=self.color(fill) if fill else None,stroke=self.color(stroke) if stroke else None,sw=sw,rx=rx))
    def line(self,x1,y1,x2,y2,c='line',sw=1,dash=None):
        self.items.append(dict(kind='line',x1=x1,y1=y1,x2=x2,y2=y2,stroke=self.color(c),sw=sw,dash=dash))
    def circle(self,x,y,r,fill=None,stroke=None,sw=1):
        self.items.append(dict(kind='circle',x=x,y=y,r=r,fill=self.color(fill) if fill else None,stroke=self.color(stroke) if stroke else None,sw=sw))
    def path(self,commands,fill=None,stroke=None,sw=1):
        self.items.append(dict(kind='path',commands=commands,fill=self.color(fill) if fill else None,stroke=self.color(stroke) if stroke else None,sw=sw))
    def text(self,x,y,text,size=24,font='Onest400',c='ink',align='left',limit=None):
        text = str(text)
        width = pdfmetrics.stringWidth(text,font,size)
        xx = x-width if align=='right' else x-width/2 if align=='center' else x
        if limit and width > limit + .5:
            QA['overlong_lines'].append([self.number,text,width,limit])
        if xx < -.5 or xx+width > self.w+.5 or y < -.5 or y+size > self.h+.5:
            QA['out_of_bounds'].append([self.number,text,[xx,y,width,size]])
        cmap = pdfmetrics.getFont(font).face.charToGlyph
        missing = [ch for ch in text if ord(ch) not in cmap and not ch.isspace()]
        if missing: QA['missing_glyphs'].append([self.number,text,''.join(missing)])
        self.items.append(dict(kind='text',x=xx,y=y,text=text,size=size,font=font,fill=self.color(c),width=width))
        return width
    def para(self,x,y,text,width,size=23,font='Onest400',c='ink',leading=None,gap=12):
        leading = leading or size*1.4
        for paragraph in str(text).split('\n'):
            if not paragraph:
                y += gap
                continue
            words = paragraph.split()
            line = ''
            for word in words:
                trial = f'{line} {word}'.strip()
                if line and pdfmetrics.stringWidth(trial,font,size) > width:
                    self.text(x,y,line,size,font,c,limit=width)
                    y += leading
                    line = word
                else: line = trial
            if line:
                self.text(x,y,line,size,font,c,limit=width)
                y += leading
            y += gap
        return y-gap
    def heading(self,title=None,sub=None,size=46):
        y = 93
        y = self.para(64,y,title or self.title,W-128,size,'Unbounded600',leading=size*1.2,gap=0)
        if sub:
            y = self.para(64,y+19,sub,W-128,22,'Onest400','muted',leading=30)
        return y+37
    def label(self,x,y,text,c='acid',size=14): self.text(x,y,text,size,'Mono500',c)
    def logo(self,x,y,width,c=None,accent=None,compact=False):
        c, accent = self.color(c or 'ink'), self.color(accent or ('acid' if self.c is LIGHT else 'fill'))
        # v5 mark: "derigava_" in the ink colour + a block cursor in the accent,
        # set in its own terminal cell (JetBrains Mono advance 600/1000):
        # x 50..550 of the cell, from the ascender of "d" (730) to the bottom of "_" (-110).
        text = 'd_' if compact else 'derigava_'
        size = width/(len(text)*.6 + .55)
        baseline=y+size*.82
        cursor=0
        for ch in text:
            name=LOGO_FONT.getBestCmap()[ord(ch)]
            pen=GlyphPen(LOGO_GLYPHS,size/1000,-size/1000,x+cursor,baseline)
            LOGO_GLYPHS[name].draw(pen)
            self.path(pen.commands,fill=c)
            cursor += LOGO_FONT['hmtx'][name][0]*size/1000
        self.rect(x+cursor+size*.05,baseline-size*.73,size*.5,size*.84,accent)
    def iconmark(self,x,y,size,foreground=None,accent=None):
        # "d_█" centred in a size×size square, 80% of its width.
        w=size*.8;si=w/1.75
        self.logo(x+(size-w)/2,y+size/2-.51*si,w,c=foreground,accent=accent,compact=True)
    def dots(self,x,y,w,h,step=25,c='line',r=1.2):
        for xx in range(int(x),int(x+w)+1,step):
            for yy in range(int(y),int(y+h)+1,step): self.circle(xx,yy,r,c)
    def cursor(self,x,y,w=40,c='fill'): self.rect(x,y,w,max(7,w*.22),c)
    def bracket(self,x,y,w,h,c='acid',sw=3,k=20):
        for a,b in [((x,y+k),(x,y)),((x,y),(x+k,y)),((x+w-k,y),(x+w,y)),((x+w,y),(x+w,y+k)),((x,y+h-k),(x,y+h)),((x,y+h),(x+k,y+h)),((x+w-k,y+h),(x+w,y+h)),((x+w,y+h),(x+w,y+h-k))]:
            self.line(*a,*b,c,sw)
    def arrow(self,x1,y1,x2,y2,c='acid',sw=2):
        self.line(x1,y1,x2,y2,c,sw)
        angle=math.atan2(y2-y1,x2-x1)
        for a in [-.65,.65]: self.line(x2,y2,x2-11*math.cos(angle+a),y2-11*math.sin(angle+a),c,sw)
    def box(self,x,y,w,h,title,body,number=None,fill='surface',size=23):
        self.rect(x,y,w,h,fill)
        yy=y+25
        if number:
            self.label(x+25,yy,number);yy+=34
        yy=self.para(x+25,yy,title,w-50,25,'Onest600',leading=32)
        self.para(x+25,yy+15,body,w-50,size,'Onest400','muted',leading=size*1.38)
    def svg(self,extra_style='',embed_fonts=False):
        s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}" role="img" aria-label="{esc(self.title)}">',f'<title>{esc(self.title)}</title>',f'<desc>{esc(COPYRIGHT)}</desc>']
        s.append('<style>text{font-kerning:none;white-space:pre}'+extra_style+'</style>')
        for i in self.items:
            k=i['kind'];fill=i.get('fill') or 'none';stroke=i.get('stroke') or 'none'
            if k=='rect':s.append(f'<rect x="{i["x"]:.3f}" y="{i["y"]:.3f}" width="{i["w"]:.3f}" height="{i["h"]:.3f}" rx="{i["rx"]}" fill="{fill}" stroke="{stroke}" stroke-width="{i["sw"]}"/>')
            elif k=='circle':s.append(f'<circle cx="{i["x"]:.3f}" cy="{i["y"]:.3f}" r="{i["r"]:.3f}" fill="{fill}" stroke="{stroke}" stroke-width="{i["sw"]}"/>')
            elif k=='line':
                dash=f' stroke-dasharray="{i["dash"]}"' if i.get('dash') else ''
                s.append(f'<line x1="{i["x1"]:.3f}" y1="{i["y1"]:.3f}" x2="{i["x2"]:.3f}" y2="{i["y2"]:.3f}" stroke="{stroke}" stroke-width="{i["sw"]}"{dash}/>')
            elif k=='path':
                d=' '.join(cmd[0]+' '+' '.join(f'{v:.3f}' for v in cmd[1:]) for cmd in i['commands'])
                s.append(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{i["sw"]}"/>')
            elif k=='text':
                family,weight,_=FONTS[i['font']]
                s.append(f'<text x="{i["x"]:.3f}" y="{i["y"]+i["size"]*.82:.3f}" font-family="{family}" font-weight="{weight}" font-size="{i["size"]}" fill="{fill}">{esc(i["text"])}</text>')
        s.append('</svg>')
        return ''.join(s)

