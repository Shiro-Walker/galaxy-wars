# core/travel_system.py
"""
Travel System for Galaxy: Fractured Dawn

Handles:
- Navigation between systems
- Fuel cost and management
- Random encounters (pirates, signals, asteroid belts)
- System arrival messages
- Music transitions
"""

import random
import time
from core.utils import (
    type_out,
    pause,
    print_divider,
    play_music,
    fade_music_out,
    roll_dice,
    chance,
)
from core.player import save_player
from core.combat import engage_pirates
from core.mining import mining_menu
from core.world import get_connections


# ---------------------------------------------------------------------------
# TRAVEL MAIN FUNCTION
# ---------------------------------------------------------------------------

def travel_to_system(player: dict, destination: str):
    """Perform travel from current system to destination system."""
    current = player.get("location", "Unknown")
    ship = player.get("ship", {"fuel": 100, "max_fuel": 100})

    print_divider("=")
    type_out(f"Plotting course from {current} → {destination}...")
    time.sleep(0.8)

    # Calculate fuel cost
    distance_cost = random.randint(8, 16)
    if ship["fuel"] < distance_cost:
        type_out(f"⚠️ Not enough fuel for the jump (need {distance_cost}, have {ship['fuel']}).")
        type_out("Consider refueling at a nearby station.")
        pause()
        return False

    # Confirm travel
    confirm = input(f"Proceed with travel? (Fuel cost: {distance_cost}) [y/n]: ").lower()
    if confirm != "y":
        type_out("Jump aborted.")
        return False

    # Start travel
    fade_music_out(1000)
    play_music("Spacey Oddity", loop=True, volume=0.55)
    type_out("Preparing jump drive...")
    time.sleep(1.5)
    type_out("Engaging hyperlight engines...")
    for _ in range(3):
        type_out("⏳ Jumping...", delay=0.05)
        time.sleep(0.6)
    print_divider("-")

    # Consume fuel
    ship["fuel"] -= distance_cost
    player["ship"] = ship
    player["location"] = destination

    # Random encounter roll
    if chance(20):
        random_encounter(player)
    else:
        arrival_sequence(destination)

    # Save player after travel
    save_player(player)

    fade_music_out(1000)
    play_music("Main Sector", loop=True, volume=0.55)
    return True


# ---------------------------------------------------------------------------
# ENCOUNTERS
# ---------------------------------------------------------------------------

def random_encounter(player: dict):
    """Trigger random space encounters during travel."""
    print_divider("=")
    type_out("� Scanning subspace... anomaly detected!")

    events = [
        ("pirates", 40),
        ("derelict_signal", 30),
        ("asteroid_field", 20),
        ("calm_space", 10),
    ]
    event = weighted_random(events)

    if event == "pirates":
        type_out("⚠️ Pirate vessels detected on long-range sensors!")
        from core.combat import engage_pirates
        engage_pirates(player)

    elif event == "derelict_signal":
        type_out("� You detect a faint distress beacon drifting in the void...")
        roll = roll_dice(20)
        if roll >= 12:
            reward = random.randint(100, 400)
            player["credits"] = player.get("credits", 0) + reward
            type_out(f"You find valuable salvage aboard the derelict. (+{reward} credits)")
        else:
            type_out("You find only wreckage and radiation traces — nothing salvageable.")

    elif event == "asteroid_field":
        type_out("� You enter an asteroid-rich region.")
        if chance(60):
            mining_menu(player)
        else:
            type_out("You navigate safely through the debris field.")

    else:
        type_out("✨ The journey is quiet — you drift peacefully among the stars.")
    pause()


# ---------------------------------------------------------------------------
# ARRIVAL SEQUENCE
# ---------------------------------------------------------------------------

def arrival_sequence(destination: str):
    """Simple arrival cinematic."""
    print_divider("=")
    fade_music_out(800)
    play_music("Main Sector", loop=True, volume=0.5)
    type_out(f"� Exiting hyperspace — now arriving at {destination}.")
    time.sleep(1.2)
    arrival_messages = [
        "The glow of nearby suns illuminates your hull plating.",
        "You pick up faint chatter from civilian transports.",
        "Your sensors recalibrate as the jump tunnel collapses.",
        "A passing freighter blinks its nav lights in greeting."
    ]
    type_out(random.choice(arrival_messages))
    print_divider("=")
    pause()


# ---------------------------------------------------------------------------
# FUEL MANAGEMENT
# ---------------------------------------------------------------------------

def refuel_ship(player: dict):
    """Refuel the player's ship at a station."""
    ship = player.get("ship", {"fuel": 100, "max_fuel": 100})
    cost_per_unit = 2
    needed = ship["max_fuel"] - ship["fuel"]

    if needed <= 0:
        type_out("Fuel tanks are already full.")
        pause()
        return

    total_cost = needed * cost_per_unit
    type_out(f"Refuel {needed} units for {total_cost} credits? (y/n)")
    choice = input("> ").lower()
    if choice == "y":
        if player["credits"] >= total_cost:
            player["credits"] -= total_cost
            ship["fuel"] = ship["max_fuel"]
            type_out("⛽ Refueling complete.")
        else:
            type_out("Not enough credits.")
    else:
        type_out("Refuel cancelled.")
    player["ship"] = ship
    save_player(player)
    pause()


# ---------------------------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------------------------

def weighted_random(choices: list):
    """choices = [(item, weight)] → returns random item"""
    total = sum(weight for _, weight in choices)
    r = random.uniform(0, total)
    upto = 0
    for item, weight in choices:
        if upto + weight >= r:
            return item
        upto += weight
    return choices[-1][0]


# ---------------------------------------------------------------------------
# SYSTEM INFO VIEWER
# ---------------------------------------------------------------------------

def show_system_info(player: dict):
    """Display current system details and connected routes."""
    current = player.get("location", "Unknown")
    print_divider("=")
    type_out(f"� System Information — {current}")
    # If your world.py defines data like population or faction, show it
    try:
        from core.world import get_system_info, get_connections
        info = get_system_info(current)
        faction = info.get("faction", "Neutral")
        pop = info.get("population", "Unknown")
        belts = ", ".join(info.get("belts", [])) if info.get("belts") else "None"
        type_out(f"Faction: {faction}")
        type_out(f"Population: {pop}")
        type_out(f"Asteroid Belts: {belts}")
        type_out("Connected Systems:")
        for dest in get_connections(current):
            print(f"  • {dest}")
    except Exception:
        type_out("No detailed data available for this system.")
    print_divider("=")
    pause()
