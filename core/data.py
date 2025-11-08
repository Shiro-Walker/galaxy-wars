# core/data.py
"""
Static data definitions for Galaxy: Fractured Dawn.

Contains:
- Ship blueprints (inspired by Galaxy on Fire HD)
- Basic economy commodities
- Default starter configuration
"""

from typing import Dict, List

# ---------------------------------------------------------------------------
# SHIPS
# ---------------------------------------------------------------------------

DEFAULT_STARTER_SHIP = "Rifter"

SHIPS: Dict[str, Dict] = {
    # === FRIGATES ===
    "Rifter": {
        "class": "Frigate",
        "price": 0,
        "module_slots": 4,
        "base_modules": ["Basic Laser Cannon", "Basic Mining Drill"],
        "max_fuel": 120,
        "hull": 75,
        "armor": 30,
        "shields": 20,
        "speed": 8,
        "cargo_capacity": 60,
        "desc": "A dependable starter ship often used by rookie pilots."
    },
    "Viper": {
        "class": "Frigate",
        "price": 1800,
        "module_slots": 6,
        "base_modules": ["Pulse Laser", "Basic Mining Drill"],
        "max_fuel": 150,
        "hull": 90,
        "armor": 35,
        "shields": 25,
        "speed": 9,
        "cargo_capacity": 70,
        "desc": "A fast and agile fighter used by bounty hunters."
    },
    "Nova Scout": {
        "class": "Frigate",
        "price": 2200,
        "module_slots": 6,
        "base_modules": ["Light Railgun", "Basic Mining Drill"],
        "max_fuel": 140,
        "hull": 85,
        "armor": 32,
        "shields": 28,
        "speed": 10,
        "cargo_capacity": 65,
        "desc": "Lightly armored but extremely maneuverable recon craft."
    },

    # === CORVETTES ===
    "Raptor": {
        "class": "Corvette",
        "price": 3400,
        "module_slots": 8,
        "base_modules": ["Auto Cannon", "IMT Extract 2.7"],
        "max_fuel": 160,
        "hull": 110,
        "armor": 45,
        "shields": 36,
        "speed": 7,
        "cargo_capacity": 110,
        "desc": "A balanced mid-tier ship popular among mercenaries."
    },
    "Falchion": {
        "class": "Corvette",
        "price": 3900,
        "module_slots": 8,
        "base_modules": ["Medium Plasma Blaster", "IMT Extract 2.7"],
        "max_fuel": 170,
        "hull": 120,
        "armor": 42,
        "shields": 44,
        "speed": 7,
        "cargo_capacity": 120,
        "desc": "A Corvette-class ship optimized for energy weapon specialists."
    },

    # === DESTROYERS ===
    "Drake": {
        "class": "Destroyer",
        "price": 5200,
        "module_slots": 10,
        "base_modules": ["Heavy Railgun", "Gunant's Drill"],
        "max_fuel": 185,
        "hull": 150,
        "armor": 58,
        "shields": 52,
        "speed": 6,
        "cargo_capacity": 140,
        "desc": "A powerful destroyer-class vessel capable of heavy damage."
    },
    "Zephyr": {
        "class": "Destroyer",
        "price": 5600,
        "module_slots": 10,
        "base_modules": ["Heavy Plasma Array", "Gunant's Drill"],
        "max_fuel": 190,
        "hull": 160,
        "armor": 55,
        "shields": 60,
        "speed": 6,
        "cargo_capacity": 150,
        "desc": "A high-tech destroyer featuring advanced plasma weaponry."
    },

    # === CRUISERS ===
    "Aegis": {
        "class": "Cruiser",
        "price": 7800,
        "module_slots": 14,
        "base_modules": ["Dual Medium Plasma", "Advanced Mining Drill"],
        "max_fuel": 210,
        "hull": 200,
        "armor": 75,
        "shields": 82,
        "speed": 5,
        "cargo_capacity": 220,
        "desc": "A heavy cruiser with advanced shield systems and room for upgrades."
    },
    "Onyx": {
        "class": "Cruiser",
        "price": 7400,
        "module_slots": 14,
        "base_modules": ["Dual Auto Cannon", "Advanced Mining Drill"],
        "max_fuel": 215,
        "hull": 195,
        "armor": 78,
        "shields": 76,
        "speed": 5,
        "cargo_capacity": 210,
        "desc": "Favored by private military contractors for its rugged reliability."
    },

    # === BATTLESHIPS ===
    "Basilisk": {
        "class": "Battleship",
        "price": 10500,
        "module_slots": 18,
        "base_modules": ["Heavy Beam Array", "Advanced Mining Drill", "Cargo Pod"],
        "max_fuel": 260,
        "hull": 260,
        "armor": 95,
        "shields": 110,
        "speed": 4,
        "cargo_capacity": 320,
        "desc": "A fearsome battleship that dominates the field with raw energy output."
    },
    "Marauder": {
        "class": "Battleship",
        "price": 12500,
        "module_slots": 18,
        "base_modules": ["Oblivion Rail Batteries", "Advanced Mining Drill", "Cargo Pod"],
        "max_fuel": 270,
        "hull": 280,
        "armor": 105,
        "shields": 120,
        "speed": 4,
        "cargo_capacity": 340,
        "desc": "A dreadnought-class warship, slow but devastating."
    },

    # === FREIGHTERS ===
    "Atlas": {
        "class": "Freighter",
        "price": 9000,
        "module_slots": 16,
        "base_modules": ["Cargo Pod", "Cargo Pod", "Basic Mining Drill"],
        "max_fuel": 320,
        "hull": 180,
        "armor": 68,
        "shields": 50,
        "speed": 4,
        "cargo_capacity": 700,
        "desc": "A long-range hauler capable of massive cargo loads."
    },
    "Erebus": {
        "class": "Freighter",
        "price": 12000,
        "module_slots": 18,
        "base_modules": ["Cargo Pod", "IMT Extract 2.9", "Advanced Mining Drill"],
        "max_fuel": 340,
        "hull": 220,
        "armor": 75,
        "shields": 62,
        "speed": 3,
        "cargo_capacity": 850,
        "desc": "Top-tier heavy freighter designed for inter-sector trade."
    },
}

