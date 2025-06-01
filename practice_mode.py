import streamlit as st
from flashcards import load_wrong_answers, save_wrong_answers
import random
from flashcards import (
    load_wrong_answers, save_wrong_answers,
    load_answered_ids, save_answered_ids
)


def run_practice_mode(flashcards):
    total = len(flashcards)

    # Handle empty question set
    if total == 0:
        st.error("⚠️ No flashcards found. Please check your questions.json.")
        st.stop()

    # Session state initialization
    
    #if 'answered_ids' not in st.session_state:
    #    st.session_state.answered_ids = set()
    if 'answered_ids' not in st.session_state:
        st.session_state.answered_ids = load_answered_ids()
    if 'practice_index' not in st.session_state:
        st.session_state.practice_index = 0
    if 'question_order' not in st.session_state:
        st.session_state.question_order = list(range(total))
        random.shuffle(st.session_state.question_order)

    # Filter unanswered
    unanswered_ids = [i for i in st.session_state.question_order if i not in st.session_state.answered_ids]

    # 🛡 Handle completed session — only if at least one question answered
    if not unanswered_ids and len(st.session_state.answered_ids) > 0:
        st.success("🎉 You've answered all questions! Restarting practice session.")
        st.session_state.answered_ids = set()
        random.shuffle(st.session_state.question_order)
        st.session_state.practice_index = 0
        st.stop()

    # Safe current index
    idx = unanswered_ids[st.session_state.practice_index % len(unanswered_ids)]
    card = flashcards[idx]

    # UI
    #$$
    st.session_state.answered_ids.add(idx)
    save_answered_ids(st.session_state.answered_ids)  # <-- Save to file#$$
    
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

        # Mark question as answered
        st.session_state.answered_ids.add(idx)

    # Navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Previous"):
            st.session_state.practice_index = max(0, st.session_state.practice_index - 1)
    with col2:
        if st.button("Next ➡️"):
            st.session_state.practice_index += 1
        
    # Optional: Reset answered questions
    if st.button("🔁 Reset Practice Progress"):
        st.session_state.answered_ids = set()
        st.session_state.practice_index = 0
        if os.path.exists("answered_questions.json"):
            os.remove("answered_questions.json")
        st.success("✅ Practice progress has been reset.")
        st.stop()
