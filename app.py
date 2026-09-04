"""
app.py
------
Streamlit GUI for the Medication Information Translator.

This is ONLY a front-end layer. It does not change any of the existing
logic — it imports and calls the same FDAClient, AITranslator, and
SearchHistory classes that main.py (the command-line version) used.
Where main.py used input()/print() in a menu loop, this file uses
Streamlit widgets (text_input, button, columns, etc.) to get input
from and show output to the user in a browser window instead.

Run with:
    streamlit run app.py
"""

import streamlit as st

from fda_client import FDAClient
from ai_translator import AITranslator
from search_history import SearchHistory

st.set_page_config(
    page_title="Medication Information Translator",
    page_icon="💊",
    layout="centered",
)

# ---------------------------------------------------------------------------
# One shared instance of each class, created once per browser session and
# reused across reruns. This mirrors main()'s three instances created at
# startup - st.session_state is Streamlit's way of persisting objects
# across each rerun of the script (Streamlit reruns the whole file on
# every interaction, so anything that needs to survive that goes here).
# ---------------------------------------------------------------------------
if "fda_client" not in st.session_state:
    st.session_state.fda_client = FDAClient()
if "ai_translator" not in st.session_state:
    st.session_state.ai_translator = AITranslator()
if "search_history" not in st.session_state:
    st.session_state.search_history = SearchHistory()
if "last_medication" not in st.session_state:
    st.session_state.last_medication = None

fda_client = st.session_state.fda_client
ai_translator = st.session_state.ai_translator
search_history = st.session_state.search_history


def run_search(drug_name: str) -> None:
    """
    Same sequence as main.py's run_search():
    input -> FDA lookup -> AI translation -> recall check -> save -> display.
    Errors are shown with st.error instead of print(), and the result is
    stored in session_state so it stays visible after the rerun that
    every Streamlit button click triggers.
    """
    drug_name = drug_name.strip()

    if drug_name == "":
        st.warning("Please enter a medication name.")
        return

    try:
        with st.spinner(f"Looking up {drug_name}..."):
            medication = fda_client.fetch_medication(drug_name)
    except ValueError as error:
        st.error(str(error))
        return
    except ConnectionError as error:
        st.error(str(error))
        return

    with st.spinner("Translating into plain language..."):
        medication.plain_language_summary = ai_translator.translate(medication.usage)

    with st.spinner("Checking for recalls..."):
        medication.recall_notice = fda_client.check_recall(drug_name)

    search_history.add_entry(medication)
    st.session_state.last_medication = medication


def display_result(medication) -> None:
    """Render one medication's full result. GUI equivalent of main.py's display_result()."""
    st.subheader(f"Results for: {medication.name.title()}")

    st.markdown("**What it's used for (technical):**")
    st.write(medication.usage)

    st.markdown("**In plain language:**")
    st.info(medication.plain_language_summary)

    st.markdown("**Warnings:**")
    st.write(medication.warnings)

    st.markdown("**Side effects:**")
    st.write(medication.side_effects)

    st.markdown("**Instructions:**")
    st.write(medication.instructions)

    if medication.recall_notice:
        st.error(f"⚠️ RECALL NOTICE: {medication.recall_notice}")
    else:
        st.success("✅ No active recall notices found.")


# ---------------------------------------------------------------------------
# Layout: title, API key notice (same check main() did at startup),
# then two tabs standing in for main.py's menu options 1 and 2.
# (Option 3, "Exit", isn't needed - closing the browser tab does that.)
# ---------------------------------------------------------------------------
st.title("💊 Medication Information Translator")
st.caption("Look up a medication and get plain-language info, powered by openFDA + Gemini.")

if ai_translator.api_key is None:
    st.warning(
        "No Gemini API key found — AI translation will be limited. "
        "Set the GEMINI_API_KEY environment variable to enable it.",
        icon="⚠️",
    )

tab_search, tab_history = st.tabs(["🔍 Look up a medication", "🕓 Search history"])

with tab_search:
    with st.form(key="search_form"):
        drug_name = st.text_input("Enter medication name", placeholder="e.g. Advil")
        submitted = st.form_submit_button("Search", use_container_width=True)

    if submitted:
        run_search(drug_name)

    if st.session_state.last_medication is not None:
        st.divider()
        display_result(st.session_state.last_medication)

with tab_history:
    all_entries = search_history.get_all()

    if not all_entries:
        st.write("No searches saved yet.")
    else:
        st.write(f"**Total searches saved:** {len(all_entries)}")
        for index, medication in enumerate(reversed(all_entries), start=1):
            with st.expander(f"{index}. {medication.name.title()}"):
                display_result(medication)
