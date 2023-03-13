import pandas as pd
from pymoo.algorithms.moo.nsga2 import NSGA2 
from pymoo.algorithms.moo.nsga3 import NSGA3
from pymoo.algorithms.moo.moead import MOEAD
from pymoo.util.ref_dirs import get_reference_directions
from pymoo.problems import get_problem

# DEFINES
PROB_NAMES = ['DTLZ1', 'DTLZ2', 'DTLZ3', 'DTLZ4', 'DTLZ5', 'DTLZ6']
ALGO_NAMES = ['NSGA2', 'NSGA3', 'MOEAD']

class Input():
    def __init__(self, csv_file):
        self.n_gen = None
        self.n_seeds = None
        self.probs = []
        self.algos = []
        self.read_input(csv_file)
        
    def read_input(self, csv_file):
        input_data = pd.read_csv(csv_file)
        for prob_name in input_data['Problem']:
            prob = get_problem(prob_name)
            if prob is not None:
                self.probs.append(prob)
        for algo_name in input_data['Algorithm']:
            algo = self.get_algo(algo_name, self.probs[0])
            if algo is not None:
                self.algos.append(algo)
        self.n_gen = input_data['n_gen'][0]
        self.n_seeds = int(input_data['n_seeds'][0])
        return
    
    def get_algo(self, algo_name, problem):
        n_dim = problem.n_obj
        ref_dirs = get_reference_directions("das-dennis", n_dim, n_partitions= 4*n_dim)
        pop_size = len(ref_dirs)
        if algo_name == 'NSGA2':
            return NSGA2(pop_size=pop_size)
        elif algo_name == 'NSGA3':
            return NSGA3(ref_dirs)
        elif algo_name == 'MOEAD':
            return MOEAD(ref_dirs)    