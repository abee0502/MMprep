import streamlit as st
from flashcards import load_flashcards
from practice_mode import run_practice_mode
from test_mode import run_test_mode
from bundle_mode import run_bundle_mode
from review_mode import run_review_mode
from full_review_mode import run_full_review_mode

def main():
    # ✅ Initialize persistent session state once
    if "initialized" not in st.session_state:
        st.session_state.answered_ids = set()
        st.session_state.practice_index = 0
        st.session_state.question_order = []
        st.session_state.initialized = True

    st.set_page_config(page_title="SAP Flashcard App", layout="wide")
    st.title("📘 SAP Flashcard Practice App")

    flashcards = load_flashcards()

    mode = st.sidebar.radio("Select Mode", [
        "Practice Mode",
        "Test Mode",
        "Bundle Practice Mode",
        "Mistake Review Mode",
        "Wrong Answer Practice Mode",
        "Full Review Mode"
    ])

    if mode == "Practice Mode":
        run_practice_mode(flashcards)
    elif mode == "Test Mode":
        run_test_mode(flashcards)
    elif mode == "Bundle Practice Mode":
        run_bundle_mode(flashcards)
    elif mode == "Mistake Review Mode":
        run_review_mode(flashcards, review_only=True)
    elif mode == "Wrong Answer Practice Mode":
        run_review_mode(flashcards, review_only=False)
    elif mode == "Full Review Mode":
        run_full_review_mode(flashcards)

if __name__ == "__main__":
    main()
