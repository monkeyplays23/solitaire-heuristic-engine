"""
montecarlo.py
-------------
Simple Monte Carlo rollout evaluator for Klondike Solitaire.

Runs N random playouts from a given state using the Simulator.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import random

from src.engine.simulator import Simulator
from src.engine.state import State, Move


@dataclass
class MCStats:
    rollouts: int = 0
    terminal_wins: int = 0
    terminal_losses: int = 0
    total_reward: float = 0.0

    def as_dict(self) -> dict:
        return {
            "rollouts": self.rollouts,
            "terminal_wins": self.terminal_wins,
            "terminal_losses": self.terminal_losses,
            "total_reward": self.total_reward,
            "visited_states": 0,
            "unique_states": 0,
        }


@dataclass
class MonteCarlo:
    rollouts: int = 100
    simulator: Simulator = field(default_factory=Simulator)
    rng: random.Random = field(default_factory=random.Random)

    # -------------------------------------------------------------
    # Run N Monte Carlo rollouts
    # -------------------------------------------------------------

    def run(self, state: State) -> dict:
        stats = MCStats()

        for _ in range(self.rollouts):
            reward, terminal = self._rollout(state)
            stats.rollouts += 1
            stats.total_reward += reward

            if terminal and reward > 0:
                stats.terminal_wins += 1
            elif terminal:
                stats.terminal_losses += 1

        return stats.as_dict()

    # -------------------------------------------------------------
    # One random playout
    # -------------------------------------------------------------

    def _rollout(self, state: State) -> tuple[float, bool]:
        sim = self.simulator
        s = state.copy()

        for _ in range(500):  # max rollout depth
            if sim.is_terminal(s):
                return sim.reward(s), True

            moves = sim.legal_moves(s)
            if not moves:
                return 0.0, True

            move = self.rng.choice(moves)
            s = sim.next_state(s, move)

        # If we hit max depth, treat as non-terminal loss
        return 0.0, True
