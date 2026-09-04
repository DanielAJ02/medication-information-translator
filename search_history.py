"""
Module 5 — Search History
Medication Information Translator

Owner: Joey

Responsibilities:
    - Save medication searches to a local JSON file.
    - Retrieve previous searches so users can view their search history.

Data File:
    data/search_history.json

Functions:
    save_search(name)  -> Saves a medication search (with a timestamp).
    load_history()      -> Returns a list of previous searches.
"""

import json
import os
from datetime import datetime

# Path to the JSON file that stores search history.
# Kept relative to the project root so it works no matter which module
# imports this file, as long as the app is run from the project root.
HISTORY_FILE = os.path.join("data", "search_history.json")


def _ensure_data_file_exists():
    """Make sure the data folder and history file exist before we touch them.

    If the 'data' folder is missing, create it. If the JSON file is missing
    or empty/corrupted, (re)initialize it with an empty list so the rest of
    the module can always assume valid JSON is on disk.
    """
    folder = os.path.dirname(HISTORY_FILE)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)

    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "w", encoding="utf-8") as file:
            json.dump([], file)
        return

    # File exists — check it actually contains valid JSON. If a previous
    # run crashed mid-write, or the file was hand-edited badly, this
    # recovers gracefully instead of crashing the whole app.
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            json.load(file)
    except (json.JSONDecodeError, ValueError):
        with open(HISTORY_FILE, "w", encoding="utf-8") as file:
            json.dump([], file)


def save_search(name):
    """Save a medication search to the local history file.

    Args:
        name (str): The medication name the user searched for.

    Raises:
        ValueError: If `name` is empty, blank, or not a string.

    Each entry is stored as a dict with the medication name and a timestamp,
    e.g. {"medication": "Ibuprofen", "timestamp": "2026-07-25T14:32:00"}.
    """
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Medication name must be a non-empty string.")

    clean_name = name.strip()

    _ensure_data_file_exists()

    try:
        history = load_history()

        entry = {
            "medication": clean_name,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }
        history.append(entry)

        with open(HISTORY_FILE, "w", encoding="utf-8") as file:
            json.dump(history, file, indent=2)

    except (OSError, IOError) as error:
        # Covers permission errors, disk issues, etc. We don't want a
        # failed history save to crash the whole medication lookup flow.
        print(f"⚠️ Could not save search history: {error}")


def load_history():
    """Load and return the list of previous medication searches.

    Returns:
        list[dict]: A list of previous search entries, most recent last.
                     Returns an empty list if there is no history yet or
                     if the history file could not be read.
    """
    _ensure_data_file_exists()

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            history = json.load(file)

        if not isinstance(history, list):
            # Defensive check: file was tampered with / not the shape we expect.
            return []

        return history

    except (json.JSONDecodeError, OSError, IOError) as error:
        print(f"⚠️ Could not load search history: {error}")
        return []


# ---------------------------------------------------------------------------
# Quick manual test — run this file directly to see it work in isolation.
# (Remove or leave in as a demo; won't run when imported by the main app.)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    save_search("Ibuprofen")
    save_search("Amoxicillin")

    print("Current search history:")
    for entry in load_history():
        print(f" - {entry['medication']} (searched at {entry['timestamp']})")
