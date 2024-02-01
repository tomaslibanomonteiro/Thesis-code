from pymoo.algorithms.moo.nsga3 import NSGA3
from pymoo.problems import get_problem
from pymoo.optimize import minimize
# import get_reference_directions
from pymoo.util.ref_dirs import get_reference_directions

# Define the problem
problem = get_problem("dtlz1", n_obj=4)

ref_dirs = get_reference_directions("das-dennis", 4, n_partitions=12)

# Define the algorithm
algorithm = NSGA3(ref_dirs=ref_dirs)

# Enable verbose output
algorithm.verbose = True

# Run the optimization
res = minimize(problem, algorithm)

# Print the results
print("Best solution found:")
print(res.X)
print("Objective values:")
print(res.F)