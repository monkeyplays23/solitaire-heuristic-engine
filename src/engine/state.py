"""
state.py
--------
Defines the core Klondike Solitaire state representation:
cards, piles, tableau, foundations, and legal move generation.

This module contains no heuristic logic; it is purely mechanical.
"""

from __future__ import annotations

from dataclasses import dataclass


# ---------------------------------------------------------------------
# Card + Deal
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class Card:
    rank: int  # 1-13 for Ace-King
    suit: str  # '♠', '♥', '♦', '♣'

    @property
    def color(self) -> str:
        return "red" if self.suit in ["♥", "♦"] else "black"


@dataclass
class Deal:
    tableau: list[list[Card]]
    stock: list[Card]
    waste: list[Card]
    foundations: dict[str, list[Card]]


# ---------------------------------------------------------------------
# State
# ---------------------------------------------------------------------

class State:
    """
    Represents a full Klondike game state, including tableau, stock, waste,
    and foundations. Provides legal move generation and state transition
    helpers.
    """

    def __init__(self, deal: Deal):
        self.tableau = deal.tableau
        self.stock = deal.stock
        self.waste = deal.waste
        self.foundations = deal.foundations

    @classmethod
    def new_game(cls, seed: int | None = None) -> "State":
        """
        Create a new deterministic starting state.

        Placeholder: returns empty tableau/stock/waste/foundations.
        """
        import random
        if seed is not None:
            random.seed(seed)

        deal = Deal(
            tableau=[[] for _ in range(7)],
            stock=[],
            waste=[],
            foundations={"♠": [], "♥": [], "♦": [], "♣": []},
        )
        return cls(deal)

    def copy(self) -> "State":
        """
        Return a shallow structural copy of the state.

        Placeholder: real deep-copying will be added later.
        """
        deal = Deal(
            tableau=[pile[:] for pile in self.tableau],
            stock=self.stock[:],
            waste=self.waste[:],
            foundations={s: p[:] for s, p in self.foundations.items()},
        )
        return State(deal)

    def is_win(self) -> bool:
        """Placeholder win condition."""
        return all(len(pile) == 13 for pile in self.foundations.values())

    def is_loss(self) -> bool:
        """Placeholder loss condition."""
        return False  # real logic comes later

    def legal_moves(self) -> list["Move"]:
        """Placeholder: no legal moves yet."""
        return []

    def apply_move(self, move: "Move") -> "State":
        """Placeholder: return state unchanged."""
        return self


# ---------------------------------------------------------------------
# Move
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class Move:
    kind: str
    src: tuple
    dst: tuple
