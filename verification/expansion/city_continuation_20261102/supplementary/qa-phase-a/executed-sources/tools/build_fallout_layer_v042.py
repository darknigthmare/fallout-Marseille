#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import hashlib, json, math, random, re

ROOT=Path(__file__).resolve().parents[1]
OUT_JSON=ROOT/'data'/'fallout_layer_v042.json'
OUT_JS=ROOT/'src'/'v042'/'00_catalog.js'
OUT_AUDIT=ROOT/'verification'/'PLACEMENT_FALLOUT_V042.json'
OUT_JSON.parent.mkdir(parents=True,exist_ok=True)
OUT_JS.parent.mkdir(parents=True,exist_ok=True)
OUT_AUDIT.parent.mkdir(parents=True,exist_ok=True)

MACROS={
 'geo_marseille':{
  'label':'Marseille','bbox':[43.2200,5.2850,43.3400,5.5100],'tier':2,'faction':'ligue',
  'anchors':[(43.2951,5.3740,'Vieux-Port'),(43.2995,5.3674,'Le Panier'),(43.2970,5.3818,'Canebière'),(43.3029,5.3804,'Saint-Charles'),(43.3046,5.3941,'Longchamp'),(43.2786,5.4315,'Saint-Loup'),(43.2868,5.4635,'Saint-Marcel'),(43.3145,5.4965,'Les Accates')],
  'ecology':['raider','feral','soapGhoul','concordeDrone','bloatfly','supermutant','protectron'],
  'elites':['markedMan','concordeMagistrate','mirelurkKing'],'boss':'sentryBot',
  'themes':['urban','metro','hospital','industrial','sewer','archive']},
 'geo_huveaune':{
  'label':'Huveaune & Aubagne','bbox':[43.2450,5.4300,43.3350,5.6400],'tier':1,'faction':'ateliers',
  'anchors':[(43.2867,5.4780,'Vallée de l’Huveaune'),(43.2824,5.5160,'La Penne'),(43.2928,5.5708,'Aubagne'),(43.2955,5.5670,'Aubagne Haute'),(43.2888,5.5770,'Céramistes'),(43.2860,5.5540,'Galeries de l’Huveaune'),(43.2858,5.5352,'Camp Major'),(43.3012,5.5948,'Beaudinard')],
  'ecology':['molerat','giantRat','raider','sanglier','tarente','robot','concordeDrone'],
  'elites':['cyberdog','registryScribe','quarryBeast'],'boss':'assaultron',
  'themes':['industrial','sewer','rail','warehouse','shelter','workshop']},
 'geo_garlaban':{
  'label':'Garlaban & Gémenos','bbox':[43.2450,5.4850,43.3900,5.6900],'tier':2,'faction':'collines',
  'anchors':[(43.3132,5.5077,'La Treille'),(43.3270,5.5710,'Font de Mai'),(43.3370,5.5660,'Garlaban'),(43.3450,5.5880,'Col des Vigies'),(43.2968,5.6275,'Gémenos'),(43.3274,5.5740,'Domaine de Font de Mai'),(43.3376,5.5678,'Sommet du Garlaban')],
  'ecology':['sanglier','mistralCicada','mutantHound','yaoGuai','raider','limestoneMaw','tarente'],
  'elites':['quarryBeast','deathclawAlpha','nightkin'],'boss':'quarryBeast',
  'themes':['cave','quarry','rural','bunker','observatory','chapel']},
 'geo_calanques':{
  'label':'Calanques & Cassis','bbox':[43.1450,5.3300,43.2850,5.6500],'tier':3,'faction':'vigies',
  'anchors':[(43.2317,5.4375,'Luminy'),(43.2120,5.4480,'Calanques'),(43.2144,5.5393,'Cassis'),(43.2064,5.5190,'Port-Miou'),(43.2486,5.5907,'Roquefort-la-Bédoule'),(43.1872,5.5628,'Cap Canaille'),(43.2107,5.4184,'Sormiou'),(43.2106,5.4488,'Morgiou')],
  'ecology':['calanqueChameleon','mirelurk','crab','radscorpion','smuggler','bloatfly','limestoneMaw'],
  'elites':['mirelurkKing','deathclawAlpha','sporeBeast'],'boss':'deathclawAlpha',
  'themes':['cave','maritime','bunker','research','cliff','smuggler']},
 'geo_laciotat':{
  'label':'La Ciotat','bbox':[43.1250,5.5400,43.2550,5.7350],'tier':3,'faction':'rade',
  'anchors':[(43.1745,5.6045,'La Ciotat'),(43.1741,5.6080,'Vieux-Port'),(43.1766,5.6125,'Maison des Travailleurs'),(43.1781,5.6172,'Cale sèche'),(43.1792,5.6215,'Coque 27'),(43.1629,5.6090,'Mugel'),(43.1892,5.6320,'Saint-Jean'),(43.1990,5.6470,'Fontsainte')],
  'ecology':['smuggler','welder','dockOctopus','mirelurk','hermitCrab','robot','sirenAutomaton'],
  'elites':['mirelurkKing','sentryBot','hermitCrab'],'boss':'sirenAutomaton',
  'themes':['shipyard','maritime','industrial','submarine','hospital','warehouse']},
 'geo_frioul':{
  'label':'Archipel du Frioul','bbox':[43.2450,5.2550,43.3150,5.3500],'tier':4,'faction':'insulaires',
  'anchors':[(43.2791,5.3025,'Port Dieudonné'),(43.2801,5.2935,'Ratonneau'),(43.2627,5.2870,'Pomègues'),(43.2799,5.3251,'Château d’If'),(43.2846,5.2952,'Hôpital Caroline'),(43.2824,5.2818,'Morgiret'),(43.2555,5.2860,'Sémaphore de Pomègues')],
  'ecology':['feral','saltHound','mirelurk','radscorpion','concordeDrone','smuggler','bloatfly'],
  'elites':['mirelurkKing','alienInvader','sentryBot'],'boss':'mirelurkKing',
  'themes':['island','fort','hospital','bunker','maritime','quarantine']},
 'geo_etoile':{
  'label':'Étoile & Allauch','bbox':[43.3000,5.4350,43.4200,5.6000],'tier':2,'faction':'collines',
  'anchors':[(43.3353,5.4824,'Allauch'),(43.3470,5.4639,'Plan-de-Cuques'),(43.3540,5.4975,'Logis-Neuf'),(43.3825,5.5365,'Pichauris'),(43.3090,5.5155,'Éoures'),(43.3035,5.5167,'Les Camoins')],
  'ecology':['mistralCicada','mutantHound','yaoGuai','sanglier','raider','molerat','bloatfly'],
  'elites':['nightkin','quarryBeast','deathclawAlpha'],'boss':'yaoGuai',
  'themes':['forest','mill','bunker','rural','observatory','quarry']},
 'geo_saintebaume':{
  'label':'Sainte-Baume','bbox':[43.2150,5.5650,43.4100,5.7550],'tier':4,'faction':'vigies',
  'anchors':[(43.3490,5.6042,'Roquevaire'),(43.3719,5.6363,'Auriol'),(43.3755,5.6060,'La Destrousse'),(43.3850,5.5770,'Peypin'),(43.2695,5.6660,'Saint-Pons'),(43.2915,5.6750,'Col de l’Ange'),(43.2767,5.6992,'Cuges-les-Pins'),(43.2450,5.6630,'Grand Caunet')],
  'ecology':['deathclaw','radscorpion','nightkin','sporeBeast','tunneler','sanglier','quarryBeast'],
  'elites':['deathclawAlpha','radscorpionQueen','quarryBeast'],'boss':'radscorpionQueen',
  'themes':['abbey','forest','cave','quarry','bunker','observatory']},
}
COUNTS={'shelter':2,'settlement':3,'outpost':3,'interior':6,'nest':8,'elite':3,'boss':1,'landmark':3,'caravan':2}
KIND_ORDER=list(COUNTS)

