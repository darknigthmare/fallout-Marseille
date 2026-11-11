#!/usr/bin/env python3
"""Deterministic, source-linked regional inventory. Names are not gameplay proof.
Uses only the checked-in legacy catalogues and authored regional visual contracts.
Does not certify encounters, acquisition routes, rights or official Fallout canon.
"""
from __future__ import annotations
import argparse, hashlib, json, re, subprocess, unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
JSON_PATH='docs/INVENTAIRE_ARSENAL_BESTIAIRE.json'
MD_PATH='docs/INVENTAIRE_ARSENAL_BESTIAIRE.md'
def fold(s):return ''.join(c for c in unicodedata.normalize('NFKD',s.casefold()) if not unicodedata.combining(c) and c.isalnum())
def sections(text,start,end):
 a=re.search(rf'^## {start}\. ',text,re.M);b=re.search(rf'^## {end+1}\. ',text,re.M)
 if not a or not b:raise ValueError('Bible section boundaries changed')
 return text[a.start():b.start()]
def bullets(text):
 result=[];section=''
 for line in text.splitlines():
  if line.startswith('## '):section=line[3:]
  if not line.startswith('- '):continue
  item=line[2:].strip().rstrip(' ;.')
  item=re.sub(r'^\*\*([^*]+)\*\*.*',r'\1',item)
  if item.startswith('Général Biset,'):item='Général Biset'
  result.append((item,section))
 return result

def build(root=ROOT):
 read=lambda p:(root/p).read_text(encoding='utf-8')
 def node(code):return json.loads(subprocess.check_output(['node','-e',code],cwd=root,text=True))
 cat=node("console.log(JSON.stringify(require('./tools/regional_catalog_snapshot.cjs')()))")
 arsenal=node("console.log(JSON.stringify(require('./src/v050/17a_regional_arsenal.js').RECORDS))")
 rigs=node("console.log(JSON.stringify(require('./src/v050/13_regional_bestiary.js').catalog()))")
 if isinstance(rigs,list):rigs={v.get('id'):v for v in rigs}
 bible=read('docs/BIBLE_LORE_FALLOUT_MISTRAL.md')
 weapon_concepts=bullets(sections(bible,38,42));creatures=bullets(sections(bible,29,36))
 # These names live in prose/subheadings instead of bullet lists. Keep their exact
 # spelling and a section anchor. Do not infer aliases from a similar animal name.
 extra={29:['Midi-Zéro'],30:['Blattes de cité','Punaises de foyer','Taupes de métro','Fouines de compteur','Mites d’archive','Termites de béton'],31:['Écorcheur calcaire'],32:['La Sardine'],35:['Hommes-lourds','Agrégats ATLAS','César ATLAS']}
 for section,names in extra.items():
  block=sections(bible,section,section)
  for name in names:
   if fold(name) not in fold(block):raise ValueError('Prose concept no longer in bible: '+name)
   creatures.append((name,f'{section}. Prose et sous-titres'))
 witness=read('src/v046/04_lore.js');m=re.search(r'bestiary:(\[[^\n]+?\])',witness)
 if not m:raise ValueError('Witness list missing')
 # The trusted checked-in literal contains strings only; no runtime is invoked.
 witnesses=node('console.log(JSON.stringify('+m[1]+'))')
 known={fold(n) for n,_ in creatures}
 for name in witnesses:
  if fold(name) not in known:creatures.append((name,'Catalogue de témoins v0.46'));known.add(fold(name))
 def exact(name,pool):return [k for k,v in pool.items() if fold(v.get('name',''))==fold(name)]
 weapons=[]
 for wid in cat['regional']:
  if wid not in cat['weapons'] or wid not in arsenal:raise ValueError('Unmapped regional ID '+wid)
  w=cat['weapons'][wid];ammo=None if w.get('melee') else w.get('ammoId','ammo10')
  if ammo and ammo not in cat['ammo']:raise ValueError('Unknown ammunition '+wid)
  weapons.append({'id':wid,'name':w['name'],'source':'src/core-v017.js','presentation_source':'src/v050/17a_regional_arsenal.js','family':arsenal[wid]['family'],'profile':arsenal[wid]['profile'],'ammo_id':ammo,'ammo_name':cat['ammo'].get(ammo,{}).get('name'),'base_damage':w['damage'],'clip':None if w.get('melee') else w['clip'],'range':w['range'],'base_reload':None if w.get('melee') else w['reload'],'status':'catalogue-et-profil','additional_presentation':arsenal[wid]['profile'] in ['ceramic-disc','mortar40','needle'],'limits':'Acquisition et équilibrage complet non certifiés par cet inventaire. Les profils partagés ne sont pas des modèles uniques.'})
 concepts=[]
 for name,section in weapon_concepts:
  ids=exact(name,cat['weapons']);concepts.append({'name':name,'section':section,'catalogue_ids':ids,'status':'nom-exact-au-catalogue' if ids else 'concept-sans-correspondance-exacte','limit':'Aucun alias ou équivalent déduit d’une ressemblance de nom.'})
 best=[]
 for name,section in creatures:
  ids=exact(name,cat['enemies']);vis=exact(name,rigs)
  best.append({'name':name,'section':section,'catalogue_ids':ids,'rig_ids':vis,'status':'representation-regionale' if vis else 'archetype-declare' if ids else 'concept-ou-temoignage','limit':"L’assemblage actuel n’est pas l’agrégat décrit en section 30." if name=='Rat-couronné' else 'Un nom et un archétype ne certifient ni modèle unique, ni quête, ni apparition régionale.'})
 sources=['src/core-v017.js','src/v046/04_lore.js','src/v050/13_regional_bestiary.js','src/v050/17a_regional_arsenal.js','docs/BIBLE_LORE_FALLOUT_MISTRAL.md']
 result={'schema':1,'scope':'55 IDs explicitement régionaux du catalogue existant ; armes des sections 38–42 ; créatures des sections 29–36 et liste des 25 témoins v0.46. Les autres armes du jeu ne sont pas renommées. Correspondances exactes normalisées, sans alias supposé.','canon':'fan-lore-original-non-officiel','source_sha256':{s:hashlib.sha256((root/s).read_bytes()).hexdigest() for s in sources},'counts':{'regional_weapon_ids':len(weapons),'bible_weapon_concepts':len(concepts),'creature_records':len(best),'regional_rigs':len(rigs)},'regional_weapons':weapons,'bible_weapons':concepts,'creatures':best,'known_gaps':['Profils génériques restants : harpons, charges de saumure, bobines et combustibles ne sont pas des alimentations uniques achevées.','Pique de la République et Mousquet voltaïque de l’An 220 ne sont pas assimilés à une lance ou un mousquet laser existant.','Pigeons postaux neutres distincts du Biset de plomb, du Pigeon-paratonnerre et du Général Biset.','Roi des Égouts et Roi-Couronne : rapprochement éditorial à résoudre, aucun boss déclaré livré.','Inventaire des armures, acquisition de chaque arme, équilibrage et campagne humaine encore à examiner.','COCHONNET PR 17 demeure séparé.']}
 return result

