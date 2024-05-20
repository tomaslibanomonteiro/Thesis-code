import numpy as np

################################################################################################################################
#####################################################    PROBLEMS    ###########################################################
################################################################################################################################

from pymoo.problems.single.knapsack import Knapsack
from pymoo.problems.many.dtlz import ScaledProblem
from pymoo.problems.many.dtlz import DTLZ1, DTLZ2, DTLZ3, DTLZ4, DTLZ5, DTLZ6, DTLZ7

class KnapsackMulti(Knapsack):
    def __init__(self, *args):
        super().__init__(*args)

    def _evaluate(self, x, out, *args, **kwargs):
        f1 = - np.sum(self.P * x, axis=1)
        f2 = np.sum(x, axis=1)

        out["F"] = np.column_stack([f1, f2])
        out["G"] = (np.sum(self.W * x, axis=1) - self.C)

class RandomKnapsackSingle(Knapsack):
    def __init__(self, n_vars=3, seed=1):
        np.random.seed(seed)
        P = np.random.randint(1, 100, size=n_vars)
        W = np.random.randint(1, 100, size=n_vars)
        C = int(np.sum(W) / 10)
        super().__init__(n_vars, W, P, C)

class RandomKnapsackMulti(KnapsackMulti):
    def __init__(self, n_vars=3, seed=1):
        np.random.seed(seed)
        P = np.random.randint(1, 100, size=n_vars)
        W = np.random.randint(1, 100, size=n_vars)
        C = int(np.sum(W) / 10)
        super().__init__(n_vars, W, P, C)

class ScaledDTLZ(ScaledProblem):
    def __init__(self, dtlz=1, n_obj=10, n_var=3, scale_factor=10, **kwargs):
        if dtlz == 1:
            problem = DTLZ1(n_var=n_var, n_obj=n_obj)
        elif dtlz == 2:
            problem = DTLZ2(n_var=n_var, n_obj=n_obj)
        elif dtlz == 3:
            problem = DTLZ3(n_var=n_var, n_obj=n_obj)
        elif dtlz == 4:
            problem = DTLZ4(n_var=n_var, n_obj=n_obj)
        elif dtlz == 5:
            problem = DTLZ5(n_var=n_var, n_obj=n_obj)
        elif dtlz == 6:
            problem = DTLZ6(n_var=n_var, n_obj=n_obj)
        elif dtlz == 7:
            problem = DTLZ7(n_var=n_var, n_obj=n_obj)
        else:
            raise ValueError("dtlz must be between 1 and 7")
        
        super().__init__(problem, scale_factor=scale_factor, **kwargs)

import pymoo.gradient.toolbox as anp
from pymoo.problems.single import Problem

class RastriginExplicitLimits(Problem):
    def __init__(self, n_var=2, A=10.0, xl=-5, xu=5, **kwargs):
        super().__init__(n_var=n_var, n_obj=1, xl=xl, xu=xu, vtype=float, **kwargs)
        self.A = A

    def _evaluate(self, x, out, *args, **kwargs):
        z = anp.power(x, 2) - self.A * anp.cos(2 * anp.pi * x)
        out["F"] = self.A * self.n_var + anp.sum(z, axis=1)

    def _calc_pareto_front(self):
        return 0.0

    def _calc_pareto_set(self):
        return np.full(self.n_var, 0)

class RosenbrockExplicitLimits(Problem):
    def __init__(self, n_var=2, xl=-2.048, xu=2.048, **kwargs):
        super().__init__(n_var=n_var, n_obj=1, n_ieq_constr=0, xl=xl, xu=xu, vtype=float, **kwargs)

    def _evaluate(self, x, out, *args, **kwargs):
        l = []
        for i in range(x.shape[1] - 1):
            val = 100 * (x[:, i + 1] - x[:, i] ** 2) ** 2 + (1 - x[:, i]) ** 2
            l.append(val)
        out["F"] = anp.sum(anp.column_stack(l), axis=1)

    def _calc_pareto_front(self):
        return 0.0

    def _calc_pareto_set(self):
        return np.full(self.n_var, 1.0)
    
class GriewankExplicitLimits(Problem):
    def __init__(self, n_var=2, xl=-600, xu=600, **kwargs):
        super().__init__(n_var=n_var, n_obj=1, xl=xl, xu=xu, vtype=float, **kwargs)

    def _evaluate(self, x, out, *args, **kwargs):
        out["F"] = 1 + 1 / 4000 * anp.sum(anp.power(x, 2), axis=1) \
                  - anp.prod(anp.cos(x / anp.sqrt(anp.arange(1, x.shape[1] + 1))), axis=1)

    def _calc_pareto_front(self):
        return 0

    def _calc_pareto_set(self):
        return np.full(self.n_var, 0)

    
