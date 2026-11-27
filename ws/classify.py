# -*- coding: utf-8 -*-
"""Разбор накладной: какие в ней категории (по-русски), какой шаблон Kaspi нужен, что уже есть на сайте."""
import os, re, collections
from . import cats
BASE=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'kaspi_templates')
# (regex по DESCRIPTION, название по-русски, имя файла шаблона Kaspi, где его взять в кабинете)
RULES=[
 (r'NIPPLE','Накладки на соски',None,'Бельё / аксессуары для бюстгальтеров'),
 (r'^BRA|BRA$','Бюстгальтеры','Women-bras-import-template.xlsm','Женское бельё → Бюстгальтеры'),
 (r'BRIEF|SHAPE','Трусы','Women-panties-import-template.xlsm','Женское бельё → Трусы'),
 (r'PYJAMA|PAJAMA|NIGHTDRESS','Пижамы и ночные сорочки','Women-nightwear-import-template.xlsm','Одежда для дома → Ночные сорочки и пижамы'),
 (r'ROBE','Халаты','Women-robes-import-template.xlsm','Одежда для дома → Халаты'),
 (r'BLOUSE|JERSEY|KNITWEAR','Блузки и джемперы','Women-blouses-import-template.xlsm','Женская одежда → Блузки'),
 (r'PANTS','Брюки','Women-pants-import-template.xlsm','Женская одежда → Брюки'),
 (r'VANITY','Косметички','Cosmetic-bags-and-travel-cases-import-template.xlsm','Аксессуары → Косметички и несессеры'),
 (r'BAG|PURSE','Сумки','Fashion-handbags-import-template.xlsm','Аксессуары → Сумки'),
 (r'BODY','Боди','Women-bodysuits-import-template.xlsm','Женская одежда → Боди'),
 (r'SOCK','Носки','Women-socks-import-template.xlsm','Женская одежда → Носки'),
 (r'TSHIRT|T-SHIRT','Футболки','Women-t-shirts-import-template.xlsm','Женская одежда → Футболки'),
 (r'\bTOP\b','Топы и майки','Women-tanks-and-camis-import-template.xlsm','Женская одежда → Майки и топы'),
 (r'DRESS','Платья',None,'Женская одежда → Платья'),
 (r'BOTTLE','Бутылки','Beverage-bottles-import-template.xlsm','Посуда → Бутылки для напитков'),
 (r'CAP\b','Кепки','Fashion-hats-and-caps-import-template.xlsm','Аксессуары → Головные уборы'),
]
def label_of(desc):
    d=desc.upper()
    for rx,name,tpl,where in RULES:
        if re.search(rx,d): return name,tpl,where
    return None,None,None
HANDLED_TPL=None
def analyze(rows):
    g=collections.OrderedDict()
    for r in rows:
        name,tpl,where=label_of(r['DESCRIPTION'])
        key=name or 'Не распознано'
        e=g.setdefault(key,{'name':key,'tpl':tpl,'where':where,'styles':set(),'positions':0,'examples':set()})
        e['styles'].add(r['STYLE']); e['positions']+=1; e['examples'].add(r['DESCRIPTION'].strip())
    out=[]
    for e in g.values():
        tpl=e['tpl']; have=bool(tpl) and os.path.exists(os.path.join(BASE,tpl))
        status='ok' if have else 'need'
        out.append({'name':e['name'],'articles':len(e['styles']),'positions':e['positions'],'tpl':tpl,'where':e['where'],'status':status,'examples':sorted(e['examples'])[:3]})
    order={'ok':0,'need':1}
    return sorted(out,key=lambda x:(order[x['status']],-x['positions']))
