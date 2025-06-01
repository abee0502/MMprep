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
    if 'question_order' not in st.session_state:
        st.session_state.question_order = list(range(total))
        random.shuffle(st.session_state.question_order)
    if 'practice_history' not in st.session_state:
        st.session_state.practice_history = []
    if 'submit_answer' not in st.session_state:
        st.session_state.submit_answer = False
    if 'current_question_id' not in st.session_state:
        unanswered = [i for i in st.session_state.question_order if i not in st.session_state.answered_ids]
        st.session_state.current_question_id = unanswered[0] if unanswered else None

    # Filter unanswered questions
    unanswered_ids = [i for i in st.session_state.question_order if i not in st.session_state.answered_ids]

    # Handle completed session
    if not unanswered_ids and len(st.session_state.answered_ids) > 0:
        st.success("🎉 You've answered all questions! Restarting practice session.")
        st.session_state.answered_ids = set()
        st.session_state.practice_history = []
        st.session_state.current_question_id = None
        random.shuffle(st.session_state.question_order)
        if os.path.exists("answered_questions.json"):
            os.remove("answered_questions.json")
        st.stop()

    # Pick the current question
    idx = st.session_state.current_question_id or unanswered_ids[0]
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
        st.session_state.submit_answer = True

    if st.session_state.submit_answer:
        st.session_state.submit_answer = False  # Reset trigger

        correct = set(card['answers'])
        chosen = set(selected)

        if correct == chosen:
            st.success("✅ Correct!")
        elif correct & chosen:
            st.warning(f"🟡 Partially correct. Correct answer(s): {', '.join(correct)}")
        else:
            st.error(f"❌ Incorrect. Correct answer(s): {', '.join(correct)}")

        # Save to wrong answer tracking
        wrong_counts = load_wrong_answers()
        if correct != chosen:
            wrong_counts[str(idx)] = wrong_counts.get(str(idx), 0) + 1
        save_wrong_answers(wrong_counts)

        # Save answered state
        st.session_state.answered_ids.add(idx)
        st.session_state.practice_history.append(idx)
        save_answered_ids(st.session_state.answered_ids)

    # Navigation
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Previous"):
            if st.session_state.practice_history:
                st.session_state.current_question_id = st.session_state.practice_history.pop()
    with col2:
        if st.button("Next ➡️"):
            remaining = [i for i in unanswered_ids if i != idx]
            if remaining:
                st.session_state.practice_history.append(idx)
                st.session_state.current_question_id = remaining[0]

    # Reset all progress
    if st.button("🔁 Reset Practice Progress"):
        st.session_state.answered_ids = set()
        st.session_state.practice_history = []
        st.session_state.current_question_id = None
        if os.path.exists("answered_questions.json"):
            os.remove("answered_questions.json")
        st.success("✅ Practice progress has been reset.")
        st.stop()
