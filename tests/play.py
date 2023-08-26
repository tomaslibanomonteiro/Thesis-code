# import pandas as pd
# from pymoo.algorithms.soo.nonconvex.ga import GA
# from pymoo.factory import get_problem
# from pymoo.optimize import minimize

# # define the problem
# problem = get_problem("ackley", n_var=10)

# # define the GA algorithm
# algorithm = GA(pop_size=100, eliminate_duplicates=True)

# # create a DataFrame to store the best solution of each generation
# best_solutions = pd.DataFrame(columns=["gen", "best_obj", "best_var"])

# # define a callback function to save the best solution of each generation
# def save_best_solution(algorithm):
#     best_idx = algorithm.pop.get("F").argmin()
#     best_obj = algorithm.pop.get("F")[best_idx]
#     best_var = algorithm.pop.get("X")[best_idx]
#     best_solutions.loc[len(algorithm.callback.data["gen"]) - 1] = [len(algorithm.callback.data["gen"]) - 1, best_obj, best_var]

# # run the optimization
# res = minimize(problem,
#                algorithm,
#                ('n_gen', 50),
#                seed=1,
#                callback=save_best_solution)

# # print the best solution found
# print("Best solution: ", res.X)
# print("Best objective value: ", res.F)

# # print the DataFrame of best solutions
# print(best_solutions)

import matplotlib.pyplot as plt

# create some sample data
x = [1, 2, 3, 4, 5]
y1 = [10, 20, 30, 40, 50]
y2 = [10000, 20000, 30000, 40000, 50000]

# create the first plot
fig, ax1 = plt.subplots()
ax1.plot(x, y1, 'b-')
ax1.set_xlabel('X-axis (km)')
ax1.set_ylabel('Y-axis (km)', color='b')

# create the second plot
ax2 = ax1.twinx()
ax2.plot(x, y2, 'r-')
ax2.set_ylabel('Y-axis (m)', color='r')

# show the plot
plt.show()