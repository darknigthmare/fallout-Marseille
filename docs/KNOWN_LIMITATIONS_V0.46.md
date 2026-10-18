# Limites explicites

1. Le programme est complet, mais le pack cartographique réel intégral n’est pas livré. L’extérieur réel exige les données requises et peut rester sur l’écran d’erreur si le cache distant ou le pack local sont absents.
2. Le réseau externe du runtime ne résout pas les serveurs cartographiques. Aucun téléchargement exhaustif ni audit commune par commune n’a été réalisé.
3. Le banc de continuité utilise des coordonnées de frontière mais une géométrie synthétique. Il prouve le comportement du pipeline, pas la fidélité de Marseille.
4. Le passage par une limite de région conserve la scène. Une extension du périmètre préparé peut provoquer un chargement volontaire et une pause.
5. Les chemins routiers et bâtiments sont importés depuis leurs sources disponibles. L’accessibilité de chaque tunnel, escalier ou parcelle n’a pas été vérifiée humainement.
6. Les hauteurs non documentées sont estimées ; le raster IGN natif complet n’est pas inclus.
7. Les modèles et intérieurs restent majoritairement procéduraux. La couche narrative est une reconstruction depuis la v0.42, pas la restauration exacte de la v0.44.
8. Tests exécutés dans Chromium avec HTML chargé par `set_content`, l’environnement bloquant la navigation Chromium vers localhost. Aucun essai matériel Windows/GPU/mobile ni enregistrement natif de service worker n’est revendiqué.
