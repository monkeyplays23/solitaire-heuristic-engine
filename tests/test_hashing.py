"""
test_hashing.py
Tests for canonical state hashing in the Solitaire Heuristic Engine.
"""

from __future__ import annotations

from src.engine.state import State, Deal, Card
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


def test_mutating_state_changes_hash():
    hasher = StateHasher()

    s = State.new_game(seed=123)
    h1 = hasher.hash(s)

    # mutate tableau structure
    s.tableau[0].append(Card(rank=1, suit="♠"))
    h2 = hasher.hash(s)

    assert h1 != h2


def test_foundations_order_does_not_affect_hash():
    """
    Foundations are a dict; Python dict iteration order is not guaranteed
    across versions. Hashing must canonicalize foundation order.
    """
    hasher = StateHasher()

    deal1 = Deal(
        tableau=[[] for _ in range(7)],
        stock=[],
        waste=[],
        foundations={"♠": [], "♥": [], "♦": [], "♣": []},
    )
    deal2 = Deal(
        tableau=[[] for _ in range(7)],
        stock=[],
        waste=[],
        foundations={"♦": [], "♣": [], "♥": [], "♠": []},
    )

    s1 = State(deal1)
    s2 = State(deal2)

    assert hasher.hash(s1) == hasher.hash(s2)


def test_tableau_deep_copy_hashes_equal():
    """
    Ensures that State.copy() produces a structurally identical state
    whose hash matches the original.
    """
    hasher = StateHasher()

    s1 = State.new_game(seed=123)
    s2 = s1.copy()

    assert hasher.hash(s1) == hasher.hash(s2)
