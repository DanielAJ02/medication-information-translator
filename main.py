"""
main.py
-------
Entry point of the Medication Information Translator.

Creates one instance of each class (FDAClient, AITranslator, SearchHistory),
then runs a simple menu loop that coordinates them:
  1. Look up a medication  -> FDAClient fetches it, AITranslator simplifies
     the language, FDAClient checks for a recall, SearchHistory saves it.
  2. View search history    -> SearchHistory loads and displays past searches.
  3. Exit
"""

from fda_client import FDAClient
from ai_translator import AITranslator
from search_history import SearchHistory


def show_menu() -> None:
    print("\n===== Medication Information Translator =====")
    print("1. Look up a medication")
    print("2. View search history")
    print("3. Exit")
    print("===============================================")


def get_menu_choice() -> int:
    """Loop until the user enters a valid menu number (1-3)."""
    while True:
        raw = input("Choose an option: ").strip()
        try:
            choice = int(raw)
            if choice in (1, 2, 3):
                return choice
            print("Please enter 1, 2, or 3.")
        except ValueError:
            print("That's not a valid number.")


def run_search(fda_client: FDAClient, ai_translator: AITranslator,
               search_history: SearchHistory) -> None:
    """
    Runs one full medication search:
    input -> FDA lookup -> AI translation -> recall check -> save -> display.
    Every external call (FDA API, Gemini API) is wrapped in a try/except,
    since these are the points most likely to fail (bad input, no internet,
    drug not found, missing API key).
    """
    drug_name = input("\nEnter medication name: ").strip()

    if drug_name == "":
        print("[X] Please enter a medication name.")
        return

    try:
        medication = fda_client.fetch_medication(drug_name)
    except ValueError as error:
        print(f"[X] {error}")
        return
    except ConnectionError as error:
        print(f"[X] {error}")
        return

    print("\nTranslating into plain language, please wait...")
    medication.plain_language_summary = ai_translator.translate(medication.usage)

    recall_notice = fda_client.check_recall(drug_name)
    medication.recall_notice = recall_notice

    display_result(medication)

    search_history.add_entry(medication)


def display_result(medication) -> None:
    """Print a single medication's full result to the screen."""
    print("\n" + "-" * 60)
    print(f"RESULTS FOR: {medication.name.title()}")
    print("-" * 60)

    print("\nWhat it's used for (technical):")
    print(f"  {medication.usage}")

    print("\nIn plain language:")
    print(f"  {medication.plain_language_summary}")

    print("\nWarnings:")
    print(f"  {medication.warnings}")

    print("\nSide effects:")
    print(f"  {medication.side_effects}")

    print("\nInstructions:")
    print(f"  {medication.instructions}")

    print()
    if medication.recall_notice:
        print(f"[!] RECALL NOTICE: {medication.recall_notice}")
    else:
        print("[OK] No active recall notices found.")

    print("-" * 60)


def view_history(search_history: SearchHistory) -> None:
    """Show every past search saved so far."""
    all_entries = search_history.get_all()

    if not all_entries:
        print("\nNo searches saved yet.")
        return

    print(f"\nTotal searches saved: {len(all_entries)}")
    for index, medication in enumerate(all_entries, start=1):
        print(f"{index}. {medication.name.title()}")


def main() -> None:
    fda_client = FDAClient()
    ai_translator = AITranslator()
    search_history = SearchHistory()

    print("Welcome to the Medication Information Translator!")

    if ai_translator.api_key is None:
        print("[!] No Gemini API key found - AI translation will be limited.")
        print("    Set the GEMINI_API_KEY environment variable to enable it.")

    while True:
        show_menu()
        choice = get_menu_choice()

        if choice == 1:
            run_search(fda_client, ai_translator, search_history)
        elif choice == 2:
            view_history(search_history)
        elif choice == 3:
            print("Goodbye!")
            break


if __name__ == "__main__":
    main()
