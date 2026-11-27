# -*- coding: utf-8 -*-
"""Шаблоны Kaspi (.xlsm): чтение, запись в sheet2.xml без потери макросов/проверок, ZIP с фото ≤ лимита."""
import re, os, shutil, zipfile, glob, io, openpyxl
from xml.sax.saxutils import escape
from PIL import Image
from openpyxl.utils import get_column_letter as L
def template_info(path):
    wb=openpyxl.load_workbook(path,keep_vba=True)
    v=wb['values']; cols={c[0]:set(x for x in c[1:] if x) for c in zip(*v.iter_rows(values_only=True)) if c[0]}
    cat=(cols.get('category') or {''}).copy().pop()
    a=wb['attributes']; heads=[a.cell(3,c).value for c in range(1,a.max_column+1)]
    return {'category':cat,'vals':cols,'ncols':sum(1 for h in heads if h),'heads':heads}
def cell(ref,v):
    if v is None or v=='': return ''
    if isinstance(v,(int,float)): return f'<c r="{ref}" s="8"><v>{v}</v></c>'
    return f'<c r="{ref}" s="8" t="inlineStr"><is><t>{escape(str(v))}</t></is></c>'
def build(template,table,ncols,outdir,name,imgroot,limit=85e6):
    os.makedirs(outdir,exist_ok=True); tmp=outdir+'/_img'; shutil.rmtree(tmp,ignore_errors=True)
    arts=sorted({t['D'] for t in table}); sizes={}
    for dcode in arts:
        a=dcode if os.path.isdir(f'{imgroot}/{dcode}') else dcode.split('-')[0]; d=f'{tmp}/{dcode}'; n=0
        src=sorted(glob.glob(f'{imgroot}/{a}/*'),key=lambda p:int(os.path.basename(p).split('.')[0]))[:5]
        os.makedirs(d,exist_ok=True)
        for f in src:
            try:
                n+=1; dst=f'{d}/{n}.jpeg'
                if f.lower().endswith(('.jpg','.jpeg')):
                    with Image.open(f) as im: w,h=im.size
                    if w<=2000 and h<=3000: shutil.copyfile(f,dst); continue     # уже подходит — без перекодирования (быстро)
                im=Image.open(f); im.draft('RGB',(1600,2400)); im=im.convert('RGB'); im.thumbnail((1600,2400))
                im.save(dst,quality=85)
            except Exception: n-=1
        sizes[dcode]=sum(os.path.getsize(p) for p in glob.glob(d+'/*'))
    parts=[];cur=[];tot=0
    for a in arts:
        if tot+sizes[a]>limit and cur: parts.append(cur);cur=[];tot=0
        cur.append(a);tot+=sizes[a]
    if cur: parts.append(cur)
    res=[]
    for pi,pa in enumerate(parts,1):
        rows=[t for t in table if t['D'] in set(pa)]
        work=f'{outdir}/_t{pi}'; shutil.rmtree(work,ignore_errors=True); os.makedirs(work)
        with zipfile.ZipFile(template) as z: z.extractall(work)
        p=work+'/xl/worksheets/sheet2.xml'; s=open(p,encoding='utf-8').read()
        xml=''.join(f'<row r="{4+i}">'+''.join(cell(f'{L(c)}{4+i}',r.get(L(c))) for c in range(1,ncols+1))+'</row>' for i,r in enumerate(rows))
        dim=re.search(r'<dimension ref="A1:[A-Z]+3"/>',s).group(0)
        s=s.replace('</sheetData>',xml+'</sheetData>').replace(dim,f'<dimension ref="A1:{L(ncols)}{3+len(rows)}"/>')
        open(p,'w',encoding='utf-8').write(s)
        xl=f'{outdir}/{name}-{pi}.xlsm'
        with zipfile.ZipFile(xl,'w',zipfile.ZIP_DEFLATED) as z:
            z.write(work+'/[Content_Types].xml','[Content_Types].xml')
            for dp,_,fs in os.walk(work):
                for f in fs:
                    full=os.path.join(dp,f);rel=os.path.relpath(full,work)
                    if rel!='[Content_Types].xml': z.write(full,rel)
        shutil.rmtree(work)
        suffix='' if len(parts)==1 else f'-часть{pi}'
        zp=f'{outdir}/{name}{suffix}.zip'
        with zipfile.ZipFile(zp,'w',zipfile.ZIP_STORED) as z:
            z.write(xl,f'{name}{suffix}.xlsm')
            for a in pa:
                for f in sorted(glob.glob(f'{tmp}/{a}/*')): z.write(f,f'images/{a}/{os.path.basename(f)}')
        os.remove(xl); res.append({'zip':zp,'articles':len(pa),'rows':len(rows),'mb':round(os.path.getsize(zp)/1e6,1)})
    shutil.rmtree(tmp,ignore_errors=True)
    return res
