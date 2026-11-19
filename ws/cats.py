# -*- coding: utf-8 -*-
"""Правила заполнения по категориям Kaspi. Ключ = значение ячейки category в листе values шаблона.
Каждая функция: (ctx) -> (table, ncols). ctx.skip(r, причина) фиксирует то, что не удалось."""
import re, collections
from .dicts import CAND, MAT, TYPE, BY_STYLE, MODEL, SZ
BRAND="Women'Secret"
def color_ru(en,allowed):
    for c in CAND.get(en.upper().strip(),[]):
        if c in allowed: return c
def cup15(sz):
    m=re.fullmatch(r'(\d{2,3})([A-D]{1,2})',sz)
    return f"{int(m.group(1))-15}{m.group(2)}" if m else None
def mats(c):
    out=[]
    for m in re.finditer(r'(\d+)\s*%\s*([A-Z][A-Z ]*?)(?=\s*\d+\s*%|$)',c.upper().strip()):
        v=MAT.get(m.group(2).strip())
        if v and v not in out: out.append(v)
    return out
class Ctx:
    def __init__(s,rows,rep,V):
        s.rows=rows; s.rep=rep; s.V=V; s.skips=[]
        s.multi=collections.defaultdict(set)
        for r in rows: s.multi[r['STYLE']].add(r['COLOUR'])
    def photo_ok(s,a): return s.rep.get(a,{}).get('n',0)>0
    def code(s,a,r): return a if len(s.multi[a])==1 else f"{a}-{r['COLOUR']}"
    def sku(s,a,r,size): return a+size if len(s.multi[a])==1 else f"{a}-{r['COLOUR']}-{size}"
    def skip(s,r,why): s.skips.append({'Артикул':r['STYLE'],'Описание':r['DESCRIPTION'].strip(),'Модель':r.get('PRODUCT MODEL',''),'Размер':r['SIZE'],'Цвет':r['COLOR DESCRIP'],'EAN':r['EAN STYLE'],'Причина':why})
def bras(c):
    V=c.V; table=[];seen=set()
    for r in [r for r in c.rows if r['DESCRIPTION'].strip()=='BRA']:
        a=r['STYLE']; size=r['SIZE'].strip().upper()
        if not c.photo_ok(a): c.skip(r,'нет фото'); continue
        t=BY_STYLE.get(a) or TYPE.get(r['PRODUCT MODEL'])
        if not t: c.skip(r,'тип не определён: '+r['PRODUCT MODEL']); continue
        col=color_ru(r['COLOR DESCRIP'],V['Цвет'])
        if not col: c.skip(r,'цвет не определён: '+r['COLOR DESCRIP']); continue
        m=mats(r['COMPOSITION'])
        if not m: c.skip(r,'нет состава'); continue
        k15=cup15(size)
        if k15: mfr=num=k15
        elif size in SZ: mfr=size; num=SZ[size]
        else: c.skip(r,'размер не распознан: '+r['SIZE']); continue
        sku=c.sku(a,r,size)
        if sku in seen: continue
        seen.add(sku)
        nm="Бралетт Women'Secret" if t=='бралетт' else f"Бюстгальтер {t} Women'Secret"
        row={'A':sku,'B':f"{nm}, {col}, {mfr}"+(f" ({num})" if size in SZ else ''),'C':BRAND,'D':c.code(a,r),'I':c.code(a,r),'J':t,'K':', '.join(m),'L':mfr,
             'N':'отсутствует' if t=='бралетт' else 'сзади','W':num,'X':col,'Y':a}
        bad=[(k,row[x]) for x,k in (('J','Тип'),('N','Застежка'),('W','Размер'),('X','Цвет')) if row[x] not in V[k]]+[('Материал',p) for p in m if p not in V['Материал']]
        if bad: c.skip(r,'нет в списке шаблона: '+str(bad)); continue
        table.append(row)
    return table,27
def panties(c):
    V=c.V; table=[];seen=set()
    maxq=max(int(x) for x in V['Количество штук в наборе'])
    for r in [r for r in c.rows if r['DESCRIPTION'].strip() in ('BRIEFS','WOMEN KNITTED PACK 7 BRIEFS','WOMEN KNITTED PACK 3 BRIEFS')]:
        a=r['STYLE']; size=r['SIZE'].strip().upper()
        if not c.photo_ok(a): c.skip(r,'нет фото'); continue
        if r['PRODUCT MODEL'] not in MODEL: c.skip(r,'модель не определена: '+r['PRODUCT MODEL']); continue
        model,rise=MODEL[r['PRODUCT MODEL']]
        qty=1; pm=re.search(r'PACK (\d+)',(r.get('TYPOLOGY','')+' '+r['DESCRIPTION']).upper())
        if pm: qty=int(pm.group(1))
        if qty>maxq: c.skip(r,f'набор из {qty} шт.: в шаблоне набор только до {maxq}'); continue
        col=color_ru(r['COLOR DESCRIP'],V['Цвет'])
        if not col: c.skip(r,'цвет не определён: '+r['COLOR DESCRIP']); continue
        m=mats(r['COMPOSITION'])
        if not m: c.skip(r,'нет состава'); continue
        if size not in SZ: c.skip(r,'размер не распознан: '+r['SIZE']); continue
        sku=c.sku(a,r,size)
        if sku in seen: continue
        seen.add(sku); num=SZ[size]
        name=(f"Набор трусов Women'Secret {qty} шт., {model}, {col}, {size} ({num})" if qty>1 else f"Трусы {model} Women'Secret, {col}, {size} ({num})")
        row={'A':sku,'B':name,'C':BRAND,'D':c.code(a,r),'I':c.code(a,r),'J':model,'L':rise,'M':size,'N':'Да' if qty>1 else 'Нет','O':str(qty),'S':', '.join(m),'W':num,'X':col,'Y':a}
        bad=[(k,row[x]) for x,k in (('J','Модель'),('L','Посадка'),('O','Количество штук в наборе'),('W','Размер'),('X','Цвет')) if row[x] not in V[k]]+[('Состав',p) for p in m if p not in V['Состав']]
        if bad: c.skip(r,'нет в списке шаблона: '+str(bad)); continue
        table.append(row)
    return table,27
