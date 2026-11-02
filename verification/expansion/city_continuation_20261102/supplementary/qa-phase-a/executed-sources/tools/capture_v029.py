"""Screenshots of the exact game. Cameras, times, perception steps and some quest
states are prepared; the test suites separately verify prerequisites and routes.
No geography import and no generated concept art used as a fake screenshot."""
from qa029_support import Game,R,H
import json,math,hashlib
G=Game('CAPTURES_V029');p=G.p;c=G.c;shots=[];cur={}

def draw(pos,yaw=0,pitch=0):
 cur.update(zone=G.s()['player']['zone'],pos=pos,yaw=yaw,pitch=pitch);return c('v028Render',pos,yaw,pitch)
def face(target,distance=6):
 x,y,z=target;found=False
 for dx,dz in [(0,distance),(distance,0),(-distance,0),(0,-distance),(distance*.7,distance*.7),(-distance*.7,distance*.7)]:
  at=[x+dx,y+1.65,z+dz]
  if not c('v020Collides',at)and c('v020LOS',at,[x,y+1.1,z]):draw(at,math.atan2(-dx,dz),-.05);found=True;break
 return found

def shot(name,title,note):
 p.evaluate("document.getElementById('toastStack').innerHTML=''");p.wait_for_timeout(90);p.screenshot(path=str(R/'verification'/name));shots.append({'file':name,'title':title,'note':note,'camera':dict(cur),'renderer':'software Chromium','sha256_html':hashlib.sha256(H.encode()).hexdigest()});print('CAPTURE',name,flush=True)

def term(id):
 G.open(id);st=G.s()['player'];draw(st['pos'],st['yaw'],-.03)

