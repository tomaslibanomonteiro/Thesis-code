import numpy as np

from pymoo.termination.max_gen import MaximumGenerationTermination

class MyNumGen(MaximumGenerationTermination):
    def __init__(self, prob_id='prob_id(convert)', **kwargs):
        if 'dtlz1' in prob_id:
            n_gen = 400
        elif 'dtlz2' in prob_id:
            n_gen = 250
        elif 'dtlz3' in prob_id:
            n_gen = 1000
        elif 'dtlz4' in prob_id:
            n_gen = 600
        else:
            raise Exception("Problem id must be 'dtlz1', 'dtlz2', 'dtlz3' or 'dtlz4'")
        super().__init__(n_gen, **kwargs)

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

from pymoo.util.reference_direction import MultiLayerReferenceDirectionFactory, UniformReferenceDirectionFactory

class MyLayers(MultiLayerReferenceDirectionFactory):
    def __init__(self, n_dim: int):
        super().__init__()
        
        layer_2 = None
        if n_dim == 2:
            layer_1 = UniformReferenceDirectionFactory(n_dim, n_partitions=99).do()
        elif n_dim == 3:
            layer_1 = UniformReferenceDirectionFactory(n_dim, n_partitions=12).do()
        elif n_dim in [4,5]:
            layer_1 = UniformReferenceDirectionFactory(n_dim, n_partitions=6).do()
        elif n_dim in [6,7,8,9,10]:
            layer_1 = UniformReferenceDirectionFactory(n_dim, n_partitions=2, scaling=0.5).do()
            layer_2 = UniformReferenceDirectionFactory(n_dim, n_partitions=3, scaling=1).do()
        elif n_dim in [11,12,13,14,15]:
            layer_1 = UniformReferenceDirectionFactory(n_dim, n_partitions=1, scaling=0.5).do()
            layer_2 = UniformReferenceDirectionFactory(n_dim, n_partitions=2, scaling=1).do()
        elif not isinstance(n_dim, int):
            raise Exception("n_dim must be an integer.")
        elif n_dim > 15 or n_dim < 2:
            raise Exception("Not implemented for n_dim > 15 or n_dim < 2.")
        
        self.add_layer(layer_1)
        if layer_2 is not None:
            self.add_layer(layer_2)

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