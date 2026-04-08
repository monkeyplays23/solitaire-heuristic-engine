"""
variants.py
Alternative heuristic scoring variants for experimentation.

These functions provide different scoring philosophies that can be
plugged into HeuristicPolicy or used for A/B testing.
"""

from __future__ import annotations

from .baseline import baseline_score


def aggressive_score(state, move, simulator):
    """
    Aggressive variant:
    - strongly favors revealing cards
    - strongly favors foundation moves
    - lightly penalizes cycling
    """
    score = baseline_score(state, move, simulator)
    score *= 1.5
    return score


def conservative_score(state, move, simulator):
    """
    Conservative variant:
    - prefers safe, incremental moves
    - avoids deep tableau stack moves
    """
    score = baseline_score(state, move, simulator)
    score *= 0.8
    return score
