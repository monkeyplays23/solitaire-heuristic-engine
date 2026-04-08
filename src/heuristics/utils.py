"""
utils.py
Helper scoring functions for the Solitaire Heuristic Evaluation Engine.

These functions compute small, composable heuristic contributions for
(state, move) pairs. They are used by baseline and variant scoring
models.
"""

from __future__ import annotations


def score_reveal(state, move):
    """
    Reward moves that reveal a face‑down tableau card.

    Returns:
        positive score if the move exposes a hidden card,
        otherwise 0.
    """
    if move.type.startswith("TABLEAU_TO_"):
        pile = state.tableau[move.src]
        if len(pile) >= 2 and not pile[-2].face_up:
            return 5
    return 0


def score_foundation(state, move):
    """
    Reward moves that build foundations.

    Returns:
        positive score for foundation moves,
        otherwise 0.
    """
    if move.type in ("WASTE_TO_FOUNDATION", "TABLEAU_TO_FOUNDATION"):
        return 10
    return 0


def score_waste(state, move):
    """
    Reward clearing cards from the waste.

    Returns:
        small positive score for waste moves,
        otherwise 0.
    """
    if move.type.startswith("WASTE_TO_"):
        return 2
    return 0
