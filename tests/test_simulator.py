"""
Tests for the Simulator interface.
"""

from __future__ import annotations

from src.engine.state import State
from src.engine.simulator import Simulator


def test_simulator_legal_moves_returns_list():
    sim = Simulator()
    s = State.new_game()

    moves = sim.legal_moves(s)
    assert isinstance(moves, list)


def test_simulator_apply_returns_state():
    sim = Simulator()
    s = State.new_game()

    # placeholder: no moves exist
    new_state = sim.apply(s, None)

    assert isinstance(new_state, State)