################################################################################################################################
#####################################################   ALGORITHMS   ###########################################################
################################################################################################################################
        
from pymoo.algorithms.moo.ctaea import RestrictedMating, comp_by_cv_dom_then_random
from pymoo.algorithms.moo.nsga2 import binary_tournament
from pymoo.algorithms.moo.nsga3 import comp_by_cv_then_random
from pymoo.algorithms.moo.unsga3 import comp_by_rank_and_ref_line_dist
from pymoo.algorithms.soo.nonconvex.ga import comp_by_cv_and_fitness
from pymoo.operators.selection.tournament import TournamentSelection

class TournamentByCVAndFitness(TournamentSelection):
    def __init__(self, pressure=2, **kwargs):
        super().__init__(func_comp=comp_by_cv_and_fitness, pressure=pressure, **kwargs) 
    
class RestrictedMatingCTAEA(RestrictedMating):
    def __init__(self, pressure=2, **kwargs):
        super().__init__(func_comp=comp_by_cv_dom_then_random, pressure=pressure, **kwargs)
        
class BinaryTournament(TournamentSelection):
    def __init__(self, pressure=2, **kwargs):
        super().__init__(func_comp=binary_tournament, pressure=pressure, **kwargs) 

class TournamentByCVThenRandom(TournamentSelection):
    def __init__(self, pressure=2, **kwargs):
        super().__init__(func_comp=comp_by_cv_then_random, pressure=pressure, **kwargs) 
        
class TournamentByRankAndRefLineDist(TournamentSelection):
    def __init__(self, pressure=2, **kwargs):
        super().__init__(func_comp=comp_by_rank_and_ref_line_dist, pressure=pressure, **kwargs) 

################################################################################################################################
#####################################################   INDICATORS   ###########################################################
################################################################################################################################


### Single-objective indicators
class BestFitness():
        """used in the case of single-objective optimization,just for code compatibility. 
        Only returns the input, because it should consist of only the best solution"""
        def __init__(self):
            pass
        
        def do(self, opt_feas, **kwargs):
            return opt_feas[0][0]
class AvgPopFitness():
    def __init__(self):
        pass
    
    def do(self, opt_feas, pop, **kwargs):
        return np.mean(pop) if len(pop) > 0 else np.nan

class MinusGoalAchieved():
    def __init__(self, goal=1.1):
        self.goal = goal
    
    def do(self, opt_feas):
        return -1 if len(opt_feas) > 0 and opt_feas[0][0] <= self.goal else 0
        
class EvalsOnGoal():
    def __init__(self, goal=1.1):
        self.goal = goal
        self.n_eval = 0
        self.evals_on_goal = np.nan
        
    def do(self, opt_feas, n_eval, **kwargs):
        
        # if it is next seed, n_evals will be lower, so evals_on_goal is set to nan again
        if n_eval <= self.n_eval:
            self.evals_on_goal = np.nan
        self.n_eval = n_eval
            
        if np.isnan(self.evals_on_goal) and len(opt_feas) > 0 and opt_feas[0][0] <= self.goal:            
            self.evals_on_goal = n_eval 
        return self.evals_on_goal

### Multi-objective indicators

from pymoo.indicators.hv import Hypervolume

class minusHypervolume(Hypervolume):
    def _do(self, F):
        return - super()._do(F)

################################################################################################################################
#####################################################   TERMINATIONS   #########################################################
################################################################################################################################

from pymoo.core.termination import Termination

class StaledBestTermination(Termination):
    def __init__(self, stale_limit=2000):
        super().__init__()
        self.stale_limit = stale_limit
        self.best = np.inf
        self.stale_start = 0

    def _update(self, algo):
        opt_feas_idx = np.where(algo.opt.get("feasible"))[0]
        opt = algo.opt.get("F")
        opt_feas = opt[opt_feas_idx]
        
        if len(opt_feas) > 0 and opt_feas[0][0] < self.best:
            self.stale_start = algo.evaluator.n_eval
            self.best = opt_feas[0][0]
        
        return 1 if algo.evaluator.n_eval - self.stale_start > self.stale_limit else 0
    
class MinFitnessTermination(Termination):
    def __init__(self, f_threshold = 1.1):
        super().__init__()
        self.f_threshold = f_threshold

    def _update(self, algo):
        opt_feas_idx = np.where(algo.opt.get("feasible"))[0]
        opt = algo.opt.get("F")
        opt_feas = opt[opt_feas_idx]
        
        return 1 if len(opt_feas) > 0 and opt_feas[0][0] <= self.f_threshold else 0

################################################################################################################################
#######################################################    PLOTTING   ###########################################################
################################################################################################################################

