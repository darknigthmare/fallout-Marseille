from qa029_support import Game
import json
G=Game('V030_TOUCH',viewport={'width':390,'height':844},touch=True);c=G.c;ck=G.check;p=G.p
p.on('dialog',lambda d:d.accept())
try:
 G.memory();p.wait_for_timeout(2000);c('v030Start');c('v021MuteEnemies');G.near('v030:station');c('v030Set',{'rig':'mistralRig','core':65,'active':False,'parts':{'head':35,'leftLeg':50}});c('v030Show')
 p.locator('.p30-slots button[data-arg="leftLeg"]').tap();ck(p.locator('.p30-slots button[data-arg="leftLeg"]').get_attribute('aria-pressed')=='true','Tactile : sélectionner la vraie pièce sans clic programmatique')
 button=p.locator('[data-p27="p30:power"]');button.scroll_into_view_if_needed();button.tap();ck(c('v030State')['active'],'Tactile : enclencher les moteurs');button=p.locator('[data-p27="p30:power"]');button.tap();ck(not c('v030State')['active'],'Tactile : arrêter les moteurs');p.locator('[data-p27="p30:eject"]').tap();ck(c('v030State')['spares']==[65] and c('v030State')['core']is None,'Tactile : éjection à charge conservée');p.locator('[data-p27="p30:used"][data-arg="0"]').tap();ck(c('v030State')['core']==65 and not c('v030State')['spares'],'Tactile : réinsérer le même cœur, pas un nouveau')
 c('v027Dispatch','theme','amber');style=p.locator('.p30-slots button.active').evaluate('(e)=>getComputedStyle(e).backgroundColor');ck(style=='rgb(245, 202, 117)','La pièce active suit le phosphore ambre');c('v027Dispatch','theme','white');style=p.locator('.p30-slots button.active').evaluate('(e)=>getComputedStyle(e).backgroundColor');ck(style=='rgb(216, 240, 233)','La pièce active suit le phosphore blanc')
 c('v027Dispatch','theme','green');ck(p.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),'Page sans débordement horizontal sur fenêtre 390 × 844');b=p.locator('[data-p27="p30:power"]');b.scroll_into_view_if_needed();ck(b.bounding_box()['height']>=30,'Commande principale accessible sans poignée minuscule')
 G.dismiss();c('v030Render',[10,1.65,36],3.14,0,True);hud=p.locator('#p30Hud').bounding_box();hint=p.locator('#v020QuestHint').bounding_box();ck(hud and hint and hud['y']>=hint['y']+hint['height'],'HUD d’armure placé sous le suivi de quête sans chevauchement');p.locator('#p30Hud').tap();ck(c('getMode')=='PIP'and p.locator('.p30-slots').is_visible(),'HUD tactile ouvre le diagnostic du châssis')
 # Real export produces a downloaded JSON with charges and selected pieces.
 c('v027Open','data','system')
 # Use the existing validated export command through debug; browser download event is real.
 with p.expect_download()as d:p.locator('[data-p27="export"]').tap()
 download=d.value;target=G.p.locator('body');path=download.path();raw=json.loads(open(path).read());ck(raw['v030']['core']==65 and raw['v030']['rigs']['mistralRig']['parts']['leftLeg']==50,'Export JSON effectivement téléchargé avec charge et état de pièce')
except Exception:G.fail()
G.output()
