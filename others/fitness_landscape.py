import numpy as np
from pymoo.problems import get_problem
from pymoo.visualization.scatter import Scatter
from pymoo.visualization.fitness_landscape import FitnessLandscape

import matplotlib.pyplot as plt

# Create the Himmelblau's problem
problem = get_problem("Himmelblau",xl=-3, xu=3)

# Create the fitness landscape object
fl = FitnessLandscape(problem, "surface")
fl.show()