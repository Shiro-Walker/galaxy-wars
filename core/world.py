# core/world.py
"""
Galaxy Map & System Data for Galaxy: Fractured Dawn

Defines:
- 40 unique star systems
- Faction territories and trade hubs
- Stations and asteroid belts
- System connection map for travel routes
"""

import os
import json
import random
from core.utils import type_out

DATA_DIR = "data"
GALAXY_PATH = os.path.join(DATA_DIR, "galaxy_map.json")


# ---------------------------------------------------------------------------
# FACTIONS
# ---------------------------------------------------------------------------

FACTIONS = [
    "Federation Core",
    "Outer Colonies",
    "Independent Frontier",
    "Pirate Sectors",
    "Corporate Syndicate",
]


# ---------------------------------------------------------------------------
# GALAXY GENERATION
# ---------------------------------------------------------------------------

def _generate_galaxy_map() -> dict:
    """Create a 40-system static galaxy layout (1-time generation)."""
    systems = {}
    for i in range(1, 41):
        name = f"System-{i:02d}"
        faction = random.choice(FACTIONS)
        num_stations = random.randint(1, 3)
        num_belts = random.randint(1, 4)

        systems[name] = {
            "name": name,
            "faction": faction,
            "stations": [f"{name} Station {n}" for n in range(1, num_stations + 1)],
            "belts": [f"{name} Belt {b}" for b in range(1, num_belts + 1)],
            "connections": [],
        }

    # Connect systems roughly in clusters
    names = list(systems.keys())
    for idx, name in enumerate(names):
        possible_links = random.sample(names, k=random.randint(2, 4))
        for link in possible_links:
            if link != name and link not in systems[name]["connections"]:
                systems[name]["connections"].append(link)
                systems[link]["connections"].append(name)

    return systems


def _save_galaxy(systems: dict):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(GALAXY_PATH, "w") as f:
        json.dump(systems, f, indent=2)


def load_galaxy_map() -> dict:
    """Load the galaxy map, or generate it if missing."""
    if not os.path.exists(GALAXY_PATH):
        systems = _generate_galaxy_map()
        _save_galaxy(systems)
        type_out("� Galaxy map generated and saved.")
        return systems
    with open(GALAXY_PATH, "r") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# WORLD QUERIES
# ---------------------------------------------------------------------------

def get_system_info(system_name: str) -> dict:
    """Return system info by name."""
    galaxy = load_galaxy_map()
    return galaxy.get(system_name, {})


def get_connections(system_name: str) -> list:
    """Return travel routes for a system."""
    galaxy = load_galaxy_map()
    return galaxy.get(system_name, {}).get("connections", [])


def list_belts(system_name: str) -> list:
    """Return asteroid belts in system."""
    galaxy = load_galaxy_map()
    return galaxy.get(system_name, {}).get("belts", [])


def list_stations(system_name: str) -> list:
    """Return station list in system."""
    galaxy = load_galaxy_map()
    return galaxy.get(system_name, {}).get("stations", [])


# ---------------------------------------------------------------------------
# UTILITY
# ---------------------------------------------------------------------------

def describe_galaxy():
    """Print a quick overview of factions and system counts."""
    galaxy = load_galaxy_map()
    faction_count = {}
    for sys in galaxy.values():
        faction = sys["faction"]
        faction_count[faction] = faction_count.get(faction, 0) + 1

    type_out("=== Galaxy Overview ===")
    for f, count in faction_count.items():
        type_out(f"{f}: {count} systems")

SYSTEMS = {
    "Sol Station": {"faction": "Federation", "population": "High", "belts": ["Veldspar Belt", "Omber Field"]},
    "Alpha Centauri": {"faction": "Neutral Zone", "population": "Medium", "belts": ["Scordite Ridge"]},
    "Vega": {"faction": "Independent", "population": "Low", "belts": ["Kernite Basin", "Pyroxeres Field"]},
}

CONNECTIONS = {
    "Sol Station": ["Alpha Centauri", "Sirius"],
    "Alpha Centauri": ["Sol Station", "Vega"],
    "Vega": ["Alpha Centauri"],
}


def get_system_info(name: str) -> dict:
    return SYSTEMS.get(name, {})


def get_connections(name: str) -> list:
    return CONNECTIONS.get(name, [])
