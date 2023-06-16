from backend.run import Run
from backend.get_defaults import Defaults

import pickle
from pymoo.optimize import minimize
from backend.get import get_problem, get_algorithm, get_termination, get_performance_indicator, get_reference_directions
from pymoo.algorithms.moo.ctaea import CTAEA
# import reference_directions das-dennis
from pymoo.util.reference_direction import UniformReferenceDirectionFactory

problem = get_problem("c1dtlz1", None, 3, k=5)

ref_dirs = UniformReferenceDirectionFactory(n_dim=3, n_partitions=12)

# ref_dirs = get_reference_directions("das-dennis", 3, n_partitions=12)

# create the algorithm object
# algorithm = get_algorithm("ctaea", ref_dirs=ref_dirs)
# create the algorithm object
algorithm = CTAEA(ref_dirs=ref_dirs)


# execute the optimization
res = minimize(problem,
               algorithm,
               ('n_gen', 600),
               seed=1,
               verbose=True
               )

# prob = get_problem("c1dtlz1", None , 3, k=5)
# n_obj = prob.n_obj
# ref_dirs = get_reference_directions("das-dennis", 3, n_partitions=12)

# # ref_dirs = get_reference_directions("das-dennis", n_dim = n_obj, n_partitions = n_obj*5)
# algo = get_algorithm("nsga3", ref_dirs=ref_dirs)

# res = minimize( algorithm=algo,
#                 problem=prob,
#                 termination=('n_gen', 2))


# with open('ga.pickle', 'rb') as f:
#     my_ga = pickle.load(f)

# res = minimize( algorithm=my_ga,
#                 problem=prob,
#                 termination=('n_gen', 2))

# print("\n\ndone\n\n")
