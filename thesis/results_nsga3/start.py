import pickle
from utils.defines import ALGO_KEY, PROB_KEY

def start(): #! save these files
    with open(f'thesis/results_nsga3/moo_run_options.pickle', 'rb') as file:
        run_options = pickle.load(file) #@IgnoreException

    with open(f'thesis/results_nsga3/moo_parameters.pickle', 'rb') as file:
        parameters = pickle.load(file) #@IgnoreException
    
    from backend.defaults import Defaults
    def_parameters = Defaults(moo=False).parameters
    
    return run_options, parameters
