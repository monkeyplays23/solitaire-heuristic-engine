"""
simulator.py
Deterministic world model for Klondike Solitaire.

This minimal version provides the interface required by MonteCarlo:
- legal_moves(state)
- apply(state, move)

Real move logic will be implemented later.
"""

from __future__ import annotations

from dataclasses import dataclass

from .state import State, Move


@dataclass
class Simulator:
    """Deterministic Solitaire transition model."""

    def legal_moves(self, state: State) -> list[Move]:
        """
        Return a list of legal moves.

        Placeholder: returns an empty list so the engine runs.
        """
        return []

    def apply(self, state: State, move: Move) -> State:
        """
        Apply a move and return the resulting state.

        Placeholder: returns the state unchanged.
        """
        return state
