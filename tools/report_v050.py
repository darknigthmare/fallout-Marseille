#!/usr/bin/env python3
"""Build the v0.50 evidence summary and two standalone visual reports.

This command does not start a browser or run the game. It validates the saved
test results, source HTML and original screenshot hashes before publishing any
aggregate. The travel fixture's hash is reconstructed from its literal private
inspector; it is not confused with the canonical, unmodified release HTML.

Requires Pillow. Run from the complete project:
    python3 tools/report_v050.py
"""
from pathlib import Path
import argparse
import ast
import base64
import hashlib
import html
import io
import json
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.50.0"
EXPECTED_HTML = "ac473edc0ecd222db0ed0dd3b29f30b245dfb2f27a967c7d588a200b11d784e5"
DRIVE = "https://drive.google.com/drive/folders/1xE5VpELY64tz5GV9CHHrlsIb_rfahRnQ"
GITHUB = "https://github.com/darknigthmare/fallout-Marseille"
EXPECTED = {
    "NATIVE_REAL_MAP.json": 83,
    "QA_POI_TRAVEL.json": 36,
    "QA_CAMPAIGN_MAP.json": 41,
    "QA_CONTINUE_SAVE.json": 18,
    "QA_LEGACY.json": 434,
}
SCOPES = {
    "NATIVE_REAL_MAP.json": "HTTP, stockage Chromium et cartes locales réels ; assistance par API de diagnostic existantes, sans injection HTML.",
    "QA_POI_TRAVEL.json": "HTML instrumenté, banc synthétique identifié, stockage et réseau contrôlés ; erreurs de trajet provoquées.",
    "QA_CAMPAIGN_MAP.json": "Vraies cartes locales et adaptateur privé de test pour les échecs, réessais, annulations et changements de contexte.",
    "QA_CONTINUE_SAVE.json": "Chromium et localStorage natifs ; sauvegardes datées préparées par un adaptateur privé ; bouton et chargeur de production.",
    "QA_LEGACY.json": "Contrats historiques adaptés au produit actuel ; bancs synthétiques et réseau contrôlé.",
    "QA_INSTALLERS.json": "Cas unitaires sur fixtures : intégrité ZIP/PBF, transport gzip borné, HTTP borné, réponses vides attestées, reprise et conservation sur échec.",
}


def score_groups(aggregate):
    counts = aggregate["countsByScope"]
    return [
        ("Parcours natif", counts["native"], "HTTP et stockage réels"),
        ("Contrats ciblés", counts["targeted"], "36 voyage · 41 campagne · 18 reprise"),
        ("Installateurs", counts["installers"], "Cas unitaires sur fixtures"),
        ("Contrats hérités", counts["inherited"], "Régressions du programme"),
    ]


SECTIONS = [
    {
        "title": "01 · Un territoire relié à la campagne",
        "intro": "Le sas charge les fichiers géographiques d’Aubagne avant de terminer le prologue. Une balise physique relie cet extérieur aux ateliers ; le retour conserve le point de départ et les acquis de la campagne.",
        "cards": [
            ("native_07_real_aubagne.png", "SORTIE DU SAS", "Une arrivée dégagée sur le vrai relief",
             "Vecteurs du pack local. Sol mesuré à 105,08 m ; œil à +1,65 m. Arrivée hors collision, balise des ateliers visible."),
            ("native_07c_narrative_workshops.png", "ATELIERS D’AUBAGNE", "Une scène narrative annoncée",
             "Le décor des ateliers est une création du jeu. Mireille reste accessible ; son dialogue atteint l’étape 3, puis le retour restaure le point géographique."),
        ],
    },
    {
        "title": "02 · Des tuiles qui changent, une scène qui tient",
        "intro": "Franchissement physique de 28,06 m, aller et retour, sur une frontière cadastrale réelle. Une demande de fenêtre anticipée assistée au diagnostic publie les vrais fichiers voisins ; les routes et bâtiments communs gardent exactement leur géométrie.",
        "cards": [
            ("native_08_day_road.png", "12 H · JOUR", "La frontière cadastrale, côté rue",
             "À l’aller : 42 → 34 tuiles, 8 retraits. Identité de scène conservée ; 8 728 bâtiments et 3 070 routes communes inchangés."),
            ("native_09_night_road.png", "21 H · NUIT", "Le même point et le même cadrage",
             "Au retour : 8 tuiles ajoutées, 8 retirées. Aucun changement des 8 317 bâtiments et 2 644 routes communs avec la scène initiale."),
        ],
    },
    {
        "title": "03 · Des limites physiques et des voyages contrôlés",
        "intro": "Le mur cadastral bloque les déplacements réels. Une cour issue du fichier PBF reste ouverte. Dans le Pip-Boy, le voyage annonce sa durée et exige une confirmation ; l’annulation conserve la position et l’heure.",
        "cards": [
            ("native_09b_real_courtyard.png", "COUR RÉELLE", "Un anneau intérieur conservé",
             "Objet cadastral 1653439797, deux anneaux. Mouvement possible dans la cour et géométrie stable après republication. Vue QA élevée, pas une caméra de marche."),
            ("native_10_travel_2_confirmation.png", "PIP-BOY", "Une confirmation lisible avant le départ",
             "Deux lieux déclarés découverts via le diagnostic, puis voyages exécutés par les boutons réels. Belvédère : 12 min ; Épave : 18 min, facturées une seule fois."),
        ],
    },
    {
        "title": "04 · Retrouver sa position après un vrai rechargement",
        "intro": "Le parcours enchaîne deux voyages, une écriture dans le stockage natif, un rechargement de page et le bouton Continuer. La dernière sauvegarde géographique passe désormais devant une ancienne enveloppe automatique.",
        "cards": [
            ("native_11_travel_2_arrival.png", "ARRIVÉE DU SECOND VOYAGE", "Épave · Galeries de l’Huveaune",
             "Arrivée libre sur les données locales. Même scène pendant le voyage ; inventaire, expérience et capsules conservés."),
            ("native_12_continue.png", "CONTINUER", "La sauvegarde récente est réellement reprise",
             "Position géographique restaurée à la précision numérique. L’étape de campagne et les sites découverts sont conservés après le rechargement natif."),
        ],
    },
]


