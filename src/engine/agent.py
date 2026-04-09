"""
agent.py
--------
Agent layer for Klondike Solitaire.

Agents wrap policies or MCTS engines and can play full games.
This is the layer used for evaluation, benchmarking, and solve-rate
experiments.

Included:
- BaseAgent
- PolicyAgent
- MCTSAgent
- HybridAgent (policy + MCTS)
- GameResult dataclass
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from src.engine.state import State, Move
from src.engine.simulator import Simulator
from src.engine.policy import Policy
from src.engine.mcts import MCTS


# ---------------------------------------------------------------------
# Game Result
# ---------------------------------------------------------------------

@dataclass
class GameResult:
    win: bool
    moves: int
    reward: float
    terminal_state: State


# ---------------------------------------------------------------------
# Base Agent
# ---------------------------------------------------------------------

class BaseAgent:
    """Abstract agent that can play a full game."""

    def choose_move(self, state: State, moves: list[Move]) -> Optional[Move]:
        raise NotImplementedError

    def play_game(self, simulator: Simulator | None = None) -> GameResult:
        sim = simulator or Simulator()
        state = State.new_game()
        moves_taken = 0

        while not sim.is_terminal(state):
            moves = sim.legal_moves(state)
            if not moves:
                break

            move = self.choose_move(state, moves)
            if move is None:
                break

            state = sim.next_state(state, move)
            moves_taken += 1

        reward = sim.reward(state)
        return GameResult(
            win=state.is_win(),
            moves=moves_taken,
            reward=reward,
            terminal_state=state,
        )


# ---------------------------------------------------------------------
# Policy Agent
# ---------------------------------------------------------------------

class PolicyAgent(BaseAgent):
    """Agent that uses a Policy to choose moves."""

    def __init__(self, policy: Policy):
        self.policy = policy

    def choose_move(self, state: State, moves: list[Move]) -> Optional[Move]:
        return self.policy.choose_move(state, moves)


# ---------------------------------------------------------------------
# MCTS Agent
# ---------------------------------------------------------------------

class MCTSAgent(BaseAgent):
    """Agent that uses MCTS to choose moves."""

    def __init__(self, mcts: MCTS):
        self.mcts = mcts

    def choose_move(self, state: State, moves: list[Move]) -> Optional[Move]:
        return self.mcts.choose(state)


# ---------------------------------------------------------------------
# Hybrid Agent (Policy-guided MCTS)
# ---------------------------------------------------------------------

class HybridAgent(BaseAgent):
    """
    Agent that uses a policy to guide MCTS rollouts or priors.
    This is the AlphaZero-style architecture.

    For now, it simply delegates to MCTS, but the structure is here
    for future expansion.
    """

    def __init__(self, mcts: MCTS, policy: Policy):
        self.mcts = mcts
        self.policy = policy

    def choose_move(self, state: State, moves: list[Move]) -> Optional[Move]:
        return self.mcts.choose(state)
