"""
policy.py
Move‑selection policies for the Solitaire Heuristic Evaluation Engine.

A Policy chooses a move from a list of legal moves. The MonteCarlo
engine delegates all decision‑making to the Policy, keeping the
simulation deterministic and modular.

This module defines:
- Policy: abstract interface
- RandomPolicy: baseline stochastic policy
- HeuristicPolicy: placeholder for scoring‑based strategies
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List
import random

from .state import State
from .simulator import Move


# ---------------------------------------------------------------------
# Base Policy Interface
# ---------------------------------------------------------------------

class Policy:
    """Abstract policy interface."""

    def choose(self, state: State, moves: List[Move]) -> Move:
        """
        Select a move from the list of legal moves.

        Subclasses must implement this method.
        """
        raise NotImplementedError("Policy.choose must be implemented.")


# ---------------------------------------------------------------------
# Random Policy (baseline)
# ---------------------------------------------------------------------

@dataclass
class RandomPolicy(Policy):
    """Randomly selects a legal move."""

    rng: random.Random = random.Random()

    def choose(self, state: State, moves: List[Move]) -> Move:
        return self.rng.choice(moves)


# ---------------------------------------------------------------------
# Heuristic Policy (placeholder)
# ---------------------------------------------------------------------

@dataclass
class HeuristicPolicy(Policy):
    """
    Placeholder heuristic policy.

    You can extend this with scoring functions such as:
    - prefer moves that reveal cards
    - prefer moves that build foundations
    - penalize cycling moves
    """

    def choose(self, state: State, moves: List[Move]) -> Move:
        # Simple fallback: choose the first move.
        # Replace with scoring logic later.
        return moves[0]
