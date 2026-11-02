#!/usr/bin/env python3
"""Convert a local, georeferenced GeoTIFF DEM into a bounded WGS84 node grid.

Nearest source cells are sampled without interpolation or NoData filling. This
is an explicit reprojection/resampling step, not a claim of native 1:1 detail.
Install requirements-geo.txt in a virtual environment to enable this tool.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import tempfile

MAX_GRID_CELLS = 1_048_576
MAX_WINDOW_CELLS = 16_777_216
MAX_INPUT_BYTES = 2 * 1024**3
MAX_OUTPUT_BYTES = 64 * 1024**2


class DemConversionError(ValueError):
    """The raster cannot be sampled within the supported data contract."""


def checked_bbox(bbox):
    if not isinstance(bbox, (list, tuple)) or len(bbox) != 4:
        raise DemConversionError("bbox must be south,west,north,east")
    if any(type(v) not in (int, float) or not math.isfinite(v) for v in bbox):
        raise DemConversionError("bbox coordinates must be finite")
    south, west, north, east = map(float, bbox)
    if not (-90 < south < north < 90 and -180 <= west < east <= 180):
        raise DemConversionError("bbox must be a non-inverted WGS84 extent without an antimeridian crossing")
    return [south, west, north, east]


def grid_shape(bbox, spacing):
    """Use local WGS84 curvature to bound nominal east/west and north/south steps."""
    if type(spacing) not in (int, float) or not math.isfinite(spacing) or spacing <= 0:
        raise DemConversionError("spacing must be a positive finite number of metres")
    south, west, north, east = checked_bbox(bbox)
    lat = math.radians((south + north) / 2)
    eccentricity_squared = 6.6943799901413165e-3
    base = 1 - eccentricity_squared * math.sin(lat) ** 2
    prime_vertical = 6378137 / math.sqrt(base)
    meridian = 6378137 * (1 - eccentricity_squared) / base**1.5
    width_metres = math.radians(east - west) * prime_vertical * math.cos(lat)
    height_metres = math.radians(north - south) * meridian
    x_intervals = max(1, math.ceil(width_metres / spacing))
    y_intervals = max(1, math.ceil(height_metres / spacing))
    width, height = x_intervals + 1, y_intervals + 1
    if width * height > MAX_GRID_CELLS:
        raise DemConversionError(f"requested output exceeds the {MAX_GRID_CELLS} sample budget; reduce bbox or increase spacing")
    return width, height, [width_metres / x_intervals, height_metres / y_intervals]


def file_sha256(path):
    digest = hashlib.sha256()
    size = 0
    with Path(path).open("rb") as stream:
        while chunk := stream.read(4 * 1024**2):
            size += len(chunk)
            if size > MAX_INPUT_BYTES:
                raise DemConversionError("input grew beyond the supported byte limit")
            digest.update(chunk)
    return digest.hexdigest()


def convert_dem(path, bbox, spacing, vertical_datum, source_crs=None):
    """Return importer-compatible JSON; read only the source window actually used.

    Requested nodes outside the raster remain null. At least one measured node
    must be available. Native NoData/masks and non-finite samples always remain
    null, including when a finer output repeats native cells.
    """
    try:
        import numpy as np
        import rasterio
        from rasterio.warp import transform, transform_bounds
        from rasterio.windows import Window
    except ImportError as error:
        raise DemConversionError("optional GIS dependencies missing; install requirements-geo.txt in a virtual environment") from error

    path = Path(path)
    if not path.is_file() or not 0 < path.stat().st_size <= MAX_INPUT_BYTES:
        raise DemConversionError(f"input must be a nonempty local file of at most {MAX_INPUT_BYTES} bytes")
    initial_stat = path.stat()
    bbox = checked_bbox(bbox)
    if not isinstance(vertical_datum, str) or not vertical_datum.strip() or len(vertical_datum) > 256:
        raise DemConversionError("an explicit vertical datum for metre altitudes is required")
    vertical_datum = vertical_datum.strip()
    width, height, actual_spacing = grid_shape(bbox, spacing)
    south, west, north, east = bbox

    try:
        with rasterio.Env(GDAL_PAM_ENABLED="NO"), rasterio.open(path, sharing=False) as dataset:
            if dataset.driver != "GTiff":
                raise DemConversionError("input must be a local GeoTIFF, not a VRT or another raster driver")
            if dataset.count != 1:
                raise DemConversionError("DEM must contain exactly one elevation band")
            dtype = np.dtype(dataset.dtypes[0])
            if not np.issubdtype(dtype, np.number) or np.issubdtype(dtype, np.complexfloating):
                raise DemConversionError("elevation band must contain real numeric samples")
            if dataset.crs is None:
                raise DemConversionError("GeoTIFF needs an explicit recognized EPSG CRS; no CRS is guessed")
            effective_crs = dataset.crs
            if source_crs is not None:
                effective_crs = rasterio.crs.CRS.from_user_input(source_crs)
                if effective_crs.to_epsg() is None:
                    raise DemConversionError("source CRS override must be a recognized EPSG identifier")
                if dataset.crs.to_epsg() is not None and dataset.crs.to_epsg() != effective_crs.to_epsg():
                    raise DemConversionError("source CRS override conflicts with the recognized GeoTIFF CRS")
            if effective_crs.to_epsg() is None:
                raise DemConversionError("GeoTIFF needs an explicit recognized EPSG CRS; supply --source-crs only from documented source metadata")
            crs = "EPSG:" + str(effective_crs.to_epsg())
            affine = dataset.transform
            if not all(math.isfinite(value) for value in affine[:6]) or affine.a <= 0 or affine.e >= 0 or abs(affine.b) > 1e-12 or abs(affine.d) > 1e-12:
                raise DemConversionError("GeoTIFF must have a north-up rectified grid; reproject rotated rasters explicitly first")
            unit = dataset.units[0]
            if unit and unit.casefold() not in ("m", "metre", "metres", "meter", "meters"):
                raise DemConversionError("elevation band must use metres; no vertical unit conversion is inferred")
            source_bounds = transform_bounds(effective_crs, "EPSG:4326", *dataset.bounds, densify_pts=21)
            source_west, source_south, source_east, source_north = source_bounds
            if not (west < source_east and east > source_west and south < source_north and north > source_south):
                raise DemConversionError("requested bbox does not overlap the source raster")

            longitudes = np.tile(np.linspace(west, east, width), height)
            latitudes = np.repeat(np.linspace(north, south, height), width)
            xs, ys = transform("EPSG:4326", effective_crs, longitudes.tolist(), latitudes.tolist())
            xs, ys = np.asarray(xs), np.asarray(ys)
            if not np.isfinite(xs).all() or not np.isfinite(ys).all():
                raise DemConversionError("bbox cannot be transformed into the raster CRS")
            cols = np.floor((xs - affine.c) / affine.a).astype(np.int64)
            rows = np.floor((ys - affine.f) / affine.e).astype(np.int64)
            inside = (cols >= 0) & (cols < dataset.width) & (rows >= 0) & (rows < dataset.height)
            if not inside.any():
                raise DemConversionError("requested grid has no nodes inside the source raster")
            first_col, last_col = int(cols[inside].min()), int(cols[inside].max())
            first_row, last_row = int(rows[inside].min()), int(rows[inside].max())
            window_width, window_height = last_col - first_col + 1, last_row - first_row + 1
            if window_width * window_height > MAX_WINDOW_CELLS:
                raise DemConversionError(f"source crop exceeds {MAX_WINDOW_CELLS} cells; convert a smaller bbox")
            samples = dataset.read(1, window=Window(first_col, first_row, window_width, window_height), masked=True)
            local_rows, local_cols = rows[inside] - first_row, cols[inside] - first_col
            source_values = samples.data[local_rows, local_cols].astype(np.float64)
            source_mask = np.ma.getmaskarray(samples)[local_rows, local_cols]
            scale, offset = float(dataset.scales[0]), float(dataset.offsets[0])
            if not math.isfinite(scale) or not math.isfinite(offset) or scale == 0:
                raise DemConversionError("invalid elevation band scale or offset")
            source_values = source_values * scale + offset
            source_mask |= ~np.isfinite(source_values)
            if ((~source_mask) & ((source_values <= -100) | (source_values >= 9000))).any():
                raise DemConversionError("unmasked elevation lies outside the game altitude range (-100,9000)m; check NoData and vertical units")
            output = np.full(width * height, np.nan)
            output[np.flatnonzero(inside)[~source_mask]] = source_values[~source_mask]
            valid = int(np.isfinite(output).sum())
            if not valid:
                raise DemConversionError("requested grid contains no measured altitude; NoData is not filled")
            values = [float(value) if math.isfinite(value) else None for value in output]
            receipt = {
                "format": "GeoTIFF", "inputSha256": file_sha256(path), "crs": crs,
                "nativePixelSize": [abs(affine.a), abs(affine.e)],
                "nativeTransform": [affine.a, affine.b, affine.c, affine.d, affine.e, affine.f],
                "sourceSize": [dataset.width, dataset.height], "resampling": "nearest",
                "sampleConvention": "WGS84 regular nodes", "requestedSpacingMeters": float(spacing),
                "actualSpacingMeters": actual_spacing, "resampled": True, "nodataPreserved": True,
                "verticalDatum": vertical_datum,
            }
            final_stat = path.stat()
            if (initial_stat.st_size, initial_stat.st_mtime_ns, initial_stat.st_ino) != (final_stat.st_size, final_stat.st_mtime_ns, final_stat.st_ino):
                raise DemConversionError("source changed during conversion; no output is published")
    except DemConversionError:
        raise
    except (OSError, ValueError, rasterio.errors.RasterioError) as error:
        raise DemConversionError(f"cannot read or transform GeoTIFF: {error}") from error
    return {
        "width": width, "height": height, "bbox": bbox, "rowOrder": "north-to-south",
        "values": values, "verticalDatum": vertical_datum, "validPoints": valid,
        "missingPoints": width * height - valid, "conversion": receipt,
    }


def write_grid(path, grid, replace=False):
    path = Path(path)
    if path.exists() and not replace:
        raise DemConversionError("output exists; choose another path or explicitly use --replace")
    raw = (json.dumps(grid, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + "\n").encode()
    if len(raw) > MAX_OUTPUT_BYTES:
        raise DemConversionError("output exceeds the importer byte budget")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix="." + path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        if replace:
            os.replace(temporary, path)
        else:
            # A concurrent conversion must not overwrite a file created after
            # the initial existence check. Both files are on the same volume.
            os.link(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def parse_bbox(text):
    try:
        return checked_bbox([float(value) for value in text.split(",")])
    except (ValueError, DemConversionError) as error:
        raise argparse.ArgumentTypeError(str(error)) from error


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Local native DEM GeoTIFF; never a remote URL")
    parser.add_argument("--bbox", required=True, type=parse_bbox, help="WGS84 south,west,north,east of sample nodes")
    parser.add_argument("--spacing", required=True, type=float, help="Nominal maximum grid step in metres (local WGS84 curvature approximation)")
    parser.add_argument("--vertical-datum", required=True, help="Explicit source datum, e.g. NGF-IGN69; does not transform heights")
    parser.add_argument("--source-crs", help="Explicit documented EPSG CRS for an unrecognized GeoTIFF WKT; never inferred from coordinates")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--replace", action="store_true", help="Explicitly replace an existing converted output")
    args = parser.parse_args(argv)
    try:
        if args.input.resolve() == args.output.resolve():
            raise DemConversionError("output must not replace the source GeoTIFF")
        if args.output.exists() and not args.replace:
            raise DemConversionError("output exists; choose another path or explicitly use --replace")
        result = convert_dem(args.input, args.bbox, args.spacing, args.vertical_datum, args.source_crs)
        write_grid(args.output, result, args.replace)
    except (DemConversionError, OSError) as error:
        print(f"Conversion refusée : {error}", file=sys.stderr)
        return 1
    print(json.dumps({"output": str(args.output), "width": result["width"], "height": result["height"],
                      "valid": result["validPoints"], "missing": result["missingPoints"],
                      "resampling": "nearest", "resampled": True, "inputSha256": result["conversion"]["inputSha256"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