def sha_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def sha_file(path):
    return sha_bytes(path.read_bytes())


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def instrumented_travel_hash(root, canonical):
    """Read only a literal AST assignment; never import the browser test."""
    tree = ast.parse((root / "tests/v050/poi_travel.py").read_text(encoding="utf-8"))
    inspectors = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "inspectors" for t in node.targets):
            inspectors = ast.literal_eval(node.value)
    if not isinstance(inspectors, str):
        raise ValueError("Inspecteurs littéraux du test de voyage introuvables")
    marker = "\ninit();\nv018AfterInit();"
    if canonical.count(marker) != 1 or "const V050_TRAVEL=" not in canonical:
        raise ValueError("Point d’instrumentation ambigu ou module de voyage absent")
    instrumented = canonical.replace(marker, "\n" + inspectors + marker, 1)
    return sha_bytes(instrumented.encode("utf-8"))


def collect(root):
    qa = root / "verification/v050"
    problems = []
    evidence_files = {}
    reports = {}

    def require(ok, message):
        if not ok:
            problems.append(message)

    def read(name, folder=qa):
        path = folder / name
        result = load_json(path)
        evidence_files[path.relative_to(root).as_posix()] = sha_file(path)
        return result

    canonical = root / "index.html"
    release = root / "JOUER_FALLOUT_MISTRAL_v0.50.html"
    digest = sha_file(canonical)
    require(digest == EXPECTED_HTML, "L’index ne correspond pas au build natif final fixé.")
    require(release.read_bytes() == canonical.read_bytes(), "Les deux HTML de livraison diffèrent.")
    source_hashes = {p.name: sha_file(p) for p in (canonical, release)}

    for name, expected in EXPECTED.items():
        r = reports[name] = read(name)
        require(r.get("version") == VERSION, f"{name} : version de rapport inattendue.")
        require(r.get("passed") == expected and r.get("failed") == 0 and r.get("total") == expected,
                f"{name} : résultat incomplet ou en échec, génération finale refusée.")
        require(not r.get("errors") and not r.get("page_errors") and not r.get("javascriptErrors"),
                f"{name} : exceptions enregistrées.")
        if "checks" in r:
            require(len(r["checks"]) == expected and all(c.get("ok") is True for c in r["checks"]),
                    f"{name} : les assertions ne confirment pas le total annoncé.")

    native = reports["NATIVE_REAL_MAP.json"]
    require(native.get("stage") == "complete" and native.get("native_navigation") is True,
            "Le parcours natif n’est pas terminé.")
    require(all(native.get(k) is False for k in ("network_mocked", "storage_mocked", "html_injected", "synthetic_lab_used")),
            "La preuve native contient une substitution de réseau, stockage, HTML ou géographie.")
    require(not native.get("debug_entry_fallback"), "Une entrée de secours ne vaut pas une sortie native du sas.")

    html_evidence = []
    for name in ("NATIVE_REAL_MAP.json", "QA_CAMPAIGN_MAP.json", "QA_CONTINUE_SAVE.json", "QA_LEGACY.json"):
        actual = reports[name].get("html_sha256")
        require(actual == digest, f"{name} : le SHA canonique ne correspond pas.")
        html_evidence.append({"file": name, "convention": "canonical_source_html", "reported": actual, "expected": digest, "valid": actual == digest})
    require(native.get("browser_document_sha256") == digest, "Le document reçu par Chromium diffère du fichier canonique.")
    travel = reports["QA_POI_TRAVEL.json"]
    instrumented = instrumented_travel_hash(root, canonical.read_text(encoding="utf-8"))
    require(travel.get("html_sha256") == instrumented, "Le SHA du HTML instrumenté pour le voyage ne se reproduit pas.")
    require(travel.get("in_memory_module_insertion") is False, "Le voyage a été testé avant intégration de son module.")
    html_evidence.append({"file": "QA_POI_TRAVEL.json", "convention": "canonical_html_plus_literal_private_test_inspectors",
                          "reported": travel.get("html_sha256"), "expected": instrumented,
                          "valid": travel.get("html_sha256") == instrumented,
                          "note": "in_memory_module_insertion=false concerne le module de jeu ; les inspecteurs privés du test sont néanmoins ajoutés au HTML exécuté."})
    for name in ("QA_CAMPAIGN_MAP.json", "QA_CONTINUE_SAVE.json"):
        require(reports[name].get("module_inserted_before_integration") is False,
                f"{name} a été exécuté avant intégration.")
    legacy = reports["QA_LEGACY.json"]
    require(legacy.get("allHtmlMatch") is True, "Les contrats hérités ne confirment pas le build actuel.")
    require(sum(s["total"] for s in legacy["suites"]) == 434, "Le détail des suites héritées ne totalise pas 434.")
    for suite in legacy["suites"]:
        r = read(suite["file"], qa / "legacy")
        require(all(r.get(k) == suite[k] for k in ("passed", "failed", "total")) and not r.get("failed"),
                f"Suite héritée périmée ou contradictoire : {suite['file']}.")
        require(not r.get("html_sha256") or r["html_sha256"] == digest,
                f"Source HTML héritée divergente : {suite['file']}.")

    installers = read("QA_INSTALLERS.json")
    installer_count = installers.get("tests")
    require(type(installer_count) is int and installer_count >= 37 and installers.get("passed") is True
            and installers.get("failures") == 0 and installers.get("errors") == 0,
            "Les tests d’installateurs ne sont pas tous réussis, ou le périmètre historique a été réduit.")
    cases = installers.get("cases", [])
    require(len(cases) == installer_count and all(c.get("passed") is True for c in cases)
            and len({c.get("test") for c in cases}) == installer_count,
            "Le détail des tests d’installateurs ne confirme pas le nombre de réussites distinctes.")
    local = read("LOCAL_DATA_STATE.json")
    require(local.get("complete") is True, "L’audit actualisé indique un pack incomplet.")
    require(local["vector"] == native["server_audit"]["vector"] and local["terrain"] == native["server_audit"]["terrain"],
            "L’audit du disque et l’audit du serveur pendant la navigation native diffèrent.")
    require(local["vector"]["expected"] == 5884 and local["vector"]["pbf"] == 4557
            and local["vector"]["officialEmpty"] == 1327 and local["terrain"]["valid"] == 8,
            "Le périmètre géographique installé n’est plus celui du test final.")
    offline = read("INSTALL_OFFLINE.json")
    require(offline.get("passed") is True and offline.get("networkAttempts") == 0
            and offline.get("coordinatesComparedBySha256") == 5884 and offline.get("emptyProofsComparedByteForByte") == 1327,
            "La preuve d’installation hors réseau est absente ou incomplète.")
    gzip_install = read("INSTALL_OFFLINE_GZIP.json")
    require(gzip_install.get("passed") is True and gzip_install.get("networkAttempts") == 0
            and gzip_install.get("coordinatesComparedBySha256") == 5884
            and gzip_install.get("emptyProofsComparedByteForByte") == 1327
            and len(gzip_install.get("terrainComparedByteForByte", [])) == 8
            and gzip_install.get("isolatedBundleClone") is True,
            "La preuve d’installation isolée avec le transport gzip est absente ou incomplète.")
    transport = gzip_install.get("gzipTransport", [])
    require(len(transport) == 1, "Le périmètre des enveloppes gzip a changé.")
    if len(transport) == 1:
        wrapped = transport[0]
        require(Path(wrapped.get("suppliedPath", "")).name == "base_00060_100.zip.gz"
                and wrapped.get("compressedBytes") == 7271970
                and wrapped.get("compressedSha256") == "8e5c14d3ff5600622792fb33a83994c3527de014c544094cd0578e2715ca9862"
                and wrapped.get("originalZipAbsentFromClone") is True
                and wrapped.get("decodedBytesLimit") == 13437755
                and wrapped.get("expectedOriginalZipSha256") == "bdfe4439f082f4a6e9d8b1c0472a4a1cefcd4e215457eec465620bedb619df94",
                "Le transport gzip ne confirme pas l’enveloppe et le ZIP original attendus.")
    ign = read("IGN_OFFICIAL_SMOKE.json")
    require(ign.get("passed") is True and ign.get("validPoints") == 4, "L’échantillon IGN ne comporte pas quatre réponses valides.")
    acquisition = read("acquisition_v050.json", root / "data/map_pack")
    for grid in acquisition["terrainGrids"]:
        require(sha_file(root / "data/map_pack" / grid["path"]) == grid["sha256"],
                f"Grille différente de son acquisition : {grid['macro']}.")

    shots = []
    for shot in native["shots"]:
        filename = shot["file"]
        require(Path(filename).name == filename, "Chemin de capture hors du dossier de preuves.")
        path = qa / filename
        actual = sha_file(path)
        require(actual == shot["sha256"], f"Capture modifiée : {filename}.")
        with Image.open(path) as im:
            width, height = im.size
        shots.append({**shot, "path": path.relative_to(root).as_posix(), "width": width, "height": height})
    selected = [c[0] for section in SECTIONS for c in section["cards"]]
    require(len(selected) == 8 and all(n in {s["file"] for s in shots} for n in selected),
            "Une des huit captures choisies manque.")

    failures = native.get("request_failures", [])
    external_cert = [f for f in failures if ".supabase.co/" in f["url"] and f.get("failure") == "net::ERR_CERT_AUTHORITY_INVALID"]
    require(len(failures) == len(external_cert) == 18, "Les erreurs réseau ont changé : le résumé doit être réexaminé.")
    require(len(native.get("console_errors", [])) == 18, "Les erreurs console natives ont changé.")
    perf = native["performance"]
    require(perf.get("median_ms") == 133.4 and perf.get("p95_ms") == 150.1
            and "SwiftShader" in perf.get("gpu", {}).get("renderer", ""), "La mesure de cadence doit être réexaminée.")
    if problems:
        raise ValueError("\n".join(problems))

    suites = []
    for name in EXPECTED:
        r = reports[name]
        suites.append({"file": f"verification/v050/{name}", "passed": r["passed"], "failed": r["failed"],
                       "total": r["total"], "scope": SCOPES[name]})
    suites.append({"file": "verification/v050/QA_INSTALLERS.json", "passed": installer_count, "failed": 0, "total": installer_count,
                   "scope": SCOPES["QA_INSTALLERS.json"]})
    groups = {"native": 83, "targeted": 95, "installers": installer_count, "inherited": 434}
    aggregate = {
        "schema": 1, "version": VERSION, "status": "complete",
        "scope": "Agrégation de preuves existantes ; aucune nouvelle exécution du jeu. Les méthodes et périmètres distincts restent explicites.",
        "html_sha256": digest, "canonicalFiles": source_hashes, "htmlEvidenceValidated": True, "htmlEvidence": html_evidence,
        "passed": sum(s["passed"] for s in suites), "failed": 0, "total": sum(s["total"] for s in suites),
        "countsByScope": groups, "suites": suites, "javascriptErrors": [],
        "additionalProofsCountedAsAssertions": False,
        "additionalProofs": {
            "offlineInstall": {"file": "verification/v050/INSTALL_OFFLINE.json", "passed": True,
                               "coordinatesComparedBySha256": 5884, "officialEmptyProofsCompared": 1327,
                               "terrainGridsCompared": 8, "networkAttempts": 0},
            "gzipTransportOfflineInstall": {"file": "verification/v050/INSTALL_OFFLINE_GZIP.json", "passed": True,
                                           "isolatedBundleClone": True, "coordinatesComparedBySha256": 5884,
                                           "officialEmptyProofsCompared": 1327, "terrainGridsCompared": 8,
                                           "networkAttempts": 0, "gzipTransport": transport,
                                           "scope": "Copie isolée où le ZIP original est absent ; seules l’enveloppe gzip, les autres ZIP et les grilles sont fournis."},
            "officialIgnSample": {"file": "verification/v050/IGN_OFFICIAL_SMOKE.json", "passed": True,
                                  "measuredPoints": 4, "scope": "Échantillon officiel isolé, sans remplacement des huit grilles livrées."},
        },
        "localData": local,
        "localDataAuditorVersionNote": "Le validateur conservé porte la version 0.46.0 ; ce fichier décrit les données réellement présentes pour la livraison 0.50.",
        "nativeMethod": {"browser": native["browser_version"], "nativeNavigation": True, "networkMocked": False,
                         "storageMocked": False, "htmlInjected": False, "syntheticLabUsed": False,
                         "assistance": native["assistance"],
                         "streamingAssistance": "Position initiale mesurée et demande de fenêtre anticipée à moins de 120 m via l’API existante ; déplacement par la collision de production. Ce contrôle ne constitue pas une randonnée manuelle."},
        "performance": perf,
        "network": {"failedInstalledDataRequests": 0, "externalCertificateFailures": 18,
                    "failure": "net::ERR_CERT_AUTHORITY_INVALID",
                    "externalUrls": sorted({f["url"] for f in external_cert}),
                    "note": "Sondes de services historiques Supabase ; aucune politique TLS relâchée dans le parcours natif."},
        "shots": shots, "reportSelectedShots": selected,
        "evidenceFilesSha256": evidence_files,
        "releaseLocations": {"github": GITHUB, "driveFolder": DRIVE,
                             "note": "Destinations de livraison ; ce rapport local ne constitue pas une preuve de publication distante."},
        "reproduction": "python3 tools/report_v050.py",
        "reproductionNote": "Pillow et les JSON/captures existants suffisent. L’agrégation refuse une preuve en échec, un ancien build ou une capture modifiée.",
    }
    return aggregate, native, acquisition


