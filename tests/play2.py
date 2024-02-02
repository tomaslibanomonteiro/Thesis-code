from pymoo.factory import get_problem
from pymoo.visualization.fitness_landscape import FitnessLandscape
import numpy as np
# Define the problem
problem = get_problem("ackley")

args = dict(cmap="summer", rstride=1, cstride=1, alpha=0.2)
plot = FitnessLandscape(problem, 'surface', 50, kwargs_surface=args)

# plot a big red dot at 0,0,0
plot.do()
point = np.array([0, 0, 12])
plot.ax.scatter(*point, color='red', s=100)
plot.show()