"""Address -> "lat,lon" via Nominatim (OpenStreetMap), free and keyless."""
import re

import requests

GEOCODE_URL = "https://nominatim.openstreetmap.org/search"
HEADERS = {"User-Agent": "rush-hour-agent"}

_COORD_RE = re.compile(r"^\s*-?\d+(\.\d+)?\s*,\s*-?\d+(\.\d+)?\s*$")


class GeocodeError(Exception):
    """Raised when an address can't be resolved to coordinates."""


def geocode(location: str) -> str:
    """Returns "lat,lon". Pass-through if `location` is already coordinates."""
    if _COORD_RE.match(location):
        return location

    resp = requests.get(GEOCODE_URL, params={
        "q": location,
        "format": "json",
        "limit": 1,
    }, headers=HEADERS, timeout=10)
    if resp.status_code != 200:
        raise GeocodeError(f"Geocoding API error {resp.status_code}: {resp.text[:200]}")

    results = resp.json()
    if not results:
        raise GeocodeError(f'Could not find a location for "{location}".')

    return f"{results[0]['lat']},{results[0]['lon']}"
