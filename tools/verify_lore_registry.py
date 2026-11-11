#!/usr/bin/env python3
"""Check the material traceability of Mistral lore; does not certify narrative canon.

No network, third-party modules or game execution. Every current 10*.js module must
belong to exactly one declared arc; each arc has a model, a logic test and chapters
linked from both the central bible and the reader-facing index.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
from urllib.parse import unquote

REGISTRY = 'docs/REGISTRE_LORE.json'
BIBLE = 'docs/BIBLE_LORE_FALLOUT_MISTRAL.md'
INDEX = 'LORE.md'


def inspect_registry(root: Path, registry: dict | None = None, bundle: str | None = None) -> dict:
    root = root.resolve()
    errors: list[str] = []
    fingerprints: dict[str, str] = {}

    def read(name: object) -> str:
        if not isinstance(name, str) or not name or '\\' in name or '://' in name:
            errors.append(f'invalid path: {name!r}')
            return ''
        rel = PurePosixPath(name)
        p = (root / name).resolve()
        if rel.is_absolute() or '..' in rel.parts or not p.is_relative_to(root):
            errors.append(f'path outside repository: {name}')
            return ''
        try:
            raw = p.read_bytes()
            text = raw.decode('utf-8')
        except (OSError, UnicodeError) as exc:
            errors.append(f'unreadable {name}: {exc}')
            return ''
        if not text.strip():
            errors.append(f'empty file: {name}')
        fingerprints[name] = hashlib.sha256(raw).hexdigest()
        return text

    def links(name: str, text: str) -> set[Path]:
        targets: set[Path] = set()
        for token in re.findall(r'\[[^\]]*\]\(([^)\s]+)', text):
            token = unquote(token.split('#', 1)[0])
            if token and not re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', token):
                targets.add((root / name).parent.joinpath(token).resolve())
        return targets

    if registry is None:
        text = read(REGISTRY)
        try:
            registry = json.loads(text)
        except (ValueError, TypeError):
            registry = None
    if not isinstance(registry, dict) or registry.get('schema') != 1:
        return {'ok': False, 'errors': errors + ['unsupported or missing registry schema'], 'sha256': fingerprints}
    if registry.get('canon') != 'fan-lore-original-non-officiel' or registry.get('narrative_year') != 2297:
        errors.append('canon qualifier or narrative year changed; review required')
    if not isinstance(registry.get('scope'), str) or not registry['scope'].strip():
        errors.append('missing scope boundary')
    entries = registry.get('entries')
    if not isinstance(entries, list) or not entries:
        return {'ok': False, 'errors': errors + ['empty entries'], 'sha256': fingerprints}
    bible = read(BIBLE)
    index = read(INDEX)
    bible_links, index_links = links(BIBLE, bible), links(INDEX, index)
    if (root / REGISTRY).resolve() not in bible_links or (root / REGISTRY).resolve() not in index_links:
        errors.append('registry must be linked from bible and index')
    if '2297' not in bible or 'création de fan non officielle' not in bible:
        errors.append('central bible must retain period and unofficial fan-work qualifier')
    ids: set[str] = set()
    modules: set[str] = set()
    chapters: set[str] = set()
    model_names: set[str] = set()
    built = read(bundle) if bundle else None
    for entry in entries:
        if not isinstance(entry, dict):
            errors.append('entry must be an object')
            continue
        key = entry.get('id')
        if not isinstance(key, str) or not re.fullmatch(r'[a-z][a-z0-9-]*', key) or key in ids:
            errors.append(f'invalid or duplicate id: {key!r}')
        else:
            ids.add(key)
        for field in ('title', 'delivered', 'open_limit'):
            if not isinstance(entry.get(field), str) or not entry[field].strip():
                errors.append(f'{key}: missing {field}')
        if entry.get('status') != 'implemented-local-scope':
            errors.append(f'{key}: undocumented status')
        model = entry.get('model')
        if not isinstance(model, str) or not re.fullmatch(r'Mistral[A-Za-z0-9_]+', model) or model in model_names:
            errors.append(f'{key}: invalid or duplicate model')
            model = None
        else:
            model_names.add(model)
        source_list = entry.get('sources')
        texts = []
        if not isinstance(source_list, list) or not source_list:
            errors.append(f'{key}: no source modules')
            source_list = []
        for path in source_list:
            text = read(path)
            texts.append(text)
            if not isinstance(path, str) or not re.fullmatch(r'src/v050/10[^/]*\.js', path):
                errors.append(f'{key}: source outside declared narrative scope')
            elif path in modules:
                errors.append(f'{key}: duplicate module {path}')
            else:
                modules.add(path)
        if model:
            pattern = r'\bconst\s+' + re.escape(model) + r'\s*='
            if not any(re.search(pattern, t) for t in texts):
                errors.append(f'{key}: model declaration not found in sources')
            if built is not None and not re.search(pattern, built):
                errors.append(f'{key}: model missing from compiled bundle')
        docs = entry.get('chapters')
        if not isinstance(docs, list) or not docs:
            errors.append(f'{key}: no chapters')
            docs = []
        for doc in docs:
            read(doc)
            if not isinstance(doc, str) or not re.fullmatch(r'docs/LORE_[A-Z0-9_]+\.md', doc):
                errors.append(f'{key}: invalid chapter path')
                continue
            if doc in chapters:
                errors.append(f'{key}: chapter has more than one owning arc: {doc}')
            chapters.add(doc)
            target = (root / doc).resolve()
            if target not in bible_links:
                errors.append(f'{key}: chapter not linked from central bible: {doc}')
            if target not in index_links:
                errors.append(f'{key}: chapter not linked from LORE.md: {doc}')
        test = entry.get('logic_test')
        read(test)
        if not isinstance(test, str) or not re.fullmatch(r'tests/expansion/lore_[a-z0-9_]+\.cjs', test):
            errors.append(f'{key}: missing scoped logic test')
    actual = {p.relative_to(root).as_posix() for p in (root / 'src/v050').glob('10*.js')}
    for missing in sorted(actual - modules):
        errors.append(f'undocumented narrative module: {missing}')
    for missing in sorted(modules - actual):
        errors.append(f'declared module absent: {missing}')
    return {'ok': not errors, 'scope': registry.get('scope'), 'entries': len(ids),
            'narrative_modules': len(modules), 'chapters': len(chapters),
            'bundle_checked': bundle, 'errors': errors, 'sha256': dict(sorted(fingerprints.items())),
            'limits': 'Structural traceability, not semantic canon validation, gameplay completion, deployment or exhaustive weapon/creature coverage.'}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument('--bundle', help='Optional compiled game path relative to root')
    p.add_argument('--output', type=Path, help='Write JSON evidence (in addition to stdout)')
    args = p.parse_args()
    report = inspect_registry(args.root, bundle=args.bundle)
    text = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    print(text, end='')
    return 0 if report['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
