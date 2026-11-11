from pathlib import Path
import hashlib
b=Path('docs/BIBLE_LORE_FALLOUT_MISTRAL.md')
assert hashlib.sha256(b.read_bytes()).hexdigest()=='a25ba015b7ef442e1cf7b803d80d4a98698355a97e4280ba9952c8c01a7e969e'
s=b.read_text()
a='Le Rat-couronné, le Roi des Égouts, Midi-Zéro, le Général Biset et les espèces annoncées gardent un statut documentaire tant que leurs propres systèmes ne sont pas vérifiés.'
z='Le Rat-couronné possède déjà un assemblage régional, des volumes ciblables et une ruée sur le type existant `giantRat`, décrits dans [BESTIAIRE_REGIONAL.md](BESTIAIRE_REGIONAL.md). Il ne doit donc pas être reclassé comme entièrement absent. Cet assemblage quadrupède ne réalise toutefois pas l’agrégat de plusieurs individus décrit en section 30 : cet écart de représentation reste ouvert. Le Roi des Égouts, Midi-Zéro, le Général Biset et les autres formes annoncées ne deviennent pas jouables par simple présence dans une liste.'
assert s.count(a)==1
s=s.replace(a,z);b.write_text(s)
audit=Path('docs/AUDIT_BIBLE_2026_11_11.md')
s=audit.read_text();s+='\n## Précision de lecture du bestiaire\n\nLe chapitre `BESTIAIRE_REGIONAL.md` et `src/v050/13_regional_bestiary.js` décrivent déjà le Rat-couronné sur `giantRat`, avec silhouette, volumes ciblables et attaque. La consolidation ne le classe donc pas parmi les espèces entièrement absentes. Sa représentation actuelle demeure différente de l’agrégat conçu en section 30 ; aucune transformation graphique n’est inventée pour combler cet écart. Cette précision documentaire ne modifie pas les statistiques, les apparitions ou les sauvegardes. Le registre des vingt ensembles couvre les modules narratifs `10*.js`, pas l’inventaire intégral du module de bestiaire 13.\n';audit.write_text(s)
r=Path('README.md');s=r.read_text();header='# FALLOUT Marseille — MISTRAL\n';assert s.startswith(header)
intro='\n## Bible et progression narrative — 11 novembre 2026\n\nLa [bible centrale consolidée](docs/BIBLE_LORE_FALLOUT_MISTRAL.md), l’[index des chapitres](LORE.md) et le [registre vérifiable des modules narratifs](docs/REGISTRE_LORE.json) rassemblent les ajouts jusqu’à **Une place dans la cour**. Le [suivi des manques](docs/ETAT_LORE_MANQUANTS.md) conserve les concepts non incarnés ; aucune faction entière ou validation IGN complète n’est déclarée terminée. Les résultats courants se trouvent dans [le rapport de compilation et de parcours](verification/bible-sync/QA.json) et [le contrôle documentaire actualisé](verification/bible-sync/DOCUMENTATION_REVIEW.json). Les bilans plus anciens ci-dessous restent historiques.\n'
r.write_text(header+intro+s[len(header):])
print('Clarified existing rat-couronne representation and linked the current bible from README. No game files changed.')
