"""
value.py
--------
Heuristic value function for Klondike Solitaire.
Compatible with the State structure where tableau = list[list[Card]].
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any

from src.engine.state import State


# ---------------------------------------------------------------------
# Centralized Heuristic Weights
# ---------------------------------------------------------------------

WEIGHTS: Dict[str, float] = {
    # Step 1 — Survival
    "mobility_reward": 0.05,
    "zero_mobility_penalty": -1.0,
    "waste_cycle_penalty": -0.5,
    "foundation_stagnation_penalty": -0.3,
    "reveal_stagnation_penalty": -0.3,
    "face_down_presence_bonus": 0.1,

    # Step 2 — Curiosity
    "direct_reveal_bonus": 0.8,
    "potential_reveal_bonus": 0.15,
    "burial_penalty_per_card": -0.02,
    "empty_column_reveal_bonus": 0.25,

    # Step 3 — Foundation Timing
    "safe_foundation_bonus": 0.1,
    "premature_foundation_penalty": -0.6,
    "balanced_foundation_bonus": 0.2,
    "low_clear_bonus": 0.05,

    # Step 4 — Tableau Structure
    "sequence_bonus": 0.03,
    "color_clump_penalty": -0.05,
    "buried_king_penalty": -0.4,
    "playable_king_bonus": 0.25,
    "open_column_bonus": 0.4,
    "messy_penalty": -0.02,

    # Step 5 — Endgame
    "foundation_progress_bonus": 0.05,
    "all_revealed_bonus": 2.0,
    "late_clear_bonus": 0.5,
    "endgame_dump_bonus": 0.1,
    "late_waste_cycle_penalty": -0.5,
}

DEBUG_HEURISTIC = False


# ---------------------------------------------------------------------
# Base Value Function
# ---------------------------------------------------------------------

class ValueFunction:
    def evaluate(self, state: State) -> float:
        raise NotImplementedError


# ---------------------------------------------------------------------
# Heuristic Value Function
# ---------------------------------------------------------------------

@dataclass
class HeuristicValueFunction(ValueFunction):
    """
    Full 5‑layer heuristic evaluator:
    1. Survival
    2. Curiosity
    3. Foundation Timing
    4. Tableau Structure
    5. Endgame Acceleration
    """

    def __init__(self):
        super().__init__()

    # -------------------------------------------------------------
    # Debug Breakdown Printer
    # -------------------------------------------------------------
    def _log_breakdown(self, breakdown: Dict[str, float], total: float):
        if not DEBUG_HEURISTIC:
            return
        print("\n=== Heuristic Breakdown ===")
        for k, v in breakdown.items():
            print(f"{k:30s}: {v:+.3f}")
        print(f"{'TOTAL':30s}: {total:+.3f}")
        print("===========================\n")

    # -------------------------------------------------------------
    # Main Evaluation
    # -------------------------------------------------------------
    def evaluate(self, state: State) -> float:
        breakdown: Dict[str, float] = {}
        score = 0.0

        # Helper lambdas for tableau access
        face_down = lambda pile: [c for c in pile if not c.face_up]
        face_up = lambda pile: [c for c in pile if c.face_up]

        # =============================================================
        # Step 1 — Survival
        # =============================================================
        """
        Step 1: Mobility + Dead-State Penalty
        ------------------------------------
        - Penalizes states with no meaningful moves
        - Penalizes repeated waste cards (spin cycles)
        - Rewards mobility (more legal moves = safer)
        - Penalizes stagnation (no reveals, no foundation progress)
        """

        step1 = 0.0

        legal_moves = state.legal_moves()
        meaningful = [m for m in legal_moves if m.kind not in ("stock_to_waste", "recycle_waste")]
        mobility = len(meaningful)

        step1 += WEIGHTS["mobility_reward"] * mobility

        if mobility == 0:
            step1 += WEIGHTS["zero_mobility_penalty"]

        if getattr(state, "waste_cycle_count", 0) >= 3:
            step1 += WEIGHTS["waste_cycle_penalty"]

        if getattr(state, "foundation_stagnation", 0) >= 5:
            step1 += WEIGHTS["foundation_stagnation_penalty"]

        if getattr(state, "reveal_stagnation", 0) >= 5:
            step1 += WEIGHTS["reveal_stagnation_penalty"]

        total_face_down = sum(len(face_down(p)) for p in state.tableau)
        if total_face_down > 0:
            step1 += WEIGHTS["face_down_presence_bonus"]

        breakdown["step1_survival"] = step1
        score += step1

        # =============================================================
        # Step 2 — Curiosity
        # =============================================================
        """
        Step 2: Reveal Bonus (Curiosity Instinct)
        ----------------------------------------
        - Rewards moves that flip face-down cards
        - Rewards positions close to revealing new cards
        - Penalizes burying face-down cards deeper
        - Rewards empty tableau columns
        """

        step2 = 0.0

        if getattr(state, "last_move_revealed", False):
            step2 += WEIGHTS["direct_reveal_bonus"]

        potential = sum(1 for p in state.tableau if face_down(p) and face_up(p))
        step2 += WEIGHTS["potential_reveal_bonus"] * potential

        buried = sum(len(face_down(p)) for p in state.tableau)
        step2 += WEIGHTS["burial_penalty_per_card"] * buried

        empty_cols = sum(1 for p in state.tableau if len(p) == 0)
        step2 += WEIGHTS["empty_column_reveal_bonus"] * empty_cols

        breakdown["step2_curiosity"] = step2
        score += step2

        # =============================================================
        # Step 3 — Foundation Timing
        # =============================================================
        """
        Step 3: Foundation Timing (Patience vs Progress)
        ------------------------------------------------
        - Rewards safe foundation moves
        - Penalizes premature foundation moves
        - Rewards balanced foundation growth
        - Rewards clearing low cards
        """

        step3 = 0.0

        safe_foundation = sum(len(p) for p in state.foundations.values() if len(p) <= 3)
        step3 += WEIGHTS["safe_foundation_bonus"] * safe_foundation

        if getattr(state, "last_move_to_foundation", None):
            moved = state.last_move_to_foundation
            moved_rank = moved.rank
            moved_color = moved.color

            needed = False
            for pile in state.tableau:
                ups = face_up(pile)
                if ups:
                    top = ups[-1]
                    if top.rank == moved_rank + 1 and top.color != moved_color:
                        needed = True
                        break

            if needed:
                step3 += WEIGHTS["premature_foundation_penalty"]

        sizes = [len(p) for p in state.foundations.values()]
        if sizes and max(sizes) - min(sizes) <= 2:
            step3 += WEIGHTS["balanced_foundation_bonus"]

        low_clear = 0
        for pile in state.tableau:
            ups = face_up(pile)
            if ups and ups[-1].rank in (2, 3, 4):
                low_clear += 1
        step3 += WEIGHTS["low_clear_bonus"] * low_clear

        breakdown["step3_foundation_timing"] = step3
        score += step3

        # =============================================================
        # Step 4 — Tableau Structure
        # =============================================================
        """
        Step 4: Tableau Structure (Board Shape Awareness)
        -------------------------------------------------
        - Rewards long alternating sequences
        - Penalizes color clumps
        - Penalizes buried kings
        - Rewards playable kings
        - Rewards open columns
        - Penalizes messy stacks
        """

        step4 = 0.0

        seq_bonus = 0
        for pile in state.tableau:
            ups = face_up(pile)
            if not ups:
                continue
            seq = 1
            for i in range(len(ups) - 1):
                a, b = ups[i], ups[i + 1]
                if a.color != b.color and a.rank == b.rank + 1:
                    seq += 1
                else:
                    break
            seq_bonus += seq
        step4 += WEIGHTS["sequence_bonus"] * seq_bonus

        clumps = 0
        for pile in state.tableau:
            ups = face_up(pile)
            for i in range(len(ups) - 1):
                if ups[i].color == ups[i + 1].color:
                    clumps += 1
        step4 += WEIGHTS["color_clump_penalty"] * clumps

        buried_kings = 0
        for pile in state.tableau:
            if any(not c.face_up for c in pile):
                if any(c.rank == 13 and c.face_up for c in pile):
                    buried_kings += 1
        step4 += WEIGHTS["buried_king_penalty"] * buried_kings

        playable_kings = sum(1 for pile in state.tableau if face_up(pile) and face_up(pile)[-1].rank == 13)
        step4 += WEIGHTS["playable_king_bonus"] * playable_kings

        open_cols = sum(1 for pile in state.tableau if len(pile) == 0)
        step4 += WEIGHTS["open_column_bonus"] * open_cols

        messy = 0
        for pile in state.tableau:
            ups = face_up(pile)
            for i in range(len(ups) - 1):
                if ups[i].rank != ups[i + 1].rank + 1:
                    messy += 1
        step4 += WEIGHTS["messy_penalty"] * messy

        breakdown["step4_structure"] = step4
        score += step4

        # =============================================================
        # Step 5 — Endgame Acceleration
        # =============================================================
        """
        Step 5: Endgame Acceleration (Win-Path Awareness)
        -------------------------------------------------
        - Rewards high foundation totals
        - Rewards clearing tableau in late game
        - Encourages foundation dumping when safe
        - Penalizes late waste cycling
        """

        step5 = 0.0

        foundation_total = sum(len(p) for p in state.foundations.values())
        step5 += WEIGHTS["foundation_progress_bonus"] * foundation_total

        if total_face_down == 0:
            step5 += WEIGHTS["all_revealed_bonus"]

        if total_face_down <= 3:
            cleared = sum(1 for pile in state.tableau if len(pile) == 0)
            step5 += WEIGHTS["late_clear_bonus"] * cleared

        if total_face_down == 0:
            for pile in state.tableau:
                ups = face_up(pile)
                step5 += WEIGHTS["endgame_dump_bonus"] * len(ups)

        if total_face_down <= 2 and getattr(state, "waste_cycle_count", 0) >= 2:
            step5 += WEIGHTS["late_waste_cycle_penalty"]

        breakdown["step5_endgame"] = step5
        score += step5

        # =============================================================
        # Step 6 — Stagnation Kill Switch
        # =============================================================

        # Combine stagnation signals
        stagnation = (
            state.reveal_stagnation +
            state.foundation_stagnation +
            state.waste_cycle_count * 10
        )

        # Apply a strong penalty if stagnation is high
        if stagnation > 20:
            score -= 0.1 * stagnation
            breakdown["step6_stagnation_penalty"] = -0.1 * stagnation
        else:
            breakdown["step6_stagnation_penalty"] = 0.0

        # -------------------------------------------------------------
        # Final
        # -------------------------------------------------------------
        self._log_breakdown(breakdown, score)
        return score
