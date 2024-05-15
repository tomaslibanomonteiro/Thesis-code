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
        
        super().__init__(problem, scale_factor=scale_factor)
    
    
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

################################################################################################################################
#####################################################   INDICATORS   ###########################################################
################################################################################################################################


### Single-objective indicators
class BestFitness():
        """used in the case of single-objective optimization,just for code compatibility. 
        Only returns the input, because it should consist of only the best solution"""
        def __init__(self, *args, **kwargs):
            pass
        
        def do(self, opt_feas, *args, **kwargs):
            return opt_feas[0][0]
class AvgPopFitness():
    def __init__(self, *args, **kwargs):
        pass
    
    def do(self, opt_feas, pop, *args, **kwargs):
        return np.mean(pop) if len(pop) > 0 else np.nan

class GoalAchieved():
    def __init__(self, goal=1.1, *args, **kwargs):
        self.goal = goal
    
    def do(self, opt_feas, *args, **kwargs):
        return -1 if opt_feas <= self.goal else 0

class EvalsOnGoal():
    def __init__(self, goal=1.1, *args, **kwargs):
        self.goal = goal
        self.n_eval = 0
        self.evals_on_goal = np.nan
        
    def do(self, opt_feas, n_eval, pop, *args, **kwargs):
        
        if n_eval <= self.n_eval:
            self.evals_on_goal = np.nan
        self.n_eval = n_eval
            
        if np.isnan(self.evals_on_goal) and opt_feas <= self.goal:            
            self.evals_on_goal = n_eval 
        return self.evals_on_goal

### Multi-objective indicators

from pymoo.indicators.hv import Hypervolume
class negativeHypervolume(Hypervolume):
    def _do(self, F):
        return - super()._do(F)

