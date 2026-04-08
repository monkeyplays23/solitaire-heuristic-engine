"""
montecarlo.py
Monte Carlo experiment harness for the Solitaire Heuristic Evaluation Engine.

This module coordinates:
- State sampling
- Deduplicated exploration
- Heuristic policy evaluation
- Rollout execution
- Statistical reporting

It is intentionally generic: the Policy and Simulator determine behavior,
while MonteCarlo orchestrates the experiment.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict

from .state import State
from .simulator import Simulator
from .hashing import StateHasher


# ------------------------------------------------------------
# Monte Carlo Result Structure
# ------------------------------------------------------------

@dataclass
class MCStats:
    """Tracks aggregate statistics across rollouts."""
    rollouts: int = 0
    terminal_wins: int = 0
    terminal_losses: int = 0
    visited_states: int = 0
    unique_states: int = 0

    def as_dict(self) -> Dict:
        return {
            "rollouts": self.rollouts,
            "terminal_wins": self.terminal_wins,
            "terminal_losses": self.terminal_losses,
            "visited_states": self.visited_states,
            "unique_states": self.unique_states,
        }


# ------------------------------------------------------------
# Monte Carlo Engine
# ------------------------------------------------------------

@dataclass
class MonteCarlo:
    """
    Monte Carlo experiment harness.

    Parameters:
    - simulator: deterministic world model
    - policy: heuristic move selector
    - hasher: canonical state identity
    - max_depth: maximum rollout depth
    - deduplicate: whether to avoid revisiting identical states
    """

    simulator: Simulator = field(default_factory=Simulator)
    policy: object = None
    hasher: StateHasher = field(default_factory=StateHasher)
    max_depth: int = 200
    deduplicate: bool = True
    rollouts: int = 100

    # Internal state
    visited: Dict[str, int] = field(default_factory=dict)

    # --------------------------------------------------------
    # Public API
    # --------------------------------------------------------

    def run(self, initial_state: State, rollouts: int = None) -> MCStats:
        """
        Run N Monte Carlo rollouts from the given initial state.
        """
        stats = MCStats()
        n = rollouts if rollouts is not None else self.rollouts

        for _ in range(n):
            stats.rollouts += 1
            result = self._rollout(initial_state)

            if result == "WIN":
                stats.terminal_wins += 1
            elif result == "LOSS":
                stats.terminal_losses += 1

        stats.visited_states = sum(self.visited.values())
        stats.unique_states = len(self.visited)

        return stats.as_dict()

    # --------------------------------------------------------
    # Rollout Logic
    # --------------------------------------------------------

    def _rollout(self, root: State) -> str:
        """
        Perform a single rollout from the root state.
        Returns:
            "WIN" or "LOSS"
        """
        state = root.copy()

        for _ in range(self.max_depth):

            # Deduplication
            if self.deduplicate:
                h = self.hasher.hash(state)
                self.visited[h] = self.visited.get(h, 0) + 1

            # Terminal check
            if state.is_win():
                return "WIN"
            if state.is_loss():
                return "LOSS"

            # Enumerate legal moves
            moves = self.simulator.legal_moves(state)
            if not moves:
                return "LOSS"

            # Policy chooses a move
            move = self.policy.choose(state, moves)

            # Apply move
            state = self.simulator.apply(state, move)

        # If we hit max depth without terminal resolution, treat as loss
        return "LOSS"
