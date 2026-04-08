"""
test_hashing.py
Tests for canonical state hashing in the Solitaire Heuristic Engine.
"""

from __future__ import annotations

from src.engine.state import State
from src.engine.hashing import StateHasher


def test_identical_states_hash_equal():
    hasher = StateHasher()

    s1 = State.new_game(seed=123)
    s2 = State.new_game(seed=123)

    h1 = hasher.hash(s1)
    h2 = hasher.hash(s2)

    assert h1 == h2


def test_different_states_hash_different():
    hasher = StateHasher()

    s1 = State.new_game(seed=123)
    s2 = State.new_game(seed=456)

    h1 = hasher.hash(s1)
    h2 = hasher.hash(s2)

    assert h1 != h2


def test_hash_is_stable():
    hasher = StateHasher()

    s = State.new_game(seed=999)

    h1 = hasher.hash(s)
    h2 = hasher.hash(s)
    h3 = hasher.hash(s)

    assert h1 == h2 == h3
