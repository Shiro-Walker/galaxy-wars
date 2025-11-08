# core/missions.py
"""
Side missions & bounty board system for Galaxy: Fractured Dawn

Features:
- Procedural mission pool (POOL_SIZE)
- Persistent mission board with BOARD_SLOTS (saved to saves/mission_board.json)
- Accept missions: cargo/passenger validation + tagging
- Combat missions launch an encounter immediately
- check_mission_completion() should be called after docking to auto-complete applicable missions
- Player missions stored under player['missions'] with structure:
    {
      "active": { mission_id: mission_dict, ... },
      "completed": [mission_id, ...]
    }
"""

import os
import json
import random
from typing import Dict, List, Tuple

from core.data import ORES
from core.utils import type_out, pause
from core.player import save_player, add_cargo, remove_cargo
from core.combat import engage_pirates, PIRATE

# persistent board path
SAVE_DIR = "saves"
BOARD_PATH = os.path.join(SAVE_DIR, "mission_board.json")

# pool/board sizes
POOL_SIZE = 120
BOARD_SLOTS = 5


# -------------------------
# Helpers: quick system pick
# -------------------------
def _random_system_name() -> str:
    # try to use the generated galaxy map names if available
    try:
        from core.world import load_galaxy_map
        systems = list(load_galaxy_map().keys())
        if systems:
            return random.choice(systems)
    except Exception:
        pass
    return f"System-{random.randint(1,40):02d}"


def _random_cargo_item() -> Tuple[str, int]:
    item = random.choice(list(ORES.keys()))
    qty = random.randint(5, 60)
    return item, qty


# -------------------------
# Mission factory functions
# -------------------------
def _make_transport_cargo(mid: int) -> Dict:
    origin = _random_system_name()
    dest = _random_system_name()
    while dest == origin:
        dest = _random_system_name()
    cargo_item, qty = _random_cargo_item()
    base = ORES.get(cargo_item, {}).get("base_value", 10)
    reward = int(qty * base * random.uniform(1.2, 2.2))
    return {
        "id": f"M{mid:04d}",
        "type": "transport",
        "subtype": "cargo",
        "title": f"Deliver {qty}× {cargo_item} to {dest}",
        "origin": origin,
        "destination": dest,
        "cargo": {cargo_item: qty},
        "reward": reward,
        "difficulty": random.choice(["Easy", "Normal", "Hard"]),
        "notes": f"Transport order for {cargo_item}."
    }


def _make_transport_passenger(mid: int) -> Dict:
    origin = _random_system_name()
    dest = _random_system_name()
    while dest == origin:
        dest = _random_system_name()
    pax = random.randint(1, 25)
    reward = int(pax * random.uniform(20, 80))
    return {
        "id": f"M{mid:04d}",
        "type": "transport",
        "subtype": "passenger",
        "title": f"Transport {pax} passengers to {dest}",
        "origin": origin,
        "destination": dest,
        "passengers": pax,
        "reward": reward,
        "difficulty": random.choice(["Easy", "Normal", "Hard"]),
        "notes": "Requires passenger capacity (Passenger Hold modules)."
    }


def _make_combat(mid: int) -> Dict:
    origin = _random_system_name()
    dest = _random_system_name()
    n = random.choice([1, 1, 2])
    reward = random.randint(300, 2000) * n
    return {
        "id": f"M{mid:04d}",
        "type": "combat",
        "title": f"Eliminate raider activity near {dest}",
        "origin": origin,
        "destination": dest,
        "enemies": n,
        "reward": reward,
        "difficulty": random.choice(["Normal", "Hard"]),
        "notes": "Combat contract — accepts will spawn an immediate engagement."
    }


def _make_mining(mid: int) -> Dict:
    origin = _random_system_name()
    ore = random.choice(list(ORES.keys()))
    qty = random.randint(10, 80)
    base = ORES.get(ore, {}).get("base_value", 10)
    reward = int(qty * base * random.uniform(1.0, 2.0))
    return {
        "id": f"M{mid:04d}",
        "type": "mining",
        "title": f"Mine {qty}× {ore} in {origin}",
        "origin": origin,
        "destination": origin,
        "ore": ore,
        "quantity": qty,
        "reward": reward,
        "difficulty": random.choice(["Easy", "Normal", "Hard"]),
        "notes": "Collect requested ore and return to specified station."
    }


def _make_salvage(mid: int) -> Dict:
    origin = _random_system_name()
    reward = random.randint(200, 1200)
    return {
        "id": f"M{mid:04d}",
        "type": "salvage",
        "title": f"Salvage derelict in {origin}",
        "origin": origin,
        "destination": origin,
        "reward": reward,
        "difficulty": random.choice(["Easy", "Normal"]),
        "notes": "Investigate a derelict and salvage useful parts."
    }


