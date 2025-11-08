# core/station.py
"""
Station Systems for Galaxy: Fractured Dawn

Handles:
- Station entry and sub-locations
- Bar interactions and random events
- Market, Hangar, and Mission Board menus
- Ambient music transitions per location
"""

import random
import time
from core.utils import (
    clear, type_out, pause, print_divider,
    play_music, fade_music_out, success, warning, error
)
from core.missions import mission_board_menu
from core.player import save_player


# ---------------------------------------------------------------------------
# MAIN STATION MENU
# ---------------------------------------------------------------------------

def station_menu(player: dict):
    """Main hub menu when docked at a station."""
    while True:
        clear()
        print_divider("=")
        type_out(f"� Docked at {player.get('docked_at', 'Unknown Station')}")
        print_divider("-")
        print("[1] Visit Bar")
        print("[2] Visit Hangar")
        print("[3] Visit Market")
        print("[4] Mission Board")
        print("[5] Depart Station")
        print_divider("-")

        choice = input("> ").strip()

        if choice == "1":
            visit_bar(player)
        elif choice == "2":
            visit_hangar(player)
        elif choice == "3":
            visit_market(player)
        elif choice == "4":
            visit_mission_board(player)
        elif choice == "5":
            fade_music_out(1000)
            type_out("Undocking and preparing for flight...")
            time.sleep(1.5)
            player["docked_at"] = None
            save_player(player)
            return
        else:
            warning("Invalid selection.")
            pause()


# ---------------------------------------------------------------------------
# BAR SYSTEM
# ---------------------------------------------------------------------------

def visit_bar(player: dict):
    """Randomized NPC interaction bar with ambient music."""
    fade_music_out(1000)
    play_music("Beneath the Noise", loop=True, volume=0.5)

    clear()
    print_divider("=")
    type_out("� Welcome to the Station Bar")
    print_divider("-")

    bar_events = [
        "You share a drink with a trader who gives you a small data cache. (+250 credits)",
        "You overhear smugglers talking about a hidden asteroid belt nearby.",
        "A drunk mercenary challenges you to a bet — and you win! (+500 credits)",
        "You accidentally spill your drink on a pirate. You lose 1000 credits replacing your gear.",
        "A mysterious agent offers you a small job on the next station. (+XP)",
        "You meet a miner who tells you about rare asteroids in the next system."
    ]
    event = random.choice(bar_events)

    type_out(event)
    if "credits" in event:
        if "lose" in event:
            player["credits"] = max(0, player.get("credits", 0) - 1000)
            warning("You lost 1000 credits!")
        elif "250" in event:
            player["credits"] = player.get("credits", 0) + 250
            success("You earned 250 credits!")
        elif "500" in event:
            player["credits"] = player.get("credits", 0) + 500
            success("You earned 500 credits!")

    if "+XP" in event:
        player["xp"] = player.get("xp", 0) + 100
        success("You gained 100 XP!")

    save_player(player)
    print_divider("-")
    pause("Press Enter to return to station...")

    fade_music_out(1000)
    play_music("Safe Zone", loop=True, volume=0.5)


# ---------------------------------------------------------------------------
# HANGAR SYSTEM
# ---------------------------------------------------------------------------

def visit_hangar(player: dict):
    """Repair, refuel, and manage ship upgrades."""
    fade_music_out(1000)
    play_music("Futuristic Home", loop=True, volume=0.5)

    while True:
        clear()
        print_divider("=")
        type_out("�️ HANGAR CONTROL")
        print_divider("-")
        print(f"Hull Integrity: {player.get('ship', {}).get('hull', 100)}%")
        print(f"Credits: {player.get('credits', 0)}")
        print("[1] Repair Ship (Cost: 250 credits)")
        print("[2] Refuel Ship (Cost: 100 credits)")
        print("[3] Purchase Insurance (Cost: 500 credits)")
        print("[4] Leave Hangar")
        print_divider("-")

        choice = input("> ").strip()
        ship = player.get("ship", {})

        if choice == "1":
            if player["credits"] >= 250:
                player["credits"] -= 250
                ship["hull"] = 100
                success("Ship fully repaired.")
            else:
                error("Not enough credits for repair.")
        elif choice == "2":
            if player["credits"] >= 100:
                player["credits"] -= 100
                ship["fuel"] = ship.get("max_fuel", 100)
                success("Ship refueled.")
            else:
                error("Not enough credits for fuel.")
        elif choice == "3":
            if player["credits"] >= 500:
                player["credits"] -= 500
                player["insurance"] = True
                success("Insurance purchased. Ship will be restored if lost.")
            else:
                error("Not enough credits for insurance.")
        elif choice == "4":
            break
        else:
            warning("Invalid selection.")
        save_player(player)
        pause()

    fade_music_out(1000)
    play_music("Safe Zone", loop=True, volume=0.5)


# ---------------------------------------------------------------------------
# MARKET SYSTEM
# ---------------------------------------------------------------------------

def visit_market(player: dict):
    """Market interface for buying and selling goods."""
    fade_music_out(1000)
    play_music("Safe Zone", loop=True, volume=0.55)

    clear()
    print_divider("=")
    type_out("� Galactic Trade Market")
    print_divider("-")
    type_out("Buy, sell, and trade valuable resources.")
    pause("Press Enter to simulate market transaction...")

    # Placeholder simulation
    gained = random.randint(100, 400)
    player["credits"] += gained
    success(f"Market trade successful. +{gained} credits.")
    save_player(player)
    pause("Press Enter to return...")

    fade_music_out(1000)
    play_music("Safe Zone", loop=True, volume=0.5)


# ---------------------------------------------------------------------------
# MISSION BOARD
# ---------------------------------------------------------------------------

def visit_mission_board(player: dict):
    """Access bounty, trade, and side missions."""
    fade_music_out(1000)
    play_music("Main Sector", loop=True, volume=0.6)

    clear()
    print_divider("=")
    type_out("� MISSION BOARD")
    print_divider("-")
    type_out("Refreshing available contracts...")
    time.sleep(1.5)
    mission_board_menu(player)
    save_player(player)
    pause("Press Enter to return...")

    fade_music_out(1000)
    play_music("Safe Zone", loop=True, volume=0.5)
