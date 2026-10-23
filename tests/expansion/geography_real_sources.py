#!/usr/bin/env python3
"""Validate installed official IGN overlays with current production HTML in Chromium.

No fixtures, HTML injection, network replacement or fabricated geographic data.
Diagnostic APIs select the scene and camera; the actual pack, local source index,
SHA-256 checks, source attributes, renderer and browser storage remain production.
This bounded source integration check is distinct from the full campaign pilot.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import sys
import threading
import time
import traceback
from http.server import ThreadingHTTPServer

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from playwright.sync_api import sync_playwright
from qa_support import chromium_path
from serve_game import GameHandler


def positions(value):
    if isinstance(value, list) and value and type(value[0]) in (float, int):
        yield value
    elif isinstance(value, list):
        for part in value:
            yield from positions(part)


def nearest_feature(rows, lat, lon):
    def distance(feature):
        points = list(positions(feature["geometry"]["coordinates"]))
        x = sum(p[0] for p in points) / len(points)
        y = sum(p[1] for p in points) / len(points)
        return math.hypot((x-lon)*math.cos(math.radians(lat)), y-lat)
    return min(rows, key=distance)


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expect-html-sha")
    parser.add_argument("--region", default="geo_huveaune")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    report = {"scope": "Installed REAL official IGN source files, current production HTML, native Chromium, loopback HTTP; diagnostic scene/camera selection", "synthetic_geography": False, "network_mocked": False, "html_injected": False, "checks": [], "page_errors": []}

    def save():
        report.update(passed=sum(c["ok"] for c in report["checks"]), failed=sum(not c["ok"] for c in report["checks"]), total=len(report["checks"]))
        (args.output / "GEOGRAPHY_REAL_SOURCES.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")

    def check(name, ok, detail=None):
        report["checks"].append({"name": name, "ok": bool(ok), "detail": detail})
        print(("OK " if ok else "FAIL ") + name, flush=True)
        save()

    html_sha = hashlib.sha256((ROOT / "index.html").read_bytes()).hexdigest()
    if args.expect_html_sha and args.expect_html_sha != html_sha:
        raise SystemExit("Current HTML differs from the requested fixed build")
    index_bytes = (ROOT / "data/map_pack/enrichment/index.json").read_bytes()
    index = json.loads(index_bytes)
    descriptor = index["regions"][args.region]
    bundle_bytes = (ROOT / descriptor["path"]).read_bytes()
    if hashlib.sha256(bundle_bytes).hexdigest() != descriptor["sha256"]:
        raise SystemExit("Installed source bundle differs from its pinned SHA-256")
    bundle = json.loads(bundle_bytes)
    grids = bundle.get("terrainTiles", [bundle["terrain"]] if "terrain" in bundle else [])
    buildings = [f for f in bundle["features"] if f["properties"]["kind"] == "building"]
    roads = [f for f in bundle["features"] if f["properties"]["kind"] == "road"]
    if not grids or not buildings or not roads:
        raise SystemExit("Real terrain, buildings and roads must already be installed")
    for grid in grids:
        if "ign" not in grid["sourceResource"].lower() or any(label in grid["provenance"]["source"].lower() for label in ("fixture", "synthetic")):
            raise SystemExit("This runner requires actual official IGN source grids")
    finest = min(grids, key=lambda g: (g["bbox"][3]-g["bbox"][1])*(g["bbox"][2]-g["bbox"][0])/(g["width"]-1)/(g["height"]-1))
    ci, cj = finest["width"]//2, finest["height"]//2
    if not finite(finest["values"][cj*finest["width"]+ci]):
        raise SystemExit("Select a finite interior fine-grid node for this source integration check")
    lat = finest["bbox"][2] - (finest["bbox"][2]-finest["bbox"][0])*cj/(finest["height"]-1)
    lon = finest["bbox"][1] + (finest["bbox"][3]-finest["bbox"][1])*ci/(finest["width"]-1)
    expected_elevation = finest["values"][cj*finest["width"]+ci]
    known_building = nearest_feature([f for f in buildings if finite(f["properties"].get("altitude_minimale_sol")) and finite(f["properties"].get("altitude_maximale_toit"))], lat, lon)
    known_road = nearest_feature([f for f in roads if finite(f["properties"].get("largeur_de_chaussee")) and f["properties"]["largeur_de_chaussee"] > 0 and all(len(p) == 3 and finite(p[2]) for p in positions(f["geometry"]["coordinates"]))], lat, lon)
    unknown_buildings = [f for f in buildings if f["properties"].get("hauteur") is None and f["properties"].get("altitude_maximale_toit") is None]
    report.update(html_sha256=html_sha, index_sha256=hashlib.sha256(index_bytes).hexdigest(), source_bundle_sha256=descriptor["sha256"], source_bundle_path=descriptor["path"], source_counts={"buildings": len(buildings), "roads": len(roads), "terrain_grids": len(grids), "terrain_nodes": sum(g["width"]*g["height"] for g in grids)})

    class Handler(GameHandler):
        def log_message(self, *arguments):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    origin = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path=chromium_path(), headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
            context = browser.new_context(viewport={"width": 1280, "height": 800}, service_workers="block")
            page = context.new_page()
            page.set_default_timeout(30000)
            page.on("pageerror", lambda error: report["page_errors"].append(str(error)))
            response = page.goto(origin + "/index.html", wait_until="load", timeout=45000)
            check("Real HTTP serves the exact requested production build", hashlib.sha256(response.body()).hexdigest() == html_sha)
            page.wait_for_function("typeof __MISTRAL_DEBUG.v050SourceObjectInfo === 'function'")
            page.wait_for_function("!document.getElementById('bootScreen').classList.contains('active')", timeout=120000)

            def call(name, *values):
                return page.evaluate("([name,values])=>__MISTRAL_DEBUG[name](...values)", [name, list(values)])

            def ready():
                deadline = time.monotonic() + 240
                printed = 0
                while time.monotonic() < deadline:
                    info = call("v047Info")
                    if info["phase"] == "failed":
                        raise RuntimeError("Actual source preparation failed: " + json.dumps(call("v046Info")))
                    if info["tiles"] > 0 and not info["loading"] and not info["anticipating"]:
                        return info
                    if time.monotonic()-printed > 15:
                        print("LOAD " + json.dumps({k: info[k] for k in ("phase", "done", "total", "tiles")}), flush=True)
                        printed = time.monotonic()
                    page.wait_for_timeout(250)
                raise TimeoutError("Actual source staging did not complete")

            call("v047Control", {"auto": False})
            call("setRenderPaused", True)
            call("v018LoadMacro", args.region)
            ready()
            check("Real source area commits successfully", call("v046Load", lat, lon) is True)
            ready()
            info = call("v050GeographyInfo")
            report["geography"] = info
            check("Hash-verified official building and road counts match disk", info["sourceBuildings"] == len(buildings) and info["sourceRoads"] == len(roads), report["source_counts"])
            imported_grids = [g for g in info["terrainSources"] if g["enrichment"]]
            check("Every retained fine and broader terrain grid reaches the staged bank", set(g["id"] for g in imported_grids) == set(g["macro"] for g in grids), imported_grids)
            sample = call("v046Height", lat, lon)
            check("The finest actual source is selected at its documented imported node", sample["sources"] == [finest["macro"]] and abs(sample["height"]-expected_elevation) < 1e-5, sample)
            check("Actual source datum remains explicit NGF-IGN69", sample["verticalDatum"].startswith("NGF-IGN69"))
            fine_mesh = info["terrainMesh"]
            check("Actual high-resolution terrain builds a bounded fine mesh", bool(fine_mesh) and fine_mesh[0]["source"] == finest["sourceResource"] and fine_mesh[0]["vertices"] <= 262144 and max(fine_mesh[0]["nodeSpacingMeters"]) < 1, fine_mesh)
            land_surface = call("v050LandSurfaceInfo")
            report["land_surface"] = land_surface
            check("Old land planes cannot mask real fine relief or its stitched boundary", land_surface["oldLandTrianglesInside"] == 0 and land_surface["clippedDraws"] > 0 and land_surface["coloredFaces"] > 0 and land_surface["seamColoredFaces"] > 0, land_surface)
            check("Fine terrain colour sampling is explicit and indexed without changing its geometry", fine_mesh[0]["colorGroups"] >= 1 and "centre" in fine_mesh[0]["colorSampling"].lower() and fine_mesh[0]["colorPolygonCount"] > 0, fine_mesh)
            conversion = finest["provenance"].get("conversion")
            check("Native raster spacing and WGS84 resampling stay separately documented", conversion is not None and conversion["nativePixelSize"] == [0.5, 0.5] and conversion["resampled"] is True and conversion["resampling"] == "nearest", conversion)
            building = call("v050SourceObjectInfo", known_building["properties"]["sourceId"])
            props = known_building["properties"]
            check("Actual building ground and roof elevations control its envelope", building is not None and abs(building["baseY"]-props["altitude_minimale_sol"]) < 1e-7 and abs(building["baseY"]+building["height"]-props["altitude_maximale_toit"]) < 1e-7, building)
            check("Unspecified building roof shape is still identified as unknown", building is not None and building["profile"]["roofEstimated"] is True)
            road = call("v050SourceObjectInfo", known_road["properties"]["sourceId"])
            check("Actual carriageway width and source XYZ survive road import", road is not None and road["profile"]["width"] == known_road["properties"]["largeur_de_chaussee"] and road["profile"]["heightBasis"] == "coordonnées Z source" and not road["profile"]["elevationAssumed"], road)
            if unknown_buildings:
                unknown = call("v050SourceObjectInfo", nearest_feature(unknown_buildings, lat, lon)["properties"]["sourceId"])
                check("Actual missing building heights remain estimates rather than fabricated measurements", unknown is not None and unknown["profile"]["estimated"] is True and unknown["profile"]["roofEstimated"] is True and unknown["profile"]["reportedHeight"] is None, unknown)
            coverages = [coverage for coverage in info["coverages"] if coverage["layer"] == "BDTOPO_V3:troncon_de_route"]
            check("Road replacement exposes complete official query coverage", bool(coverages) and all(c["complete"] and c["returned"] > 0 for c in coverages), coverages)
            polygons = []
            for coverage in coverages:
                s, w, n, e = coverage["bbox"]
                polygons.append([[p[0], p[2]] for p in [call("v046Project", args.region, la, lo) for la, lo in ((s,w),(s,e),(n,e),(n,w))]])
            audit = page.evaluate("""polygons=>{
              const inside=(poly,p)=>{let hit=false;for(let i=0,j=poly.length-1;i<poly.length;j=i++){const a=poly[i],b=poly[j];if((a[1]>p[1])!==(b[1]>p[1])&&p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0])hit=!hit;}return hit;};
              const boundary=(poly,p)=>poly.some((a,i)=>{const b=poly[(i+1)%poly.length],dx=b[0]-a[0],dz=b[1]-a[1],t=Math.max(0,Math.min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dz)/(dx*dx+dz*dz)));return Math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dz)<1e-5;});
              const report={basePaths:0,sourcePaths:0,baseMidpointsInside:0,sourceVerticesOutside:0};
              for(const d of __MISTRAL_DEBUG.v018Geometry())if(d.layer==='transportation'&&d.roadPath){
                if(String(d.id||'').startsWith('source:')){report.sourcePaths++;for(const p of d.roadPath)if(!polygons.some(poly=>inside(poly,p)||boundary(poly,p)))report.sourceVerticesOutside++;}
                else{report.basePaths++;for(let i=1;i<d.roadPath.length;i++){const a=d.roadPath[i-1],b=d.roadPath[i],p=[(a[0]+b[0])/2,(a[1]+b[1])/2];if(polygons.some(poly=>inside(poly,p)&&!boundary(poly,p)))report.baseMidpointsInside++;}}
              }return report;
            }""", polygons)
            check("Old base-map roads are absent inside the completed authoritative query", audit["baseMidpointsInside"] == 0 and audit["basePaths"] > 0, audit)
            check("Imported road strokes stop at their actual acquisition boundary", audit["sourceVerticesOutside"] == 0 and audit["sourcePaths"] > 0, audit)
            point = call("v046Project", args.region, lat, lon)
            call("v018CaptureAt", [point[0], sample["height"]+25, point[2]], .5, -.5)
            page.screenshot(path=str(args.output / "REAL_IGN_AUBAGNE.png"))
            cache_before = call("v050GeographyInfo")["terrainCache"]
            edge_lat, edge_lon = 43.2973, 5.5702
            if finest["bbox"][0] <= edge_lat <= finest["bbox"][2] and finest["bbox"][1] <= edge_lon <= finest["bbox"][3]:
                started = time.monotonic()
                check("A second anchor near the actual workshop gateway prepares successfully", call("v046Load", edge_lat, edge_lon) is True)
                ready()
                edge_info = call("v050GeographyInfo")
                check("The complete small LiDAR patch reuses its bounded cache near the gateway", edge_info["terrainCache"]["hits"] > cache_before["hits"] and edge_info["terrainMesh"][0]["vertices"] == finest["width"]*finest["height"] and edge_info["terrainCache"]["entries"] <= 2 and edge_info["terrainCache"]["bytes"] <= 64*1024*1024, {"before": cache_before, "after": edge_info["terrainCache"], "elapsed_seconds": time.monotonic()-started, "mesh": edge_info["terrainMesh"]})
                started = time.monotonic()
                check("Returning to the actual fine-grid centre prepares successfully", call("v046Load", lat, lon) is True)
                ready()
                centre_info = call("v050GeographyInfo")
                check("The centre return reuses the same complete LiDAR node count and cache", centre_info["terrainCache"]["hits"] > edge_info["terrainCache"]["hits"] and centre_info["terrainMesh"][0]["vertices"] == finest["width"]*finest["height"] and centre_info["terrainCache"]["entries"] <= 2 and centre_info["terrainCache"]["bytes"] <= 64*1024*1024, {"before": edge_info["terrainCache"], "after": centre_info["terrainCache"], "elapsed_seconds": time.monotonic()-started})
            broad = next((g for g in grids if g["macro"] != finest["macro"]), None)
            if broad:
                # A real point outside the small fine patch but inside broad coverage.
                broad_lat = broad["bbox"][2] - (broad["bbox"][2]-broad["bbox"][0])*.1
                broad_lon = broad["bbox"][3] - (broad["bbox"][3]-broad["bbox"][1])*.1
                broad_sample = call("v046Height", broad_lat, broad_lon)
                check("Broader real source remains available outside the fine patch", broad_sample["sources"] == [broad["macro"]] and finite(broad_sample["height"]), broad_sample)
                check("A second actual sector prepares with the retained terrain atlas", call("v046Load", broad_lat, broad_lon) is True)
                ready()
            check("No source-fetch, hash, coverage or staging error was recorded", not call("v050GeographyInfo")["errors"], call("v050GeographyInfo")["errors"])
            check("No JavaScript exception occurred while loading actual sources", not report["page_errors"], report["page_errors"])
            context.close()
            browser.close()
    except Exception:
        report["exception"] = traceback.format_exc()
        check("Real source browser pilot completes", False, report["exception"])
        print(report["exception"], flush=True)
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=5)
    check("Production HTML and actual source snapshot remained unchanged", hashlib.sha256((ROOT/"index.html").read_bytes()).hexdigest() == html_sha and (ROOT/"data/map_pack/enrichment/index.json").read_bytes() == index_bytes)
    save()
    print(json.dumps({key: report[key] for key in ("passed", "failed", "total")}))
    return int(bool(report["failed"] or report["page_errors"]))


if __name__ == "__main__":
    raise SystemExit(main())
