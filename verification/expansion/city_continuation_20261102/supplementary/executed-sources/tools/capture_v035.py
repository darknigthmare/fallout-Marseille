from pathlib import Path
from playwright.sync_api import sync_playwright
from qa_support import chromium_path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
R=Path(__file__).resolve().parents[1];O=R/'verification';O.mkdir(exist_ok=True);H=(R/'JOUER_FALLOUT_MISTRAL_v0.35.html').read_text();shots=[];errs=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':1440,'height':900});p.on('pageerror',lambda e:errs.append(str(e)));p.on('dialog',lambda d:d.accept());p.set_content(H,wait_until='load');p.locator('#menuScreen.active').wait_for(timeout=30000);p.wait_for_timeout(300)
 p.evaluate("window.__S=new Map();Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>__S.get(k)??null,setItem:(k,v)=>__S.set(k,String(v)),removeItem:k=>__S.delete(k)}})")
 def c(n,*a):return p.evaluate('(a)=>__MISTRAL_DEBUG.'+n+'(...a)',list(a))
 def snap(fn,title):p.screenshot(path=str(O/fn));shots.append((O/fn,title));print('CAP',fn)
 snap('v035_01_menu.png','Menu principal restructuré')
 p.click('#btnV035Career');snap('v035_02_carriere.png','Carrière et chapitres');p.click('[data-v35="close"]')
 c('v018NoNetwork',True);c('setRenderPaused',True);c('v018StartStory');p.locator('#v35pTitle:not(.hidden)').wait_for(timeout=12000);snap('v035_03_titre_a03.png','Nouvelle campagne · A-03');p.wait_for_timeout(3100)
 c('v021RenderAt',[0,2.0,60],0,-.03,2);snap('v035_04_dortoir_a03.png','Dortoir des Fontaines')
 c('v35pLocker');p.locator('#dialogueChoices button').first.click();c('v35pClinic');p.locator('#dialogueChoices button').first.click();c('v35pFilter');p.locator('#dialogueChoices button').first.click();c('v35pBreakfast');p.locator('#dialogueChoices button').first.click();c('v35pRation');snap('v035_05_refus_a03.png','Incident déclencheur joué');p.evaluate('__MISTRAL_DEBUG.v020ModalDismiss()')
 c('v018StartFree');p.wait_for_timeout(500)
 c('v035SaveSlot',1);c('v035Open','saves');snap('v035_06_sauvegardes.png','Trois emplacements manuels');p.keyboard.press('Escape')
 c('v035Open','operations');snap('v035_07_operations.png','Huit opérations rejouables');p.keyboard.press('Escape')
 c('v020Load','aubagne');c('v020Approach','v035-vault-return');c('v020Interact','v035-vault-return');p.wait_for_timeout(300);c('v021RenderAt',[0,2.0,8],0,-.04,2);snap('v035_08_hub_a03.png','Retour au hub A-03')
 c('v020Load','aubagne');c('v035StartOperation','ateliers');p.wait_for_timeout(200);stats=c('v020Stats');pt=next(x['pos'] for x in stats['interactables'] if x['id']=='v035-op-ateliers-0');c('v021RenderAt',[pt[0],pt[1]+1.7,pt[2]+4],0,-.08,2);snap('v035_09_operation.png','Opération physique dans le monde')
 c('v035Recap');c('v035Open','recap');snap('v035_10_bilan.png','Bilan de session');p.set_viewport_size({'width':390,'height':844});c('v035Open','saves');snap('v035_11_mobile.png','Sauvegardes en portrait');b.close()
# contact sheet
ims=[]
for path,title in shots:
 im=Image.open(path).convert('RGB');im.thumbnail((640,390));ims.append((im,title))
 W=1320;pad=20;rowh=455;Hh=100+((len(ims)+1)//2)*rowh
 out=Image.new('RGB',(W,Hh),(12,17,14));d=ImageDraw.Draw(out)
 try:f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',28);s=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
 except:f=s=None
 d.text((25,20),'FALLOUT : MISTRAL — v0.35 · RELÈVE COMPLÈTE',fill=(235,224,178),font=f);d.text((25,58),'Captures directes : carrière, sauvegardes, opérations, hub et bilan.',fill=(170,190,165),font=s)
 for i,(im,title) in enumerate(ims):
  x=20+(i%2)*650;y=100+(i//2)*rowh;out.paste(im,(x+(640-im.width)//2,y));d.text((x+12,y+400),title,fill=(225,217,173),font=s)
 out.save(R/'RAPPORT_VISUEL_V0.35.png')
 (O/'CAPTURES_V035.json').write_text(json.dumps({'html_sha256':hashlib.sha256(H.encode()).hexdigest(),'errors':errs,'shots':[{'file':p.name,'title':t} for p,t in shots]},ensure_ascii=False,indent=2))
 print('DONE',len(shots),errs)
