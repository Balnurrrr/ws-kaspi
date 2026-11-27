# -*- coding: utf-8 -*-
"""Остальные категории Women'Secret. Тип/модель товара, которые нельзя понять из накладной (определялись по фото),
берутся из справочника KNOWN (артикул -> параметры). Нового артикула в справочнике нет -> строка идёт в «Не сделано» с причиной."""
from .cats import *
from .cats import HANDLERS, color_ru, mats, BRAND
from .dicts import SZ, MAT
MAT=dict(MAT); MAT.update({'ACRYLIC':'акрил','WOOL':'шерсть','POLYAMIDE':'полиамид'})
def mats2(c,V,key='Состав'):
    out=[]
    for m in re.finditer(r'(\d+)\s*%\s*([A-Z][A-Z ]*?)(?=\s*\d+\s*%|$)',c.upper().strip()):
        v=MAT.get(m.group(2).strip())
        if v=='модал' and v not in V[key]: v='вискоза'
        if v and v not in out: out.append(v)
    return out
NOSPEC='тип не определён по накладной — нужно посмотреть фото (добавить артикул в справочник)'
def garments(ctx,rows,spec_of,rowfn,checks,mat_key='Состав',sizes=True):
    V=ctx.V; table=[]; seen=set()
    for r in rows:
        a=r['STYLE']; size=r['SIZE'].strip().upper()
        if not ctx.photo_ok(a): ctx.skip(r,'нет фото'); continue
        spec=spec_of(r)
        if spec is None: ctx.skip(r,NOSPEC); continue
        if isinstance(spec,str) and spec.startswith('!'): ctx.skip(r,spec[1:]); continue
        col=color_ru(r['COLOR DESCRIP'],V['Цвет'])
        if not col: ctx.skip(r,'цвет не определён: '+r['COLOR DESCRIP']); continue
        m=mats2(r['COMPOSITION'],V,mat_key)
        if not m: ctx.skip(r,'нет состава'); continue
        if sizes and size not in SZ: ctx.skip(r,'размер не распознан: '+r['SIZE']); continue
        row=rowfn(ctx,a,r,spec,size,col,m)
        if row['A'] in seen: continue
        bad=[]
        for c,k in checks:
            for v in str(row[c]).split(', '):
                if v not in V[k]: bad.append((k,v))
        if bad: ctx.skip(r,'нет в списке шаблона: '+str(bad)); continue
        seen.add(row['A']); table.append(row)
    return table
def base(ctx,a,r,size):
    return {'A':ctx.sku(a,r,size),'C':BRAND,'D':ctx.code(a,r),'I':ctx.code(a,r)}
def of(r,*desc): return r['DESCRIPTION'].strip() in desc
# ---- справочник артикулов (определено по фото в поставках 09.10 и 28.10)
PANTS={s:'повседневные брюки' for s in '3704538 3704539 3704543 3704574 3704575 3704580 3704581 3704582'.split()}|{s:'джоггеры' for s in '3704548 3704549 3704576 3704583 3704585'.split()}
ROBES={'3144623':'хлопковый халат','3144638':'хлопковый халат','4414342':'велюровый халат'}
BL={'3274541','3274542','3274544','3274545','3274546','3274584','3274587','3274588','3274589','3274598','3274600','3274601'}
def pants(ctx):
    def rowfn(ctx,a,r,mod,size,col,m):
        d=base(ctx,a,r,size); d.update({'B':f"{mod.capitalize()} Women'Secret, {col}, {size} ({SZ[size]})",'J':mod,'M':size,'N':'средняя','P':', '.join(m),'AC':SZ[size],'AD':col,'AE':a}); return d
    t=garments(ctx,[r for r in ctx.rows if of(r,'PANTS')],lambda r:PANTS.get(r['STYLE']),rowfn,[('J','Модель'),('N','Посадка'),('P','Состав'),('AC','Размер'),('AD','Цвет')])
    return t,33
def robes(ctx):
    def spec(r):
        if 'SWEATER' in r.get('SUBTYPOLOGY','').upper() or 'ZIP' in r.get('PRODUCT MODEL','').upper(): return '!не халат (кофта на молнии) — другая категория'
        return ROBES.get(r['STYLE'])
    def rowfn(ctx,a,r,mod,size,col,m):
        d=base(ctx,a,r,size); d.update({'B':f"{mod.capitalize()} Women'Secret, {col}, {size} ({SZ[size]})",'J':mod,'K':size,'P':', '.join(m),'Y':SZ[size],'Z':col,'AA':a}); return d
    return garments(ctx,[r for r in ctx.rows if of(r,'ROBE')],spec,rowfn,[('J','Модель'),('P','Состав'),('Y','Размер'),('Z','Цвет')]),29
