"""
policy.py
---------
Policy module for Klondike Solitaire.

A Policy chooses a move from a list of legal moves.
This is the strategic layer of the engine: different policies
encode different heuristics or decision styles.

Included:
- Policy (abstract base)
- RandomPolicy
- GreedyPolicy (simple rule ordering)
- HeuristicPolicy (scored evaluation)
- PolicyFactory (string → policy)
"""

from __future__ import annotations

from dataclasses import dataclass
import random

from src.engine.state import State, Move
from src.engine.simulator import Simulator


# ---------------------------------------------------------------------
# Base Policy
# ---------------------------------------------------------------------

class Policy:
    """Abstract move-selection policy."""

    def choose(self, state: State, moves: list[Move]) -> Move:
        raise NotImplementedError

    def choose_move(self, state: State, moves: list[Move]):
        if not moves:
            return None
        return self.choose(state, moves)


# ---------------------------------------------------------------------
# Random Policy
# ---------------------------------------------------------------------

@dataclass
class RandomPolicy(Policy):
    rng: random.Random = random.Random()

    def choose(self, state: State, moves: list[Move]) -> Move:
        return self.rng.choice(moves)


# ---------------------------------------------------------------------
# Greedy Policy (simple rule ordering)
# ---------------------------------------------------------------------

@dataclass
class GreedyPolicy(Policy):
    """
    A simple rule-based policy:
    1. Prefer foundation moves
    2. Prefer moves that flip a face-down card
    3. Prefer tableau-to-tableau moves
    4. Otherwise choose randomly
    """

    rng: random.Random = random.Random()
    sim: Simulator = Simulator()

    def choose(self, state: State, moves: list[Move]) -> Move:
        # 1. Foundation moves
        foundation_moves = [
            m for m in moves
            if m.kind in ("waste_to_foundation", "tableau_to_foundation")
        ]
        if foundation_moves:
            return foundation_moves[0]

        # 2. Moves that flip a card
        flip_moves = []
        for m in moves:
            if m.kind == "tableau_to_tableau":
                src, idx = m.src
                pile = state.tableau[src]
                if idx > 0 and not pile[idx - 1].face_up:
                    flip_moves.append(m)
        if flip_moves:
            return flip_moves[0]

        # 3. Tableau moves
        tableau_moves = [
            m for m in moves if m.kind == "tableau_to_tableau"
        ]
        if tableau_moves:
            return tableau_moves[0]

        # 4. Fallback random
        return self.rng.choice(moves)


# ---------------------------------------------------------------------
# Heuristic Policy (scored evaluation)
# ---------------------------------------------------------------------

@dataclass
class HeuristicPolicy(Policy):
    """
    Assigns a score to each move and picks the highest-scoring one.

    Heuristics:
    +10 foundation move
    +8  flipping a face-down card
    +5  king to empty tableau
    +2  building tableau stack
    -3  recycling waste
    """

    rng: random.Random = random.Random()
    sim: Simulator = Simulator()

    def choose(self, state: State, moves: list[Move]) -> Move:
        scored = [(self._score_move(state, m), m) for m in moves]
        scored.sort(key=lambda x: x[0], reverse=True)
        best_score = scored[0][0]

        # If multiple moves tie, choose randomly among them
        best_moves = [m for s, m in scored if s == best_score]
        return self.rng.choice(best_moves)

    # -------------------------------------------------------------
    # Heuristic scoring
    # -------------------------------------------------------------

    def _score_move(self, state: State, move: Move) -> int:
        score = 0

        # Foundation moves
        if move.kind in ("waste_to_foundation", "tableau_to_foundation"):
            score += 10

        # Moves that flip a face-down card
        if move.kind == "tableau_to_tableau":
            src, idx = move.src
            pile = state.tableau[src]
            if idx > 0 and not pile[idx - 1].face_up:
                score += 8

        # King to empty tableau
        if move.kind in ("waste_to_tableau", "tableau_to_tableau"):
            dst_pile, _ = move.dst
            if not state.tableau[dst_pile]:
                # Check if the moved card is a King
                if move.kind == "waste_to_tableau":
                    card = state.waste[-1]
                else:
                    src, idx = move.src
                    card = state.tableau[src][idx]
                if card.rank == 13:
                    score += 5

        # Building tableau stacks
        if move.kind == "tableau_to_tableau":
            score += 2

        # Penalize recycling
        if move.kind == "recycle_waste":
            score -= 3

        return score


# ---------------------------------------------------------------------
# Policy Factory
# ---------------------------------------------------------------------

class PolicyFactory:
    """Create policies by name."""

    @staticmethod
    def create(name: str) -> Policy:
        name = name.lower()

        if name == "random":
            return RandomPolicy()

        if name == "greedy":
            return GreedyPolicy()

        if name == "heuristic":
            return HeuristicPolicy()

        raise ValueError(f"Unknown policy: {name}")
