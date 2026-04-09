"""
evaluation.py
--------------
Evaluation harness for Solitaire agents.

Provides:
- run_games(agent, n)
- returns win rate, avg moves, avg reward
"""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean

from src.engine.agent import BaseAgent, GameResult
from src.engine.simulator import Simulator


@dataclass
class EvaluationResult:
    games: int
    wins: int
    win_rate: float
    avg_moves: float
    avg_reward: float


def run_games(agent: BaseAgent, n: int = 100) -> EvaluationResult:
    results: list[GameResult] = []

    for _ in range(n):
        result = agent.play_game(Simulator())
        results.append(result)

    wins = sum(1 for r in results if r.win)
    win_rate = wins / n
    avg_moves = mean(r.moves for r in results)
    avg_reward = mean(r.reward for r in results)

    return EvaluationResult(
        games=n,
        wins=wins,
        win_rate=win_rate,
        avg_moves=avg_moves,
        avg_reward=avg_reward,
    )
 