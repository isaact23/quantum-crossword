# Quantum Crossword

# Each square is: 1 qubit if horizontal, 1 qubit if vertical, 100+ qubits for horizontal word, 100+ qubits for
# vertical word.

import dimod
import neal
from words import WORDS

# Crossword constants
CROSSWORD_SIZE = 8  # Width and height
WORD_LIMIT = 100  # Maximum number of words


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

            # Qubits for horizontal/vertical enabled
            qubits += 2

            # Qubits for each word
            qubits += word_counts_under[CROSSWORD_SIZE - i]
            qubits += word_counts_under[CROSSWORD_SIZE - j]

    qubo = gen_empty_qubo(qubits)

    # Constraints:

    # Up to one horizontal and one vertical word per square.
    # Words must be short enough to fit within the crossword bounds.
    for i in range(CROSSWORD_SIZE):
        for j in range(CROSSWORD_SIZE):
            q = qubit_offsets[i][j]

            # Horizontals
            y1 = q
            qubo[(y1, y1)] += 1
            row_word_count = word_counts_under[CROSSWORD_SIZE - j]
            for k in range(row_word_count):
                x = q + 2 + k
                qubo[(x, x)] += 1
                qubo[(y1, x)] -= 2
                for k2 in range(k + 1, row_word_count):
                    x2 = q + 2 + k2
                    qubo[(x, x2)] += 2

            # Verticals
            y2 = y1 + 1
            qubo[(y2, y2)] += 1
            col_word_count = word_counts_under[CROSSWORD_SIZE - i]
            for k in range(col_word_count):
                x = q + 2 + row_word_count + k
                qubo[(x, x)] += 1
                qubo[(y1, x)] -= 2
                for k2 in range(k + 1, col_word_count):
                    x2 = q + 2 + row_word_count + k2
                    qubo[(x, x2)] += 2

    # For horizontal words, ensure no overlap of other words.
    for i in range(CROSSWORD_SIZE):
        for j in range(CROSSWORD_SIZE):
            q = qubit_offsets[i][j]
            row_word_count = word_counts_under[CROSSWORD_SIZE - j]
            for k in range(row_word_count):
                x1 = q + 2 + k
                # TODO: Add function that allows us to 'ban' words if a qubit is enabled.


    print("QUBO generated.")
    print()

    # Solve QUBO
    result = neal.SimulatedAnnealingSampler().sample_qubo(Q=qubo, num_reads=1)

    print("QUBO solved.")
    print()

    # Generate crossword puzzle from result
    crossword_words_row = {}
    crossword_words_col = {}
    datum = result.first
    sample = datum.sample
    energy = datum.energy
    for i in range(CROSSWORD_SIZE):
        crossword_words_row[i] = {}
        crossword_words_col[i] = {}
        for j in range(CROSSWORD_SIZE):
            q = qubit_offsets[i][j] + 2
            crossword_words_row[i][j] = ''
            crossword_words_col[i][j] = ''

            # Find words associated with enabled qubits
            row_word_count = word_counts_under[CROSSWORD_SIZE - j]
            for k in range(row_word_count):
                if sample[q + k] == 1:
                    crossword_words_row[i][j] = word_list[k]
                    break
            col_word_count = word_counts_under[CROSSWORD_SIZE - i]
            for k in range(col_word_count):
                if sample[q + row_word_count + k] == 1:
                    crossword_words_col[i][j] = word_list[k]
                    break

    # Print results
    print("Rows:")
    for row in crossword_words_row:
        for col in crossword_words_row:
            word = crossword_words_row[row][col]
            print(f'[{word:{8}}] ', end='')
        print()
    print("Cols:")
    for row in crossword_words_col:
        for col in crossword_words_col:
            word = crossword_words_col[row][col]
            print(f'[{word:{8}}] ', end='')
        print()


if __name__ == '__main__':
    gen()
