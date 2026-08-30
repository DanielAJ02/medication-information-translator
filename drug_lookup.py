import requests


BASE_URL = "https://api.fda.gov/drug/label.json"


def get_drug_info(drug_name):
    """Fetch drug information from the openFDA API."""

    try:
        params = {
            "search": f'openfda.brand_name:"{drug_name}"',
            "limit": 1
        }

        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        if "results" not in data or not data["results"]:
            return {
                "success": False,
                "message": f"No information found for '{drug_name}'."
            }

        drug = data["results"][0]

        return {
            "success": True,
            "drug_name": drug_name,
            "usage": drug.get(
                "indications_and_usage",
                ["Information not available."]
            )[0],
            "warnings": drug.get(
                "warnings",
                ["Information not available."]
            )[0],
            "side_effects": drug.get(
                "adverse_reactions",
                ["Information not available."]
            )[0],
            "instructions": drug.get(
                "dosage_and_administration",
                ["Information not available."]
            )[0]
        }

    except requests.exceptions.RequestException as error:
        return {
            "success": False,
            "message": f"Error fetching drug information: {error}"
        }


if __name__ == "__main__":
    drug_name = input("Enter a medication name: ")

    result = get_drug_info(drug_name)

    if result["success"]:
        print("\nDrug:", result["drug_name"])

        print("\n--- USAGE ---")
        print(result["usage"])

        print("\n--- WARNINGS ---")
        print(result["warnings"])

        print("\n--- SIDE EFFECTS ---")
        print(result["side_effects"])

        print("\n--- INSTRUCTIONS ---")
        print(result["instructions"])

    else:
        print(result["message"])