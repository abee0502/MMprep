import streamlit as st
from flashcards import load_wrong_answers, save_wrong_answers
import random

def run_bundle_mode(flashcards):
    # Bundle size selector (default: 5)
    bundle_size = st.sidebar.slider("Select number of questions", 3, 20, 5)
    bundle_sample = random.sample(flashcards, min(bundle_size, len(flashcards)))
    st.subheader(f"🔁 Bundle Practice: {bundle_size} Random Questions")

    answers = {}

    for i, card in enumerate(bundle_sample):
        st.markdown(f"### Question {i + 1} of {bundle_size}")
        st.progress((i + 1) / bundle_size)
        st.write(card['question'])
        st.markdown(f"**{card.get('instruction', '')}**")

        for key, val in card['options'].items():
            if st.checkbox(f"{key}. {val}", key=f"bundle_{i}_{key}"):
                answers.setdefault(i, []).append(key)

    if st.button("Submit Bundle"):
        score = 0
        wrong_counts = load_wrong_answers()

        for i, card in enumerate(bundle_sample):
            correct = set(card["answers"])
            chosen = set(answers.get(i, []))
            if correct == chosen:
                score += 1
            else:
                qid = str(flashcards.index(card))
                wrong_counts[qid] = wrong_counts.get(qid, 0) + 1

        save_wrong_answers(wrong_counts)
        st.success(f"✅ Bundle Score: {score} / {bundle_size}")
