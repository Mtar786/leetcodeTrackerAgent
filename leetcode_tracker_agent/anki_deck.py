"""Helpers for interacting with Anki via AnkiConnect.

AnkiConnect is a plugin for the Anki desktop app that exposes a simple
HTTP API on port 8765. It allows external tools to create decks, add
notes, and perform other operations. This module wraps a few common
AnkiConnect actions for the LeetCode Tracker Agent.

See https://ankiweb.net/shared/info/2055492159 for installation
instructions for AnkiConnect.
"""

from __future__ import annotations

import json
from typing import List, Optional

import requests


ANKI_CONNECT_URL = "http://localhost:8765"


def _invoke(action: str, **params) -> dict:
    """Invoke an AnkiConnect action.

    Raises a RuntimeError if the call fails or returns an error.
    """
    payload = {
        "action": action,
        "version": 6,
        "params": params or {},
    }
    try:
        resp = requests.post(ANKI_CONNECT_URL, json=payload, timeout=10)
        resp.raise_for_status()
        result = resp.json()
    except Exception as exc:
        raise RuntimeError(f"Failed to call AnkiConnect: {exc}") from exc
    if result.get("error"):
        raise RuntimeError(f"AnkiConnect error: {result['error']}")
    return result.get("result")


def ensure_deck_exists(deck_name: str) -> None:
    """Create a deck if it does not already exist.

    Parameters
    ----------
    deck_name: str
        Name of the deck to create or ensure exists.
    """
    try:
        _invoke("createDeck", deck=deck_name)
    except RuntimeError as exc:
        # If deck already exists, AnkiConnect returns an error; ignore it
        if "deck already exists" not in str(exc).lower():
            raise


def add_note_to_anki(
    deck_name: str,
    model_name: str,
    front: str,
    back: str,
    *,
    tags: Optional[List[str]] = None,
) -> int:
    """Add a flashcard to an Anki deck.

    Parameters
    ----------
    deck_name: str
        Name of the target deck.
    model_name: str
        Name of the note model, e.g. "Basic".
    front: str
        Front (question) text of the flashcard.
    back: str
        Back (answer) text of the flashcard.
    tags: Optional[List[str]]
        Optional list of tags to apply to the note.

    Returns
    -------
    int
        The identifier of the newly created note.

    Raises
    ------
    RuntimeError
        If the note could not be added.
    """
    note = {
        "deckName": deck_name,
        "modelName": model_name,
        "fields": {
            "Front": front,
            "Back": back,
        },
        "options": {
            "allowDuplicate": False,
        },
        "tags": tags or [],
    }
    return _invoke("addNote", note=note)