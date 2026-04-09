"""
value.py
--------
Value function module for Klondike Solitaire.

This module provides:
- ValueFunction (abstract base)
- HeuristicValueFunction (feature-based evaluator)
- DEFAULT_WEIGHTS (normalized, configurable)
- Feature extraction helpers

The value function estimates how "good" a state is on a normalized
scale [0, 1], where 1.0 is a winning state and 0.0 is a deadlocked
or hopeless state.

This is the classical, authored version of a value network.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from src.engine.state import State
from src.engine.simulator import Simulator


# ---------------------------------------------------------------------
# Base Value Function
# ---------------------------------------------------------------------

class ValueFunction:
    """Abstract state evaluator."""

    def evaluate(self, state: State) -> float:
        raise NotImplementedError


# ---------------------------------------------------------------------
# Default normalized weights (sum ≈ 1.0)
# ---------------------------------------------------------------------

DEFAULT_WEIGHTS: Dict[str, float] = {
    "foundation_progress": 0.25,
    "flipped_cards": 0.15,
    "mobility": 0.20,
    "empty_tableau": 0.10,
    "sequence_quality": 0.10,
    "face_down_penalty": 0.10,
    "waste_penalty": 0.05,
    "deadlock_penalty": 0.05,
}


# ---------------------------------------------------------------------
# Heuristic Value Function
# ---------------------------------------------------------------------

@dataclass
class HeuristicValueFunction(ValueFunction):
    """
    Feature-based heuristic evaluator with configurable normalized weights.

    Produces a score in [0, 1] representing the estimated probability
    of eventually winning from the given state.
    """

    weights: Dict[str, float]
    simulator: Simulator = Simulator()

    def evaluate(self, state: State) -> float:
        # Terminal states override everything
        if state.is_win():
            return 1.0

        moves = self.simulator.legal_moves(state)
        if not moves:
            return 0.0

        # Extract features
        f = self._extract_features(state, moves)

        # Weighted sum
        score = 0.0
        for name, value in f.items():
            w = self.weights.get(name, 0.0)
            score += w * value

        # Clamp to [0, 1]
        return max(0.0, min(1.0, score))

    # -----------------------------------------------------------------
    # Feature extraction
    # -----------------------------------------------------------------

    def _extract_features(self, state: State, moves) -> Dict[str, float]:
        total_cards = 52

        # Foundation progress (0–1)
        foundation_cards = sum(len(pile) for pile in state.foundations.values())
        foundation_progress = foundation_cards / total_cards

        # Flipped cards (face-up tableau cards)
        face_up = sum(
            1 for pile in state.tableau for c in pile if c.face_up
        )
        flipped_cards = face_up / total_cards

        # Mobility (normalized legal move count)
        mobility = min(1.0, len(moves) / 20)

        # Empty tableau piles (0–1)
        empty_tableau = sum(1 for pile in state.tableau if not pile) / 7

        # Sequence quality (longest descending alternating run)
        sequence_quality = self._sequence_quality(state)

        # Face-down penalty (0–1)
        face_down = sum(
            1 for pile in state.tableau for c in pile if not c.face_up
        )
        face_down_penalty = face_down / total_cards

        # Waste penalty (late-cycle waste is bad)
        waste_penalty = min(1.0, len(state.waste) / 24)

        # Deadlock penalty (no good moves)
        deadlock_penalty = 1.0 if not moves else 0.0

        return {
            "foundation_progress": foundation_progress,
            "flipped_cards": flipped_cards,
            "mobility": mobility,
            "empty_tableau": empty_tableau,
            "sequence_quality": sequence_quality,
            "face_down_penalty": face_down_penalty,
            "waste_penalty": waste_penalty,
            "deadlock_penalty": deadlock_penalty,
        }

    # -----------------------------------------------------------------
    # Sequence quality helper
    # -----------------------------------------------------------------

    def _sequence_quality(self, state: State) -> float:
        """
        Measures the quality of tableau sequences by finding the longest
        descending alternating-color run. Normalized to [0, 1].
        """
        best = 0

        for pile in state.tableau:
            run = 1
            for i in range(len(pile) - 1):
                a = pile[i]
                b = pile[i + 1]
                if (
                    a.face_up
                    and b.face_up
                    and a.rank == b.rank + 1
                    and a.color != b.color
                ):
                    run += 1
                else:
                    break
            best = max(best, run)

        # Normalize: max useful run length is ~13
        return min(1.0, best / 13)
