"""
hashing.py
Canonical state hashing for the Solitaire Heuristic Engine.

This module provides a deterministic, collision-resistant identity function
for any State instance. It converts the entire game configuration into a
canonical tuple representation and hashes it using SHA-256.

The canonicalization rules ensure:
- Stable ordering of tableau piles
- Stable ordering of foundations
- Stable representation of face-up / face-down cards
- No dependence on Python object identity
"""

from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from typing import Tuple, Iterable

from .state import State, Card


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def _card_to_tuple(card: Card) -> Tuple[int, str, int]:
    """
    Convert a Card into a canonical tuple:
    (rank, suit, face_up_flag)

    This ensures that two cards with identical values produce identical
    representations regardless of Python object identity.
    """
    return (card.rank, card.suit, 1 if card.face_up else 0)


def _pile_to_tuple(pile: Iterable[Card]) -> Tuple[Tuple[int, str, int], ...]:
    """
    Convert a pile (list of cards) into a canonical tuple of card tuples.
    """
    return tuple(_card_to_tuple(c) for c in pile)


# ------------------------------------------------------------
# Canonicalization
# ------------------------------------------------------------

def canonicalize_state(state: State) -> Tuple:
    """
    Convert the entire State into a canonical, hashable tuple.

    Structure:
    (
        stock_tuple,
        waste_tuple,
        foundations_tuple_of_tuples,
        tableau_tuple_of_tuples
    )

    This representation is stable across runs and independent of
    Python object identity.
    """
    stock_t = _pile_to_tuple(state.stock)
    waste_t = _pile_to_tuple(state.waste)

    # Foundations: ensure deterministic ordering by suit
    # (If your foundations are stored differently, tell me and I’ll adapt.)
    if isinstance(state.foundations, dict):
        foundations_t = tuple(
            _pile_to_tuple(state.foundations[suit])
            for suit in sorted(state.foundations.keys())
        )
    else:
        # Already a list-like structure
        foundations_t = tuple(_pile_to_tuple(p) for p in state.foundations)

    # Tableau: stable ordering by pile index
    tableau_t = tuple(_pile_to_tuple(pile) for pile in state.tableau)

    return (stock_t, waste_t, foundations_t, tableau_t)


# ------------------------------------------------------------
# Hashing Interface
# ------------------------------------------------------------

@dataclass(frozen=True)
class StateHasher:
    """
    Stateless hashing utility for State objects.

    Usage:
        hasher = StateHasher()
        h = hasher.hash(state)
    """

    def hash(self, state: State) -> str:
        """
        Return a hex digest representing the canonical identity of the state.
        """
        canonical = canonicalize_state(state)
        encoded = repr(canonical).encode("utf-8")
        return sha256(encoded).hexdigest()

    def short(self, state: State, length: int = 12) -> str:
        """
        Return a shorter hash prefix for logging or debugging.
        """
        return self.hash(state)[:length]
