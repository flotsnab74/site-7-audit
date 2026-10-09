#!/usr/bin/env python3
"""Разовая SEO-правка структуры (идемпотентна): <main>, подвал без h4, порядок заголовков,
подписи таблиц, alt у миниатюр. Запуск из корня: python3 scripts/seo-pass.py"""
import re,glob
pages=sorted(glob.glob('*.html')+glob.glob('services/*.html'))
H2_FIX={'delivery.html','materials.html','production.html','quality.html','services/index.html'}
ALT={'material-titanium.jpg':{'Титан':'Титановый прокат — пластина'},
     'material-copper.jpg':{'Медь':'Медный прокат — пруток'},
     'material-brass.jpg':{'Латунь':'Латунный прокат — шестигранный пруток'}}
CAP={'equipment.html':'Станки партнёрского завода: количество, диапазон обработки и точность',
     'services/compare.html':'Сравнение технологий обработки: точность, размер партии и оснастка'}
for f in pages:
    t=open(f,encoding='utf-8').read(); o=t
    # 1. <main>
    if '<main' not in t:
        t=t.replace('</header>','</header>\n<main id="main">',1)
        t=t.replace('<footer','</main>\n<footer',1)
    # 2. подвал: h4 -> p.footer-title
    t=re.sub(r'<h4>(Разделы|Компания|Контакты)</h4>',r'<p class="footer-title">\1</p>',t)
    # 3. h3 до первого h2 -> h2
    if f in H2_FIX:
        i=t.find('<h2'); i=i if i>0 else len(t)
        a,b=t[:i],t[i:]
        a=re.sub(r'<h3\b([^>]*)>(.*?)</h3>',r'<h2\1>\2</h2>',a,flags=re.S)
        t=a+b
    t=re.sub(r'(<div class="pick-card">)<h4>(.*?)</h4>',r'\1<h3>\2</h3>',t)
    # 4. alt: миниатюры галереи берут описание из data-alt кнопки
    t=re.sub(r'(<button[^>]*\bdata-alt=")([^"]*)("[^>]*>\s*<img[^>]*?alt=)""',lambda m:m.group(1)+m.group(2)+m.group(3)+'"'+m.group(2)+'"',t)
    t=re.sub(r'<img([^>]*src="[^"]*tech-welding\.jpg"[^>]*)alt=""',r'<img\1alt="Сварка и сборка металлических конструкций"',t)
    t=re.sub(r'<img([^>]*src="https://images\.unsplash\.com/photo-1645754884968[^"]*"[^>]*)alt=""',r'<img\1alt="Гибка листового металла"',t)
    for src,m in ALT.items():
        for old,new in m.items():
            t=re.sub(r'(<img[^>]*src="[^"]*%s"[^>]*alt=)"%s"'%(re.escape(src),re.escape(old)),r'\1"%s"'%new,t)
    # 5. таблицы: caption (скрыт визуально) + scope у th
    if f in CAP and '<caption' not in t:
        t=t.replace('<table class="compare-table">','<table class="compare-table">\n<caption class="sr-only">%s</caption>'%CAP[f],1)
    t=re.sub(r'<th>(?!</th>)',r'<th scope="col">',t)
    if t!=o: open(f,'w',encoding='utf-8').write(t)
# CSS
c=open('styles.css',encoding='utf-8').read()
if '.footer-title' not in c:
    c=c.replace('.footer-grid h4 {','.footer-grid h4, .footer-grid .footer-title {',1)
    # p внутри подвала мог иметь отступы/цвет; задаём явный margin как у h4 ниже при необходимости
if '.sr-only' not in c:
    c+='\n.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0;}\n'
if 'h3→h2 copy' not in c:
    def dup(m):
        pre,sel,post=m.group(1),m.group(2),m.group(3)
        if sel.lstrip().startswith(('@','/*')) or 'h2' in sel or not re.search(r'\bh3\b',sel): return m.group(0)
        parts=[x.strip() for x in sel.split(',')]
        new=[]
        for x in parts:
            new.append(x)
            if re.search(r'\bh3\b',x): new.append(re.sub(r'\bh3\b','h2',x))
        return pre+', '.join(new)+post
    c=re.sub(r'((?:^|\})[ \t]*\n?[ \t]*)([^{}\n][^{}]*?)([ \t]*\{)',dup,c,flags=re.M)
    c+='\n/* h3→h2 copy: стили карточек продублированы для h2 (порядок заголовков) */\n'
open('styles.css','w',encoding='utf-8').write(c)
print('ok')
