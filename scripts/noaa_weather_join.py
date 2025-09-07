# scripts/noaa_join.py
"""
Join NOAA daily weather to geo events (by event date).
Inputs  : geo_events_sample.csv  (repo root or ./data/)
Outputs : data/events_with_noaa.csv
Deps    : pandas, requests (no geo deps needed here)
Env     : NOAA_TOKEN must be set (https://www.ncdc.noaa.gov/cdo-web/token)
"""
from __future__ import annotations
import os, time, math
import pandas as pd
from pathlib import Path
import requests
from common import find_data_file, make_retry_session

from dotenv import load_dotenv
load_dotenv()  # load variables from .env if present

NCEI_BASE = "https://www.ncei.noaa.gov/cdo-web/api/v2"

def ncei_request(path: str, params: dict, token: str, timeout=(10,120), session=None):
    session = session or make_retry_session()
    url = f"{NCEI_BASE}/{path}"
    headers = {"token": token}
    manual_retries = 2
    for i in range(manual_retries + 1):
        try:
            r = session.get(url, headers=headers, params=params, timeout=timeout)
            r.raise_for_status()
            return r.json()
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
            if i < manual_retries:
                time.sleep(2 * (i + 1))
                continue
            raise
        except requests.HTTPError:
            raise RuntimeError(f"NCEI HTTP {r.status_code}: {r.text[:400]}")

def bbox_from_point(lat: float, lon: float, km: float = 50.0):
    dlat = km / 111.0
    dlon = km / (111.0 * max(0.1, math.cos(math.radians(lat))))
    return (lon - dlon, lat - dlat, lon + dlon, lat + dlat)

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    from math import radians, sin, cos, asin, sqrt
    p1, p2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlmb = radians(lon2 - lon1)
    a = sin(dphi/2)**2 + cos(p1)*cos(p2)*sin(dlmb/2)**2
    return 2 * R * asin(sqrt(a))

def find_nearest_station(lat, lon, start, end, token, datasetid="GHCND", km=50, session=None):
    session = session or make_retry_session()
    minlon, minlat, maxlon, maxlat = bbox_from_point(lat, lon, km)
    js = ncei_request(
        "stations",
        {
            "datasetid": datasetid,
            "extent": f"{minlat},{minlon},{maxlat},{maxlon}",
            "startdate": start,
            "enddate": end,
            "limit": 1000,
        },
        token, session=session
    )
    results = js.get("results", []) if isinstance(js, dict) else []
    if not results:
        return None
    best = min(results, key=lambda s: haversine_km(lat, lon, s.get("latitude"), s.get("longitude")))
    best = dict(best)
    best["dist_km"] = haversine_km(lat, lon, best["latitude"], best["longitude"])
    return best

def fetch_daily_chunked(stationid, start, end, token, datatypes=("TMAX","TMIN","PRCP","WSF2"), chunk_days=30, limit=1000, session=None):
    session = session or make_retry_session()
    start_dt = pd.to_datetime(start).normalize()
    end_dt   = pd.to_datetime(end).normalize()
    frames = []
    current = start_dt
    while current <= end_dt:
        chunk_end = min(current + pd.Timedelta(days=chunk_days-1), end_dt)
        params = {
            "datasetid": "GHCND",
            "stationid": stationid,
            "startdate": current.strftime("%Y-%m-%d"),
            "enddate":   chunk_end.strftime("%Y-%m-%d"),
            "units": "standard",
            "limit": limit,
            "datatypeid": list(datatypes),
        }
        try:
            js = ncei_request("data", params, token, timeout=(10,120), session=session)
            res = js.get("results", []) if isinstance(js, dict) else []
            if res:
                frames.append(pd.DataFrame(res))
        except Exception as e:
            print(f"[WARN] NOAA chunk {current.date()}..{chunk_end.date()} failed: {e}")
        current = chunk_end + pd.Timedelta(days=1)

    if not frames:
        return pd.DataFrame(columns=["date"])
    df = pd.concat(frames, ignore_index=True).drop_duplicates()
    df["date"] = pd.to_datetime(df["date"], utc=True, errors="coerce").dt.tz_convert(None).dt.normalize()
    df = df.pivot_table(index="date", columns="datatype", values="value", aggfunc="first").reset_index()
    df.columns.name = None
    return df

def main():
    token = os.environ.get("NOAA_TOKEN")
    if not token:
        raise SystemExit("Please set NOAA_TOKEN (https://www.ncdc.noaa.gov/cdo-web/token)")

    events_path = find_data_file("geo_events_sample.csv")
    out_path = Path(find_data_file("events_with_noaa.csv"))
    print(f"[i] Reading events: {events_path}")
    events = pd.read_csv(events_path)

    # Parse event times; sample uses naive microsecond strings
    events["_event_dt"] = pd.to_datetime(
        events["date_modified"].fillna(events["date_created"]),
        utc=True, errors="coerce"
    ).dt.tz_convert(None)

    # Window with 1-day padding, strict (no fallback)
    evt_min, evt_max = events["_event_dt"].min(), events["_event_dt"].max()
    if pd.isna(evt_min) or pd.isna(evt_max):
        raise SystemExit(
            "No valid event timestamps found. Please clean your data or supply --start-date/--end-date."
        )

    start = (evt_min - pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    end   = (evt_max + pd.Timedelta(days=1)).strftime("%Y-%m-%d")

    # Representative point: median lat/lng
    nonnull = events.dropna(subset=["lat","lng"]).copy()
    nonnull["lat"] = pd.to_numeric(nonnull["lat"], errors="coerce")
    nonnull["lng"] = pd.to_numeric(nonnull["lng"], errors="coerce")
    mid_lat, mid_lng = float(nonnull["lat"].median()), float(nonnull["lng"].median())

    print(f"[i] Date window: {start}..{end}")
    print(f"[i] Finding nearest GHCND station near ({mid_lat:.4f},{mid_lng:.4f})")
    station = find_nearest_station(mid_lat, mid_lng, start, end, token, km=50)
    if station is None:
        raise SystemExit("No nearby GHCND station found; increase km or adjust dates.")

    print(f"[i] Station: {station.get('id')}  dist≈{station.get('dist_km'):.2f} km")
    daily = fetch_daily_chunked(station["id"], start, end, token, datatypes=("TMAX","TMIN","PRCP","WSF2"), chunk_days=30)
    if daily.empty:
        raise SystemExit("No NOAA daily observations for this window.")

    daily["noaa_date"] = pd.to_datetime(daily["date"], errors="coerce").dt.date
    events["_event_date"] = events["_event_dt"].dt.date

    joined = events.merge(daily, left_on="_event_date", right_on="noaa_date", how="left")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    joined.to_csv(out_path, index=False)
    print(f"[✓] Wrote {out_path}  rows={len(joined)}")

if __name__ == "__main__":
    main()
