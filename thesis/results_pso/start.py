import pickle
from utils.defines import ALGO_KEY, PROB_KEY

def start():
    with open(f'thesis/results_pso/soo_run_options_2var.pickle', 'rb') as file:
        run_options = pickle.load(file) #@IgnoreException

    with open(f'thesis/results_pso/soo_parameters.pickle', 'rb') as file:
        parameters = pickle.load(file) #@IgnoreException
    
    from backend.defaults import Defaults
    def_parameters = Defaults(moo=False).parameters
    
    def_parameters[ALGO_KEY] = parameters[ALGO_KEY]
    def_parameters[PROB_KEY] = parameters[PROB_KEY]
    
    def_parameters[PROB_KEY]['rosenbrock']['xl'] = -30
    def_parameters[PROB_KEY]['rosenbrock']['xu'] = 30 
    def_parameters[PROB_KEY]['rastrigin']['xl'] = -5.12
    def_parameters[PROB_KEY]['rastrigin']['xu'] = 5.12
            

    return run_options, def_parameters, {}, {}
