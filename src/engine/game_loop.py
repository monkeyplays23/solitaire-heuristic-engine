"""
game_loop.py
------------
Simple CLI game loop for Klondike Solitaire.

Supports:
- agent-driven play (watch the AI)
- step-by-step rendering
"""

from __future__ import annotations

from time import sleep

from src.engine.state import State, Move
from src.engine.simulator import Simulator
from src.engine.agent import BaseAgent


# ---------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------

def render_state(state: State) -> None:
    print("\n=== STATE ===")
    foundation_counts = {s: len(p) for s, p in state.foundations.items()}
    print(f"Foundations: {foundation_counts}")
    print(f"Waste: {len(state.waste)}  Stock: {len(state.stock)}")
    print("Tableau:")
    for i, pile in enumerate(state.tableau, start=1):
        up = "".join(str(c) for c in pile if c.face_up)
        down = len([c for c in pile if not c.face_up])
        print(f"  {i}: [{down} down] {up}")
    print("=============\n")


def render_move(move: Move) -> None:
    print(f"Move: {move}")


# ---------------------------------------------------------------------
# Game loop
# ---------------------------------------------------------------------

def play_with_agent(agent, simulator=None, delay=0.2, step=False, quiet=False):
    sim = simulator or Simulator()
    state = State.new_game()
    moves_taken = 0

    while not sim.is_terminal(state):
        if not quiet:
            render_state(state)

        legal = sim.legal_moves(state)
        if not legal:
            break

        move = agent.choose_move(state, legal)
        if move is None:
            break

        if not quiet:
            render_move(move)

        state = sim.next_state(state, move)
        moves_taken += 1

        # No sleeping in quiet mode
        if not quiet:
            if step:
                input()
            else:
                sleep(delay)

    if not quiet:
        render_state(state)

    reward = sim.reward(state)
    win = state.is_win()

    print(f"Game finished. Moves: {moves_taken}, Win: {win}, Reward: {reward}")

    return win


# ---------------------------------------------------------------------
# Simple CLI entry point
# ---------------------------------------------------------------------

def main() -> None:
    from src.engine.mcts_alpha import AlphaMCTS, AlphaMCTSAgent, HeuristicPriorPolicy
    from src.engine.value import HeuristicValueFunction, DEFAULT_WEIGHTS
    from src.engine.policy import HeuristicPolicy

    games = 100
    wins = 0

    for i in range(1, games + 1):
        print(f"Starting game {i}...")

        # NEW simulator per game
        sim = Simulator()

        value_fn = HeuristicValueFunction(weights=DEFAULT_WEIGHTS, simulator=sim)
        prior_policy = HeuristicPriorPolicy(policy=HeuristicPolicy())
        mcts = AlphaMCTS(prior_policy=prior_policy, value_fn=value_fn, simulator=sim)
        agent = AlphaMCTSAgent(mcts)

        win = play_with_agent(agent, simulator=sim, quiet=True)
        if win:
            wins += 1

        print(f"Completed game {i}. Total wins so far: {wins}/{i}\n")

    print(f"Final win rate: {wins}/{games}")


if __name__ == "__main__":
    main()