from pymoo.visualization.scatter import Plot
from pymoo.visualization.fitness_landscape import FitnessLandscape
from pymoo.util.misc import all_combinations
from utils.utils import MyMessageBox
class MyFitnessLandscape(Plot):
    def __init__(self,
                 problem,
                 n_samples_2D=500,
                 n_samples_3D=30,
                 colorbar=False,
                 contour_levels=30,
                 max_n_solutions=100,
                 show_best_sol=True,
                 zoom_on_solutions=False,
                 labels=True,
                 **kwargs):

        super().__init__(**kwargs)
        self.problem = problem
        self.n_samples_2D = n_samples_2D
        self.n_samples_3D = n_samples_3D
        self.colorbar = colorbar
        self.sets_of_points = []
        self.sets_labels = []
        self.contour_levels = contour_levels
        self.max_n_solutions = max_n_solutions
        self.show_best_sol = show_best_sol
        self.zoom_on_solutions = zoom_on_solutions

        self.kwargs_surface = dict(cmap="summer", rstride=1, cstride=1, alpha=0.2)
        self.kwargs_contour = dict(linestyles="solid", offset=-1)
        self.kwargs_contour_labels = None

    def _do(self):

        problem, sets_of_points = self.problem, self.sets_of_points

        # find the min and max values of the decision variable between the sets of points
        if self.zoom_on_solutions and sets_of_points != []:
            x_min = min([min(points[:, 0]) for points in sets_of_points])
            x_max = max([max(points[:, 0]) for points in sets_of_points])
        else:
            x_min, x_max = problem.xl[0], problem.xu[0]

        if problem.n_var == 1 and problem.n_obj == 1:

            self.init_figure()
            X = np.linspace(x_min, x_max, self.n_samples_2D)[:, None]
            Z = problem.evaluate(X, return_values_of=["F"])
            self.ax.plot(X, Z, alpha=0.2)
            self.ax.set_xlabel("x")
            self.ax.set_ylabel("f(x)")
            
            self.plot_points()

        elif problem.n_var == 2 and problem.n_obj == 1:
            n_samples = self.n_samples_3D

            if self.zoom_on_solutions and sets_of_points != []:
                y_min = min([min(points[:, 1]) for points in sets_of_points])
                y_max = max([max(points[:, 1]) for points in sets_of_points])
            else:
                y_min, y_max = problem.xl[1], problem.xu[1]
            
            A = np.linspace(x_min, x_max, n_samples)
            B = np.linspace(y_min, y_max, n_samples)
            X = all_combinations(A, B)

            F = np.reshape(problem.evaluate(X, return_values_of=["F"]), (n_samples, n_samples))

            _X = X[:, 0].reshape((n_samples, n_samples))
            _Y = X[:, 1].reshape((n_samples, n_samples))
            _Z = F.reshape((n_samples, n_samples))

            self.init_figure(plot_3D=True)

            surf = self.ax.plot_surface(_X, _Y, _Z, **self.kwargs_surface)
            if self.colorbar:
                self.fig.colorbar(surf)
            
            self.plot_points()
        else:
            raise Exception("Only landscapes of problems with one or two variables and one objective can be visualized.") #@IgnoreException

    def plot_points(self):
        
        for points, (best_label, gen_label), in zip(self.sets_of_points, self.sets_labels):
            # if points have 2 dimensions, add the third dimension with the fitness value
            best_label, gen_label = best_label, gen_label
            if len(points[0]) in [2,3]:
                x,y = points[1:, 0], points[1:, 1]
                best_x, best_y = points[0, 0], points[0, 1]
                if len(points[0]) == 2:
                    self.ax.scatter(x, y, s=10, label=gen_label, alpha=0.5)
                    self.ax.scatter(best_x, best_y, s=50, label=best_label, alpha=1) if self.show_best_sol else None
                if len(points[0]) == 3:
                    z, best_z = points[1:, 2], points[0, 2]
                    self.ax.scatter(x, y, z, s=20, label=gen_label, alpha=0.5)
                    self.ax.scatter(best_x, best_y, best_z, s=100, label=best_label, alpha=1) if self.show_best_sol else None
            else:
                self.sets_of_points = []
                MyMessageBox(f"Solutions have {len(points[0])-1} dimensions in decision space, only 1 or 2 are supported")
                    
    def add(self, points, label):
        
        self.legend = True
        
        # get the points coordinates from the points arg
        best_point = points[0, :]
        
        # if the number of points is greater than 10, get a random sample of 10 points
        cutoff = 100
        if len(points[:, 0]) > cutoff:
            points = points[np.random.choice(len(points[1:, 0]), cutoff, replace=False), :]
        gen_label = label
        best_label = label + f" (Best sol)"
        
        points = np.concatenate((best_point[np.newaxis,:], points))
        self.sets_of_points.append(points)  
        self.sets_labels.append((best_label, gen_label))
