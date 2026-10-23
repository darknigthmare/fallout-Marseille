#!/usr/bin/env python3
"""Discover and acquire one official IGN LiDAR HD MNT tile and a measured patch.

The Atom catalogue is inspected first. Current LiDAR MNT exports are discovered
through the official WFS metadata layer, whose url_mnt supplies the complete
GetMap GeoTIFF URL; no dated tile/download URL is manufactured. TLS and the
inherited proxy remain enabled. Only data.geopf.fr URLs are followed.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import re
import tempfile
import time
from urllib.parse import parse_qs, urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener
import xml.etree.ElementTree as ET

from convert_ign_dem import DemConversionError, checked_bbox, convert_dem, grid_shape, parse_bbox, write_grid

HOST = "data.geopf.fr"
ATOM = "http://www.w3.org/2005/Atom"
GPF = "https://data.geopf.fr/annexes/ressources/xsd/gpf_dl.xsd"
WFS = "http://www.opengis.net/wfs/2.0"
METADATA_LAYER = "IGNF_LIDAR-HD_METADONNEE:metadata"
MNT_LAYER = "IGNF_LIDAR-HD_MNT_ELEVATION.ELEVATIONGRIDCOVERAGE.LAMB93"
MAX_XML_BYTES = 32 * 1024**2
MAX_DOWNLOAD_BYTES = 500 * 1024**2
MAX_PATCH_CELLS = 262_144


class AcquisitionError(ValueError):
    pass


def checked_url(url):
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname != HOST or parsed.username or parsed.password or parsed.fragment or parsed.port not in (None, 443):
        raise AcquisitionError("only HTTPS data.geopf.fr URLs are supported; any new download hostname needs environment configuration")
    if not parsed.path.startswith(("/telechargement/", "/wfs/", "/wms-r")):
        raise AcquisitionError("URL is outside the documented IGN catalogue, WFS or raster services")
    return url


class ScopedRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        checked_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class Client:
    def __init__(self, timeout=90):
        self.timeout = timeout
        self.last_request = 0.
        self.opener = build_opener(ScopedRedirects())

    def open(self, url):
        checked_url(url)
        delay = .25 - (time.monotonic() - self.last_request)
        if delay > 0:
            time.sleep(delay)
        self.last_request = time.monotonic()
        return self.opener.open(Request(url, headers={"User-Agent": "Fallout-Mistral-NativeDEM/0.50"}), timeout=self.timeout)

    def read(self, url, maximum=MAX_XML_BYTES):
        with self.open(url) as response:
            declared = response.headers.get("Content-Length")
            if declared is not None and int(declared) > maximum:
                raise AcquisitionError("declared response exceeds the byte budget")
            raw = response.read(maximum + 1)
            if len(raw) > maximum:
                raise AcquisitionError("response exceeds the byte budget")
            if declared is not None and len(raw) != int(declared):
                raise AcquisitionError("response byte count differs from Content-Length")
            return raw


def xml(raw):
    if b"<!DOCTYPE" in raw.upper() or b"<!ENTITY" in raw.upper():
        raise AcquisitionError("XML declarations with entities are not accepted")
    try:
        return ET.fromstring(raw)
    except ET.ParseError as error:
        raise AcquisitionError(f"incomplete or invalid service XML: {error}") from error


def atom_page(raw):
    root = xml(raw)
    if root.tag != "{" + ATOM + "}feed":
        raise AcquisitionError("catalogue response is not an Atom feed")
    try:
        page = int(root.attrib["{" + GPF + "}page"])
        pages = int(root.attrib["{" + GPF + "}pagecount"])
        total = int(root.attrib["{" + GPF + "}totalentries"])
    except (KeyError, ValueError) as error:
        raise AcquisitionError("catalogue pagination is missing") from error
    if not 1 <= page <= pages <= 20 or not 0 <= total <= 1000:
        raise AcquisitionError("catalogue exceeds the supported discovery budget")
    entries = []
    for item in root.findall("{" + ATOM + "}entry"):
        title = item.findtext("{" + ATOM + "}title", "")
        links = [checked_url(link.attrib["href"]) for link in item.findall("{" + ATOM + "}link")
                 if link.get("type") == "application/atom+xml" and link.get("href")]
        entries.append({"title": title, "links": links})
    return page, pages, total, entries


def discover_catalogue(client, output):
    result, expected_pages, expected_total = [], None, None
    page = 1
    while expected_pages is None or page <= expected_pages:
        url = "https://data.geopf.fr/telechargement/capabilities?" + urlencode({"limit": 50, "page": page})
        raw = client.read(url)
        observed, pages, total, entries = atom_page(raw)
        if observed != page or expected_pages is not None and (pages != expected_pages or total != expected_total):
            raise AcquisitionError("catalogue changed or pagination was ignored during discovery")
        expected_pages, expected_total = pages, total
        result.extend(entries)
        (output / f"catalogue-page-{page}.xml").write_bytes(raw)
        page += 1
    if len(result) != expected_total:
        raise AcquisitionError("catalogue page counts do not match the reported total")
    return {"resources": expected_total, "pages": expected_pages,
            "lidarResources": [entry for entry in result if "lidar" in entry["title"].lower()]}


def ring_contains(ring, lon, lat):
    inside = False
    for i in range(len(ring)):
        x, y = ring[i][:2]
        xx, yy = ring[i - 1][:2]
        if (y > lat) != (yy > lat) and lon < (xx - x) * (lat - y) / (yy - y) + x:
            inside = not inside
    return inside


def geometry_contains(geometry, lon, lat):
    kind, coordinates = geometry.get("type"), geometry.get("coordinates")
    polygons = [coordinates] if kind == "Polygon" else coordinates if kind == "MultiPolygon" else []
    try:
        return any(rings and ring_contains(rings[0], lon, lat) and not any(ring_contains(hole, lon, lat) for hole in rings[1:]) for rings in polygons)
    except (TypeError, ValueError, IndexError):
        raise AcquisitionError("metadata coverage polygon is invalid")


def native_request(url):
    checked_url(url)
    params = {key.upper(): values for key, values in parse_qs(urlsplit(url).query).items()}
    required = {"SERVICE": "WMS", "REQUEST": "GetMap", "CRS": "EPSG:2154", "LAYERS": MNT_LAYER, "FORMAT": "image/geotiff"}
    for key, value in required.items():
        if params.get(key) != [value]:
            raise AcquisitionError(f"metadata MNT URL has an unsupported {key}")
    try:
        bounds = [float(value) for value in params["BBOX"][0].split(",")]
        width, height = int(params["WIDTH"][0]), int(params["HEIGHT"][0])
        filename = params["FILENAME"][0]
    except (KeyError, IndexError, ValueError) as error:
        raise AcquisitionError("metadata MNT URL lacks a bounded raster request") from error
    if len(bounds) != 4 or not all(math.isfinite(v) for v in bounds) or bounds[0] >= bounds[2] or bounds[1] >= bounds[3]:
        raise AcquisitionError("invalid native raster bounds")
    if not 2 <= width <= 8192 or not 2 <= height <= 8192 or width * height > 16_777_216:
        raise AcquisitionError("native raster exceeds the supported tile budget")
    if not re.fullmatch(r"[A-Za-z0-9_.-]{1,180}\.tif", filename):
        raise AcquisitionError("unsafe native raster filename")
    return {"bounds": bounds, "size": [width, height], "filename": filename, "crs": "EPSG:2154"}


def select_tile(payload, bbox):
    if not isinstance(payload, dict) or payload.get("type") != "FeatureCollection" or not isinstance(payload.get("features"), list):
        raise AcquisitionError("metadata response is not a GeoJSON FeatureCollection")
    features = payload["features"]
    if payload.get("numberMatched") != len(features) or len(features) > 32:
        raise AcquisitionError("metadata query was truncated; use a smaller patch")
    south, west, north, east = checked_bbox(bbox)
    probes = [(west, south), (west, north), (east, south), (east, north), ((west + east) / 2, (south + north) / 2)]
    for feature in features:
        properties = feature.get("properties", {})
        geometry = feature.get("geometry", {})
        if properties.get("systeme_planimetrique") != "LAMB93" or properties.get("systeme_altimetrique") != "IGN69":
            continue
        if all(geometry_contains(geometry, lon, lat) for lon, lat in probes):
            request = native_request(properties.get("url_mnt", ""))
            return feature, request
    raise AcquisitionError("no single native MNT tile covers the requested patch; reduce the bbox or acquire neighboring tiles separately")


def download(client, url, directory, filename):
    descriptor, temporary = tempfile.mkstemp(prefix=".native-dem-", suffix=".part", dir=directory)
    size, digest = 0, hashlib.sha256()
    try:
        with os.fdopen(descriptor, "wb") as target, client.open(url) as response:
            expected = response.headers.get("Content-Length")
            if expected is not None and not 0 < int(expected) <= MAX_DOWNLOAD_BYTES:
                raise AcquisitionError("native tile exceeds the download budget")
            while chunk := response.read(1024**2):
                size += len(chunk)
                if size > MAX_DOWNLOAD_BYTES:
                    raise AcquisitionError("native tile exceeds the download budget")
                digest.update(chunk)
                target.write(chunk)
            if not size or expected is not None and size != int(expected):
                raise AcquisitionError("native tile response is empty or truncated")
            target.flush()
            os.fsync(target.fileno())
        sha = digest.hexdigest()
        path = directory / (sha[:16] + "-" + filename)
        if path.exists():
            if hashlib.sha256(path.read_bytes()).hexdigest() != sha:
                raise AcquisitionError("existing content-addressed tile is corrupt")
        else:
            os.link(temporary, path)
        return path, sha, size
    finally:
        Path(temporary).unlink(missing_ok=True)


def acquire(bbox, spacing, output, timeout=90):
    import rasterio
    bbox = checked_bbox(bbox)
    width, height, _ = grid_shape(bbox, spacing)
    if width * height > MAX_PATCH_CELLS:
        raise AcquisitionError(f"requested native patch exceeds {MAX_PATCH_CELLS} nodes; reduce bbox or increase spacing")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    client = Client(timeout)
    catalogue = discover_catalogue(client, output)
    capabilities_url = "https://data.geopf.fr/wfs/ows?" + urlencode({"service": "WFS", "version": "2.0.0", "request": "GetCapabilities"})
    raw = client.read(capabilities_url)
    capabilities = xml(raw)
    names = {node.text for node in capabilities.findall(".//{" + WFS + "}FeatureType/{" + WFS + "}Name")}
    if METADATA_LAYER not in names:
        raise AcquisitionError("official WFS does not announce the LiDAR metadata layer")
    (output / "wfs-capabilities.xml").write_bytes(raw)
    south, west, north, east = bbox
    params = {"service": "WFS", "version": "2.0.0", "request": "GetFeature", "typenames": METADATA_LAYER,
              "srsName": "urn:ogc:def:crs:OGC:1.3:CRS84", "bbox": f"{west},{south},{east},{north},urn:ogc:def:crs:OGC:1.3:CRS84",
              "count": 32, "outputFormat": "application/json"}
    metadata_url = "https://data.geopf.fr/wfs/ows?" + urlencode(params)
    raw = client.read(metadata_url, 2 * 1024**2)
    payload = json.loads(raw)
    feature, request = select_tile(payload, bbox)
    (output / "lidar-metadata.json").write_bytes(raw)
    url = feature["properties"]["url_mnt"]
    tile, sha, size = download(client, url, output, request["filename"])
    with rasterio.open(tile) as raster:
        expected = request["bounds"]
        if raster.driver != "GTiff" or raster.count != 1 or raster.dtypes[0] not in ("float32", "float64"):
            raise AcquisitionError("official MNT response is not a single-band numeric elevation GeoTIFF")
        if [raster.width, raster.height] != request["size"] or any(abs(a - b) > .00001 for a, b in zip(raster.bounds, expected)):
            raise AcquisitionError("GeoTIFF dimensions or bounds differ from the metadata request")
        header = {"wkt": raster.crs.to_wkt() if raster.crs else None, "epsg": raster.crs.to_epsg() if raster.crs else None,
                  "nativePixelSize": list(raster.res), "nodata": raster.nodata}
    grid = convert_dem(tile, bbox, spacing, "NGF-IGN69", source_crs=request["crs"])
    identity = hashlib.sha256(json.dumps({"bbox": bbox, "spacing": spacing}).encode()).hexdigest()[:12]
    grid_path = output / f"{sha[:16]}-{identity}-grid.json"
    if not grid_path.exists():
        write_grid(grid_path, grid)
    elif json.loads(grid_path.read_text()) != grid:
        raise AcquisitionError("existing converted grid differs from the verified source conversion")
    receipt = {"provider": "IGN", "product": "MNT LiDAR HD", "catalogue": catalogue,
               "discovery": "Catalogue Atom + actual WFS metadata url_mnt export; no guessed tile URL",
               "metadataUrl": metadata_url, "metadataFeature": feature, "downloadUrl": url,
               "downloadedAt": dt.datetime.now(dt.timezone.utc).isoformat(), "tile": str(tile), "bytes": size,
               "sha256": sha, "upstreamChecksum": None, "checksumScope": "SHA-256 of bytes received over verified HTTPS; no upstream checksum was supplied",
               "license": "Licence Ouverte 2.0", "attribution": "IGN — LiDAR HD", "nativeRequest": request,
               "nativeHeader": header, "effectiveCrs": request["crs"], "crsOverrideExplicit": header["epsg"] is None,
               "verticalDatum": "NGF-IGN69", "patch": str(grid_path), "bbox": bbox,
               "width": grid["width"], "height": grid["height"], "validPoints": grid["validPoints"], "missingPoints": grid["missingPoints"],
               "resampling": "nearest", "resampled": True}
    (output / "ACQUISITION.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bbox", type=parse_bbox, required=True, help="Patch sample nodes south,west,north,east in WGS84")
    parser.add_argument("--spacing", type=float, default=.5, help="Nominal sampled patch spacing in metres")
    parser.add_argument("--output", type=Path, required=True, help="Local acquisition/cache directory outside tracked source files")
    parser.add_argument("--timeout", type=float, default=90)
    args = parser.parse_args(argv)
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error("timeout must be positive")
    try:
        result = acquire(args.bbox, args.spacing, args.output, args.timeout)
    except (AcquisitionError, DemConversionError, OSError, ValueError, ET.ParseError, ImportError) as error:
        print(f"Acquisition refusée : {error}", file=__import__("sys").stderr)
        return 1
    print(json.dumps({key: result[key] for key in ("tile", "patch", "sha256", "bytes", "width", "height", "validPoints", "missingPoints", "resampling")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
