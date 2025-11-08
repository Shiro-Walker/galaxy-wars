# core/mining.py
"""
Mining & Refining System for Galaxy: Fractured Dawn

Features:
- Scanning systems for asteroid belts (shows ore class F->S)
- Mining mini-game with difficulty and yield scaling
- Pirate ambush chance while mining (engages core.combat)
- Equipment wear / drill damage chance
- Refining ores into refined materials (mini-game with success roll)
- Music transitions for mining sessions

Notes:
- Uses audio helpers from core.utils (play_music, fade_music_out, play_sound_effect)
- Uses core.world for belt listing, core.data for ore definitions
- Uses core.player to add/remove cargo and save player state
"""

import random
import time
from typing import List, Dict, Tuple

from core.utils import (
    type_out,
    pause,
    print_divider,
    play_music,
    fade_music_out,
    play_sound_effect,
    roll_dice,
    weighted_choice,
)
from core.world import list_belts
from core.data import ORES, REFINED
from core.player import add_cargo, remove_cargo, save_player
from core.combat import engage_pirates

# -------------------------
# Local helpers
# -------------------------

def chance(percent: int) -> bool:
    """Return True percent% of the time (1-100)."""
    return random.randint(1, 100) <= max(0, min(percent, 100))


RARITY_ORDER = ["F", "E", "D", "C", "B", "A", "S"]
# map rarity letter to difficulty multiplier (higher = harder)
RARITY_DIFFICULTY = {r: i for i, r in enumerate(RARITY_ORDER)}  # F=0 .. S=6


# -------------------------
# Scanning
# -------------------------

def scan_system_for_belts(player: Dict) -> List[Tuple[int, str, str]]:
    """
    Scan the current system and return a list of belts with a sampled ore type and rarity.
    Returns list of tuples: (index, belt_name, ore_name)
    """
    system = player.get("location")
    belts = list_belts(system)
    print_divider("=")
    type_out(f"� Scanning {system} for asteroid belts...")
    time.sleep(0.8)

    if not belts:
        type_out("No asteroid belts detected in this system.")
        return []

    detected = []
    for idx, b in enumerate(belts, start=1):
        # pick ore biased by rarity weights (common ores more likely)
        ore = weighted_choice({
            "Veldspar": 30,
            "Scordite": 25,
            "Pyroxeres": 18,
            "Omber": 12,
            "Kernite": 8,
            "Plagioclase": 5,
            "Hedbergite": 2,
        })
        rarity = ORES.get(ore, {}).get("rarity", "F")
        type_out(f"[{idx}] {b} — {ore} Belt ({rarity}-class)")
        detected.append((idx, b, ore))
    print_divider("=")
    return detected


# -------------------------
# Mining Mini-Game
# -------------------------

def mine_belt(player: Dict, belt_name: str, chosen_ore: str = None):
    """
    Perform mining in the specified belt.
    - chosen_ore (optional): if provided, attempt to mine that ore (if belt indicated it).
    - Yields ore amount based on a dice roll modified by ore rarity and player's mining modules.
    - May trigger pirate ambush or equipment wear.
    """
    # start mining music
    fade_music_out(800)
    play_music("Asteroid Collision", loop=True, volume=0.55)
    play_sound_effect("drill_start", volume=0.6)

    # determine which ore to sample for this belt
    ore_name = chosen_ore or random.choice(list(ORES.keys()))
    ore_info = ORES.get(ore_name, {"base_value": 10, "rarity": "F"})
    rarity = ore_info.get("rarity", "F")
    difficulty = RARITY_DIFFICULTY.get(rarity, 0)

    type_out(f"⛏️ Beginning extraction on {belt_name} — targeting {ore_name} ({rarity}-Class).")
    pause("Press Enter to begin extraction sequence...")

    # Mini-game: three-step extraction: Scan -> Stabilize -> Extract
    # Each step uses a d20 roll against a DC based on rarity (higher rarity -> higher DC)
    steps = [
        ("scan", 10 + difficulty * 2, "Scanning for concentrated seams..."),
        ("stabilize", 11 + difficulty * 2, "Stabilizing extractor and aligning laser arrays..."),
        ("extract", 9 + difficulty * 2, "Engaging extraction — break the ore seams!")
    ]
    successes = 0
    for step_id, dc, msg in steps:
        type_out(msg)
        time.sleep(0.6)
        roll = roll_dice(20)
        type_out(f"� Roll: {roll} vs DC {dc}")
        time.sleep(0.4)
        if roll >= dc:
            successes += 1
            type_out("→ Success.")
        else:
            type_out("→ Partial / Failed.")
        time.sleep(0.3)

        # small chance for pirate attraction on failed stabilize/extract
        if step_id in ("stabilize", "extract") and not (roll >= dc) and chance(8 + difficulty * 3):
            type_out("� Your extraction emitted a high-power signature!")
            fade_music_out(400)
            play_sound_effect("alert", volume=0.7)
            engage_pirates(player)
            # if player destroyed, abort
            if player.get("hull", 0) <= 0:
                fade_music_out(800)
                return

    # determine yield based on successes and ore rarity
    base_yield = random.randint(6, 18)
    yield_multiplier = 1.0 + (successes * 0.35)  # each success increases yield
    rarity_bonus = max(0.5, 1.0 + (RARITY_DIFFICULTY.get(rarity, 0) * -0.08))  # rarer ores slightly lower yield per roll
    total_yield = max(1, int(base_yield * yield_multiplier * rarity_bonus))

    # equipment wear chance
    if chance(6 + difficulty * 4):
        type_out("⚙️ Your mining drill suffered wear during extraction — yield reduced.")
        total_yield = max(1, int(total_yield * 0.6))
        play_sound_effect("drill_fail", volume=0.6)

    # Add cargo and report
    added = add_cargo(player, ore_name, total_yield)
    if added:
        type_out(f"� Extracted {total_yield} × {ore_name} ({rarity}-Class) and placed into cargo hold.")
    else:
        type_out(f"⚠️ Not enough cargo space for the ore. You jettison {total_yield} units.")
        # optional: lose the ore (no reward)

    # small chance to find bonus salvage
    if chance(12):
        bonus = random.randint(10, 60)
        player["credits"] = player.get("credits", 0) + bonus
        type_out(f"� You salvage small components during mining: +{bonus} credits.")

    save_player(player)

    # end mining music
    fade_music_out(1000)
    play_music("Main Sector", loop=True, volume=0.45)
    play_sound_effect("drill_stop", volume=0.4)


