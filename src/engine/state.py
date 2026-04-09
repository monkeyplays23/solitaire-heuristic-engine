"""
state.py
--------
Defines the core Klondike Solitaire state representation:
cards, piles, tableau, foundations, and legal move generation.

This module contains no heuristic logic; it is purely mechanical.
"""

from __future__ import annotations

from dataclasses import dataclass
import random


# ---------------------------------------------------------------------
# Card + Deal
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class Card:
    rank: int  # 1-13 for Ace-King
    suit: str  # '♠', '♥', '♦', '♣'
    face_up: bool = True

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
# Move
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class Move:
    kind: str
    src: tuple | None
    dst: tuple | None


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

    # -----------------------------------------------------------------
    # New Game
    # -----------------------------------------------------------------

    @classmethod
    def new_game(cls, seed=None):
        rng = random.Random(seed)

        # ----- 1. Build full 52-card deck -----
        suits = ["♠", "♥", "♦", "♣"]
        deck = [Card(rank=r, suit=s, face_up=False)
                for s in suits
                for r in range(1, 14)]

        rng.shuffle(deck)

        # ----- 2. Deal tableau piles (1..7 cards) -----
        tableau = []
        index = 0
        for pile_size in range(1, 8):
            pile = deck[index:index + pile_size]
            index += pile_size

            # flip only the top card
            pile = [Card(c.rank, c.suit, face_up=False) for c in pile]
            pile[-1] = Card(pile[-1].rank, pile[-1].suit, face_up=True)

            tableau.append(pile)

        # ----- 3. Remaining cards become stock -----
        stock = deck[index:]
        stock = [Card(c.rank, c.suit, face_up=False) for c in stock]

        # ----- 4. Empty waste + foundations -----
        waste = []
        foundations = {"♠": [], "♥": [], "♦": [], "♣": []}

        return cls(Deal(tableau, stock, waste, foundations))

    # -----------------------------------------------------------------
    # Copy
    # -----------------------------------------------------------------

    def copy(self) -> "State":
        deal = Deal(
            tableau=[pile[:] for pile in self.tableau],
            stock=self.stock[:],
            waste=self.waste[:],
            foundations={s: p[:] for s, p in self.foundations.items()},
        )
        return State(deal)

    # -----------------------------------------------------------------
    # Win/Loss
    # -----------------------------------------------------------------

    def is_win(self) -> bool:
        return all(len(pile) == 13 for pile in self.foundations.values())

    def is_loss(self) -> bool:
        return False  # real logic comes later

    # -----------------------------------------------------------------
    # Legal Move Helpers
    # -----------------------------------------------------------------

    def _can_place_on_tableau(self, card: Card, pile: list[Card]) -> bool:
        if not pile:
            return card.rank == 13  # only Kings on empty tableau
        top = pile[-1]
        return (top.face_up
                and top.color != card.color
                and top.rank == card.rank + 1)

    def _can_place_on_foundation(self, card: Card) -> bool:
        pile = self.foundations[card.suit]
        if not pile:
            return card.rank == 1  # Ace
        return pile[-1].rank + 1 == card.rank

    # -----------------------------------------------------------------
    # Legal Move Generation
    # -----------------------------------------------------------------

    def legal_moves(self) -> list["Move"]:
        moves = []

        # ---------------------------------------------------------
        # 1. Stock → Waste
        # ---------------------------------------------------------
        if self.stock:
            moves.append(Move("stock_to_waste", None, None))
        elif self.waste:
            moves.append(Move("recycle_waste", None, None))

        # ---------------------------------------------------------
        # 2. Waste → Tableau / Foundation
        # ---------------------------------------------------------
        if self.waste:
            card = self.waste[-1]

            # waste → tableau
            for i, pile in enumerate(self.tableau):
                if self._can_place_on_tableau(card, pile):
                    moves.append(Move("waste_to_tableau", None, (i, None)))

            # waste → foundation
            if self._can_place_on_foundation(card):
                moves.append(Move("waste_to_foundation", None, (card.suit,
                                                                None)))

        # ---------------------------------------------------------
        # 3. Tableau → Foundation
        # ---------------------------------------------------------
        for i, pile in enumerate(self.tableau):
            if pile and pile[-1].face_up:
                card = pile[-1]
                if self._can_place_on_foundation(card):
                    moves.append(Move("tableau_to_foundation", (i, -1),
                                      (card.suit, None)))

        # ---------------------------------------------------------
        # 4. Tableau → Tableau (moving stacks)
        # ---------------------------------------------------------
        for i, src in enumerate(self.tableau):
            for idx, card in enumerate(src):
                if not card.face_up:
                    continue  # can't move face-down cards

                stack = src[idx:]

                for j, dst in enumerate(self.tableau):
                    if i == j:
                        continue

                    if self._can_place_on_tableau(stack[0], dst):
                        moves.append(Move("tableau_to_tableau",
                                          (i, idx), (j, None)))

        return moves

    # -----------------------------------------------------------------
    # Transition Helpers
    # -----------------------------------------------------------------

    def _move_tableau_to_tableau(self, src_pile, idx, dst_pile):
        stack = self.tableau[src_pile][idx:]
        del self.tableau[src_pile][idx:]
        self.tableau[dst_pile].extend(stack)

        # flip new top card if needed
        if self.tableau[src_pile] and not self.tableau[src_pile][-1].face_up:
            c = self.tableau[src_pile][-1]
            self.tableau[src_pile][-1] = Card(c.rank, c.suit, True)

    def _move_tableau_to_foundation(self, src_pile):
        card = self.tableau[src_pile].pop()
        self.foundations[card.suit].append(card)

        if self.tableau[src_pile] and not self.tableau[src_pile][-1].face_up:
            c = self.tableau[src_pile][-1]
            self.tableau[src_pile][-1] = Card(c.rank, c.suit, True)

    def _move_waste_to_tableau(self, dst_pile):
        card = self.waste.pop()
        self.tableau[dst_pile].append(card)

    def _move_waste_to_foundation(self):
        card = self.waste.pop()
        self.foundations[card.suit].append(card)

    def _draw_from_stock(self):
        card = self.stock.pop()
        self.waste.append(Card(card.rank, card.suit, True))

    def _recycle_waste(self):
        while self.waste:
            c = self.waste.pop()
            self.stock.append(Card(c.rank, c.suit, False))

    # -----------------------------------------------------------------
    # Apply Move
    # -----------------------------------------------------------------

    def apply_move(self, move: "Move") -> "State":
        s = self.copy()
        kind = move.kind

        if kind == "stock_to_waste":
            s._draw_from_stock()

        elif kind == "recycle_waste":
            s._recycle_waste()

        elif kind == "waste_to_tableau":
            dst_pile, _ = move.dst
            s._move_waste_to_tableau(dst_pile)

        elif kind == "waste_to_foundation":
            s._move_waste_to_foundation()

        elif kind == "tableau_to_foundation":
            src_pile, _ = move.src
            s._move_tableau_to_foundation(src_pile)

        elif kind == "tableau_to_tableau":
            src_pile, idx = move.src
            dst_pile, _ = move.dst
            s._move_tableau_to_tableau(src_pile, idx, dst_pile)

        return s
