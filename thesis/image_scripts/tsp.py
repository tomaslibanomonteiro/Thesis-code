import numpy as np
import matplotlib.pyplot as plt
from pymoo.problems import get_problem
from pymoo.visualization.fitness_landscape import FitnessLandscape
from pymoo.core.repair import Repair
from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.optimize import minimize
from pymoo.problems.single.traveling_salesman import create_random_tsp_problem
from pymoo.operators.sampling.rnd import PermutationRandomSampling
from pymoo.operators.crossover.ox import OrderCrossover
from pymoo.operators.mutation.inversion import InversionMutation
from pymoo.termination.default import DefaultSingleObjectiveTermination
from pymoo.util.plotting import plot

def visualize(problem, x, fig=None, ax=None, show=True, label=True):
    with plt.style.context('ggplot'):

        if fig is None or ax is None:
            fig, ax = plt.subplots()

        # plot cities using scatter plot
        ax.scatter(problem.cities[:, 0], problem.cities[:, 1], s=250)
        if label:
            # annotate cities
            for i, c in enumerate(problem.cities):
                ax.annotate(str(i), xy=c, fontsize=10, ha="center", va="center", color="white")

        # plot the line on the path
        for i in range(len(x)):
            current = x[i]
            next_ = x[(i + 1) % len(x)]
            ax.plot(problem.cities[[current, next_], 0], problem.cities[[current, next_], 1], '--', color="grey")

        fig.suptitle("Route length: %.4f" % problem.get_route_length(x))

        if show:
            fig.show()

def TSP():
    
    class StartFromZeroRepair(Repair):

        def _do(self, problem, X, **kwargs):
            I = np.where(X == 0)[1]

            for k in range(len(X)):
                i = I[k]
                X[k] = np.concatenate([X[k, i:], X[k, :i]])

            return X

    problem = create_random_tsp_problem(30, 100, seed=3)

    algorithm = GA(
        pop_size=20,
        sampling=PermutationRandomSampling(),
        mutation=InversionMutation(),
        crossover=OrderCrossover(),
        repair=StartFromZeroRepair(),
        eliminate_duplicates=True
    )

    # if the algorithm did not improve the last 200 generations then it will terminate (and disable the max generations)
    termination = DefaultSingleObjectiveTermination(period=200, n_max_gen=np.inf)

    res = minimize(
        problem,
        algorithm,
        termination,
        seed=1,
    )
    fig, ax = plt.subplots()
    visualize(problem, res.X, fig, ax)
    fig.savefig('tsp.png')

TSP()