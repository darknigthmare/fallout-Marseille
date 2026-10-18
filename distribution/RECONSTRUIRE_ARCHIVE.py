#!/usr/bin/env python3
"""Reconstitue et verifie l'archive v0.49 sans telechargement ni ecrasement."""
from pathlib import Path
import hashlib
import json
import os
import sys
import tempfile
import zipfile

ARCHIVE = 'FALLOUT_MISTRAL_v0.49_PROJET_COMPLET.zip'
EXPECTED_SHA256 = '172783f2026a1b8537b45a3b91df89bcd6afe425ade8613bb0210aff2ed6477c'
CHUNK = 1024 * 1024


def sha256(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(CHUNK), b''):
            value.update(block)
    return value.hexdigest()


def main():
    folder = Path(__file__).resolve().parent
    target = folder / ARCHIVE
    if target.exists():
        if target.is_file() and sha256(target) == EXPECTED_SHA256:
            print('Archive deja presente et verifiee :', target.name)
            return
        raise RuntimeError('Un fichier different porte deja le nom du ZIP final. Aucun ecrasement effectue.')
    manifest = json.loads((folder / 'ARCHIVE_PARTS.json').read_text(encoding='utf-8'))
    names = [ARCHIVE + '.001', ARCHIVE + '.002']
    if manifest['archive']['name'] != ARCHIVE or manifest['archive']['sha256'] != EXPECTED_SHA256:
        raise RuntimeError('Le manifeste ne correspond pas a cette livraison.')
    if [part['name'] for part in manifest['parts']] != names:
        raise RuntimeError('La liste des deux parties ne correspond pas a cette livraison.')
    for part in manifest['parts']:
        path = folder / part['name']
        if not path.is_file():
            raise RuntimeError('Partie manquante : ' + part['name'])
        if path.stat().st_size != part['bytes'] or sha256(path) != part['sha256']:
            raise RuntimeError('Partie incomplete ou alteree : ' + part['name'])
        print('Partie verifiee :', part['name'])
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=folder, prefix=ARCHIVE + '.', suffix='.reconstruction.tmp', delete=False) as out:
            temporary = Path(out.name)
            digest = hashlib.sha256()
            total = 0
            for name in names:
                with (folder / name).open('rb') as stream:
                    for block in iter(lambda: stream.read(CHUNK), b''):
                        out.write(block)
                        digest.update(block)
                        total += len(block)
        if total != manifest['archive']['bytes'] or digest.hexdigest() != EXPECTED_SHA256:
            raise RuntimeError('La verification du ZIP reconstitue a echoue.')
        with zipfile.ZipFile(temporary) as archive:
            if archive.testzip() is not None:
                raise RuntimeError('Le controle interne du ZIP a echoue.')
        if target.exists():
            raise RuntimeError('Un ZIP est apparu pendant la recomposition. Aucun ecrasement effectue.')
        os.rename(temporary, target)
        temporary = None
        print('Archive complete reconstituee et verifiee :', target.name)
        print('Extrayez le ZIP, puis lancez LANCER_APP_WINDOWS.bat ou le lanceur Linux/macOS.')
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, RuntimeError, zipfile.BadZipFile) as error:
        print('Erreur :', error, file=sys.stderr)
        sys.exit(1)
