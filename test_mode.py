import streamlit as st
from flashcards import load_wrong_answers, save_wrong_answers
import random

def run_test_mode(flashcards):
    test_sample = random.sample(flashcards, min(100, len(flashcards)))
    st.subheader("🧪 Test Mode: Answer all questions, then submit")
    answers = {}

    for i, card in enumerate(test_sample):
        with st.expander(f"Q{i+1}: {card['question']}"):
            st.markdown(f"**{card.get('instruction', '')}**")
            for key, val in card["options"].items():
                if st.checkbox(f"{key}. {val}", key=f"test_{i}_{key}"):
                    answers.setdefault(i, []).append(key)

    if st.button("Submit Test"):
        score = 0
        wrong_counts = load_wrong_answers()

        for i, card in enumerate(test_sample):
            correct = set(card["answers"])
            chosen = set(answers.get(i, []))
            if correct == chosen:
                score += 1
            else:
                qid = str(flashcards.index(card))  # Global index for tracking
                wrong_counts[qid] = wrong_counts.get(qid, 0) + 1

        save_wrong_answers(wrong_counts)
        st.success(f"✅ Final Score: {score} / {len(test_sample)}")
        st.info("❌ Mistakes have been saved for review.")