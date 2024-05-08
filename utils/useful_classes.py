import numpy as np

from pymoo.problems.single.knapsack import Knapsack

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
        
from pymoo.algorithms.moo.ctaea import RestrictedMating, comp_by_cv_dom_then_random
from pymoo.algorithms.moo.nsga2 import binary_tournament
from pymoo.algorithms.moo.nsga3 import comp_by_cv_then_random
from pymoo.algorithms.moo.unsga3 import comp_by_rank_and_ref_line_dist
from pymoo.algorithms.soo.nonconvex.ga import comp_by_cv_and_fitness
from pymoo.operators.selection.tournament import TournamentSelection

class TournamentByCVAndFitness(TournamentSelection):
    def __init__(self, pressure=2, **kwargs):
        super().__init__(func_comp=comp_by_cv_and_fitness, **kwargs)
    
class RestrictedMatingCTAEA(RestrictedMating):
    def __init__(self, pressure=2, **kwargs):
        super().__init__(func_comp=comp_by_cv_dom_then_random, **kwargs)
        
class BinaryTournament(TournamentSelection):
    def __init__(self, pressure=2, **kwargs):
        super().__init__(func_comp=binary_tournament, **kwargs)

class TournamentByCVThenRandom(TournamentSelection):
    def __init__(self, pressure=2, **kwargs):
        super().__init__(func_comp=comp_by_cv_then_random, **kwargs)
        
class TournamentByRankAndRefLineDist(TournamentSelection):
    def __init__(self, pressure=2, **kwargs):
        super().__init__(func_comp=comp_by_rank_and_ref_line_dist, **kwargs)


class BestSol():
        """used in the case of single-objective optimization,just for code compatibility. 
        Only returns the input, because it should consist of only the best solution"""
        def __init__(self, *args, **kwargs):
            pass
        
        def do(self, solution_np_array, *args, **kwargs):
            return solution_np_array[0][0] if len(solution_np_array) > 0 else np.nan

from pymoo.indicators.hv import Hypervolume

class negativeHypervolume(Hypervolume):
    def _do(self, F):
        return - super()._do(F)