"""
mcts_alpha.py
-------------
AlphaZero-style MCTS for Klondike Solitaire.

This module provides:
- PriorPolicy (abstract + default heuristic prior)
- AlphaNode (tree node with priors + value stats)
- AlphaMCTS (PUCT-based search)
- AlphaMCTSAgent (agent wrapper)

This version uses:
- policy priors instead of uniform exploration
- value function bootstrap instead of rollouts
- PUCT formula for balanced exploration/exploitation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from src.engine.state import State, Move
from src.engine.simulator import Simulator
from src.engine.value import ValueFunction
from src.engine.policy import Policy
import time


# ---------------------------------------------------------------------
# Prior Policy
# ---------------------------------------------------------------------

class PriorPolicy:
    """
    Abstract prior policy.

    Produces a probability distribution over legal moves.
    """

    def priors(self, state: State, moves: list[Move]) -> Dict[Move, float]:
        raise NotImplementedError


class HeuristicPriorPolicy(PriorPolicy):
    def __init__(self, policy: Policy):
        self.policy = policy

    def priors(self, state: State, moves: list[Move]) -> Dict[Move, float]:
        if not moves:
            return {}

        scores = []
        for move in moves:
            scores.append(1.0)

        total = sum(scores)
        return {m: s / total for m, s in zip(moves, scores)}


# ---------------------------------------------------------------------
# AlphaZero-style MCTS Node
# ---------------------------------------------------------------------

@dataclass
class AlphaNode:
    state: State
    prior: float
    parent: Optional[AlphaNode] = None
    children: Dict[Move, AlphaNode] = field(default_factory=dict)
    visits: int = 0
    value_sum: float = 0.0

    @property
    def value(self) -> float:
        if self.visits == 0:
            return 0.0
        return self.value_sum / self.visits

    def expand(self, moves: list[Move], priors: Dict[Move, float], simulator: Simulator):
        for move in moves:
            next_state = simulator.next_state(self.state, move)
            self.children[move] = AlphaNode(
                state=next_state,
                prior=priors.get(move, 0.0),
                parent=self,
            )


# ---------------------------------------------------------------------
# AlphaZero-style MCTS
# ---------------------------------------------------------------------

class AlphaMCTS:
    def __init__(
        self,
        prior_policy: PriorPolicy,
        value_fn: ValueFunction,
        simulator: Simulator | None = None,
        c_puct: float = 1.4,
        iterations: int = 50,  # was 200
    ):
        self.prior_policy = prior_policy
        self.value_fn = value_fn
        self.simulator = simulator or Simulator()
        self.c_puct = c_puct
        self.iterations = iterations
        self.root: Optional[AlphaNode] = None

    # -------------------------------------------------------------
    # PUCT selection
    # -------------------------------------------------------------

    def _select_child(self, node: AlphaNode) -> tuple[Move, AlphaNode]:
        best_score = -1e9
        best_move = None
        best_child = None

        parent_visits = max(1, node.visits)

        for move, child in node.children.items():
            q = child.value
            u = (
                self.c_puct
                * child.prior
                * (parent_visits ** 0.5)
                / (1 + child.visits)
            )
            score = q + u

            if score > best_score:
                best_score = score
                best_move = move
                best_child = child

        return best_move, best_child

    # -------------------------------------------------------------
    # Main search loop
    # -------------------------------------------------------------

    def choose(self, state: State) -> Optional[Move]:
        moves = self.simulator.legal_moves(state)
        if not moves:
            return None

        self.root = AlphaNode(state=state, prior=1.0)

        priors = self.prior_policy.priors(state, moves)
        self.root.expand(moves, priors, self.simulator)

        start = time.time()
        for i in range(self.iterations):
            if time.time() - start > 1.0:  # 1 second cap per decision
                # print(f"MCTS early stop at {i} iterations")  # optional
                break
            self._simulate(self.root)

        best_move = max(
            self.root.children.items(),
            key=lambda kv: kv[1].visits,
        )[0]

        return best_move

    # -------------------------------------------------------------
    # Single simulation
    # -------------------------------------------------------------

    def _simulate(self, node: AlphaNode) -> float:
        # Terminal?
        if self.simulator.is_terminal(node.state):
            value = self.simulator.reward(node.state)
            node.visits += 1
            node.value_sum += value
            return value

        # Expand if leaf
        if not node.children:
            moves = self.simulator.legal_moves(node.state)
            if not moves:
                value = 0.0
                node.visits += 1
                node.value_sum += value
                return value

            priors = self.prior_policy.priors(node.state, moves)
            node.expand(moves, priors, self.simulator)

            # Bootstrap value
            value = self.value_fn.evaluate(node.state)
            node.visits += 1
            node.value_sum += value
            return value

        # Otherwise, select child
        move, child = self._select_child(node)
        value = self._simulate(child)

        # Backprop
        node.visits += 1
        node.value_sum += value
        return value


# ---------------------------------------------------------------------
# Agent wrapper
# ---------------------------------------------------------------------

class AlphaMCTSAgent:
    """Agent that uses AlphaZero-style MCTS."""

    def __init__(self, mcts: AlphaMCTS):
        self.mcts = mcts

    def choose_move(self, state: State, moves: list[Move]) -> Optional[Move]:
        return self.mcts.choose(state)

    def play_game(self, simulator: Simulator | None = None):
        from src.engine.agent import BaseAgent
        return BaseAgent.play_game(self, simulator)
