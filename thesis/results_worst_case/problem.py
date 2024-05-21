from pymoo.core.problem import ElementwiseProblem
import numpy as np

from pymoo.core.problem import ElementwiseProblem
from pymoo.core.variable import Real, Integer, Choice, Binary

class MultiObjectiveMixedTSP(ElementwiseProblem):

    def __init__(self, cities_coord, costMatrixDict, timeMatrixDict, **kwargs):
        
        assert cities_coord.shape[1] == 2
        assert len(costMatrixDict) == len(timeMatrixDict)
        assert set(costMatrixDict.keys()) == set(timeMatrixDict.keys())
        for matrix in list(costMatrixDict.values()) + list(timeMatrixDict.values()): 
            assert matrix.shape[0] == matrix.shape[1]
            assert matrix.shape[0] == cities_coord.shape[0]        
            
        self.n_cities, _ = cities_coord.shape
        self.cities_coord = cities_coord
        self.Time = {k: v for k, v in timeMatrixDict.items()}
        self.Cost = {k: v for k, v in costMatrixDict.items()}
        self.transport_options = list(self.Time.keys())
                
        super().__init__(n_var=self.n_cities, n_obj=2, **kwargs)
        
    def _evaluate(self, x, out, *args, **kwargs):
        
        n_cities, path, transport_idx = self.n_cities, x[:, 0], x[:, 1]
        duration = 0
        cost = 0
        for k in range(n_cities - 1):
            i, j = path[k], path[k + 1]
            transport_k = self.transport_options[transport_idx[k]]
            duration += self.Time[transport_k][i, j]
            cost += self.Cost[transport_k][i, j]
            
        # back to the initial city
        last, first = path[-1], path[0]
        transport_last = self.transport_options[transport_idx[-1]]
        duration += self.Time[transport_last][last, first]  
        cost += self.Cost[transport_last][last, first]
        
        out['F'] = np.array([duration, cost])

def mutateMatrix(original, percentage=10):
    # Create a matrix of the same shape as the original matrix with random values between 1 - percentage and 1 + percentage
    lower = -percentage / 100
    upper = percentage / 100
    randoms = np.random.uniform(lower, upper, original.shape)
    return original * (1 + randoms)

class RandomMultiMixedTSP(MultiObjectiveMixedTSP):
    
    def __init__(self, n_cities=22, trp1 = 'car', trp2 = 'train', trp2_factor=1.1, trp3 = 'plane', trp3_factor=1.3, grid_size=1000, seed=0, **kwargs):
    
        cities = np.random.uniform(0, grid_size, (n_cities, 2))
        
        # calculate the distance matrix
        from scipy.spatial.distance import cdist
        trp1_T = cdist(cities, cities)
        trp2_T = 1/trp2_factor * trp1_T 
        trp3_T = 1/trp3_factor * trp1_T
                
        # integer distance matrix
        trp1_C = mutateMatrix(trp1_T, percentage=10)
        trp2_C = mutateMatrix(trp1_T * trp2_factor, percentage=10)
        trp3_C = mutateMatrix(trp1_T * trp3_factor, percentage=10)
                
        super().__init__(cities, {trp1: trp1_C, trp2: trp2_C, trp3: trp3_C}, {trp1: trp1_T, trp2: trp2_T, trp3: trp3_T}, **kwargs)