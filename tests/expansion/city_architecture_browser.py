#!/usr/bin/env python3
"""Assisted native-browser contracts for the installed Marseille city atlas.

The exact production HTML, real GameHandler, city partitions, terrain, source
hashes, UI and browser storage are used. Existing diagnostic APIs load sectors,
place a camera on measured clear ground and pause simulation/rendering. They do
not fabricate buildings, substitute HTTP, inject HTML or grant a documentary
plan. Portal, landing and container actions use actual keyboard/UI controls.
This is a bounded integration pilot, not an unassisted citywide playthrough.
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
import urllib.request
from http.server import ThreadingHTTPServer

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from playwright.sync_api import sync_playwright
from qa_support import chromium_path
from serve_game import GameHandler

CITY = "geo_marseille_commune"
TARGETS = (("vieux_port", 43.2965, 5.3698), ("estaque", 43.362, 5.312))


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def main():
    started = time.monotonic()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expect-html-sha", required=True)
    parser.add_argument("--ready-timeout", type=int, default=300)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    report = {"scope": __doc__, "html_sha256": None, "stage": "preflight",
              "html_injected": False, "network_mocked": False,
              "storage_mocked": False, "synthetic_geography": False,
              "assistance": ["Existing macro/sector loading APIs",
                             "Measured, collision-free camera selection and existing physical approach helper",
                             "Existing QA simulation freeze and paused continuous rendering; explicit real WebGL captures"],
              "checks": [], "shots": [], "page_errors": [],
              "console_errors": [], "request_failures": [], "local_http_errors": [], "sectors": {},
              "stage_history": [], "timings": {}}
    page = None
    server = None
    worker = None
    frozen = {}

    def save():
        report["elapsed_seconds"] = round(time.monotonic() - started, 3)
        report.update(passed=sum(c["ok"] for c in report["checks"]),
                      failed=sum(not c["ok"] for c in report["checks"]),
                      total=len(report["checks"]))
        (args.output / "CITY_ARCHITECTURE_BROWSER.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n")

    def stage(name):
        report["stage"] = name
        report["stage_history"].append({"stage": name, "elapsed_seconds": round(time.monotonic() - started, 3)})
        print("STAGE " + name, flush=True)
        save()

    def check(name, ok, detail=None):
        report["checks"].append({"name": name, "ok": bool(ok), "detail": detail})
        print(("OK " if ok else "FAIL ") + name, flush=True)
        save()

    def require(name, ok, detail=None):
        check(name, ok, detail)
        if not ok:
            raise AssertionError(name)

    def debug(name, *values):
        return page.evaluate("([name,values])=>__MISTRAL_DEBUG[name](...values)", [name, list(values)])

    def shot(name, label):
        path = args.output / (name + ".png")
        page.screenshot(path=str(path))
        report["shots"].append({"file": path.name, "label": label, "sha256": sha(path.read_bytes())})
        save()

    def ready():
        deadline, printed = time.monotonic() + args.ready_timeout, 0
        while time.monotonic() < deadline:
            info = debug("v047Info")
            if info["phase"] == "failed":
                raise RuntimeError("Real city staging failed: " + json.dumps(debug("v046Info")))
            if info["tiles"] > 0 and not info["loading"] and not info["anticipating"]:
                return info
            if time.monotonic() - printed >= 15:
                print("LOAD " + json.dumps({k: info[k] for k in ("phase", "done", "total", "tiles")}), flush=True)
                printed = time.monotonic()
            page.wait_for_timeout(250)
        report["readiness_failure"] = {"map": debug("v047Info"), "city": debug("v051CityInfo"), "preparation": debug("v048Info")}
        raise TimeoutError("Actual city staging did not complete within the bounded readiness timeout")

    def capture_here(yaw=None, pitch=None):
        player = debug("getState")["player"]
        return debug("v018CaptureAt", player["pos"], player["yaw"] if yaw is None else yaw,
                     player["pitch"] if pitch is None else pitch)

    def physical_interaction(interaction_id, expected_label):
        """Use the existing collision/LOS-checked approach, then a real E key."""
        approach = debug("v020Approach", interaction_id)
        if not approach:
            return False
        if interaction_id.startswith("city-door:"):
            # The historical approach helper uses object-height + 0.65 m;
            # seed the exterior camera on the actual measured ground instead
            # of saving that small artificial hover as a return altitude.
            ll = debug("v046LL")
            ground = debug("v046Height", *ll)
            if not finite(ground["height"]):
                return False
            player = debug("getState")["player"]
            debug("v018CaptureAt", [player["pos"][0], ground["height"] + 1.65, player["pos"][2]], player["yaw"], 0)
            placed = debug("getState")["player"]
            require("Portal setup places a standing player at the measured production ground height",
                    not placed.get("crouched", False) and abs(placed["pos"][1] - ground["height"] - 1.65) < 1e-7,
                    {"ground": ground, "position": placed["pos"], "eye_height": 1.65})
        else:
            capture_here(pitch=0)
        label = page.locator("#interactLabel").inner_text()
        if expected_label.casefold() not in label.casefold():
            return False
        if interaction_id.startswith("city-door:"):
            ll = debug("v046LL")
            report["entrance_approach"] = {"interaction": interaction_id, "approach": approach,
                                            "latlon": ll, "ground": debug("v046Height", *ll),
                                            "canonical_position": debug("getState")["player"]["pos"]}
        page.keyboard.press("e")
        return True

    def landing():
        # Return to the unchanged, already clear landing spawn before the
        # proximity-checked user action; no action function is invoked here.
        info = debug("v020Stats")
        interaction = next((i for i in info["interactables"] if i["id"] == "city-interior-landing"), None)
        require("The real interior exposes an accessible landing interaction", interaction is not None)
        position = [interaction["pos"][0], interaction["pos"][1] + .55, interaction["pos"][2]]
        require("Landing camera remains on clear interior floor", not debug("v020Collides", position), position)
        debug("v018CaptureAt", position, 0, 0)
        require("The visible interaction targets the actual landing", "palier" in page.locator("#interactLabel").inner_text().lower())
        page.keyboard.press("e")
        page.locator("#dialogue").wait_for(state="visible")

    def read_saved():
        key = debug("v018PersistentStatus")["key"]
        return key, page.evaluate("key=>{const raw=localStorage.getItem(key);return raw?JSON.parse(raw):null;}", key)

    def go_to_floor(target):
        current = debug("v050CityInteriorInfo")["active"]["floor"]
        require("The requested storey is adjacent to the current landing", abs(target - current) == 1,
                {"from": current, "to": target})
        landing()
        label = ("Monter au niveau " if target > current else "Descendre au niveau ") + str(target)
        page.get_by_role("button", name=label, exact=True).click()
        page.wait_for_function("n=>__MISTRAL_DEBUG.v050CityInteriorInfo().active?.floor===n", arg=target)
        require("The landing dialog closes after its storey transition", page.locator("#dialogue").is_hidden())

    try:
        html = (ROOT / "index.html").read_bytes()
        require("The requested frozen production HTML is installed", sha(html) == args.expect_html_sha, sha(html))
        report["html_sha256"] = sha(html)
        for name in ("index.json", "terrain-index.json", "water-index.json"):
            path = ROOT / "data/map_pack/city" / name
            frozen[path] = path.read_bytes()
        frozen[ROOT / "index.html"] = html
        index = json.loads(frozen[ROOT / "data/map_pack/city/index.json"])
        coverage, municipality = index["coverage"], index["municipality"]
        boundary_descriptor = municipality["boundary"]
        boundary_path = ROOT / boundary_descriptor["path"]
        boundary_raw = boundary_path.read_bytes()
        frozen[boundary_path] = boundary_raw
        require("Official full-commune boundary is locally pinned by bytes and SHA-256",
                len(boundary_raw) == boundary_descriptor["bytes"] and sha(boundary_raw) == boundary_descriptor["sha256"], boundary_descriptor)
        require("The installed city index identifies a completed Marseille acquisition",
                municipality["code"] == "13055" and municipality["name"] == "Marseille"
                and coverage["complete"] is True and len(index["tiles"]) == coverage["tileCount"]
                and coverage["uniqueBuildings"] > 0 and coverage["uniqueRoads"] > 0, coverage)
        require("The frozen city acquisition contains the expected complete source inventory",
                (coverage["uniqueBuildings"], coverage["uniqueRoads"], len(index["tiles"])) == (291001, 55449, 290))
        terrain_index = json.loads(frozen[ROOT / "data/map_pack/city/terrain-index.json"])
        water_index = json.loads(frozen[ROOT / "data/map_pack/city/water-index.json"])
        base_regions = json.loads((ROOT / "data/map_pack/terrain/manifest_v039.json").read_text())["regions"]
        require("All twenty-five requested fine terrain partitions are certified complete",
                terrain_index["coverage"]["fineComplete"] is True
                and terrain_index["coverage"]["requestedFinePartitions"] == 25
                and terrain_index["coverage"]["completedFinePartitions"] == 25,
                terrain_index["coverage"])
        report["source_snapshot"] = {"html_sha256": sha(html),
                                     "index_sha256": sha(frozen[ROOT / "data/map_pack/city/index.json"]),
                                     "terrain_index_sha256": sha(frozen[ROOT / "data/map_pack/city/terrain-index.json"]),
                                     "water_index_sha256": sha(frozen[ROOT / "data/map_pack/city/water-index.json"]),
                                     "boundary_sha256": sha(boundary_raw), "municipality": municipality,
                                     "coverage": coverage}

        class Handler(GameHandler):
            def log_message(self, *arguments):
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        origin = f"http://127.0.0.1:{server.server_address[1]}"
        stage("municipal_server_audit")
        audit_started = time.monotonic()
        with urllib.request.urlopen(origin + "/__mistral/city-sources", timeout=120) as response:
            audit = json.load(response)
            audit_headers = {"status": response.status, "cache_control": response.headers.get("Cache-Control")}
        report["timings"]["server_full_partition_audit_seconds"] = round(time.monotonic() - audit_started, 3)
        report["server_audit"] = audit
        require("Actual server verifies every installed partition and returns an uncached complete audit",
                audit_headers == {"status": 200, "cache_control": "no-store"} and audit["ok"] and audit["present"]
                and audit["indexSha256"] == report["source_snapshot"]["index_sha256"]
                and audit["municipality"]["bbox"] == municipality["bbox"] and audit["coverage"] == coverage
                and audit["totalBuildings"] == coverage["uniqueBuildings"]
                and audit["totalRoads"] == coverage["uniqueRoads"] and audit["tileCount"] == len(index["tiles"]), audit_headers)
        require("Real municipal terrain accompanies the full-boundary source index", audit["terrain"]["present"] is True, audit["terrain"])

        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path=chromium_path(), headless=True,
                                         args=["--no-sandbox", "--disable-dev-shm-usage"])
            context = browser.new_context(viewport={"width": 1440, "height": 900})
            page = context.new_page()
            page.set_default_timeout(30000)
            page.on("pageerror", lambda error: report["page_errors"].append(str(error)))
            page.on("console", lambda message: report["console_errors"].append(message.text) if message.type == "error" else None)
            page.on("requestfailed", lambda request: report["request_failures"].append({"url": request.url, "failure": request.failure}))
            page.on("response", lambda response: report["local_http_errors"].append({"url": response.url, "status": response.status})
                    if response.url.startswith(origin + "/data/map_pack/city/") and response.status >= 400 else None)
            page.on("dialog", lambda dialog: dialog.accept())
            response = page.goto(origin + "/index.html?skipboot", wait_until="load", timeout=60000)
            require("Native Chromium receives the unchanged production document over real HTTP",
                    response.status == 200 and sha(response.body()) == args.expect_html_sha)
            page.wait_for_function("!document.getElementById('bootScreen').classList.contains('active')", timeout=120000)
            page.wait_for_function("['v051CityReady','v051CityInfo','v051WaterInfo','v050FacadeInfo','v050CityInteriorInfo'].every(k=>typeof __MISTRAL_DEBUG[k]==='function')")
            debug("v051CityReady")
            info = debug("v051CityInfo")
            require("Runtime registers the real commune and complete partition inventory",
                    info["registered"] and info["indexPresent"] and info["terrainIndexPresent"]
                    and info["municipality"]["code"] == "13055" and info["coverage"] == coverage
                    and info["tilesAvailable"] == len(index["tiles"]), info)
            stage("city_source_panel")
            page.locator("#v050MapStatus").click()
            page.locator("[data-city-source-status]").wait_for(state="visible")
            page.wait_for_function("__MISTRAL_DEBUG.v051CityPanel().data?.present===true", timeout=120000)
            debug("v051ReadCityStatus")
            panel = debug("v051CityPanel")
            report["city_panel"] = panel
            require("Player-visible city panel reports the actual audited building and road totals",
                    panel["error"] is None and panel["data"]["totalBuildings"] == audit["totalBuildings"]
                    and panel["data"]["totalRoads"] == audit["totalRoads"] and panel["data"]["coverageComplete"]
                    and (panel["data"]["totalBuildings"], panel["data"]["totalRoads"], panel["data"]["tileCount"]) == (291001, 55449, 290))
            shot("01_city_sources", "Unmodified menu source panel, actual municipal HTTP audit")
            page.locator("#v047CloseStatus").click()
            debug("v047Control", {"auto": False})
            debug("setRenderPaused", True)
            stage("initial_macro")
            initial_started = time.monotonic()
            debug("v018LoadMacro", CITY)
            ready()
            report["timings"]["initial_macro_staging_seconds"] = round(time.monotonic() - initial_started, 3)

            def water_probe(lat, lon):
                return page.evaluate("""([lat,lon])=>{const d=__MISTRAL_DEBUG,p=d.v046Project('geo_huveaune',lat,lon),geometry=d.v018Geometry(),sea=geometry.filter(g=>g.layer==='water'&&String(g.id||'').startsWith('water:ign-sea:')),hits=sea.filter(g=>d.v018Contains(g.rings,p[0],p[2]));return{latlon:[lat,lon],projected:p,ground:d.v046Height(lat,lon),maritimePolygonsLoaded:sea.length,maritimeHits:hits.map(g=>({id:g.id,mesh:g.mesh,renderY:g.pos[1],rings:g.rings.length})),collision:d.v046Collide(p[0],p[2])};}""", [lat, lon])

            stage("maritime_diagnostic")
            require("The real maritime diagnostic sector prepares successfully", debug("v046Load", 43.35, 5.30) is True)
            ready()
            sea, maritime = water_probe(43.35, 5.30), debug("v051WaterInfo")
            report["maritime"] = {"sea": sea, "runtime": maritime}
            require("The actual official water atlas is present with its pinned source and unsimplified shoreline",
                    maritime["present"] and maritime["tiles"] == len(water_index["tiles"])
                    and maritime["source"] == water_index["source"]
                    and maritime["derivation"] == water_index["derivation"] and maritime["derivation"]["noSimplification"] is True,
                    maritime)
            require("The loaded official sea polygon blocks walking independently of missing or zero terrain",
                    sea["maritimePolygonsLoaded"] > 0 and bool(sea["maritimeHits"]) and sea["collision"] is True,
                    sea)
            require("The water atlas declares nominal sea level without claiming a tidal measurement",
                    maritime["derivation"]["renderSeaLevelMetres"] == 0
                    and all(abs(hit["renderY"] - .02) < 1e-8 for hit in sea["maritimeHits"]),
                    {"nominal_level_metres": maritime["derivation"]["renderSeaLevelMetres"],
                     "render_separation_metres": .02, "raw_terrain": sea["ground"]})
            require("The maritime projected cache stays within its byte budget",
                    maritime["cache"]["bytes"] <= maritime["cache"]["budgetBytes"]
                    and maritime["cache"]["overBudgetBytes"] == 0 and not maritime["errors"], maritime["cache"])

            for name, lat, lon in TARGETS:
                stage(name)
                sector_started = time.monotonic()
                require(name + ": production staging loads actual city sources", debug("v046Load", lat, lon) is True)
                stream = ready()
                report["timings"][name + "_staging_seconds"] = round(time.monotonic() - sector_started, 3)
                # Sample real measured clear points; these coordinates create
                # no geometry and do not replace the source height bank.
                candidates = [[lat + dz / 111320, lon + dx / (111320 * math.cos(math.radians(lat)))]
                              for dz in range(-100, 101, 20) for dx in range(-100, 101, 20)]
                clear = page.evaluate("""points=>{const d=__MISTRAL_DEBUG;return points.map(ll=>{const p=d.v046Project('geo_huveaune',...ll),h=d.v046Height(...ll);return{ll,p,height:h.height,sources:h.sources,clear:Number.isFinite(h.height)&&!h.missing&&!d.v046Collide(p[0],p[2])};}).filter(p=>p.clear);} """, candidates)
                require(name + ": a measured collision-free camera point exists", bool(clear))
                clear.sort(key=lambda p: math.hypot(p["ll"][0] - lat, (p["ll"][1] - lon) * math.cos(math.radians(lat))))
                point = clear[0]
                debug("v018CaptureAt", [point["p"][0], point["height"] + 1.65, point["p"][2]], 0, -.15)
                debug("v050FacadeRefresh")
                debug("v050CityInteriorBind")
                city, facades, interiors = debug("v051CityInfo"), debug("v050FacadeInfo"), debug("v050CityInteriorInfo")
                report["sectors"][name] = {"anchor": [lat, lon], "camera": point, "city": city, "facades": facades,
                                             "doors": interiors["doors"], "origins": stream["origins"]}
                require(name + ": real city buildings and roads are streamed instead of the whole atlas",
                        city["loadedBuildings"] > 0 and city["loadedRoads"] > 0 and 0 < city["loadedPartitions"] < city["tilesAvailable"], city)
                require(name + ": municipal vector and terrain caches remain within their byte budgets",
                        all(city[k]["bytes"] <= city[k]["budgetBytes"] and city[k]["overBudgetBytes"] == 0
                            for k in ("cache", "terrainCache")), {k: city[k] for k in ("cache", "terrainCache")})
                require(name + ": nearby source buildings receive bounded rendered facade details",
                        facades["buildings"] > 0 and facades["visibleBuildings"] > 0 and facades["openings"] > 0
                        and facades["quads"] <= 8192 and facades["cache"]["bytes"] <= 8 * 1024 * 1024
                        and facades["cache"]["entries"] <= 64, facades)
                metric = page.evaluate("""()=>{
                  const d=__MISTRAL_DEBUG, samples=d.v050FacadeInfo().selection.map(s=>d.v050FacadeBuilding(s.id)).filter(s=>s?.rendered&&!s.ringsTruncated).slice(0,4), geometry=d.v018Geometry().filter(g=>g.mesh==='prism'&&g.layer==='building');
                  const sameRing=(a,b)=>{const trim=r=>r.length>1&&Math.hypot(r[0][0]-r.at(-1)[0],r[0][1]-r.at(-1)[1])<1e-7?r.slice(0,-1):r; a=trim(a);b=trim(b);return a.length===b.length&&a.every((p,i)=>Math.hypot(p[0]-b[i][0],p[1]-b[i][1])<1e-7);};
                  return samples.map(s=>({id:s.id,sourceId:s.sourceId,baseY:s.baseY,height:s.height,levels:s.levels,levelHeight:s.levelHeight,levelsBasis:s.levelsBasis,renderedOpenings:s.openings.length,provenance:s.provenance,
                    sourceEnvelopePreserved:geometry.some(g=>Math.abs(g.baseY-s.baseY)<1e-7&&Math.abs(g.height-s.height)<1e-7&&g.rings.length===s.rings.length&&g.rings.every((r,i)=>sameRing(r,s.rings[i]))),
                    openingsWithinSourceFaces:s.openings.every(o=>{const r=s.rings[o.ringIndex],a=r?.[o.edgeIndex],b=r?.[o.edgeIndex+1];return a&&b&&o.width>0&&o.height>0&&o.offset>=0&&o.bottom>=0&&o.offset+o.width<=Math.hypot(b[0]-a[0],b[1]-a[1])+1e-6&&o.bottom+o.height<=s.height+1e-6&&['invented','documented'].includes(o.provenance);})}));
                }""")
                report["sectors"][name]["metric_facade_samples"] = metric
                require(name + ": rendered facade details preserve the actual source outline and metric envelope",
                        bool(metric) and all(s["sourceEnvelopePreserved"] and s["openingsWithinSourceFaces"]
                                             and abs(s["levels"] * s["levelHeight"] - s["height"]) < 1e-7
                                             for s in metric) and any(s["renderedOpenings"] > 0 for s in metric), metric)
                doors = debug("v050FacadeDoors")
                require(name + ": generated doors use plausible metric dimensions and explicit provenance",
                        bool(doors) and all(.78 <= d["width"] <= 20 and 1.85 <= d["height"] <= 20
                                            and d["provenance"] in ("invented", "documented")
                                            and all(finite(v) for k in ("center", "inside", "outside") for v in d[k])
                                            for d in doors), doors[:8])
                require(name + ": actual accessible building portals are available", bool(interiors["doors"]), interiors["doors"][:8])
                if name == "estaque":
                    inside_old = any(r["bbox"][0] <= lat <= r["bbox"][2] and r["bbox"][1] <= lon <= r["bbox"][3]
                                     for r in base_regions)
                    require("Estaque demonstrates actual coverage beyond all eight original base-region rectangles",
                            not inside_old and any("hors du pack" in key for key in stream["origins"]), stream["origins"])
                    land = water_probe(lat, lon)
                    report["maritime"]["land"] = land
                    require("The actual Estaque land point is outside every loaded maritime polygon",
                            land["maritimePolygonsLoaded"] > 0 and not land["maritimeHits"] and finite(land["ground"]["height"]), land)
                shot("02_" + name, "Actual municipal sector; measured diagnostic camera, source buildings and facade LOD")

            stage("interior_ui")
            choices = sorted((d for d in debug("v050CityInteriorInfo")["doors"] if d["levels"] >= 2), key=lambda d: (d["levels"], d["id"]))
            portal = None
            for candidate in choices[:64]:
                if physical_interaction(candidate["id"], "Entrer"):
                    page.wait_for_timeout(200)
                    if debug("v050CityInteriorInfo")["active"]:
                        portal = candidate
                        break
            require("A real multi-storey building is entered through its keyboard portal interaction", portal is not None)
            active = debug("v050CityInteriorInfo")["active"]
            street_floor = active["streetFloor"]
            other_floor = street_floor + 1 if street_floor + 1 < active["levels"] else street_floor - 1
            initial_state = debug("getState")
            return_point = initial_state["v050City"]["returnPoint"]
            entrance_ll = report["entrance_approach"]["latlon"]
            require("Cold Continue is exercised inside a building whose saved street lies beyond the original eight regions",
                    return_point["macro"] == CITY and not any(r["bbox"][0] <= entrance_ll[0] <= r["bbox"][2]
                    and r["bbox"][1] <= entrance_ll[1] <= r["bbox"][3] for r in base_regions),
                    {"latlon": entrance_ll, "return_macro": return_point["macro"]})
            report["interior"] = {"portal": portal, "building": active, "street_floor": street_floor,
                                  "adjacent_floor": other_floor, "return_point": return_point}
            require("Entered building identity, source footprint and explicit invented plan survive the portal",
                    active["id"] == portal["building"] and active["floor"] == street_floor and active["levels"] >= 2
                    and 0 <= street_floor < active["levels"] and 0 <= other_floor < active["levels"]
                    and active["layoutProvenance"] == "invented", active)
            entry_signature = active["signature"]
            capture_here()
            shot("03_interior_entry", "Actual source-footprint building, explicitly invented arrangement at the measured street-entry storey")
            go_to_floor(other_floor)
            upper = debug("v050CityInteriorInfo")["active"]
            report["interior"]["adjacent"] = upper
            require("The landing UI reaches a different storey of the same actual building",
                    upper["id"] == active["id"] and upper["floor"] == other_floor
                    and upper["streetFloor"] == street_floor and upper["signature"] != entry_signature, upper)
            before_reload = debug("getState")
            saved_key, saved = read_saved()
            require("Native localStorage contains the current building, floor and exterior return point",
                    saved is not None and saved["v050City"]["active"]["building"]["id"] == active["id"]
                    and saved["v050City"]["active"]["floor"] == other_floor
                    and saved["v050City"]["active"]["streetFloor"] == street_floor
                    and saved["v050City"]["returnPoint"] == return_point,
                    {"key": saved_key, "floor": saved["v050City"]["active"]["floor"] if saved else None})
            capture_here()
            shot("04_interior_adjacent", "Same building, actual landing UI and a different metric storey")
            stage("native_continue")
            response = page.reload(wait_until="load", timeout=60000)
            require("Reload retains the exact frozen production HTML", sha(response.body()) == args.expect_html_sha)
            page.wait_for_function("!document.getElementById('bootScreen').classList.contains('active')", timeout=120000)
            page.locator("#btnContinue").click()
            page.wait_for_function("n=>__MISTRAL_DEBUG.v050CityInteriorInfo().active?.floor===n", arg=other_floor, timeout=120000)
            restored = debug("v050CityInteriorInfo")["active"]
            report["interior"].update(restored=restored, saved_key=saved_key)
            capture_here()
            debug("v047Control", {"auto": False})
            require("Actual Continue restores the same floor, deterministic plan and source-building identity",
                    restored["id"] == upper["id"] and restored["floor"] == other_floor
                    and restored["streetFloor"] == street_floor and restored["signature"] == upper["signature"], restored)
            require("Continue preserves inventory and the exact geographic return coordinates",
                    debug("getState")["inventory"] == before_reload["inventory"]
                    and debug("getState")["v050City"]["returnPoint"] == return_point)

            stage("finite_loot")
            chests = [c for c in debug("v026Containers") if c["id"].startswith("city:") and sum(c["items"].values()) > 0]
            chosen = None
            for chest in chests:
                if physical_interaction("v026:" + chest["key"], "Fouiller"):
                    chosen = chest
                    break
            require("An actual finite interior reserve can be opened through the proximity interaction", chosen is not None)
            report["interior"]["loot_key"] = chosen["key"]
            page.locator('[data-v26="all"]').click()
            empty = next(c for c in debug("v026Containers") if c["key"] == chosen["key"])
            looted_inventory = debug("getState")["inventory"]
            require("The real loot UI empties the reserve exactly once", all(n == 0 for n in empty["items"].values())
                    and looted_inventory != before_reload["inventory"], {"key": chosen["key"], "before": chosen["items"], "after": empty["items"]})
            require("An emptied reserve disables repeated take-all", page.locator('[data-v26="all"]').is_disabled())
            page.locator('[data-v26="close"]').click()
            go_to_floor(street_floor)
            go_to_floor(other_floor)
            revisited = next(c for c in debug("v026Containers") if c["key"] == chosen["key"])
            require("Rebuilding the storey preserves its emptied reserve and finite inventory",
                    all(n == 0 for n in revisited["items"].values()) and debug("getState")["inventory"] == looted_inventory)
            go_to_floor(street_floor)
            require("Street-entry storey reconstructs the same deterministic actual-footprint plan",
                    debug("v050CityInteriorInfo")["active"]["signature"] == entry_signature)
            stage("return_exterior")
            landing()
            page.get_by_role("button", name="Sortir vers la rue", exact=True).click()
            ready()
            page.wait_for_function("!__MISTRAL_DEBUG.v050CityInteriorInfo().exitPending && __MISTRAL_DEBUG.v050CityInteriorInfo().active===null", timeout=120000)
            require("The landing dialog closes when the player returns to the street", page.locator("#dialogue").is_hidden())
            exterior = debug("getState")
            ll = debug("v046LL")
            report["interior"].update(returned_position=exterior["player"]["pos"], returned_ground=debug("v046Height", *ll),
                                      returned_latlon=ll, inventory_preserved=exterior["inventory"] == looted_inventory,
                                      return_point_cleared=exterior["v050City"]["returnPoint"] is None)
            require("The actual exterior return restores the saved entrance coordinates and inventory",
                    math.dist(exterior["player"]["pos"], return_point["pos"]) < .2
                    and exterior["inventory"] == looted_inventory
                    and exterior["v050City"]["returnPoint"] is None,
                    {"expected": return_point, "actual": exterior["player"]["pos"],
                     "ground": report["interior"]["returned_ground"], "entrance_approach": report.get("entrance_approach"),
                     "inventory_preserved": report["interior"]["inventory_preserved"],
                     "return_point_cleared": report["interior"]["return_point_cleared"]})
            capture_here()
            shot("05_return_estaque", "Real reloaded municipal exterior at the conserved entrance position")
            report["final_city"] = debug("v051CityInfo")
            report["final_interior"] = debug("v050CityInteriorInfo")
            require("No city hash, fetch, staging or interior transaction exception was recorded",
                    not report["final_city"]["errors"] and not report["final_interior"]["errors"])
            require("No installed municipal source HTTP request failed", not report["local_http_errors"], report["local_http_errors"])
            require("No global JavaScript exception occurred", not report["page_errors"], report["page_errors"])
            context.close()
            browser.close()
        stage("complete")
    except Exception:
        report["exception"] = traceback.format_exc()
        check("The native municipal architecture pilot completes", False, report["exception"])
        print(report["exception"], flush=True)
        if page is not None and not page.is_closed():
            try:
                shot("FAILURE", "Actual UI at the failure; no synthetic replacement")
            except Exception:
                pass
    finally:
        if server:
            server.shutdown()
            server.server_close()
        if worker:
            worker.join(timeout=5)
        if frozen:
            changed = [{"path": str(path.relative_to(ROOT)), "before_sha256": sha(raw),
                        "after_sha256": sha(path.read_bytes()) if path.exists() else None}
                       for path, raw in frozen.items() if not path.exists() or path.read_bytes() != raw]
            check("Production HTML, all three city indices and official boundary stayed unchanged",
                  not changed, changed)
        save()
    print(json.dumps({key: report[key] for key in ("passed", "failed", "total", "stage")}))
    return int(bool(report["failed"] or report["page_errors"] or report.get("stage") != "complete"))


if __name__ == "__main__":
    raise SystemExit(main())
