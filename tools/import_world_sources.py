#!/usr/bin/env python3
"""Import supplied measured sources, offline, without rewriting the base map."""
from pathlib import Path
import argparse
import json
import sys

from world_sources import SourceError, bounded_bytes, decode_json, provenance, publish_bundle, read_geojson, read_terrain

ROOT = Path(__file__).resolve().parents[1]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--region", required=True, help="Existing macro identifier, e.g. geo_huveaune")
    parser.add_argument("--geojson", type=Path, help="Source FeatureCollection with buildings and/or roads")
    parser.add_argument("--terrain", type=Path, help="Source regular grid, JSON or ESRI ASCII")
    parser.add_argument("--terrain-format", choices=("json", "ascii"), default="json")
    parser.add_argument("--crs", choices=("EPSG:4326", "EPSG:2154"), default="EPSG:4326", help="GeoJSON input CRS; terrain input must be EPSG:4326")
    parser.add_argument("--source", required=True, help="Actual source/provider name, not an inferred certification")
    parser.add_argument("--resource", default="local-survey", help="Stable declared provider resource identifier")
    parser.add_argument("--license", required=True)
    parser.add_argument("--attribution", required=True)
    parser.add_argument("--acquired-at", required=True, help="Source acquisition date YYYY-MM-DD")
    parser.add_argument("--source-url", help="Public source citation; never fetched")
    parser.add_argument("--vertical-datum", help="Required for terrain and 3D features, e.g. NGF-IGN69")
    parser.add_argument("--output", type=Path, default=ROOT / "data/map_pack/enrichment")
    mutation = parser.add_mutually_exclusive_group()
    mutation.add_argument("--replace", action="store_true", help="Explicitly replace this region's active enrichment, retaining old bundles")
    mutation.add_argument("--merge", action="store_true", help="Keep existing measured terrain and other source objects while merging this import")
    args = parser.parse_args(argv)
    if args.geojson is None and args.terrain is None:
        parser.error("provide --geojson and/or --terrain")
    try:
        manifest = decode_json(bounded_bytes(ROOT / "data/map_pack/terrain/manifest_v039.json"))
        regions = {r["macro"]: r["bbox"] for r in manifest["regions"]}
        if args.region not in regions:
            raise SourceError("region is not part of the supplied territory manifest")
        source = provenance(name=args.source, license=args.license, attribution=args.attribution, acquired_at=args.acquired_at,
                            resource=args.resource, url=args.source_url, vertical_datum=args.vertical_datum)
        features = read_geojson(bounded_bytes(args.geojson), source, regions[args.region], args.crs) if args.geojson else []
        terrain = read_terrain(bounded_bytes(args.terrain), args.region, source, regions[args.region], args.terrain_format) if args.terrain else None
        result = publish_bundle(args.output, args.region, source, features=features, terrain=terrain, replace=args.replace, merge=args.merge)
    except (SourceError, OSError, KeyError, TypeError) as error:
        print(f"Import refusé : {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
