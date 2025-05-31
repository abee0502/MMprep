import streamlit as st
from flashcards import load_wrong_answers, save_wrong_answers
import random

def run_practice_mode(flashcards):
    total = len(flashcards)

    # Session state initialization
    if 'answered_ids' not in st.session_state:
        st.session_state.answered_ids = set()
    if 'practice_index' not in st.session_state:
        st.session_state.practice_index = 0
    if 'question_order' not in st.session_state:
        st.session_state.question_order = list(range(total))
        random.shuffle(st.session_state.question_order)

    # Filter for unanswered questions
    unanswered_ids = [i for i in st.session_state.question_order if i not in st.session_state.answered_ids]
    if not unanswered_ids:
        st.session_state.answered_ids = set()
        random.shuffle(st.session_state.question_order)
        unanswered_ids = st.session_state.question_order.copy()
        st.session_state.practice_index = 0

    # Current question index
    idx = unanswered_ids[st.session_state.practice_index % len(unanswered_ids)]
    card = flashcards[idx]

    # UI
    st.subheader(f"Question {len(st.session_state.answered_ids) + 1} of {total}")
    st.progress((len(st.session_state.answered_ids) + 1) / total)
    st.write(card['question'])
    st.markdown(f"**{card.get('instruction', '')}**")

    selected = []
    for key, val in card['options'].items():
        if st.checkbox(f"{key}. {val}", key=f"practice_{idx}_{key}"):
            selected.append(key)

    if st.button("Submit Answer") and selected:
        correct = set(card['answers'])
        chosen = set(selected)

        if correct == chosen:
            st.success("✅ Correct!")
        elif correct & chosen:
            st.warning(f"🟡 Partially correct. Correct answer(s): {', '.join(correct)}")
        else:
            st.error(f"❌ Incorrect. Correct answer(s): {', '.join(correct)}")

        wrong_counts = load_wrong_answers()
        if correct != chosen:
            wrong_counts[str(idx)] = wrong_counts.get(str(idx), 0) + 1
        save_wrong_answers(wrong_counts)

        st.session_state.answered_ids.add(idx)

    # Navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Previous"):
            st.session_state.practice_index = max(0, st.session_state.practice_index - 1)
    with col2:
        if st.button("Next ➡️"):
            st.session_state.practice_index += 1
