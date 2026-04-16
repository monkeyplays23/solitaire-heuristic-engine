from __future__ import annotations

from src.engine.state import State, Move
from src.engine.simulator import Simulator
from src.engine.value import HeuristicValueFunction


class GreedyHeuristicAgent:
    def __init__(self, simulator: Simulator | None = None):
        self.sim = simulator or Simulator()
        self.value_fn = HeuristicValueFunction()

    def choose_move(self, state: State, moves: list[Move]) -> Move | None:
        if not moves:
            return None

        best_move = None
        best_score = -1.0

        for m in moves:
            next_state = self.sim.next_state(state, m)
            score = self.value_fn.evaluate(next_state)
            if score > best_score:
                best_score = score
                best_move = m

        return best_move
