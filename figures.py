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

FOLDER = "thesis_figures/"

def aucley():
    problem = get_problem("ackley", n_var=2, a=20, b=1/5, c=2 * np.pi)

    FitnessLandscape(problem, angle=(45, 45), _type="surface").save(FOLDER + 'ackley_surface.png')

    FitnessLandscape(problem, _type="contour", colorbar=True).save(FOLDER + 'ackley_contour.png')

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

    from pymoo.problems.single.traveling_salesman import visualize
    fig, ax = plt.subplots()
    visualize(problem, res.X, fig, ax)
    fig.savefig(FOLDER + 'tsp.png')

def Himmelblau():
    problem = get_problem("himmelblau")

    FitnessLandscape(problem, angle=(45, 45), _type="surface").save(FOLDER + 'himmelblau_surface.png')

    FitnessLandscape(problem, _type="contour", colorbar=True).save(FOLDER + 'himmelblau_contour.png')   

def Rastrigin():
    problem = get_problem("rastrigin", n_var=2)

    FitnessLandscape(problem, angle=(45, 45), _type="surface").save(FOLDER + 'rastrigin_surface.png')

    FitnessLandscape(problem, _type="contour", colorbar=True).save(FOLDER + 'rastrigin_contour.png')

def Rosenbrock():
    problem = get_problem("rosenbrock", n_var=2)

    FitnessLandscape(problem, angle=(45, 45), _type="surface").save(FOLDER + 'rosenbrock_surface.png')

    FitnessLandscape(problem, _type="contour", colorbar=True).save(FOLDER + 'rosenbrock_contour.png')

def ZDT(zdt=1):

    problem = get_problem("zdt" + str(zdt))
    plot(problem.pareto_front(), no_fill=True)
    
def main():
    ZDT(3)

if __name__ == '__main__':
    main()