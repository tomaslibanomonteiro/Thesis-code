from backend.run import Run
from backend.get_defaults import Defaults

import pickle
from pymoo.optimize import minimize
from backend.get import get_problem, get_algorithm, get_termination, get_performance_indicator
    

prob = get_problem("ackley")
algo = get_algorithm("ga")

res = minimize( algorithm=algo,
                problem=prob,
                termination=('n_gen', 2))

# defaults = Defaults()
# algo_list = defaults.algo
# algo_row = []
# for algo_row in algo_list:
#     if algo_row[0][1] == "ga":
#         break
# algo_row = [algo_row[1]] + algo_row[5:7]

# algo_dict = dict(algo_row)

# algo2 = get_algorithm("ga", **algo_dict)
# algo2 = run_object.run_args[0].algo_object

# res = minimize( algorithm=algo2,
#                 problem=prob,
#                 termination=('n_gen', 2))

with open('ga.pickle', 'rb') as f:
    my_ga = pickle.load(f)

res = minimize( algorithm=my_ga,
                problem=prob,
                termination=('n_gen', 2))

print("\n\ndone\n\n")
