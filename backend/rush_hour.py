#!/usr/bin/env python3
"""Day-1 MVP: given an origin + destination, tell you the rush hour windows.

Uses TomTom's Routing API predictive traffic (departAt in the future is
supported and returns a traffic-model estimate). For each sampled hour we
compare travelTimeInSeconds (with traffic) to noTrafficTravelTimeInSeconds
(without) — a ratio > threshold means that hour is congested.

Takes coordinates, not addresses — TomTom's free-tier geocoding has weak
Pakistan coverage (collapses distinct Lahore addresses to the same city
centroid), so address resolution is left to the caller (e.g. a map picker).

Usage:
    export TOMTOM_API_KEY=...
    python3 rush_hour.py "31.5820,74.3299" "31.5075,74.3453"
"""
import argparse
import os
import sys
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv

ROUTING_URL = "https://api.tomtom.com/routing/1/calculateRoute/{coords}/json"


class RushHourError(Exception):
    """Raised when the traffic API can't answer (bad key, bad coordinates, etc.)."""


def fetch_hourly_ratios(origin: str, destination: str, api_key: str,
                         start_hour: int = 6, end_hour: int = 22) -> list[tuple[int, float]]:
    """Query one hour at a time for tomorrow (safely in the future) and
    return [(hour, travelTimeInSeconds / noTrafficTravelTimeInSeconds), ...].
    origin/destination are "lat,lon" strings."""
    tomorrow = datetime.now() + timedelta(days=1)
    ratios = []
    for hour in range(start_hour, end_hour + 1):
        departure = tomorrow.replace(hour=hour, minute=0, second=0, microsecond=0)
        url = ROUTING_URL.format(coords=f"{origin}:{destination}")
        resp = requests.get(url, params={
            "key": api_key,
            "traffic": "true",
            "departAt": departure.strftime("%Y-%m-%dT%H:%M:%S"),
            "computeTravelTimeFor": "all",
        }, timeout=10)
        if resp.status_code != 200:
            raise RushHourError(f"TomTom API error {resp.status_code}: {resp.text[:200]}")
        routes = resp.json().get("routes")
        if not routes:
            continue
        summary = routes[0]["summary"]
        duration = summary["noTrafficTravelTimeInSeconds"]
        duration_in_traffic = summary["travelTimeInSeconds"]
        ratios.append((hour, duration_in_traffic / duration))
    return ratios


def classify_rush_hours(hour_ratios: list[tuple[int, float]], threshold: float = 1.15) -> list[tuple[int, int]]:
    """Collapse consecutive congested hours (ratio > threshold) into windows."""
    windows = []
    window_start = None
    prev_hour = None
    for hour, ratio in hour_ratios:
        congested = ratio > threshold
        if congested and window_start is None:
            window_start = hour
        elif not congested and window_start is not None:
            windows.append((window_start, prev_hour + 1))
            window_start = None
        prev_hour = hour
    if window_start is not None:
        windows.append((window_start, prev_hour + 1))
    return windows


def format_windows(windows: list[tuple[int, int]]) -> str:
    if not windows:
        return "No significant rush hour congestion detected."

    def fmt_hour(h):
        suffix = "am" if h < 12 else "pm"
        h12 = h % 12 or 12
        return f"{h12}{suffix}"

    return "Peak traffic " + ", ".join(f"{fmt_hour(s)}-{fmt_hour(e)}" for s, e in windows)


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Find rush hour windows between two points.")
    parser.add_argument("origin", help='"lat,lon"')
    parser.add_argument("destination", help='"lat,lon"')
    parser.add_argument("--threshold", type=float, default=1.15,
                         help="traffic/no-traffic duration ratio that counts as congested")
    args = parser.parse_args()

    api_key = os.environ.get("TOMTOM_API_KEY")
    if not api_key:
        sys.exit("Set TOMTOM_API_KEY in your environment first.")

    try:
        ratios = fetch_hourly_ratios(args.origin, args.destination, api_key)
    except RushHourError as e:
        sys.exit(str(e))
    if not ratios:
        sys.exit("No traffic data returned — check the coordinates are on a road TomTom can route.")

    windows = classify_rush_hours(ratios, args.threshold)
    print(format_windows(windows))
    print("\nHourly detail:")
    for hour, ratio in ratios:
        flag = " <-- congested" if ratio > args.threshold else ""
        print(f"  {hour:02d}:00  ratio={ratio:.2f}{flag}")


if __name__ == "__main__":
    main()
