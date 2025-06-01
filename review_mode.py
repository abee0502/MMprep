import streamlit as st
from flashcards import load_wrong_answers, save_wrong_answers
import random
import os

def run_review_mode(flashcards, review_only=True):
    wrong_counts = load_wrong_answers()
    if not wrong_counts:
        st.success("🎉 No mistakes to review! You've mastered all questions.")
        return

    sorted_wrongs = sorted(wrong_counts.items(), key=lambda x: -x[1])  # Sort by most missed
    st.subheader("❌ Mistake Review Mode" if review_only else "🎯 Wrong Answer Practice Mode")

    # ✅ Add reset button in practice mode
    if not review_only:
        if st.button("❌ Reset All Mistake Records"):
            if os.path.exists("wrong_answers.json"):
                os.remove("wrong_answers.json")
                st.success("✅ Mistake records cleared!")
                st.experimental_rerun()
            else:
                st.info("ℹ️ No mistake records to reset.")

    if review_only:
        # Review mode: read-only view
        for qid, count in sorted_wrongs:
            idx = int(qid)
            card = flashcards[idx]
            with st.expander(f"❌ Missed {count}x — {card['question']}"):
                st.markdown(f"**{card.get('instruction', '')}**")
                for key, val in card["options"].items():
                    st.markdown(f"{key}. {val}")
                st.markdown(f"**Correct Answer(s):** {', '.join(card['answers'])}")
    else:
        # Practice mode: active answering
        if "wrong_practice_index" not in st.session_state:
            st.session_state.wrong_practice_index = 0
            wrong_indices = [int(i) for i in wrong_counts.keys()]
            random.shuffle(wrong_indices)
            st.session_state.wrong_indices = wrong_indices

        total = len(st.session_state.wrong_indices)
        idx_pos = st.session_state.wrong_practice_index

        if idx_pos >= total:
            st.success("✅ You've practiced all your mistakes!")
            st.session_state.wrong_practice_index = 0
            return

        idx = st.session_state.wrong_indices[idx_pos]
        card = flashcards[idx]

        st.subheader(f"Practice Mistake {idx_pos + 1} of {total}")
        st.write(card['question'])
        st.markdown(f"**{card.get('instruction', '')}**")

        selected = []
        for key, val in card["options"].items():
            if st.checkbox(f"{key}. {val}", key=f"review_practice_{key}_{idx}"):
                selected.append(key)

        if st.button("Submit Answer"):
            correct = set(card["answers"])
            chosen = set(selected)
            if correct == chosen:
                st.success("✅ Correct!")
            elif correct & chosen:
                st.warning(f"🟡 Partially correct. Correct answer(s): {', '.join(correct)}")
            else:
                st.error(f"❌ Incorrect. Correct answer(s): {', '.join(correct)}")

            # Re-track mistakes
            if correct != chosen:
                wrong_counts[str(idx)] = wrong_counts.get(str(idx), 0) + 1
                save_wrong_answers(wrong_counts)

        if st.button("Next Mistake"):
            st.session_state.wrong_practice_index += 1
