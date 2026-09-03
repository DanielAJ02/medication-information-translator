"""
fda_client.py
--------------
Defines the FDAClient class - handles all communication with the two
openFDA APIs:
  1. Drug Labeling API  -> usage, warnings, side effects, instructions
  2. Recall/Enforcement API -> active recall notices

Also handles:
  - regex validation of the medication name before searching
  - network errors (no internet, timeout)
  - missing/empty results (drug not found, or found but some fields blank)

openFDA does not require an API key for reasonable personal/student use,
which is why there's no key needed here (unlike AITranslator's Gemini calls).
"""

import re
import requests
from medication import Medication

FDA_LABEL_URL = "https://api.fda.gov/drug/label.json"
FDA_RECALL_URL = "https://api.fda.gov/drug/enforcement.json"

# A medication name should only contain letters, spaces, and hyphens.
# This regex pattern is used to validate input before we ever call the API -
# catches obvious junk input early, instead of wasting an API call on it.
VALID_NAME_PATTERN = re.compile(r"^[A-Za-z\s\-]+$")


class FDAClient:
    """Handles all lookups against the openFDA APIs."""

    def is_valid_name(self, drug_name: str) -> bool:
        """
        Check a medication name against VALID_NAME_PATTERN using regex.
        Returns True only if the name contains letters/spaces/hyphens only,
        and isn't empty.
        """
        name = drug_name.strip()
        if not name:
            return False
        return bool(VALID_NAME_PATTERN.match(name))

    def fetch_medication(self, drug_name: str) -> Medication:
        """
        Look up a medication by name using the openFDA Drug Labeling API.
        Returns a Medication object filled with whatever fields were found.
        Raises ValueError if the name is invalid or nothing was found.
        Raises ConnectionError if the request fails due to network issues.
        """
        if not self.is_valid_name(drug_name):
            raise ValueError(
                f"'{drug_name}' is not a valid medication name "
                "(only letters, spaces, and hyphens are allowed)"
            )

        query = f'openfda.brand_name:"{drug_name}"'
        params = {"search": query, "limit": 1}

        try:
            response = requests.get(FDA_LABEL_URL, params=params, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as error:
            raise ConnectionError(f"Could not reach the FDA API: {error}")

        data = response.json()
        results = data.get("results")

        if not results:
            raise ValueError(f"No information found for '{drug_name}'")

        record = results[0]

        # Each of these fields can be MISSING from the API's response
        # depending on the drug, so we use .get() with a fallback list
        # and safely grab the first item, or an empty string if nothing's there.
        return Medication(
            name=drug_name,
            usage=self._first_or_default(record.get("indications_and_usage")),
            warnings=self._first_or_default(record.get("warnings")),
            side_effects=self._first_or_default(record.get("adverse_reactions")),
            instructions=self._first_or_default(record.get("dosage_and_administration")),
        )

    def check_recall(self, drug_name: str) -> str:
        """
        Check the openFDA Recall/Enforcement API for an active recall
        notice on this medication. Returns the recall reason as a string,
        or an empty string if no recall is found.
        Network errors here are caught and turned into a warning string
        rather than crashing the whole search, since a recall check
        failing shouldn't block showing the user the drug info they asked for.
        """
        query = f'openfda.brand_name:"{drug_name}"'
        params = {"search": query, "limit": 1}

        try:
            response = requests.get(FDA_RECALL_URL, params=params, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            return "Could not check recall status (network issue)."

        data = response.json()
        results = data.get("results")

        if not results:
            return ""

        record = results[0]
        return record.get("reason_for_recall", "Recall found, but no reason was listed.")

    @staticmethod
    def _first_or_default(field_value, default: str = "Not specified") -> str:
        """
        openFDA often returns fields as a LIST of strings (sometimes with
        just one item). This helper safely grabs the first item, or
        returns a default message if the field was missing/empty entirely.
        """
        if isinstance(field_value, list) and len(field_value) > 0:
            return field_value[0]
        return default
