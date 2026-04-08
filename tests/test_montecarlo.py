"""
Tests for Monte Carlo rollout behavior.
"""

from __future__ import annotations

from src.engine.state import State
from src.engine.montecarlo import MonteCarlo


def test_montecarlo_runs():
    mc = MonteCarlo(rollouts=10)
    s = State.new_game()

    result = mc.run(s)

    assert "terminal_wins" in result
    assert "terminal_losses" in result
    assert "visited_states" in result
    assert "unique_states" in result