def blouses(ctx):
    def spec(r):
        if r['STYLE'] in BL: return 'блузка'
        return '!не блузка / категория не определена: '+r['DESCRIPTION'].strip()
    def rowfn(ctx,a,r,mod,size,col,m):
        d=base(ctx,a,r,size); d.update({'B':f"Блузка Women'Secret, {col}, {size} ({SZ[size]})",'J':mod,'N':size,'R':', '.join(m),'AB':SZ[size],'AC':col,'AD':a}); return d
    rows=[r for r in ctx.rows if r['STYLE'] in BL or of(r,'BLOUSE','WOMEN KNITTED BLOUSE')]
    return garments(ctx,rows,spec,rowfn,[('J','Модель'),('R','Состав'),('AB','Размер'),('AC','Цвет')]),32
BODY={'5054903':('боди-топ','U-вырез'),'5691576':('боди-топ','v-вырез')}
def bodysuits(ctx):
    def rowfn(ctx,a,r,spec,size,col,m):
        d=base(ctx,a,r,size); d.update({'B':f"Боди Women'Secret, {col}, {size} ({SZ[size]})",'J':spec[0],'N':size,'O':spec[1],'T':', '.join(m),'AC':SZ[size],'AD':col,'AE':a}); return d
    return garments(ctx,[r for r in ctx.rows if of(r,'BODY')],lambda r:BODY.get(r['STYLE']),rowfn,[('J','Модель'),('O','Воротник/вырез'),('T','Состав'),('AC','Размер'),('AD','Цвет')]),33
def socks(ctx):
    def rowfn(ctx,a,r,spec,size,col,m):
        return {'A':a+'U','B':f"Носки Women'Secret, {col}, универсальный размер",'C':BRAND,'D':a,'I':a,'J':'носки','K':'Нет','L':'U','N':', '.join(m),'T':'1 пара','W':'универсальный','X':col,'Y':a}
    return garments(ctx,[r for r in ctx.rows if of(r,'SOCKS')],lambda r:1,rowfn,[('J','Модель'),('N','Состав'),('T','Количество пар'),('W','Размер'),('X','Цвет')],sizes=False),27
TANK={'5104064':('кроп-топ','американская пройма','укороченная'),'5104065':('кроп-топ','американская пройма','укороченная'),'4024423':('майка','U-вырез','стандартная'),'4024425':('майка','U-вырез','стандартная')}
def tanks(ctx):
    def rowfn(ctx,a,r,s,size,col,m):
        d=base(ctx,a,r,size); d.update({'B':f"{s[0].capitalize()} Women'Secret, {col}, {size} ({SZ[size]})",'J':s[0],'L':s[1],'O':size,'P':s[2],'Q':', '.join(m),'AA':SZ[size],'AB':col,'AC':a}); return d
    rows=[r for r in ctx.rows if r['STYLE'] in TANK]
    return garments(ctx,rows,lambda r:TANK.get(r['STYLE']),rowfn,[('J','Модель'),('L','Вырез'),('P','Длина'),('Q','Состав'),('AA','Размер'),('AB','Цвет')]),31
JACK={'3144635':('демисезонная куртка','до бедра'),'4414341':('демисезонная куртка','до бедра'),'4684192':('демисезонная куртка','до бедра'),'1694031':('демисезонная куртка','до талии')}
def jackets(ctx):
    def rowfn(ctx,a,r,s,size,col,m):
        d=base(ctx,a,r,size); d.update({'B':f"{s[0].capitalize()} Women'Secret, {col}, {size} ({SZ[size]})",'J':s[0],'M':size,'N':s[1],'R':'демисезон','S':', '.join(m),'U':'отсутствует','AG':SZ[size],'AH':col,'AI':a}); return d
    rows=[r for r in ctx.rows if r['STYLE'] in JACK]
    return garments(ctx,rows,lambda r:JACK.get(r['STYLE']),rowfn,[('J','Модель'),('N','Длина изделия'),('R','Сезон'),('S','Состав'),('U','Утеплитель'),('AG','Размер'),('AH','Цвет')]),37
def cardigans(ctx):
    def rowfn(ctx,a,r,s,size,col,m):
        num={'S/M':'44, 46','L/XL':'48, 50'}.get(size)
        return {'A':a+size.replace('/',''),'B':f"Кардиган Women'Secret, {col}, {size} ({(num or '').replace(', ','–')})",'C':BRAND,'D':ctx.code(a,r),'I':ctx.code(a,r),'J':'кардиган','N':size,'S':', '.join(m),'AB':num or '','AC':col,'AD':a}
    return garments(ctx,[r for r in ctx.rows if r['STYLE']=='3144631'],lambda r:1,rowfn,[('J','Модель'),('S','Состав'),('AB','Размер'),('AC','Цвет')],sizes=False),32
