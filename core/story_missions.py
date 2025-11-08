# core/story_missions.py
"""
Story Mission Manager for Galaxy: Fractured Dawn (Extended Dialogue Edition)

Adds:
- RPG-style dialogue sequences for story steps
- Multi-paragraph dialogue playback with typewriter pacing
- Story steps can now include "dialogues" array
"""

import json
import os
import random
from typing import Dict, List, Optional

from core.utils import type_out, pause, clear
from core.player import save_player
from core.combat import engage_pirates

DATA_DIR = "data"
STORY_PATH = os.path.join(DATA_DIR, "story_missions.json")


# ---------------------------------------------------------------------------
# STORY FILE HANDLING
# ---------------------------------------------------------------------------

def load_story_definitions() -> Dict[str, Dict]:
    """Load the story mission definitions (create defaults if missing)."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(STORY_PATH):
        return _generate_default_story_missions()
    try:
        with open(STORY_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return _generate_default_story_missions()


def _generate_default_story_missions() -> Dict[str, Dict]:
    """
    Create a small chain of placeholder story missions.
    You’ll later expand this file to 120+ missions externally.
    """
    missions = {}

    missions["S001"] = {
        "id": "S001",
        "title": "Prologue — Escape from Terra",
        "description": "The Federation has declared martial law across Terra Prime.",
        "steps": [
            {
                "id": "s1-dialogue",
                "type": "dialogue",
                "dialogues": [
                    {
                        "speaker": "Commander Rhea",
                        "text": (
                            "Captain, listen closely. The Federation has gone rogue. "
                            "They’ve blockaded every jump gate out of Terra Prime. "
                            "We need you to reach Nova Sector — it’s our only safe route out."
                        )
                    },
                    {
                        "speaker": "You",
                        "text": (
                            "Understood, Commander. What about the crew of the *Dauntless*?"
                        )
                    },
                    {
                        "speaker": "Commander Rhea",
                        "text": (
                            "Already evacuated. You’re the last ship still running. "
                            "Now go — before the Federation detects your drive signature!"
                        )
                    }
                ],
            },
            {"id": "s1-travel", "type": "travel", "target": "System-02"},
            {"id": "s1-dock", "type": "dock", "target": "System-02 Station 1"},
        ],
        "reward": 500,
        "next": "S002",
    }

    missions["S002"] = {
        "id": "S002",
        "title": "Signal in the Dark",
        "description": (
            "Weeks after your escape, you intercept a faint transmission "
            "originating from Beta Reach. The signal carries a voice you thought lost..."
        ),
        "steps": [
            {
                "id": "s2-dialogue",
                "type": "dialogue",
                "dialogues": [
                    {
                        "speaker": "You",
                        "text": (
                            "That can’t be right... This signature—it matches Commander Rhea’s old ID."
                        )
                    },
                    {
                        "speaker": "Navigator Kira",
                        "text": (
                            "It’s faint, but it’s there. Could she have survived the blockade?"
                        )
                    },
                    {
                        "speaker": "You",
                        "text": (
                            "Plot a course for Beta Reach. We’re going to find out who’s really sending this signal."
                        )
                    }
                ],
            },
            {"id": "s2-travel", "type": "travel", "target": "System-05"},
            {"id": "s2-combat", "type": "combat", "enemies": 1},
            {"id": "s2-dock", "type": "dock", "target": "System-05 Station 1"},
        ],
        "reward": 900,
        "next": None,
    }

    with open(STORY_PATH, "w") as f:
        json.dump(missions, f, indent=2)
    type_out("Created default story mission definitions.")
    return missions


# ---------------------------------------------------------------------------
# PLAYER STORY STATE
# ---------------------------------------------------------------------------

def ensure_story_state(player: Dict):
    """Ensure story mission data exists in player profile."""
    if "missions" not in player:
        player["missions"] = {}
    player["missions"].setdefault("story", {})
    story = player["missions"]["story"]
    story.setdefault("active", {})
    story.setdefault("current", None)
    story.setdefault("completed", [])


def get_current_story(player: Dict) -> Optional[Dict]:
    ensure_story_state(player)
    current = player["missions"]["story"].get("current")
    if not current:
        return None
    return player["missions"]["story"]["active"].get(current)


# ---------------------------------------------------------------------------
# DIALOGUE ENGINE
# ---------------------------------------------------------------------------

def play_dialogue_sequence(dialogues: List[Dict]):
    """Play a dialogue sequence (multi-paragraph RPG-style)."""
    clear()
    type_out("=== Dialogue Sequence ===")
    for line in dialogues:
        speaker = line.get("speaker", "Unknown")
        text = line.get("text", "")
        print()
        type_out(f"{speaker}:")
        type_out(f"  {text}")
        pause("Press Enter to continue...")
    type_out("=== End of Dialogue ===")
    pause()


# ---------------------------------------------------------------------------
# STORY FLOW
# ---------------------------------------------------------------------------

def start_story_mission(player: Dict, mission_id: str):
    """Start a story mission by ID."""
    defs = load_story_definitions()
    if mission_id not in defs:
        type_out(f"❌ Story mission {mission_id} not found.")
        return False

    ensure_story_state(player)
    mission_def = defs[mission_id]

    instance = {
        "id": mission_id,
        "title": mission_def["title"],
        "description": mission_def.get("description", ""),
        "steps": mission_def.get("steps", []),
        "current_step": 0,
        "reward": mission_def.get("reward", 0),
        "next": mission_def.get("next"),
    }

    player["missions"]["story"]["active"] = {mission_id: instance}
    player["missions"]["story"]["current"] = mission_id
    save_player(player)

    type_out(f"� Story Mission Started: {mission_def['title']}")
    pause("Press Enter to continue...")
    check_story_triggers(player)
    return True


def _advance_step(player: Dict, mission_id: str):
    """Move to next step, handle completion when last step reached."""
    inst = player["missions"]["story"]["active"].get(mission_id)
    if not inst:
        return
    inst["current_step"] += 1
    steps = inst.get("steps", [])
    if inst["current_step"] >= len(steps):
        _complete_story(player, mission_id)
    else:
        save_player(player)
        check_story_triggers(player)


def _complete_story(player: Dict, mission_id: str):
    """Mark story complete, grant reward, and unlock next mission."""
    defs = load_story_definitions()
    inst = player["missions"]["story"]["active"].get(mission_id)
    reward = inst.get("reward", 0)
    player["credits"] += reward
    type_out(f"� Story Complete: {inst['title']} — +{reward} credits!")
    player["missions"]["story"]["completed"].append(mission_id)
    player["missions"]["story"]["active"] = {}
    player["missions"]["story"]["current"] = None
    save_player(player)
    pause()

    next_id = inst.get("next")
    if next_id:
        type_out("Next story mission unlocked.")
        pause()
        start_story_mission(player, next_id)


# ---------------------------------------------------------------------------
# STEP TRIGGERS (TRAVEL, DOCK, COMBAT, DIALOGUE)
# ---------------------------------------------------------------------------

def check_story_triggers(player: Dict):
    """Check if current step conditions are met and auto-progress."""
    inst = get_current_story(player)
    if not inst:
        return
    step_idx = inst.get("current_step", 0)
    steps = inst.get("steps", [])
    if step_idx >= len(steps):
        return

    step = steps[step_idx]
    stype = step.get("type")

    if stype == "dialogue":
        dialogues = step.get("dialogues")
        if dialogues:
            play_dialogue_sequence(dialogues)
        _advance_step(player, inst["id"])
        return

    if stype == "travel":
        if player.get("location") == step.get("target"):
            type_out(f"Arrived at {step['target']}.")
            _advance_step(player, inst["id"])
            return

    if stype == "dock":
        docked = player.get("docked_at") or player.get("current_station")
        if docked and step.get("target") in docked:
            type_out(f"Docked at {docked}.")
            _advance_step(player, inst["id"])
            return

    if stype == "combat":
        type_out("⚔️ Story combat initiated...")
        engage_pirates(player)
        if player["hull"] > 0:
            _advance_step(player, inst["id"])
        return
