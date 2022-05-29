# Quantum Crossword

# Each square is: 1 qubit if is a letter, 26 qubits for the letter, 100 qubits for word across,
# 100 qubits for word down, 2 qubits to allow either 0 or 1 horizontal or vertical words.

import dimod
import neal
from words import WORDS

# Crossword constants
CROSSWORD_SIZE = 6  # Width and height
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

    # Overwrite word list with sorted word array
    word_list = []
    for i in range(CROSSWORD_SIZE + 1):
        word_sublist = sorted_words.get(i)
        if word_sublist is not None:
            word_list += word_sublist

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
        for i in range(max_length + 1):
            word_counts_under[max_length] += word_counts.get(i)

    # Get number of qubits per square
    qubits = 0
    qubit_offsets = {}
    for i in range(CROSSWORD_SIZE):
        qubit_offsets[i] = {}
        for j in range(CROSSWORD_SIZE):
            qubit_offsets[i][j] = qubits

            # Letter / enabled / slack qubits
            qubits += 29

            # Qubits for each word
            qubits += word_counts_under.get(CROSSWORD_SIZE - i)
            qubits += word_counts_under.get(CROSSWORD_SIZE - j)

    qubo = gen_empty_qubo(qubits)

    # Constraints:

    # The more letters filled, the better the solution.
    for i in range(CROSSWORD_SIZE):
        for j in range(CROSSWORD_SIZE):
            q = qubit_offsets[i][j]
            qubo[(q, q)] -= 0.1

    # Letters must be part of a word.
    for i in range(CROSSWORD_SIZE):
        for j in range(CROSSWORD_SIZE):
            pass

    # There can be at most one letter per square.
    for i in range(CROSSWORD_SIZE):
        for j in range(CROSSWORD_SIZE):
            q = qubit_offsets[i][j]
            for k1 in range(26):
                q1 = q + k1 + 1
                qubo[(q1, q1)] -= 1
                for k2 in range(k1 + 1, 26):
                    q2 = q + k2 + 1
                    qubo[(q1, q2)] += 2

    # There can be at most one horizontal word per square.
    for i in range(CROSSWORD_SIZE):
        for j in range(CROSSWORD_SIZE):
            q = qubit_offsets[i][j]
            word_count_row = word_counts_under[CROSSWORD_SIZE - j]
            word_count_col = word_counts_under[CROSSWORD_SIZE - i]
            y = q + 27 + word_count_row + word_count_col
            qubo[(y, y)] -= 1
            for k1 in range(word_count_row):
                q1 = q + 27 + k1
                qubo[(q1, q1)] -= 1
                qubo[(q1, y)] += 2
                for k2 in range(k1 + 1, word_count_row):
                    q2 = q + 27 + k2
                    qubo[(q1, q2)] += 2

    # There can be at most one vertical word per square.
    for i in range(CROSSWORD_SIZE):
        for j in range(CROSSWORD_SIZE):
            q = qubit_offsets[i][j]
            word_count_row = word_counts_under[CROSSWORD_SIZE - j]
            word_count_col = word_counts_under[CROSSWORD_SIZE - i]
            y = q + 27 + word_count_row + word_count_col + 1
            qubo[(y, y)] -= 1
            for k1 in range(word_count_col):
                q1 = q + 27 + k1 + word_count_row
                qubo[(q1, q1)] -= 1
                qubo[(q1, y)] += 2
                for k2 in range(k1 + 1, word_count_col):
                    q2 = q + 27 + k2 + word_count_row
                    qubo[(q1, q2)] += 2

    # If there is a horizontal word, the squares before and after must be empty.
    # If there is a horizontal word, all letters must be present and open.
    for i in range(CROSSWORD_SIZE):
        for j in range(CROSSWORD_SIZE):
            q = qubit_offsets[i][j]
            word_count_row = word_counts_under[CROSSWORD_SIZE - j]
            for k in range(word_count_row):
                q1 = q + 27 + k  # Horizontal word enabled
                word = word_list[k]
                if j > 0:
                    q2 = qubit_offsets[i][j - 1]  # Letter enabled
                    qubo[(q2, q1)] += 1
                if j < CROSSWORD_SIZE - len(word):
                    q2 = qubit_offsets[i][j + len(word)]  # Letter enabled
                    qubo[(q1, q2)] += 1
                for l in range(len(word)):
                    q2 = qubit_offsets[i][j + l] + ord(word[l]) - 96  # Letter id
                    qubo[(q1, q1)] += 1
                    if q1 > q2:
                        qubo[(q2, q1)] -= 1
                    else:
                        qubo[(q1, q2)] -= 1


    # If there is a vertical word, the squares below and above must be empty.
    # If there is a vertical word, all letters must be present and open.

    # Solve QUBO
    result = neal.SimulatedAnnealingSampler().sample_qubo(Q=qubo, num_reads=1)

    # Generate crossword puzzle from result
    crossword = {}
    crossword_words_row = {}
    crossword_words_col = {}
    datum = result.first
    sample = datum.sample
    energy = datum.energy
    for i in range(CROSSWORD_SIZE):
        crossword[i] = {}
        crossword_words_row[i] = {}
        crossword_words_col[i] = {}
        for j in range(CROSSWORD_SIZE):
            offset = qubit_offsets[i][j]
            crossword[i][j] = '-'
            crossword_words_row[i][j] = ''
            crossword_words_col[i][j] = ''
            if sample[offset] == 1:
                for k in range(26):
                    if sample[offset + k + 1] == 1:
                        crossword[i][j] = chr(k + 97)
                        break
            row_word_count = word_counts_under[CROSSWORD_SIZE - j]
            for k in range(row_word_count):
                if sample[offset + 27 + k] == 1:
                    crossword_words_row[i][j] = word_list[k]
                    break
            col_word_count = word_counts_under[CROSSWORD_SIZE - i]
            for k in range(col_word_count):
                if sample[offset + 27 + row_word_count + k] == 1:
                    crossword_words_col[i][j] = word_list[k]
                    break

    # Print results
    for row in crossword:
        for col in crossword[row]:
            letter = crossword[row][col]
            print(f'[{letter}] ', end='')
        print()

    for row in crossword_words_row:
        for col in crossword_words_row:
            word = crossword_words_row[row][col]
            print(f'[{word:{8}}] ', end='')
        print()

if __name__ == '__main__':
    gen()