# -------------------------
# Batch Mining Interface
# -------------------------

def mining_menu(player: Dict):
    """
    Interactive mining menu:
    - Scan system for belts
    - Select a belt to mine
    - Start extraction
    """
    while True:
        clear_or_banner()
        type_out(f"⛏️ Mining Console — Current System: {player.get('location')}")
        belts = scan_system_for_belts(player)
        if not belts:
            pause("No belts found. Press Enter to return.")
            return

        type_out("Select a belt to mine or [0] to exit:")
        for idx, belt, ore in belts:
            print(f"[{idx}] {belt} — {ore}")
        print("[0] Exit Mining Console")

        choice = input("> ").strip()
        if not choice.isdigit():
            continue
        idx = int(choice)
        if idx == 0:
            return
        selected = next((b for b in belts if b[0] == idx), None)
        if not selected:
            type_out("Invalid selection.")
            continue
        _, belt_name, ore_name = selected
        mine_belt(player, belt_name, chosen_ore=ore_name)


def clear_or_banner():
    """Small helper to clear screen or print banner (keeps UI tidy)."""
    try:
        from core.utils import clear
        clear()
    except Exception:
        print_divider("=")
        type_out("⛏️ Mining Console")


# -------------------------
# Refining Mini-Game
# -------------------------

def refine_ores(player: Dict):
    """
    Convert raw ores in cargo into refined materials.
    Uses a success roll per ore batch — failures can reduce yield.
    """
    cargo = player.get("cargo", {})
    ores_in_cargo = {k: v for k, v in cargo.items() if k in ORES}
    if not ores_in_cargo:
        type_out("You have no raw ores to refine.")
        pause()
        return

    fade_music_out(600)
    play_music("Futuristic Home", loop=True, volume=0.45)
    play_sound_effect("refinery_start", volume=0.6)

    type_out("� Refinery — Processing raw ores into refined components.")
    for ore, qty in ores_in_cargo.items():
        if qty <= 0:
            continue
        ore_info = ORES.get(ore, {})
        base_val = ore_info.get("base_value", 10)
        # determine output refined material by weighted mapping (simplified)
        refined_candidate = weighted_choice({
            "Tritanium": 40,
            "Pyerite": 30,
            "Mexallon": 15,
            "Isogen": 10,
            "Nocxium": 5,
        })
        type_out(f"Processing {qty}× {ore} into {refined_candidate}...")
        time.sleep(0.6)
        # success roll
        roll = roll_dice(20)
        if roll <= 6:
            # failure — lose some ore
            lost = max(1, qty // 2)
            remove_cargo(player, ore, lost)
            type_out(f"❌ Refining failed (roll {roll}). Lost {lost} units of {ore}.")
        else:
            efficiency = 0.5 + (roll / 40)  # between ~0.525 and 1.0
            refined_qty = max(1, int(qty * efficiency))
            add_cargo(player, refined_candidate, refined_qty)
            remove_cargo(player, ore, qty)
            type_out(f"✅ Refined into {refined_qty}× {refined_candidate} (roll {roll}).")

    play_sound_effect("refinery_end", volume=0.6)
    fade_music_out(800)
    play_music("Main Sector", loop=True, volume=0.45)
    save_player(player)
    pause("Refining complete. Press Enter to continue...")


# -------------------------
# Quick utility: direct mine (used by missions or events)
# -------------------------

def quick_mine_yield(player: Dict, ore_name: str, difficulty_modifier: int = 0) -> int:
    """
    Non-interactive mining used by missions:
    Returns amount of ore added to cargo (or 0 on fail).
    """
    ore_info = ORES.get(ore_name, {"base_value": 10, "rarity": "F"})
    rarity = ore_info.get("rarity", "F")
    difficulty = RARITY_DIFFICULTY.get(rarity, 0) + difficulty_modifier

    roll = roll_dice(20)
    base = random.randint(4, 12)
    success = roll >= max(6, 10 + difficulty)
    if not success:
        return 0
    amt = int(base * (1.0 + (20 - difficulty) / 20.0))
    added = add_cargo(player, ore_name, amt)
    if added:
        save_player(player)
        return amt
    return 0
