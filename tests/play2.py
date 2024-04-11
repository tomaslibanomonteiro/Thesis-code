import os
import csv

# Find a unique file name
i = 1
while os.path.exists(f"output{i}.csv"):
    i += 1

from pymoo.algorithms.moo.nsga3 import NSGA3
from pymoo.algorithms.moo.moead import MOEAD
from pymoo.util.ref_dirs import get_reference_directions
from pymoo.termination import get_termination
from pymoo.problems import get_problem
from pymoo.optimize import minimize
from pymoo.visualization.scatter import Scatter
from pymoo.indicators.igd import IGD
from numpy import median, min, max
# Define the algorithms
from pymoo.decomposition.tchebicheff import Tchebicheff
from pymoo.decomposition.pbi import PBI
from pymoo.operators.mutation.pm import PM


n_gens = [250, 1000, 600]

# Define the reference directions
ref_dirs = get_reference_directions("das-dennis", 3, n_partitions=12)

# Define the problem
problems = [ 
    ('dtlz2', get_problem("dtlz2", ref_dirs=ref_dirs)),
    ('dtlz3', get_problem("dtlz3", ref_dirs=ref_dirs)),
    ('dtlz4', get_problem("dtlz4", ref_dirs=ref_dirs)),
            ]

permutation=PM(prob=1/10)

algorithms = [
    ('NSGA3', NSGA3(ref_dirs=ref_dirs, permutation=permutation)), 
    ('MOEAD - PBI', MOEAD(ref_dirs=ref_dirs, decomposition=PBI(), permutation=permutation)),
    ('MOEAD - Tchebicheff', MOEAD(ref_dirs=ref_dirs, decomposition=Tchebicheff(), permutation=permutation))
]

# Define the seeds
seeds = [1, 2, 3]


# Open the unique file in write mode
with open(f'output{i}.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    
    # Write the header
    writer.writerow(["Problem", "Algorithm", "Best IGD", "Worst IGD", "Median IGD"])

    for prob, n_gen in zip(problems, n_gens):
        print(f"Problem: {prob[0]}")
        igd_calc = IGD(prob[1].pareto_front())
        
        # Define the termination criterion
        # For each algorithm
        for algo in algorithms:
            print(f"Algorithm: {algo[0]}")
            
            # Define a list to store the IGD values
            igd_values = []

            # For each seed
            for seed in seeds:
                print(f"Seed: {seed}")

                # Perform the optimization
                res = minimize(prob[1],
                            algo[1],
                            get_termination("n_gen", n_gen),
                            seed=seed,
                            verbose=False)

                # Get the objective values
                F = res.F

                # Calculate the IGD value and add it to the list
                igd_values.append(igd_calc.do(F))

            # Calculate the best, worst, and median IGD values
            best_igd = min(igd_values)
            worst_igd = max(igd_values)
            median_igd = median(igd_values)

            print(f"Best IGD: {best_igd:.4e}")
            print(f"Worst IGD: {worst_igd:.4e}")
            print(f"Median IGD: {median_igd:.4e}")
            
            # Write the values to the file in a table-like manner
            writer.writerow([prob[0], algo[0], best_igd, worst_igd, median_igd])