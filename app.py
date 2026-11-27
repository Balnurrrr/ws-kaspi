# -*- coding: utf-8 -*-
import os, uuid, json, shutil, threading, time, secrets, re
from functools import wraps
from flask import Flask, request, redirect, url_for, session, render_template, jsonify, send_from_directory, send_file, abort
from werkzeug.utils import secure_filename
from ws import job, pl as plmod, classify
DATA=os.environ.get('WS_DATA','/tmp/ws-data'); os.makedirs(DATA+'/jobs',exist_ok=True)
USERS=dict(p.split(':',1) for p in os.environ.get('WS_USERS','admin:admin').split(',') if ':' in p)   # "анна:пароль1,олег:пароль2"
app=Flask(__name__); app.secret_key=os.environ.get('SECRET_KEY') or secrets.token_hex(16)
app.config.update(MAX_CONTENT_LENGTH=400*1024*1024,SESSION_COOKIE_HTTPONLY=True,SESSION_COOKIE_SAMESITE='Lax',PERMANENT_SESSION_LIFETIME=12*3600)
JOBS={}
def login_required(f):
    @wraps(f)
    def w(*a,**k):
        if not session.get('u'): return redirect(url_for('login'))
        return f(*a,**k)
    return w
@app.route('/login',methods=['GET','POST'])
def login():
    err=''
    if request.method=='POST':
        u,p=request.form.get('u','').strip(),request.form.get('p','')
        if u in USERS and secrets.compare_digest(USERS[u],p): session.permanent=True; session['u']=u; return redirect('/')
        err='Неверный логин или пароль'; time.sleep(1)
    return render_template('login.html',err=err)
@app.route('/logout')
def logout(): session.clear(); return redirect('/login')
@app.route('/')
@login_required
def index(): return render_template('index.html',user=session['u'],cats=[c.replace('Master - ','') for c in job.cats.HANDLERS])
def cleanup():
    for d in os.listdir(DATA+'/jobs'):
        p=f'{DATA}/jobs/{d}'
        if time.time()-os.path.getmtime(p)>24*3600: shutil.rmtree(p,ignore_errors=True); JOBS.pop(d,None)
@app.route('/analyze',methods=['POST'])
@login_required
def analyze():
    cleanup()
    f=request.files.get('pl')
    if not f or not f.filename: return render_template('index.html',user=session['u'],err='Загрузите накладную (PL).')
    jid=uuid.uuid4().hex[:12]; jd=f'{DATA}/jobs/{jid}'; os.makedirs(jd+'/templates'); os.makedirs(jd+'/uploads'); f.save(jd+'/pl.xlsx')
    try: rows=plmod.load_pl(jd+'/pl.xlsx')
    except Exception as e:
        shutil.rmtree(jd,ignore_errors=True); return render_template('index.html',user=session['u'],err=f'Не удалось прочитать накладную: {e}')
    res=classify.analyze(rows)
    return render_template('analyze.html',user=session['u'],jid=jid,res=res,total=len(rows),fname=f.filename,
                           need=[r for r in res if r['status']=='need'])
@app.route('/start/<jid>',methods=['POST'])
@login_required
def start(jid):
    jd=f'{DATA}/jobs/{jid}'
    if not re.fullmatch(r'[0-9a-f]{12}',jid) or not os.path.exists(jd+'/pl.xlsx'): abort(404)
    tpls=[f for f in request.files.getlist('tpl') if f.filename]
    for i,f in enumerate(tpls): f.save(f'{jd}/templates/{i}_{secure_filename(f.filename) or "t.xlsm"}')
    links=[l.strip() for l in re.split(r'[\s,]+',request.form.get('links','')) if l.strip().startswith('http')]
    for f in request.files.getlist('photos'):
        if f.filename: open(jd+'/uploads/'+os.path.basename(f.filename),'wb').write(f.read())
    json.dump(links,open(jd+'/links.json','w'))
    st={'user':session['u'],'stage':'Запуск','finished':False}; JOBS[jid]=st
    threading.Thread(target=job.run_job,args=(jd,st),daemon=True).start()
    return redirect(url_for('job_page',jid=jid))
@app.route('/job/<jid>')
@login_required
def job_page(jid):
    if jid not in JOBS: abort(404)
    return render_template('job.html',jid=jid)
@app.route('/status/<jid>')
@login_required
def status(jid):
    st=JOBS.get(jid) or abort(404)
    if st['user']!=session['u']: abort(403)
    return jsonify({k:v for k,v in st.items() if k!='trace'})
@app.route('/download_all/<jid>')
@login_required
def download_all(jid):
    import zipfile, io
    st=JOBS.get(jid) or abort(404)
    if st['user']!=session['u']: abort(403)
    out=f'{DATA}/jobs/{jid}/out'; path=f'{DATA}/jobs/{jid}/all.zip'
    with zipfile.ZipFile(path,'w',zipfile.ZIP_STORED) as z:
        for f in sorted(os.listdir(out)):
            if f.endswith('.zip') or f.endswith('.xlsx'): z.write(f'{out}/{f}',f)
    return send_file(path,as_attachment=True,download_name='Kaspi-все-архивы.zip',mimetype='application/zip')
@app.route('/download/<jid>/<name>')
@login_required
def download(jid,name):
    st=JOBS.get(jid) or abort(404)
    if st['user']!=session['u']: abort(403)
    return send_from_directory(f'{DATA}/jobs/{jid}/out',name,as_attachment=True)
if __name__=='__main__': app.run(port=5060,debug=False)