SHELTERS=[
 ('A-11','La Voix des absents','Une IA doit déterminer quels habitants existent encore lorsque les registres se contredisent.'),
 ('M-08','Le Mistral captif','La ventilation alterne calme artificiel et bourrasques afin de mesurer l’obéissance collective.'),
 ('R-17','Deux noms pour une vie','Chaque résident reçoit deux identités administratives qui finissent par entrer en conflit.'),
 ('F-04','La Table commune','Les rations sont calculées par réputation plutôt que par besoin médical.'),
 ('C-22','Mémoire blanche','Les archives personnelles sont réécrites tous les sept ans.'),
 ('H-09','La Rivière fermée','L’accès à l’eau dépend d’un vote automatisé impossible à contester.'),
 ('S-31','Dernier soleil','Un cycle lumineux raccourci transforme la notion de jour et de travail.'),
 ('P-06','Les Héritiers','Les métiers sont attribués avant la naissance par prédiction statistique.'),
 ('D-14','Le Port intérieur','Une communauté maritime est enfermée sans jamais voir la mer.'),
 ('E-03','La Dette vivante','Chaque soin crée une dette transmissible aux descendants.'),
 ('G-25','Les Mille témoins','Toute décision nécessite un nombre croissant de signatures physiques.'),
 ('B-19','La Porte égale','Aucune porte ne peut rester ouverte plus longtemps pour une personne que pour une autre.'),
 ('T-02','Le Silence utile','Les annonces officielles remplacent peu à peu les conversations privées.'),
 ('V-27','La Saison fixe','Le climat reste artificiellement identique pendant plusieurs générations.'),
 ('L-12','La Liste parfaite','Le noyau supprime toute donnée qu’il ne parvient pas à classer.'),
 ('N-05','Les Jumeaux du réseau','Deux abris identiques reçoivent volontairement des informations contradictoires.'),
]

