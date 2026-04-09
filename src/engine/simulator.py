"""
simulator.py
------------
Pure mechanical simulator for Klondike Solitaire.

This module wraps the State class and exposes a clean interface for
rollouts, MCTS, and heuristic evaluation. It contains no heuristics.
"""

from __future__ import annotations

from dataclasses import dataclass
from src.engine.state import State, Move


@dataclass(frozen=True)
class Transition:
    state: State
    move: Move | None
    reward: float
    terminal: bool


class Simulator:
    """
    A pure state-transition sandbox for Klondike Solitaire.

    Provides:
      - initial_state(seed)
      - legal_moves(state)
      - next_state(state, move)
      - is_terminal(state)
      - reward(state)
    """

    # -------------------------------------------------------------
    # Initialization
    # -------------------------------------------------------------

    def initial_state(self, seed=None) -> State:
        return State.new_game(seed)

    # -------------------------------------------------------------
    # Move enumeration
    # -------------------------------------------------------------

    def legal_moves(self, state: State) -> list[Move]:
        return state.legal_moves()

    # -------------------------------------------------------------
    # State transition
    # -------------------------------------------------------------

    def next_state(self, state: State, move: Move) -> State:
        return state.apply_move(move)

    # -------------------------------------------------------------
    # Terminal detection
    # -------------------------------------------------------------

    def is_terminal(self, state: State) -> bool:
        return state.is_win() or state.is_loss()

    # -------------------------------------------------------------
    # Reward function (for RL/MCTS)
    # -------------------------------------------------------------

    def reward(self, state: State) -> float:
        """
        Purely mechanical reward:
          +1 for win
           0 otherwise

        You can replace this later with:
          - foundation count
          - heuristic score
          - shaped reward
        """
        return 1.0 if state.is_win() else 0.0

    # -------------------------------------------------------------
    # One-step transition wrapper
    # -------------------------------------------------------------

    def step(self, state: State, move: Move) -> Transition:
        next_s = state.apply_move(move)
        return Transition(
            state=next_s,
            move=move,
            reward=self.reward(next_s),
            terminal=self.is_terminal(next_s),
        )

    # ---------------------------------------------------------------------
    # Compatibility wrapper for older tests
    # ---------------------------------------------------------------------

    def apply(self, state: State, move: Move | None) -> State:
        if move is None:
            return state
        return self.next_state(state, move)
