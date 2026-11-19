# -*- coding: utf-8 -*-
import os, uuid, json, shutil, threading, time, secrets, re
from functools import wraps
from flask import Flask, request, redirect, url_for, session, render_template, jsonify, send_from_directory, abort
from werkzeug.utils import secure_filename
from ws import job
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
def index(): return render_template('index.html',user=session['u'])
def cleanup():
    for d in os.listdir(DATA+'/jobs'):
        p=f'{DATA}/jobs/{d}'
        if time.time()-os.path.getmtime(p)>24*3600: shutil.rmtree(p,ignore_errors=True); JOBS.pop(d,None)
@app.route('/start',methods=['POST'])
@login_required
def start():
    cleanup()
    pl=request.files.get('pl'); tpls=[f for f in request.files.getlist('tpl') if f.filename]
    if not pl or not pl.filename or not tpls: return render_template('index.html',user=session['u'],err='Нужна накладная (PL) и хотя бы один шаблон Kaspi.')
    jid=uuid.uuid4().hex[:12]; jd=f'{DATA}/jobs/{jid}'; os.makedirs(jd+'/templates'); os.makedirs(jd+'/uploads')
    pl.save(jd+'/pl.xlsx')
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
@app.route('/download/<jid>/<name>')
@login_required
def download(jid,name):
    st=JOBS.get(jid) or abort(404)
    if st['user']!=session['u']: abort(403)
    return send_from_directory(f'{DATA}/jobs/{jid}/out',name,as_attachment=True)
if __name__=='__main__': app.run(port=5060,debug=False)
