"""
baseline.py
Baseline heuristic scoring for the Solitaire Heuristic Evaluation Engine.

These scoring functions evaluate a (state, move) pair and return a numeric
score. Higher scores indicate more desirable moves.

This baseline model favors:
- revealing hidden cards
- building foundations
- moving cards off the waste
"""

from __future__ import annotations

from .utils import score_reveal, score_foundation, score_waste


def baseline_score(state, move, simulator):
    """
    Compute a baseline heuristic score for a move.

    Parameters:
    - state: current State
    - move: Move being evaluated
    - simulator: Simulator used to preview the result

    Returns:
        numeric score (higher is better)
    """
    score = 0

    # Reward revealing a face‑down card
    score += score_reveal(state, move)

    # Reward building foundations
    score += score_foundation(state, move)

    # Reward clearing waste
    score += score_waste(state, move)

    return score
