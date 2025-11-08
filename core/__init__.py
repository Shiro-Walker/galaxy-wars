# core/__init__.py
"""
Core package initialization for Galaxy: Fractured Dawn.

This directory contains all core game modules, including:
- utils: helper functions (printing, clearing, dice rolls)
- data: ship templates, commodities, base stats
- player: save/load player data, ship management
- world: galaxy map generation and system data
- travel: inter-system navigation and random events
- mining: resource gathering system
- combat: turn-based battle logic
- missions: side and bounty missions
- story_missions: main story campaign
- station: docking, market, bar, hangar, mission board
- ui: main interface and dynamic menus
- intro: cinematic intro and new game setup
"""

__all__ = [
    "utils",
    "data",
    "player",
    "world",
    "travel",
    "mining",
    "combat",
    "missions",
    "story_missions",
    "station",
    "ui",
    "intro",
]

def describe_core():
    """Quick summary of available core systems."""
    systems = [
        "Utilities / Engine Core",
        "Galaxy Map & Travel System",
        "Combat Engine",
        "Mining & Resource Gathering",
        "Story & Side Missions",
        "Docking / Station Systems",
        "Player Save Management",
        "Intro Cinematic & Game Flow",
    ]
    print("=== Core Systems Loaded ===")
    for s in systems:
        print(" -", s)