def generate_mission_pool(size: int = POOL_SIZE) -> List[Dict]:
    pool = []
    weights = ["transport_cargo"] * 40 + ["transport_passenger"] * 10 + ["combat"] * 25 + ["mining"] * 25 + ["salvage"] * 20
    for i in range(1, size + 1):
        kind = random.choice(weights)
        if kind == "transport_cargo":
            pool.append(_make_transport_cargo(i))
        elif kind == "transport_passenger":
            pool.append(_make_transport_passenger(i))
        elif kind == "combat":
            pool.append(_make_combat(i))
        elif kind == "mining":
            pool.append(_make_mining(i))
        else:
            pool.append(_make_salvage(i))
    return pool


# -------------------------
# Persistence: board save/load
# -------------------------
def refresh_mission_board(force: bool = False) -> List[Dict]:
    """
    Build a new mission board of BOARD_SLOTS offers sampled from the pool.
    Save to disk so the board persists until the next economy refresh.
    """
    os.makedirs(SAVE_DIR, exist_ok=True)
    if os.path.exists(BOARD_PATH) and not force:
        try:
            with open(BOARD_PATH, "r") as f:
                board = json.load(f)
            return board
        except Exception:
            pass

    pool = generate_mission_pool()
    board = random.sample(pool, k=min(BOARD_SLOTS, len(pool)))
    with open(BOARD_PATH, "w") as f:
        json.dump(board, f, indent=2)
    return board


def get_current_board() -> List[Dict]:
    if not os.path.exists(BOARD_PATH):
        return refresh_mission_board()
    with open(BOARD_PATH, "r") as f:
        try:
            return json.load(f)
        except Exception:
            return refresh_mission_board()


# -------------------------
# Player mission helpers
# -------------------------
def ensure_player_missions(player: Dict):
    if "missions" not in player:
        player["missions"] = {"active": {}, "completed": []}
    else:
        player["missions"].setdefault("active", {})
        player["missions"].setdefault("completed", [])


def accept_mission(player: Dict, mission_id: str) -> bool:
    """
    Accept a mission from the current board.
    For cargo transport: check cargo space, add cargo and tag mission.
    For passenger transport: check passenger capacity (modules) and tag.
    For combat: spawn combat immediately.
    For mining/salvage: add to active list for player to complete in-system.
    """
    ensure_player_missions(player)
    board = get_current_board()
    mission = next((m for m in board if m["id"] == mission_id), None)
    if not mission:
        type_out("Mission not found on the current board.")
        return False

    ship_modules = player.get("ship_modules", [])
    ship_capacity = 0
    # get cargo capacity from player's ship (via core.player helper get_player_ship)
    try:
        from core.player import get_player_ship
        ps = get_player_ship(player)
        ship_capacity = ps.get("cargo_capacity", 0)
    except Exception:
        ship_capacity = player.get("cargo_capacity", 0) or 100

    # accept logic per type
    mtype = mission.get("type")
    if mtype == "transport" and mission.get("subtype") == "cargo":
        total_qty = sum(mission.get("cargo", {}).values())
        current_load = sum(player.get("cargo", {}).values()) if player.get("cargo") else 0
        if current_load + total_qty > ship_capacity:
            type_out("Not enough cargo space to accept this mission.")
            return False
        # add cargo and tag
        for item, qty in mission.get("cargo", {}).items():
            add_cargo(player, item, qty)
        copy = dict(mission)
        copy["_mission_tag"] = {"cargo_added": dict(mission.get("cargo", {}))}
        player["missions"]["active"][mission_id] = copy
        save_player(player)
        type_out(f"Mission {mission_id} accepted: cargo loaded.")
        return True

    if mtype == "transport" and mission.get("subtype") == "passenger":
        # calculate passenger capacity from modules
        pax_capacity = 0
        from core.modules import MODULES as MODDEF
        for m in ship_modules:
            if MODDEF.get(m) and MODDEF[m].get("type") == "utility" and MODDEF[m].get("effect", {}).get("cargo_bonus") is None:
                # passenger modules may be named Passenger Hold in future; this is a placeholder
                pass
        # For now, accept passenger missions if ship has at least one Cargo Pod (simplified)
        if "Passenger Hold" not in ship_modules and "Small Cabin" not in ship_modules and "Medium Cabin" not in ship_modules:
            type_out("Your ship lacks passenger accommodations to accept this mission.")
            return False
        copy = dict(mission)
        copy["_mission_tag"] = {"passengers_onboard": mission.get("passengers", 0)}
        player["missions"]["active"][mission_id] = copy
        save_player(player)
        type_out(f"Mission {mission_id} accepted: passengers aboard.")
        return True

    if mtype == "combat":
        # spawn immediate combat based on 'enemies' count (use engage_pirates repeatedly)
        enemies = mission.get("enemies", 1)
        type_out(f"Accepting combat contract {mission_id} — engaging {enemies} raiders.")
        success = True
        for _ in range(enemies):
            engage_pirates(player)  # engage_pirates handles outcomes & loot
            # after each engagement, check if player still alive
            if player.get("hull", 0) <= 0:
                success = False
                break
        if success:
            # reward and mark complete
            player["missions"]["completed"].append(mission_id)
            save_player(player)
            type_out(f"Combat contract {mission_id} completed. Reward: {mission.get('reward',0)} credits added.")
            player["credits"] = player.get("credits", 0) + mission.get("reward", 0)
            save_player(player)
            return True
        else:
            type_out("Combat failed or you were destroyed. Mission not completed.")
            return False

    if mtype in ("mining", "salvage"):
        player["missions"]["active"][mission_id] = dict(mission)
        save_player(player)
        type_out(f"Mission {mission_id} accepted. See mission details in your mission log.")
        return True

    type_out("Unhandled mission type.")
    return False


