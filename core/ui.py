# core/ui.py
"""
User Interface & Main Game Loop for Galaxy: Fractured Dawn

Handles:
- Main menu and game loop navigation
- Travel, docking, mission, and story access
- Automatic background music switching by activity
"""

import sys
from core.utils import (
    type_out,
    pause,
    clear,
    print_divider,
    play_music,
    fade_music_out,
)
from core.player import (
    load_player,
    save_player,
    show_player_status,
)
from core.travel import travel_to_system, show_system_info, dock_menu
from core.station import station_menu
from core.missions import show_player_missions, check_mission_completion
from core.story_missions import check_story_triggers, start_story_mission, track_story_progress


# ---------------------------------------------------------------------------
# MAIN MENU (START SCREEN)
# ---------------------------------------------------------------------------

def show_main_menu():
    """Main start menu for continuing or starting new game."""
    clear()
    print_divider("=")
    type_out("� GALAXY: FRACTURED DAWN")
    print_divider("=")
    print("[1] Start / Continue Game")
    print("[2] New Game (Reset Progress)")
    print("[3] Exit")
    print_divider("-")

    choice = input("> ").strip()
    if choice == "1":
        player = load_player()
        main_game_loop(player)
    elif choice == "2":
        from core.player import new_player
        confirm = input("This will erase your save. Proceed? (y/n): ").lower()
        if confirm == "y":
            player = new_player()
            type_out("New game created.")
            pause()
            main_game_loop(player)
    else:
        sys.exit()


# ---------------------------------------------------------------------------
# GAME LOOP
# ---------------------------------------------------------------------------

def main_game_loop(player: dict):
    """Main gameplay loop with music and location transitions."""
    clear()
    type_out(f"Welcome back, Captain {player['name']}!")
    fade_music_out(1000)
    play_music("Main Sector", loop=True, volume=0.55)
    check_story_triggers(player)
    pause("Press Enter to continue...")

    while True:
        clear()
        print_divider("=")
        type_out(f"� Current System: {player['location']}")
        print_divider("-")
        print("[1] Show System Info")
        print("[2] Travel")
        print("[3] Dock at Station")
        print("[4] Player Status")
        print("[5] Missions")
        print("[6] Story Mission")
        print("[7] Save & Exit")
        print_divider("-")

        choice = input("> ").strip()

        # -------------------------------------------------------------------
        # 1. Show System Info
        # -------------------------------------------------------------------
        if choice == "1":
            show_system_info(player)
            pause()

        # -------------------------------------------------------------------
        # 2. Travel
        # -------------------------------------------------------------------
        elif choice == "2":
            fade_music_out(1200)
            play_music("Spacey Oddity", loop=True, volume=0.6)
            from core.world import get_connections
            connections = get_connections(player["location"])
            if not connections:
                type_out("No jump routes available.")
                pause()
                continue

            print_divider("=")
            type_out("� Available Destinations:")
            for i, dest in enumerate(connections, start=1):
                print(f"[{i}] {dest}")
            print("[0] Cancel")
            print_divider("-")

            selection = input("> ").strip()
            if not selection.isdigit() or selection == "0":
                fade_music_out(1000)
                play_music("Main Sector", loop=True, volume=0.5)
                continue

            idx = int(selection) - 1
            if 0 <= idx < len(connections):
                destination = connections[idx]
                travel_to_system(player, destination)
                save_player(player)
                check_story_triggers(player)

            fade_music_out(1000)
            play_music("Main Sector", loop=True, volume=0.5)

        # -------------------------------------------------------------------
        # 3. Docking Menu
        # -------------------------------------------------------------------
        elif choice == "3":
            fade_music_out(1500)
            play_music("Safe Zone", loop=True, volume=0.55)
            dock_menu(player)
            if player.get("docked_at"):
                check_mission_completion(player)
                check_story_triggers(player)
                station_menu(player)
            save_player(player)
            fade_music_out(1200)
            play_music("Main Sector", loop=True, volume=0.5)

        # -------------------------------------------------------------------
        # 4. Player Status
        # -------------------------------------------------------------------
        elif choice == "4":
            show_player_status(player)
            pause()

        # -------------------------------------------------------------------
        # 5. Missions
        # -------------------------------------------------------------------
        elif choice == "5":
            fade_music_out(800)
            play_music("Safe Zone", loop=True, volume=0.55)
            show_player_missions(player)
            pause()
            fade_music_out(800)
            play_music("Main Sector", loop=True, volume=0.5)

        # -------------------------------------------------------------------
        # 6. Story Mission
        # -------------------------------------------------------------------
        elif choice == "6":
            story_menu(player)

        # -------------------------------------------------------------------
        # 7. Exit Game
        # -------------------------------------------------------------------
        elif choice == "7":
            fade_music_out(1000)
            type_out("Saving progress...")
            save_player(player)
            type_out("Goodbye, Captain.")
            pause()
            sys.exit()

        else:
            type_out("Invalid selection.")
            pause()


# ---------------------------------------------------------------------------
# STORY MENU
# ---------------------------------------------------------------------------

def story_menu(player: dict):
    """Manage story mission progression."""
    clear()
    print_divider("=")
    type_out("� Story Mission Menu")
    print_divider("-")
    print("[1] View Current Mission")
    print("[2] Start Story (if none active)")
    print("[3] Cancel Current Story Mission")
    print("[4] Return to Main Menu")
    print_divider("-")

    choice = input("> ").strip()
    if choice == "1":
        track_story_progress(player)
    elif choice == "2":
        from core.story_missions import load_story_definitions
        defs = load_story_definitions()
        current = player.get("missions", {}).get("story", {}).get("current")
        if current:
            type_out("Story mission already in progress.")
        else:
            first_mission = list(defs.keys())[0]
            start_story_mission(player, first_mission)
    elif choice == "3":
        from core.story_missions import cancel_story_mission
        cancel_story_mission(player)
    elif choice == "4":
        return
    pause()
