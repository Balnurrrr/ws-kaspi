# -*- coding: utf-8 -*-
import openpyxl, warnings, collections, re
warnings.filterwarnings('ignore')
def load_pl(path):
    rows=list(openpyxl.load_workbook(path,read_only=True).active.iter_rows(values_only=True))
    hd=['COLOUR' if str(h)=='0' else str(h) for h in rows[0]]; ix={h:i for i,h in enumerate(hd)}
    need=['STYLE','EAN STYLE','SIZE','DESCRIPTION','COMPOSITION','COLOR DESCRIP']
    miss=[k for k in need if k not in ix]
    if miss: raise ValueError('В накладной нет колонок: '+', '.join(miss))
    s=lambda r,k:(str(r[ix[k]]).strip() if k in ix and r[ix[k]] is not None else '')
    out=[];seen=set()
    for r in rows[1:]:
        if not s(r,'STYLE'): continue
        e=s(r,'EAN STYLE')
        if e in seen: continue          # дубли строк из-за коробок
        seen.add(e); out.append({k:s(r,k) for k in hd}|{'_q':r[ix['QUANTITY']] if 'QUANTITY' in ix else None})
    return out
