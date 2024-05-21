from pymoo.operators.sampling.rnd import Sampling
from pymoo.operators.crossover.ox import ox, Crossover
from pymoo.operators.mutation.inversion import random_sequence, inversion_mutation, Mutation
from pymoo.core.repair import Repair
import numpy as np
from pymoo.core.duplicate import DuplicateElimination


class PermutationRandomSampling(Sampling):

    def _do(self, problem, n_samples, **kwargs):
        
        X = np.full((n_samples, problem.n_cities, 2), -1, dtype=int)
        for i in range(n_samples):
            path = np.random.permutation(problem.n_cities)
            transport = np.random.randint(0, len(problem.transport_options), problem.n_cities)
            X[i] = np.column_stack([path, transport])

        return X

class StartFromZeroRepair(Repair):

    def _do(self, problem, X, **kwargs):
        # reorder X so that the first column starts with 0 and the rest of the columns are shifted accordingly
        for i, x in enumerate(X):
            I = np.where(x[:, 0] == 0)[0]
            
            if I.size > 0:
                # Rotate the rows of X so that the row where the first column is 0 comes first
                x = np.roll(x, -I[0], axis=0)
            X[i] = x
            
        return X    

class MixedDuplicateElimination(DuplicateElimination):
    def is_equal(self, a, b):
        print("a", a)
        print("b", b)
        
        return np.all(a[:, 0] == b[:, 0])
    
class InversionMutation(Mutation):

    def __init__(self, prob=1.0):
        """

        This mutation is applied to permutations. It randomly selects a segment of a chromosome and reverse its order.
        For instance, for the permutation `[1, 2, 3, 4, 5]` the segment can be `[2, 3, 4]` which results in `[1, 4, 3, 2, 5]`.

        Parameters
        ----------
        prob : float
            Probability to apply the mutation to the individual
            
        """
        super().__init__()
        self.prob = prob

    def _do(self, problem, X, **kwargs):
        Y = X.copy()
        for i, y in enumerate(X):
            if np.random.random() < self.prob:
                seq = random_sequence(len(y))
                Y[i] = inversion_mutation(y, seq, inplace=True)

        return Y
    
class OrderCrossover(Crossover):

    def __init__(self, shift=False, **kwargs):
        super().__init__(2, 2, **kwargs)
        self.shift = shift

    def _do(self, problem, X, **kwargs):
        _, n_matings, n_var, _ = X.shape
        Y = np.full((self.n_offsprings, n_matings, n_var, 2), -1, dtype=int)
    
        for j in range(2):  # New loop to iterate over the last dimension of X
            for i in range(n_matings):
                a, b = X[:, i, :, j]
                n = len(a)
    
                # define the sequence to be used for crossover
                start, end = random_sequence(n)
    
                Y[0, i, :, j] = ox(a, b, seq=(start, end), shift=self.shift)
                Y[1, i, :, j] = ox(b, a, seq=(start, end), shift=self.shift)
    
        return Y    
    
if __name__ == '__main__':
    from algorithm import main
    main()