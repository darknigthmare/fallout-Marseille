#!/usr/bin/env python3
"""Real-HTTP source integration with explicitly synthetic, isolated source files.

This is a runtime contract test, not evidence of a new real-world survey. The
production HTML, importer, hash verification, map preparation, renderer, original
pack and Chromium are used. Only the optional local source directory is supplied
by a temporary fixture. No HTML/network/storage mocking is installed in Chromium.
Existing diagnostic APIs select the geographic scene and inspect its geometry.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys
import tempfile
import threading
import time
import traceback
from http.server import ThreadingHTTPServer
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from playwright.sync_api import sync_playwright
from qa_support import chromium_path
from serve_game import GameHandler
from world_sources import provenance, publish_bundle, read_geojson, read_terrain


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / ".venv/geography-browser")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    report = {"scope": "Production HTML, real loopback HTTP, original map pack, isolated SYNTHETIC source fixture; not real-world acquisition evidence", "checks": [], "page_errors": [], "network_mocked": False, "html_injected": False}

    def check(name, ok, detail=None):
        report["checks"].append({"name": name, "ok": bool(ok), "detail": detail})
        print(("OK " if ok else "FAIL ") + name, flush=True)

    original_sha = hashlib.sha256((ROOT / "index.html").read_bytes()).hexdigest()
    report["html_sha256"] = original_sha
    lat, lon = 43.2966, 5.5708
    region = "geo_huveaune"
    bounds = json.loads((ROOT / "data/map_pack/terrain/manifest_v039.json").read_text())
    bbox = next(row["bbox"] for row in bounds["regions"] if row["macro"] == region)
    with tempfile.TemporaryDirectory(prefix="mistral-source-fixture-") as temporary:
        output = Path(temporary)
        source = provenance(name="QA SYNTHETIC SOURCE FIXTURE — NOT A REAL SURVEY", license="CC0 test data", attribution="Mistral synthetic fixture", acquired_at="2026-10-23", resource="qa-source-fixture", vertical_datum="NGF-IGN69 (synthetic test values, not a survey)")
        outer = [[lon-.00028, lat+.00007], [lon-.00008, lat+.00007], [lon-.00008, lat+.00029], [lon-.00028, lat+.00029], [lon-.00028, lat+.00007]]
        hole = [[lon-.00022, lat+.00013], [lon-.00022, lat+.00023], [lon-.00014, lat+.00023], [lon-.00014, lat+.00013], [lon-.00022, lat+.00013]]
        geojson = {"type": "FeatureCollection", "features": [
            {"type": "Feature", "id": "synthetic-courtyard", "properties": {"kind": "building", "z_min_sol": 170, "z_max_toit": 188, "min_height": 2, "roof:height": 3, "roof:shape": "gabled", "roof:direction": 90}, "geometry": {"type": "Polygon", "coordinates": [outer, hole]}},
            {"type": "Feature", "id": "synthetic-bridge", "properties": {"kind": "road", "bridge": "yes", "width": "6 m"}, "geometry": {"type": "LineString", "coordinates": [[lon-.0003, lat-.00016, 190], [lon+.0003, lat-.00016, 192]]}}
        ]}
        values = [170 + j*.2 + i*.3 for j in range(9) for i in range(9)]
        values[0], values[8] = -4, None
        terrain = {"width": 9, "height": 9, "bbox": [lat-.0004, lon-.0004, lat+.0004, lon+.0004], "rowOrder": "north-to-south", "values": values}
        features = read_geojson(json.dumps(geojson).encode(), source, bbox)
        grid = read_terrain(json.dumps(terrain).encode(), region, source, bbox)
        publish_bundle(output, region, source, features=features, terrain=grid)

        class Handler(GameHandler):
            def translate_path(self, path):
                clean = unquote(urlsplit(path).path)
                prefix = "/data/map_pack/enrichment/"
                if clean.startswith(prefix):
                    leaf = clean[len(prefix):]
                    if Path(leaf).name == leaf:
                        return str(output / leaf)
                    return str(output / "invalid-path")
                return super().translate_path(path)

            def log_message(self, *args):
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        origin = f"http://127.0.0.1:{server.server_address[1]}"
        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(executable_path=chromium_path(), headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
                context = browser.new_context(viewport={"width": 1280, "height": 800}, service_workers="block")
                page = context.new_page()
                page.set_default_timeout(25000)
                page.on("pageerror", lambda e: report["page_errors"].append(str(e)))
                response = page.goto(origin + "/index.html", wait_until="load", timeout=45000)
                check("Native HTTP document matches the current build", hashlib.sha256(response.body()).hexdigest() == original_sha)
                page.wait_for_function("typeof __MISTRAL_DEBUG.v050GeographyInfo === 'function'")
                page.wait_for_function("!document.getElementById('bootScreen').classList.contains('active')", timeout=120000)

                def call(name, *arguments):
                    return page.evaluate("([n,a])=>__MISTRAL_DEBUG[n](...a)", [name, list(arguments)])

                def ready():
                    end = time.monotonic() + 180
                    while time.monotonic() < end:
                        info = call("v047Info")
                        if info["phase"] == "failed":
                            raise RuntimeError("Source preparation failed: " + json.dumps(call("v046Info")))
                        if info["tiles"] > 0 and not info["loading"] and not info["anticipating"]:
                            return info
                        page.wait_for_timeout(250)
                    raise TimeoutError("Source-enriched geographic preparation timed out")

                call("v047Control", {"auto": False})
                call("setRenderPaused", True)
                call("v018LoadMacro", region)
                ready()
                check("Measured overlay is loaded through the production resource path", region in call("v050GeographyInfo")["loadedRegions"])
                check("Optional source index passes SHA-256 verification", call("v050GeographyInfo")["indexPresent"] and not call("v050GeographyInfo")["errors"])
                result = call("v046Load", lat, lon)
                check("Source area preparation succeeds", result is True)
                ready()
                info = call("v050GeographyInfo")
                report["geography"] = info
                check("Both source objects retain their identities", info["sourceBuildings"] == 1 and info["sourceRoads"] == 1)
                building = next(o for o in info["sourceObjects"] if o["sourceId"] == "synthetic-courtyard")
                road = next(o for o in info["sourceObjects"] if o["sourceId"] == "synthetic-bridge")
                check("Source building uses measured absolute ground and minimum floor", building["baseY"] == 172 and building["profile"]["totalHeight"] == 18 and not building["profile"]["estimated"], building)
                check("Source courtyard remains a hole in the imported footprint", building["footprintRings"] == 2)
                check("Pitched roof separates measured eaves from ridge", building["height"] == 13 and building["profile"]["roofHeight"] == 3)
                check("Route preserves source width and explicit XYZ deck height", road["profile"]["width"] == 6 and not road["profile"]["elevationAssumed"] and road["profile"]["heightBasis"] == "coordonnées Z source", road)
                sample = call("v046Height", lat, lon)
                check("Fine terrain samples actual source elevations", abs(sample["height"] - 172) < 1e-7 and sample["sourceResource"] == "qa-source-fixture", sample)
                fine = info["terrainMesh"]
                check("Fine terrain mesh retains every native imported grid node", len(fine) == 1 and fine[0]["vertices"] == 81 and fine[0]["faces"] < 128 and max(fine[0]["nodeSpacingMeters"]) < 12, fine)
                land_surface = call("v050LandSurfaceInfo")
                check("Old land planes leave the fine relief and its NoData holes visible", land_surface["oldLandTrianglesInside"] == 0 and land_surface["coloredFaces"] == fine[0]["faces"] and land_surface["seamColoredFaces"] > 0, land_surface)
                geometry = page.evaluate("__MISTRAL_DEBUG.v018Geometry().filter(d=>d.mesh==='terrain'&&d.vertices?.length===81&&d.vertices.some(p=>Math.abs(p[1]+4.06)<1e-6)).map(d=>({minimum:Math.min(...d.vertices.map(p=>p[1])),faces:d.faces.length}))")
                check("Measured negative elevations are not flattened to sea level", bool(geometry) and abs(geometry[0]["minimum"] + 4.06) < 1e-7, geometry)
                point = call("v046Project", region, lat, lon)
                call("v018CaptureAt", [point[0], 173.65, point[2]], 0, 0)
                page.screenshot(path=str(args.output / "SYNTHETIC_SOURCE_FIXTURE.png"))
                call("v046Load", lat+.001, lon+.001)
                ready()
                check("A second sector loads without requesting a fictitious enrichment DEM", not call("v050GeographyInfo")["errors"])
                check("No JavaScript exception in source-enriched navigation", not report["page_errors"], report["page_errors"])
                context.close()
                browser.close()
        except Exception:
            report["exception"] = traceback.format_exc()
            check("Source browser pilot completes", False, report["exception"])
            print(report["exception"], flush=True)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
    check("Production HTML unchanged throughout the fixture run", hashlib.sha256((ROOT / "index.html").read_bytes()).hexdigest() == original_sha)
    report.update(passed=sum(c["ok"] for c in report["checks"]), failed=sum(not c["ok"] for c in report["checks"]), total=len(report["checks"]))
    (args.output / "GEOGRAPHY_SOURCE_BROWSER.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in ("passed", "failed", "total")}))
    return int(bool(report["failed"] or report["page_errors"]))


if __name__ == "__main__":
    raise SystemExit(main())
