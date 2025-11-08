# core/combat.py
"""
Turn-Based Combat System for Galaxy: Fractured Dawn

Features:
- D&D-style d20 checks for attacks (using roll_dice)
- Kinetic / Energy / Blast weapon types
- Ammo and Power Grid management
- Emergency Power (risky overcharge)
- Scan enemy action (consumes a turn, can fail)
- Detailed combat log printed at end of each turn with rolls
- Music and sound hooks: plays battle music on engage, restores afterwards
"""

import random
import time
from typing import List, Dict, Tuple

from core.utils import (
    type_out,
    print_divider,
    roll_dice,
    chance,
    pause,
    play_music,
    fade_music_out,
    play_sound_effect,
)
from core.modules import get_module
from core.player import get_player_ship, save_player

# ---------------------------------------------------------------------------
# Example enemy templates (expandable)
# ---------------------------------------------------------------------------

PIRATE_TEMPLATE = {
    "id": "pirate_sholen",
    "name": "Sholen Raider",
    "class": "Frigate",
    "hull": 100,
    "armor": 98,
    "shields": 60,
    # weakness multipliers: >1 = weak, <1 = resistant, 1 = neutral
    "weakness": {"kinetic": 1.1, "energy": 0.9, "blast": 1.2},
    "damage_range": (8, 18),
    "accuracy": 12,  # target DC (lower harder to hit)
}

# ---------------------------------------------------------------------------
# Combat entrypoint
# ---------------------------------------------------------------------------

