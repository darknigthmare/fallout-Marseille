# Lancer v0.48

Décompresser l’archive entière. Sous Windows, utiliser `LANCER_APP_WINDOWS.bat`. Sous Linux/macOS, employer le lanceur local correspondant. Le HTML `JOUER_FALLOUT_MISTRAL_v0.48.html` est également autonome.

Le projet complet se reconstruit par `python3 tools/build_single.py`. `npm run qa` lance les contrôles inclus ; Chromium et Playwright sont requis pour les scénarios navigateur. Les tests purs utilisent Node.

Ctrl + Maj + F9 ouvre le banc synthétique ; le retour se fait par le contrôle de sortie du banc et restaure la campagne précédente. Ce banc n’est pas la carte réelle.

Le pack cartographique lourd n’est pas inclus. Les outils historiques d’installation sont conservés mais aucun service distant n’est annoncé comme opérationnel sans vérification actuelle.
