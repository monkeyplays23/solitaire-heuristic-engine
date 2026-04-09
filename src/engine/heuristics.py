"""
heuristics.py
--------------
Shared heuristic utilities for Klondike Solitaire.

This module provides:
- StateFeatures (dataclass)
- MoveFeatures (dataclass)
- extract_state_features(state)
- extract_move_features(state, move)
- reusable feature helpers

This is the shared substrate used by:
- policies
- value functions
- AlphaZero-style MCTS
- evaluation tools
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict

from src.engine.state import State, Move


# ---------------------------------------------------------------------
# Dataclasses for structured features
# ---------------------------------------------------------------------

@dataclass
class StateFeatures:
    foundation_cards: int
    face_down_cards: int
    face_up_cards: int
    empty_tableau: int
    mobility: int
    longest_sequence: int
    broken_sequences: int
    waste_size: int
    stock_size: int


@dataclass
class MoveFeatures:
    is_flip: bool
    is_foundation: bool
    is_king_to_empty: bool
    is_tableau_build: bool
    is_recycle: bool


# ---------------------------------------------------------------------
# State feature extraction
# ---------------------------------------------------------------------

def extract_state_features(state: State, legal_moves: List[Move] | None = None) -> StateFeatures:
    foundation_cards = sum(len(pile) for pile in state.foundation)

    face_down_cards = sum(
        1 for pile in state.tableau for c in pile if not c.face_up
    )

    face_up_cards = sum(
        1 for pile in state.tableau for c in pile if c.face_up
    )

    empty_tableau = sum(1 for pile in state.tableau if not pile)

    mobility = len(legal_moves) if legal_moves is not None else 0

    longest_sequence, broken_sequences = _sequence_metrics(state)

    waste_size = len(state.waste)
    stock_size = len(state.stock)

    return StateFeatures(
        foundation_cards=foundation_cards,
        face_down_cards=face_down_cards,
        face_up_cards=face_up_cards,
        empty_tableau=empty_tableau,
        mobility=mobility,
        longest_sequence=longest_sequence,
        broken_sequences=broken_sequences,
        waste_size=waste_size,
        stock_size=stock_size,
    )


# ---------------------------------------------------------------------
# Move feature extraction
# ---------------------------------------------------------------------

def extract_move_features(state: State, move: Move) -> MoveFeatures:
    return MoveFeatures(
        is_flip=_is_flip_move(move),
        is_foundation=_is_foundation_move(move),
        is_king_to_empty=_is_king_to_empty(move),
        is_tableau_build=_is_tableau_build(move),
        is_recycle=_is_recycle_move(move),
    )


# ---------------------------------------------------------------------
# Sequence metrics
# ---------------------------------------------------------------------

def _sequence_metrics(state: State) -> tuple[int, int]:
    longest = 0
    broken = 0

    for pile in state.tableau:
        if not pile:
            continue

        run = 1
        for i in range(len(pile) - 1):
            a = pile[i]
            b = pile[i + 1]

            if (
                a.face_up
                and b.face_up
                and a.rank == b.rank + 1
                and a.color != b.color
            ):
                run += 1
            else:
                broken += 1
                break

        longest = max(longest, run)

    return longest, broken


# ---------------------------------------------------------------------
# Move classification helpers
# ---------------------------------------------------------------------

def _is_flip_move(move: Move) -> bool:
    return move.kind == "flip"


def _is_foundation_move(move: Move) -> bool:
    return move.kind == "to_foundation"


def _is_king_to_empty(move: Move) -> bool:
    return move.kind == "to_empty_tableau"


def _is_tableau_build(move: Move) -> bool:
    return move.kind == "tableau_build"


def _is_recycle_move(move: Move) -> bool:
    return move.kind == "recycle"