def hoodies(ctx):
    def rowfn(ctx,a,r,s,size,col,m):
        d=base(ctx,a,r,size); d.update({'B':f"Свитшот Women'Secret с принтом, {col}, {size} ({SZ[size]})",'J':'свитшот','N':size,'S':', '.join(m),'U':'демисезон','AC':SZ[size],'AD':col,'AE':a}); return d
    return garments(ctx,[r for r in ctx.rows if r['STYLE']=='3274586'],lambda r:1,rowfn,[('J','Модель'),('S','Состав'),('U','Сезон'),('AC','Размер'),('AD','Цвет')]),33
def tshirts(ctx):
    def rowfn(ctx,a,r,s,size,col,m):
        d=base(ctx,a,r,size); d.update({'B':f"Лонгслив-поло Women'Secret в полоску, {col}, {size} ({SZ[size]})",'K':'лонгслив','M':'поло','O':size,'S':', '.join(m),'AD':SZ[size],'AE':col,'AF':a}); return d
    return garments(ctx,[r for r in ctx.rows if r['STYLE']=='3274539'],lambda r:1,rowfn,[('K','Модель'),('M','Воротник/вырез'),('S','Состав'),('AD','Размер'),('AE','Цвет')]),34
COS={'4844721':('мультиколор','полоска','полиэстер','молния',(18,27,12)),'4844742':('розовый','однотонный','полиамид','молния',(32,15,None)),
 '4844743':('зеленый','однотонный','полиамид','молния',(27,11,None)),'4844744':('бежевый','однотонный','полиамид','молния',(19,9,None)),
 '4844775':('бежевый','однотонный','полиуретан','молния',(22,8,None)),'4844777':('белый','клетка','полиэстер','молния',(17,22,10)),
 '4844778':('коричневый','животный','полиэстер','молния',(15,23,14)),'4844785':('бордовый','рисунок','полиэстер','молния',(21,32,10))}
def cosmetic(ctx):
    V=ctx.V; table=[]; done=set()
    for r in ctx.rows:
        a=r['STYLE']
        if not r['DESCRIPTION'].upper().find('VANITY')>=0 or a in done: continue
        done.add(a)
        if not ctx.photo_ok(a): ctx.skip(r,'нет фото'); continue
        if a not in COS: ctx.skip(r,'размеры, узор и материал косметички берутся по фото/сайту — артикул нужно добавить в справочник'); continue
        col,pat,mat,clasp,(x,y,z)=COS[a]; w,h=max(x,y),min(x,y)
        row={'A':a+'U','B':f"Косметичка Women'Secret, {col}",'C':BRAND,'D':a,'I':a,'J':'косметичка','K':'для женщин','L':clasp,'N':h,'O':w,'Q':pat,'T':a,'U':mat,'V':col,'W':'Китай'}
        if z: row['P']=z
        bad=[(k,row[c]) for c,k in (('J','Тип'),('K','Пол'),('L','Застежка'),('Q','Узор'),('U','Материал'),('V','Цвет'),('W','Страна производитель')) if row[c] not in V[k]]
        if bad: ctx.skip(r,'нет в списке шаблона: '+str(bad)); continue
        table.append(row)
    return table,23
HB={'3064310':('сумка тоут','полиэстер','молния','коричневый',14,39,37,"Сумка Women'Secret, коричневый"),'1374472':('клатч','силикон','молния','голубой',10,17,10,"Клатч Women'Secret силиконовый Miffy, голубой")}
def handbags(ctx):
    V=ctx.V; table=[]; done=set()
    for r in ctx.rows:
        a=r['STYLE']
        if not of(r,'BAG','PURSE') or a in done: continue
        done.add(a)
        if not ctx.photo_ok(a): ctx.skip(r,'нет фото'); continue
        if a not in HB: ctx.skip(r,'тип, материал и размеры сумки — по фото; артикул нужно добавить в справочник'); continue
        typ,mat,clasp,col,dd,ww,hh,nm=HB[a]
        row={'A':a+'U','B':nm,'C':BRAND,'D':a,'I':a,'J':typ,'L':mat,'M':clasp,'P':'Китай','S':'повседневный','T':a,'U':dd,'V':ww,'W':hh,'X':col,'Y':'для женщин'}
        bad=[(k,row[c]) for c,k in (('J','Тип сумки'),('L','Материал верха'),('M','Застежка'),('P','Страна производства'),('S','Стиль'),('X','Цвет'),('Y','Для кого')) if row[c] not in V[k]]
        if bad: ctx.skip(r,'нет в списке шаблона: '+str(bad)); continue
        table.append(row)
    return table,25
HANDLERS.update({'Master - Women pants':pants,'Master - Women robes':robes,'Master - Women blouses':blouses,'Master - Women bodysuits':bodysuits,
 'Master - Women socks':socks,'Master - Women tanks and camis':tanks,'Master - Women lightweight jackets':jackets,'Master - Women cardigans':cardigans,
 'Master - Women hoodies':hoodies,'Master - Women t-shirts':tshirts,'Master - Cosmetic bags and travel cases':cosmetic,'Master - Fashion handbags':handbags})
