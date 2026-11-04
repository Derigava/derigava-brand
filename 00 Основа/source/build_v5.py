from pathlib import Path
import sys, json, html, io, base64, shutil, math, re, importlib.util, os
BASE=Path(__file__).resolve().parents[1]
ROOT=BASE.parent
spec=importlib.util.spec_from_file_location('engine',BASE/'source/engine.py')
E=importlib.util.module_from_spec(spec);spec.loader.exec_module(E)
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg
from fontTools.ttLib import TTFont as Font
from fontTools.varLib.instancer import instantiateVariableFont
import pypdfium2 as pdfium
from PIL import Image
from PIL.PngImagePlugin import PngInfo

COPYRIGHT='© 2026 Дмитрий Горлов (Dmitriy Gorlov). Все права защищены.'
AUTHOR='Дмитрий Горлов (Dmitriy Gorlov)'
TMP=E.TMP
for weight,opsz in [(400,18),(600,48)]:
    p=TMP/f'Literata{weight}.ttf'
    if not p.exists():
        f=instantiateVariableFont(Font(BASE/'assets/fonts/Literata-Variable.ttf'),{'wght':weight,'opsz':opsz},inplace=False)
        for n in f['name'].names:
            if n.nameID==6:n.string=f'Literata-DerigavaW{weight}'.encode(n.getEncoding())
        f.save(p)
    name=f'Literata{weight}';pdfmetrics.registerFont(TTFont(name,str(p)));E.FONTS[name]=('Literata',weight,p)

CONFIG=[
 dict(key='biology',folder='01 Биология',code='BIO',name='Биология',subtitle='Наблюдать живое',accent='#4ADE80',deep='#1A6B3C',bg='#0E1712',paper='#EFF3E9',muted='#A4B3A1',genres=['Пост','Факт','Разбор исследования','Статья','Статья для журнала'],topics='Ботаника · Экосистемы · Эволюция · Эпизоотия',title='Устройство\nживой системы',voice='Точная формулировка, любопытство, границы вывода. Источник не прячется за красивой картинкой.',principle='Научная графика отделена от декоративной. У факта есть источник, у исследования метод и ограничения.',quote='[Проверенный факт]\n\n[Короткое пояснение, которое не расширяет вывод источника.]',quote_source='ШАБЛОН / ЗАМЕНИТЬ ПОЛЯ И ДОБАВИТЬ ИСТОЧНИК'),
 dict(key='writing',folder='02 Писательство',code='TEXT',name='Писательство',subtitle='Исследовать сознание',accent='#CEB7ED',deep='#6E437C',bg='#17131B',paper='#F4EEF5',muted='#BEB0C7',genres=['Проза','Рассказ','Цитата','Фрагмент','Авторская заметка'],topics='Сознание · Коллективный разум · ИИ',title='Без\nпродолжения',voice='Бытовая деталь, внутренний ритм, пауза. История может не давать удобного вывода.',principle='Литературе не нужен обязательный CTA. Ритм абзацев и авторская пунктуация сохраняются.',quote='Интонация была своя, родная, годами отшлифованная.',quote_source='ДМИТРИЙ ГОРЛОВ / «БЕЗ ПРОДОЛЖЕНИЯ» / 23.10.2026'),
 dict(key='technology',folder='03 Техника и AI',code='TECH',name='Техника и AI',subtitle='Разбираться и пробовать',accent='#65D9E8',deep='#086578',bg='#0B151B',paper='#EDF5F7',muted='#A4B7C0',genres=['Linux','Игры','AI и AGI','Агенты','Инструкция'],topics='Linux · Игры · AI · AGI · Агенты',title='О чём агенту\nдумать дальше?',voice='Разговорное объяснение, техническая конкретика, опыт и гипотезы с явными границами.',principle='Команда, среда и версия инструмента видны. Предположение об AGI оформляется как гипотеза.',quote='Непрерывной становится не нейросеть. Непрерывным становится состояние агента.',quote_source='ДМИТРИЙ ГОРЛОВ / АВТОРСКАЯ ГИПОТЕЗА / 26.09.2026'),
 dict(key='management',folder='04 Управление и продажи',code='WORK',name='Управление\nи продажи',subtitle='Согласовывать действия',accent='#B8FF2C',deep='#3D6E00',bg='#0A0B0A',paper='#F3F5EF',muted='#9CA697',genres=['Команда','Разбор','Процесс','Обучение','Итоги'],topics='Команда · Процессы · Обучение · Продажи',title='Разобрать\nпроцесс',voice='Конкретика и уважение. Ирония возможна, публичное унижение людей нет.',principle='Показатели получают период и источник. Разбор направлен на ситуацию и действия, а не на оценку человека.',quote='[Наблюдение о работе]\n\n[Контекст и следующий вопрос для команды.]',quote_source='ШАБЛОН / УПРАВЛЕНЧЕСКИЙ ТЕКСТ НЕ ПРЕДОСТАВЛЕН'),
 dict(key='personal',folder='05 Личное',code='LIFE',name='Личное',subtitle='Замечать и оставаться собой',accent='#F0A38B',deep='#93432C',bg='#1C1412',paper='#F9F0EA',muted='#C0ADA5',genres=['Наблюдение','Дневник','Опыт','Вопрос','Повседневность'],topics='Повседневность · Мировоззрение · Опыт · Самоирония',title='Ого, меня\nне было месяц.',voice='Разговорность, самоирония, честный незавершённый опыт. Не каждую заметку нужно превращать в урок.',principle='Личный текст не обязан доказывать продуктивность. Бытовая история может остаться бытовой историей.',quote='Увы, Дима — не команда разработчиков с шестью свободными годами.',quote_source='ДМИТРИЙ ГОРЛОВ / ЛИЧНЫЙ ПОСТ / 05.08.2026')
]
for d in CONFIG:d['path']=ROOT/d['folder'];d['art']=d['path']/'illustrations/key-visual.png'

def palette(d,light=False):
    return dict(bg=d['paper'] if light else d['bg'],surface='#FFFFFF' if light else '#1D2322',raised='#E3E7DF' if light else '#27302B',line='#B8C1B4' if light else '#485349',ink='#171A17' if light else '#F4F3EB',muted='#575E55' if light else d['muted'],acid=d['deep'] if light else d['accent'],fill=d['accent'],deep=d['deep'],onacid='#101410',alert='#A83E06' if light else '#FFAE79')

