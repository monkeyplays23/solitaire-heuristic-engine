import pytest
from src.engine.state import State, Card


def test_new_game_has_52_cards():
    """A real Klondike deal must contain all 52 cards exactly once."""
    s = State.new_game(seed=123)

    # flatten all cards
    all_cards = []
    for pile in s.tableau:
        all_cards.extend(pile)
    all_cards.extend(s.stock)
    all_cards.extend(s.waste)
    for pile in s.foundations.values():
        all_cards.extend(pile)

    assert len(all_cards) == 52

    # ensure no duplicates by identity
    seen = set()
    for c in all_cards:
        key = (c.rank, c.suit)
        assert key not in seen
        seen.add(key)


def test_tableau_structure():
    """Tableau piles must have sizes 1..7."""
    s = State.new_game(seed=123)

    sizes = [len(p) for p in s.tableau]
    assert sizes == [1, 2, 3, 4, 5, 6, 7]


def test_tableau_top_cards_face_up():
    """Only the top card of each tableau pile should be face-up."""
    s = State.new_game(seed=123)

    for pile in s.tableau:
        if len(pile) > 1:
            # all but last must be face-down
            for c in pile[:-1]:
                assert c.face_up is False
        # last card must be face-up
        assert pile[-1].face_up is True


def test_stock_size_is_correct():
    """After dealing 1..7 cards, stock should contain 52 - 28 = 24 cards."""
    s = State.new_game(seed=123)
    assert len(s.stock) == 24
    # all stock cards must be face-down
    assert all(c.face_up is False for c in s.stock)


def test_new_game_is_deterministic_with_seed():
    """Same seed → identical deal; different seed → different deal."""
    s1 = State.new_game(seed=999)
    s2 = State.new_game(seed=999)
    s3 = State.new_game(seed=1000)

    # serialize tableau for comparison
    def serialize(state):
        return [
            [(c.rank, c.suit, c.face_up) for c in pile]
            for pile in state.tableau
        ]

    assert serialize(s1) == serialize(s2)
    assert serialize(s1) != serialize(s3)
