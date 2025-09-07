# scripts/common.py
# Minimal helper utilities shared by the demo scripts.
# Deps: pandas, shapely, requests

from __future__ import annotations
import os, re, time, math, json
from pathlib import Path
import requests

def find_data_file(name: str) -> str:
    """
    Look for a CSV either in ./data/<name> or ./<name>.
    Returns the best existing path as a string; otherwise returns the preferred ./data/<name> path
    (so scripts write outputs there by default).
    """
    p1 = Path("data") / name
    p2 = Path(name)
    if p1.exists():
        return str(p1)
    if p2.exists():
        return str(p2)
    # by default, prefer ./data/<name>
    Path("data").mkdir(parents=True, exist_ok=True)
    return str(p1)

# ---------------------------
# Geometry helpers (EWKT/WKT)
# ---------------------------
def strip_srid(geom: str) -> str:
    """Turn 'SRID=4326;WKT...' into 'WKT...'"""
    if not isinstance(geom, str):
        return geom
    if geom.startswith("SRID="):
        return geom.split(";", 1)[1]
    return geom

# ---------------------------
# HTTP session with retries
# ---------------------------
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def make_retry_session(retries: int = 5, backoff: float = 1.0) -> requests.Session:
    retry = Retry(
        total=retries, connect=retries, read=retries,
        backoff_factor=backoff, status_forcelist=(429,500,502,503,504),
        allowed_methods=frozenset(["GET"]), raise_on_status=False
    )
    s = requests.Session()
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.mount("http://",  HTTPAdapter(max_retries=retry))
    return s
