# scripts/osm_amenities.py
"""
Tiny OSM amenity demo around each perimeter centroid.
Inputs  : perimeter_sample.csv  (repo root or ./data/)
Outputs : data/osm_amenities.csv
Deps    : pandas, shapely, requests
Note    : Overpass is a public API; be gentle (simple queries + small radius).
"""
from __future__ import annotations
import sys, json, time
import pandas as pd
from pathlib import Path
import requests
from shapely import wkt
from shapely.geometry import shape
from shapely.ops import unary_union
from common import find_data_file, strip_srid, make_retry_session

from dotenv import load_dotenv
load_dotenv()  # load variables from .env if present

OVERPASS = "https://overpass-api.de/api/interpreter"

def query_overpass(amenities, lat, lon, radius_m=3000, session=None):
    """
    Query nodes with the given amenities within a radius of (lat,lon).
    Returns list of dicts with osm_id, name, amenity, lat, lon.
    """
    session = session or make_retry_session()
    # Build OR filter for amenities
    amenity_filters = "".join([f'node(around:{radius_m},{lat},{lon})["amenity"="{a}"];' for a in amenities])
    q = f"""
    [out:json][timeout:25];
    (
      {amenity_filters}
    );
    out center;
    """
    r = session.get(OVERPASS, params={"data": q})
    r.raise_for_status()
    data = r.json()
    rows = []
    for el in data.get("elements", []):
        tags = el.get("tags", {})
        rows.append({
            "osm_id": f'{el.get("type")}:{el.get("id")}',
            "name": tags.get("name", ""),
            "amenity": tags.get("amenity", ""),
            "lat": el.get("lat") if "lat" in el else el.get("center",{}).get("lat"),
            "lon": el.get("lon") if "lon" in el else el.get("center",{}).get("lon"),
        })
    return rows

def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--amenities", type=str, default="fire_station,hospital,police,school",
                    help="Comma-separated list of amenity keys to count (default: fire_station,hospital,police,school)")
    ap.add_argument("--radius-km", type=float, default=5.0, help="Search radius in kilometers (default: 5km)")
    args = ap.parse_args(argv)

    perim_path = find_data_file("perimeter_sample.csv")
    out_path = Path(find_data_file("osm_amenities.csv"))
    print(f"[i] Reading perimeters: {perim_path}")
    perims = pd.read_csv(perim_path, dtype=str)

    # Compute centroids from EWKT/WKT
    centroids = []
    for i, row in perims.iterrows():
        wkt_text = strip_srid(row.get("geom",""))
        if not wkt_text:
            continue
        try:
            geom = wkt.loads(wkt_text)
            c = geom.representative_point() if geom.is_empty else geom.centroid
            centroids.append((i+1, c.y, c.x))  # (perim_id, lat, lon)
        except Exception as e:
            print(f"[WARN] Failed WKT parse on row {i}: {e}"); continue

    amenities = [a.strip() for a in args.amenities.split(",") if a.strip()]
    radius_m = int(args.radius_km * 1000)

    session = make_retry_session()
    all_rows = []
    for perim_id, lat, lon in centroids:
        print(f"[i] OSM near perimeter {perim_id} at ({lat:.5f},{lon:.5f})  r={args.radius_km}km")
        try:
            rows = query_overpass(amenities, lat, lon, radius_m=radius_m, session=session)
            for r in rows:
                r["perim_id"] = perim_id
            all_rows.extend(rows)
            time.sleep(1.2)  # be nice to Overpass
        except Exception as e:
            print(f"[WARN] Overpass failed for perimeter {perim_id}: {e}")

    df = pd.DataFrame(all_rows, columns=["osm_id","name","amenity","lat","lon","perim_id"])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"[✓] Wrote {out_path}  rows={len(df)}")

    # quick pivot summary
    if not df.empty:
        piv = (df.groupby(["perim_id","amenity"]).size().reset_index(name="count"))
        print(piv.head())

if __name__ == "__main__":
    main()
