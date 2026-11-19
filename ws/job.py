# -*- coding: utf-8 -*-
import os, json, traceback, zipfile, collections
import openpyxl
from openpyxl.styles import Font, PatternFill
from . import pl, photos, kaspi, cats
def run_job(jd, st):
    """jd — папка задания: pl.xlsx, templates/*.xlsm, uploads/*, links.json. st — словарь статуса (для страницы прогресса)."""
    try:
        st.update(stage='Читаю накладную'); rows=pl.load_pl(jd+'/pl.xlsx')
        tpls={}
        for f in sorted(os.listdir(jd+'/templates')):
            i=kaspi.template_info(jd+'/templates/'+f); i['file']=jd+'/templates/'+f; tpls[i['category']]=i
        unknown=[k for k in tpls if k not in cats.HANDLERS]
        st['templates']=[{'file':os.path.basename(i['file']),'category':k,'supported':k in cats.HANDLERS} for k,i in tpls.items()]
        rows=[r for r in rows]
        # фото: нужны только по артикулам, которые пойдут в поддерживаемые категории (простота: по всем)
        cols=collections.defaultdict(set)
        for r in rows: cols[r['STYLE']].add(r['COLOUR'].zfill(2))
        yfiles={}
        for link in json.load(open(jd+'/links.json')):
            st.update(stage='Читаю папку Яндекс.Диска'); 
            try: yfiles.update(photos.ydisk_list(link))
            except Exception as e: st.setdefault('warnings',[]).append(f'Не открылась ссылка {link}: {e}')
        up={}
        if os.path.isdir(jd+'/uploads'):
            for f in os.listdir(jd+'/uploads'): up[f]=open(jd+'/uploads/'+f,'rb').read()
        def prog(i,n,a): st.update(stage=f'Ищу фото: {i} из {n} артикулов',done=i,total=n)
        rep=photos.run(cols,jd+'/img',yfiles,up,prog)
        st['photos']={'with':sum(1 for v in rep.values() if v['n']),'without':sum(1 for v in rep.values() if not v['n'])}
        out=jd+'/out'; os.makedirs(out,exist_ok=True); results=[]; allskips=[]
        for cat,i in tpls.items():
            if cat not in cats.HANDLERS: continue
            st.update(stage=f'Собираю: {cat}')
            ctx=cats.Ctx(rows,rep,i['vals']); table,nc=cats.HANDLERS[cat](ctx)
            table.sort(key=lambda x:(x['D'],x['W'] if 'W' in x else ''))
            name=cat.replace('Master - ','').replace(' ','-')
            res=kaspi.build(i['file'],table,nc,out,name,jd+'/img') if table else []
            results.append({'category':cat,'positions':len(table),'zips':[{**z,'zip':os.path.basename(z['zip'])} for z in res]})
            for s in ctx.skips: s['Категория']=cat
            allskips+=ctx.skips
        # то, что не попало ни в одну категорию (нет шаблона)
        if allskips or unknown:
            wb=openpyxl.Workbook(); ws=wb.active; ws.title='Не сделано'
            hd=['Категория','Артикул','Описание','Модель','Размер','Цвет','EAN','Причина']; ws.append(hd)
            for s in allskips: ws.append([s.get(h,'') for h in hd])
            for c in ws[1]: c.font=Font(bold=True,color='FFFFFF'); c.fill=PatternFill('solid',fgColor='C0392B')
            wb.save(out+'/Не_сделано.xlsx')
        st.update(stage='Готово',finished=True,results=results,skipped=len(allskips),unsupported=unknown)
    except Exception as e:
        st.update(stage='Ошибка',finished=True,error=f'{e}',trace=traceback.format_exc())
