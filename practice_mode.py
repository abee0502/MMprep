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

    # ─── Initialize session state ──────────────────────────────────
    if 'answered_ids' not in st.session_state:
        st.session_state.answered_ids = load_answered_ids()

    if 'question_order' not in st.session_state:
        st.session_state.question_order = list(range(total))
        random.shuffle(st.session_state.question_order)

    if 'history' not in st.session_state:
        # Pick first unanswered question
        unanswered = [i for i in st.session_state.question_order
                      if i not in st.session_state.answered_ids]
        if not unanswered:
            # All answered: reset on first load
            st.session_state.answered_ids = set()
            random.shuffle(st.session_state.question_order)
            unanswered = st.session_state.question_order.copy()
        first_idx = unanswered[0]
        st.session_state.history = [first_idx]
        st.session_state.history_pos = 0

    if 'submit_answer' not in st.session_state:
        st.session_state.submit_answer = False
    if 'has_submitted' not in st.session_state:
        st.session_state.has_submitted = False

    # ─── Determine unanswered questions ────────────────────────────
    unanswered_ids = [i for i in st.session_state.question_order
                      if i not in st.session_state.answered_ids]

    # ─── Handle completed session (all answered) ───────────────────
    if not unanswered_ids and len(st.session_state.answered_ids) > 0:
        st.success("🎉 You've answered all questions! Restarting practice session.")
        st.session_state.answered_ids = set()
        st.session_state.history = []
        st.session_state.history_pos = 0
        st.session_state.has_submitted = False
        random.shuffle(st.session_state.question_order)
        if os.path.exists("answered_questions.json"):
            os.remove("answered_questions.json")
        st.stop()

    # ─── Read current question from history ────────────────────────
    idx = st.session_state.history[st.session_state.history_pos]
    card = flashcards[idx]

    # ─── DISPLAY QUESTION & INDICATOR ──────────────────────────────
    # Show position = history_pos + 1, out of total flashcards
    question_number = st.session_state.history_pos + 1
    st.subheader(f"Question {question_number} of {total}")
    st.progress(question_number / total)
    st.write(card['question'])
    st.markdown(f"**{card.get('instruction', '')}**")

    # ─── CHECKBOXES ────────────────────────────────────────────────
    selected = []
    for key, val in card['options'].items():
        if st.session_state.get(f"practice_{idx}_{key}", False):
            selected.append(key)
        st.checkbox(f"{key}. {val}", key=f"practice_{idx}_{key}")

    # ─── SUBMIT LOGIC ──────────────────────────────────────────────
    if st.button("Submit Answer") and selected:
        st.session_state.submit_answer = True

    if st.session_state.submit_answer:
        st.session_state.submit_answer = False
        st.session_state.has_submitted = True

        correct = set(card['answers'])
        chosen = set(selected)

        if correct == chosen:
            st.success("✅ Correct!")
        elif correct & chosen:
            st.warning(f"🟡 Partially correct. Correct answer(s): {', '.join(correct)}")
        else:
            st.error(f"❌ Incorrect. Correct answer(s): {', '.join(correct)}")

        # ─── Track wrong answers ────────────────────────────────────
        wrong_counts = load_wrong_answers()
        if correct != chosen:
            wrong_counts[str(idx)] = wrong_counts.get(str(idx), 0) + 1
        save_wrong_answers(wrong_counts)

        # ─── Save answered state ────────────────────────────────────
        st.session_state.answered_ids.add(idx)
        save_answered_ids(st.session_state.answered_ids)

    # ─── NAVIGATION BUTTONS (no st.experimental_rerun) ──────────────
    col_prev, col_next = st.columns(2)

    with col_prev:
        if st.button("⬅️ Previous"):
            if st.session_state.history_pos > 0:
                st.session_state.history_pos -= 1
                st.session_state.has_submitted = False

    with col_next:
        if st.button("Next ➡️"):
            if st.session_state.has_submitted:
                # After submission, compute new unanswered and next index
                unanswered_ids = [i for i in st.session_state.question_order
                                  if i not in st.session_state.answered_ids]
                remaining = [i for i in unanswered_ids if i != idx]
                if remaining:
                    next_idx = remaining[0]
                    # Trim any “forward” history if user had gone back
                    st.session_state.history = st.session_state.history[:st.session_state.history_pos + 1]
                    # Append next question and advance pointer
                    st.session_state.history.append(next_idx)
                    st.session_state.history_pos += 1
                    st.session_state.has_submitted = False
            else:
                st.warning("⚠️ Please submit your answer before moving to the next question.")

    # ─── RESET PROGRESS BUTTON ────────────────────────────────────
    if st.button("🔁 Reset Practice Progress"):
        st.session_state.answered_ids = set()
        st.session_state.history = []
        st.session_state.history_pos = 0
        st.session_state.has_submitted = False
        if os.path.exists("answered_questions.json"):
            os.remove("answered_questions.json")
        st.success("✅ Practice progress has been reset.")
        st.stop()
