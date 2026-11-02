"""Package the tested files, not a rebuilt/different program."""
from pathlib import Path
import hashlib,json,zipfile,shutil
R=Path(__file__).resolve().parents[1];P=R.parent;V=R/'verification'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
qa=json.loads((V/'QA_GLOBAL_V030.json').read_text());cap=json.loads((V/'CAPTURES_V030.json').read_text());h=R/'JOUER_FALLOUT_MISTRAL_v0.30.html'
assert qa['failed']==0 and not qa['errors'] and qa['same_html'] and qa['html_sha256']==sha(h)==cap['html_sha256'] and not cap['errors']
# Remove developer-only probes and cache files; evidence of executed final suites stays.
for pat in ['smoke*','probe*','*_FAILURE.png','*.pid']:
 for p in V.glob(pat):p.unlink()
for p in R.rglob('__pycache__'):shutil.rmtree(p)
for fn in ['smoke_v030.py','probe_trade_v030.py']:(R/'tools'/fn).unlink(missing_ok=True)
summary={'version':'0.30.0','title':'Sous la cuirasse','html_sha256':sha(h),'html_bytes':h.stat().st_size,'qa':qa['total'],'passed':qa['passed'],'failed':qa['failed'],'new_tests':qa['new'],'retained_tests':qa['retained'],'screenshots':len(cap['images']),'official_geodata_files':0,'base_archive_sha256':json.loads((R/'data/BASE_V029.json').read_text())['archive_sha256']}
(R/'data/BUILD_V030.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
(R/'docs/RAPPORT_QA.md').write_text(f'''# Rapport QA — v0.30 « Sous la cuirasse »

## Build réellement exécutée
SHA-256 : `{sha(h)}`. Taille : {h.stat().st_size:,} octets.

**{qa['passed']} contrôles ciblés réussis sur {qa['total']}**, {qa['failed']} échec, aucune exception JavaScript remontée. {qa['retained']} régressions et {qa['new']} contrôles nouveaux, {qa['suites']} suites/reports. Chaque résultat est recalculé sur le même HTML, pas repris d’un ancien bilan.

## Couverture
Les suites héritées chargent individuellement les 86 configurations historiques et vérifient le socle des inventaires, dialogues, enquêtes, soins, plans, tir et V.A.T.S. Les nouveaux essais vérifient les six plaques, les coûts de réparation, la charge réelle, éjection/réinsertion sans création, saturation/déplétion, mouvement bloqué et effectif, saut, tirs émis ou annulés, réglages, reventes et métadonnées d’occasion.

La quête est parcourue par ses dialogues et prérequis physiques : escalier de la galerie, actionneur, cahier, consignation, devis, châssis, cellule, puis portillon manuel. Le point de contrôle réellement atteint est réimporté pour le chemin motorisé et la seconde conclusion. Les récompenses et six scènes d’épilogue sont vérifiées. Les marches au contrôleur sont distinguées des approches directement préparées.

Le test tactile emploie de vrais gestes `tap`, dans une fenêtre de 390 × 844. Les pièces suivent le phosphore, les commandes manipulent la charge et le HUD n’empiète pas sur le suivi de quête. L’export JSON a réellement produit un téléchargement.

## Adaptations et correctifs
Les tests historiques ont changé de fichier d’entrée, de titre et de clés attendues ; le nombre d’espaces aux amarres devient onze, puisqu’une vraie baie y a été ajoutée. Voir `data/ADAPTATION_TESTS_V030.json`. Les assertions de gameplay n’ont pas été remplacées par des compteurs de contenu.

La passe a notamment corrigé le contournement du verrou d’armure via l’ancien sac, l’ancien entretien moyen qui nivelait les six pièces, le chevauchement du HUD et des suivis, le retour à la ligne du pourcentage et le support de certains objets de quête. Les tests conservent les contrôles sur ces points.

## Limites des preuves
Chromium logiciel, HTML exact via set_content. Navigation fichier/serveur bloquée dans l’environnement administré. Le refus du stockage natif opaque est vérifié avant l’installation déclarée d’un stockage mémoire pour les scénarios d’écriture réussie. Ni GPU matériel ni iPhone réel ni parcours humain intégral ne sont certifiés.

Les essais isolés de combat utilisent une arène marquée synthétique. Les captures visuelles sont prises dans les vrais lieux fictifs du jeu, avec caméras et quelques états préparés, pas dans une commune réelle. Aucune géographie officielle importée.

Les vérifications supplémentaires de paquet figurent dans le fichier `FALLOUT_MISTRAL_v0.30_CONTROLES_LIVRAISON.json` fourni à côté des ZIP.
''')
(V/'README.md').write_text('Les 22 captures décrites dans CAPTURES_V030.json proviennent du même HTML que les suites. Les autres résultats/sous-rapports sont les preuves de test. Les noms de suites anciennes désignent le socle testé, pas une ancienne build exécutée. Les fixtures synthétiques de combat ne sont pas des données réelles.\n')
files=sorted(p for p in R.rglob('*')if p.is_file() and p.name!='MANIFEST_SHA256.json' and p.suffix not in ['.pyc','.zip'] and '__pycache__'not in p.parts)
manifest={'version':'0.30.0','hash':'sha256','excludes':['MANIFEST_SHA256.json lui-même'],'files':[{'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in files]}
(R/'MANIFEST_SHA256.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
full=P/'FALLOUT_MISTRAL_v0.30_PROJET_COMPLET.zip'
with zipfile.ZipFile(full,'w',zipfile.ZIP_DEFLATED,compresslevel=7)as z:
 for p in files+[R/'MANIFEST_SHA256.json']:z.write(p,arcname=(Path(R.name)/p.relative_to(R)).as_posix())
selected=[h,R/'README_FR.md',R/'LANCER_JEU.bat',R/'LANCER_JEU.sh',R/'RAPPORT_VISUEL_V0.30.png',R/'docs/CONTROLES.md',R/'docs/CONTENU_V0.30.md',R/'docs/STATUT_PRODUCTION.md',R/'docs/MIGRATION_V029_V030.md',R/'docs/RAPPORT_QA.md']
small_manifest={'files':[{'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in selected]}
with zipfile.ZipFile(P/'FALLOUT_MISTRAL_v0.30_JEU_SEUL.zip','w',zipfile.ZIP_DEFLATED,compresslevel=7)as z:
 for p in selected:z.write(p,arcname=p.relative_to(R).as_posix())
 z.writestr('MANIFEST_SHA256.json',json.dumps(small_manifest,ensure_ascii=False,indent=2))
items=[h,P/'FALLOUT_MISTRAL_v0.30_JEU_SEUL.zip',full,R/'RAPPORT_VISUEL_V0.30.png',R/'RAPPORT_VISUEL_V0.30.html']
(P/'FALLOUT_MISTRAL_v0.30_CHECKSUMS.txt').write_text('\n'.join(sha(p)+'  '+p.name for p in items)+'\n')
print(json.dumps({'files':len(files),'artifacts':[{p.name:p.stat().st_size}for p in items]},indent=2))
