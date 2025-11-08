# core/utils.py
"""
Utility Functions for Galaxy: Fractured Dawn

Provides:
- Text formatting, animation, and colors
- Console control (clear, pause)
- D&D-style dice rolling and parsing
- Probability rolls
- Sound & Music integration system
"""

import os
import sys
import time
import random
import re

# ---------------------------------------------------------------------------
# BASIC UTILITIES
# ---------------------------------------------------------------------------

def type_out(text: str, delay: float = 0.02, newline: bool = True):
    """Display text gradually for cinematic pacing."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    if newline:
        print()


def print_divider(char: str = "-", length: int = 50):
    """Simple divider line for menus."""
    print(char * length)


def clear():
    """Clear terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def pause(msg: str = "Press Enter to continue..."):
    """Pause until input."""
    input(msg)


# ---------------------------------------------------------------------------
# COLOR SYSTEM
# ---------------------------------------------------------------------------

class Colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def color_text(text: str, color: str) -> str:
    """Wrap text with ANSI color codes."""
    return f"{color}{text}{Colors.ENDC}"


def info(text: str): print(color_text(text, Colors.OKBLUE))
def success(text: str): print(color_text(text, Colors.OKGREEN))
def warning(text: str): print(color_text(text, Colors.WARNING))
def error(text: str): print(color_text(text, Colors.FAIL))


# ---------------------------------------------------------------------------
# CHANCE / PROBABILITY SYSTEM
# ---------------------------------------------------------------------------

def chance(percent: int) -> bool:
    """Return True with a given percentage chance (1–100)."""
    return random.randint(1, 100) <= max(0, min(percent, 100))


# ---------------------------------------------------------------------------
# DICE MECHANICS (D&D STYLE)
# ---------------------------------------------------------------------------

def roll_dice(sides: int = 20) -> int:
    """Roll a single die (default d20)."""
    return random.randint(1, sides)


def roll_with_advantage(sides: int = 20) -> int:
    """Roll twice, take the higher."""
    return max(random.randint(1, sides), random.randint(1, sides))


def roll_with_disadvantage(sides: int = 20) -> int:
    """Roll twice, take the lower."""
    return min(random.randint(1, sides), random.randint(1, sides))


def roll_dnd(dice_str: str) -> int:
    """
    Roll D&D-style dice notation like '2d6+3' or '1d20'.
    Returns total result and prints the roll breakdown.
    """
    match = re.match(r"(\d*)d(\d+)([+-]\d+)?", dice_str.replace(" ", ""))
    if not match:
        raise ValueError(f"Invalid dice format: {dice_str}")

    num = int(match.group(1)) if match.group(1) else 1
    sides = int(match.group(2))
    mod = int(match.group(3)) if match.group(3) else 0

    rolls = [random.randint(1, sides) for _ in range(num)]
    total = sum(rolls) + mod
    print(f"� roll_dnd({dice_str}) → rolls={rolls} total={total}")
    return total


def skill_check(dc: int, modifier: int = 0) -> (bool, int):
    """Perform D&D style skill check (returns success flag, total)."""
    roll = roll_dice(20)
    total = roll + modifier
    success_flag = total >= dc
    result = "✅ Success!" if success_flag else "❌ Failed."
    print(f"� Rolled {roll} + {modifier} = {total} | DC {dc} → {result}")
    return success_flag, total


# ---------------------------------------------------------------------------
# RANDOM HELPERS
# ---------------------------------------------------------------------------

def weighted_choice(choices: dict):
    """Randomly select item from dict of {item: weight}."""
    total = sum(choices.values())
    r = random.uniform(0, total)
    upto = 0
    for item, weight in choices.items():
        if upto + weight >= r:
            return item
        upto += weight
    return random.choice(list(choices.keys()))


def random_name(prefix="SYS") -> str:
    """Generate a random system or NPC name."""
    suffix = random.randint(100, 999)
    return f"{prefix}-{suffix}"


# ---------------------------------------------------------------------------
# SOUND / MUSIC SYSTEM
# ---------------------------------------------------------------------------

import pygame
SOUND_PATH = "BGM"
_music_initialized = False


def init_audio():
    """Initialize pygame mixer safely."""
    global _music_initialized
    if _music_initialized:
        return
    try:
        pygame.mixer.init()
        _music_initialized = True
        print("[Audio] Mixer initialized.")
    except Exception as e:
        print(f"[Audio Init Error] {e}")
        _music_initialized = False


def play_music(track_name: str, loop: bool = True, volume: float = 0.6):
    """Play background music from /BGM directory."""
    init_audio()
    if not _music_initialized:
        return
    file_path = os.path.join(SOUND_PATH, f"{track_name}.wav")
    if not os.path.exists(file_path):
        print(f"[Audio] Missing track: {file_path}")
        return
    try:
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1 if loop else 0)
        print(f"[Audio] Now playing: {track_name}")
    except Exception as e:
        print(f"[Audio Error] {e}")


def stop_music():
    """Stop all music playback."""
    try:
        pygame.mixer.music.stop()
    except Exception:
        pass


def fade_music_out(duration_ms: int = 2000):
    """Fade out currently playing music."""
    try:
        pygame.mixer.music.fadeout(duration_ms)
    except Exception:
        pass


def play_sound_effect(effect_name: str, volume: float = 1.0):
    """Play short sound effect (safe if file missing)."""
    init_audio()
    if not _music_initialized:
        return
    file_path = os.path.join(SOUND_PATH, f"{effect_name}.wav")
    if not os.path.exists(file_path):
        return
    try:
        sound = pygame.mixer.Sound(file_path)
        sound.set_volume(volume)
        sound.play()
    except Exception as e:
        print(f"[Sound Effect Error] {e}")
