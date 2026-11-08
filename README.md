# 8-Puzzle Search Solver

A from-scratch Python implementation of classic AI search strategies applied to the
8-puzzle, with a side-by-side efficiency comparison. Built for the *Artificial
Intelligence / Intelligent Systems* course at "Gheorghe Asachi" Technical University
of Iași.

**Search methods:** BFS · DFS · depth-limited DFS · Uniform Cost Search · Greedy best-first · A*  
**Heuristics:** `h1` = misplaced tiles, `h2` = sum of Manhattan distances

## Run

```bash
python3 puzzle8.py        # no dependencies, Python 3.8+
```

The script runs its own unit tests (actions and heuristics), a small sanity check, and
then the full comparison below. The full output is saved in [`results.txt`](results.txt)
(UCS is the slow one: ~45 s because its frontier scan is O(n)).

## Problem instance

```
Initial        Goal
3 _ 8          5 6 _
7 1 5          3 4 7
6 2 4          2 1 8
```

## Results

| Method                 | Solution | Steps  | Expanded nodes | Max frontier | Time (s) |
|------------------------|----------|-------:|---------------:|-------------:|---------:|
| BFS                    | yes, optimal | 21 | 67 183 | 26 477 | 0.40 |
| DFS                    | yes, not optimal | 82 757 | 91 404 | 64 099 | 0.28 |
| Limited DFS (20 / 30)  | no       | –      | –       | –      | –    |
| UCS                    | yes, optimal | 21 | 67 183 | 26 477 | 43.39 |
| Greedy + h1            | yes, not optimal | 81 | 1 325 | 843 | 0.035 |
| Greedy + h2            | yes, not optimal | 45 | 134 | 100 | 0.0015 |
| A* + h1                | yes, optimal | 21 | 5 275 | 3 278 | 0.37 |
| **A\* + h2**           | **yes, optimal** | **21** | **336** | **209** | **0.0036** |

Optimal solution (21 moves of the blank): `R D L L D R R U L U R D L L U R D D R U U`

### Take-aways

- **BFS / UCS** are optimal but expand ~67k nodes; with uniform step costs they explore the same nodes.
- **DFS** finds *a* path, but an absurdly long one (82 757 steps). With a depth limit it finds nothing: a limit of 20 is below the optimal depth (21), and with 30 the search still fails, most likely because the explored set discards states that were first reached at a depth too close to the limit.
- **Greedy** is very fast but not optimal; the better heuristic (`h2`) cuts both the path length (81 → 45) and the work (1 325 → 134 expansions).
- **A\*** with admissible heuristics stays optimal. The more informed `h2` expands **~16× fewer nodes** than `h1` (336 vs 5 275) and is the best trade-off here.

## Code structure

| Piece | Function(s) |
|-------|-------------|
| Moves | `actUp`, `actDown`, `actLeft`, `actRight` |
| Expansion | `expandare` (generates successors with `g`, `h`, `f`) |
| Heuristics | `h1`, `h2` |
| Frontier strategies | `dupa_largime` (BFS), `dupa_adancime` (DFS), `dupa_cost` (UCS), `dupa_greedy`, `dupa_Astar` |
| Search loop | `cauta` (graph search with explored set and optional depth limit) |
| Analysis | `analiza_metode` |

Function names follow the Romanian course material (*adâncime* = depth, *lățime* = breadth,
*căutare* = search).
