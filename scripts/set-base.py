#!/usr/bin/env python3
"""Прописывает адрес сайта во все SEO-места: canonical, og:url, абсолютные og:image,
JSON-LD (url, BreadcrumbList), sitemap.xml, robots.txt.
Запуск из корня репозитория:  python3 scripts/set-base.py https://pmc.ru
Скрипт можно запускать повторно (идемпотентен) — при смене домена достаточно запустить с новым адресом."""
import sys,re,json,glob,os,html,datetime
ARGS=sys.argv[1:]
TOUCH=[]
if '--touch' in ARGS:
    k=ARGS.index('--touch'); TOUCH=ARGS[k+1:]; ARGS=ARGS[:k]
BASE=(ARGS[0] if ARGS else 'https://site-7-audit.vercel.app').rstrip('/')
DATES=json.load(open('scripts/page-dates.json',encoding='utf-8'))
today=datetime.date.today().isoformat()
pages=sorted(glob.glob('*.html')+glob.glob('services/*.html'))
for f in pages:
    DATES.setdefault(f,{'published':today,'modified':today})
for f in TOUCH: DATES[f]['modified']=today   # --touch стр.html — отметить реальное изменение содержания
json.dump(DATES,open('scripts/page-dates.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
def url_of(f): return BASE+'/' if f=='index.html' else BASE+'/'+f
def title_of(t):
    m=re.search(r'<title>(.*?)</title>',t,re.S); s=html.unescape(m.group(1)) if m else ''
    return s.split(' — ')[0].strip()
CRUMB={'services/index.html':'Услуги'}
SERV_NAMES={}
for f in pages:
    t=open(f,encoding='utf-8').read(); o=t
    u=url_of(f)
    # canonical
    t=re.sub(r'\s*<link rel="canonical"[^>]*>','',t)
    t=t.replace('</title>','</title>\n<link rel="canonical" href="%s">'%u,1)
    # og:url
    t=re.sub(r'\s*<meta property="og:url"[^>]*>','',t)
    t=re.sub(r'(<meta property="og:type"[^>]*>)',r'\1\n<meta property="og:url" content="%s">'%u,t,count=1)
    # og:image / twitter:image absolute
    def img(m):
        v=m.group(2)
        if v.startswith('http'): return m.group(0)
        v=v.lstrip('./'); return '%s"%s/%s"'%(m.group(1),BASE,v)
    t=re.sub(r'(<meta (?:property="og:image"|name="twitter:image") content=)"([^"]*)"',img,t)
    # JSON-LD: пересобрать url и хлебные крошки
    blocks=re.findall(r'<script type="application/ld\+json">(.*?)</script>',t,re.S)
    keep=[]
    for b in blocks:
        j=json.loads(b)
        if j.get('@type') in ('BreadcrumbList','WebPage','WebSite'): continue
        if j.get('@type') in ('Organization','ContactPage','AboutPage','Service','FAQPage'):
            j['url']=u
            if j['@type'] in ('ContactPage','AboutPage','FAQPage'):
                j['inLanguage']='ru'; j['datePublished']=DATES[f]['published']; j['dateModified']=DATES[f]['modified']
            if j['@type']=='Service': j.get('provider',{})['url']=BASE+'/'
            if j['@type']=='ContactPage': j['mainEntity']['url']=BASE+'/'
        keep.append(j)
    if not any(j.get('@type') in ('ContactPage','AboutPage','FAQPage') for j in keep):
        dm=re.search(r'<meta name="description" content="([^"]*)"',t)
        wp={"@context":"https://schema.org","@type":"WebPage","url":u,"name":title_of(t),"inLanguage":"ru",
            "datePublished":DATES[f]['published'],"dateModified":DATES[f]['modified'],
            "isPartOf":{"@type":"WebSite","name":"Precision Metalworks Contract","url":BASE+'/'}}
        if dm: wp["description"]=html.unescape(dm.group(1))
        keep.append(wp)
    if f=='index.html':
        keep.append({"@context":"https://schema.org","@type":"WebSite","name":"Precision Metalworks Contract","url":BASE+'/',"inLanguage":"ru"})
    if f!='index.html':
        items=[{"@type":"ListItem","position":1,"name":"Главная","item":BASE+'/'}]
        if f.startswith('services/') and f!='services/index.html':
            items.append({"@type":"ListItem","position":2,"name":"Услуги","item":BASE+'/services/index.html'})
        items.append({"@type":"ListItem","position":len(items)+1,"name":title_of(t),"item":u})
        keep.append({"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":items})
    t=re.sub(r'\s*<script type="application/ld\+json">.*?</script>','',t,flags=re.S)
    ld=''.join('<script type="application/ld+json">\n'+json.dumps(j,ensure_ascii=False,indent=2)+'\n</script>\n' for j in keep)
    t=t.replace('</head>',ld+'</head>',1)
    if t!=o: open(f,'w',encoding='utf-8').write(t)
# sitemap
def prio(f):
    if f=='index.html': return '1.0'
    if f in ('services/index.html','services/compare.html'): return '0.9'
    if f.startswith('services/'): return '0.8'
    if f in ('equipment.html','gallery.html','materials.html','quality.html','delivery.html','contacts.html'): return '0.7'
    return '0.6'
rows=['  <url><loc>%s</loc><lastmod>%s</lastmod><changefreq>monthly</changefreq><priority>%s</priority></url>'%(url_of(f),DATES[f]['modified'],prio(f)) for f in pages]
open('sitemap.xml','w',encoding='utf-8').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+'\n'.join(rows)+'\n</urlset>\n')
# robots
r=open('robots.txt',encoding='utf-8').read()
r=re.sub(r'Sitemap:.*','Sitemap: %s/sitemap.xml'%BASE,r)
if 'Host:' not in r: pass
open('robots.txt','w',encoding='utf-8').write(r)
print('Готово. Адрес сайта:',BASE,'| страниц:',len(pages))
