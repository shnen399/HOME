import os, re, json, time
from datetime import datetime
from typing import Dict
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

TITLE_SELECTOR   = os.getenv("TITLE_SELECTOR", "#editArticle-header-title")
CONTENT_SELECTOR = os.getenv("CONTENT_SELECTOR", "[contenteditable='true']")
PUBLISH_SELECTOR = os.getenv("PUBLISH_SELECTOR", "#edit-article-footer > div.action-buttons > button.radius.primary")

FAIL_DB  = "account_failures.json"
ACCOUNTS_FILE = "pixnet_accounts.txt"
LOG_FILE = "發文紀錄.txt"

def _now(): return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def _append_log(d): open(LOG_FILE,"a",encoding="utf-8").write(json.dumps({**d,"ts":_now()}, ensure_ascii=False)+"\n")

def _load_fail(): 
    try: return json.load(open(FAIL_DB,"r",encoding="utf-8"))
    except: return {}
def _save_fail(db: Dict[str,int]): json.dump(db, open(FAIL_DB,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
def _bump(email): db=_load_fail(); db[email]=int(db.get(email,0))+1; _save_fail(db); return db[email]
def _reset(email): db=_load_fail(); 
# ensure reset
def _reset(email):
    db = _load_fail()
    if email in db: db[email]=0; _save_fail(db)

def _delete_line(email):
    if not os.path.exists(ACCOUNTS_FILE): return False
    lines=[]; removed=False
    for line in open(ACCOUNTS_FILE,"r",encoding="utf-8"):
        if line.strip().startswith("#") or ":" not in line: lines.append(line); continue
        acc=line.strip().split(":",1)[0].strip()
        if acc.lower()==email.lower() and not removed: removed=True; continue
        lines.append(line)
    if removed: open(ACCOUNTS_FILE,"w",encoding="utf-8").writelines(lines)
    return removed

def _driver(headless=True):
    o=Options(); o.add_argument("--disable-gpu"); o.add_argument("--no-sandbox"); o.add_argument("--lang=zh-TW"); o.add_argument("--window-size=1366,768")
    if headless: o.add_argument("--headless=new")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=o)

def _login(d, email, pwd):
    d.get("https://panel.pixnet.cc/"); w=WebDriverWait(d,30); time.sleep(2)
    if "account.pixnet.net" in d.current_url or "login" in d.current_url:
        e = w.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="email"], input[name="account"], #account'))); e.clear(); e.send_keys(email)
        p = w.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="password"], input[name="password"], #password'))); p.clear(); p.send_keys(pwd)
        try: d.find_element(By.CSS_SELECTOR,'button[type="submit"], button.login, input[type="submit"]').click()
        except: p.send_keys(Keys.ENTER)
        w.until(EC.url_contains("panel.pixnet.cc"))

def _open_create(d):
    d.get("https://panel.pixnet.cc/#/create-article")
    WebDriverWait(d,30).until(EC.presence_of_element_located((By.CSS_SELECTOR, TITLE_SELECTOR)))

def _fill_title(d, t):
    el=WebDriverWait(d,20).until(EC.presence_of_element_located((By.CSS_SELECTOR, TITLE_SELECTOR))); el.clear(); el.send_keys(t)

def _fill_content(d, html):
    w=WebDriverWait(d,15)
    try:
        ed=w.until(EC.presence_of_element_located((By.CSS_SELECTOR, CONTENT_SELECTOR)))
        d.execute_script("""const el=arguments[0],h=arguments[1]; el.focus(); el.innerHTML=h; ['input','change','keyup'].forEach(e=>el.dispatchEvent(new Event(e,{bubbles:true})));""", ed, html.replace("\n","<br/>")); return
    except: pass
    try:
        iframe=d.find_element(By.CSS_SELECTOR,"iframe, #mce_0_ifr"); d.switch_to.frame(iframe)
        body=d.find_element(By.CSS_SELECTOR,"body"); body.clear(); body.send_keys(html); d.switch_to.default_content(); return
    except: pass
    raise RuntimeError("找不到內容編輯區")

def _publish(d):
    btn=WebDriverWait(d,25).until(EC.element_to_be_clickable((By.CSS_SELECTOR,PUBLISH_SELECTOR))); btn.click()
    WebDriverWait(d,40).until(lambda x: "article" in x.current_url or "article-list" in x.current_url or "panel.pixnet.cc" in x.current_url)

def _extract_url(d):
    import re
    anchors=d.find_elements(By.CSS_SELECTOR,"a[href]"); hrefs=[a.get_attribute("href") for a in anchors if a.get_attribute("href")]
    for h in hrefs:
        if re.search(r"pixnet\.net/.*/post/\d+", h) or re.search(r"pixnet\.net/blog/post/\d+", h): return h
    cur=d.current_url
    if re.search(r"pixnet\.net/.*/post/\d+", cur) or re.search(r"pixnet\.net/blog/post/\d+", cur): return cur
    try:
        d.get("https://panel.pixnet.cc/#/article-list"); WebDriverWait(d,15).until(EC.presence_of_element_located((By.CSS_SELECTOR,"a[href]")))
        anchors=d.find_elements(By.CSS_SELECTOR,"a[href]"); hrefs=[a.get_attribute("href") for a in anchors if a.get_attribute("href")]
        for h in hrefs:
            if re.search(r"pixnet\.net/.*/post/\d+", h) or re.search(r"pixnet\.net/blog/post/\d+", h): return h
    except: pass
    return ""

def read_accounts(path=ACCOUNTS_FILE):
    out=[]
    for line in open(path,"r",encoding="utf-8"):
        line=line.strip()
        if not line or line.startswith("#") or ":" not in line: continue
        u,p=line.split(":",1); out.append((u.strip(), p.strip()))
    return out

def post_one(email, pwd, title, content, tags=None, headless=True):
    d=_driver(headless=headless)
    try:
        _login(d,email,pwd); _open_create(d); _fill_title(d,title); _fill_content(d,content); _publish(d)
        url=_extract_url(d)
        _append_log({"account":email,"status":"success","title":title,"url":url}); _reset(email)
        return True, url or "OK"
    except Exception as e:
        cnt=_bump(email); _append_log({"account":email,"status":"fail","title":title,"error":str(e),"note":f"第 {cnt} 次失敗"})
        if cnt>=3:
            removed=_delete_line(email)
            _append_log({"account":email,"status":"removed" if removed else "remove_failed","reason":f"連續失敗 {cnt} 次"})
        return False, str(e)
    finally:
        try: d.quit()
        except: pass

def post_all(accounts_file, title, content, tags=None, headless=True):
    res=[]
    for u,p in read_accounts(accounts_file):
        ok,msg=post_one(u,p,title,content,tags=headless,headless=headless)
        res.append({"email":u,"ok":ok,"msg":msg}); time.sleep(3)
    return res