class S(E.Scene):
    def __init__(self,title,d=None,light=False,w=1280,h=905,number=0,frame=False):
        self.title=title;self.chapter=(d['code'] if d else 'PERSONAL SYSTEM');self.number=number;self.w=w;self.h=h
        self.c=palette(d,light) if d else dict(E.LIGHT if light else E.DARK)
        self.items=[];self.rect(0,0,w,h,'bg')
        self.d=d
        if frame:
            self.label(56,28,f'DERIGAVA / {self.chapter}',size=12,c='muted')
            self.text(w-56,28,'V5 / FIVE WORLDS',12,'Mono400','muted',align='right')
            self.text(56,h-34,'© 2026 ДМИТРИЙ ГОРЛОВ / DMITRIY GORLOV',11,'Mono400','muted')
            if number:self.text(w-56,h-34,f'{number:02d}',12,'Mono500','muted',align='right')
    def logo(self,x,y,width,c=None,accent=None,compact=False):
        return super().logo(x,y,width,c or 'ink',accent or 'acid',compact)
    def image(self,path,x,y,w,h):self.items.append(dict(kind='image',path=str(path),x=x,y=y,w=w,h=h))
    def vector(self,path,x,y,w,h,c='acid',opacity=1):
        svg=Path(path).read_text(encoding='utf-8').replace('currentColor',self.color(c))
        self.items.append(dict(kind='svg',xml=svg,x=x,y=y,w=w,h=h,opacity=opacity))
    def svg(self,target):
        unitw,unith=('210mm','297mm') if (self.w,self.h)==(794,1123) else (str(self.w),str(self.h))
        out=[f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{unitw}" height="{unith}" viewBox="0 0 {self.w} {self.h}"><title>{html.escape(self.title)}</title><desc>{html.escape(COPYRIGHT)}</desc>']
        out.append('<style>'+font_css(os.path.relpath(BASE/'assets/fonts',Path(target).parent).replace('\\','/')+'/')+'text{font-kerning:none;white-space:pre}</style>')
        items=self.items
        for i in items:
            if i['kind']=='image':
                href=os.path.relpath(i['path'],Path(target).parent).replace('\\','/')
                out.append(f'<image x="{i["x"]}" y="{i["y"]}" width="{i["w"]}" height="{i["h"]}" xlink:href="{html.escape(href)}" preserveAspectRatio="xMidYMid slice"/>')
            elif i['kind']=='svg':
                xml=re.sub(r'<\?xml[^>]+\?>','',i['xml']);xml=xml[xml.index('<svg'):]
                xml=re.sub(r'\swidth="[^"]*"','',xml,count=1);xml=re.sub(r'\sheight="[^"]*"','',xml,count=1)
                xml=xml.replace('<svg ',f'<svg x="{i["x"]}" y="{i["y"]}" width="{i["w"]}" height="{i["h"]}" opacity="{i["opacity"]}" ',1)
                out.append(xml)
            else:
                self.items=[i];frag=E.Scene.svg(self);out.append(frag.split('</style>',1)[1].rsplit('</svg>',1)[0])
        self.items=items;out.append('</svg>');return ''.join(out)

def font_css(prefix):
    faces=[('Onest','Onest-Variable.ttf','100 900'),('Unbounded','Unbounded-Variable.ttf','200 900'),('JetBrains Mono','JetBrainsMono-Regular.ttf','400'),('JetBrains Mono','JetBrainsMono-Medium.ttf','500'),('Literata','Literata-Variable.ttf','200 900')]
    return ''.join(f'@font-face{{font-family:"{fam}";font-weight:{wei};src:url("{prefix}{fn}")}}' for fam,fn,wei in faces)

def pdf(scenes,path,natural=False):
    cv=canvas.Canvas(str(path),pageCompression=1);cv.setTitle(Path(path).stem);cv.setAuthor(AUTHOR);cv.setSubject(COPYRIGHT);cv.setCreator('Derigava v5 build')
    for idx,s in enumerate(scenes):
        scale=.75 if natural else 841.89/1280
        cv.setPageSize((s.w*scale,s.h*scale));cv.saveState();cv.scale(scale,scale)
        cv.bookmarkPage(f'p{idx}');cv.addOutlineEntry(s.title,f'p{idx}',0,False)
        for i in s.items:
            k=i['kind']
            if i.get('fill'):cv.setFillColorRGB(*E.rgb(i['fill']))
            if i.get('stroke'):cv.setStrokeColorRGB(*E.rgb(i['stroke']))
            cv.setLineWidth(i.get('sw',1))
            if k=='rect':cv.roundRect(i['x'],s.h-i['y']-i['h'],i['w'],i['h'],i['rx'],stroke=int(bool(i['stroke'])),fill=int(bool(i['fill'])))
            elif k=='circle':cv.circle(i['x'],s.h-i['y'],i['r'],stroke=int(bool(i['stroke'])),fill=int(bool(i['fill'])))
            elif k=='line':
                cv.setDash([float(v) for v in i['dash'].split()] if i.get('dash') else []);cv.line(i['x1'],s.h-i['y1'],i['x2'],s.h-i['y2']);cv.setDash()
            elif k=='text':cv.setFont(i['font'],i['size']);cv.drawString(i['x'],s.h-i['y']-i['size']*.82,i['text'])
            elif k=='path':
                p=cv.beginPath()
                for cmd in i['commands']:
                    t,*v=cmd
                    if t=='M':p.moveTo(v[0],s.h-v[1])
                    elif t=='L':p.lineTo(v[0],s.h-v[1])
                    elif t=='C':p.curveTo(v[0],s.h-v[1],v[2],s.h-v[3],v[4],s.h-v[5])
                    elif t=='Z':p.close()
                cv.drawPath(p,stroke=int(bool(i['stroke'])),fill=int(bool(i['fill'])))
            elif k=='image':
                im=Image.open(i['path']);iw,ih=im.size;ratio=max(i['w']/iw,i['h']/ih);ww,hh=iw*ratio,ih*ratio
                cv.saveState();p=cv.beginPath();p.rect(i['x'],s.h-i['y']-i['h'],i['w'],i['h']);cv.clipPath(p,stroke=0)
                cv.drawImage(i['path'],i['x']+(i['w']-ww)/2,s.h-i['y']-i['h']+(i['h']-hh)/2,ww,hh,mask='auto');cv.restoreState()
            elif k=='svg':
                draw=svg2rlg(io.BytesIO(i['xml'].encode()));draw.scale(i['w']/draw.width,i['h']/draw.height)
                cv.saveState();cv.setStrokeAlpha(i['opacity']);cv.setFillAlpha(i['opacity']);renderPDF.draw(draw,cv,i['x'],s.h-i['y']-i['h']);cv.restoreState()
        cv.restoreState();cv.showPage()
    cv.save()

def png_info():
    info=PngInfo();info.add_itxt('Author',AUTHOR);info.add_itxt('Copyright',COPYRIGHT);return info

def raster(s,path,transparent=False):
    temp=TMP/(Path(path).stem+'.pdf');pdf([s],temp,natural=True)
    doc=pdfium.PdfDocument(temp);im=doc[0].render(scale=4/3,fill_color=(255,255,255,0) if transparent else (255,255,255,255)).to_pil();im.save(path,dpi=(96,96),pnginfo=png_info());doc.close()

def paste(t,s,x,y,w,h):
    # Reuse vector geometry from the source renderer, keeping raster/vector insert order.
    for i in s.items:
        if i['kind'] in ['image','svg']:
            q=dict(i);q.update(x=x+i['x']*w/s.w,y=y+i['y']*h/s.h,w=i['w']*w/s.w,h=i['h']*h/s.h);t.items.append(q)
        else:
            class Stub:pass
            one=Stub();one.w=s.w;one.h=s.h;one.items=[i]
            transplant(t,one,x,y,w,h)

def transplant(t,s,x,y,w,h):
    sx,sy=w/s.w,h/s.h
    for old in s.items:
        i=dict(old);k=i['kind']
        if k in ['rect','text']:i['x']=x+i['x']*sx;i['y']=y+i['y']*sy
        if k=='rect':i['w']*=sx;i['h']*=sy;i['rx']*=sx;i['sw']*=sx
        elif k=='text':i['size']*=sx;i['width']*=sx
        elif k=='line':
            for key in ['x1','x2']:i[key]=x+i[key]*sx
            for key in ['y1','y2']:i[key]=y+i[key]*sy
            i['sw']*=sx
        elif k=='circle':i['x']=x+i['x']*sx;i['y']=y+i['y']*sy;i['r']*=sx;i['sw']*=sx
        elif k=='path':
            cmds=[]
            for cmd in i['commands']:
                v=list(cmd[1:])
                for j in range(0,len(v),2):v[j]=x+v[j]*sx;v[j+1]=y+v[j+1]*sy
                cmds.append((cmd[0],*v))
            i['commands']=cmds
        t.items.append(i)

def head(s,d,label):
    s.logo(64,54,240);s.label(s.w-64,60,label,c='muted',size=19) if s.w>1500 else s.text(s.w-64,62,label,18,'Mono500','muted',align='right')
def tail(s,d,note=''):
    s.text(64,s.h-71,f'DERIGAVA / {d["code"]}',18,'Mono500','acid')
    if note:s.text(s.w-64,s.h-71,note,16,'Mono400','muted',align='right')

STORY_START='В половине первого Саша поставил греться вчерашний рис и вернулся к компьютеру. До перерыва оставалось отправить таблицу. Потом можно было поесть, забрать посылку и купить хлеб. Хлеб он записал в телефон: вчера тоже собирался купить.'
PERSONAL_START='Я сдался и заархивировал систему на мини-ПК. Это всё ещё чертовски увлекательно, но когда тебе просто хочется послушать музыку, а вместо этого приходится четыре часа драться с аудиокодеками и радиочипом — становится неприятно.'

def template(d,kind,i=0):
    key=d['key'];serif=key=='writing';display='Literata600' if serif else 'Unbounded600'
    w,h=(794,1123) if kind in ['article','journal','journal-review'] else (1920,1080) if kind=='slide' else (1080,1920) if kind=='story' else (1080,1080) if kind=='quote' else (1080,1350)
    light=kind in ['article','journal','journal-review','quote'] or (kind=='carousel' and i in [1,2])
    s=S(f'{d["name"].replace(chr(10)," ")} / {kind}',d,light,w,h)
    if kind=='cover':
        s.image(d['art'],0,0,w,720)
        s.logo(64,56,270,c='#F4F3EB',accent=d['accent']);s.label(64,165,('РАССКАЗ' if serif else 'АГЕНТЫ / ГИПОТЕЗА' if key=='technology' else d['genres'][0].upper()),size=21)
        s.rect(0,720,w,630,'bg');s.label(64,772,d['code']+' / '+d['subtitle'].upper(),size=19)
        s.text(w-64,733,'ХУДОЖЕСТВЕННАЯ ИЛЛЮСТРАЦИЯ',12,'Mono400','muted',align='right')
        s.para(64,843,d['title'],948,83 if serif else 60,display,leading=102 if serif else 80)
        s.para(64,1110,d['topics'],930,30,'Onest400','muted',leading=44)
        tail(s,d,'ДМИТРИЙ ГОРЛОВ');return s
    if kind=='quote':
        s.logo(64,48,230);s.text(64,190,'«',150,'Literata600','acid')
        s.para(64,360,d['quote'],940,46 if serif else 42,'Literata400' if serif else 'Onest500',leading=65 if serif else 60)
        s.para(64,855,d['quote_source'],940,18,'Mono400','muted',leading=27);return s
    if kind=='journal-review':
        s.logo(58,46,180);s.label(58,146,'РАЗБОР ЖУРНАЛЬНОЙ ПУБЛИКАЦИИ / ШАБЛОН',size=11)
        s.para(58,190,'[Название публикации]',678,32,'Onest600',leading=43)
        s.rect(58,309,678,174,'#FFFFFF','line')
        s.para(78,330,'Авторы оригинала: [имена]\nЖурнал: [название], [год]\nDOI / URL: [первоисточник]',638,16,'Onest400',leading=28)
        for j,(title,body) in enumerate([('Вопрос','[Что именно проверяли авторы.]'),('Метод','[Дизайн, объекты, выборка, условия.]'),('Результат','[Основной вывод без расширения смысла.]'),('Ограничения','[Границы интерпретации и открытые вопросы.]')]):
            yy=527+j*106;s.text(58,yy,title,19,'Onest600');s.para(260,yy,body,474,17,'Onest400','muted',leading=25)
        s.line(58,1016,736,1016);s.text(58,1043,'КОММЕНТАРИЙ: ДМИТРИЙ ГОРЛОВ / DERIGAVA',11,'Mono400','muted');return s
    if kind=='article' or kind=='journal':
        s.logo(58,46,180);s.text(736,53,d['code']+' / 01',11,'Mono500','muted',align='right')
        article_label={'biology':'СТАТЬЯ / ШАБЛОН','writing':'ФРАГМЕНТ РАССКАЗА','technology':'АГЕНТЫ / АВТОРСКАЯ ГИПОТЕЗА','management':'РАЗБОР / ШАБЛОН','personal':'ЛИЧНЫЙ ОПЫТ'}[key]
        s.label(58,150,('ЖУРНАЛЬНАЯ СТАТЬЯ / ШАБЛОН' if kind=='journal' else article_label),size=11)
        title={'biology':'[Название исследования]','writing':'Без продолжения','technology':'Непрерывность агента','management':'Разбор рабочей ситуации','personal':'Ого, меня не было месяц.'}[key]
        yy=s.para(58,192,title,678,36,'Literata600' if serif else 'Onest600',leading=47)
        s.text(58,yy+22,'Дмитрий Горлов / Derigava',13,'Onest400','muted')
        body={'biology':'[Контекст и исследовательский вопрос.]\n\n[Что наблюдали и каким методом.]\n\n[Результат и границы его интерпретации.]\n\n[Первичный источник: автор, год, DOI или URL.]','writing':STORY_START+'\n\nВ папке лежали два файла с почти одинаковыми названиями. Саша выбрал верхний, прикрепил к письму, нажал «Отправить». Микроволновка пискнула. Он принёс тарелку к столу, попробовал рис с краю. В середине ещё холодный.','technology':'Поймал себя на мысли, что мы, возможно, немного не там ищем качественный скачок к AGI.\n\nОбычно вопрос ставится примерно так: какая архитектура придёт после трансформеров? Что должно появиться внутри модели, чтобы она наконец стала достаточно «разумной»?\n\nА что, если ничего принципиально нового внутри и не потребуется?','management':'[Ситуация и контекст.]\n\n[Наблюдаемые факты без оценки человека.]\n\n[Какие действия и условия могли повлиять.]\n\n[О чём договорились и когда вернёмся к вопросу.]','personal':PERSONAL_START+'\n\nСправедливости ради, иногда мне хочется драться с аудиокодеками и радиочипом восемь часов. Это никуда не ушло.\n\nНо тут или одно, или другое.'}[key]
        if kind=='journal':
            yy=s.para(58,yy+76,'Аннотация\n[Цель, метод, основные результаты и ограничения. Ключевые слова: заполнить.]',678,15,'Onest400',leading=23)
            for x,txt in [(58,'Введение\n[Проблема и источники.]\n\nМатериалы и методы\n[Дизайн, выборка, процедура.]'),(414,'Результаты\n[Данные и подписи к рисункам.]\n\nОбсуждение\n[Интерпретация и ограничения.]')]:s.para(x,yy+44,txt,320,16,'Onest400',leading=26)
            s.para(58,870,'[Список литературы]\nОформление под требования конкретного журнала. Здесь нет выдуманной публикации или DOI.',678,13,'Onest400','muted',leading=20)
        else:s.para(58,yy+79,body,678,18,'Literata400' if serif else 'Onest400',leading=29,gap=9)
        s.line(58,1034,736,1034);s.text(58,1056,('ФРАГМЕНТ / 23.10.2026' if serif else 'АВТОРСКАЯ ГИПОТЕЗА / 26.09.2026' if key=='technology' else 'ФРАГМЕНТ / 05.08.2026' if key=='personal' else 'ШАБЛОН / ЗАПОЛНИТЬ ПОЛЯ'),10,'Mono400','muted');return s
    if kind=='slide':
        s.image(d['art'],840,0,1080,1080);s.rect(0,0,840,1080,'bg')
        s.logo(96,72,305);s.label(96,220,d['code']+' / '+('АГЕНТЫ' if key=='technology' else d['genres'][0].upper()),size=23)
        s.para(96,345,d['title'],665,74 if serif else 57,display,leading=94 if serif else 78)
        s.para(96,729,d['topics'],650,29,'Onest400','muted',leading=44)
        s.text(96,976,'ДМИТРИЙ ГОРЛОВ',21,'Mono400','muted');return s
    if kind=='story':
        s.image(d['art'],0,260,1080,720);s.logo(72,73,265)
        s.label(72,1030,'АГЕНТЫ / ГИПОТЕЗА' if key=='technology' else d['genres'][0].upper(),size=23)
        s.para(72,1110,d['title'],936,76 if serif else 59,display,leading=95 if serif else 78)
        s.para(72,1465,d['topics'],936,31,'Onest400','muted',leading=45)
        s.text(72,1577,'DERIGAVA / '+d['code'],22,'Mono500','acid');return s
    if kind=='carousel':
        titles={'biology':['Наблюдение','Вопрос','Метод','Ограничения'],'writing':['Фрагмент','Голос','Пауза','Продолжение'],'technology':['Агент по вызову','Память','Состояние','Что дальше?'],'management':['Ситуация','Факты','Договорённость','Возврат к вопросу'],'personal':['Ого.','Что было','Что не вышло','Что осталось']}[key]
        s.label(64,70,d['code']+' / '+('АГЕНТЫ' if key=='technology' else d['genres'][0].upper()),size=21);s.text(1016,70,f'0{i+1} / 04',20,'Mono400','muted',align='right')
        s.para(64,230,titles[i],940,88 if serif else 61,display,leading=105 if serif else 82)
        mods=d['modules'];s.vector(d['path']/mods[i%3]['file'],64,500,952,530,'acid',.8)
        body= '«Что мне стоит подумать следующим?»' if key=='technology' and i==3 else '[Текст фрагмента без изменения авторского ритма.]' if serif else '[Содержание этого кадра. Одна самостоятельная мысль.]'
        s.para(64,1090,body,935,30,'Literata400' if serif else 'Onest400',leading=43);tail(s,d);return s
    # Post: genre-specific typography and information structure.
    head(s,d,'AI / ПРАКТИКА' if key=='technology' else d['genres'][1].upper())
    if key=='writing':
        s.text(64,232,'01',23,'Mono500','acid');s.para(64,306,'В середине\nещё холодный.',945,88,'Literata400',leading=116)
        s.vector(d['path']/d['modules'][2]['file'],64,705,930,320,'acid',.75)
        s.para(64,1130,'Фрагмент рассказа «Без продолжения».\nДмитрий Горлов, 23.10.2026',930,25,'Onest400','muted',leading=38)
    elif key=='technology':
        s.para(64,223,'Гораздо полезнее\nмыслить\nпоколениями.',944,58,display,leading=80)
        yy=565
        for n,(a,b) in enumerate([('01','Первая версия'),('02','Обратная связь'),('03','Новая ветка')]):
            s.rect(64,yy,952,124,'surface');s.label(96,yy+43,a,size=23);s.text(199,yy+36,b,35,'Onest500');yy+=154
        s.para(64,1117,'Из поста о генерации изображений, 11.08.2026. Схема передаёт авторский подход.',932,25,'Onest400','muted',leading=36)
    elif key=='personal':
        s.para(64,225,'Увы, Дима —',940,70,'Onest600',leading=89)
        s.para(64,355,'не команда разработчиков с шестью свободными годами.',940,53,'Onest400',leading=74)
        s.image(d['art'],64,723,952,390)
        s.text(64,1168,'Личный пост / 05.08.2026',25,'Onest400','muted')
    elif key=='biology':
        s.label(64,224,'ФАКТ / [ТЕМА]',size=22);s.text(64,298,'[01]',142,'Mono500','acid')
        s.para(64,508,'[Короткий проверенный факт]',920,53,'Onest500',leading=73)
        s.vector(d['path']/d['modules'][0]['file'],64,733,660,400,'acid',.9)
        s.para(760,802,'Источник\n[Автор, год]\n[DOI / URL]',256,29,'Onest400','muted',leading=43)
    else:
        s.para(64,225,'Разбор\nбез ярлыков',940,66,display,leading=89)
        for j,(a,b) in enumerate([('Контекст','[Что произошло]'),('Факт','[Что наблюдали]'),('Действие','[О чём договорились]')]):
            yy=561+j*167;s.label(64,yy,a.upper(),size=21);s.para(64,yy+48,b,930,39,'Onest500',leading=52);s.line(64,yy+132,1016,yy+132)
        s.label(64,1153,'ШАБЛОН / ЗАМЕНИТЬ ПОЛЯ',size=18,c='muted')
    tail(s,d);return s

def prepare():
    # Icons and modules are stored files; manifest.json is the source of their titles and usage.
    for d in CONFIG:
        p=d['path']
        for folder in ['icons','graphics','illustrations','templates']:(p/folder).mkdir(parents=True,exist_ok=True)
        saved=json.loads((p/'manifest.json').read_text(encoding='utf-8'))
        d['icons']=saved['icons'];d['modules']=saved['modules']

def direction_pages(d,templates):
    out=[]
    s=S(d['name'].replace('\n',' '),d)
    s.image(d['art'],0,0,1280,853);s.rect(0,0,510,905,'bg')
    s.logo(56,52,330);s.label(56,210,d['code']+' / 0'+str(CONFIG.index(d)+1),size=18)
    s.para(56,323,d['name'],430,54 if d['key']=='writing' else 43,'Literata600' if d['key']=='writing' else 'Unbounded600',leading=74 if d['key']=='writing' else 61)
    s.para(56,578,d['subtitle'],405,31,'Onest500',leading=43)
    s.para(56,723,d['topics'],405,20,'Onest400','muted',leading=29)
    s.text(1224,829,'ХУДОЖЕСТВЕННАЯ ИЛЛЮСТРАЦИЯ',10,'Mono400','muted',align='right');s.text(56,866,'© 2026 ДМИТРИЙ ГОРЛОВ / DMITRIY GORLOV',11,'Mono400','muted');out.append(s)
    s=S('Визуальный код / '+d['code'],d,True,frame=True)
    s.text(56,102,'Визуальный код',44,'Unbounded600')
    s.para(56,177,d['voice'],1140,24,'Onest400','muted',leading=34)
    for i,(name,col) in enumerate([('ОСНОВА',d['bg']),('АКЦЕНТ',d['accent']),('БУМАГА',d['paper']),('ТЕКСТ НА БУМАГЕ',d['deep'])]):
        xx=56+i*300;s.rect(xx,301,270,119,col,'line');s.label(xx,442,name,size=12,c='muted');s.text(xx,474,col,20,'Mono500')
    s.vector(d['path']/d['modules'][0]['file'],56,555,570,250,'acid')
    s.para(700,562,d['principle'],490,27,'Literata400' if d['key']=='writing' else 'Onest400',leading=40)
    s.label(700,773,' / '.join(d['genres'][:3]).upper(),size=12,c='muted');out.append(s)
    s=S('24 иконки / '+d['code'],d,frame=True)
    s.text(56,102,'24 иконки',45,'Unbounded600');s.text(56,174,'64 × 64 / контур 2 / currentColor / минимум 32 px',19,'Mono400','muted')
    for i,item in enumerate(d['icons']):
        x=56+(i%6)*200;y=253+(i//6)*145
        s.vector(d['path']/item['file'],x+40,y,64,64,'acid')
        s.para(x,y+86,item['title'],174,16,'Onest400',leading=22)
    out.append(s)
    s=S('Короткие форматы / '+d['code'],d,True,frame=True)
    s.text(56,102,'Короткие форматы',43,'Unbounded600')
    s.para(56,175,'Пост, цитата и вертикальный экран имеют собственную композицию.',1150,22,'Onest400','muted',leading=31)
    paste(s,templates['post'],56,270,330,412.5);paste(s,templates['quote'],430,270,330,330);paste(s,templates['story'],809,270,264,469.3)
    s.label(56,722,'ПОСТ / 1080 × 1350',size=12);s.label(430,640,'ЦИТАТА / 1080 × 1080',size=12);s.label(809,779,'СТОРИС / 1080 × 1920',size=12)
    s.para(56,783,('В образцах использованы авторские фрагменты. Содержание не подгоняется под обязательный вывод.' if d['key'] in ['writing','personal','technology'] else 'Поля в квадратных скобках заполняются реальным содержанием. Научные и рабочие факты не выдумываются.'),680,20,'Onest400','muted',leading=29);out.append(s)
    s=S('Чтение и серии / '+d['code'],d,True,frame=True)
    s.text(56,102,'Чтение и серии',44,'Unbounded600');s.text(56,177,'Длинная форма сохраняет ритм. Серия делит материал по смыслу.',22,'Onest400','muted')
    paste(s,templates['journal-review'] if 'journal-review' in templates else templates['article'],56,258,365,516)
    for i in range(4):paste(s,templates[f'carousel-{i+1}'],496+(i%2)*256,258+(i//2)*276,208,260)
    s.label(56,809,'A4 / '+('РАЗБОР ПУБЛИКАЦИИ' if d['key']=='biology' else 'ДЛИННЫЙ ТЕКСТ'),size=12);s.label(1020,283,'01-04',size=15);s.para(1020,332,'Обложка\nРазвитие\nПауза\nЗавершение',190,21,'Onest400','muted',leading=39);out.append(s)
    s=S('Графические модули / '+d['code'],d,frame=True)
    s.text(56,102,'Графическая материя',42,'Unbounded600');s.para(56,177,'Три редактируемых модуля для обложек, полей, разделителей и серий.',1145,23,'Onest400','muted',leading=33)
    for i,item in enumerate(d['modules']):
        xx=56+i*400;s.rect(xx,304,368,260,'surface');s.vector(d['path']/item['file'],xx+12,314,344,229,'acid')
        s.para(xx,609,item['title'],368,25,'Onest500',leading=35)
    usage_rule={'biology':'Декоративная структура не является микрофотографией или научной диаграммой. Для данных используйте отдельную схему с источником.','writing':'Графика поддерживает паузу и ритм. Она не должна перекрывать текст или навязывать рассказу обязательный вывод.','technology':'Декоративная трассировка не описывает реальную архитектуру. Для инструкции нужны точная схема, среда и условия запуска.','management':'Ритм и согласованные блоки показывают структуру работы. Реальные показатели добавляются с периодом, единицами и источником.','personal':'Графика оставляет место бытовой детали, недосказанности и самоиронии. Личную заметку не нужно превращать в универсальный урок.'}[d['key']]
    s.para(56,742,usage_rule,1130,23,'Onest400','muted',leading=33);out.append(s)
    return out

def foundation():
    out=[]
    s=S('Derigava / пять направлений')
    for i,d in enumerate(CONFIG):s.image(d['art'],i*256,0,256,550)
    s.rect(0,550,1280,355,'bg');s.logo(56,600,790)
    s.text(56,794,'Пять направлений одного автора',30,'Onest400','muted');s.label(1210,803,'V5',size=18);s.text(56,866,'© 2026 ДМИТРИЙ ГОРЛОВ / DMITRIY GORLOV',11,'Mono400','muted');out.append(s)
    s=S('Пять визуальных миров',light=True,frame=True)
    s.text(56,99,'Пять визуальных миров',44,'Unbounded600')
    for i,d in enumerate(CONFIG):
        x=56+i*240;s.rect(x,245,216,383,d['bg']);s.rect(x,245,216,12,d['accent']);s.vector(d['path']/d['icons'][i]['file'],x+67,304,80,80,d['accent'])
        s.para(x+18,439,d['name'],181,24,'Literata400' if d['key']=='writing' else 'Onest500',d['accent'],leading=33)
        s.label(x+18,577,d['code'],size=15,c=d['muted'])
    s.para(56,711,'Общими остаются имя, логотип и характер автора. Направления различаются цветом, изображением, типографикой и композиционной логикой.',1140,26,'Onest400','muted',leading=38);out.append(s)
    s=S('Связность без одинаковости',light=True,frame=True)
    s.text(56,99,'Связность без одинаковости',41,'Unbounded600')
    s.logo(56,270,780,c='#101310',accent='#3D6E00')
    for i,d in enumerate(CONFIG):
        y=460+i*65;s.rect(56,y,36,8,d['accent']);s.text(121,y-9,'derigava_ / '+d['code'],23,'Mono500',d['deep']);s.text(590,y-9,d['genres'][0]+' · '+d['genres'][1]+' · '+d['genres'][2],22,'Onest400','muted')
    s.para(56,803,'Код направления используется в метке. Форма логотипа сохраняется; акцент может принимать цвет направления.',1140,19,'Onest400','muted',leading=27);out.append(s)
    s=S('Знак',light=True,frame=True)
    s.text(56,99,'Знак',44,'Unbounded600')
    s.para(56,170,'derigava_ и блок-курсор. Подчёркивание всегда в цвете текста, курсор — единственный цветной элемент.',1150,22,'Onest400','muted',leading=31)
    s.rect(56,250,760,300,'#0A0B0A');s.logo(110,345,560,c='#ECF2E8',accent='#B8FF2C')
    s.rect(840,250,180,300,'#0A0B0A');s.iconmark(840,310,180,foreground='#ECF2E8',accent='#B8FF2C')
    s.rect(1040,250,184,300,'#FFFFFF','line');s.iconmark(1042,310,180,foreground='#101310',accent='#3D6E00')
    for i,(a,b) in enumerate([('ЦВЕТ','Курсор кислотный на тёмном, тёмно-зелёный #3D6E00 на светлом. В направлении — акцент направления.'),('РАЗМЕР','Не меньше 96 px по ширине на экране и 25 мм в печати. Компактный знак — от 24 px.'),('ПОЛЕ','Вокруг знака свободно минимум на ширину курсора.'),('НЕЛЬЗЯ','Красить подчёркивание, убирать курсор, обводить, добавлять тени и градиенты.')]):
        x=56+(i%2)*600;y=600+(i//2)*110;s.label(x,y,a,size=14);s.para(x,y+30,b,540,20,'Onest400','muted',leading=28)
    out.append(s)
    s=S('Голос взят из реальных постов',light=True,frame=True)
    s.text(56,99,'Голос взят из реальных постов',39,'Unbounded600')
    quotes=[('САМОИРОНИЯ','Увы, Дима — не команда разработчиков с шестью свободными годами.','05.08.2026'),('ОБЪЯСНЕНИЕ','Гораздо полезнее мыслить поколениями.','11.08.2026'),('ГИПОТЕЗА','А что, если ничего принципиально нового внутри и не потребуется?','26.09.2026'),('ПРОЗА','В середине ещё холодный.','«Без продолжения», 23.10.2026')]
    for i,(label,q,src) in enumerate(quotes):
        x=56+(i%2)*600;y=256+(i//2)*255;s.label(x,y,label,size=14);s.para(x,y+48,q,536,27,'Literata400' if i==3 else 'Onest400',leading=39);s.text(x,y+197,src,15,'Mono400','muted')
    out.append(s)
    s=S('Как устроен комплект',light=True,frame=True)
    s.text(56,99,'От библиотеки к публикации',43,'Unbounded600')
    for i,(a,b) in enumerate([('01 / Направление','Выберите папку по содержанию материала, а не по площадке.'),('02 / Жанр','Возьмите пост, цитату, статью, серию или вертикальный формат.'),('03 / Содержание','Сохраните свой ритм. Поля шаблона замените реальными данными.'),('04 / Выпуск','SVG редактируется; PNG показывает готовый вид. Шрифты и иллюстрации в комплекте.')]):
        yy=263+i*131;s.label(56,yy,a,size=21);s.para(550,yy,b,654,25,'Onest400','muted',leading=36)
    s.label(56,821,'120 ИКОНОК / 15 МОДУЛЕЙ / 5 ИЛЛЮСТРАЦИЙ / 52 МАКЕТА',size=14);out.append(s)
    kit=ROOT/'04 Управление и продажи'/'Командный кит'
    s=S('Командный кит',light=True,frame=True)
    s.text(56,99,'Командный кит',44,'Unbounded600')
    s.para(56,170,'Внутренние материалы для команды: объявления в чат, итоги и рейтинги, обучение, таблицы. Та же палитра, что у WORK: терминальный чёрный и кислотный акцент.',1150,22,'Onest400','muted',leading=31)
    for x,y,w,h,f in [(56,270,300,375,'18-format-FormatResults.png'),(376,270,300,300,'17-format-FormatPost.png'),(696,270,211,375,'19-format-FormatStory.png'),(927,270,297,167,'22-format-FormatSlideScript.png')]:
        s.image(kit/'previews'/'terminal'/f,x,y,w,h)
    s.para(927,460,'16 компонентов, 7 форматов, правила голоса и данных, Excel-навык derigava-tables. Темы Terminal и Paper.',297,18,'Onest400','muted',leading=26)
    s.label(56,690,'ПАПКА / 04 УПРАВЛЕНИЕ И ПРОДАЖИ / КОМАНДНЫЙ КИТ',size=14)
    s.para(56,730,'Публичные тексты об управлении и продажах берут макеты WORK. Внутренние — компоненты кита: brandbook.html, source, excel.',1140,20,'Onest400','muted',leading=29);out.append(s)
    return out

def make_html(pages):
    labels={'cover':'Обложка','post':'Пост','quote':'Цитата','story':'Сторис','article':'Длинный текст A4','slide':'Титульный слайд','journal':'Научный манускрипт A4','journal-review':'Разбор журнальной публикации','carousel-1':'Карусель 01','carousel-2':'Карусель 02','carousel-3':'Карусель 03','carousel-4':'Карусель 04'}
    tabs=''.join(f'<a href="#d{i}"><i style="background:{d["accent"]}"></i>{html.escape(d["name"].replace(chr(10)," "))}</a>' for i,d in enumerate(CONFIG))
    parts=[]
    for idx,d in enumerate(CONFIG):
        link=lambda p:html.escape(p.relative_to(ROOT).as_posix(),quote=True)
        cards=''.join(f'<a class="tile" href="{link(p.with_suffix(".svg"))}"><img loading="lazy" src="{link(p)}" alt="{html.escape(labels.get(p.stem,p.stem))}"><span>{html.escape(labels.get(p.stem,p.stem))}</span></a>' for p in sorted((d['path']/'templates').glob('*.png')))
        icons=''.join(f'<figure><a href="{link(d["path"]/it["file"])}" aria-label="Открыть иконку: {html.escape(it["title"])}"><img loading="lazy" src="{link(d["path"]/it["file"])}" alt=""></a><figcaption>{html.escape(it["title"])}</figcaption></figure>' for it in d['icons'])
        parts.append(f'<section id="d{idx}" style="--ac:{d["deep"]}"><div class="section-top"><div><p>{d["code"]}</p><h2>{html.escape(d["name"].replace(chr(10)," "))}</h2><p>{d["topics"]}</p></div><a class="download" href="{link(d["path"]/(d["code"]+" — визуальный гид.pdf"))}">Открыть гид PDF</a></div><img class="hero" src="{link(d["art"])}" alt="Художественная иллюстрация направления"><p class="intro">{d["voice"]}</p><h3>Макеты</h3><div class="templates">{cards}</div><h3>24 иконки SVG</h3><div class="icons">{icons}</div><p class="note">SVG открывается по нажатию на макет. Иконки используют currentColor; цвет меняется в редакторе. Квадратные скобки обозначают поля для заполнения.</p></section>')
    content='''<!doctype html><html lang="ru"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Derigava v5 / Пять направлений</title><style>'''+font_css('00 Основа/assets/fonts/')+'''*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:80px}body{margin:0;background:#f3f5ef;color:#171a17;font-family:Onest,sans-serif}header{background:#0a0b0a;color:#ecf2e8;padding:38px max(5vw,20px)}header strong{font:48px 'JetBrains Mono',monospace}header b{color:#b8ff2c}header p{color:#a4b3a1;font-size:19px}nav{position:sticky;top:0;z-index:2;background:#fff;display:flex;gap:14px;padding:16px max(5vw,20px);overflow:auto;border-bottom:1px solid #ccc}nav a{white-space:nowrap;text-decoration:none;color:#171a17;font-size:14px}nav i{display:inline-block;width:9px;height:9px;margin-right:7px}main{max-width:1380px;margin:auto;padding:30px 24px}section{padding:20px 0 70px;scroll-margin-top:70px}h2{font-family:Unbounded;font-size:38px;margin:10px 0 18px}h3{font-size:26px;margin:45px 0 24px}.section-top{display:flex;align-items:center;justify-content:space-between;gap:24px}.section-top p{color:#575e55}.download{border:1px solid var(--ac);padding:12px 16px;color:var(--ac);text-decoration:none;white-space:nowrap}.hero{width:100%;max-height:560px;object-fit:cover;margin-top:18px}.intro{max-width:850px;font-size:23px;line-height:1.5}.templates{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:22px;align-items:start}.tile{display:block;text-decoration:none;color:#575e55;font-size:12px;overflow:hidden}.tile img{display:block;width:100%;height:320px;object-fit:contain;background:#e3e7df;padding:10px}.tile span{display:block;padding-top:10px}.icons{display:grid;grid-template-columns:repeat(8,minmax(0,1fr));gap:14px}figure{margin:0;padding:20px 7px;background:#fff;text-align:center}figure img{width:48px;height:48px}figcaption{font-size:12px;padding-top:15px;line-height:1.35}.note{color:#575e55;font-size:14px;line-height:1.5}.top-download{color:#b8ff2c;text-decoration:none}footer{max-width:1380px;margin:auto;padding:0 24px 48px;color:#575e55;font-size:14px;line-height:1.5}footer a{color:#171a17}.master{margin-bottom:40px}a:focus-visible{outline:3px solid #80530a;outline-offset:4px}@media(max-width:800px){.templates{grid-template-columns:repeat(2,minmax(0,1fr))}.icons{grid-template-columns:repeat(4,minmax(0,1fr))}h2{font-size:27px}.section-top{display:block}.download{display:inline-block;margin:10px 0}.tile img{height:260px}header strong{font-size:36px}}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}</style><header><strong>derigava_<b>█</b></strong><p>Пять направлений одного автора / Дмитрий Горлов / Dmitriy Gorlov</p><a class="top-download" href="Derigava — визуальная система v5.pdf">Общий брендбук PDF</a> &nbsp;·&nbsp; <a class="top-download" href="04 Управление и продажи/Командный кит/brandbook.html">Командный кит</a></header><nav>'''+tabs+'''</nav><main>'''+''.join(parts)+'''</main><footer>© 2026 Дмитрий Горлов (Dmitriy Gorlov). Все права защищены. Условия: <a href="LICENSE.md">LICENSE.md</a>. Происхождение материалов и участие ИИ: <a href="NOTICE.md">NOTICE.md</a>.</footer></html>'''
    content=content.replace('figcaption{font-size:12px','figcaption{overflow-wrap:anywhere;hyphens:auto;font-size:12px')
    content=content.replace('<title>','<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 64 64%27%3E%3Crect width=%2764%27 height=%2764%27 fill=%27%230a0b0a%27/%3E%3Crect x=%2738%27 y=%2716%27 width=%2714%27 height=%2732%27 fill=%27%23b8ff2c%27/%3E%3Cpath d=%27M12 44h20v4H12z%27 fill=%27%23ecf2e8%27/%3E%3C/svg%3E"><title>',1)
    (ROOT/'Начать здесь.html').write_text(content,encoding='utf-8',newline='\n')

def main():
    prepare();pages=foundation();all_templates=[];book_only='--book-only' in sys.argv
    for d in CONFIG:
        templates={}
        for kind in ['cover','post','quote','story','article','slide']+(['journal','journal-review'] if d['key']=='biology' else []):templates[kind]=template(d,kind)
        for i in range(4):templates[f'carousel-{i+1}']=template(d,'carousel',i)
        for name,scene in templates.items():
            path=d['path']/'templates'/f'{name}.svg'
            if not book_only:path.write_text(scene.svg(path),encoding='utf-8',newline='\n');raster(scene,path.with_suffix('.png'))
            all_templates.append((d['key'],name,scene))
        for item in ([] if book_only else d['icons']):
            scene=S(item['title'],d,w=128,h=128);scene.items=[];scene.vector(d['path']/item['file'],0,0,128,128,'acid')
            # A transparent raster companion keeps the SVG source fully editable.
            temp=TMP/'icon.pdf';pdf([scene],temp,natural=True);doc=pdfium.PdfDocument(temp);im=doc[0].render(scale=4/3,fill_color=(255,255,255,0)).to_pil();im.save((d['path']/item['file']).with_suffix('.png'),pnginfo=png_info());doc.close()
        for item in ([] if book_only else d['modules']):
            scene=S(item['title'],d,w=1200,h=800);scene.vector(d['path']/item['file'],0,0,1200,800,'acid');raster(scene,(d['path']/item['file']).with_suffix('.png'))
        dp=direction_pages(d,templates);pdf(dp,d['path']/(d['code']+' — визуальный гид.pdf'));pages.extend(dp)
    for n,s in enumerate(pages,1):
        s.number=n
        s.text(s.w-56,s.h-34,f'{n:02d} / {len(pages):02d}',12,'Mono500','muted',align='right')
    pdf(pages,ROOT/'Derigava — визуальная система v5.pdf')
    for n,s in enumerate(pages,1):raster(s,ROOT/'previews'/f'{n:02d}.png')
    make_html(pages)
    (BASE/'source/palettes.json').write_text(json.dumps([{k:d[k] for k in ['key','name','accent','deep','bg','paper','voice','principle','topics','genres']} for d in CONFIG],ensure_ascii=False,indent=2),encoding='utf-8',newline='\n')
    qa={k:v for k,v in E.QA.items()}
    (TMP/'layout.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
    (TMP/'scenes.json').write_text(json.dumps([dict(title=s.title,text=[i for i in s.items if i['kind']=='text']) for s in pages],ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'pages':len(pages),'templates':len(all_templates),'icons':sum(len(d['icons']) for d in CONFIG),'modules':15,'layout':{k:len(v) for k,v in qa.items()}},ensure_ascii=False))

if __name__=='__main__':main()
