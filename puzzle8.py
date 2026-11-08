# -*- coding: utf-8 -*-
"""
8-Puzzle search solver - uninformed and informed search methods
Efficiency analysis (BFS, DFS, limited DFS, UCS, Greedy, A*)

Initial state: (3, 0, 8, 7, 1, 5, 6, 2, 4)
Goal state:    (5, 6, 0, 3, 4, 7, 2, 1, 8)
(0 = the blank tile)
"""

from collections import namedtuple
import time

DJOC = 3  # board size: 3x3

# Search tree node
Nod = namedtuple("Nod", ["stare", "pred", "d", "g", "h", "f"])
# stare - puzzle configuration (tuple of 9 elements)
# pred  - predecessor node (used to rebuild the solution)
# d     - action that led to this state
# g     - path cost from the initial state
# h     - heuristic estimate
# f     - f = g + h (A*) or f = h (greedy)

# ============================================================
# Actions (move the blank tile Up, Down, Left, Right)
# ============================================================

def actUp(stare):
    """Move the blank up. Returns (new_state, action, inverse_action) or None."""
    pos = stare.index(0)
    if pos < DJOC:  # first row: cannot move up
        return None
    new_pos = pos - DJOC
    lst = list(stare)
    lst[pos], lst[new_pos] = lst[new_pos], lst[pos]
    return (tuple(lst), 'U', 'D')


def actDown(stare):
    """Move the blank down."""
    pos = stare.index(0)
    if pos >= DJOC * (DJOC - 1):  # last row
        return None
    new_pos = pos + DJOC
    lst = list(stare)
    lst[pos], lst[new_pos] = lst[new_pos], lst[pos]
    return (tuple(lst), 'D', 'U')


def actLeft(stare):
    """Move the blank to the left."""
    pos = stare.index(0)
    if pos % DJOC == 0:  # first column
        return None
    new_pos = pos - 1
    lst = list(stare)
    lst[pos], lst[new_pos] = lst[new_pos], lst[pos]
    return (tuple(lst), 'L', 'R')


def actRight(stare):
    """Move the blank to the right."""
    pos = stare.index(0)
    if pos % DJOC == DJOC - 1:  # last column
        return None
    new_pos = pos + 1
    lst = list(stare)
    lst[pos], lst[new_pos] = lst[new_pos], lst[pos]
    return (tuple(lst), 'R', 'L')


def test_actiuni():
    si = (1, 2, 3, 4, 0, 5, 6, 7, 8)  # middle
    assert actUp(si)[0] == (1, 0, 3, 4, 2, 5, 6, 7, 8)
    assert actDown(si)[0] == (1, 2, 3, 4, 7, 5, 6, 0, 8)
    assert actLeft(si)[0] == (1, 2, 3, 0, 4, 5, 6, 7, 8)
    assert actRight(si)[0] == (1, 2, 3, 4, 5, 0, 6, 7, 8)

    si = (1, 2, 0, 3, 4, 5, 6, 7, 8)  # top-right corner
    assert actUp(si) is None
    assert actRight(si) is None

    si = (0, 1, 2, 3, 4, 5, 6, 7, 8)  # top-left corner
    assert actUp(si) is None
    assert actLeft(si) is None

    si = (1, 2, 3, 4, 5, 6, 0, 7, 8)  # bottom-left corner
    assert actDown(si) is None
    assert actLeft(si) is None
    assert actUp(si)[0] == (1, 2, 3, 0, 5, 6, 4, 7, 8)

    print("✓ Action tests passed")


# ============================================================
# Node expansion
# ============================================================

def expandare(nod, sf=(0, 0, 0), hfun=None):
    """Expand a node into all valid successors.
    hfun: heuristic h(state, goal); sf: goal state.
    """
    if not hfun:
        hfun = lambda x, y: 0

    actiuni = [actUp(nod.stare), actLeft(nod.stare),
               actRight(nod.stare), actDown(nod.stare)]
    actiuni = [x for x in actiuni if x is not None]

    noduri = []
    for (stare_noua, actiune, _) in actiuni:
        g_nou = nod.g + 1  # every move costs 1
        h_nou = hfun(stare_noua, sf)
        f_nou = g_nou + h_nou
        noduri.append(Nod(stare=stare_noua, pred=nod, d=actiune,
                          g=g_nou, h=h_nou, f=f_nou))
    return noduri


