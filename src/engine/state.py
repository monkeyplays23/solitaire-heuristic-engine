"""
state.py
--------
Defines the core Klondike Solitaire state representation:
cards, piles, tableau, foundations, and legal move generation.

This module contains no heuristic logic it is purely mechanical.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Card:
    rank: int  # 1-13 for Ace-King
    suit: str  # '♠', '♥', '♦', '♣'

    @property
    def color(self):
        return 'red' if self.suit in ['♥', '♦'] else 'black'


@dataclass
class Deal:
    tableau: list[list[Card]]           # 7 piles with varying number of cards
    stock: list[Card]                   # Remaining cards to draw
    waste: list[Card]                   # Discarded cards from stock
    foundations: dict[str, list[Card]]  # 4 piles for each suit


class GameState:
    """
    Represents a full Klondike game state, including tableau, stock, waste, and foundations. Provides legal move
    generation and state transition helpers.
    """
    def __init__(self, deal: Deal):
        self.tableau = deal.tableau
        self.stock = deal.stock
        self.waste = deal.waste
        self.foundations = deal.foundations

    def legal_moves(self):
        """
        Returns a list of legal moves from the current state. A move is an opaque object defined later.
        """
        return []

    def apply_move(self, move):
        """
        Applies a move and mutates the state.
        """
        raise NotImplementedError


@dataclass(frozen=True)
class Move:
    kind: str
    src: tuple
    dst: tuple

    def is_win(self):
        return all(len(pile) == 13 for pile in self.foundations.values())

    def is_dead(self):
        return len(self.legal_moves()) == 0
