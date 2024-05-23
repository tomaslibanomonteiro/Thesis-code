from pymoo.operators.sampling.rnd import Sampling
from pymoo.operators.crossover.ox import ox, Crossover
from pymoo.operators.mutation.inversion import random_sequence, inversion_mutation, Mutation
from pymoo.core.repair import Repair
import numpy as np
from pymoo.core.duplicate import DuplicateElimination

def setTransportsOnNewPaths(new_paths, X):
    
    new_X = np.full((X.shape), -1, dtype=int)
    pop_size, n_cities = X.shape[0], X.shape[1]//2

    old_paths, old_trps = X[:,:n_cities], X[:,n_cities:]
    
    # loop over all individuals
    for i, old_path, old_trp, new_path in zip(range(pop_size), old_paths, old_trps, new_paths):
        if np.array_equal(new_path, old_path):
            new_X[i] = X[i]
        else:
            # loop over all cities
            for k in range(n_cities):
                old_trp_idx = np.where(old_path == new_path[k])
                new_X[i,k] = new_path[k]
                new_X[i,k+n_cities] = old_trp[old_trp_idx]
            
    return new_X

class PermutationRandomSampling(Sampling):

    def _do(self, problem, n_samples, **kwargs):
        
        X = np.full((n_samples, problem.n_var), -1, dtype=int)
        for i in range(n_samples):
            path = np.random.permutation(problem.n_cities)
            transport = np.random.randint(0, len(problem.transport_options), problem.n_cities)
            X[i, :] = np.concatenate([path, transport])

        return X

class StartFromZeroRepair(Repair):

    def _do(self, problem, X, **kwargs):
        X_path = X[:,:problem.n_cities].copy()
        I = np.where(X_path == 0)[1]

        for k in range(len(X_path)):
            i = I[k]
            X_path[k] = np.concatenate([X_path[k, i:], X_path[k, :i]])

        return setTransportsOnNewPaths(X_path, X)
        
class OrderCrossover(Crossover):

    def __init__(self, shift=False, **kwargs):
        super().__init__(2, 2, **kwargs)
        self.shift = shift

    def _do(self, problem, X, **kwargs):
        
        X_path = X[:,:,:problem.n_cities].copy()
        n_parents, n_matings, n_cities = X_path.shape
        Y_path = np.full((self.n_offsprings, n_matings, n_cities), -1, dtype=int)

        for i in range(n_matings):
            a, b = X_path[:, i, :]
            n = len(a)

            # define the sequence to be used for crossover
            start, end = random_sequence(n)

            Y_path[0, i, :] = ox(a, b, seq=(start, end), shift=self.shift)
            Y_path[1, i, :] = ox(b, a, seq=(start, end), shift=self.shift)

        Y = np.full((self.n_offsprings, n_matings, n_cities*2), -1, dtype=int)
        Y[0, :, :] = setTransportsOnNewPaths(Y_path[0, :, :], X[0, :, :])
        Y[1, :, :] = setTransportsOnNewPaths(Y_path[1, :, :], X[1, :, :])
        return Y

class InversionFlipMutation(Mutation):

    def __init__(self, prob=1.0, prob_var=0.7, only_flip = False, **kwargs):
        """

        This mutation is applied to permutations. It randomly selects a segment of a chromosome and reverse its order.
        For instance, for the permutation `[1, 2, 3, 4, 5]` the segment can be `[2, 3, 4]` which results in `[1, 4, 3, 2, 5]`.

        Parameters
        ----------
        prob : float
            Probability to apply the mutation to the individual
            
        """
        super().__init__(prob_var=prob_var, **kwargs)
        self.prob = prob
        self.only_flip = only_flip

    def _do(self, problem, X, **kwargs):
        
        if not self.only_flip:
            # inversion part
            X_path = X[:,:problem.n_cities]
            Y_path = X_path.copy()
            for i, y in enumerate(X_path):
                if np.random.random() < self.prob:
                    seq = random_sequence(len(y))
                    Y_path[i] = inversion_mutation(y, seq, inplace=True)

            Y = setTransportsOnNewPaths(Y_path, X)
        else:
            Y = X.copy()
            Y_path = Y[:,:problem.n_cities]
                
        Y_trp = Y[:,problem.n_cities:]
        # bitflip part
        prob_var = self.get_prob_var(problem)
        flip = np.random.random(Y_trp.shape) < prob_var
        flip_values = np.random.randint(0, len(problem.transport_options), Y_trp.shape)
        Y_trp[flip] = flip_values[flip]
        
        Y = np.concatenate([Y_path, Y_trp], axis=1)
        return Y        

if __name__ == '__main__':
    from main import main
    main()