KIND_NAMES={
 'settlement':['Relais','Commune','Hameau','Cour des survivants','Marché protégé','Place des vivants'],
 'outpost':['Poste de veille','Barrage','Tour de garde','Atelier fortifié','Dépôt défensif'],
 'interior':['Sous-sol','Dépôt condamné','Galerie technique','Hôpital oublié','Station enterrée','Bunker civil','Carrière creuse','Archives murées'],
 'nest':['Nid irradié','Terrier','Zone de chasse','Fosse contaminée','Ruines infestées','Couloir de prédation'],
 'elite':['Repaire alpha','Territoire vétéran','Antre légendaire','Secteur rouge'],
 'boss':['Menace régionale'],
 'landmark':['Mémorial','Belvédère','Épave','Observatoire','Tour brisée','Jardin irradié'],
 'caravan':['Halte caravanière','Relais marchand','Camp de passage','Aire de ravitaillement'],
}
FACTION_NAMES={'ligue':'Ligue du Mistral','ateliers':'Ateliers libres','collines':'Vigies des Collines','vigies':'Veilleurs du relief','rade':'Communes de la Rade','insulaires':'Insulaires du Frioul'}
NPC_ROLES=['intendante','médecin itinérant','récupérateur','cartographe','vigie','mécanicienne','marchand','archiviste','éclaireuse','cultivatrice','radio-opérateur','soigneuse']


def stable_seed(*parts:str)->int:
 return int(hashlib.sha256('|'.join(parts).encode()).hexdigest()[:16],16)

def meters(a,b):
 lat=(a[0]+b[0])/2
 return math.hypot((a[0]-b[0])*110540,(a[1]-b[1])*111320*math.cos(math.radians(lat)))

