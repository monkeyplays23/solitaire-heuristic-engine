"""
run_experiment.py
CLI entry point for the Solitaire Heuristic Evaluation Engine.

This script:
- builds an initial state
- selects a policy
- runs Monte Carlo rollouts
- prints summary statistics
"""

from __future__ import annotations

from dataclasses import dataclass

from ..engine.state import State
from ..engine.simulator import Simulator
from ..engine.montecarlo import MonteCarlo
from ..engine.policy import RandomPolicy


@dataclass
class Config:
    rollouts: int = 1000
    max_depth: int = 200


def main():
    cfg = Config()

    # Initial state
    state = State.new_game()

    # Core engine components
    simulator = Simulator()
    policy = RandomPolicy()
    mc = MonteCarlo(
        simulator=simulator,
        policy=policy,
        max_depth=cfg.max_depth,
    )

    stats = mc.run(state, rollouts=cfg.rollouts)

    print("Monte Carlo Results:")
    for k, v in stats.as_dict().items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
