import streamlit as st

def run_full_review_mode(flashcards):
    st.subheader("📖 Full Review of All Questions with Answers")

    for i, card in enumerate(flashcards):
        with st.expander(f"Question {i+1}: {card['question']}"):
            st.markdown(f"**{card.get('instruction', '')}**")
            for key, val in card['options'].items():
                st.markdown(f"{key}. {val}")
            correct = set(card['answers'])
            st.markdown(f"**✅ Correct Answer(s):** {', '.join(correct)}")