def jitter(anchor,rng,min_m,max_m,bbox):
 for _ in range(80):
  r=rng.uniform(min_m,max_m);ang=rng.uniform(0,math.tau)
  lat=anchor[0]+math.sin(ang)*r/110540
  lon=anchor[1]+math.cos(ang)*r/(111320*math.cos(math.radians(anchor[0])))
  if bbox[0]+.001<lat<bbox[2]-.001 and bbox[1]+.001<lon<bbox[3]-.001:
   return round(lat,7),round(lon,7)
 return round(anchor[0],7),round(anchor[1],7)

RANGES={
 'shelter':(700,1800),'settlement':(100,650),'outpost':(450,1400),'interior':(250,1150),'nest':(650,2300),'elite':(1000,2800),'boss':(1400,3400),'landmark':(120,800),'caravan':(180,700)
}

sites=[]
shelter_idx=0
for macro,profile in MACROS.items():
 placed=[]
 for kind in KIND_ORDER:
  count=COUNTS[kind]
  for i in range(count):
   rng=random.Random(stable_seed('v042',macro,kind,str(i)))
   anchor=profile['anchors'][(i*3+KIND_ORDER.index(kind))%len(profile['anchors'])]
   min_m,max_m=RANGES[kind]
   # Major safe places stay closer to verified named anchors.
   if kind in {'settlement','caravan','landmark'}: min_m*=.45;max_m*=.75
   lat,lon=jitter(anchor,rng,min_m,max_m,profile['bbox'])
   # Avoid stacking generated sites.  Relax progressively in dense coastal macros.
   attempts=0
   while any(meters((lat,lon),(s['lat'],s['lon'])) < (180 if kind in {'nest','elite'} else 130) for s in placed) and attempts<40:
    lat,lon=jitter(anchor,rng,min_m,max_m,profile['bbox']);attempts+=1
   tier=max(1,min(5,profile['tier'] + (1 if kind in {'elite','boss'} else 0) + (i%3==2 and kind in {'interior','nest'})))
   site_id=f"v042-{macro.replace('geo_','')}-{kind}-{i+1:02d}"
   theme=profile['themes'][(i+KIND_ORDER.index(kind))%len(profile['themes'])]
   enemy_types=[profile['ecology'][(i+j)%len(profile['ecology'])] for j in range(3)]
   elite_type=profile['elites'][i%len(profile['elites'])]
   boss_type=profile['boss']
   faction=profile['faction'] if kind in {'settlement','outpost','caravan'} else ('concorde' if i%4==0 else 'hostile')
   safe=kind in {'settlement','caravan'}
   visitable=kind in {'shelter','interior'}
   if kind=='shelter':
    code,title,experiment=SHELTERS[shelter_idx];shelter_idx+=1
    name=f"Abri {code} · {title}";description=experiment;interior='shelter';unique=True
   elif kind=='boss':
    name=f"{KIND_NAMES[kind][0]} · {anchor[2]}";description=f"Une signature de niveau régional est installée près de {anchor[2]}.";interior=None;unique=True
   else:
    stem=KIND_NAMES[kind][i%len(KIND_NAMES[kind])]
    name=f"{stem} · {anchor[2]}";description=f"{stem} établi dans le secteur de {anchor[2]}, au cœur de {profile['label']}.";interior=theme if visitable else None;unique=kind in {'elite','landmark'}
   npc_slots={'settlement':4,'outpost':3,'caravan':2}.get(kind,0)
   enemy_slots={'nest':4+(i%2),'elite':5,'boss':7,'interior':3+(i%3),'shelter':4}.get(kind,0)
   site={
    'id':site_id,'macro':macro,'lat':lat,'lon':lon,'kind':kind,'name':name,'description':description,
    'anchor':anchor[2],'tier':int(tier),'faction':faction,'factionLabel':FACTION_NAMES.get(faction,faction.title()),
    'safe':safe,'visitable':visitable,'interior':interior,'theme':theme,'unique':unique,
    'discoverRadius':260 if safe or kind=='landmark' else 190,
    'activationRadius':850 if safe or visitable else 620,
    'enemyRadius':370 if kind in {'nest','elite','boss'} else 260,
    'npcSlots':npc_slots,'npcRoles':[NPC_ROLES[(i+j+KIND_ORDER.index(kind))%len(NPC_ROLES)] for j in range(npc_slots)],
    'enemySlots':enemy_slots,'enemyTypes':enemy_types,'eliteType':elite_type,'bossType':boss_type,
    'rewardCaps':20+tier*14+(80 if kind=='boss' else 35 if kind=='elite' else 0),
    'rewardXP':25+tier*20+(160 if kind=='boss' else 70 if kind=='elite' else 0),
    'respawnHours':0 if unique or visitable else 72,
    'icon':{'shelter':'vault','settlement':'home','outpost':'guard','interior':'door','nest':'skull','elite':'star','boss':'crown','landmark':'pin','caravan':'trade'}[kind],
   }
   sites.append(site);placed.append(site)