def engage_pirates(player: Dict, enemy_template: Dict = None):
    """
    Main combat loop invoked for pirate encounters and combat missions.
    Plays combat music, runs turn-based actions until one side is destroyed or player escapes.
    """
    enemy_template = enemy_template or PIRATE_TEMPLATE
    enemy = enemy_template.copy()
    # make mutable copies of armor/hull/shields
    enemy["hull"] = int(enemy.get("hull", 100))
    enemy["armor"] = int(enemy.get("armor", 100))
    enemy["shields"] = int(enemy.get("shields", 50))

    ship_stats = get_player_ship(player)
    player["hull"] = int(player.get("hull", ship_stats.get("hull", 100)))
    player["armor"] = int(player.get("armor", ship_stats.get("armor", 100)))
    player["shields"] = int(player.get("shields", ship_stats.get("shields", 100)))
    player_power = ship_stats.get("power_grid", 100)
    player_ammo = int(player.get("ammo", 0))

    battle_log: List[str] = []
    play_music("Hive Invasion", loop=True, volume=0.75)
    play_sound_effect("combat_start", volume=0.6)

    type_out(f"⚠️ Combat initiated: {enemy['name']} ({enemy['class']})")
    pause("Press Enter to engage...")

    # Combat loop
    turn = 1
    while enemy["hull"] > 0 and player["hull"] > 0:
        print_divider("=")
        type_out(f"--- Turn {turn} ---")
        type_out(f"Player: Hull {player['hull']} | Armor {player['armor']} | Shields {player['shields']} | Power {player_power} | Ammo {player_ammo}")
        type_out(f"{enemy['name']}: Hull {enemy['hull']} | Armor {enemy['armor']} | Shields {enemy['shields']}")
        print_divider("-")

        # Player action
        action = combat_menu()
        p_log, player_power, player_ammo = handle_player_action(
            player, ship_stats, enemy, player_power, player_ammo, action
        )
        battle_log.extend(p_log)

        # Enemy turn (if still alive)
        if enemy["hull"] > 0:
            e_log = enemy_attack(player, enemy)
            battle_log.extend(e_log)

        # End of turn power regen and small ammo restore after traveling or turn end
        player_power = min(player_power + max(3, ship_stats.get("speed", 5) // 2), ship_stats.get("power_grid", 100))
        # slight passive ammo regen (fictional small resupply)
        if chance(5):
            player_ammo += 1
            battle_log.append("Passive systems scavenged +1 ammo this turn.")

        # Print turn's combat log (include rolls and details)
        print_combat_log(battle_log, player, enemy)
        battle_log = []  # clear for next turn

        # short delay to make reading easier
        pause()
        turn += 1

    # Combat resolution
    fade_music_out(800)
    play_sound_effect("combat_end", volume=0.6)
    if player["hull"] <= 0:
        type_out("� Your ship has been destroyed in combat!")
        # handle ship loss externally through player manager
        # We keep player state here but return so caller can handle collision consequences.
        save_player(player)
        return False
    else:
        type_out(f"� Enemy {enemy['name']} destroyed!")
        # salvage / reward
        reward = random.randint(150, 400)
        player["credits"] = player.get("credits", 0) + reward
        type_out(f"Recovered salvage worth {reward} credits.")
        save_player(player)
        return True


# ---------------------------------------------------------------------------
# Combat UI / Action handlers
# ---------------------------------------------------------------------------

def combat_menu() -> str:
    """Return player's combat choice."""
    print("[1] Attack")
    print("[2] Emergency Power")
    print("[3] Scan Enemy")
    print("[4] Retreat")
    return input("> ").strip()


def handle_player_action(player: dict, ship_stats: dict, enemy: dict, power_grid: int, ammo: int, action: str) -> Tuple[List[str], int, int]:
    """
    Execute the player's chosen action and return:
    - list of log strings for this action
    - updated power_grid
    - updated ammo
    """
    log: List[str] = []
    modules = player.get("ship_modules", [])

    if action == "1":  # Attack
        logs, power_grid, ammo = perform_attack(player, ship_stats, enemy, modules, power_grid, ammo)
        log.extend(logs)

    elif action == "2":  # Emergency Power
        res_text, power_grid = emergency_power(power_grid)
        log.append(res_text)

    elif action == "3":  # Scan
        scan_log = scan_enemy(enemy)
        log.extend(scan_log)

    elif action == "4":  # Retreat attempt
        log.append("Attempting to retreat...")
        if chance(50):
            log.append("Retreat successful!")
            # Retreat ends combat by setting enemy hull to 0? We'll return early
            enemy["hull"] = enemy["hull"]  # no change, caller handles
            # We return logs and set a flag via special entry
            log.append("[RETREATED]")
        else:
            log.append("Retreat failed! Enemy prevents escape.")
    else:
        log.append("No valid action chosen — turn skipped.")

    return log, power_grid, ammo


# ---------------------------------------------------------------------------
# Attack / Weapon Resolution
# ---------------------------------------------------------------------------

def perform_attack(player: dict, ship_stats: dict, enemy: dict, modules: List[str], power_grid: int, ammo: int) -> Tuple[List[str], int, int]:
    """
    Iterate through installed weapon modules and attempt to fire them.
    Energy weapons consume power_grid, kinetic weapons consume ammo.
    Returns logs and updated power_grid/ammo.
    """
    logs: List[str] = []
    logs.append("=====[Combat Log]=====")
    total_rolls = []

    # Track aggregated damage by type for logging
    dmg_summary = {"kinetic": 0, "energy": 0, "blast": 0}
    used_modules = 0

    for mod_name in modules:
        mod = get_module(mod_name)
        if not mod or mod.get("type") != "weapon":
            continue
        used_modules += 1
        # attack roll (d20)
        attack_roll = roll_dice(20)
        total_rolls.append((mod_name, attack_roll))
        base_min, base_max = mod.get("damage", (5, 10))
        damage = random.randint(base_min, base_max)

        # critical/miss
        if attack_roll == 20:
            damage = int(damage * 1.8)
            logs.append(f"� Crit! {mod_name} scored a critical (roll {attack_roll}).")
        elif attack_roll <= 2:
            logs.append(f"❌ {mod_name} misfired (roll {attack_roll}).")
            continue  # missed, no resource consumption

        # resource checks
        dtype = mod.get("damage_type", "kinetic")
        if mod.get("ammo_use", 0) > 0:
            need = mod.get("ammo_use", 0)
            if ammo < need:
                logs.append(f"⚠️ {mod_name} has insufficient ammo — cannot fire.")
                continue
            ammo -= need
        elif mod.get("power_use", 0) > 0:
            need = mod.get("power_use", 0)
            if power_grid < need:
                logs.append(f"⚠️ {mod_name} failed to fire (insufficient power).")
                continue
            power_grid -= need

        # apply enemy weakness/resistance
        multiplier = enemy.get("weakness", {}).get(dtype, 1.0)
        applied = int(damage * multiplier)
        # first apply to shields
        if enemy.get("shields", 0) > 0:
            to_shield = min(enemy["shields"], applied)
            enemy["shields"] -= to_shield
            applied -= to_shield
            logs.append(f"{mod_name} deals {to_shield} pts damage to Shields. (roll {attack_roll})")
        if applied > 0:
            enemy["hull"] -= applied
            logs.append(f"{mod_name} deals {applied} pts to Hull ({dtype}). (roll {attack_roll})")

        dmg_summary[dtype] += damage

    if used_modules == 0:
        logs.append("No weapons installed or available to fire.")

    # show enemy status brief
    logs.append(f"{enemy['name']}: Hull {max(0, enemy['hull'])} | Armor {enemy.get('armor',0)} | Shield {max(0, enemy.get('shields',0))}")
    # include a compact roll summary
    logs.append("Rolls:")
    for mn, r in total_rolls:
        logs.append(f" - {mn}: d20={r}")

    return logs, power_grid, ammo


# ---------------------------------------------------------------------------
# Emergency Power
# ---------------------------------------------------------------------------

def emergency_power(power_grid: int) -> Tuple[str, int]:
    """
    Attempt to divert extra energy to weapons/shields.
    Success -> temporary burst added to power grid.
    Failure -> overload, lose power and potentially damage systems.
    """
    roll = roll_dice(20)
    if roll >= 14:
        boost = random.randint(12, 30)
        new_grid = min(140, power_grid + boost)
        return f"⚡ Emergency Power engaged! Success (roll {roll}). +{boost} Power Grid.", new_grid
    else:
        penalty = random.randint(8, 25)
        new_grid = max(0, power_grid - penalty)
        # small chance to disable one random weapon (flavor)
        if chance(20):
            return f"� Overload! (roll {roll}) Systems damaged — -{penalty} Power Grid. Weapons may malfunction.", new_grid
        return f"� Overload! (roll {roll}) -{penalty} Power Grid.", new_grid


# ---------------------------------------------------------------------------
# Scan Enemy
# ---------------------------------------------------------------------------

def scan_enemy(enemy: dict) -> List[str]:
    """
    Spend a turn to scan enemy shields/armor for weaknesses.
    Scan may fail on low roll.
    """
    logs: List[str] = []
    roll = roll_dice(20)
    if roll <= 5:
        logs.append(f"Scan failed (roll {roll}). Enemy sensors scrambled.")
    else:
        logs.append(f"=====[Scan Results]===== (roll {roll})")
        for dtype, mult in enemy.get("weakness", {}).items():
            tag = "(w)" if mult > 1.0 else "(r)" if mult < 1.0 else ""
            logs.append(f" - {dtype.title():<7}: multiplier {mult} {tag}")
    return logs


# ---------------------------------------------------------------------------
# Enemy Action
# ---------------------------------------------------------------------------

def enemy_attack(player: dict, enemy: dict) -> List[str]:
    """
    Enemy makes an attack roll; applies damage to player's shields/hull.
    """
    logs: List[str] = []
    roll = roll_dice(20)
    if roll <= 3:
        logs.append(f"{enemy['name']} missed their attack! (roll {roll})")
        return logs

    damage = random.randint(*enemy.get("damage_range", (6, 14)))
    if roll == 20:
        damage = int(damage * 1.8)
        logs.append(f"� Critical hit from {enemy['name']}! (roll {roll})")

    # apply to player shields first
    if player.get("shields", 0) > 0:
        absorbed = min(player["shields"], damage)
        player["shields"] -= absorbed
        damage -= absorbed
        logs.append(f"{enemy['name']} dealt {absorbed} damage to your Shields.")
    if damage > 0:
        player["hull"] = max(0, player["hull"] - damage)
        logs.append(f"{enemy['name']} dealt {damage} damage to your Hull.")
    return logs


# ---------------------------------------------------------------------------
# Combat Log Display
# ---------------------------------------------------------------------------

def print_combat_log(logs: List[str], player: dict, enemy: dict):
    """ Nicely format and print logs; show short status blocks for both ships. """
    print_divider("=")
    for entry in logs:
        type_out(entry, delay=0.004)
    print_divider("-")
    # display compact status with weakness tags similar to example
    def format_status(title: str, data: dict, weak_map: Dict[str, float]) -> List[str]:
        lines = []
        hull = data.get("hull", 0)
        armor = data.get("armor", 0)
        shields = data.get("shields", 0)
        # build weakness string
        wm = []
        for k, v in weak_map.items():
            if v > 1.0:
                wm.append(f"({k[0]})")
        lines.append(f"{title}:")
        lines.append(f" Hull : {hull} | Armor: {armor} | Shield: {shields}")
        lines.append(f" Weakness tags: " + ", ".join([f"{k}={('weak' if v>1 else 'res' if v<1 else 'neutral')}" for k, v in weak_map.items()]))
        return lines

    # enemy status
    enemy_lines = format_status(enemy["name"], enemy, enemy.get("weakness", {}))
    for l in enemy_lines:
        type_out(l, delay=0.002)

    # player status (use ship modules for player weakness display placeholder)
    player_weakness = {"kinetic": 1.0, "energy": 1.0, "blast": 1.0}
    player_lines = format_status(player.get("name", "Player"), player, player_weakness)
    for l in player_lines:
        type_out(l, delay=0.002)
    print_divider("=")
