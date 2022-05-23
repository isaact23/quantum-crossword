# Quantum Crossword

import dimod
from dwave.system import LeapHybridCQMSampler

def example():
    # 10 qubits
    x = [dimod.Binary(f'x_{i}') for i in range(10)]
    cqm = dimod.ConstrainedQuadraticModel()

    # Objective: as many 1s as possible.
    cqm.set_objective(-sum(x))

    # Constraint: no more than 3 1s.
    cqm.add_constraint(sum(x) <= 3, label='max_sum')

    # Solve
    solver = LeapHybridCQMSampler()
    result = solver.sample_cqm(cqm)
    print(result)


if __name__ == '__main__':
    example()
