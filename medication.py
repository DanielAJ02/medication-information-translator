"""
medication.py
--------------
Defines the Medication class - a simple container for one medication's
information. Its whole job is to hold data cleanly, so other classes
(FDAClient, AITranslator, SearchHistory) don't have to pass around a
loose collection of separate variables or a raw dictionary.

This is a good first class to learn OOP with: it has almost no logic,
just an __init__ to store values and a couple of helper methods.
"""


class Medication:
    """Represents a single medication and its key information."""

    def __init__(self, name: str, usage: str = "", warnings: str = "",
                 side_effects: str = "", instructions: str = ""):
        self.name = name
        self.usage = usage
        self.warnings = warnings
        self.side_effects = side_effects
        self.instructions = instructions

        # These start empty and get filled in later by AITranslator
        # and FDAClient once those steps run.
        self.plain_language_summary = ""
        self.recall_notice = ""

    def to_dict(self) -> dict:
        """
        Convert this Medication object into a plain dictionary.
        Needed because JSON files (used by SearchHistory) can only
        store simple data types like dicts, lists, strings and numbers -
        not custom objects like Medication directly.
        """
        return {
            "name": self.name,
            "usage": self.usage,
            "warnings": self.warnings,
            "side_effects": self.side_effects,
            "instructions": self.instructions,
            "plain_language_summary": self.plain_language_summary,
            "recall_notice": self.recall_notice,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Medication":
        """
        Build a Medication object back FROM a dictionary.
        Used when loading saved search history back out of the JSON file.
        A classmethod is a function that builds/returns an instance of
        the class itself, rather than working on an existing instance.
        """
        med = cls(
            name=data.get("name", ""),
            usage=data.get("usage", ""),
            warnings=data.get("warnings", ""),
            side_effects=data.get("side_effects", ""),
            instructions=data.get("instructions", ""),
        )
        med.plain_language_summary = data.get("plain_language_summary", "")
        med.recall_notice = data.get("recall_notice", "")
        return med

    def __str__(self) -> str:
        """
        Controls what gets shown when you print(some_medication_object)
        or convert it to a string. Without this, printing an object
        would just show something unhelpful like <Medication object at 0x...>.
        """
        return f"Medication: {self.name.title()}"
