import pandas as pd
from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.factory import get_problem
from pymoo.optimize import minimize

# define the problem
problem = get_problem("ackley", n_var=10)

# define the GA algorithm
algorithm = GA(pop_size=100, eliminate_duplicates=True)

# create a DataFrame to store the best solution of each generation
best_solutions = pd.DataFrame(columns=["gen", "best_obj", "best_var"])

# define a callback function to save the best solution of each generation
def save_best_solution(algorithm):
    best_idx = algorithm.pop.get("F").argmin()
    best_obj = algorithm.pop.get("F")[best_idx]
    best_var = algorithm.pop.get("X")[best_idx]
    best_solutions.loc[len(algorithm.callback.data["gen"]) - 1] = [len(algorithm.callback.data["gen"]) - 1, best_obj, best_var]

# run the optimization
res = minimize(problem,
               algorithm,
               ('n_gen', 50),
               seed=1,
               callback=save_best_solution)

# print the best solution found
print("Best solution: ", res.X)
print("Best objective value: ", res.F)

# print the DataFrame of best solutions
print(best_solutions)