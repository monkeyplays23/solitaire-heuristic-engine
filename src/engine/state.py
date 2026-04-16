"""
state.py
--------
Defines the core Klondike Solitaire state representation:
cards, piles, tableau, foundations, and legal move generation.

Now fully instrumented for heuristic evaluation.
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

    @property
    def rank_str(self) -> str:
        mapping = {
            1: "A",
            11: "J",
            12: "Q",
            13: "K",
        }
        return mapping.get(self.rank, str(self.rank))


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
# State (FULLY INSTRUMENTED)
# ---------------------------------------------------------------------

class State:
    """
    Represents a full Klondike game state, including tableau, stock, waste,
    and foundations. Now fully instrumented for heuristic evaluation.
    """

    def __init__(self, deal: Deal):
        self.tableau = deal.tableau
        self.stock = deal.stock
        self.waste = deal.waste
        self.foundations = deal.foundations

        # -------------------------------------------------------------
        # Instrumentation fields
        # -------------------------------------------------------------
        self.last_move_revealed = False
        self.last_move_to_foundation = None

        self.waste_cycle_count = 0
        self.last_waste_top = None

        self.foundation_stagnation = 0
        self.last_foundation_totals = self._foundation_total()

        self.reveal_stagnation = 0
        self.last_face_down_total = self._face_down_total()

        self.move_counter = 0

    # -------------------------------------------------------------
    # Instrumentation helpers
    # -------------------------------------------------------------
    def _foundation_total(self) -> int:
        return sum(len(p) for p in self.foundations.values())

    def _face_down_total(self) -> int:
        return sum(1 for pile in self.tableau for c in pile if not c.face_up)

    def _update_instrumentation(self, before: "State", move: Move):
        """Compare before/after and update heuristic signals."""
        self.move_counter += 1

        # -----------------------------
        # 1. Reveal detection
        # -----------------------------
        before_down = before._face_down_total()
        after_down = self._face_down_total()

        if after_down < before_down:
            self.last_move_revealed = True
            self.reveal_stagnation = 0
        else:
            self.last_move_revealed = False
            self.reveal_stagnation += 1

        # -----------------------------
        # 2. Foundation progress
        # -----------------------------
        before_f = before._foundation_total()
        after_f = self._foundation_total()

        if after_f > before_f:
            # detect which card moved
            for suit, pile in self.foundations.items():
                if len(pile) > len(before.foundations[suit]):
                    self.last_move_to_foundation = pile[-1]
                    break
            self.foundation_stagnation = 0
        else:
            self.last_move_to_foundation = None
            self.foundation_stagnation += 1

        # -----------------------------
        # 3. Waste cycle detection
        # -----------------------------
        before_top = before.waste[-1] if before.waste else None
        after_top = self.waste[-1] if self.waste else None

        if after_top == before_top and move.kind in ("recycle_waste", "stock_to_waste"):
            self.waste_cycle_count += 1
        else:
            self.waste_cycle_count = 0

        self.last_waste_top = after_top

    # -------------------------------------------------------------
    # New Game
    # -------------------------------------------------------------
    @classmethod
    def new_game(cls, seed=None):
        rng = random.Random(seed)

        suits = ["♠", "♥", "♦", "♣"]
        deck = [Card(rank=r, suit=s, face_up=False)
                for s in suits
                for r in range(1, 14)]

        rng.shuffle(deck)

        tableau = []
        index = 0
        for pile_size in range(1, 8):
            pile = deck[index:index + pile_size]
            index += pile_size

            pile = [Card(c.rank, c.suit, face_up=False) for c in pile]
            pile[-1] = Card(pile[-1].rank, pile[-1].suit, face_up=True)

            tableau.append(pile)

        stock = [Card(c.rank, c.suit, face_up=False) for c in deck[index:]]
        waste = []
        foundations = {"♠": [], "♥": [], "♦": [], "♣": []}

        return cls(Deal(tableau, stock, waste, foundations))

    # -------------------------------------------------------------
    # Copy
    # -------------------------------------------------------------
    def copy(self) -> "State":
        new = State(Deal(
            tableau=[pile[:] for pile in self.tableau],
            stock=self.stock[:],
            waste=self.waste[:],
            foundations={s: p[:] for s, p in self.foundations.items()},
        ))

        # copy instrumentation
        new.last_move_revealed = self.last_move_revealed
        new.last_move_to_foundation = self.last_move_to_foundation
        new.waste_cycle_count = self.waste_cycle_count
        new.last_waste_top = self.last_waste_top
        new.foundation_stagnation = self.foundation_stagnation
        new.last_foundation_totals = self.last_foundation_totals
        new.reveal_stagnation = self.reveal_stagnation
        new.last_face_down_total = self.last_face_down_total
        new.move_counter = self.move_counter

        return new

    # -------------------------------------------------------------
    # Win/Loss
    # -------------------------------------------------------------
    def is_win(self) -> bool:
        return all(len(pile) == 13 for pile in self.foundations.values())

    def is_loss(self) -> bool:
        return False

    # -------------------------------------------------------------
    # Legal Move Helpers
    # -------------------------------------------------------------
    def _can_place_on_tableau(self, card: Card, pile: list[Card]) -> bool:
        if not pile:
            return card.rank == 13
        top = pile[-1]
        return (top.face_up
                and top.color != card.color
                and top.rank == card.rank + 1)

    def _can_place_on_foundation(self, card: Card) -> bool:
        pile = self.foundations[card.suit]
        if not pile:
            return card.rank == 1
        return pile[-1].rank + 1 == card.rank

    # -------------------------------------------------------------
    # Legal Move Generation
    # -------------------------------------------------------------
    def legal_moves(self) -> list["Move"]:
        moves = []

        if self.stock:
            moves.append(Move("stock_to_waste", None, None))
        elif self.waste:
            moves.append(Move("recycle_waste", None, None))

        if self.waste:
            card = self.waste[-1]

            for i, pile in enumerate(self.tableau):
                if self._can_place_on_tableau(card, pile):
                    moves.append(Move("waste_to_tableau", None, (i, None)))

            if self._can_place_on_foundation(card):
                moves.append(Move("waste_to_foundation", None, (card.suit, None)))

        for i, pile in enumerate(self.tableau):
            if pile and pile[-1].face_up:
                card = pile[-1]
                if self._can_place_on_foundation(card):
                    moves.append(Move("tableau_to_foundation", (i, -1), (card.suit, None)))

        for i, src in enumerate(self.tableau):
            for idx, card in enumerate(src):
                if not card.face_up:
                    continue
                stack = src[idx:]
                for j, dst in enumerate(self.tableau):
                    if i == j:
                        continue
                    if self._can_place_on_tableau(stack[0], dst):
                        moves.append(Move("tableau_to_tableau", (i, idx), (j, None)))

        return moves

    # -------------------------------------------------------------
    # Transition Helpers
    # -------------------------------------------------------------
    def _move_tableau_to_tableau(self, src_pile, idx, dst_pile):
        stack = self.tableau[src_pile][idx:]
        del self.tableau[src_pile][idx:]
        self.tableau[dst_pile].extend(stack)

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

    # -------------------------------------------------------------
    # Apply Move (instrumented)
    # -------------------------------------------------------------
    def apply_move(self, move: "Move") -> "State":
        before = self.copy()
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

        # Update instrumentation
        s._update_instrumentation(before, move)

        return s

    # -------------------------------------------------------------
    # Pretty Print
    # -------------------------------------------------------------
    def pretty(self) -> str:
        """Return a simple ASCII representation of the Klondike state."""
        def fmt(card):
            if not card.face_up:
                return "XX"
            return f"{card.rank_str}{card.suit}"

        f = self.foundations
        foundations_str = (
            f"♠:{fmt(f['♠'][-1]) if f['♠'] else '--'}  "
            f"♥:{fmt(f['♥'][-1]) if f['♥'] else '--'}  "
            f"♦:{fmt(f['♦'][-1]) if f['♦'] else '--'}  "
            f"♣:{fmt(f['♣'][-1]) if f['♣'] else '--'}"
        )

        waste_str = fmt(self.waste[-1]) if self.waste else "--"
        stock_str = f"{len(self.stock)} cards"

        tableau_lines = []
        for i, pile in enumerate(self.tableau):
            cards = " ".join(fmt(c) for c in pile)
            tableau_lines.append(f"{i+1}: {cards}")

        tableau_str = "\n".join(tableau_lines)

        return (
            "Foundations: " + foundations_str + "\n"
            "Waste: " + waste_str + "    "
            "Stock: " + stock_str + "\n\n"
            "Tableau:\n" + tableau_str
        )
