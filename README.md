**************************************************
Solitaire Heuristic Evaluation Engine
Independent Systems Project by Samuel A. Murrah
Initiated: April 2026
**************************************************

A minimal, architectural framework for evaluating decision heuristics over a large, deduplicated state‑space of
Klondike Solitaire deals. This project is not a game; it is a policy‑evaluation engine designed to measure how
efficiently a heuristic can solve unique initial states without repeating work.

The system generates canonical representations of initial deals, hashes them, and guarantees that each deal is
evaluated exactly once. This enables clean statistical measurement of heuristic performance without redundant
computation.

Purpose:
--------
Modern compute systems waste enormous cycles reprocessing identical states. This project demonstrates a contrasting
approach:

* Canonical state hashing
* Deduplicated sampling
* Heuristic‑driven evaluation
* Statistical convergence over unique states

Solitaire provides a compact, well‑structured domain for exploring these ideas.

Core Concepts:
--------------
1. Canonical Deal Hashing
   Each initial Klondike layout is serialized into a canonical byte sequence and hashed (SHA‑256 by default).
   This hash uniquely identifies the deal’s state‑space.

2. Deduplicated Monte Carlo Sampling
   The engine maintains a set of previously evaluated deal hashes.
   If a generated deal already exists in the set, it is discarded and a new one is sampled.

   This ensures:
   * No repeated deals
   * No wasted evaluation cycles
   * Clean statistical sampling

3. Heuristic Policy Evaluation
   Heuristics are defined as policies that map a game state to a move.
   The engine runs the policy until the game is won or no legal moves remain.

   Multiple heuristics can be implemented and compared under identical sampling conditions.

4. Statistical Reporting
   The engine tracks:
   * Win rate
   * Average moves
   * Average evaluation time
   * Coverage relative to theoretical solvability

   This produces a clear picture of heuristic strength.

Repository Structure:
---------------------
```
solitaire-heuristic-engine/
│
├── README.md
├── pyproject.toml / requirements.txt
│
├── src/
│   ├── engine/
│   │   ├── state.py          # card, deck, tableau, foundations
│   │   ├── hashing.py        # canonical serialization + hashing
│   │   ├── simulator.py      # applies moves, detects win/loss
│   │   ├── montecarlo.py     # deduped sampling + experiment loop
│   │   └── policy.py         # base Policy class
│   │
│   ├── heuristics/
│   │   ├── baseline.py       # primary heuristic implementation
│   │   └── variants.py       # optional alternative heuristics
│   │
│   └── cli/
│       └── run_experiment.py # command-line entry point
│
├── tests/
│   ├── test_hashing.py
│   ├── test_state.py
│   ├── test_policy.py
│   └── test_montecarlo.py
│
└── experiments/
    ├── results/
    └── notebooks/
```
Running an Experiment:
----------------------
python -m src.cli.run_experiment --games 10000 --policy baseline

This will:
* Generate 10,000 unique deals
* Evaluate them with the selected heuristic
* Produce running statistics
* Store results for later analysis

Why Solitaire?
--------------
* Large but well‑bounded state‑space
* Clear notion of solvability
* Deterministic initial layout
* Natural mapping to canonical hashing
* Rich space for heuristic design

It is an ideal domain for demonstrating state deduplication, policy evaluation, and compute‑efficient sampling.

Intended Audience:
------------------
* Systems engineers
* Researchers working with Monte Carlo methods
* Developers interested in state‑space reduction
* Anyone exploring heuristic evaluation frameworks

The project is intentionally minimal, modular, and free of GUI overhead.

Status:
-------
Active development.
Baseline heuristic implemented.
Additional heuristics and parallel sampling planned.

Design Philosophy:
------------------
This engine is built around a single principle:
treat state as a first‑class entity and never repeat work.

Rather than re‑evaluating identical initial conditions, the system:

* canonicalizes each deal,
* hashes it,
* and guarantees that no state is ever processed twice.

This mirrors the design of efficient simulation systems, build pipelines, and distributed compute frameworks where
correctness and performance depend on recognizing when work has already been done.

The project favors:

* minimalism over feature accumulation
* determinism over convenience
* explicit state over implicit behavior
* composability over monolithic design
* clarity over cleverness

Every module has a single responsibility. Every transformation is explicit. Every state is observable and reproducible.
The result is a system that is small in surface area but large in conceptual leverage.

Motivation:
-----------
Modern compute systems burn cycles repeating work they have already performed. This waste appears in simulation
pipelines, Monte Carlo methods, reinforcement learning loops, rendering systems, compilers, distributed builds, and
everyday applications.

The Solitaire domain provides a compact, well‑bounded environment to demonstrate a contrasting approach:

* hash the state
* cache the result
* never repeat work

By evaluating heuristics only on unique initial deals, the engine becomes a tool for:

* measuring heuristic strength
  Heuristic strength is defined as the proportion of unique initial deals a policy successfully solves, combined with
  the efficiency and stability of those solutions across a deduplicated Monte Carlo sample of the Klondike state‑space.

* understanding coverage of the solvable state‑space
* demonstrating how canonicalization + deduplication reduce computational waste

This project serves as a small but concrete example of a broader systems principle:
efficiency emerges from respecting the identity of state.


Architecture Diagram:
---------------------
Below is a high‑level view of the system’s flow and module boundaries:
```
                   +---------------------------+
                   |     Heuristic Policy      |
                   |  (decision rules / moves) |
                   +-------------+-------------+
                                 |
                                 v
+-------------------+     +------+-------+     +---------------------+
|   Deal Generator   +---->  Canonical   +----->  Deduplication Set  |
|  (random shuffle)  |     |  Hashing    |     |  (seen deal hashes) |
+-------------------+     +------+-------+     +----------+----------+
                                 |                         |
                                 | new deal                | duplicate
                                 v                         |
                       +---------+---------+               |
                       |     Simulator      |<-------------+
                       | (apply moves until |
                       |   win or stop)     |
                       +---------+----------+
                                 |
                                 v
                       +---------+----------+
                       |     Statistics     |
                       |  (win rate, moves, |
                       |   convergence)     |
                       +--------------------+
```

Future Work:
------------
Several extensions are planned to expand the engine’s analytical and computational capabilities:

* Parallel sampling across worker processes
* Additional heuristic families for comparative evaluation
* Configurable rule variants (draw‑1, Vegas scoring, restricted move sets)
* Improved simulator performance through state‑transition caching
* Optional visualization tools for debugging and analysis
* Exportable experiment logs for external statistical processing

Design Constraints:
-------------------
The system intentionally avoids:

* GUI components or visual rendering
* Implicit randomness or hidden state transitions
* Monolithic classes that mix simulation, policy, and sampling
* Re‑evaluation of any previously seen initial deal
* Domain‑specific shortcuts that compromise generality

These constraints ensure the engine remains minimal, reproducible, and architecturally clean.

Performance Considerations:
---------------------------
The engine is optimized around:

* O(1) hash‑set membership checks
* deterministic canonical serialization
* minimal object allocation during simulation
* separation of policy logic from state transitions
* predictable control flow for profiling and tuning

As heuristics become more sophisticated, the simulator and hashing layers can be independently optimized without
affecting the overall architecture.

## License

This project is released under the MIT License.
You are free to use, modify, and distribute the code, provided that proper attribution is maintained.

See the full license text in the `LICENSE` file.

## Attribution

If you use or reference this project in your own work, please include a link back to the repository and credit:

**Samuel A. Murrah — Solitaire Heuristic Evaluation Engine**

Attribution is not required for personal experimentation, but it is appreciated in academic, professional, or published contexts.