# ---------------------------------------------------------------------------
# ECONOMY ITEMS (ORES, REFINING, COMMODITIES)
# ---------------------------------------------------------------------------

ORES: Dict[str, Dict] = {
    "Veldspar": {"type": "ore", "base_value": 15, "rarity": "F"},
    "Scordite": {"type": "ore", "base_value": 22, "rarity": "E"},
    "Pyroxeres": {"type": "ore", "base_value": 35, "rarity": "D"},
    "Omber": {"type": "ore", "base_value": 50, "rarity": "C"},
    "Kernite": {"type": "ore", "base_value": 75, "rarity": "B"},
    "Plagioclase": {"type": "ore", "base_value": 90, "rarity": "A"},
    "Hedbergite": {"type": "ore", "base_value": 120, "rarity": "S"},
}

REFINED: Dict[str, Dict] = {
    "Tritanium": {"type": "refined", "base_value": 45},
    "Pyerite": {"type": "refined", "base_value": 60},
    "Mexallon": {"type": "refined", "base_value": 95},
    "Isogen": {"type": "refined", "base_value": 120},
    "Nocxium": {"type": "refined", "base_value": 160},
}

MODULES: List[str] = [
    "Basic Laser Cannon", "Pulse Laser", "Heavy Railgun", "Plasma Blaster",
    "Auto Cannon", "Cargo Pod", "Basic Mining Drill", "IMT Extract 2.7",
    "IMT Extract 2.9", "Advanced Mining Drill", "Shield Booster", "Hull Repair Unit"
]

# ---------------------------------------------------------------------------
# STARTER DATA
# ---------------------------------------------------------------------------

STARTER_PLAYER = {
    "name": "Rookie",
    "credits": 1000,
    "ship": DEFAULT_STARTER_SHIP,
    "cargo": {},
    "location": "Terra Station",
    "fuel": 100,
    "missions": {"story": {}, "side": {}, "bounties": {}},
}