try:
 G.memory();shot('01_menu.png','Les portes ont des oreilles','Menu du fichier exact. Le nouveau départ est une exploration distincte ; il demande confirmation.')
 G.reset();G.near('v029:adrien');st=G.s()['player'];draw(st['pos'],st['yaw'],.04)
 shot('02_adrien_depot.png','Adrien, technicien des accès','Personnage ajouté à la cour historique d’Aubagne. Modèle procédural partagé, pas un nouveau personnage photoréaliste.')
 c('v029Talk');G.speak('suivre le refus');shot('03_adrien_dossier.png','Une panne mécanique et une règle d’exclusion','L’enquête est acceptée par le dialogue réel. Le dossier indique les pièces et journaux à consulter.')
 G.dismiss();G.near('v029:terminal:depot');st=G.s()['player'];draw([st['pos'][0]+1.0,1.65,st['pos'][2]+2.0],-.16,-.08)
 shot('04_controleur_physique.png','Un poste présent dans le dépôt','Le contrôleur est un objet de la scène avec clavier, écran et collision. Les commandes ne sont pas accessibles de n’importe où.')
 term('depot');G.click('hack');shot('05_deduction.png','Déduction par position des lettres','Douze candidats de cinq lettres. Les boutons sont réellement cliquables ; quatre essais, trois séquences de mémoire limitées.')
 d=c('v029Deck','depot');wrong=next(i for i in range(12)if i!=d['answer']);G.click('word',wrong);G.click('bracket',0)
 shot('06_similitude.png','Un indice, pas un résultat aléatoire','Un mauvais candidat a consommé un essai. La similitude et le leurre retiré proviennent du même mot de passe persistant.')
 for i in [i for i in range(12)if i!=d['answer']and i not in G.st()['terminals']['depot']['guessed']and i not in G.st()['terminals']['depot']['removed']][:3]:G.click('word',i)
 shot('07_verrouillage.png','Verrouillé après quatre erreurs','Verrouillage obtenu par quatre tentatives réellement effectuées. Attendre dans le menu ne fait pas progresser les 45 secondes de jeu actif.')
 G.dismiss();G.near('v029:badge:d4');c('v029Credential','d4');G.dismiss();term('depot');G.click('badge');G.click('command','door')
 shot('08_commande_confirmation.png','L’habilitation, puis la commande','La fiche D-4 contourne l’authentification, même pendant le verrouillage. Elle n’ouvre pas automatiquement le volet : une confirmation séparée est nécessaire.')
 G.click('cancel');G.dismiss();draw([-15,1.65,37.7],math.pi,0)
 shot('09_volet_ferme.png','Avant : le magasin technique fermé','Alcôve ajoutée dans la cour existante, pas une nouvelle commune. Les murs et le volet empêchent réellement le passage.')
 term('depot');G.click('command','door');G.click('confirm','door');G.dismiss();draw([-15,1.65,37.7],math.pi,0)
 shot('10_volet_ouvert.png','Après : le passage est ouvert','Même caméra et même scène que l’image précédente. La collision du volet est désactivée, les murs restent solides.')
 walk=c('v021ActualWalk',[-15,0,44.35]);cur['walk']=walk;draw([-15,1.65,43.4],math.pi,-.13)
 shot('11_interieur_service.png','Le contact dans le local de service','Intérieur accessible en marchant, sans chargement. Sa poignée mécanique fonctionne depuis l’intérieur même sans authentification.')
 c('v029Contact');G.dismiss();G.load('traverse_archives');G.near('v029:badge:a2');st=G.s()['player'];draw(st['pos'],st['yaw'],-.16);c('v029Credential','a2')
 shot('12_fiche_etage.png','A-2, une autre voie que la Science','La fiche se trouve dans la galerie haute. La capture prépare la caméra ; les tests effectuent séparément la montée aux escaliers avec le contrôleur.')
 G.dismiss();term('archives');G.click('badge');G.click('read',1)
 shot('13_journal_archives.png','Le journal de la Traverse','Un texte original fournit la preuve A-2 et rejoint les notes du Pip-Boy. Cette copie ne commande pas la machine à distance.')
 G.dismiss();G.reset('transit_depot',False);c('v023Special',{'I':10});term('depot');G.click('hack');d=c('v029Deck','depot');G.click('word',d['answer']);G.click('command','standby');G.click('confirm','standby');G.dismiss()
 e=next(e for e in c('v029Stealth')['enemies']if e['id']=='transit_depot:unit');face(e['pos'],5);c('v029AI',.01);st=G.s()['player'];draw(st['pos'],st['yaw'],st['pitch'])
 shot('14_automate_veille.png','Le Protectron est en veille, pas mort','Automate réellement présent au dépôt. Il reste vivant, visible et sans récompense de mort. Sa consignation est contrôlée séparément par les tests.')
 # A real existing enemy, fixed facing and a fraction of the real acquisition procedure.
 G.reset('transit_depot',False);en=c('v029Stealth')['enemies'][0];e=en['pos'];chosen=None
 for dx,dz in [(0,4.5),(4.5,0),(-4.5,0),(0,-4.5),(3.2,3.2)]:
  at=[e[0]+dx,e[1]+1.65,e[2]+dz]
  if not c('v020Collides',at)and c('v020LOS',at,[e[0],e[1]+1.1,e[2]]):chosen=(at,math.atan2(-dx,dz),math.atan2(dx,-dz));break
 if chosen:
  at,yaw,enemyyaw=chosen;c('v020SetPlayer',{'pos':at,'crouched':True});c('v020EnemyPatch',{'yaw':enemyyaw,'alerted':False,'v029Sense':{'awareness':0,'heard':None,'time':0}});c('v029Observe',.32);c('v029Stealth');draw(at,yaw,-.05)
  shot('15_soupcon.png','Infiltration : soupçon avant acquisition','Ennemi existant du dépôt, orientation et progression du regard préparées pour rendre le compteur lisible. La détection et les obstacles sont vérifiés dans la suite perception.')
 # Prepared complete dossier for outcome/report; full normal credential route is separately tested.
 G.reset();c('v029Set',{'quest':{'accepted':True,'proof':{'route':True,'filter':True,'clause':True},'contact':True}});c('v020Seed',{'scrap':4,'circuitry':3});G.near('v029:adrien');st=G.s()['player'];draw(st['pos'],st['yaw']);c('v029Preview','supervised')
 shot('16_bilan.png','Une règle vérifiable avant signature','État de dossier préparé pour présenter le bilan. Une autre suite parcourt la collecte et l’autre issue sans le G.O.A.T.')
 G.speak('Confirmer');shot('17_epilogue.png','Le contact revient','Première des trois scènes textuelles de la conclusion surveillée. Les deux conclusions comportent six textes distincts ; aucun doublage n’est ajouté.')
 for _ in range(3):p.locator('#dialogueChoices button').first.click()
 G.open('depot');G.click('hack');d=c('v029Deck','depot');G.click('word',d['answer']);G.click('read',1);G.dismiss();c('v027Open','data','security')
 shot('18_pip_controleurs.png','Copie locale dans DATA','Contrôleurs visités et journaux acquis. L’archive est en lecture seule, sans réinitialisation des essais ni commande de sécurité.')
 G.dismiss();G.reset();term('depot');G.click('hack');p.set_viewport_size({'width':390,'height':844})
 shot('19_mobile_terminal.png','Le terminal sur une fenêtre étroite','Fenêtre 390 × 844, pas un test matériel iPhone. Les vrais gestes tactiles sont exécutés dans la suite QA tactile.')
except Exception:G.fail()
(R/'verification/CAPTURES_V029.json').write_text(json.dumps({'html_sha256':hashlib.sha256(H.encode()).hexdigest(),'errors':G.errors,'images':shots,'scope':'Exact runtime software captures. Fixed cameras, frozen runtime and some prepared state; walkthroughs/physics tested separately. Fictional scenes, no real map data.'},ensure_ascii=False,indent=2))
raise SystemExit(G.output())
