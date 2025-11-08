# core/modules.py
"""
Module & Equipment System for Galaxy: Fractured Dawn

Handles:
- Ship modules: weapons, mining drills, cargo, utility, passenger holds
- Defines stats for combat, mining, and support
- Helper functions to manage module installation, removal, and info display
"""

from core.utils import type_out, print_divider


# ---------------------------------------------------------------------------
# MODULE DEFINITIONS
# ---------------------------------------------------------------------------

MODULES = {
    # --- Weapons (Energy, Kinetic, Blast) ---
    "Pulse Laser": {
        "type": "weapon",
        "damage_type": "energy",
        "damage": (12, 22),
        "ammo_use": 0,
        "power_use": 15,
        "desc": "Standard ship laser, reliable mid-range energy weapon.",
    },
    "Mass Driver": {
        "type": "weapon",
        "damage_type": "kinetic",
        "damage": (8, 16),
        "ammo_use": 2,
        "power_use": 5,
        "desc": "Kinetic slug thrower, uses ammo but effective against armor.",
    },
    "Plasma Cannon": {
        "type": "weapon",
        "damage_type": "blast",
        "damage": (16, 28),
        "ammo_use": 3,
        "power_use": 12,
        "desc": "High-damage plasma bolt weapon; heavy power and ammo usage.",
    },
    "Beam Lance": {
        "type": "weapon",
        "damage_type": "energy",
        "damage": (24, 38),
        "ammo_use": 0,
        "power_use": 20,
        "desc": "Advanced beam weapon that cuts through armor at close range.",
    },

    # --- Mining Equipment ---
    "Basic Mining Drill": {
        "type": "mining",
        "power_use": 5,
        "efficiency": 1.0,
        "desc": "Entry-level mining laser with standard yield output.",
    },
    "Advanced Drill": {
        "type": "mining",
        "power_use": 8,
        "efficiency": 1.4,
        "desc": "Improved mining rig for faster extraction and better yields.",
    },
    "Industrial Excavator": {
        "type": "mining",
        "power_use": 15,
        "efficiency": 2.0,
        "desc": "Heavy-duty mining unit, optimized for rich ore belts.",
    },

    # --- Utility Modules ---
    "Cargo Pod": {
        "type": "utility",
        "effect": {"cargo_bonus": 25},
        "desc": "Increases cargo capacity by +25 units.",
    },
    "Medium Cargo Bay": {
        "type": "utility",
        "effect": {"cargo_bonus": 60},
        "desc": "Expanded cargo space for trade or transport.",
    },
    "Passenger Hold": {
        "type": "utility",
        "effect": {"passenger_capacity": 10},
        "desc": "Allows for carrying passengers on missions.",
    },
    "Shield Booster": {
        "type": "utility",
        "effect": {"shield_bonus": 15},
        "desc": "Improves total shield capacity.",
    },
    "Reactor Upgrade": {
        "type": "utility",
        "effect": {"power_bonus": 10},
        "desc": "Increases base power grid output for sustained combat.",
    },
    "Nanite Repair Bay": {
        "type": "utility",
        "effect": {"repair_rate": 5},
        "desc": "Slowly regenerates hull integrity after combat.",
    },

    # --- Special Systems ---
    "Scanner Array": {
        "type": "special",
        "effect": {"scan_bonus": 15},
        "desc": "Increases scan success rate when surveying belts or ships.",
    },
    "Warp Stabilizer": {
        "type": "special",
        "effect": {"fuel_efficiency": 10},
        "desc": "Reduces fuel consumption by 10%.",
    },
    "Pirate Transponder": {
        "type": "special",
        "effect": {"pirate_reputation": 20},
        "desc": "Masks your identity from pirates; reduces ambush chance.",
    },
}


# ---------------------------------------------------------------------------
# MODULE MANAGEMENT
# ---------------------------------------------------------------------------

def get_module(name: str) -> dict:
    """Return module data by name."""
    return MODULES.get(name, {})


def list_modules(module_type: str = None):
    """List all modules or filter by type."""
    print_divider("=")
    type_out("=== Available Modules ===")
    for name, mod in MODULES.items():
        if module_type and mod["type"] != module_type:
            continue
        dmg_info = ""
        if mod["type"] == "weapon":
            dmg_info = f" Damage: {mod['damage'][0]}–{mod['damage'][1]}"
        elif mod["type"] == "mining":
            dmg_info = f" Efficiency: {mod['efficiency']:.1f}"
        type_out(f"- {name} ({mod['type'].title()}){dmg_info}")
        type_out(f"  {mod['desc']}")
    print_divider("=")


def install_module(player: dict, module_name: str):
    """Install a module on the player’s ship if there’s capacity."""
    ship = player.get("ship_data", {})
    module_slots = ship.get("modules", 4)
    installed = player.get("ship_modules", [])
    if len(installed) >= module_slots:
        type_out("⚠️ No available module slots.")
        return False
    if module_name not in MODULES:
        type_out("❌ Invalid module.")
        return False
    installed.append(module_name)
    player["ship_modules"] = installed
    type_out(f"✅ Installed {module_name}.")
    return True


def remove_module(player: dict, module_name: str):
    """Remove a module from the player’s ship."""
    installed = player.get("ship_modules", [])
    if module_name not in installed:
        type_out(f"{module_name} is not installed.")
        return False
    installed.remove(module_name)
    type_out(f"❎ Removed {module_name}.")
    player["ship_modules"] = installed
    return True


def show_installed_modules(player: dict):
    """Display player’s current installed modules."""
    modules = player.get("ship_modules", [])
    print_divider("=")
    type_out("� Installed Modules:")
    if not modules:
        type_out("No modules installed.")
        return
    for mod in modules:
        info = MODULES.get(mod, {})
        desc = info.get("desc", "")
        type_out(f"- {mod}: {desc}")
    print_divider("=")
