"""
mcts.py
-------
Monte Carlo Tree Search for Klondike Solitaire.

This is a pure UCT implementation:
- Selection via UCT
- Expansion on first visit
- Rollout via MonteCarlo
- Backpropagation of reward

No heuristics, no priors, no neural nets.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math
import random

from src.engine.state import State, Move
from src.engine.simulator import Simulator
from src.engine.montecarlo import MonteCarlo


@dataclass
class Node:
    state: State
    parent: "Node | None"
    move: Move | None
    children: dict[Move, "Node"] = field(default_factory=dict)
    visits: int = 0
    value: float = 0.0  # cumulative reward

    def uct_score(self, exploration: float = 1.414) -> float:
        if self.visits == 0:
            return float("inf")
        return (self.value / self.visits) + exploration * math.sqrt(
            math.log(self.parent.visits) / self.visits
        )


class MCTS:
    """
    Pure UCT Monte Carlo Tree Search.

    Parameters:
    - simulator: world model
    - rollout: MonteCarlo evaluator
    - iterations: number of MCTS iterations
    """

    def __init__(
        self,
        simulator: Simulator | None = None,
        rollout: MonteCarlo | None = None,
        iterations: int = 200,
        exploration: float = 1.414,
        rng: random.Random | None = None,
    ):
        self.sim = simulator or Simulator()
        self.rollout = rollout or MonteCarlo(rollouts=1)
        self.iterations = iterations
        self.exploration = exploration
        self.rng = rng or random.Random()

    # -------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------

    def choose(self, state: State) -> Move:
        root = Node(state=state, parent=None, move=None)

        for _ in range(self.iterations):
            leaf = self._select(root)
            child = self._expand(leaf)
            reward = self._simulate(child)
            self._backpropagate(child, reward)

        # choose the move with highest visit count
        best_move = max(
            root.children.items(),
            key=lambda kv: kv[1].visits,
        )[0]

        return best_move

    # -------------------------------------------------------------
    # Selection
    # -------------------------------------------------------------

    def _select(self, node: Node) -> Node:
        while node.children:
            node = max(
                node.children.values(),
                key=lambda n: n.uct_score(self.exploration),
            )
        return node

    # -------------------------------------------------------------
    # Expansion
    # -------------------------------------------------------------

    def _expand(self, node: Node) -> Node:
        if self.sim.is_terminal(node.state):
            return node

        moves = self.sim.legal_moves(node.state)
        for move in moves:
            if move not in node.children:
                next_state = self.sim.next_state(node.state, move)
                child = Node(
                    state=next_state,
                    parent=node,
                    move=move,
                )
                node.children[move] = child
                return child

        # fallback: no expansion possible
        return node

    # -------------------------------------------------------------
    # Simulation (rollout)
    # -------------------------------------------------------------

    def _simulate(self, node: Node) -> float:
        return self.rollout._rollout(node.state)[0]

    # -------------------------------------------------------------
    # Backpropagation
    # -------------------------------------------------------------

    def _backpropagate(self, node: Node, reward: float) -> None:
        while node is not None:
            node.visits += 1
            node.value += reward
            node = node.parent
