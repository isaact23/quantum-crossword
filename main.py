# Quantum Crossword

# Each square is: 1 qubit if is a letter, 26 qubits for the letter, 100 qubits for word across,
# 100 qubits for word down.

import dimod
import neal
from words import WORDS

# Crossword constants
CROSSWORD_SIZE = 5  # Width and height
WORD_LIMIT = 50  # Maximum number of words


# Sort words into their lengths
def sort_words(words) -> dict:
    sorted_words = {}
    for word in words:
        length = len(word)
        if length >= 3:
            if sorted_words.get(length) is None:
                sorted_words[length] = []
            sorted_words[length].append(word)
    return sorted_words


# Generate empty QUBO
def gen_empty_qubo(size: int) -> dict:
    qubo = {}
    for i in range(size):
        for j in range(i, size):
            qubo[(i, j)] = 0

    return qubo


def gen():
    # Reduce word bank size
    if 0 <= WORD_LIMIT <= len(WORDS):
        word_list = WORDS[0:WORD_LIMIT]
    else:
        word_list = WORDS

    # Sort words into their lengths
    sorted_words = sort_words(word_list)

    # Get total number of words of each length
    word_counts = {}
    for i in range(CROSSWORD_SIZE):
        word_counts[i] = 0
    for length in sorted_words:
        word_counts[length] = len(sorted_words[length])

    # Get total number of words under each length
    word_counts_under = {}
    for i in range(CROSSWORD_SIZE):
        word_counts_under[i] = 0
    for max_length in word_counts:
        word_counts_under[max_length] = 0
        for i in range(3, max_length + 1):
            word_counts_under[max_length] += word_counts.get(i)

    # Get number of qubits per square
    qubits = 0
    qubit_offsets = {}
    for i in range(CROSSWORD_SIZE):
        qubit_offsets[i] = {}
        for j in range(CROSSWORD_SIZE):
            qubit_offsets[i][j] = qubits

            # Letter / enabled qubits
            qubits += 27

            # Qubits for each word
            qubits += word_counts_under.get(CROSSWORD_SIZE - i)
            qubits += word_counts_under.get(CROSSWORD_SIZE - j)

    qubo = gen_empty_qubo(qubits)

    # Constraints:

    # There can be at most one letter per square.
    # There can be at most one horizontal word per square.
    # There can be at most one vertical word per square.
    # If there is a horizontal word, the squares before and after must be empty.
    # If there is a vertical word, the squares below and above must be empty.
    # If there is a horizontal word, all letters must be present.
    # If there is a vertical word, all letters must be present.
    # If a square is not occupied by a word, it must be blank.

    # Solve QUBO
    result = neal.SimulatedAnnealingSampler().sample_qubo(Q=qubo, num_reads=5)

    # Generate crossword puzzle from result
    crossword = {}
    datum = result.first
    sample = datum.sample
    energy = datum.energy
    for i in range(CROSSWORD_SIZE):
        crossword[i] = {}
        for j in range(CROSSWORD_SIZE):
            offset = qubit_offsets[i][j]
            crossword[i][j] = '-'
            if sample[offset] == 1:
                for k in range(26):
                    if sample[offset + k + 1] == 1:
                        crossword[i][j] = chr(k + 97)
                        break
    for row in crossword:
        for col in crossword[row]:
            letter = crossword[row][col]
            print(f'[{letter}] ', end='')
        print()


if __name__ == '__main__':
    gen()