def markdown(d):
 lines=['# Arsenal et bestiaire — inventaire lié aux sources','',d['scope'],'','**Une ligne n’est pas une promesse de contenu terminé.** Les nombres décrivent les entrées examinées, pas autant de nouveaux modèles ou de nouvelles missions. Le fichier JSON voisin conserve les identifiants et les empreintes.','','## Armes régionales déjà déclarées','','| ID | Arme | Présentation | Alimentation |','|---|---|---|---|']
 for w in d['regional_weapons']:lines.append(f"| `{w['id']}` | {w['name']} | `{w['profile']}` | {w['ammo_name'] or 'Mêlée'} |")
 lines+=['','Les 55 associations vers des profils partagés sont explicites. La scie et le mortier ont chacun une présentation supplémentaire ; le profil pneumatique est partagé par les deux aiguilles. Les valeurs de dégâts/rechargement sont lues dans le catalogue, pas inventées par le carnet.','','## Armes conçues dans la bible','','| Nom de la bible | Section | Correspondance exacte dans les données |','|---|---|---|']
 for r in d['bible_weapons']:lines.append(f"| {r['name']} | {r['section']} | {', '.join('`'+v+'`' for v in r['catalogue_ids']) or 'Aucune — concept à traiter'} |")
 lines+=['','Une absence de correspondance exacte ne prouve pas une absence de tout équivalent fonctionnel. Elle interdit simplement de fusionner deux armes distinctes sur la base de leur nom.','','## Désignations de créatures et automates','','| Nom | Source narrative | Données / représentation | État et limite |','|---|---|---|']
 for r in d['creatures']:
  ids=', '.join(r['catalogue_ids']+[f"rig:{s}" for s in r['rig_ids']]) or '—'
  lines.append(f"| {r['name']} | {r['section']} | {ids} | {r['status']} {'· agrégat non représenté' if r['name']=='Rat-couronné' else ''} |")
 lines+=['','Les désignations proches ou au singulier/pluriel restent séparées tant qu’un alias n’est pas attesté : le total n’est pas un décompte d’espèces uniques. Les cinq formes régionales du module 13 ne sont pas les vingt-cinq noms du catalogue des témoins. Les quatre figures Fallout récurrentes du même module conservent leurs identités. Les variantes de cigales, les créatures marines et les robots seulement nommés restent des concepts tant que leur boucle n’est pas réalisée.','','## Manques maintenus ouverts','']+['- '+x for x in d['known_gaps']]+['','## Reproduire la vérification','','`python tools/audit_regional_content.py --check`','','Le générateur examine les sources locales ; il ne contacte aucun service et n’édite aucune sauvegarde. Le contrôle échoue si les données documentées ne correspondent plus aux sources.','']
 return '\n'.join(lines)

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');a=p.parse_args();d=build();outputs={JSON_PATH:json.dumps(d,ensure_ascii=False,indent=2)+'\n',MD_PATH:markdown(d)}
 for name,text in outputs.items():
  path=ROOT/name
  if a.check:
   if not path.is_file() or path.read_text()!=text:raise SystemExit('Inventaire périmé : '+name)
  else:path.write_text(text,encoding='utf-8')
 print(json.dumps({'ok':True,**d['counts']},ensure_ascii=False))
if __name__=='__main__':main()