HANDLERS={'Master - Women bras':bras,'Master - Women panties':panties}

def parts(r):
    m=r['PRODUCT MODEL'].upper(); sub=r['SUBTYPOLOGY'].upper(); a=r['STYLE']
    if a=='4444833': return 'ночная сорочка',['ночная сорочка']
    if 'NIGHTDRESS' in sub or 'NIGHTDRESS' in m or 'NIGHTDRES' in m: return 'ночная сорочка',['ночная сорочка']
    if m.startswith('SHORT SLEEVES MEDIUM') or m.startswith('LONG SLEEVES SHORT N'): return 'ночная сорочка',['ночная сорочка']
    if a in ('3134129','3134131'): return 'пижама',['свитшот','брюки']      # по фото
    if m.startswith('LONG SLEEVES MASCULI'): return 'пижама',['рубашка','брюки']
    if m.startswith('SHORT SLEEVES MASCUL'): return 'пижама',['рубашка','бриджи'] if 'CAPRI' in sub else ['рубашка','брюки']
    if m.startswith('SHORT SLEEVES LONG P'): return 'пижама',['футболка','брюки']
    if m.startswith('LONG SLEEVES LONG PA'): return 'пижама',['лонгслив','брюки']
    if m.startswith('STRAPS SHORT PANT'): return 'пижама',['майка','шорты']
    if m.startswith('SHORT SLEEVES T SHIR'): return 'пижама',['футболка']
    if m.startswith('LONG SLEEVES T SHIRT'): return 'пижама',['лонгслив']
    if m=='SHORT PANT': return 'пижама',['шорты']
    return None
PJ_DESC={'PYJAMA','WOMEN KNITTED PYJAMA BLOUSE','WOMEN KNITTED PYJAMA','WOMEN KNITTED PYJAMA T-SHIRT','PYJAMA BLOUSE','PYJAMA SHORTS','NIGHTDRESS'}
def nightwear(ctx):
    V=ctx.V
    rows=[r for r in ctx.rows if r['DESCRIPTION'].strip() in PJ_DESC or r['STYLE']=='4444833']
    code_of=ctx.code; sku_of=ctx.sku; photo_ok=ctx.photo_ok
    skip=lambda cat,r,why:ctx.skip(r,why)
    table=[];seen=set()
    for r in rows:
        a=r['STYLE']; size=r['SIZE'].strip().upper()
        if not photo_ok(a): skip('pyj',r,'нет фото'); continue
        if a=='3134170': skip('pyj',r,'детская пижама (размеры 3/4…11/12 лет), нужна детская категория'); continue
        p=parts(r)
        if not p: skip('pyj',r,'комплектация не определена'); continue
        model,items=p
        col=color_ru(r['COLOR DESCRIP'],V['Цвет'])
        if not col: skip('pyj',r,'цвет не определён: '+r['COLOR DESCRIP']); continue
        m=mats(r['COMPOSITION'])
        if not m: skip('pyj',r,'нет состава'); continue
        if size not in SZ: skip('pyj',r,'размер не распознан: '+r['SIZE']); continue
        sku=sku_of(a,r,size)
        if sku in seen: continue
        seen.add(sku); num=SZ[size]
        if model=='ночная сорочка': name=f"Ночная сорочка Women'Secret, {col}, {size} ({num})"
        elif len(items)>1: name=f"Пижама Women'Secret {items[0]} и {items[1]}, {col}, {size} ({num})"
        else: name=f"Пижама Women'Secret {items[0]}, {col}, {size} ({num})"
        row={'A':sku,'B':name,'C':BRAND,'D':code_of(a,r),'I':code_of(a,r),'J':model,'K':size,'O':', '.join(items),'P':', '.join(m),'Y':num,'Z':col,'AA':a}
        bad=[(k,row[x]) for x,k in (('J','Модель'),('Y','Размер'),('Z','Цвет')) if row[x] not in V[k]]+[('Комплектация',i) for i in items if i not in V['Комплектация']]+[('Состав',p) for p in m if p not in V['Состав']]
        if bad: skip('pyj',r,'нет в списке шаблона: '+str(bad)); continue
        table.append(row)
    return table,29
HANDLERS['Master - Women nightwear']=nightwear
