# Quantum Crossword

import dimod
from dwave.system import LeapHybridCQMSampler
from words import WORDS

# Define crossword width and height
SIZE = 9


def gen():
    cqm = dimod.ConstrainedQuadraticModel()

    # o_i,j is whether a square is occupied (has a letter).
    o = []
    for i in range(SIZE):
        for j in range(SIZE):
            o[i][j * SIZE] = dimod.Binary(f'o_{i},{j}')

    # x_i,j is the letter in row i and col j.
    l = []
    for i in range(SIZE):
        for j in range(SIZE):
            l[i][j * SIZE] = dimod.Integer(f'l_{i},{j}')

    # Objective: fill as many squares as possible with letters.
    cqm.set_objective(-sum(o))


if __name__ == '__main__':
    gen()
