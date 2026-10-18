# Fallout : Mistral v0.38 — Cadastre complet

## Résultat principal
La totalité du manifeste vectoriel est présente dans le cache territorial : 367 coordonnées de fond et 5 517 coordonnées cadastrales. Le cadastre se compose de 4 190 PBF contenant des entités et de 1 327 réponses officielles HTTP 204 sans contenu.

## Relais v0.38
Le nouveau relais sert uniquement les entrées déjà archivées. Il ne télécharge pas arbitrairement une URL fournie par le client. Une tuile vide renvoie un corps de zéro octet, `X-Map-Empty: 1` et le SHA-256 du contenu vide.

## Moteur
Ordre de résolution : pack disque, IndexedDB, cache territorial v0.38, puis source directe si la configuration l'autorise. L'interface distingue coordonnées, PBF, réponses vides, mémoire locale et relief.

## Installation hors ligne
L'installateur comprend les réponses vides et crée un marqueur `.empty.json`. L'auditeur refuse un fichier de zéro octet sans cette preuve.

## Ce qui reste
Le relief numérique officiel est toujours absent. La complétude du cache ne constitue pas une certification visuelle et topologique de toute la région. Les bâtiments coupés, portes d'intérieurs, littoral, performances et traversées longues restent à contrôler.
