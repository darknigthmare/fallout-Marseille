# Supabase — cache cartographique v0.37

Le dossier contient le contrat SQL et la source de l’Edge Function déployée.

- table technique RLS, sans droit anon/authenticated ;
- bucket privé limité à 8 Mo ;
- Edge Function avec JWT/publishable key ;
- aucun secret service-role dans le client du jeu.

Le fichier SQL est un contrat de reproduction, pas la preuve qu’une migration a été appliquée dans un autre projet.