def image_data(root, name):
    raw = (root / "verification/v050" / name).read_bytes()
    return "data:image/png;base64," + base64.b64encode(raw).decode("ascii")


def make_html(root, aggregate, acquisition):
    esc = html.escape
    cards = "".join(f'<div class="score"><strong>{n}</strong><span>{esc(title)}</span><small>{esc(note)}</small></div>'
                    for title, n, note in score_groups(aggregate))
    sections = []
    for section in SECTIONS:
        figures = []
        for name, kicker, title, caption in section["cards"]:
            figures.append(f'<figure><img src="{image_data(root, name)}" alt="{esc(title)}" width="1440" height="900">'
                           f'<figcaption><span class="eyebrow">{esc(kicker)}</span><h3>{esc(title)}</h3><p>{esc(caption)}</p>'
                           f'<a href="verification/v050/{name}">Capture originale · SHA vérifié</a></figcaption></figure>')
        sections.append(f'<section><h2>{esc(section["title"])}</h2><p class="intro">{esc(section["intro"])}</p>'
                        f'<div class="pair">{"".join(figures)}</div></section>')
    rows = "".join(f'<tr><td><a href="{s["file"]}">{Path(s["file"]).name}</a></td><td>{s["passed"]}/{s["total"]}</td><td>{esc(s["scope"])}</td></tr>'
                   for s in aggregate["suites"])
    grid_names = {"geo_marseille": "Marseille", "geo_huveaune": "Huveaune et Aubagne", "geo_garlaban": "Garlaban",
                  "geo_calanques": "Calanques", "geo_laciotat": "La Ciotat", "geo_frioul": "Frioul",
                  "geo_etoile": "Étoile", "geo_saintebaume": "Sainte-Baume"}
    grid_rows = "".join(f'<tr><td>{grid_names[g["macro"]]}</td><td>{g["validPoints"]:,}</td><td>{g["missingPoints"]:,}</td>'
                        f'<td>{g["approximateSpacingMeters"]["x"]} × {g["approximateSpacingMeters"]["y"]} m</td></tr>'.replace(",", " ")
                        for g in acquisition["terrainGrids"])
    originals = "".join(f'<li><a href="{s["path"]}">{esc(s["file"])}</a><small>{esc(s["label"])}</small>'
                        f'<code>{s["sha256"]}</code></li>' for s in aggregate["shots"])
    return f"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>FALLOUT : MISTRAL v0.50 — Rapport de validation</title>
