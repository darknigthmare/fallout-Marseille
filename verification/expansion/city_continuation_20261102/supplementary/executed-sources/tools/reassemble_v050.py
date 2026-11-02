#!/usr/bin/env python3
"""Reassemble the v0.50 full ZIP from verified local parts, without downloading."""
from pathlib import Path, PurePosixPath
import hashlib
import json
import os
import sys
import tempfile
import zipfile

ARCHIVE = 'FALLOUT_MISTRAL_v0.50_PROJET_COMPLET.zip'
BLOCK = 1024 * 1024


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(BLOCK), b''):
            digest.update(block)
    return digest.hexdigest()


def main():
    folder = Path(__file__).resolve().parent
    manifest = json.loads((folder / 'ARCHIVE_PARTS.json').read_text(encoding='utf-8'))
    archive = manifest['archive']
    if archive['name'] != ARCHIVE or not isinstance(archive['bytes'], int):
        raise ValueError('Le manifeste ne correspond pas au projet complet v0.50.')
    parts = manifest['parts']
    expected_names = [ARCHIVE + f'.{i:03d}' for i in range(1, len(parts) + 1)]
    if not parts or [part['name'] for part in parts] != expected_names:
        raise ValueError('La liste des parties est invalide ou désordonnée.')
    if sum(part['bytes'] for part in parts) != archive['bytes']:
        raise ValueError('Les tailles des parties ne correspondent pas au ZIP final.')
    target = folder / ARCHIVE
    if target.exists():
        if target.is_file() and target.stat().st_size == archive['bytes'] and sha(target) == archive['sha256']:
            print('Archive déjà présente et vérifiée :', target.name)
            return
        raise RuntimeError('Un fichier différent porte déjà le nom du ZIP final. Aucun écrasement effectué.')
    for part in parts:
        path = folder / part['name']
        if not path.is_file() or path.stat().st_size != part['bytes'] or sha(path) != part['sha256']:
            raise RuntimeError('Partie manquante, incomplète ou altérée : ' + part['name'])
        print('Partie vérifiée :', part['name'], flush=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=folder, prefix=ARCHIVE + '.', suffix='.reconstruction.tmp', delete=False) as out:
            temporary = Path(out.name)
            digest = hashlib.sha256()
            total = 0
            for part in parts:
                with (folder / part['name']).open('rb') as source:
                    for block in iter(lambda: source.read(BLOCK), b''):
                        out.write(block)
                        digest.update(block)
                        total += len(block)
        if total != archive['bytes'] or digest.hexdigest() != archive['sha256']:
            raise RuntimeError('L’empreinte du ZIP reconstitué ne correspond pas au manifeste.')
        with zipfile.ZipFile(temporary) as bundle:
            if bundle.testzip() is not None:
                raise RuntimeError('Le contrôle interne du ZIP a échoué.')
            if any(n.startswith(('/', '\\')) or '\\' in n or '..' in PurePosixPath(n).parts for n in bundle.namelist()):
                raise RuntimeError('Un chemin du ZIP est invalide.')
        # Exclusive creation preserves an existing file even if it appeared meanwhile.
        try:
            with target.open('xb') as out, temporary.open('rb') as source:
                for block in iter(lambda: source.read(BLOCK), b''):
                    out.write(block)
        except FileExistsError:
            raise RuntimeError('Un ZIP est apparu pendant la recomposition. Aucun écrasement effectué.')
        except OSError:
            target.unlink(missing_ok=True)
            raise
        print('Archive complète reconstituée et vérifiée :', target.name)
        print('Extrayez-la, puis ouvrez le lanceur LANCER_APP de votre système.')
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, zipfile.BadZipFile) as error:
        print('Erreur :', error, file=sys.stderr)
        sys.exit(1)