# -------------------------
# Completion checks (call when docking)
# -------------------------
def check_mission_completion(player: Dict) -> List[str]:
    """
    When player docks (or on-demand), call this to check for mission completions.
    For cargo transport: removes mission-tagged cargo and grants reward when at destination.
    For passengers: disembark when at destination.
    For mining: if player has required ore in cargo while at origin/destination, remove and reward.
    For salvage: simple success roll when at origin to decide reward.
    """
    ensure_player_missions(player)
    active = dict(player["missions"].get("active", {}))  # copy to iterate
    completed = []
    current_system = player.get("location")
    docked_station = player.get("docked_at") or player.get("current_station")

    for mid, m in active.items():
        mtype = m.get("type")
        dest = m.get("destination")
        origin = m.get("origin")
        # Cargo transport
        if mtype == "transport" and m.get("subtype") == "cargo":
            if current_system == dest or (docked_station and dest in docked_station):
                tag = m.get("_mission_tag", {}).get("cargo_added", {})
                ok = True
                for item, qty in tag.items():
                    removed = remove_cargo(player, item, qty)
                    if not removed:
                        ok = False
                if ok:
                    player["credits"] = player.get("credits", 0) + m.get("reward", 0)
                    player["missions"]["completed"].append(mid)
                    del player["missions"]["active"][mid]
                    type_out(f"Mission {mid} complete! Reward: {m.get('reward',0)} credits.")
                    save_player(player)
                    completed.append(mid)
                else:
                    type_out(f"Mission {mid} incomplete — required cargo missing.")
        # Passenger transport
        elif mtype == "transport" and m.get("subtype") == "passenger":
            if current_system == dest or (docked_station and dest in docked_station):
                player["credits"] = player.get("credits", 0) + m.get("reward", 0)
                player["missions"]["completed"].append(mid)
                del player["missions"]["active"][mid]
                type_out(f"Passenger mission {mid} complete. Reward: {m.get('reward',0)} credits.")
                save_player(player)
                completed.append(mid)
        # Mining mission
        elif mtype == "mining":
            if current_system == origin or (docked_station and origin in docked_station):
                ore = m.get("ore")
                qty = m.get("quantity", 0)
                have = player.get("cargo", {}).get(ore, 0)
                if have >= qty:
                    remove_cargo(player, ore, qty)
                    player["credits"] = player.get("credits", 0) + m.get("reward", 0)
                    player["missions"]["completed"].append(mid)
                    del player["missions"]["active"][mid]
                    type_out(f"Mining mission {mid} completed. Reward: {m.get('reward',0)} credits.")
                    save_player(player)
                    completed.append(mid)
                else:
                    type_out(f"Mining mission {mid} incomplete: have {have}/{qty} {ore}.")
        # Salvage mission
        elif mtype == "salvage":
            if current_system == origin or (docked_station and origin in docked_station):
                roll = random.randint(1, 20)
                if roll > 8:
                    player["credits"] = player.get("credits", 0) + m.get("reward", 0)
                    player["missions"]["completed"].append(mid)
                    del player["missions"]["active"][mid]
                    type_out(f"Salvage mission {mid} succeeded. Reward: {m.get('reward',0)} credits.")
                    save_player(player)
                    completed.append(mid)
                else:
                    type_out(f"Salvage mission {mid} failed (Roll {roll}).")
    return completed


# -------------------------
# UI helpers
# -------------------------
def show_board():
    board = get_current_board()
    type_out("\n=== Mission Board ===")
    for m in board:
        type_out(f"[{m['id']}] {m['title']} - Reward: {m.get('reward',0)}")
        type_out(f"   {m.get('notes','')}")
    pause()


def show_player_missions(player: Dict):
    ensure_player_missions(player)
    type_out("\n=== Active Missions ===")
    if not player["missions"]["active"]:
        type_out("No active missions.")
    for mid, m in player["missions"]["active"].items():
        type_out(f"[{mid}] {m.get('title')} -> {m.get('destination')} Reward: {m.get('reward',0)}")
    type_out("\n=== Completed Missions ===")
    for mid in player["missions"]["completed"]:
        type_out(f"- {mid}")
    pause()