# ============================================================
# Heuristics
# ============================================================

def h1(s, sf):
    """Number of misplaced tiles (blank excluded)."""
    contor = 0
    for i in range(len(s)):
        if s[i] != 0 and s[i] != sf[i]:
            contor += 1
    return contor


def h2(s, sf):
    """Sum of Manhattan distances of every tile (blank excluded)."""
    contor = 0
    for val in range(1, DJOC * DJOC):
        pos_curent = s.index(val)
        pos_final = sf.index(val)
        r_c, c_c = pos_curent // DJOC, pos_curent % DJOC
        r_f, c_f = pos_final // DJOC, pos_final % DJOC
        contor += abs(r_c - r_f) + abs(c_c - c_f)
    return contor


def test_h1():
    sx = (1, 2, 3, 4, 0, 5, 6, 7, 8)
    sf = (1, 2, 3, 4, 5, 8, 6, 0, 7)
    val = h1(sx, sf)
    print(f"  h1({sx}, {sf}) = {val}")
    # pos 5: 5!=8, pos 7: 7!=0, pos 8: 8!=7 => h1 = 3
    assert val == 3
    print("✓ h1 tests passed")


def test_h2():
    sx = (1, 2, 3, 4, 0, 5, 6, 7, 8)
    sf = (1, 2, 3, 4, 5, 8, 6, 0, 7)
    val = h2(sx, sf)
    print(f"  h2({sx}, {sf}) = {val}")
    assert val == 3
    print("✓ h2 tests passed")


# ============================================================
# Frontier selection strategies
# ============================================================

def dupa_adancime(front):
    """DFS: last in, first out (stack)."""
    return front.pop(-1)


def dupa_largime(front):
    """BFS: first in, first out (queue)."""
    return front.pop(0)


def dupa_cost(front):
    """UCS: node with the smallest g."""
    nod = min(front, key=lambda e: e.g)
    front.remove(nod)
    return nod


def dupa_greedy(front):
    """Greedy best-first: node with the smallest h."""
    nod = min(front, key=lambda e: e.h)
    front.remove(nod)
    return nod


def dupa_Astar(front):
    """A*: node with the smallest f = g + h."""
    nod = min(front, key=lambda e: e.f)
    front.remove(nod)
    return nod


# ============================================================
# General graph search
# ============================================================

def reconstituie_drum(nod):
    """Rebuild the sequence of actions from the initial state to `nod`."""
    drum = []
    curent = nod
    while curent.pred:
        drum.append((curent.d, curent.stare))
        curent = curent.pred
    drum.reverse()
    return drum


def cauta(si, sf, selectie=dupa_adancime, hfun=None, limita=None, verbose=True):
    """
    General graph search.
    si: initial state, sf: goal state
    selectie: frontier selection strategy
    hfun: heuristic (None => h = 0)
    limita: depth limit (None => unlimited)
    Returns (path, expanded_nodes, seconds, max_frontier) or None.
    """
    hfun_intern = hfun if hfun else (lambda x, y: 0)

    start_time = time.time()

    h0 = hfun_intern(si, sf)
    nod_initial = Nod(stare=si, pred=None, d=None, g=0, h=h0, f=h0)

    frontiera = [nod_initial]
    explorat = set()
    nr_expandari = 0
    max_frontiera = 1

    while frontiera:
        nod = selectie(frontiera)

        if nod.stare == sf:
            elapsed = time.time() - start_time
            drum = reconstituie_drum(nod)
            if verbose:
                print(f"  Solution found in {len(drum)} steps")
                print(f"  Actions: {' -> '.join([a for a, s in drum])}")
                print(f"  Expanded nodes: {nr_expandari}")
                print(f"  Max frontier size: {max_frontiera}")
                print(f"  Time: {elapsed:.4f}s")
            return drum, nr_expandari, elapsed, max_frontiera

        if nod.stare in explorat:
            continue

        explorat.add(nod.stare)

        if limita is not None and nod.g >= limita:
            continue

        succesori = expandare(nod, sf, hfun_intern)
        nr_expandari += 1

        for s in succesori:
            if s.stare not in explorat:
                frontiera.append(s)

        if len(frontiera) > max_frontiera:
            max_frontiera = len(frontiera)

        # Safety stop
        if nr_expandari > 500000:
            elapsed = time.time() - start_time
            if verbose:
                print(f"  STOPPED: more than 500000 expansions ({elapsed:.4f}s)")
            return None

    elapsed = time.time() - start_time
    if verbose:
        print(f"  No solution found ({nr_expandari} expansions, {elapsed:.4f}s)")
    return None


