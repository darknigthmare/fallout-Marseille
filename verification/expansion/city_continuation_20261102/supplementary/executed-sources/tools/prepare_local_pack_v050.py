"""Prepare the verified, bundled geography before starting the local game.

This helper only extracts archives already shipped with the repository. It
never turns a game launch into an implicit network installation.
"""
from pathlib import Path
import json
import subprocess
import sys


def needs_preparation(root: Path) -> bool:
    pack = root / 'data/map_pack'
    manifest = json.loads((pack / 'manifest_v038.json').read_text(encoding='utf-8'))
    for row in manifest['tiles']:
        path = root / row['local']
        if not path.is_file():
            return True
        if path.stat().st_size == 0 and not path.with_suffix(path.suffix + '.empty.json').is_file():
            return True
    terrain = json.loads((pack / 'terrain/manifest_v039.json').read_text(encoding='utf-8'))
    return any(not (pack / 'terrain' / (region['macro'] + '.json')).is_file() for region in terrain['regions'])


def prepare_if_bundled(root: Path) -> bool:
    """Return whether files are ready, preserving a playable menu on failure."""
    try:
        if not needs_preparation(root):
            return True
        if not (root / 'data/map_pack/archives/manifest.json').is_file():
            return False
        print('Préparation des cartes fournies avec le jeu… Aucun téléchargement.', flush=True)
        result = subprocess.run(
            [sys.executable, str(root / 'tools/install_local_pack_v041.py'),
             '--offline', '--workers', '3'], cwd=root, check=False
        )
        if result.returncode == 0:
            return True
        print('La préparation est incomplète. Consultez Cartes & territoire dans le menu.', flush=True)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f'Préparation locale indisponible : {error}', flush=True)
    return False


if __name__ == '__main__':
    raise SystemExit(0 if prepare_if_bundled(Path(__file__).resolve().parents[1]) else 1)
