import json
import os

# File paths
QUESTION_FILE = "questions.json"
WRONG_ANSWER_FILE = "wrong_answers.json"

def load_flashcards():
    """Load the list of flashcards (questions) from the JSON file."""
    with open(QUESTION_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_wrong_answers():
    """Load the dictionary of wrong answer counts."""
    if os.path.exists(WRONG_ANSWER_FILE):
        with open(WRONG_ANSWER_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_wrong_answers(wrong_counts):
    """Save the dictionary of wrong answer counts to file."""
    with open(WRONG_ANSWER_FILE, 'w', encoding='utf-8') as f:
        json.dump(wrong_counts, f)
