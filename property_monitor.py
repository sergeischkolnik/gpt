# -*- coding: utf-8 -*-
"""
Monitor rental listings on Funda.nl and Pararius.nl for specific search criteria.
The script periodically queries both sites for houses for rent in Delft and
Delfgauw (minimum 3 rooms, maximum €2750) and reports any new listings.

Due to the environment restrictions this script cannot be executed here, but it
shows how one could implement such a monitor using only the Python standard
library.
"""

import json
import re
import time
import urllib.request
import urllib.parse
from datetime import datetime
from typing import Dict, List, Tuple

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122 Safari/537.36"
)
HEADERS = {"User-Agent": USER_AGENT}

# URLs for the searches. These may require adjustment if the sites change their
# query parameters.
FUNDA_URL = (
    "https://www.funda.nl/en/huur/{city}/huis/3-kamers/?price=0-2750"
)
PARARIUS_URL = (
    "https://www.pararius.com/apartments/{city}/3-rooms/0-2750"
)

DATA_FILE = "listings.json"
CHECK_INTERVAL = 1800  # 30 minutes


def fetch(url: str) -> str:
    """Return the contents of *url* as text using urllib."""
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def parse_funda(html: str) -> List[Tuple[str, str]]:
    """Extract listing ids and urls from Funda search result HTML."""
    listings = []
    # Funda listing links typically look like /en/huur/delft/<slug>/some-id/
    for match in re.finditer(r"href=\"(/en/huur/[^\"]+/\d+)/\"", html):
        url = urllib.parse.urljoin("https://www.funda.nl", match.group(1))
        listing_id = match.group(1).rstrip("/").split("/")[-1]
        listings.append((listing_id, url))
    return listings


def parse_pararius(html: str) -> List[Tuple[str, str]]:
    """Extract listing ids and urls from Pararius search result HTML."""
    listings = []
    # Pararius listing links typically contain /property/ followed by an id.
    for match in re.finditer(r"href=\"(https://www.pararius.com/[^\"]+/property-\d+)\"", html):
        url = match.group(1)
        listing_id = url.split("-")[-1]
        listings.append((listing_id, url))
    return listings


def load_previous() -> Dict[str, Dict[str, str]]:
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return {}


def save_listings(data: Dict[str, Dict[str, str]]) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def search_site(site: str, city: str) -> List[Tuple[str, str]]:
    if site == "funda":
        url = FUNDA_URL.format(city=urllib.parse.quote(city))
        html = fetch(url)
        return parse_funda(html)
    elif site == "pararius":
        url = PARARIUS_URL.format(city=urllib.parse.quote(city))
        html = fetch(url)
        return parse_pararius(html)
    else:
        raise ValueError(f"Unknown site: {site}")


def check_for_new_listings() -> None:
    previous = load_previous()
    current = {"funda": {}, "pararius": {}}
    for site in current.keys():
        for city in ("delft", "delfgauw"):
            try:
                listings = search_site(site, city)
            except Exception as exc:
                print(f"Error fetching {site} for {city}: {exc}")
                continue
            for listing_id, url in listings:
                current[site][listing_id] = url
                if listing_id not in previous.get(site, {}):
                    print(
                        f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] "
                        f"New listing on {site} ({city}): {url}"
                    )
    save_listings(current)


def main() -> None:
    while True:
        check_for_new_listings()
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
