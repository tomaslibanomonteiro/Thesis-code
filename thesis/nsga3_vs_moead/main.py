UNIQUE_FILE = False

import os
import csv

# Find a unique file name
if UNIQUE_FILE:
    i = 1
    while os.path.exists(f"output{i}.csv"):
        i += 1
else:
    i = ""

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

SEEDS = 3

n_gens = [400,
        #   1000,
        #   1000
          ]

n_var, n_obj = 12, 3 # 14, 5
# Define the problem
problems = [ 
    ('sdtlz1', get_problem("sdtlz1", n_var=n_var, n_obj=n_obj, scale_factor=1000)),
    # ('dtlz3', get_problem("dtlz3", n_var=n_var, n_obj=n_obj)),
    # ('dtlz4', get_problem("dtlz4", n_var=n_var, n_obj=n_obj)),
]

# Define the reference directions
ref_dirs = get_reference_directions("das-dennis", n_obj, n_partitions=12) # 6

# Define the mutation operator
mutation=PM(prob=1/n_var, eta=20)

algorithms = [
    ('NSGA3', NSGA3(ref_dirs=ref_dirs, mutation=mutation)), 
    ('MOEAD - PBI', MOEAD(ref_dirs=ref_dirs, decomposition=PBI(), mutation=mutation)),
    # ('MOEAD - Tchebicheff', MOEAD(ref_dirs=ref_dirs, decomposition=Tchebicheff(), mutation=mutation))
]

# Open the unique file in write mode
with open(f'output{i}.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    
    # Write the header
    writer.writerow(["Problem", "Algorithm", "Best IGD (O)", "Median IGD (O)", "Worst IGD (O)", "Best IGD (P)", "Median IGD (P)", "Worst IGD (P)"])

    for prob, n_gen in zip(problems, n_gens):
        print(f"Problem: {prob[0]}")
        igd_calc = IGD(prob[1].pareto_front(ref_dirs=ref_dirs))
        
        # Define the termination criterion
        # For each algorithm
        for algo in algorithms:
            print(f"Algorithm: {algo[0]}")
            
            # Define a list to store the IGD values
            igd_opt_values = []
            igd_pop_values = []
            
            # For each seed
            for seed in range(SEEDS):
                print(f"Seed: {seed}")

                # Perform the optimization
                res = minimize(prob[1],
                            algo[1],
                            termination=get_termination("n_gen", n_gen),
                            seed=seed)

                # Get the objective values
                import numpy as np
                alg = res.algorithm
                
                # algo opt values
                feas = np.where(alg.opt.get("feasible"))[0]
                algo_opt = alg.opt.get("F")[feas]
                igd_algo_opt = igd_calc.do(algo_opt)
                igd_opt_values.append(igd_algo_opt)

                # pop opt values
                feas = np.where(alg.pop.get("feasible"))[0]
                algo_pop = alg.pop.get("F")[feas]
                # get the non dominated solutions
                # from pymoo.util.nds.non_dominated_sorting import NonDominatedSorting
                # non_dom_pop_idx = NonDominatedSorting().do(algo_pop, only_non_dominated_front=True)
                # non_dom_pop = algo_pop[non_dom_pop_idx] 
                # igd_algo_pop = igd_calc.do(non_dom_pop)
                igd_pop_values.append(igd_calc.do(algo_pop))
                
            # Calculate the best, worst, and median IGD values for opt
            best_igd_opt = min(igd_opt_values)
            worst_igd_opt = max(igd_opt_values)
            median_igd_opt = median(igd_opt_values)

            # Calculate the best, worst, and median IGD values for pop
            best_igd_pop = min(igd_pop_values)
            worst_igd_pop = max(igd_pop_values)
            median_igd_pop = median(igd_pop_values)

            print(f"  Best IGD for pop/opt (Equal? {best_igd_pop == best_igd_opt}): {best_igd_pop:.4e}/{best_igd_opt:.4e}")
            print(f"Median IGD for pop/opt (Equal? {median_igd_pop == median_igd_opt}): {median_igd_pop:.4e}/{median_igd_opt:.4e}")
            print(f" Worst IGD for pop/opt (Equal? {worst_igd_pop == worst_igd_opt}): {worst_igd_pop:.4e}/{worst_igd_opt:.4e}")

            # Write the values to the file in a table-like manner
            writer.writerow([prob[0], algo[0], 
                             "{:.2e}".format(best_igd_opt), "{:.2e}".format(median_igd_opt), "{:.2e}".format(worst_igd_opt),
                             "{:.2e}".format(best_igd_pop), "{:.2e}".format(median_igd_pop), "{:.2e}".format(worst_igd_pop)])