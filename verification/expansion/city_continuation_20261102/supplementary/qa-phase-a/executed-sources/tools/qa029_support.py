"""Exact single-file browser harness. Opaque-origin storage is explicitly tested
before using a declared memory adapter. No GPU / geospatial validation claimed."""
from pathlib import Path
import hashlib,json,traceback
from playwright.sync_api import sync_playwright
from qa_support import chromium_path
R=Path(__file__).resolve().parents[1]
H=(R/'JOUER_FALLOUT_MISTRAL_v0.35.html').read_text()
class Game:
 def __init__(self,name,viewport=None,touch=False):
  self.name=name;self.checks=[];self.errors=[];self.pw=sync_playwright().start()
  self.b=self.pw.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage'])
  self.p=self.b.new_page(viewport=viewport or {'width':1440,'height':960},has_touch=touch);self.p.set_default_timeout(7000)
  self.p.on('pageerror',lambda e:self.errors.append(str(e)));self.p.set_content(H,wait_until='load');self.p.locator('#btnV029').wait_for(state='attached',timeout=30000)
  self.c('setRenderPaused',True);self.c('v022Freeze',True);self.c('v018NoNetwork',True)
 def c(self,n,*a):return self.p.evaluate('(a)=>__MISTRAL_DEBUG.'+n+'(...a)',list(a))
 def s(self):return self.c('getState')
 def st(self):return self.c('v029State')
 def check(self,ok,name,detail=None):
  self.checks.append({'ok':bool(ok),'name':name,'detail':detail});print(('OK 'if ok else 'FAIL ')+name,flush=True)
 def memory(self):
  self.p.evaluate("window.__STORE={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>__STORE[k]??null,setItem:(k,v)=>__STORE[k]=String(v),removeItem:k=>delete __STORE[k]}})")
 def dismiss(self):
  self.c('v029Close')
  if self.p.locator('#pipboy').is_visible():self.c('closePip')
  self.c('v020ModalDismiss')
 def load(self,zone='transit_depot',mute=True):
  self.dismiss();self.c('v020Load',zone);self.c('v022ResetRuntime');self.c('v022Time',10)
  if mute:self.c('v021MuteEnemies')
 def reset(self,zone='transit_depot',mute=True):
  self.dismiss();self.c('v020Reset');self.load(zone,mute);self.c('v028Settings',{'survivalNeeds':False});self.c('v026Carry',False)
 def near(self,id):return self.c('v020Approach',id)
 def open(self,id):
  d=self.c('v029Defs')[id]
  if self.s()['player']['zone']!=d['zone']:self.load(d['zone'])
  self.near(d['anchor']);return self.c('v029Open',id)
 def click(self,a,arg=None):
  sel='#terminal29 [data-t29="'+a+'"]'+('' if arg is None else '[data-arg="'+str(arg)+'"]')
  self.p.locator(sel).first.click()
 def speak(self,needle):self.p.locator('#dialogueChoices button').filter(has_text=needle).first.click()
 def solve(self,id):
  self.c('v023Special',{'I':10});self.open(id);self.click('hack');deck=self.c('v029Deck',id);self.click('word',deck['answer']);return deck
 def output(self):
  result={'version':'0.35.0','html_sha256':hashlib.sha256(H.encode()).hexdigest(),'passed':sum(x['ok']for x in self.checks),'failed':sum(not x['ok']for x in self.checks),'total':len(self.checks),'results':self.checks,'errors':self.errors,'scope':'Exact HTML via set_content; software Chromium; controlled state/poses disclosed; successful saves via declared memory adapter. Native opaque-origin refusal checked separately. No official geospatial data.'}
  (R/'verification'/('QA_'+self.name+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2));self.b.close();self.pw.stop();print('TOTAL',result['passed'],result['failed'],'ERRORS',self.errors,flush=True);return bool(result['failed']or self.errors)
 def fail(self):self.check(False,'Exception du scénario',traceback.format_exc())