meta={
 'version':'0.42.0','seed':'fallout-mistral-v042','siteCount':len(sites),'macroCount':len(MACROS),
 'counts':{k:sum(1 for s in sites if s['kind']==k) for k in COUNTS},
 'visitable':sum(1 for s in sites if s['visitable']),
 'hostileSites':sum(1 for s in sites if s['kind'] in {'nest','elite','boss'}),
 'npcSlots':sum(s['npcSlots'] for s in sites),
 'enemySlots':sum(s['enemySlots'] for s in sites),
 'macroCounts':{m:sum(1 for s in sites if s['macro']==m) for m in MACROS},
 'generatedWith':'tools/build_fallout_layer_v042.py',
}

# Validation
errors=[]
for s in sites:
 b=MACROS[s['macro']]['bbox']
 if not (b[0] <= s['lat'] <= b[2] and b[1] <= s['lon'] <= b[3]):errors.append(f"outside:{s['id']}")
 if s['tier'] not in range(1,6):errors.append(f"tier:{s['id']}")
for m in MACROS:
 kinds={s['kind'] for s in sites if s['macro']==m}
 if kinds!=set(COUNTS):errors.append(f"kinds:{m}:{sorted(kinds)}")
 if sum(1 for s in sites if s['macro']==m)!=31:errors.append(f"count:{m}")
ids=[s['id'] for s in sites]
if len(ids)!=len(set(ids)):errors.append('duplicate_ids')
meta['validation']={'ok':not errors,'errors':errors}
if errors: raise SystemExit(errors)

payload={'meta':meta,'macros':{k:{x:v[x] for x in ('label','bbox','tier','faction','ecology','elites','boss','themes')} for k,v in MACROS.items()},'sites':sites}
OUT_JSON.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
js='/* Generated by tools/build_fallout_layer_v042.py. */\nconst V042_LAYER_META='+json.dumps(meta,ensure_ascii=False,separators=(',',':'))+';\nconst V042_MACRO_PROFILES='+json.dumps(payload['macros'],ensure_ascii=False,separators=(',',':'))+';\nconst V042_CATALOG='+json.dumps(sites,ensure_ascii=False,separators=(',',':'))+';\n'
OUT_JS.write_text(js,encoding='utf-8')
# Audit summary includes distribution and spacing evidence.
spacing={}
for m in MACROS:
 ms=[s for s in sites if s['macro']==m];mins=[]
 for i,a in enumerate(ms):
  for b in ms[i+1:]:mins.append(meters((a['lat'],a['lon']),(b['lat'],b['lon'])))
 spacing[m]=round(min(mins),1) if mins else None
audit={'meta':meta,'spacingMinMeters':spacing,'siteExamples':sites[:12],'sha256':hashlib.sha256(OUT_JSON.read_bytes()).hexdigest()}
OUT_AUDIT.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(meta,ensure_ascii=False,indent=2))
