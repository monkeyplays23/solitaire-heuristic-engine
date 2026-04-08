"""
Tests for the Policy interface.
"""

from __future__ import annotations

from src.engine.state import State
from src.engine.policy import Policy


def test_policy_handles_empty_moves():
    policy = Policy()
    s = State.new_game()

    move = policy.choose_move(s, moves=[])
    assert move is None
