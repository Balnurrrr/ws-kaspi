# -*- coding: utf-8 -*-
"""Фото: 1) официальный сайт Women'Secret, 2) публичные папки Яндекс.Диска, 3) загруженные файлы. Каждое фото проверяется."""
import json, re, os, shutil, io, ssl, urllib.request, urllib.parse
try:
    import certifi; CTX=ssl.create_default_context(cafile=certifi.where())
except Exception: CTX=None
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
KINDS=['FM','D1','D2','D3','TM','D4','D8','D5','FL']
SITE='https://womensecret.com/dw/image/v2/AAYL_PRD/on/demandware.static/-/Sites-gc-ws-master-catalog/default/images/hi-res/'
UA={'User-Agent':'Mozilla/5.0'}
def http(url,timeout=40):
    return urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=timeout,context=CTX).read()
def valid(b):
    try:
        im=Image.open(io.BytesIO(b)); im.verify(); return len(b)>5000
    except Exception: return False
def ydisk_list(public_key,path='/'):
    """все файлы публичной папки (с подпапками): {имя: (public_key, path)}"""
    out={}
    def walk(p):
        off=0
        while True:
            u='https://cloud-api.yandex.net/v1/disk/public/resources?'+urllib.parse.urlencode({'public_key':public_key,'path':p,'limit':200,'offset':off})
            d=json.loads(http(u))
            items=d.get('_embedded',{}).get('items',[])
            for it in items:
                if it['type']=='dir': walk(it['path'])
                elif re.search(r'\.(jpe?g|png|webp)$',it['name'],re.I): out[it['name']]=(public_key,it['path'])
            if len(items)<200: break
            off+=200
    walk(path); return out
def ydisk_get(public_key,path):
    u='https://cloud-api.yandex.net/v1/disk/public/resources/download?'+urllib.parse.urlencode({'public_key':public_key,'path':path})
    return http(json.loads(http(u))['href'],120)
def get_article(a,colours,root,yfiles,uploaded):
    code=('0'+a) if len(a)==6 else a
    d=f'{root}/{a}'; shutil.rmtree(d,ignore_errors=True); os.makedirs(d); got=[]; src=''
    def save(b,ext='jpg'):
        got.append(1); open(f'{d}/{len(got)}.{ext}','wb').write(b)
    for c in sorted(colours):                      # 1) сайт бренда
        for k in KINDS:
            if len(got)>=5: break
            for _ in range(2):
                try:
                    b=http(f'{SITE}P_{code}{c}{k}.jpg')
                    if valid(b): save(b); src='сайт'; break
                except Exception: pass
        if got: break
    if not got:                                    # 2) папки Яндекс.Диска и загруженные файлы
        pat=re.compile(r'(?:[0-9a-f]{8}-)?(?:P_)?%s(?!\d)'%re.escape(code if code in ''.join(yfiles) else a))
        rank=lambda n:(KINDS.index(m.group(1)) if (m:=re.match(r'P_\d{9}(\w+)\.',n)) and m.group(1) in KINDS else 99,n)
        names=sorted([n for n in list(yfiles)+list(uploaded) if re.match(r'(?:[0-9a-f]{8}-)?(?:P_)?(?:%s|%s)'%(code,a),n)],key=rank)
        for n in names[:5]:
            try:
                b=uploaded[n] if n in uploaded else ydisk_get(*yfiles[n])
                if valid(b): save(b,n.rsplit('.',1)[-1].lower()); src='папка'
            except Exception: pass
    return a,len(got),src
def run(cols,root,yfiles,uploaded,progress=None,workers=6):
    os.makedirs(root,exist_ok=True); rep={}
    with ThreadPoolExecutor(workers) as ex:
        for i,(a,n,s) in enumerate(ex.map(lambda kv:get_article(kv[0],kv[1],root,yfiles,uploaded),sorted(cols.items())),1):
            rep[a]={'n':n,'src':s}
            if progress: progress(i,len(cols),a)
    return rep
