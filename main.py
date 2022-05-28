# Quantum Crossword

# Each square is: 1 qubit if is a letter, 26 qubits for the letter, 100 qubits for word across,
# 100 qubits for word down.

import dimod
import neal
from words import WORDS

# Define crossword width and height
SIZE = 9


def gen():
    qubo = {}

    # Sort words into their lengths
    sorted_words = {}
    for word in WORDS:
        length = len(word)
        if length >= 3:
            if sorted_words.get(length) is None:
                sorted_words[length] = []
            sorted_words[length].append(word)



if __name__ == '__main__':
    gen()
