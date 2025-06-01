import streamlit as st
import random
import os
from flashcards import (
    load_wrong_answers, save_wrong_answers,
    load_answered_ids, save_answered_ids
)

def run_practice_mode(flashcards):
    total = len(flashcards)

    if total == 0:
        st.error("⚠️ No flashcards found. Please check your questions.json.")
        st.stop()

    # Initialize session state
    if 'answered_ids' not in st.session_state:
        st.session_state.answered_ids = load_answered_ids()
    if 'practice_index' not in st.session_state:
        st.session_state.practice_index = 0
    if 'question_order' not in st.session_state:
        st.session_state.question_order = list(range(total))
        random.shuffle(st.session_state.question_order)
    if 'practice_history' not in st.session_state:
        st.session_state.practice_history = []

    # Filter unanswered questions
    unanswered_ids = [i for i in st.session_state.question_order if i not in st.session_state.answered_ids]

    if not unanswered_ids and len(st.session_state.answered_ids) > 0:
        st.success("🎉 You've answered all questions! Restarting practice session.")
        st.session_state.answered_ids = set()
        random.shuffle(st.session_state.question_order)
        st.session_state.practice_index = 0
        st.session_state.practice_history = []
        st.stop()

    # Current question
    idx = unanswered_ids[st.session_state.practice_index % len(unanswered_ids)]
    card = flashcards[idx]

    # UI
    st.subheader(f"Question {len(st.session_state.answered_ids) + 1} of {total}")
    st.progress((len(st.session_state.answered_ids) + 1) / total)
    st.write(card['question'])
    st.markdown(f"**{card.get('instruction', '')}**")

    selected = []
    for key, val in card['options'].items():
        if st.session_state.get(f"practice_{idx}_{key}", False):
            selected.append(key)
        st.checkbox(f"{key}. {val}", key=f"practice_{idx}_{key}")

    if st.button("Submit Answer") and selected:
        correct = set(card['answers'])
        chosen = set(selected)

        if correct == chosen:
            st.success("✅ Correct!")
        elif correct & chosen:
            st.warning(f"🟡 Partially correct. Correct answer(s): {', '.join(correct)}")
        else:
            st.error(f"❌ Incorrect. Correct answer(s): {', '.join(correct)}")

        # Track wrong answers
        wrong_counts = load_wrong_answers()
        if correct != chosen:
            wrong_counts[str(idx)] = wrong_counts.get(str(idx), 0) + 1
        save_wrong_answers(wrong_counts)

        # Save progress
        st.session_state.answered_ids.add(idx)
        st.session_state.practice_history.append(idx)
        save_answered_ids(st.session_state.answered_ids)

    # Navigation
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Previous"):
            if st.session_state.practice_history:
                st.session_state.practice_index = max(0, st.session_state.practice_history.pop())
    with col2:
        if st.button("Next ➡️"):
            st.session_state.practice_index += 1

    # Reset button
    if st.button("🔁 Reset Practice Progress"):
        st.session_state.answered_ids = set()
        st.session_state.practice_index = 0
        st.session_state.practice_history = []
        if os.path.exists("answered_questions.json"):
            os.remove("answered_questions.json")
        st.success("✅ Practice progress has been reset.")
        st.stop()
