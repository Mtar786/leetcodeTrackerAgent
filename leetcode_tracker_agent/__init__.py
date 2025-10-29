"""Top‑level package for the LeetCode Tracker Agent.

This agent tracks your progress on LeetCode, generates concise summaries of
solved problems using a large language model, and updates both a Google Doc
and an Anki deck. The main functionality is exposed through the
``cli`` module for command‑line usage as well as helper modules for
interacting with external services.
"""

from .leetcode_api import get_recent_solved_problems, get_problem_details
from .summary import summarize_problem
from .google_docs import append_to_doc
from .anki_deck import add_note_to_anki, ensure_deck_exists

__all__ = [
    "get_recent_solved_problems",
    "get_problem_details",
    "summarize_problem",
    "append_to_doc",
    "add_note_to_anki",
    "ensure_deck_exists",
]