# ============================================================
# Comparative analysis
# ============================================================

def afiseaza_stare(stare):
    """Print a state as a 3x3 grid."""
    for i in range(DJOC):
        row = stare[i * DJOC:(i + 1) * DJOC]
        print("  ", " ".join(str(x) if x != 0 else "_" for x in row))


def analiza_metode(si, sf):
    """Run every search method and compare their efficiency."""
    print("=" * 70)
    print("SEARCH METHODS EFFICIENCY ANALYSIS - 8 PUZZLE")
    print("=" * 70)

    print("\nInitial state:")
    afiseaza_stare(si)
    print("\nGoal state:")
    afiseaza_stare(sf)

    print(f"\nh1(si, sf) = {h1(si, sf)} (misplaced tiles)")
    print(f"h2(si, sf) = {h2(si, sf)} (Manhattan distance)")

    metode = [
        ("BFS (breadth-first)", dupa_largime, None, None),
        ("DFS (depth-first)", dupa_adancime, None, None),
        ("Limited DFS (limit=20)", dupa_adancime, None, 20),
        ("Limited DFS (limit=30)", dupa_adancime, None, 30),
        ("UCS (uniform cost)", dupa_cost, None, None),
        ("Greedy with h1", dupa_greedy, h1, None),
        ("Greedy with h2", dupa_greedy, h2, None),
        ("A* with h1", dupa_Astar, h1, None),
        ("A* with h2", dupa_Astar, h2, None),
    ]

    rezultate = []

    for (nume, selectie, hfun, limita) in metode:
        print(f"\n{'─' * 60}")
        print(f"Method: {nume}")
        print(f"{'─' * 60}")

        rez = cauta(si, sf, selectie=selectie, hfun=hfun,
                    limita=limita, verbose=True)

        if rez is not None:
            drum, nr_exp, timp, max_front = rez
            rezultate.append((nume, len(drum), nr_exp, max_front, timp, "Yes"))
        else:
            rezultate.append((nume, "-", "-", "-", "-", "No"))

    print(f"\n\n{'=' * 90}")
    print("COMPARISON TABLE")
    print(f"{'=' * 90}")
    print(f"{'Method':<30} {'Found':>8} {'Steps':>8} {'Expanded':>12} {'Max front.':>12} {'Time(s)':>10}")
    print(f"{'─' * 90}")

    for (nume, pasi, nr_exp, max_front, timp, gasit) in rezultate:
        if gasit == "Yes":
            print(f"{nume:<30} {gasit:>8} {pasi:>8} {nr_exp:>12} {max_front:>12} {timp:>10.4f}")
        else:
            print(f"{nume:<30} {gasit:>8} {'─':>8} {'─':>12} {'─':>12} {'─':>10}")

    print(f"{'=' * 90}")


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    print("Running tests...\n")
    test_actiuni()
    test_h1()
    test_h2()

    print("\n" + "=" * 50)
    print("Simple check: si -> sf1 (4 actions)")
    print("=" * 50)
    si_test = (1, 2, 3, 4, 0, 5, 6, 7, 8)
    sf1_test = (1, 2, 3, 4, 5, 8, 6, 0, 7)
    print("\nA* with h2:")
    cauta(si_test, sf1_test, selectie=dupa_Astar, hfun=h2)

    print("\n\n")
    si_tema = (3, 0, 8, 7, 1, 5, 6, 2, 4)
    sf_tema = (5, 6, 0, 3, 4, 7, 2, 1, 8)
    analiza_metode(si_tema, sf_tema)
