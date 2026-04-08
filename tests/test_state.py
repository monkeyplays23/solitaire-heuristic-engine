"""
Tests for the State class structure and behavior.
"""

from __future__ import annotations

from src.engine.state import State


def test_new_game_structure():
    s = State.new_game(seed=123)

    assert len(s.tableau) == 7
    assert isinstance(s.stock, list)
    assert isinstance(s.waste, list)
    assert set(s.foundations.keys()) == {"♠", "♥", "♦", "♣"}


def test_copy_is_independent():
    s1 = State.new_game(seed=123)
    s2 = s1.copy()

    assert s1.tableau == s2.tableau
    assert s1.stock == s2.stock
    assert s1.waste == s2.waste
    assert s1.foundations == s2.foundations

    assert s1.tableau is not s2.tableau
    assert s1.stock is not s2.stock
    assert s1.waste is not s2.waste
    assert s1.foundations is not s2.foundations


def test_placeholder_win_loss():
    s = State.new_game()
    assert s.is_win() is False
    assert s.is_loss() is False
