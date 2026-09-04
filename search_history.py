"""
search_history.py
-------------------
Defines the SearchHistory class - handles FILE HANDLING for the app.
Saves every completed search to a local JSON file, so past searches
persist even after the program closes, and can be loaded back and
displayed later.

JSON was chosen because it maps naturally onto Python dictionaries/lists,
and because Medication objects already have a to_dict() / from_dict()
pair (see medication.py) specifically to make saving/loading easy.
"""

import json
import os
from medication import Medication

DEFAULT_FILE_PATH = "search_history.json"


class SearchHistory:
    """Handles saving and loading medication search history to/from a file."""

    def __init__(self, file_path: str = DEFAULT_FILE_PATH):
        self.file_path = file_path

    def add_entry(self, medication: Medication) -> None:
        """
        Add one Medication search result to the history file.
        Loads whatever's already saved, appends the new entry, then
        writes the whole updated list back to the file.
        """
        history = self._load_raw()
        history.append(medication.to_dict())
        self._save_raw(history)

    def get_all(self) -> list:
        """
        Return every past search as a list of Medication objects,
        most recent last (same order they were saved in).
        """
        raw_history = self._load_raw()
        return [Medication.from_dict(entry) for entry in raw_history]

    def _load_raw(self) -> list:
        """
        Internal helper: read the raw list of dictionaries from the file.
        Handles two expected failure cases gracefully:
          - the file doesn't exist yet (first run) -> returns an empty list
          - the file exists but contains invalid/corrupted JSON -> also
            returns an empty list, rather than crashing the whole program
        """
        if not os.path.exists(self.file_path):
            return []

        try:
            with open(self.file_path, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            return []

    def _save_raw(self, history: list) -> None:
        """Internal helper: write the given list of dictionaries to the file as JSON."""
        with open(self.file_path, "w") as file:
            json.dump(history, file, indent=2)

    def count(self) -> int:
        """Return how many searches have been saved in total."""
        return len(self._load_raw())
