import numpy as np
from pymoo.algorithms.moo.nsga2 import RankAndCrowding
from thesis.results_worst_case.operators import setTransportsOnNewPaths

class RankAndCrowdingACO(RankAndCrowding):

    def __init__(self, q=1, ev = 0.9, ph_factor=2, heu_factor=2, nds=None, crowding_func="cd"):
    
        self.pheromone = None
        self.best_time = None
        self.ev = ev
        self.q = q
        self.ph_factor = ph_factor
        self.heu_factor = heu_factor

        super().__init__(nds, crowding_func)

    def _do(self, problem, pop, *args, n_survive=None, **kwargs):

        # do the normal rank and crowding
        pop = super()._do(problem, pop, *args, n_survive=n_survive, **kwargs)
        
        # do the ACO update
        norm_D, n_cities, X, F = problem.norm_D, problem.n_cities, pop.get("X"), pop.get("F")
        
        if self.pheromone is None:
            self.pheromone = np.zeros((n_cities, n_cities))
        
        X_path = X[:, :n_cities].copy()
        norm_F = (F - F.min(axis=0)) / (F.max(axis=0) - F.min(axis=0))
        single_F = norm_F.sum(axis=1)
        
        # update pheromone
        for ant, fit in zip(X_path, single_F):
            for i in range(n_cities):
                old_ph = self.pheromone[ant[i], ant[(i+1) % n_cities]]
                self.pheromone[ant[i], ant[(i+1) % n_cities]] = self.ev * old_ph + self.ev * self.q / fit
                self.pheromone[ant[(i+1) % n_cities], ant[i]] = self.ev * old_ph + self.ev * self.q / fit
        
        # normalize pheromone
        self.pheromone = self.pheromone / self.pheromone.max()
        
        # get probability matrix
        probs = np.zeros((n_cities, n_cities))
        for i in range(n_cities):
            for j in range(n_cities):
                probs[i, j] = self.pheromone[i, j] ** self.ph_factor * (1 / norm_D[i, j]) ** self.heu_factor if i != j else 0
        
        # set the minimum probability to the minimum probability of the matrix
        min_prob = np.min(probs[probs.nonzero()])
        probs = probs + min_prob
        np.fill_diagonal(probs, 0)
        
        for ant in range(len(X_path)):
            probs_copy = probs.copy()
            curr_city = 0
            X_path[ant, 0] = curr_city
            for i in range(n_cities-1): 
                # Update the path
                new_city = np.random.choice(n_cities, p=probs_copy[curr_city, :] / probs_copy[curr_city, :].sum())
                X_path[ant, i+1] = new_city 
                
                # Prevent the ant from visiting the same city twice
                probs_copy[curr_city, :] = 0
                probs_copy[:, curr_city] = 0
                
                # Update the current city                
                curr_city = new_city
        X = setTransportsOnNewPaths(X_path, X)
        pop.set("X", X) 
        
        return pop


if __name__ == '__main__':
    from main import main
    main()

