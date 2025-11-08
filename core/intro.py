# core/intro.py
"""
Intro Cinematic for Galaxy: Fractured Dawn

A text-based story opening inspired by Galaxy on Fire HD,
introducing the player to the fractured state of the galaxy.
"""

from core.utils import type_out, clear, print_divider, pause
import time


def play_intro():
    """Plays the cinematic intro with scrolling text."""
    clear()
    print_divider("=")
    type_out("� GALAXY: FRACTURED DAWN")
    print_divider("=")
    time.sleep(1.5)

    # Opening narrative
    paragraphs = [
        "In the twilight of the 4th Expansion Era, the Orion Federation collapsed.",
        "Worlds once bound by trade and science became fractured realms — isolated, lawless, and desperate.",
        "Pirates claimed the outer sectors. Corporations built empires in the shadows. The old fleets were gone... and with them, order itself.",
        "",
        "You are one of the drifters — a survivor, a smuggler, a pilot seeking purpose among the ruins of a once-great civilization.",
        "Your ship may be small, your weapons outdated... but the stars still call your name.",
        "",
        "Somewhere beyond the border worlds, whispers speak of an anomaly — a power older than the galaxy itself.",
        "Those who seek it vanish. Those who find it... are never the same.",
        "",
        "This is your story. Your flight. Your fractured dawn."
    ]

    for para in paragraphs:
        type_out(para)
        time.sleep(1.5)

    print_divider("-")
    type_out("Initializing flight systems...")
    time.sleep(1.2)
    type_out("Restoring pilot memory core...")
    time.sleep(1.2)
    type_out("Power grid nominal. Engines online.")
    time.sleep(1.2)
    print_divider("=")
    type_out("� Welcome to Galaxy: Fractured Dawn.")
    pause()
