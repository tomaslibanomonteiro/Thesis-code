from pymoo.problems import get_problem
from pymoo.visualization.scatter import Scatter

# get the dtlz1 problem
problem = get_problem("dtlz1")

# get the Pareto front of the problem
pareto_front = problem.pareto_front()

# create a scatter plot of the Pareto front
scatter = Scatter(title="DTLZ1 Pareto Front")
scatter.add(pareto_front)
scatter.show()