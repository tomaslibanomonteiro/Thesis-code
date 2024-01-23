from backend.get import get_problem, get_algorithm
from pymoo.optimize import minimize

# Define the problem
problem = get_problem("g1")

# Define the algorithm
algorithm = get_algorithm("cmaes")

# Optimize the problem
result = minimize(problem,
                  algorithm,
                  seed=1,
                  verbose=False)

# Print the optimal solution
print("Best solution found:", result.X)
print("Objective value:", result.F)