<style>
:root{{--bg:#111914;--panel:#1d2820;--line:#42513d;--text:#eeecd9;--muted:#b8c1a9;--gold:#ddc56b;--green:#acd28e}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:17px/1.62 system-ui,-apple-system,"Segoe UI",sans-serif}}
main{{max-width:1320px;margin:auto;padding:46px 36px 70px}}a{{color:var(--gold);text-underline-offset:3px}}
.eyebrow{{font:700 12px/1.5 ui-monospace,monospace;letter-spacing:.17em;color:var(--gold)}}
.mast{{display:flex;justify-content:space-between;gap:22px;border-bottom:1px solid var(--line);padding-bottom:18px}}
.stamp{{border:1px solid var(--green);color:var(--green);padding:4px 12px;white-space:nowrap;font:700 12px/1.7 ui-monospace,monospace}}
h1{{font-size:clamp(38px,5.7vw,76px);letter-spacing:-.055em;line-height:1.02;margin:27px 0 20px;max-width:1000px}}
.lead{{font-size:21px;max-width:1060px;color:var(--muted)}}h2{{font-size:29px;line-height:1.24;letter-spacing:-.025em;margin:0 0 15px}}h3{{font-size:21px;line-height:1.25;margin:10px 0}}
p{{margin:0 0 15px}}.scores{{display:grid;grid-template-columns:repeat(4,1fr);gap:15px;margin:30px 0 20px}}
.score{{background:var(--panel);border-top:3px solid var(--gold);padding:18px 20px;display:grid}}
.score strong{{font-size:52px;line-height:1.1;letter-spacing:-.05em}}.score span{{font-weight:700}}.score small{{color:var(--muted);font-size:12px}}
.data-strip{{padding:21px 25px;background:#273728;border-left:5px solid var(--green);font-size:18px}}
.data-strip strong{{color:#d3edb6}}section{{padding-top:45px}}.intro{{max-width:1150px;color:var(--muted)}}
.pair{{display:grid;grid-template-columns:1fr 1fr;gap:22px;margin-top:23px}}figure{{margin:0;background:var(--panel);border:1px solid var(--line)}}
figure img{{display:block;width:100%;height:auto}}figcaption{{padding:20px 23px 23px}}figcaption p{{font-size:15px;color:var(--muted)}}figcaption a{{font-size:12px}}
.note{{border-left:4px solid var(--gold);background:#272b1e;padding:22px 25px;margin-top:23px}}.method{{background:var(--panel);padding:25px;border:1px solid var(--line)}}
.method h3{{color:var(--gold);margin-top:0}}.method p,.method li{{font-size:15px;color:var(--muted)}}ul{{padding-left:21px}}
.table-wrap{{overflow:auto;margin:22px 0}}table{{width:100%;border-collapse:collapse;font-size:14px}}th,td{{text-align:left;padding:13px 15px;border-bottom:1px solid var(--line);vertical-align:top}}
th{{background:var(--panel);color:var(--gold);font-size:12px;letter-spacing:.05em}}td:nth-child(2){{font-variant-numeric:tabular-nums;white-space:nowrap}}
.total{{font-weight:700;background:var(--panel)}}code,pre{{font-family:ui-monospace,monospace}}code{{overflow-wrap:anywhere;font-size:12px;color:var(--green)}}
pre{{background:#0b110d;border:1px solid var(--line);padding:17px;white-space:pre-wrap;font-size:14px}}
details{{border:1px solid var(--line);padding:18px 23px;margin-top:24px}}summary{{cursor:pointer;font-weight:700;color:var(--gold)}}
details li{{padding:12px 0}}details small,details code{{display:block}}details small{{color:var(--muted);font-size:12px}}
footer{{border-top:1px solid var(--line);margin-top:42px;padding-top:25px;color:var(--muted);font-size:13px}}.links{{display:flex;gap:22px;flex-wrap:wrap;margin:18px 0}}
@media(max-width:760px){{main{{padding:25px 18px 50px}}.mast{{display:block}}.stamp{{display:inline-block;margin-top:14px}}.scores{{grid-template-columns:repeat(2,1fr)}}.pair{{grid-template-columns:1fr}}.lead{{font-size:18px}}h2{{font-size:25px}}}}
@media print{{body{{background:#fff;color:#172116;font-size:11px}}main{{max-width:none;padding:0}}.mast,.scores,.pair,figure,.method{{break-inside:avoid}}section{{padding-top:24px}}.lead{{font-size:15px}}h1{{font-size:38px}}h2{{font-size:22px}}h3{{font-size:16px}}figcaption p,.method p{{font-size:11px}}a{{color:#4a551e}}figure,.method,.score,.data-strip,.note,th,.total{{background:#f1f3ea;color:#172116}}.intro,figcaption p,.lead,.method p,footer{{color:#384430}}.eyebrow{{color:#546029}}.score strong{{font-size:32px}}details{{display:none}}}}
</style></head><body><main>
<header><div class="mast"><div class="eyebrow">FALLOUT : MISTRAL · PROVENCE 2291<br>DOSSIER DE VALIDATION · 18 OCTOBRE 2026</div><div class="stamp">V0.50 · PREUVES VÉRIFIÉES</div></div>
<h1>Les routes retrouvées.</h1><p class="lead">La campagne rejoint le territoire réel d’Aubagne. Les trajets, les collisions et la reprise de sauvegarde sont vérifiés sur les données livrées.</p>
<div class="scores">{cards}</div><div class="data-strip"><strong>5 884 / 5 884 coordonnées · 8 / 8 grilles de relief</strong><br>
4 557 PBF non vides + 1 327 réponses officiellement vides. Aucun fichier manquant ou invalide dans l’audit actualisé.</div></header>
{"".join(sections)}
<section><h2>Ce que les preuves établissent</h2><p class="intro">{aggregate["total"]} assertions réussies, réparties entre des méthodes différentes. Ce total ne représente pas {aggregate["total"]} parcours natifs et ne vaut pas certification de chaque rue ou de chaque lieu du catalogue.</p>
<div class="table-wrap"><table><thead><tr><th>RAPPORT SOURCE</th><th>RÉSULTAT</th><th>MÉTHODE ET PÉRIMÈTRE</th></tr></thead><tbody>{rows}<tr class="total"><td>Total d’assertions</td><td>{aggregate["passed"]} / {aggregate["total"]}</td><td>0 échec enregistré dans les suites agrégées.</td></tr></tbody></table></div>
<div class="pair"><div class="method"><h3>Parcours natif : ce qui est réel</h3><p>Chromium {aggregate["nativeMethod"]["browser"]} ouvre le serveur localhost. Le document reçu, les PBF, le relief et le stockage du navigateur sont réels. Aucune injection HTML, substitution du réseau ou du stockage, ni carte de laboratoire.</p>
<p>Les approches et actions du prologue, certaines positions de mesure, l’heure jour/nuit et la découverte préalable de deux lieux utilisent les API de diagnostic déjà présentes. Le déplacement vérifié passe par les collisions de production. La demande de fenêtre anticipée est assistée ; aucune randonnée manuelle intégrale n’est revendiquée.</p>
<p>La balise des ateliers est d’abord testée avec la simulation active. Le gel de simulation rend ensuite les mesures reproductibles. Le menu mobile de 390 px est contrôlé ; cela ne certifie pas tout le jeu tactile.</p></div>
<div class="method"><h3>Installation et données : preuves complémentaires</h3><p>L’installation dans un dossier vide a utilisé les 24 ZIP fournis et les huit grilles livrées : 5 884 coordonnées comparées par SHA-256, 1 327 attestations de vide et huit grilles comparées octet pour octet. Aucun appel réseau lors de cette installation.</p>
<p>Le dépôt GitHub transporte ces 24 archives sous la forme de 23 ZIP et d’un ZIP enveloppé en gzip. L’installateur décompacte automatiquement cette enveloppe avec une limite de taille, puis contrôle le SHA du ZIP original. Le projet complet distribué sur Drive conserve les 24 ZIP d’origine.</p>
<p>Une seconde installation isolée, où le ZIP original est absent et seule son enveloppe gzip est fournie, confirme les mêmes 5 884 coordonnées, 1 327 preuves de vide et huit grilles, avec zéro tentative réseau.</p>
<p>Un appel réel distinct au service officiel IGN a rendu quatre altitudes valides près d’Aubagne. Cet échantillon confirme ce chemin d’acquisition ; il ne remplace pas les huit grilles du snapshot et n’ajoute pas quatre tests au total d’assertions.</p>
<p><a href="verification/v050/INSTALL_OFFLINE.json">Installation hors réseau</a> · <a href="verification/v050/INSTALL_OFFLINE_GZIP.json">Installation isolée via gzip</a> · <a href="verification/v050/IGN_OFFICIAL_SMOKE.json">Échantillon IGN</a> · <a href="verification/v050/LOCAL_DATA_STATE.json">Audit local actualisé</a></p></div></div></section>
<section><h2>Du relief mesuré, avec ses zones sans donnée</h2><p class="intro">Huit grilles de 161 × 161 points : 174 944 altitudes valides et 32 424 valeurs NoData. Le relief est échantillonné et interpolé ; les valeurs manquantes restent absentes. Les emprises sont géographiques, tandis que bâtiments, hauteurs non renseignées et décors sont interprétés par le jeu.</p>
<div class="table-wrap"><table><thead><tr><th>SECTEUR</th><th>ALTITUDES VALIDES</th><th>NODATA</th><th>PAS APPROXIMATIF X × Y</th></tr></thead><tbody>{grid_rows}</tbody></table></div>
<p class="intro">Provenance déclarée du snapshot : OpenStreetMap contributors (ODbL), Cadastre Etalab / DGFiP (Licence Ouverte 2.0), RGE ALTI IGN (Licence Ouverte 2.0). Données historiques récupérées le 18 octobre 2026 ; les dates et empreintes par fichier figurent dans <a href="data/map_pack/acquisition_v050.json">l’inventaire d’acquisition</a>.</p></section>
<section><h2>Limites observées et portée du résultat</h2><div class="pair"><div class="method"><h3>Rendu logiciel : environ 7,5 images/s</h3><p>La mesure native utilise SwiftShader, le moteur graphique logiciel de cet environnement : 26 échantillons, médiane de 133,4 ms par image, p95 de 150,1 ms. Le rendu reste actif, mais cette cadence limite le confort de cette exécution.</p><p>Aucune performance de GPU matériel, de téléphone ou de poste utilisateur n’est déduite de cette mesure. La scène mesurée contient 4 732 groupes de rendu et 169 949 triangles.</p></div>
<div class="method"><h3>18 sondes externes en erreur de certificat</h3><p>Chromium relève 18 erreurs ERR_CERT_AUTHORITY_INVALID sur des sondes de services Supabase historiques. Le contrôle TLS n’a pas été relâché. Aucune requête de PBF ou de relief installé n’a échoué ; aucune exception JavaScript n’a été observée.</p><p>La campagne et les voyages ont utilisé le pack local. Le rapport ne garantit pas la disponibilité future des relais distants ni l’installation PWA native.</p></div></div>
<div class="note"><strong>Lecture fidèle des captures.</strong> Les extérieurs montrent les empreintes et le relief chargés, avec les représentations du prototype. Les ateliers sont une scène narrative construite à la main. Les captures du rapport sont huit fichiers natifs dont les SHA correspondent au pilote ; la vue de cour est une inspection élevée explicitement signalée.</div></section>
<section><h2>Intégrité et reproduction</h2><p>Le même HTML a été servi, reçu par Chromium et conservé pendant tout le parcours :</p><pre>{aggregate["html_sha256"]}</pre>
<p class="intro">Le test ciblé de voyage calcule son empreinte après l’ajout d’inspecteurs privés. L’agrégateur reconstruit cette insertion littérale depuis le HTML canonique et compare l’empreinte attendue. Il ne confond pas ce fichier instrumenté avec l’exécution native sans injection.</p>
<pre>python3 tools/report_v050.py</pre><p class="intro">La génération utilise Pillow et les rapports/captures existants. Elle refuse les preuves en échec, les mauvais SHA, les anciennes versions et les captures modifiées. Elle ne lance aucun navigateur.</p>
<div class="links"><a href="verification/v050/QA_GLOBAL.json">Agrégateur JSON</a><a href="docs/INSTALLATION_V050.md">Installation</a><a href="docs/KNOWN_LIMITATIONS_V0.50.md">Limites connues</a><a href="docs/PROVENANCE_V050.md">Provenance</a><a href="RAPPORT_VISUEL_V0.50.png">Version PNG autonome</a></div>
<details><summary>Inventaire des 20 captures et de leurs empreintes</summary><ul>{originals}</ul></details></section>
<footer><strong>FALLOUT : MISTRAL v0.50 — Les routes retrouvées.</strong><br>Prototype de fan non officiel ; aucune approbation de Bethesda revendiquée.
<div class="links"><a href="{GITHUB}">Dépôt du projet</a><a href="{DRIVE}">Dossier de livraison v0.50</a></div>
<p>Les huit images sont intégrées au HTML et restent visibles lorsqu’il est téléchargé seul. Les liens vers les JSON, notices et captures originales sont disponibles dans les archives complètes. Les liens de diffusion sont des destinations ; ce rapport local ne certifie pas une publication distante.</p></footer>
</main></body></html>
"""


class Poster:
    def __init__(self, font_dir):
        self.width = 1800
        self.image = Image.new("RGB", (self.width, 6800), "#111914")
        self.draw = ImageDraw.Draw(self.image)
        self.font_dir = font_dir
        self.cache = {}
        self.margin = 70
        self.content = self.width - 2 * self.margin
        self.text_color = "#eeecd9"
        self.muted = "#b8c1a9"
        self.gold = "#ddc56b"

    def font(self, size, bold=False, mono=False):
        key = (size, bold, mono)
        if key not in self.cache:
            filename = "DejaVuSansMono" if mono else "DejaVuSans"
            if bold:
                filename += "-Bold"
            self.cache[key] = ImageFont.truetype(str(self.font_dir / (filename + ".ttf")), size)
        return self.cache[key]

    def text(self, x, y, value, width, size=27, color=None, bold=False, mono=False, line=1.34):
        font = self.font(size, bold, mono)
        advance = round(size * line)
        for paragraph in value.split("\n"):
            words = paragraph.split()
            current = ""
            for word in words:
                candidate = (current + " " + word).strip()
                if current and font.getlength(candidate) > width:
                    self.draw.text((x, y), current, font=font, fill=color or self.text_color)
                    y += advance
                    current = word
                else:
                    current = candidate
            self.draw.text((x, y), current, font=font, fill=color or self.text_color)
            y += advance
        return y

    def rect(self, box, fill="#1d2820", outline="#42513d", radius=0):
        if radius:
            self.draw.rounded_rectangle(box, radius, fill=fill, outline=outline, width=1)
        else:
            self.draw.rectangle(box, fill=fill, outline=outline, width=1)

    def figure(self, root, x, y, width, card):
        name, kicker, title, caption = card
        height = round(width * 900 / 1440)
        with Image.open(root / "verification/v050" / name) as original:
            resized = original.convert("RGB").resize((width, height), Image.Resampling.LANCZOS)
        self.image.paste(resized, (x, y))
        caption_height = 218
        self.rect((x, y + height, x + width, y + height + caption_height))
        ty = self.text(x + 24, y + height + 18, kicker, width - 48, 18, self.gold, True, True)
        ty = self.text(x + 24, ty + 8, title, width - 48, 27, bold=True)
        ty = self.text(x + 24, ty + 9, caption, width - 48, 23, self.muted)
        if ty > y + height + caption_height - 4:
            raise ValueError(f"Légende trop longue pour la composition PNG : {name}")
        return y + height + caption_height

    def method(self, x, y, width, title, paragraphs, height):
        self.rect((x, y, x + width, y + height))
        cursor = self.text(x + 27, y + 23, title, width - 54, 28, self.gold, True)
        for p in paragraphs:
            cursor = self.text(x + 27, cursor + 13, p, width - 54, 24, self.muted)
        if cursor > y + height - 12:
            raise ValueError("Bloc de méthode trop long pour le PNG.")

    def finish(self, y):
        if y > self.image.height:
            raise ValueError("La composition dépasse la hauteur prévue.")
        buffer = io.BytesIO()
        self.image.crop((0, 0, self.width, y)).save(buffer, format="PNG", optimize=True)
        return buffer.getvalue()


def make_png(root, aggregate, font_dir):
    p = Poster(font_dir)
    m, w = p.margin, p.content
    p.text(m, 48, "FALLOUT : MISTRAL  /  PROVENCE 2291", w, 24, p.gold, True, True)
    p.text(m, 91, "DOSSIER DE VALIDATION · 18 OCTOBRE 2026 · V0.50", w, 19, p.muted, mono=True)
    y = p.text(m, 140, "Les routes retrouvées.", w, 78, bold=True, line=1.12)
    y = p.text(m, y + 20, "La campagne rejoint le territoire réel d’Aubagne. Trajets, collisions et sauvegardes vérifiés sur les données livrées.", w - 80, 32, p.muted)
    y += 30
    gap = 18
    cw = (w - gap * 3) // 4
    for i, (title, number, note) in enumerate(score_groups(aggregate)):
        x = m + i * (cw + gap)
        p.rect((x, y, x + cw, y + 146))
        p.draw.rectangle((x, y, x + cw, y + 4), fill=p.gold)
        p.text(x + 22, y + 15, str(number), cw - 44, 57, bold=True)
        p.text(x + 22, y + 85, title, cw - 44, 24, bold=True)
        p.text(x + 22, y + 117, note, cw - 44, 16, p.muted)
    y += 169
    p.rect((m, y, m + w, y + 108), fill="#273728")
    p.text(m + 24, y + 16, "5 884 coordonnées complètes  ·  8 grilles de relief", w - 48, 31, "#d3edb6", True)
    p.text(m + 24, y + 64, "4 557 PBF non vides + 1 327 vides attestés · aucun fichier manquant ou invalide", w - 48, 24, p.muted)
    y += 148
    colgap = 28
    col = (w - colgap) // 2
    for section in SECTIONS:
        y = p.text(m, y, section["title"], w, 36, bold=True)
        y = p.text(m, y + 12, section["intro"], w, 26, p.muted)
        y += 25
        ends = [p.figure(root, m + i * (col + colgap), y, col, card) for i, card in enumerate(section["cards"])]
        y = max(ends) + 47
    y = p.text(m, y, f"{aggregate['total']} assertions réussies, avec des méthodes explicites", w, 36, bold=True)
    y = p.text(m, y + 12, f"83 natifs + 36 voyage + 41 campagne + 18 Continuer + {aggregate['countsByScope']['installers']} installateurs + 434 hérités. Installation hors réseau et échantillon IGN consignés en preuves complémentaires, sans gonfler ce total.", w, 26, p.muted)
    y += 24
    left = [
        "Navigation HTTP, stockage Chromium, PBF et relief locaux réels. Aucune injection HTML, substitution de réseau ou stockage, ni carte synthétique dans le pilote natif.",
        "Approches, positions de mesure, heure et découverte préalable de deux sites assistées par les API de diagnostic existantes. La fenêtre anticipée est demandée par le pilote ; le mouvement passe par les collisions de production.",
        "Ateliers explicitement narratifs. Vue de cour élevée pour l’inspection. Menu mobile testé à 390 px ; aucune certification générale du jeu tactile.",
    ]
    right = [
        "SwiftShader : 26 échantillons, médiane 133,4 ms/image et p95 150,1 ms, soit environ 7,5 images/s. Rendu logiciel de cet environnement ; aucune promesse de performances matérielles.",
        "18 erreurs de certificat sur les sondes externes Supabase. Aucun échec de PBF ou relief installé et aucune exception JavaScript. Les politiques TLS restent actives.",
        "174 944 altitudes valides et 32 424 NoData. Relief échantillonné ; les absences restent absentes. Emprises réelles, bâtiments et décors interprétés par le prototype.",
    ]
    mh = 500
    p.method(m, y, col, "Méthode et assistance", left, mh)
    p.method(m + col + colgap, y, col, "Limites observées", right, mh)
    y += mh + 34
    y = p.text(m, y, "Installation hors réseau vérifiée", w, 29, p.gold, True)
    y = p.text(m, y + 9, "Dossier vide · 24 ZIP fournis · 5 884 SHA de coordonnées comparés · 1 327 attestations de vide et 8 grilles identiques · zéro appel réseau. Un appel officiel IGN séparé a rendu 4 altitudes valides près d’Aubagne.", w, 25, p.muted)
    y = p.text(m, y + 12, "Transport GitHub : 23 ZIP + 1 ZIP enveloppé en gzip. Installation isolée validée sans le ZIP original et sans réseau, avec les mêmes données en sortie. Le projet Drive conserve les 24 ZIP originaux.", w, 24, p.muted)
    y += 26
    p.draw.line((m, y, m + w, y), fill="#42513d", width=2)
    y = p.text(m, y + 22, "HTML canonique reçu par Chromium · SHA-256", w, 21, p.gold, True, True)
    y = p.text(m, y + 6, aggregate["html_sha256"], w, 23, "#acd28e", mono=True)
    y = p.text(m, y + 15, "Huit captures natives originales, empreintes vérifiées. Rapport détaillé : RAPPORT_VISUEL_V0.50.html · Sources : verification/v050/QA_GLOBAL.json", w, 22, p.muted)
    y = p.text(m, y + 13, "© OpenStreetMap contributors · Cadastre Etalab / DGFiP · RGE ALTI IGN. Prototype de fan non officiel ; aucune approbation de Bethesda revendiquée.", w, 21, p.muted)
    return p.finish(y + 43)


def choose_fonts(argument):
    if argument:
        candidates = [Path(argument)]
    else:
        candidates = [Path("/usr/share/fonts/truetype/dejavu")]
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", 20)
            candidates.append(Path(font.path).parent)
        except OSError:
            pass
    for directory in candidates:
        if all((directory / n).is_file() for n in ("DejaVuSans.ttf", "DejaVuSans-Bold.ttf", "DejaVuSansMono.ttf", "DejaVuSansMono-Bold.ttf")):
            return directory
    raise ValueError("Polices DejaVu introuvables ; fournir --font-dir avec les fichiers DejaVu Sans et Sans Mono.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--font-dir", help="Dossier des polices DejaVu TTF pour une génération portable.")
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        aggregate, native, acquisition = collect(root)
        html_text = make_html(root, aggregate, acquisition)
        png_bytes = make_png(root, aggregate, choose_fonts(args.font_dir))
        aggregate["visualReport"] = {"html": "RAPPORT_VISUEL_V0.50.html", "png": "RAPPORT_VISUEL_V0.50.png",
                                    "embeddedNativeImages": 8, "allOriginalScreenshotHashesVerified": True,
                                    "html_sha256": sha_bytes(html_text.encode("utf-8")), "png_sha256": sha_bytes(png_bytes),
                                    "rendering": "HTML autonome et composition Pillow avec huit captures natives redimensionnées sans recadrage.",
                                    "reproducibility": "Contenus déterministes pour les mêmes preuves, polices DejaVu et version de Pillow."}
        # No report is changed until all input validation and both renderings succeed.
        (root / "RAPPORT_VISUEL_V0.50.html").write_text(html_text, encoding="utf-8")
        (root / "RAPPORT_VISUEL_V0.50.png").write_bytes(png_bytes)
        (root / "verification/v050/QA_GLOBAL.json").write_text(dump_json(aggregate), encoding="utf-8")
        print(dump_json({"passed": aggregate["passed"], "failed": aggregate["failed"], "total": aggregate["total"],
                         "htmlEvidenceValidated": aggregate["htmlEvidenceValidated"],
                         "verifiedScreenshots": len(aggregate["shots"]), "embeddedImages": 8,
                         "report": aggregate["visualReport"]}))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print("Rapport final non généré : " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
