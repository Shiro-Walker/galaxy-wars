# core/player.py
"""
Player Manager for Galaxy: Fractured Dawn

Handles:
- Player data (stats, cargo, credits, missions)
- Ship ownership and upgrades
- Save/load persistent single-player data
- Cargo management
- Module bonuses (cargo, shields, power)
"""

import json
import os
from typing import Dict

from core.utils import type_out, print_divider
from core.modules import MODULES


# ---------------------------------------------------------------------------
# SAVE SYSTEM
# ---------------------------------------------------------------------------

SAVE_DIR = "saves"
PLAYER_SAVE = os.path.join(SAVE_DIR, "player.json")


def new_player(name: str = "ShiroWalker") -> Dict:
    """Create a new player profile with starter ship and stats."""
    player = {
        "name": name,
        "credits": 1000,
        "location": "System-01",
        "docked_at": None,
        "fuel": 100,
        "ammo": 50,
        "hull": 100,
        "armor": 100,
        "shields": 100,
        "cargo": {},
        "missions": {"active": {}, "completed": [], "story": {}},
        "ship": "Rifter",
        "ship_data": {
            "modules": 4,
            "cargo_capacity": 50,
            "power_grid": 100,
        },
        "ship_modules": ["Pulse Laser", "Basic Mining Drill"],
        "insurance": False,
        "debt": 0,
    }
    save_player(player)
    return player


def save_player(player: Dict):
    """Save player data to file."""
    os.makedirs(SAVE_DIR, exist_ok=True)
    with open(PLAYER_SAVE, "w") as f:
        json.dump(player, f, indent=2)


def load_player() -> Dict:
    """Load player from disk or create a new one if missing."""
    os.makedirs(SAVE_DIR, exist_ok=True)
    if not os.path.exists(PLAYER_SAVE):
        type_out("No save found. Creating new pilot profile...")
        return new_player()
    with open(PLAYER_SAVE, "r") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# CARGO MANAGEMENT
# ---------------------------------------------------------------------------

def add_cargo(player: Dict, item: str, qty: int) -> bool:
    """Add item to cargo hold if space allows."""
    cap = get_cargo_capacity(player)
    current = sum(player.get("cargo", {}).values())
    if current + qty > cap:
        type_out(f"⚠️ Not enough cargo space! {cap - current} units free.")
        return False
    player["cargo"][item] = player.get("cargo", {}).get(item, 0) + qty
    save_player(player)
    return True


def remove_cargo(player: Dict, item: str, qty: int) -> bool:
    """Remove item from cargo hold."""
    if player.get("cargo", {}).get(item, 0) < qty:
        return False
    player["cargo"][item] -= qty
    if player["cargo"][item] <= 0:
        del player["cargo"][item]
    save_player(player)
    return True


def show_cargo(player: Dict):
    """Display cargo contents."""
    print_divider("=")
    type_out("� Cargo Manifest:")
    if not player["cargo"]:
        type_out("Empty.")
        return
    total = sum(player["cargo"].values())
    cap = get_cargo_capacity(player)
    for item, qty in player["cargo"].items():
        type_out(f"- {item}: {qty}")
    type_out(f"Total: {total}/{cap}")
    print_divider("=")


def get_cargo_capacity(player: Dict) -> int:
    """Calculate total cargo space (base + module bonuses)."""
    base = player["ship_data"].get("cargo_capacity", 50)
    for mod_name in player.get("ship_modules", []):
        mod = MODULES.get(mod_name)
        if mod and mod.get("type") == "utility":
            bonus = mod.get("effect", {}).get("cargo_bonus", 0)
            base += bonus
    return base


# ---------------------------------------------------------------------------
# SHIP & MODULE SYSTEM
# ---------------------------------------------------------------------------

def get_player_ship(player: Dict) -> Dict:
    """Return player's current ship data including module effects."""
    ship = player["ship_data"].copy()
    # Apply bonuses from modules
    for mod_name in player.get("ship_modules", []):
        mod = MODULES.get(mod_name, {})
        if mod.get("type") == "utility":
            eff = mod.get("effect", {})
            for stat, bonus in eff.items():
                if stat == "shield_bonus":
                    player["shields"] += bonus
                elif stat == "power_bonus":
                    ship["power_grid"] += bonus
    return ship


def repair_ship(player: Dict, cost_per_hp: int = 5):
    """Repair damaged hull for credits."""
    missing = 100 - player["hull"]
    if missing <= 0:
        type_out("Ship hull fully intact.")
        return
    cost = missing * cost_per_hp
    if player["credits"] < cost:
        type_out("Not enough credits to fully repair hull.")
        affordable = player["credits"] // cost_per_hp
        player["hull"] += affordable
        player["credits"] = 0
        type_out(f"Repaired {affordable} HP of hull.")
    else:
        player["credits"] -= cost
        player["hull"] = 100
        type_out("Hull fully repaired.")
    save_player(player)


def refuel_ship(player: Dict, cost_per_unit: int = 3):
    """Refuel ship using credits."""
    missing = 100 - player["fuel"]
    if missing <= 0:
        type_out("Fuel tanks full.")
        return
    cost = missing * cost_per_unit
    if player["credits"] < cost:
        affordable = player["credits"] // cost_per_unit
        player["fuel"] += affordable
        player["credits"] = 0
        type_out(f"Refueled {affordable} units of fuel.")
    else:
        player["credits"] -= cost
        player["fuel"] = 100
        type_out("Ship fully refueled.")
    save_player(player)


def insure_ship(player: Dict, cost: int = 1000):
    """Buy insurance for current ship."""
    if player["insurance"]:
        type_out("Insurance already active.")
        return
    if player["credits"] < cost:
        type_out("Not enough credits for insurance.")
        return
    player["credits"] -= cost
    player["insurance"] = True
    type_out("✅ Ship insurance purchased.")
    save_player(player)


def handle_ship_loss(player: Dict):
    """Handle when the ship is destroyed."""
    if player["insurance"]:
        type_out("� Insurance claim processed: new starter ship issued.")
        player["ship"] = "Rifter"
        player["ship_data"] = {"modules": 4, "cargo_capacity": 50, "power_grid": 100}
        player["hull"] = 100
        player["insurance"] = False
        player["ship_modules"] = ["Pulse Laser", "Basic Mining Drill"]
    else:
        type_out("❌ Ship destroyed — no insurance! A replacement is loaned to you.")
        player["debt"] += 2000
        player["credits"] = max(0, player["credits"] - 500)
        player["ship"] = "Rifter"
        player["ship_data"] = {"modules": 4, "cargo_capacity": 50, "power_grid": 100}
        player["hull"] = 100
        player["ship_modules"] = ["Pulse Laser", "Basic Mining Drill"]
    save_player(player)


def show_player_status(player: Dict):
    """Display player stats and ship info."""
    print_divider("=")
    type_out(f"Pilot: {player['name']}")
    type_out(f"Credits: {player['credits']:,} | Debt: {player.get('debt',0):,}")
    type_out(f"Location: {player['location']}")
    type_out(f"Fuel: {player['fuel']} | Ammo: {player['ammo']}")
    type_out(f"Hull: {player['hull']} | Armor: {player['armor']} | Shields: {player['shields']}")
    type_out(f"Ship: {player['ship']} | Modules: {len(player.get('ship_modules', []))}/{player['ship_data']['modules']}")
    print_divider("=")
